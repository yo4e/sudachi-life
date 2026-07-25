"""Administrative reconciliation for committed prune staging artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sqlite3

from .checkpoint_core import _fsync_dir, validate_checkpoint_directory
from .checkpoint_retention_types import CheckpointRetentionReconciliationResult
from .clock import Clock, RealClock
from .errors import CheckpointError, OrganismNotFoundError
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state

_PENDING_EVENT_TYPE = "checkpoint_retention_cleanup_reconciliation_pending"
_COMPLETED_EVENT_TYPE = "checkpoint_retention_cleanup_reconciled"


def _decode_payload(raw: object, *, context: str) -> dict[str, object]:
    try:
        payload = json.loads(str(raw))
    except (TypeError, json.JSONDecodeError) as exc:
        raise CheckpointError(f"{context} payload is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise CheckpointError(f"{context} payload is not an object")
    return payload


def _completed_pending_sequences(connection: sqlite3.Connection) -> set[int]:
    completed: set[int] = set()
    rows = connection.execute(
        "SELECT payload_json FROM event WHERE event_type = ? ORDER BY event_sequence",
        (_COMPLETED_EVENT_TYPE,),
    ).fetchall()
    for row in rows:
        payload = _decode_payload(
            row["payload_json"],
            context="checkpoint retention cleanup completion",
        )
        value = payload.get("reconciliation_pending_event_sequence")
        if value is not None:
            completed.add(int(value))
    return completed


def _unresolved_pending_event(
    connection: sqlite3.Connection,
) -> sqlite3.Row | None:
    completed = _completed_pending_sequences(connection)
    rows = connection.execute(
        """SELECT event_sequence, wall_time_utc_us, payload_json
           FROM event WHERE event_type = ? ORDER BY event_sequence""",
        (_PENDING_EVENT_TYPE,),
    ).fetchall()
    unresolved = [row for row in rows if int(row["event_sequence"]) not in completed]
    if len(unresolved) > 1:
        raise CheckpointError(
            "multiple unresolved checkpoint-retention cleanup reconciliations exist"
        )
    return unresolved[0] if unresolved else None


def _scheduled_directories(payload: dict[str, object]) -> tuple[str, ...]:
    raw_names = payload.get("staging_directories")
    if not isinstance(raw_names, list) or not raw_names:
        raise CheckpointError(
            "checkpoint retention cleanup pending event has no staging directories"
        )
    names = tuple(str(name) for name in raw_names)
    if names != tuple(sorted(set(names))):
        raise CheckpointError(
            "checkpoint retention cleanup pending directories are not canonical"
        )
    if any(not name.startswith(".pruning-") for name in names):
        raise CheckpointError(
            "checkpoint retention cleanup pending directory has an invalid name"
        )
    return names


def _validate_committed_prune_staging(
    connection: sqlite3.Connection,
    staged_dir: Path,
) -> None:
    checkpoint_id = staged_dir.name.removeprefix(".pruning-")
    if connection.execute(
        "SELECT 1 FROM checkpoint_registry WHERE checkpoint_id = ?",
        (checkpoint_id,),
    ).fetchone() is not None:
        raise CheckpointError("retention staging still has a canonical registry row")

    pruned_events = connection.execute(
        "SELECT payload_json FROM event WHERE event_type = 'checkpoint_pruned' "
        "ORDER BY event_sequence"
    ).fetchall()
    if not any(
        _decode_payload(
            row["payload_json"],
            context="checkpoint_pruned",
        ).get("pruned_checkpoint_id")
        == checkpoint_id
        for row in pruned_events
    ):
        raise CheckpointError(
            "retention staging has no committed checkpoint_pruned audit event"
        )

    try:
        staged_manifest = json.loads(
            (staged_dir / "manifest.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckpointError("retention staging manifest is not valid JSON") from exc
    validate_checkpoint_directory(staged_dir, expected_manifest=staged_manifest)


def _insert_event(
    connection: sqlite3.Connection,
    *,
    organism: sqlite3.Row,
    wall_time_utc_us: int,
    event_type: str,
    payload: dict[str, object],
) -> int:
    cursor = connection.execute(
        """INSERT INTO event (
               organism_id, lineage_generation, lifecycle_number,
               wall_time_utc_us, event_type, source, payload_json,
               schema_version, environment_version, budget_config_version
           ) VALUES (?, ?, ?, ?, ?, 'administration:checkpoint-retention',
                     ?, ?, ?, ?)""",
        (
            organism["organism_id"],
            organism["lineage_generation"],
            organism["lifecycle_number"],
            wall_time_utc_us,
            event_type,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
            organism["schema_version"],
            organism["environment_version"],
            organism["budget_config_version"],
        ),
    )
    return int(cursor.lastrowid)


def reconcile_checkpoint_retention_staging(
    runtime_root: Path | str,
    organism_id: str,
    *,
    clock: Clock | None = None,
    protected_test_failure_after_delete_before_completion: bool = False,
) -> CheckpointRetentionReconciliationResult:
    """Reconcile committed prune staging through a durable, retryable two-step audit."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database)
    pending_event_sequence: int | None = None
    pending_wall_time_utc_us: int | None = None
    scheduled: tuple[str, ...] = ()
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
            raise CheckpointError(
                "canonical organism state is missing during retention reconciliation"
            )

        staged = tuple(
            sorted(
                path.name
                for path in paths.checkpoints.iterdir()
                if path.is_dir() and path.name.startswith(".pruning-")
            )
        )
        pending = _unresolved_pending_event(connection)
        if pending is not None:
            payload = _decode_payload(
                pending["payload_json"],
                context="checkpoint retention cleanup pending",
            )
            scheduled = _scheduled_directories(payload)
            pending_event_sequence = int(pending["event_sequence"])
            pending_wall_time_utc_us = int(pending["wall_time_utc_us"])
            unexpected = sorted(set(staged) - set(scheduled))
            if unexpected:
                raise CheckpointError(
                    "unexpected retention staging appeared during pending reconciliation: "
                    f"{unexpected!r}"
                )
        elif staged:
            for name in staged:
                _validate_committed_prune_staging(
                    connection,
                    paths.checkpoints / name,
                )
            reading = (clock or RealClock()).read()
            scheduled = staged
            pending_wall_time_utc_us = reading.wall_time_utc_us
            pending_event_sequence = _insert_event(
                connection,
                organism=organism,
                wall_time_utc_us=reading.wall_time_utc_us,
                event_type=_PENDING_EVENT_TYPE,
                payload={
                    "checkpoint_ids": [
                        name.removeprefix(".pruning-") for name in scheduled
                    ],
                    "reason": "committed_prune_cleanup_reconciliation",
                    "staging_directories": list(scheduled),
                    "status_before": organism["status"],
                },
            )
        else:
            connection.commit()
            return CheckpointRetentionReconciliationResult(
                organism_id=organism_id,
                removed_staging_directories=(),
                remaining_staging_directories=(),
                status=str(organism["status"]),
                maintenance_reason=organism["maintenance_reason"],
                audit_event_sequence=None,
            )

        for name in scheduled:
            staged_dir = paths.checkpoints / name
            if staged_dir.exists():
                _validate_committed_prune_staging(connection, staged_dir)
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()

    if pending_event_sequence is None or pending_wall_time_utc_us is None:
        raise CheckpointError("retention reconciliation pending audit was not established")

    for name in scheduled:
        staged_dir = paths.checkpoints / name
        try:
            shutil.rmtree(staged_dir)
        except FileNotFoundError:
            pass
        _fsync_dir(paths.checkpoints)

    if protected_test_failure_after_delete_before_completion:
        raise CheckpointError(
            "protected test interrupted retention reconciliation after deletion "
            "before completion audit"
        )

    completion = connect_database(paths.database)
    try:
        completion.execute("BEGIN IMMEDIATE")
        validate_canonical_state(completion, expect_checkpoint_pending=False)
        organism = completion.execute(
            """SELECT organism_id, lineage_generation, lifecycle_number, status,
                      maintenance_reason, schema_version, environment_version,
                      budget_config_version
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise CheckpointError(
                "canonical organism state is missing during retention completion"
            )
        if any((paths.checkpoints / name).exists() for name in scheduled):
            raise CheckpointError(
                "retention staging remains before reconciliation completion audit"
            )

        existing = completion.execute(
            "SELECT event_sequence, payload_json FROM event WHERE event_type = ? "
            "ORDER BY event_sequence",
            (_COMPLETED_EVENT_TYPE,),
        ).fetchall()
        audit_event_sequence = None
        for row in existing:
            payload = _decode_payload(
                row["payload_json"],
                context="checkpoint retention cleanup completion",
            )
            if int(
                payload.get("reconciliation_pending_event_sequence", -1)
            ) == pending_event_sequence:
                audit_event_sequence = int(row["event_sequence"])
                break
        if audit_event_sequence is None:
            audit_event_sequence = _insert_event(
                completion,
                organism=organism,
                wall_time_utc_us=pending_wall_time_utc_us,
                event_type=_COMPLETED_EVENT_TYPE,
                payload={
                    "reason": "committed_prune_cleanup_reconciled",
                    "reconciliation_pending_event_sequence": pending_event_sequence,
                    "removed_staging_directories": list(scheduled),
                    "status_after": organism["status"],
                },
            )
        validate_canonical_state(completion, expect_checkpoint_pending=False)
        completion.commit()
        status = str(organism["status"])
        maintenance_reason = organism["maintenance_reason"]
    except Exception:
        if completion.in_transaction:
            completion.rollback()
        raise
    finally:
        completion.close()

    remaining = tuple(
        sorted(
            path.name
            for path in paths.checkpoints.iterdir()
            if path.is_dir() and path.name.startswith(".pruning-")
        )
    )
    return CheckpointRetentionReconciliationResult(
        organism_id=organism_id,
        removed_staging_directories=scheduled,
        remaining_staging_directories=remaining,
        status=status,
        maintenance_reason=maintenance_reason,
        audit_event_sequence=audit_event_sequence,
    )
