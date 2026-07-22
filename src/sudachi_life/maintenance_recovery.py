"""Explicit administrative recovery from protected maintenance state."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import sqlite3

from .clock import Clock, RealClock
from .constants import (
    CONSECUTIVE_FAILURE_LIMIT,
    MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
)
from .errors import OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state

_RECOVERY_REASON_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class InvalidMaintenanceRecoveryReasonError(SudachiError):
    """The caller-supplied administrative recovery reason is invalid."""


class MaintenanceClearBusyError(SudachiError):
    """The administrative maintenance-clear transaction could not acquire ownership."""


class MaintenanceClearRejectedError(SudachiError):
    """Canonical state is not eligible for the protected maintenance clear."""


@dataclass(frozen=True, slots=True)
class MaintenanceClearResult:
    organism_id: str
    previous_status: str
    status: str
    previous_maintenance_reason: str
    recovery_reason: str
    consecutive_failures_before: int
    consecutive_failures_after: int
    latest_stable_checkpoint_id: str
    latest_stable_event_sequence: int
    queued_input_events_preserved: int
    audit_event_sequence: int

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "previous_status": self.previous_status,
            "status": self.status,
            "previous_maintenance_reason": self.previous_maintenance_reason,
            "recovery_reason": self.recovery_reason,
            "consecutive_failures_before": self.consecutive_failures_before,
            "consecutive_failures_after": self.consecutive_failures_after,
            "latest_stable_checkpoint_id": self.latest_stable_checkpoint_id,
            "latest_stable_event_sequence": self.latest_stable_event_sequence,
            "queued_input_events_preserved": self.queued_input_events_preserved,
            "audit_event_sequence": self.audit_event_sequence,
        }


def validate_maintenance_recovery_reason(recovery_reason: str) -> str:
    if not _RECOVERY_REASON_RE.fullmatch(recovery_reason):
        raise InvalidMaintenanceRecoveryReasonError(
            "maintenance recovery reason must be 1-128 ASCII letters, digits, dots, "
            "underscores, colons, or hyphens and must start with a letter or digit"
        )
    return recovery_reason


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def clear_maintenance(
    runtime_root: Path | str,
    organism_id: str,
    recovery_reason: str,
    *,
    clock: Clock | None = None,
) -> MaintenanceClearResult:
    """Clear the protected consecutive-failure maintenance condition atomically."""

    recovery_reason = validate_maintenance_recovery_reason(recovery_reason)
    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database)
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise MaintenanceClearBusyError(
                    "organism maintenance clear is busy; this attempt was not queued"
                ) from exc
            raise

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            """SELECT organism_id, lineage_generation, lifecycle_number, status,
                      checkpoint_pending, latest_stable_checkpoint_id,
                      latest_stable_event_sequence, consecutive_failures,
                      maintenance_reason, schema_version, environment_version,
                      budget_config_version
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise MaintenanceClearRejectedError("canonical organism state is missing")
        if organism["status"] != "maintenance_required":
            raise MaintenanceClearRejectedError(
                "organism is not eligible for maintenance clear: "
                f"status={organism['status']}"
            )
        if int(organism["consecutive_failures"]) != CONSECUTIVE_FAILURE_LIMIT:
            raise MaintenanceClearRejectedError(
                "maintenance clear requires the exact protected failure threshold"
            )
        if organism["maintenance_reason"] != MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT:
            raise MaintenanceClearRejectedError(
                "maintenance clear does not support the canonical maintenance reason"
            )

        checkpoint_id = organism["latest_stable_checkpoint_id"]
        if checkpoint_id is None:
            raise SchemaValidationError(
                "maintenance state has no latest stable checkpoint identifier"
            )
        checkpoint = connection.execute(
            """SELECT checkpoint_id, lineage_generation, event_sequence, protected
               FROM checkpoint_registry WHERE checkpoint_id = ?""",
            (checkpoint_id,),
        ).fetchone()
        if checkpoint is None:
            raise SchemaValidationError(
                "latest stable checkpoint is missing from the canonical registry"
            )
        if (
            int(checkpoint["lineage_generation"]) != int(organism["lineage_generation"])
            or int(checkpoint["event_sequence"])
            != int(organism["latest_stable_event_sequence"])
            or int(checkpoint["protected"]) != 1
        ):
            raise SchemaValidationError(
                "latest stable checkpoint registry row does not match protected organism state"
            )

        queued_before = int(
            connection.execute(
                "SELECT COUNT(*) FROM inbox_event WHERE consumed = 0"
            ).fetchone()[0]
        )
        reading = (clock or RealClock()).read()

        cursor = connection.execute(
            """UPDATE organism
               SET status = 'sleeping', consecutive_failures = 0,
                   maintenance_reason = NULL, last_sleep_wall_time_utc_us = ?
               WHERE singleton_id = 1 AND status = 'maintenance_required'
                     AND checkpoint_pending = 0 AND consecutive_failures = ?
                     AND maintenance_reason = ?""",
            (
                reading.wall_time_utc_us,
                CONSECUTIVE_FAILURE_LIMIT,
                MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            ),
        )
        if cursor.rowcount != 1:
            raise MaintenanceClearRejectedError(
                "canonical maintenance state changed before clear"
            )

        payload = {
            "checkpoint_event_sequence": int(organism["latest_stable_event_sequence"]),
            "checkpoint_id": str(checkpoint_id),
            "consecutive_failures_after": 0,
            "consecutive_failures_before": CONSECUTIVE_FAILURE_LIMIT,
            "maintenance_reason_before": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            "recovery_reason": recovery_reason,
            "status_after": "sleeping",
            "status_before": "maintenance_required",
        }
        event_cursor = connection.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               ) VALUES (?, ?, ?, ?, 'maintenance_cleared',
                         'administration:maintenance-clear', ?, ?, ?, ?)""",
            (
                organism["organism_id"],
                organism["lineage_generation"],
                organism["lifecycle_number"],
                reading.wall_time_utc_us,
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
                organism["schema_version"],
                organism["environment_version"],
                organism["budget_config_version"],
            ),
        )
        audit_event_sequence = int(event_cursor.lastrowid)

        queued_after = int(
            connection.execute(
                "SELECT COUNT(*) FROM inbox_event WHERE consumed = 0"
            ).fetchone()[0]
        )
        if queued_after != queued_before:
            raise SchemaValidationError(
                "maintenance clear changed queued input state"
            )

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
        return MaintenanceClearResult(
            organism_id=str(organism["organism_id"]),
            previous_status="maintenance_required",
            status="sleeping",
            previous_maintenance_reason=MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            recovery_reason=recovery_reason,
            consecutive_failures_before=CONSECUTIVE_FAILURE_LIMIT,
            consecutive_failures_after=0,
            latest_stable_checkpoint_id=str(checkpoint_id),
            latest_stable_event_sequence=int(organism["latest_stable_event_sequence"]),
            queued_input_events_preserved=queued_after,
            audit_event_sequence=audit_event_sequence,
        )
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()
