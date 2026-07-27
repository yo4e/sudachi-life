from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.checkpoint_repair import (
    PendingCheckpointRepairRejectedError,
    repair_pending_checkpoint_registration,
)
from sudachi_life.constants import RUNTIME_WORKING_SET_MAX_BYTES
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.runtime_storage import runtime_working_set_bytes
from sudachi_life.storage import connect_database, read_status

from phase1_audit_helpers import _wake_clock
from test_phase2_absolute_active_and_repair_limits import _initialize_v2
from test_phase2_checkpoint_artifact_exact_limit import _published_pending_orphan
from test_phase2_projection_rollback import _rollback_clock


def _sparse_file(path: Path, size: int) -> None:
    assert size >= 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


def _complete_checkpoint_wake(tmp_path: Path):
    runtime_root, paths = _initialize_v2(tmp_path, "absolute-checkpoint-ws-v2")
    enqueue_garden_tick(
        paths,
        "absolute-checkpoint-ws-source",
        clock=_rollback_clock(1_780_000_000_000_000, 80_000_000),
    )
    result = perform_garden_wake(
        runtime_root,
        paths.organism_id,
        seed=3,
        clock=_wake_clock(1_781_000_000_000_000),
    )
    assert result.status == "sleeping"
    return runtime_root, paths


def _prepared_checkpoint_wake(tmp_path: Path):
    runtime_root, paths = _initialize_v2(tmp_path, "absolute-checkpoint-ws-v2")
    enqueue_garden_tick(
        paths,
        "absolute-checkpoint-ws-source",
        clock=_rollback_clock(1_780_000_000_000_000, 80_000_000),
    )
    return runtime_root, paths


def test_checkpoint_publication_accepts_exact_working_set_limit(tmp_path: Path) -> None:
    _control_root, control_paths = _complete_checkpoint_wake(tmp_path / "control")
    control_final = runtime_working_set_bytes(control_paths)

    runtime_root, paths = _prepared_checkpoint_wake(tmp_path / "probe")
    _sparse_file(
        paths.restore_candidates / ".absolute-checkpoint-ws-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - control_final,
    )
    result = perform_garden_wake(
        runtime_root,
        paths.organism_id,
        seed=3,
        clock=_wake_clock(1_781_000_000_000_000),
    )
    assert result.status == "sleeping"
    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES


def test_checkpoint_publication_rejects_one_byte_over_working_set_without_temp(
    tmp_path: Path,
) -> None:
    _control_root, control_paths = _complete_checkpoint_wake(tmp_path / "control")
    control_final = runtime_working_set_bytes(control_paths)

    runtime_root, paths = _prepared_checkpoint_wake(tmp_path / "probe")
    _sparse_file(
        paths.restore_candidates / ".absolute-checkpoint-ws-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - control_final + 1,
    )
    before_visible = sorted(
        entry.name
        for entry in paths.checkpoints.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    )
    before_working_set = runtime_working_set_bytes(paths)
    assert before_working_set < RUNTIME_WORKING_SET_MAX_BYTES

    with pytest.raises(CheckpointError, match="runtime working set"):
        perform_garden_wake(
            runtime_root,
            paths.organism_id,
            seed=3,
            clock=_wake_clock(1_781_000_000_000_000),
        )

    assert runtime_working_set_bytes(paths) == before_working_set
    assert not any(
        entry.name.startswith(".tmp-checkpoint-")
        for entry in paths.checkpoints.iterdir()
    )
    assert sorted(
        entry.name
        for entry in paths.checkpoints.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    ) == before_visible
    status = read_status(paths)
    assert status.status == "checkpoint_pending"
    assert status.checkpoint_pending is True


def _repair_at(tmp_path: Path):
    runtime_root, paths, orphan = _published_pending_orphan(tmp_path)
    result = repair_pending_checkpoint_registration(
        runtime_root,
        paths.organism_id,
        clock=_rollback_clock(1_790_000_000_000_000, 90_000_000),
    )
    assert result.checkpoint_id == orphan.name
    return runtime_root, paths, orphan


def test_pending_repair_accepts_exact_working_set_limit(tmp_path: Path) -> None:
    _control_root, control_paths, _control_orphan = _repair_at(tmp_path / "control")
    control_final = runtime_working_set_bytes(control_paths)

    runtime_root, paths, orphan = _published_pending_orphan(tmp_path / "probe")
    _sparse_file(
        paths.restore_candidates / ".absolute-repair-ws-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - control_final,
    )
    result = repair_pending_checkpoint_registration(
        runtime_root,
        paths.organism_id,
        clock=_rollback_clock(1_790_000_000_000_000, 90_000_000),
    )
    assert result.checkpoint_id == orphan.name
    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES


def test_pending_repair_rejects_working_set_one_byte_over_without_mutation(
    tmp_path: Path,
) -> None:
    _control_root, control_paths, _control_orphan = _repair_at(tmp_path / "control")
    control_final = runtime_working_set_bytes(control_paths)

    runtime_root, paths, orphan = _published_pending_orphan(tmp_path / "probe")
    _sparse_file(
        paths.restore_candidates / ".absolute-repair-ws-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - control_final + 1,
    )
    before = read_status(paths)
    before_working_set = runtime_working_set_bytes(paths)

    with pytest.raises(
        PendingCheckpointRepairRejectedError,
        match="runtime working set",
    ):
        repair_pending_checkpoint_registration(
            runtime_root,
            paths.organism_id,
            clock=_rollback_clock(1_790_000_000_000_000, 90_000_000),
        )

    assert read_status(paths) == before
    assert runtime_working_set_bytes(paths) == before_working_set
    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT 1 FROM checkpoint_registry WHERE checkpoint_id=?",
            (orphan.name,),
        ).fetchone() is None
    finally:
        connection.close()
    assert orphan.is_dir()
