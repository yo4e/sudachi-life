from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3

import pytest

from sudachi_life.checkpoint_repair import (
    PendingCheckpointRepairRejectedError,
    repair_pending_checkpoint_registration,
)
from sudachi_life.checkpoints import (
    reconcile_checkpoint_retention_staging,
    validate_checkpoint_directory,
)
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import (
    MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
    MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
)
from sudachi_life.errors import CheckpointError, SchemaValidationError
from sudachi_life.inbox import InputRejectedError, enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.runtime_storage import runtime_working_set_bytes
from sudachi_life.storage import connect_database, initialize_database, read_status

from phase1_audit_helpers import (
    _checkpoint_boundaries,
    _enqueue_and_wake,
    _publish_pending_snapshot,
    _wake_clock,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_missing_append_only_trigger_is_rejected_by_active_and_checkpoint_validation(
    initialized,
    tmp_path: Path,
) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute("DROP TRIGGER event_no_update")
    finally:
        connection.close()

    with pytest.raises(SchemaValidationError, match="schema fingerprint"):
        read_status(paths)
    with pytest.raises(SchemaValidationError, match="schema fingerprint"):
        enqueue_garden_tick(
            paths,
            "schema-corruption-tick",
            clock=FakeClock([]),
        )

    corrupted = tmp_path / "corrupted-checkpoint"
    corrupted.mkdir()
    source_dir = paths.checkpoints / genesis.checkpoint_id
    database = corrupted / "organism.sqlite3"
    manifest_path = corrupted / "manifest.json"
    database.write_bytes((source_dir / "organism.sqlite3").read_bytes())
    manifest = json.loads((source_dir / "manifest.json").read_text(encoding="utf-8"))
    snapshot = sqlite3.connect(database, isolation_level=None)
    try:
        snapshot.execute("DROP TRIGGER event_no_update")
    finally:
        snapshot.close()
    manifest["database_size_bytes"] = database.stat().st_size
    manifest["database_sha256"] = _sha256(database)
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(CheckpointError, match="schema fingerprint"):
        validate_checkpoint_directory(corrupted, expected_manifest=manifest)


def test_genesis_published_orphan_can_be_registered(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    paths = OrganismPaths.build(runtime_root, "genesis-repair")
    wall_time, boundary = initialize_database(
        paths,
        clock=FakeClock([ClockReading(100, 1_000_000)]),
    )
    assert boundary == 2
    orphan = _publish_pending_snapshot(
        paths,
        provenance="genesis",
        creation_wall_time_utc_us=wall_time,
    )

    result = repair_pending_checkpoint_registration(
        runtime_root,
        paths.organism_id,
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    assert result.checkpoint_id == orphan.name
    assert result.previous_latest_stable_checkpoint_id is None
    assert result.previous_latest_stable_event_sequence == 0
    assert result.registered_checkpoint_count == 1
    assert result.status == "sleeping"
    status = read_status(paths)
    assert status.status == "sleeping"
    assert status.latest_stable_event_sequence == 2


def test_maintenance_bound_pending_orphan_repairs_to_stable_maintenance(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE inventory SET water_units = 0 WHERE singleton_id = 1")
        connection.execute("UPDATE garden_plot SET fruit = 0 WHERE plot_id = 'bed-b'")
        connection.execute(
            "UPDATE environment_state SET objective_complete = 0 WHERE singleton_id = 1"
        )
        connection.commit()
    finally:
        connection.close()

    _enqueue_and_wake(runtime_root, initial.organism_id, 1)
    _enqueue_and_wake(runtime_root, initial.organism_id, 2)
    with pytest.raises(CheckpointError, match="deadline"):
        _enqueue_and_wake(
            runtime_root,
            initial.organism_id,
            3,
            timeout_checkpoint=True,
        )
    pending = read_status(paths)
    assert pending.status == "checkpoint_pending"
    assert pending.consecutive_failures == 3
    assert pending.maintenance_reason == MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT

    result = repair_pending_checkpoint_registration(
        runtime_root,
        initial.organism_id,
        clock=FakeClock([ClockReading(900, 9_000_000)]),
    )
    assert result.status == "maintenance_required"
    repaired = read_status(paths)
    assert repaired.status == "maintenance_required"
    assert repaired.checkpoint_pending is False
    assert repaired.maintenance_reason == MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT
