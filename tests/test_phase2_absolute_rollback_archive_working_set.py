from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.constants import RUNTIME_WORKING_SET_MAX_BYTES
from sudachi_life.rollback import RollbackArchiveError, prepare_rollback_archive
from sudachi_life.runtime_storage import runtime_working_set_bytes

from test_phase2_projection_rollback import _prepared_pair


def _prepare_schema_v2_zero(tmp_path: Path):
    _v1_root, _v1, v2_root, v2, _left, _right = _prepared_pair(tmp_path)
    return v2_root, v2


def _sparse_file(path: Path, size: int) -> None:
    assert size >= 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


def _control_archive(tmp_path: Path):
    root, paths = _prepare_schema_v2_zero(tmp_path)
    archive = prepare_rollback_archive(root, paths.organism_id, 2)
    final_working_set = runtime_working_set_bytes(paths)
    manifest_size = (archive.archive_dir / "manifest.json").stat().st_size
    assert manifest_size > 1
    return archive, final_working_set, manifest_size


def test_rollback_archive_accepts_exact_absolute_working_set_limit(
    tmp_path: Path,
) -> None:
    control, control_final, manifest_size = _control_archive(tmp_path / "control")
    root, paths = _prepare_schema_v2_zero(tmp_path / "probe")
    padding = RUNTIME_WORKING_SET_MAX_BYTES - control_final
    _sparse_file(paths.rollback_archives / ".absolute-limit-padding", padding)

    before = runtime_working_set_bytes(paths)
    assert before < RUNTIME_WORKING_SET_MAX_BYTES
    assert (
        before + control.database_size_bytes + manifest_size
        == RUNTIME_WORKING_SET_MAX_BYTES
    )

    archive = prepare_rollback_archive(root, paths.organism_id, 2)
    assert archive.database_size_bytes == control.database_size_bytes
    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES


def test_rollback_archive_removes_new_publication_one_byte_over_working_set(
    tmp_path: Path,
) -> None:
    control, control_final, manifest_size = _control_archive(tmp_path / "control")
    root, paths = _prepare_schema_v2_zero(tmp_path / "probe")
    padding = RUNTIME_WORKING_SET_MAX_BYTES - control_final + 1
    padding_path = paths.rollback_archives / ".absolute-limit-padding"
    _sparse_file(padding_path, padding)

    before = runtime_working_set_bytes(paths)
    before_entries = {entry.name for entry in paths.rollback_archives.iterdir()}
    assert before < RUNTIME_WORKING_SET_MAX_BYTES
    assert before + control.database_size_bytes <= RUNTIME_WORKING_SET_MAX_BYTES
    assert (
        before + control.database_size_bytes + manifest_size
        == RUNTIME_WORKING_SET_MAX_BYTES + 1
    )

    with pytest.raises(RollbackArchiveError, match="working set"):
        prepare_rollback_archive(root, paths.organism_id, 2)

    assert padding_path.is_file()
    assert {entry.name for entry in paths.rollback_archives.iterdir()} == before_entries
    assert runtime_working_set_bytes(paths) == before
    assert runtime_working_set_bytes(paths) <= RUNTIME_WORKING_SET_MAX_BYTES
