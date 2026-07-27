from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from sudachi_life.constants import (
    ACTIVE_DATABASE_MAX_BYTES,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from sudachi_life.rollback_complete import (
    RollbackCompletionRejectedError,
    complete_rollback,
)
from sudachi_life.rollback_replace import (
    ActiveReplacementError,
    replace_active_with_candidate,
)
from sudachi_life.runtime_storage import runtime_working_set_bytes
from sudachi_life.storage import connect_database, read_status

from test_phase2_absolute_idempotent_working_set import _prepared_transformed
from test_phase2_absolute_repair_active_limit import _inflate_active_freelist
from test_phase2_projection_rollback import _rollback_clock


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sparse_file(path: Path, size: int) -> None:
    assert size >= 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


def _prepared_replaced(tmp_path: Path):
    root, paths, archive, source, transformed = _prepared_transformed(tmp_path)
    replacement = replace_active_with_candidate(
        root,
        "paired",
        transformed.transformed_candidate_id,
    )
    assert replacement.status == "rollback_in_progress"
    return root, paths, archive, source, transformed, replacement


def _prepared_completed(tmp_path: Path):
    root, paths, archive, source, transformed, replacement = _prepared_replaced(
        tmp_path
    )
    completion = complete_rollback(
        root,
        "paired",
        transformed.transformed_candidate_id,
        clock=_rollback_clock(1_730_000_000_000_000, 13_000_000),
    )
    assert completion.status == "sleeping"
    return root, paths, archive, source, transformed, replacement, completion


def test_active_replacement_staging_accepts_exact_working_set_limit(
    tmp_path: Path,
) -> None:
    root, paths, _archive, _source, transformed = _prepared_transformed(tmp_path)
    current = runtime_working_set_bytes(paths)
    padding_size = (
        RUNTIME_WORKING_SET_MAX_BYTES
        - current
        - transformed.database_size_bytes
    )
    assert padding_size >= 0
    _sparse_file(paths.restore_candidates / ".replacement-exact-padding", padding_size)

    result = replace_active_with_candidate(
        root,
        "paired",
        transformed.transformed_candidate_id,
    )
    assert result.status == "rollback_in_progress"
    assert not any(
        entry.name.startswith(".tmp-active-replacement-")
        for entry in paths.organism_dir.iterdir()
    )


def test_active_replacement_staging_rejects_one_byte_over_without_mutation(
    tmp_path: Path,
) -> None:
    root, paths, _archive, _source, transformed = _prepared_transformed(tmp_path)
    current = runtime_working_set_bytes(paths)
    padding_size = (
        RUNTIME_WORKING_SET_MAX_BYTES
        - current
        - transformed.database_size_bytes
        + 1
    )
    _sparse_file(paths.restore_candidates / ".replacement-over-padding", padding_size)
    before_sha = _sha256(paths.database)
    before_status = read_status(paths)

    with pytest.raises(ActiveReplacementError, match="working-set limit"):
        replace_active_with_candidate(
            root,
            "paired",
            transformed.transformed_candidate_id,
        )

    assert _sha256(paths.database) == before_sha
    assert read_status(paths) == before_status
    assert not any(
        entry.name.startswith(".tmp-active-replacement-")
        for entry in paths.organism_dir.iterdir()
    )


def test_existing_replacement_reentry_rejects_over_limit_without_mutation(
    tmp_path: Path,
) -> None:
    root, paths, _archive, _source, transformed, _replacement = _prepared_replaced(
        tmp_path
    )
    current = runtime_working_set_bytes(paths)
    _sparse_file(
        paths.restore_candidates / ".replacement-reentry-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - current + 1,
    )
    before_sha = _sha256(paths.database)
    before_status = read_status(paths)

    with pytest.raises(ActiveReplacementError, match="runtime working set"):
        replace_active_with_candidate(
            root,
            "paired",
            transformed.transformed_candidate_id,
        )

    assert _sha256(paths.database) == before_sha
    assert read_status(paths) == before_status


def test_rollback_completion_accepts_exact_working_set_limit(tmp_path: Path) -> None:
    (
        _control_root,
        control_paths,
        _control_archive,
        _control_source,
        _control_transformed,
        _control_replacement,
        _control_completion,
    ) = _prepared_completed(tmp_path / "control")
    control_final = runtime_working_set_bytes(control_paths)

    root, paths, _archive, _source, transformed, _replacement = _prepared_replaced(
        tmp_path / "probe"
    )
    _sparse_file(
        paths.restore_candidates / ".completion-exact-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - control_final,
    )
    result = complete_rollback(
        root,
        "paired",
        transformed.transformed_candidate_id,
        clock=_rollback_clock(1_730_000_000_000_000, 13_000_000),
    )
    assert result.status == "sleeping"
    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES


def test_rollback_completion_rejects_one_byte_over_without_mutation(
    tmp_path: Path,
) -> None:
    (
        _control_root,
        control_paths,
        _control_archive,
        _control_source,
        _control_transformed,
        _control_replacement,
        _control_completion,
    ) = _prepared_completed(tmp_path / "control")
    control_final = runtime_working_set_bytes(control_paths)

    root, paths, _archive, _source, transformed, _replacement = _prepared_replaced(
        tmp_path / "probe"
    )
    _sparse_file(
        paths.restore_candidates / ".completion-over-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - control_final + 1,
    )
    before_status = read_status(paths)
    before_sha = _sha256(paths.database)
    before_ws = runtime_working_set_bytes(paths)

    with pytest.raises(RollbackCompletionRejectedError, match="runtime working set"):
        complete_rollback(
            root,
            "paired",
            transformed.transformed_candidate_id,
            clock=_rollback_clock(1_730_000_000_000_000, 13_000_000),
        )

    assert read_status(paths) == before_status
    assert _sha256(paths.database) == before_sha
    assert runtime_working_set_bytes(paths) == before_ws
    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT 1 FROM event WHERE event_type='rollback_completed'"
        ).fetchone() is None
    finally:
        connection.close()


