"""Explicit maintenance warning for committed retention cleanup failure."""

from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from .constants import (
    CHECKPOINT_RETENTION_LIMIT,
    MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
)
from .errors import CheckpointError
from .paths import OrganismPaths
from .runtime_storage import checkpoint_store_bytes
from .storage import connect_database, validate_canonical_state


def _record_post_commit_cleanup_warning(
    paths: OrganismPaths,
    *,
    staged_dir: Path,
    candidate: sqlite3.Row,
    latest_checkpoint_id: str,
    latest_event_sequence: int,
    wall_time_utc_us: int,
) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            """SELECT organism_id, lineage_generation, lifecycle_number, status,
                      maintenance_reason, schema_version, environment_version,
                      budget_config_version
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise CheckpointError("canonical organism state is missing during cleanup warning")
        status_after = str(organism["status"])
        maintenance_reason = organism["maintenance_reason"]
        if status_after == "sleeping":
            connection.execute(
                """UPDATE organism
                   SET status = 'maintenance_required', maintenance_reason = ?
                   WHERE singleton_id = 1 AND status = 'sleeping'
                         AND checkpoint_pending = 0""",
                (MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,),
            )
            status_after = "maintenance_required"
            maintenance_reason = MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED
        elif status_after != "maintenance_required":
            raise CheckpointError(
                f"retention cleanup warning cannot classify status={status_after}"
            )

        rows = connection.execute(
            "SELECT checkpoint_id, event_sequence FROM checkpoint_registry "
            "ORDER BY event_sequence, checkpoint_id"
        ).fetchall()
        payload = {
            "candidate_checkpoint_id": str(candidate["checkpoint_id"]),
            "candidate_event_sequence": int(candidate["event_sequence"]),
            "candidate_restored": False,
            "checkpoint_store_bytes": checkpoint_store_bytes(paths),
            "injection_point": "after_registry_commit_before_staging_cleanup",
            "latest_stable_checkpoint_id": latest_checkpoint_id,
            "latest_stable_event_sequence": latest_event_sequence,
            "maintenance_reason": maintenance_reason,
            "reason": "post_commit_staging_cleanup_failed",
            "registered_checkpoint_boundaries": [int(row["event_sequence"]) for row in rows],
            "registered_checkpoint_count": len(rows),
            "retention_limit": CHECKPOINT_RETENTION_LIMIT,
            "stable_checkpoint_count": len(rows),
            "staging_directory": staged_dir.name,
            "status_after": status_after,
        }
        connection.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               ) VALUES (?, ?, ?, ?, 'checkpoint_retention_failed',
                         'administration:checkpoint-retention', ?, ?, ?, ?)""",
            (
                organism["organism_id"],
                organism["lineage_generation"],
                organism["lifecycle_number"],
                wall_time_utc_us,
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
                organism["schema_version"],
                organism["environment_version"],
                organism["budget_config_version"],
            ),
        )
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()
