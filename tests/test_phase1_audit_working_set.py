from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.runtime_storage import runtime_working_set_bytes
from sudachi_life.storage import read_status

from phase1_audit_helpers import _wake_clock


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
        "sudachi_life.runtime_storage.RUNTIME_WORKING_SET_MAX_BYTES",
        old_expression + 1024,
    )

    enqueue_garden_tick(
        paths,
        "working-set-tick",
        clock=FakeClock([ClockReading(1300, 13_000_000)]),
    )
    with pytest.raises(CheckpointError, match="working set"):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=1,
            clock=_wake_clock(1400),
        )
    status = read_status(paths)
    assert status.status == "checkpoint_pending"
    assert status.checkpoint_pending is True
