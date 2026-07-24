from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.checkpoint_repair import repair_pending_checkpoint_registration
from sudachi_life.checkpoints import reconcile_checkpoint_retention_staging
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import InputRejectedError, enqueue_garden_tick
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status

from phase1_audit_helpers import _checkpoint_boundaries, _enqueue_and_wake


def test_repaired_checkpoint_runs_the_same_retention_policy(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    for index in range(1, 4):
        _enqueue_and_wake(runtime_root, initial.organism_id, index)
    assert _checkpoint_boundaries(paths) == [2, 13, 24, 34]

    with pytest.raises(CheckpointError, match="deadline"):
        _enqueue_and_wake(
            runtime_root,
            initial.organism_id,
            4,
            timeout_checkpoint=True,
        )
    assert _checkpoint_boundaries(paths) == [2, 13, 24, 34]

    result = repair_pending_checkpoint_registration(
        runtime_root,
        initial.organism_id,
        clock=FakeClock([ClockReading(1000, 10_000_000)]),
    )
    assert result.registered_checkpoint_count == 4
    assert _checkpoint_boundaries(paths) == [2, 24, 34, 44]


def test_enqueue_rolls_back_before_crossing_active_database_limit(
    initialized,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    connection = connect_database(paths.database, read_only=True)
    try:
        page_count = int(connection.execute("PRAGMA page_count").fetchone()[0])
        page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
    finally:
        connection.close()
    protected_limit = page_count * page_size
    monkeypatch.setattr(
        "sudachi_life.runtime_storage.ACTIVE_DATABASE_MAX_BYTES",
        protected_limit,
    )

    rejected_id = None
    for index in range(1, 1000):
        candidate = f"bounded-enqueue-{index:04d}-" + "x" * 100
        try:
            enqueue_garden_tick(
                paths,
                candidate,
                clock=FakeClock([ClockReading(1000 + index, index)]),
            )
        except InputRejectedError as exc:
            assert "audited rollback" in str(exc)
            rejected_id = candidate
            break
    assert rejected_id is not None

    connection = connect_database(paths.database, read_only=True)
    try:
        allocated = int(connection.execute("PRAGMA page_count").fetchone()[0]) * int(
            connection.execute("PRAGMA page_size").fetchone()[0]
        )
        assert allocated <= protected_limit
        assert connection.execute(
            "SELECT 1 FROM inbox_event WHERE external_event_id = ?",
            (rejected_id,),
        ).fetchone() is None
    finally:
        connection.close()


def test_post_commit_retention_cleanup_is_explicit_and_reconcilable(
    initialized,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    for index in range(1, 4):
        _enqueue_and_wake(runtime_root, initial.organism_id, index)

    import sudachi_life.checkpoint_retention_prune as retention_prune

    original_rmtree = retention_prune.shutil.rmtree

    def fail_pruning_cleanup(path, *args, **kwargs):
        if Path(path).name.startswith(".pruning-"):
            raise OSError("protected post-commit cleanup failure")
        return original_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(retention_prune.shutil, "rmtree", fail_pruning_cleanup)
    fourth = _enqueue_and_wake(runtime_root, initial.organism_id, 4)
    assert fourth.status == "maintenance_required"
    status = read_status(paths)
    assert status.maintenance_reason == MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED
    staging = sorted(
        path.name
        for path in paths.checkpoints.iterdir()
        if path.name.startswith(".pruning-")
    )
    assert len(staging) == 1
    assert len(_checkpoint_boundaries(paths)) == 4

    monkeypatch.setattr(retention_prune.shutil, "rmtree", original_rmtree)
    result = reconcile_checkpoint_retention_staging(
        runtime_root,
        initial.organism_id,
        clock=FakeClock([ClockReading(1200, 12_000_000)]),
    )
    assert result.removed_staging_directories == tuple(staging)
    assert result.remaining_staging_directories == ()
    assert result.status == "maintenance_required"
    assert result.audit_event_sequence is not None
