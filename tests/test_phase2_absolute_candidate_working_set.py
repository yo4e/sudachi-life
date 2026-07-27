from __future__ import annotations

from pathlib import Path

from sudachi_life.constants import RUNTIME_WORKING_SET_MAX_BYTES
from sudachi_life.phase2_schema import ZERO_CAREGIVER_CONFIGURATION_VERSION
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import RestoreCandidateError, build_restore_candidate
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_transform import CandidateTransformError, transform_restore_candidate
from sudachi_life.runtime_storage import runtime_working_set_bytes

from test_phase2_projection_rollback import _prepared_pair, _rollback_clock


def _prepare_intent(tmp_path: Path):
    v1_root, _v1, v2_root, v2, _left, _right = _prepared_pair(tmp_path)
    archive = prepare_rollback_archive(v2_root, "paired", 2)
    begin_rollback(
        v2_root,
        "paired",
        archive.archive_id,
        clock=_rollback_clock(1_710_000_000_000_000, 11_000_000),
    )
    return v2_root, v2


def _sparse_file(path: Path, size: int) -> None:
    if size < 0:
        raise AssertionError(f"negative sparse padding: {size}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


def test_source_candidate_cannot_publish_one_byte_over_absolute_working_set(
    tmp_path: Path,
) -> None:
    control_root, control_paths = _prepare_intent(tmp_path / "control")
    control_candidate = build_restore_candidate(control_root, "paired")
    control_final_working_set = runtime_working_set_bytes(control_paths)
    control_manifest_size = (
        control_candidate.candidate_dir / "manifest.json"
    ).stat().st_size
    assert control_manifest_size > 1

    probe_root, probe_paths = _prepare_intent(tmp_path / "probe")
    padding_size = RUNTIME_WORKING_SET_MAX_BYTES - control_final_working_set + 1
    _sparse_file(
        probe_paths.restore_candidates / ".absolute-limit-padding",
        padding_size,
    )
    before = runtime_working_set_bytes(probe_paths)
    assert before < RUNTIME_WORKING_SET_MAX_BYTES
    assert (
        before + control_candidate.database_size_bytes
        <= RUNTIME_WORKING_SET_MAX_BYTES
    )
    assert (
        before
        + control_candidate.database_size_bytes
        + control_manifest_size
        == RUNTIME_WORKING_SET_MAX_BYTES + 1
    )

    try:
        build_restore_candidate(probe_root, "paired")
    except RestoreCandidateError:
        pass

    assert runtime_working_set_bytes(probe_paths) <= RUNTIME_WORKING_SET_MAX_BYTES


def _prepare_source_candidate(tmp_path: Path):
    root, paths = _prepare_intent(tmp_path)
    source = build_restore_candidate(root, "paired")
    return root, paths, source


def test_transformed_candidate_cannot_publish_one_byte_over_absolute_working_set(
    tmp_path: Path,
) -> None:
    control_root, control_paths, control_source = _prepare_source_candidate(
        tmp_path / "control"
    )
    control_transformed = transform_restore_candidate(
        control_root,
        "paired",
        control_source.candidate_id,
        "absolute transformed boundary",
        clock=_rollback_clock(1_720_000_000_000_000, 12_000_000),
    )
    control_final_working_set = runtime_working_set_bytes(control_paths)
    control_manifest_size = (
        control_transformed.transformed_candidate_dir / "manifest.json"
    ).stat().st_size
    assert control_manifest_size > 1

    probe_root, probe_paths, probe_source = _prepare_source_candidate(
        tmp_path / "probe"
    )
    padding_size = RUNTIME_WORKING_SET_MAX_BYTES - control_final_working_set + 1
    _sparse_file(
        probe_paths.restore_candidates / ".absolute-limit-padding",
        padding_size,
    )
    before = runtime_working_set_bytes(probe_paths)
    assert before < RUNTIME_WORKING_SET_MAX_BYTES
    assert (
        before + probe_source.database_size_bytes
        <= RUNTIME_WORKING_SET_MAX_BYTES
    )
    assert (
        before
        + control_transformed.database_size_bytes
        + control_manifest_size
        == RUNTIME_WORKING_SET_MAX_BYTES + 1
    )

    try:
        transform_restore_candidate(
            probe_root,
            "paired",
            probe_source.candidate_id,
            "absolute transformed boundary",
            clock=_rollback_clock(1_720_000_000_000_000, 12_000_000),
        )
    except CandidateTransformError:
        pass

    assert runtime_working_set_bytes(probe_paths) <= RUNTIME_WORKING_SET_MAX_BYTES