def test_completed_rollback_reentry_rejects_over_limit_without_mutation(
    tmp_path: Path,
) -> None:
    root, paths, _archive, _source, transformed, _replacement, _completion = (
        _prepared_completed(tmp_path)
    )
    current = runtime_working_set_bytes(paths)
    _sparse_file(
        paths.restore_candidates / ".completion-reentry-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - current + 1,
    )
    before_status = read_status(paths)
    before_sha = _sha256(paths.database)

    with pytest.raises(RollbackCompletionRejectedError, match="runtime working set"):
        complete_rollback(
            root,
            "paired",
            transformed.transformed_candidate_id,
            clock=_rollback_clock(1_730_000_000_000_000, 13_000_000),
        )

    assert read_status(paths) == before_status
    assert _sha256(paths.database) == before_sha


def test_rollback_completion_accepts_active_database_at_exact_limit(
    tmp_path: Path,
) -> None:
    root, paths, _archive, _source, transformed, _replacement = _prepared_replaced(
        tmp_path
    )
    assert _inflate_active_freelist(paths.database, one_page_over=False) == (
        ACTIVE_DATABASE_MAX_BYTES
    )

    result = complete_rollback(
        root,
        "paired",
        transformed.transformed_candidate_id,
        clock=_rollback_clock(1_730_000_000_000_000, 13_000_000),
    )
    assert result.status == "sleeping"


def test_rollback_completion_rejects_active_database_one_page_over_without_mutation(
    tmp_path: Path,
) -> None:
    root, paths, _archive, _source, transformed, _replacement = _prepared_replaced(
        tmp_path
    )
    over = _inflate_active_freelist(paths.database, one_page_over=True)
    assert over > ACTIVE_DATABASE_MAX_BYTES
    before_status = read_status(paths)
    before_sha = _sha256(paths.database)

    with pytest.raises(RollbackCompletionRejectedError, match="active database"):
        complete_rollback(
            root,
            "paired",
            transformed.transformed_candidate_id,
            clock=_rollback_clock(1_730_000_000_000_000, 13_000_000),
        )

    assert read_status(paths) == before_status
    assert _sha256(paths.database) == before_sha
