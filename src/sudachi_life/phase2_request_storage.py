"""Physical admission for the optional schema-v2 request extension."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

from .constants import (
    ACTIVE_DATABASE_MAX_BYTES,
    CHECKPOINT_STORE_MAX_BYTES,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from .paths import OrganismPaths
from .runtime_storage import (
    ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
    active_database_allocated_bytes,
    active_database_files_bytes,
    checkpoint_store_bytes,
    runtime_working_set_bytes,
)

# Checkpoint creation already reserves 4096 bytes for the canonical manifest.
# The request extension uses the same established allowance without changing the
# protected checkpoint format or any accepted limit.
CHECKPOINT_MANIFEST_ALLOWANCE_BYTES = 4096

# B-tree cell headers, primary/unique indexes, and the final checkpoint-pending
# event need bounded page headroom beyond the measured canonical request bytes.
# Actual allocation is measured again before the extension savepoint is released.
REQUEST_BTREE_OVERHEAD_PAGES = 4
CHECKPOINT_TAIL_ALLOWANCE_PAGES = 2


@dataclass(frozen=True, slots=True)
class RequestStorageProjection:
    active_allocated_bytes: int
    active_sidecar_bytes: int
    projected_active_bytes: int
    projected_active_files_bytes: int
    projected_checkpoint_bytes: int
    projected_checkpoint_store_bytes: int
    projected_working_set_bytes: int
    reserve_bytes: int
    admissible: bool


def _page_size(connection: sqlite3.Connection) -> int:
    page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
    if page_size <= 0:
        raise ValueError("SQLite request-extension page size is invalid")
    return page_size


def _round_pages(value: int, page_size: int) -> int:
    if value < 0:
        raise ValueError("request-extension projected bytes may not be negative")
    return ((value + page_size - 1) // page_size) * page_size


def _projection(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
    *,
    request_row_bytes: int,
    request_event_bytes: int,
    include_request_growth: bool,
) -> RequestStorageProjection:
    page_size = _page_size(connection)
    active_allocated = active_database_allocated_bytes(connection)
    active_files = active_database_files_bytes(paths)
    database_size = paths.database.stat().st_size
    sidecars = max(0, active_files - database_size)

    if include_request_growth:
        measured_request_bytes = request_row_bytes + request_event_bytes
        request_growth = _round_pages(measured_request_bytes, page_size)
        request_growth += REQUEST_BTREE_OVERHEAD_PAGES * page_size
    else:
        request_growth = 0
    tail_growth = CHECKPOINT_TAIL_ALLOWANCE_PAGES * page_size
    projected_active = active_allocated + request_growth + tail_growth
    projected_active_files = projected_active + sidecars
    projected_checkpoint = projected_active + CHECKPOINT_MANIFEST_ALLOWANCE_BYTES
    projected_checkpoint_store = checkpoint_store_bytes(paths) + projected_checkpoint

    current_working_set = runtime_working_set_bytes(paths)
    current_active_main = database_size
    projected_main_growth = max(0, projected_active - current_active_main)
    projected_working_set = (
        current_working_set + projected_main_growth + projected_checkpoint
    )

    admissible = all(
        (
            projected_active_files + ACTIVE_DATABASE_WAKE_RESERVE_BYTES
            <= ACTIVE_DATABASE_MAX_BYTES,
            projected_checkpoint_store <= CHECKPOINT_STORE_MAX_BYTES,
            projected_working_set <= RUNTIME_WORKING_SET_MAX_BYTES,
        )
    )
    return RequestStorageProjection(
        active_allocated_bytes=active_allocated,
        active_sidecar_bytes=sidecars,
        projected_active_bytes=projected_active,
        projected_active_files_bytes=projected_active_files,
        projected_checkpoint_bytes=projected_checkpoint,
        projected_checkpoint_store_bytes=projected_checkpoint_store,
        projected_working_set_bytes=projected_working_set,
        reserve_bytes=ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
        admissible=admissible,
    )


def project_request_storage_before_write(
    connection: sqlite3.Connection,
    *,
    runtime_root: Path,
    organism_id: str,
    request_row_bytes: int,
    request_event_bytes: int,
) -> RequestStorageProjection:
    """Conservatively project the complete optional extension and checkpoint."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    return _projection(
        connection,
        paths,
        request_row_bytes=request_row_bytes,
        request_event_bytes=request_event_bytes,
        include_request_growth=True,
    )


def project_request_storage_after_write(
    connection: sqlite3.Connection,
    *,
    runtime_root: Path,
    organism_id: str,
) -> RequestStorageProjection:
    """Measure actual request pages and project only the remaining core tail."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    return _projection(
        connection,
        paths,
        request_row_bytes=0,
        request_event_bytes=0,
        include_request_growth=False,
    )
