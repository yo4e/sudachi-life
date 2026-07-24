from __future__ import annotations

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


def test_runtime_working_set_counts_sidecars_and_retained_rollback_evidence(
    initialized,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    paths.rollback_archives.mkdir()
    paths.restore_candidates.mkdir()
    (paths.rollback_archives / "archive.bin").write_bytes(b"a" * 4096)
    (paths.restore_candidates / "candidate.bin").write_bytes(b"b" * 8192)
    sidecar = Path(str(paths.database) + "-journal")
    sidecar.write_bytes(b"w" * 2048)

    total = runtime_working_set_bytes(paths)
    old_expression = paths.database.stat().st_size + sum(
        path.stat().st_size
        for path in paths.checkpoints.rglob("*")
        if path.is_file()
    )
    assert total >= old_expression + 4096 + 8192 + 2048
    sidecar.unlink()
    monkeypatch.setattr(
        "sudachi_life.lifecycle.RUNTIME_WORKING_SET_MAX_BYTES",
        old_expression + 1024,
    )

    enqueue_garden_tick(
        paths,
        "working-set-tick",
        clock=FakeClock([ClockReading(1300, 13_000_000)]),
    )
    clock = FakeClock([])
    with pytest.raises(SchemaValidationError, match="working set"):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=1,
            clock=clock,
        )
    assert clock.read_count == 0
