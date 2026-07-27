"""Projected committed working-set accounting for an open SQLite write transaction."""

from __future__ import annotations

import sqlite3

from .constants import RUNTIME_WORKING_SET_MAX_BYTES
from .errors import SchemaValidationError
from .paths import OrganismPaths
from .runtime_storage import active_database_allocated_bytes, tree_size_no_symlinks


def projected_committed_runtime_working_set_bytes(
    paths: OrganismPaths,
    connection: sqlite3.Connection,
) -> int:
    """Measure the post-write allocation plus every non-active artifact class.

    The open rollback journal is intentionally excluded: it disappears on commit.
    The connection's page accounting already includes pages allocated by the
    uncommitted canonical writes and therefore predicts the committed database.
    """

    return sum(
        (
            active_database_allocated_bytes(connection),
            tree_size_no_symlinks(paths.checkpoints),
            tree_size_no_symlinks(paths.rollback_archives),
            tree_size_no_symlinks(paths.restore_candidates),
        )
    )


def ensure_projected_committed_runtime_working_set_within_limit(
    paths: OrganismPaths,
    connection: sqlite3.Connection,
    *,
    context: str,
) -> int:
    size = projected_committed_runtime_working_set_bytes(paths, connection)
    if size > RUNTIME_WORKING_SET_MAX_BYTES:
        raise SchemaValidationError(
            f"{context}: runtime working set exceeds protected Phase 1 limit"
        )
    return size
