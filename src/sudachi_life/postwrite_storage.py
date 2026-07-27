"""Projected committed physical accounting for an open SQLite write transaction."""

from __future__ import annotations

import sqlite3

from .constants import (
    ACTIVE_DATABASE_MAX_BYTES,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from .errors import SchemaValidationError
from .paths import OrganismPaths
from .runtime_storage import active_database_allocated_bytes, tree_size_no_symlinks


def projected_committed_runtime_working_set_bytes(
    paths: OrganismPaths,
    connection: sqlite3.Connection,
) -> int:
    """Measure post-write allocation plus every non-active artifact class.

    The open rollback journal is intentionally excluded because it disappears on
    commit. SQLite page accounting already includes pages allocated by the
    uncommitted canonical writes and therefore predicts the committed database.
    """

    active_bytes = active_database_allocated_bytes(connection)
    return sum(
        (
            active_bytes,
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
    active_bytes = active_database_allocated_bytes(connection)
    if active_bytes > ACTIVE_DATABASE_MAX_BYTES:
        raise SchemaValidationError(
            f"{context}: active database exceeds protected Phase 1 limit"
        )
    size = sum(
        (
            active_bytes,
            tree_size_no_symlinks(paths.checkpoints),
            tree_size_no_symlinks(paths.rollback_archives),
            tree_size_no_symlinks(paths.restore_candidates),
        )
    )
    if size > RUNTIME_WORKING_SET_MAX_BYTES:
        raise SchemaValidationError(
            f"{context}: runtime working set exceeds protected Phase 1 limit"
        )
    return size
