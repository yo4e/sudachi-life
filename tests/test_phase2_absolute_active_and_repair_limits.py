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
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import ACTIVE_DATABASE_MAX_BYTES, CHECKPOINT_ARTIFACT_MAX_BYTES
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import InputRejectedError, enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import ZERO_CAREGIVER_CONFIGURATION_VERSION
from sudachi_life.runtime_storage import (
    ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
    active_database_allocated_bytes,
)
from sudachi_life.storage import connect_database, read_status, validate_canonical_state

from phase1_audit_helpers import _wake_clock


def _initialize_v2(tmp_path: Path, organism_id: str) -> tuple[Path, OrganismPaths]:
    runtime_root = tmp_path / "runtime"
    initialize_organism(
        runtime_root,
        organism_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=1_700_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
        schema_version=2,
        consultation_configuration_version=ZERO_CAREGIVER_CONFIGURATION_VERSION,
    )
    return runtime_root, OrganismPaths.build(runtime_root, organism_id)


def _allocated_bytes(paths: OrganismPaths) -> int:
    connection = connect_database(paths.database, read_only=True)
    try:
        return active_database_allocated_bytes(connection)
    finally:
        connection.close()


def _bulk_append_valid_inputs(paths: OrganismPaths, *, target_bytes: int) -> int:
    connection = connect_database(paths.database)
    try:
        organism = connection.execute(
            "SELECT organism_id, lineage_generation, lifecycle_number, schema_version, "
            "environment_version, budget_config_version FROM organism WHERE singleton_id=1"
        ).fetchone()
        next_inbox = int(
            connection.execute("SELECT COALESCE(MAX(inbox_id), 0) + 1 FROM inbox_event").fetchone()[0]
        )
        next_event = int(
            connection.execute("SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM event").fetchone()[0]
        )
        inserted = 0
        while active_database_allocated_bytes(connection) < target_bytes:
            remaining = target_bytes - active_database_allocated_bytes(connection)
            batch_size = 200 if remaining > 256 * 1024 else 20
            inbox_rows = []
            event_rows = []
            for offset in range(batch_size):
                inbox_id = next_inbox + offset
                event_sequence = next_event + offset
                external_event_id = f"absolute-fill-{inbox_id:08d}-" + "x" * 96
                wall_time = 1_710_000_000_000_000 + inbox_id
                inbox_rows.append(
                    (
                        inbox_id,
                        external_event_id,
                        "synthetic:garden_tick",
                        "administration:cli",
                        wall_time,
                        None,
                        0,
                    )
                )
                event_rows.append(
                    (
                        event_sequence,
                        organism["organism_id"],
                        organism["lineage_generation"],
                        organism["lifecycle_number"],
                        wall_time,
                        "input_enqueued",
                        "administration:cli",
                        json.dumps(
                            {
                                "external_event_id": external_event_id,
                                "event_type": "synthetic:garden_tick",
                                "inbox_id": inbox_id,
                            },
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        organism["schema_version"],
                        organism["environment_version"],
                        organism["budget_config_version"],
                    )
                )
            connection.execute("BEGIN IMMEDIATE")
            connection.executemany(
                "INSERT INTO inbox_event (inbox_id, external_event_id, event_type, source, "
                "received_wall_time_utc_us, claimed_lifecycle_number, consumed) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                inbox_rows,
            )
            connection.executemany(
                "INSERT INTO event (event_sequence, organism_id, lineage_generation, "
                "lifecycle_number, wall_time_utc_us, event_type, source, payload_json, "
                "schema_version, environment_version, budget_config_version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                event_rows,
            )
            connection.commit()
            next_inbox += batch_size
            next_event += batch_size
            inserted += batch_size
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        return inserted
    finally:
        if connection.in_transaction:
            connection.rollback()
        connection.close()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inflate_freelist_over_limit(database: Path) -> int:
    connection = sqlite3.connect(database, isolation_level=None)
    try:
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("CREATE TABLE absolute_limit_padding (value BLOB NOT NULL)")
        while True:
            page_count = int(connection.execute("PRAGMA page_count").fetchone()[0])
            page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
            if page_count * page_size > CHECKPOINT_ARTIFACT_MAX_BYTES:
                break
            connection.execute(
                "INSERT INTO absolute_limit_padding(value) VALUES (zeroblob(?))",
                (64 * 1024,),
            )
        connection.execute("DROP TABLE absolute_limit_padding")
    finally:
        connection.close()
    size = database.stat().st_size
    assert size > CHECKPOINT_ARTIFACT_MAX_BYTES
    return size


def _rewrite_orphan_identity(orphan_dir: Path) -> Path:
    database = orphan_dir / "organism.sqlite3"
    manifest_path = orphan_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = _sha256(database)
    checkpoint_id = (
        f"cp-g{int(manifest['lineage_generation']):06d}-"
        f"e{int(manifest['event_sequence']):012d}-{digest[:8]}"
    )
    manifest["checkpoint_id"] = checkpoint_id
    manifest["database_size_bytes"] = database.stat().st_size
    manifest["database_sha256"] = digest
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    final = orphan_dir.parent / checkpoint_id
    orphan_dir.rename(final)
    return final


def test_schema_v2_absolute_active_limit_preserves_exact_next_wake_reserve(
    tmp_path: Path,
) -> None:
    runtime_root, paths = _initialize_v2(tmp_path, "absolute-active-v2")
    inserted = _bulk_append_valid_inputs(
        paths,
        target_bytes=(
            ACTIVE_DATABASE_MAX_BYTES
            - ACTIVE_DATABASE_WAKE_RESERVE_BYTES
            - 512 * 1024
        ),
    )
    assert inserted > 0

    accepted: list[str] = []
    rejected_id = None
    for index in range(5000):
        candidate = f"reserve-boundary-{index:04d}-" + "z" * 96
        try:
            enqueue_garden_tick(
                paths,
                candidate,
                clock=FakeClock.fixed(
                    wall_time_utc_us=1_720_000_000_000_000 + index,
                    monotonic_ns=20_000_000 + index,
                ),
            )
        except InputRejectedError:
            rejected_id = candidate
            break
        accepted.append(candidate)

    assert accepted
    assert rejected_id is not None
    allocated_before_wake = _allocated_bytes(paths)
    assert (
        allocated_before_wake + ACTIVE_DATABASE_WAKE_RESERVE_BYTES
        <= ACTIVE_DATABASE_MAX_BYTES
    )
    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT 1 FROM inbox_event WHERE external_event_id=?",
            (rejected_id,),
        ).fetchone() is None
        assert connection.execute(
            "SELECT 1 FROM event WHERE payload_json LIKE ?",
            (f'%"external_event_id":"{rejected_id}"%',),
        ).fetchone() is None
    finally:
        connection.close()

    result = perform_garden_wake(
        runtime_root,
        paths.organism_id,
        seed=1,
        clock=_wake_clock(1_730_000_000_000_000),
    )
    assert result.status == "sleeping"
    assert _allocated_bytes(paths) <= ACTIVE_DATABASE_MAX_BYTES
    assert read_status(paths).schema_version == 2


