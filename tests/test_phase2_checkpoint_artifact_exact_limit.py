from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.checkpoint_repair import repair_pending_checkpoint_registration
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import CHECKPOINT_ARTIFACT_MAX_BYTES
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.storage import connect_database, read_status, validate_canonical_state

from test_phase2_absolute_active_and_repair_limits import (
    _initialize_v2,
    _rewrite_orphan_identity,
)


def _published_pending_orphan(
    tmp_path: Path,
) -> tuple[Path, object, Path]:
    runtime_root, paths = _initialize_v2(tmp_path, "exact-checkpoint-v2")
    enqueue_garden_tick(
        paths,
        "repair-at-limit-source",
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
    return runtime_root, paths, orphan_dirs[0]


def test_pending_repair_accepts_checkpoint_database_at_exact_artifact_limit(
    tmp_path: Path,
) -> None:
    runtime_root, paths, orphan_dir = _published_pending_orphan(tmp_path)
    database = orphan_dir / "organism.sqlite3"
    assert database.stat().st_size < CHECKPOINT_ARTIFACT_MAX_BYTES

    # SQLite accepts page-aligned trailing bytes while preserving the canonical
    # database body and integrity result. They remain real protected file bytes,
    # so this places the artifact exactly at the accepted physical ceiling.
    with database.open("r+b") as handle:
        handle.truncate(CHECKPOINT_ARTIFACT_MAX_BYTES)
    orphan = _rewrite_orphan_identity(orphan_dir)
    assert (orphan / "organism.sqlite3").stat().st_size == CHECKPOINT_ARTIFACT_MAX_BYTES

    snapshot = connect_database(orphan / "organism.sqlite3", read_only=True)
    try:
        integrity = snapshot.execute("PRAGMA integrity_check").fetchall()
        assert len(integrity) == 1 and integrity[0][0] == "ok"
        validate_canonical_state(snapshot, expect_checkpoint_pending=True)
    finally:
        snapshot.close()

    before = read_status(paths)
    assert before.checkpoint_pending is True
    result = repair_pending_checkpoint_registration(
        runtime_root,
        paths.organism_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=1_750_000_000_000_000,
            monotonic_ns=50_000_000,
        ),
    )

    assert result.checkpoint_id == orphan.name
    after = read_status(paths)
    assert after.status == "sleeping"
    assert after.checkpoint_pending is False
    assert after.latest_stable_checkpoint_id == orphan.name
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT database_size_bytes FROM checkpoint_registry WHERE checkpoint_id=?",
            (orphan.name,),
        ).fetchone()
    finally:
        connection.close()
    assert row is not None
    assert int(row[0]) == CHECKPOINT_ARTIFACT_MAX_BYTES
