"""Protected no-symlink Phase 1 storage accounting."""

from __future__ import annotations

import os
from pathlib import Path
import sqlite3

from .constants import (
    ACTIVE_DATABASE_MAX_BYTES,
    CHECKPOINT_STORE_MAX_BYTES,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from .errors import SchemaValidationError
from .paths import OrganismPaths

_SQLITE_SIDECAR_SUFFIXES = ("-journal", "-wal", "-shm")


def _file_size_no_symlink(path: Path) -> int:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return 0
    if path.is_symlink():
        raise SchemaValidationError(f"protected storage path may not be a symlink: {path}")
    if not path.is_file():
        raise SchemaValidationError(f"protected storage entry is not a regular file: {path}")
    return int(metadata.st_size)


def tree_size_no_symlinks(root: Path) -> int:
    """Return regular-file bytes beneath root without following symlinks."""

    try:
        if root.is_symlink():
            raise SchemaValidationError(
                f"protected storage directory may not be a symlink: {root}"
            )
        entries = list(os.scandir(root))
    except FileNotFoundError:
        return 0
    if not root.is_dir():
        raise SchemaValidationError(f"protected storage root is not a directory: {root}")

    total = 0
    pending = entries
    while pending:
        entry = pending.pop()
        path = Path(entry.path)
        if entry.is_symlink():
            raise SchemaValidationError(
                f"protected storage entry may not be a symlink: {path}"
            )
        if entry.is_file(follow_symlinks=False):
            total += int(entry.stat(follow_symlinks=False).st_size)
        elif entry.is_dir(follow_symlinks=False):
            pending.extend(os.scandir(path))
        else:
            raise SchemaValidationError(
                f"protected storage entry is not a regular file or directory: {path}"
            )
    return total


def active_database_allocated_bytes(connection: sqlite3.Connection) -> int:
    page_count = int(connection.execute("PRAGMA page_count").fetchone()[0])
    page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
    if page_count < 0 or page_size <= 0:
        raise SchemaValidationError("SQLite active-database page accounting is invalid")
    return page_count * page_size


def active_database_files_bytes(paths: OrganismPaths) -> int:
    total = _file_size_no_symlink(paths.database)
    database_text = str(paths.database)
    for suffix in _SQLITE_SIDECAR_SUFFIXES:
        total += _file_size_no_symlink(Path(database_text + suffix))
    return total


def checkpoint_store_bytes(paths: OrganismPaths) -> int:
    return tree_size_no_symlinks(paths.checkpoints)


def runtime_working_set_bytes(paths: OrganismPaths) -> int:
    """Account for every protected Phase 1 runtime artifact class."""

    return sum(
        (
            active_database_files_bytes(paths),
            checkpoint_store_bytes(paths),
            tree_size_no_symlinks(paths.rollback_archives),
            tree_size_no_symlinks(paths.restore_candidates),
        )
    )


def ensure_active_database_within_limit(
    connection: sqlite3.Connection,
    *,
    context: str,
    limit: int | None = None,
) -> int:
    if limit is None:
        limit = ACTIVE_DATABASE_MAX_BYTES
    size = active_database_allocated_bytes(connection)
    if size > limit:
        raise SchemaValidationError(
            f"{context}: active database would exceed protected Phase 1 limit"
        )
    return size


def ensure_checkpoint_store_within_limit(
    paths: OrganismPaths,
    *,
    context: str,
    limit: int | None = None,
) -> int:
    if limit is None:
        limit = CHECKPOINT_STORE_MAX_BYTES
    size = checkpoint_store_bytes(paths)
    if size > limit:
        raise SchemaValidationError(
            f"{context}: checkpoint store exceeds protected Phase 1 limit"
        )
    return size


def ensure_runtime_working_set_within_limit(
    paths: OrganismPaths,
    *,
    context: str,
    additional_bytes: int = 0,
    limit: int | None = None,
) -> int:
    if limit is None:
        limit = RUNTIME_WORKING_SET_MAX_BYTES
    if additional_bytes < 0:
        raise SchemaValidationError("projected protected storage bytes may not be negative")
    size = runtime_working_set_bytes(paths) + additional_bytes
    if size > limit:
        raise SchemaValidationError(
            f"{context}: runtime working set exceeds protected Phase 1 limit"
        )
    return size