def test_pending_repair_rejects_checkpoint_database_one_page_over_absolute_limit(
    tmp_path: Path,
) -> None:
    runtime_root, paths = _initialize_v2(tmp_path, "absolute-repair-v2")
    enqueue_garden_tick(
        paths,
        "repair-over-limit-source",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    with pytest.raises(CheckpointError, match="deadline"):
        perform_garden_wake(
            runtime_root,
            paths.organism_id,
            seed=1,
            clock=FakeClock(
                [
                    ClockReading(300, 10_000_000),
                    ClockReading(300, 15_000_000),
                    ClockReading(301, 20_000_000),
                    ClockReading(302, 30_000_000),
                    ClockReading(303, 5_030_000_001),
                ]
            ),
        )

    connection = connect_database(paths.database, read_only=True)
    try:
        registered = {
            str(row[0])
            for row in connection.execute("SELECT checkpoint_id FROM checkpoint_registry")
        }
    finally:
        connection.close()
    orphan_dirs = [
        entry
        for entry in paths.checkpoints.iterdir()
        if entry.is_dir() and entry.name not in registered
    ]
    assert len(orphan_dirs) == 1
    over_limit_size = _inflate_freelist_over_limit(
        orphan_dirs[0] / "organism.sqlite3"
    )
    orphan = _rewrite_orphan_identity(orphan_dirs[0])

    snapshot = connect_database(orphan / "organism.sqlite3", read_only=True)
    try:
        validate_canonical_state(snapshot, expect_checkpoint_pending=True)
    finally:
        snapshot.close()
    before = read_status(paths)
    assert before.checkpoint_pending is True

    with pytest.raises(
        PendingCheckpointRepairRejectedError,
        match="checkpoint database exceeds",
    ):
        repair_pending_checkpoint_registration(
            runtime_root,
            paths.organism_id,
            clock=FakeClock.fixed(
                wall_time_utc_us=1_740_000_000_000_000,
                monotonic_ns=40_000_000,
            ),
        )

    assert over_limit_size > CHECKPOINT_ARTIFACT_MAX_BYTES
    assert read_status(paths) == before
    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT 1 FROM checkpoint_registry WHERE checkpoint_id=?",
            (orphan.name,),
        ).fetchone() is None
    finally:
        connection.close()
    assert orphan.is_dir()
