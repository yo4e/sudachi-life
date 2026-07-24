"""Administrative reconciliation for committed prune staging artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import shutil

from .checkpoint_core import _fsync_dir, validate_checkpoint_directory
from .checkpoint_retention_types import CheckpointRetentionReconciliationResult
from .clock import Clock, RealClock
from .errors import CheckpointError, OrganismNotFoundError
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state


def reconcile_checkpoint_retention_staging(
    runtime_root: Path | str,
    organism_id: str,
    *,
    clock: Clock | None = None,
) -> CheckpointRetentionReconciliationResult:
    """Delete only committed prune staging directories and record reconciliation."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")
    connection = connect_database(paths.database)
    removed: list[str] = []
    audit_event_sequence: int | None = None
    try:
        connection.execute("BEGIN IMMEDIATE")
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            """SELECT organism_id, lineage_generation, lifecycle_number, status,
                      maintenance_reason, schema_version, environment_version,
                      budget_config_version
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        staged = sorted(
            path
            for path in paths.checkpoints.iterdir()
            if path.is_dir() and path.name.startswith(".pruning-")
        )
        for staged_dir in staged:
            checkpoint_id = staged_dir.name.removeprefix(".pruning-")
            if connection.execute(
                "SELECT 1 FROM checkpoint_registry WHERE checkpoint_id = ?",
                (checkpoint_id,),
            ).fetchone() is not None:
                raise CheckpointError(
                    "retention staging still has a canonical registry row"
                )
            pruned_events = connection.execute(
                "SELECT payload_json FROM event WHERE event_type = 'checkpoint_pruned' "
                "ORDER BY event_sequence"
            ).fetchall()
            if not any(
                json.loads(row["payload_json"]).get("pruned_checkpoint_id") == checkpoint_id
                for row in pruned_events
            ):
                raise CheckpointError(
                    "retention staging has no committed checkpoint_pruned audit event"
                )
            staged_manifest = json.loads(
                (staged_dir / "manifest.json").read_text(encoding="utf-8")
            )
            validate_checkpoint_directory(
                staged_dir, expected_manifest=staged_manifest
            )
            shutil.rmtree(staged_dir)
            _fsync_dir(paths.checkpoints)
            removed.append(staged_dir.name)

        if removed:
            reading = (clock or RealClock()).read()
            cursor = connection.execute(
                """INSERT INTO event (
                       organism_id, lineage_generation, lifecycle_number,
                       wall_time_utc_us, event_type, source, payload_json,
                       schema_version, environment_version, budget_config_version
                   ) VALUES (?, ?, ?, ?, 'checkpoint_retention_cleanup_reconciled',
                             'administration:checkpoint-retention', ?, ?, ?, ?)""",
                (
                    organism["organism_id"],
                    organism["lineage_generation"],
                    organism["lifecycle_number"],
                    reading.wall_time_utc_us,
                    json.dumps(
                        {
                            "removed_staging_directories": removed,
                            "reason": "committed_prune_cleanup_reconciled",
                            "status_after": organism["status"],
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    organism["schema_version"],
                    organism["environment_version"],
                    organism["budget_config_version"],
                ),
            )
            audit_event_sequence = int(cursor.lastrowid)
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()

    remaining = tuple(
        sorted(
            path.name
            for path in paths.checkpoints.iterdir()
            if path.is_dir() and path.name.startswith(".pruning-")
        )
    )
    status_connection = connect_database(paths.database, read_only=True)
    try:
        row = status_connection.execute(
            "SELECT status, maintenance_reason FROM organism WHERE singleton_id = 1"
        ).fetchone()
    finally:
        status_connection.close()
    return CheckpointRetentionReconciliationResult(
        organism_id=organism_id,
        removed_staging_directories=tuple(removed),
        remaining_staging_directories=remaining,
        status=str(row["status"]),
        maintenance_reason=row["maintenance_reason"],
        audit_event_sequence=audit_event_sequence,
    )
