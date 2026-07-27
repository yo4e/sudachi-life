from __future__ import annotations

from pathlib import Path
import sqlite3

import pytest

from sudachi_life.checkpoint_repair import (
    PendingCheckpointRepairRejectedError,
    repair_pending_checkpoint_registration,
)
from sudachi_life.constants import ACTIVE_DATABASE_MAX_BYTES
from sudachi_life.runtime_storage import active_database_allocated_bytes
from sudachi_life.storage import connect_database, read_status, validate_canonical_state

from test_phase2_checkpoint_artifact_exact_limit import _published_pending_orphan
from test_phase2_projection_rollback import _rollback_clock


def _inflate_active_freelist(database: Path, *, one_page_over: bool) -> int:
    connection = sqlite3.connect(database, isolation_level=None)
    try:
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute("CREATE TABLE active_limit_padding (value BLOB NOT NULL)")
        while True:
            page_count = int(connection.execute("PRAGMA page_count").fetchone()[0])
            page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
            allocated = page_count * page_size
            target_reached = (
                allocated > ACTIVE_DATABASE_MAX_BYTES
                if one_page_over
                else allocated >= ACTIVE_DATABASE_MAX_BYTES
            )
            if target_reached:
                break
            remaining = ACTIVE_DATABASE_MAX_BYTES - allocated
            payload = 64 * 1024 if remaining > 128 * 1024 else 512
            connection.execute(
                "INSERT INTO active_limit_padding(value) VALUES (zeroblob(?))",
                (payload,),
            )
        connection.execute("DROP TABLE active_limit_padding")
        page_count = int(connection.execute("PRAGMA page_count").fetchone()[0])
        page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
    finally:
        connection.close()
    allocated = page_count * page_size
    if one_page_over:
        assert allocated > ACTIVE_DATABASE_MAX_BYTES
    else:
        assert allocated == ACTIVE_DATABASE_MAX_BYTES
    return allocated


def _active_allocated(database: Path) -> int:
    connection = connect_database(database, read_only=True)
    try:
        return active_database_allocated_bytes(connection)
    finally:
        connection.close()


def test_pending_repair_accepts_active_database_at_exact_limit(tmp_path: Path) -> None:
    runtime_root, paths, orphan = _published_pending_orphan(tmp_path)
    assert _inflate_active_freelist(paths.database, one_page_over=False) == (
        ACTIVE_DATABASE_MAX_BYTES
    )
    snapshot = connect_database(paths.database, read_only=True)
    try:
        validate_canonical_state(snapshot, expect_checkpoint_pending=True)
    finally:
        snapshot.close()

    result = repair_pending_checkpoint_registration(
        runtime_root,
        paths.organism_id,
        clock=_rollback_clock(1_800_000_000_000_000, 100_000_000),
    )
    assert result.checkpoint_id == orphan.name
    assert _active_allocated(paths.database) == ACTIVE_DATABASE_MAX_BYTES


def test_pending_repair_rejects_active_database_one_page_over_without_mutation(
    tmp_path: Path,
) -> None:
    runtime_root, paths, orphan = _published_pending_orphan(tmp_path)
    over = _inflate_active_freelist(paths.database, one_page_over=True)
    assert over > ACTIVE_DATABASE_MAX_BYTES
    snapshot = connect_database(paths.database, read_only=True)
    try:
        validate_canonical_state(snapshot, expect_checkpoint_pending=True)
    finally:
        snapshot.close()
    before = read_status(paths)

    with pytest.raises(
        PendingCheckpointRepairRejectedError,
        match="active database",
    ):
        repair_pending_checkpoint_registration(
            runtime_root,
            paths.organism_id,
            clock=_rollback_clock(1_800_000_000_000_000, 100_000_000),
        )

    assert read_status(paths) == before
    assert _active_allocated(paths.database) == over
    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT 1 FROM checkpoint_registry WHERE checkpoint_id=?",
            (orphan.name,),
        ).fetchone() is None
    finally:
        connection.close()
    assert orphan.is_dir()
