"""Explicit administrative repair for one published pending checkpoint."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from .checkpoint_repair_commit import commit_pending_checkpoint_candidate
from .checkpoint_repair_types import (
    PendingCheckpointRepairBusyError,
    PendingCheckpointRepairRejectedError,
    PendingCheckpointRepairResult,
    is_busy,
)
from .checkpoint_repair_validate import validate_pending_checkpoint_candidate
from .checkpoint_retention import enforce_checkpoint_retention
from .clock import Clock, RealClock
from .errors import CheckpointError, OrganismNotFoundError, SchemaValidationError
from .paths import OrganismPaths
from .runtime_storage import checkpoint_store_bytes
from .storage import connect_database


def repair_pending_checkpoint_registration(
    runtime_root: Path | str,
    organism_id: str,
    *,
    clock: Clock | None = None,
) -> PendingCheckpointRepairResult:
    """Register exactly one fully validated published orphan and clear pending state."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")
    connection = connect_database(paths.database)
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if is_busy(exc):
                raise PendingCheckpointRepairBusyError(
                    "pending checkpoint repair is busy; this attempt was not queued"
                ) from exc
            raise
        candidate = validate_pending_checkpoint_candidate(connection, paths)
        audit_event_sequence, wall_time_utc_us = commit_pending_checkpoint_candidate(
            connection,
            candidate,
            clock=clock or RealClock(),
        )
    except PendingCheckpointRepairBusyError:
        raise
    except PendingCheckpointRepairRejectedError:
        if connection.in_transaction:
            connection.rollback()
        raise
    except (CheckpointError, SchemaValidationError, sqlite3.Error, OSError, ValueError) as exc:
        if connection.in_transaction:
            connection.rollback()
        raise PendingCheckpointRepairRejectedError(str(exc)) from exc
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()

    enforce_checkpoint_retention(
        paths,
        latest_checkpoint_id=candidate.expected_checkpoint_id,
        latest_event_sequence=candidate.pending_boundary,
        wall_time_utc_us=wall_time_utc_us,
    )
    final_connection = connect_database(paths.database, read_only=True)
    try:
        final_row = final_connection.execute(
            "SELECT status FROM organism WHERE singleton_id = 1"
        ).fetchone()
        registered_count = int(
            final_connection.execute("SELECT COUNT(*) FROM checkpoint_registry").fetchone()[0]
        )
    finally:
        final_connection.close()
    return PendingCheckpointRepairResult(
        organism_id=str(candidate.organism["organism_id"]),
        status_before="checkpoint_pending",
        status=str(final_row["status"]),
        checkpoint_id=candidate.expected_checkpoint_id,
        lineage_generation=candidate.pending_generation,
        event_sequence=candidate.pending_boundary,
        previous_latest_stable_checkpoint_id=candidate.previous_checkpoint_id,
        previous_latest_stable_event_sequence=candidate.previous_boundary,
        registered_checkpoint_count=registered_count,
        checkpoint_store_bytes=checkpoint_store_bytes(paths),
        audit_event_sequence=audit_event_sequence,
    )


__all__ = [
    "PendingCheckpointRepairBusyError",
    "PendingCheckpointRepairRejectedError",
    "PendingCheckpointRepairResult",
    "repair_pending_checkpoint_registration",
]
