from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.constants import RUNTIME_WORKING_SET_MAX_BYTES
from sudachi_life.rollback import RollbackArchiveError, prepare_rollback_archive
from sudachi_life.rollback_candidate import RestoreCandidateError, build_restore_candidate
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_transform import CandidateTransformError, transform_restore_candidate
from sudachi_life.runtime_storage import runtime_working_set_bytes

from test_phase2_projection_rollback import _prepared_pair, _rollback_clock


def _sparse_file(path: Path, size: int) -> None:
    assert size > 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


def _prepared_archive(tmp_path: Path):
    _v1_root, _v1, v2_root, v2, _left, _right = _prepared_pair(tmp_path)
    archive = prepare_rollback_archive(v2_root, "paired", 2)
    return v2_root, v2, archive


def _prepared_source(tmp_path: Path):
    root, paths, archive = _prepared_archive(tmp_path)
    begin_rollback(
        root,
        "paired",
        archive.archive_id,
        clock=_rollback_clock(1_710_000_000_000_000, 11_000_000),
    )
    source = build_restore_candidate(root, "paired")
    return root, paths, archive, source


def _prepared_transformed(tmp_path: Path):
    root, paths, archive, source = _prepared_source(tmp_path)
    transformed = transform_restore_candidate(
        root,
        "paired",
        source.candidate_id,
        "idempotent working-set boundary",
        clock=_rollback_clock(1_720_000_000_000_000, 12_000_000),
    )
    return root, paths, archive, source, transformed


def _push_one_over(paths, name: str) -> Path:
    current = runtime_working_set_bytes(paths)
    assert current < RUNTIME_WORKING_SET_MAX_BYTES
    padding = paths.restore_candidates / name
    _sparse_file(padding, RUNTIME_WORKING_SET_MAX_BYTES - current + 1)
    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES + 1
    return padding


def test_existing_archive_reentry_rejects_over_limit_without_deleting_archive(
    tmp_path: Path,
) -> None:
    root, paths, archive = _prepared_archive(tmp_path)
    _push_one_over(paths, ".idempotent-archive-padding")

    with pytest.raises(RollbackArchiveError, match="runtime working set"):
        prepare_rollback_archive(root, "paired", 2)

    assert archive.archive_dir.is_dir()
    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES + 1


def test_existing_source_candidate_reentry_rejects_over_limit_without_deleting_candidate(
    tmp_path: Path,
) -> None:
    root, paths, _archive, source = _prepared_source(tmp_path)
    _push_one_over(paths, ".idempotent-source-padding")

    with pytest.raises(RestoreCandidateError, match="runtime working set"):
        build_restore_candidate(root, "paired")

    assert source.candidate_dir.is_dir()
    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES + 1


def test_existing_transformed_candidate_reentry_rejects_over_limit_without_deleting_candidate(
    tmp_path: Path,
) -> None:
    root, paths, _archive, source, transformed = _prepared_transformed(tmp_path)
    _push_one_over(paths, ".idempotent-transformed-padding")

    with pytest.raises(CandidateTransformError, match="runtime working set"):
        transform_restore_candidate(
            root,
            "paired",
            source.candidate_id,
            "idempotent working-set boundary",
            clock=_rollback_clock(1_720_000_000_000_000, 12_000_000),
        )

    assert transformed.transformed_candidate_dir.is_dir()
    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES + 1
