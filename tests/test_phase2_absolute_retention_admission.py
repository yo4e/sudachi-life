from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.checkpoint_retention import enforce_checkpoint_retention
from sudachi_life.constants import RUNTIME_WORKING_SET_MAX_BYTES
from sudachi_life.errors import CheckpointError
from sudachi_life.runtime_storage import runtime_working_set_bytes
from sudachi_life.storage import connect_database, read_status

from test_phase2_projection_rollback import _prepared_pair


def _sparse_file(path: Path, size: int) -> None:
    assert size >= 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


def _prepared_retention(tmp_path: Path):
    _v1_root, _v1, v2_root, v2, _left, _right = _prepared_pair(tmp_path)
    connection = connect_database(v2.database, read_only=True)
    try:
        organism = connection.execute(
            "SELECT latest_stable_checkpoint_id, latest_stable_event_sequence "
            "FROM organism WHERE singleton_id=1"
        ).fetchone()
        event_count = int(connection.execute("SELECT COUNT(*) FROM event").fetchone()[0])
        registry = tuple(
            str(row[0])
            for row in connection.execute(
                "SELECT checkpoint_id FROM checkpoint_registry ORDER BY event_sequence"
            ).fetchall()
        )
    finally:
        connection.close()
    return (
        v2_root,
        v2,
        str(organism["latest_stable_checkpoint_id"]),
        int(organism["latest_stable_event_sequence"]),
        event_count,
        registry,
    )


def _assert_unchanged(paths, *, status, event_count: int, registry: tuple[str, ...]) -> None:
    assert read_status(paths) == status
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(connection.execute("SELECT COUNT(*) FROM event").fetchone()[0]) == event_count
        assert tuple(
            str(row[0])
            for row in connection.execute(
                "SELECT checkpoint_id FROM checkpoint_registry ORDER BY event_sequence"
            ).fetchall()
        ) == registry
    finally:
        connection.close()


def test_retention_admission_accepts_exact_working_set_without_mutation(
    tmp_path: Path,
) -> None:
    root, paths, latest_id, latest_event, event_count, registry = _prepared_retention(
        tmp_path
    )
    current = runtime_working_set_bytes(paths)
    _sparse_file(
        paths.restore_candidates / ".retention-exact-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - current,
    )
    before = read_status(paths)

    enforce_checkpoint_retention(
        paths,
        latest_checkpoint_id=latest_id,
        latest_event_sequence=latest_event,
        wall_time_utc_us=1_810_000_000_000_000,
    )

    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES
    _assert_unchanged(paths, status=before, event_count=event_count, registry=registry)


def test_retention_admission_rejects_one_byte_over_without_mutation(
    tmp_path: Path,
) -> None:
    _root, paths, latest_id, latest_event, event_count, registry = _prepared_retention(
        tmp_path
    )
    current = runtime_working_set_bytes(paths)
    _sparse_file(
        paths.restore_candidates / ".retention-over-padding",
        RUNTIME_WORKING_SET_MAX_BYTES - current + 1,
    )
    before = read_status(paths)

    with pytest.raises(CheckpointError, match="runtime working set"):
        enforce_checkpoint_retention(
            paths,
            latest_checkpoint_id=latest_id,
            latest_event_sequence=latest_event,
            wall_time_utc_us=1_810_000_000_000_000,
        )

    assert runtime_working_set_bytes(paths) == RUNTIME_WORKING_SET_MAX_BYTES + 1
    _assert_unchanged(paths, status=before, event_count=event_count, registry=registry)
