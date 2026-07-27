from __future__ import annotations

from pathlib import Path

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import (
    ACTIVE_DATABASE_MAX_BYTES,
    CHECKPOINT_ARTIFACT_MAX_BYTES,
    CHECKPOINT_STORE_MAX_BYTES,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
)
from sudachi_life.runtime_storage import (
    ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
    active_database_files_bytes,
    checkpoint_store_bytes,
    runtime_working_set_bytes,
)
from sudachi_life.storage import connect_database

from phase1_audit_helpers import _wake_clock


def test_successful_request_and_checkpoint_preserve_all_physical_limits(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime"
    organism_id = "request-storage-success"
    initialize_organism(
        root,
        organism_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_300_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
        schema_version=PHASE2_SCHEMA_VERSION,
        consultation_configuration_version=FIXTURE_CONFIGURATION_VERSION,
    )
    paths = OrganismPaths.build(root, organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE inventory SET water_units=0 WHERE singleton_id=1")
        connection.execute("UPDATE garden_plot SET moisture=1, fruit=0")
        connection.execute(
            "UPDATE environment_state SET objective_complete=0 WHERE singleton_id=1"
        )
        connection.commit()
    finally:
        connection.close()
    enqueue_garden_tick(
        paths,
        "request-storage-success-tick",
        clock=FakeClock([ClockReading(2_301_000_000_000_000, 20_000_000)]),
    )

    result = perform_garden_wake(
        root,
        organism_id,
        seed=4,
        clock=_wake_clock(2_302_000_000_000_000),
    )
    assert result.status == "sleeping"
    assert result.consultation_request is not None
    assert result.consultation_request.created is True

    manifest = validate_checkpoint_directory(result.checkpoint.checkpoint_dir)
    assert int(manifest["database_size_bytes"]) <= CHECKPOINT_ARTIFACT_MAX_BYTES
    assert (
        active_database_files_bytes(paths) + ACTIVE_DATABASE_WAKE_RESERVE_BYTES
        <= ACTIVE_DATABASE_MAX_BYTES
    )
    assert checkpoint_store_bytes(paths) <= CHECKPOINT_STORE_MAX_BYTES
    assert runtime_working_set_bytes(paths) <= RUNTIME_WORKING_SET_MAX_BYTES
