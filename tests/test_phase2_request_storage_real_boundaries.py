from __future__ import annotations

from pathlib import Path
import sqlite3

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import ACTIVE_DATABASE_MAX_BYTES
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_request_storage import project_request_storage_before_write
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
)
from sudachi_life.runtime_storage import (
    ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
    active_database_allocated_bytes,
    checkpoint_store_bytes,
    runtime_working_set_bytes,
)
from sudachi_life.storage import connect_database, validate_canonical_state

from phase1_audit_helpers import _wake_clock


def _initialize(tmp_path: Path, organism_id: str) -> tuple[Path, OrganismPaths]:
    root = tmp_path / "runtime"
    initialize_organism(
        root,
        organism_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_100_000_000_000_000,
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
    return root, paths


def _allocated(paths: OrganismPaths) -> int:
    connection = connect_database(paths.database, read_only=True)
    try:
        return active_database_allocated_bytes(connection)
    finally:
        connection.close()


def _grow_to_exact_reserve_boundary(paths: OrganismPaths) -> None:
    connection = sqlite3.connect(paths.database, isolation_level=None)
    try:
        connection.execute("PRAGMA journal_mode=DELETE")
        page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
        target_bytes = ACTIVE_DATABASE_MAX_BYTES - ACTIVE_DATABASE_WAKE_RESERVE_BYTES
        assert target_bytes % page_size == 0
        target_pages = target_bytes // page_size
        applied = int(
            connection.execute(f"PRAGMA max_page_count={target_pages}").fetchone()[0]
        )
        assert applied == target_pages
        connection.execute(
            "CREATE TABLE request_reserve_padding (value BLOB NOT NULL)"
        )
        blob_size = 64 * 1024
        while True:
            page_count = int(connection.execute("PRAGMA page_count").fetchone()[0])
            if page_count == target_pages:
                break
            try:
                connection.execute(
                    "INSERT INTO request_reserve_padding(value) VALUES (zeroblob(?))",
                    (blob_size,),
                )
            except sqlite3.DatabaseError:
                if blob_size == 64 * 1024:
                    blob_size = 4096
                elif blob_size == 4096:
                    blob_size = 256
                else:
                    raise
        connection.execute("DROP TABLE request_reserve_padding")
        assert int(connection.execute("PRAGMA page_count").fetchone()[0]) == target_pages
        assert int(connection.execute("PRAGMA freelist_count").fetchone()[0]) > 0
    finally:
        connection.close()

    connection = connect_database(paths.database, read_only=True)
    try:
        validate_canonical_state(connection, expect_checkpoint_pending=False)
    finally:
        connection.close()
    assert _allocated(paths) == (
        ACTIVE_DATABASE_MAX_BYTES - ACTIVE_DATABASE_WAKE_RESERVE_BYTES
    )


def _enqueue(paths: OrganismPaths, external_id: str, offset: int) -> None:
    enqueue_garden_tick(
        paths,
        external_id,
        clock=FakeClock(
            [ClockReading(2_101_000_000_000_000 + offset, 20_000_000 + offset)]
        ),
    )


def test_real_reserve_boundary_refuses_only_request_and_allows_next_wake(
    tmp_path: Path,
) -> None:
    root, paths = _initialize(tmp_path, "request-real-reserve")
    _grow_to_exact_reserve_boundary(paths)
    _enqueue(paths, "request-reserve-first", 1)
    _enqueue(paths, "request-reserve-second", 2)

    first = perform_garden_wake(
        root,
        paths.organism_id,
        seed=1,
        clock=_wake_clock(2_102_000_000_000_000),
    )
    assert first.status == "sleeping"
    assert first.consultation_request is not None
    assert first.consultation_request.created is False
    assert (
        first.consultation_request.reason
        == "consultation_request_not_created_storage_budget"
    )
    assert _allocated(paths) + ACTIVE_DATABASE_WAKE_RESERVE_BYTES == (
        ACTIVE_DATABASE_MAX_BYTES
    )
    manifest = validate_checkpoint_directory(first.checkpoint.checkpoint_dir)
    assert int(manifest["database_size_bytes"]) == _allocated(paths)

    second = perform_garden_wake(
        root,
        paths.organism_id,
        seed=2,
        clock=_wake_clock(2_103_000_000_000_000),
    )
    assert second.status == "sleeping"
    assert second.consultation_request is not None
    assert second.consultation_request.created is False
    assert _allocated(paths) + ACTIVE_DATABASE_WAKE_RESERVE_BYTES == (
        ACTIVE_DATABASE_MAX_BYTES
    )

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM consultation_request"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM event "
            "WHERE source='organism:consultation.request'"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM inbox_event WHERE consumed=0"
        ).fetchone()[0] == 0
    finally:
        connection.close()


def test_request_projection_counts_real_wal_shm_checkpoint_and_working_set(
    tmp_path: Path,
) -> None:
    _root, paths = _initialize(tmp_path, "request-real-sidecars")
    keeper = sqlite3.connect(paths.database, isolation_level=None)
    try:
        mode = str(keeper.execute("PRAGMA journal_mode=WAL").fetchone()[0]).lower()
        assert mode == "wal"
        keeper.execute("BEGIN IMMEDIATE")
        keeper.execute(
            "UPDATE environment_state SET environment_step=environment_step "
            "WHERE singleton_id=1"
        )
        keeper.commit()

        wal = Path(str(paths.database) + "-wal")
        shm = Path(str(paths.database) + "-shm")
        assert wal.is_file() and wal.stat().st_size > 0
        assert shm.is_file() and shm.stat().st_size > 0
        sidecar_bytes = wal.stat().st_size + shm.stat().st_size

        connection = connect_database(paths.database, read_only=True)
        try:
            projection = project_request_storage_before_write(
                connection,
                runtime_root=paths.runtime_root,
                organism_id=paths.organism_id,
                request_row_bytes=1024,
                request_event_bytes=2048,
            )
        finally:
            connection.close()

        assert projection.active_sidecar_bytes == sidecar_bytes
        assert projection.projected_active_files_bytes == (
            projection.projected_active_bytes + sidecar_bytes
        )
        assert projection.projected_checkpoint_store_bytes == (
            checkpoint_store_bytes(paths) + projection.projected_checkpoint_bytes
        )
        assert projection.projected_working_set_bytes == (
            runtime_working_set_bytes(paths)
            + max(
                0,
                projection.projected_active_bytes - paths.database.stat().st_size,
            )
            + projection.projected_checkpoint_bytes
        )
    finally:
        keeper.close()
