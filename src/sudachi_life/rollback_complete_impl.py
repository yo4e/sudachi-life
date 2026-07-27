"""Atomic completion of one fully replaced rollback lineage."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any

from .clock import Clock, RealClock
from .errors import OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .rollback_intent import _canonical_sqlite_snapshot
from .rollback_replace import (
    _TRANSFORMED_CANDIDATE_ID_RE,
    _read_manifest,
    _validate_artifact_chain,
    _validate_replaced,
)
from .storage import connect_database, validate_canonical_state


class RollbackCompletionBusyError(SudachiError):
    """Rollback completion could not acquire fail-fast administrative ownership."""


class RollbackCompletionRejectedError(SudachiError):
    """The replaced rollback body is not eligible for completion."""


class _InjectedRollbackCompletionFailure(Exception):
    """Protected test-only failure after completion state and event mutation."""


@dataclass(frozen=True, slots=True)
class RollbackCompletionResult:
    organism_id: str
    transformed_candidate_id: str
    archive_id: str
    selected_checkpoint_id: str
    abandoned_lineage_generation: int
    new_lineage_generation: int
    source_lifecycle_number: int
    source_event_sequence: int
    restoration_event_sequence: int
    completion_event_sequence: int
    administrative_reason: str
    queued_input_events_preserved: int
    transformed_candidate_database_sha256: str
    transformed_candidate_manifest_sha256: str
    recovered_existing_completion: bool
    status: str

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "transformed_candidate_id": self.transformed_candidate_id,
            "archive_id": self.archive_id,
            "selected_checkpoint_id": self.selected_checkpoint_id,
            "abandoned_lineage_generation": self.abandoned_lineage_generation,
            "new_lineage_generation": self.new_lineage_generation,
            "source_lifecycle_number": self.source_lifecycle_number,
            "source_event_sequence": self.source_event_sequence,
            "restoration_event_sequence": self.restoration_event_sequence,
            "completion_event_sequence": self.completion_event_sequence,
            "administrative_reason": self.administrative_reason,
            "queued_input_events_preserved": self.queued_input_events_preserved,
            "transformed_candidate_database_sha256": (
                self.transformed_candidate_database_sha256
            ),
            "transformed_candidate_manifest_sha256": (
                self.transformed_candidate_manifest_sha256
            ),
            "recovered_existing_completion": self.recovered_existing_completion,
            "status": self.status,
        }


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def _completion_payload(
    manifest: dict[str, Any],
    *,
    candidate_organism: sqlite3.Row,
    queued_input_events: int,
    transformed_candidate_manifest_sha256: str,
) -> dict[str, object]:
    return {
        "administrative_reason": manifest["administrative_reason"],
        "archive_database_sha256": manifest["archive_database_sha256"],
        "archive_id": manifest["archive_id"],
        "archive_manifest_sha256": manifest["archive_manifest_sha256"],
        "abandoned_event_sequence": manifest["abandoned_event_sequence"],
        "abandoned_lifecycle_number": manifest["abandoned_lifecycle_number"],
        "abandoned_lineage_generation": manifest["abandoned_lineage_generation"],
        "completion_event_sequence": manifest["restoration_event_sequence"] + 1,
        "consecutive_failures_after": 0,
        "consecutive_failures_before": int(candidate_organism["consecutive_failures"]),
        "implementation_version": "0.1.0",
        "maintenance_reason_before": candidate_organism["maintenance_reason"],
        "new_lineage_generation": manifest["new_lineage_generation"],
        "queued_input_events_preserved": queued_input_events,
        "replacement_validated": True,
        "restoration_event_sequence": manifest["restoration_event_sequence"],
        "rollback_started_event_sequence": manifest["rollback_started_event_sequence"],
        "selected_checkpoint_database_sha256": manifest[
            "selected_checkpoint_database_sha256"
        ],
        "selected_checkpoint_event_sequence": manifest[
            "selected_checkpoint_event_sequence"
        ],
        "selected_checkpoint_id": manifest["selected_checkpoint_id"],
        "selected_checkpoint_lineage_generation": manifest[
            "selected_checkpoint_lineage_generation"
        ],
        "selected_checkpoint_manifest_sha256": manifest[
            "selected_checkpoint_manifest_sha256"
        ],
        "source_lifecycle_number": manifest["source_lifecycle_number"],
        "source_restore_candidate_database_sha256": manifest[
            "source_restore_candidate_database_sha256"
        ],
        "source_restore_candidate_id": manifest["source_restore_candidate_id"],
        "source_restore_candidate_manifest_sha256": manifest[
            "source_restore_candidate_manifest_sha256"
        ],
        "status_after": "sleeping",
        "status_before": "rollback_in_progress",
        "transformed_candidate_database_sha256": manifest["database_sha256"],
        "transformed_candidate_id": manifest["transformed_candidate_id"],
        "transformed_candidate_manifest_sha256": transformed_candidate_manifest_sha256,
    }


def _candidate_completion_facts(context) -> tuple[sqlite3.Row, int, dict[str, object]]:
    candidate = connect_database(context.candidate_dir / "organism.sqlite3", read_only=True)
    try:
        candidate_organism = candidate.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        if candidate_organism is None:
            raise RollbackCompletionRejectedError(
                "transformed candidate organism state is missing"
            )
        queued = int(
            candidate.execute(
                "SELECT COUNT(*) FROM inbox_event WHERE consumed = 0"
            ).fetchone()[0]
        )
        payload = _completion_payload(
            context.manifest,
            candidate_organism=candidate_organism,
            queued_input_events=queued,
            transformed_candidate_manifest_sha256=context.manifest_sha256,
        )
        return candidate_organism, queued, payload
    finally:
        candidate.close()


def _validate_completed(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
    transformed_candidate_id: str,
):
    candidate_dir, manifest = _read_manifest(paths, transformed_candidate_id)
    context = _validate_artifact_chain(paths, connection, candidate_dir, manifest)
    candidate = connect_database(candidate_dir / "organism.sqlite3", read_only=True)
    try:
        candidate_organism = candidate.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        organism = connection.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        tip = connection.execute(
            "SELECT * FROM event ORDER BY event_sequence DESC LIMIT 1"
        ).fetchone()
        if candidate_organism is None or organism is None or tip is None:
            raise RollbackCompletionRejectedError(
                "completed rollback state is missing protected rows"
            )

        expected_organism = {
            "organism_id": manifest["organism_id"],
            "lineage_generation": manifest["new_lineage_generation"],
            "lifecycle_number": manifest["source_lifecycle_number"],
            "status": "sleeping",
            "checkpoint_pending": 0,
            "pending_checkpoint_generation": None,
            "pending_checkpoint_event_sequence": None,
            "latest_stable_checkpoint_id": manifest["selected_checkpoint_id"],
            "latest_stable_event_sequence": manifest["source_event_sequence"],
            "consecutive_failures": 0,
            "maintenance_reason": None,
        }
        for key, value in expected_organism.items():
            if organism[key] != value:
                raise RollbackCompletionRejectedError(
                    f"completed rollback organism does not match request: {key}"
                )
        allowed_organism_changes = {
            "status",
            "consecutive_failures",
            "maintenance_reason",
            "last_sleep_wall_time_utc_us",
        }
        for key in candidate_organism.keys():
            if key not in allowed_organism_changes and organism[key] != candidate_organism[key]:
                raise RollbackCompletionRejectedError(
                    f"rollback completion changed protected organism column: {key}"
                )

        expected_tip = {
            "event_sequence": manifest["restoration_event_sequence"] + 1,
            "organism_id": manifest["organism_id"],
            "lineage_generation": manifest["new_lineage_generation"],
            "lifecycle_number": manifest["source_lifecycle_number"],
            "event_type": "rollback_completed",
            "source": "administration:rollback",
            "schema_version": manifest["schema_version"],
            "environment_version": manifest["environment_version"],
            "budget_config_version": manifest["budget_config_version"],
        }
        for key, value in expected_tip.items():
            if tip[key] != value:
                raise RollbackCompletionRejectedError(
                    f"rollback completion event does not match request: {key}"
                )
        if organism["last_sleep_wall_time_utc_us"] != tip["wall_time_utc_us"]:
            raise RollbackCompletionRejectedError(
                "rollback completion sleep time does not match completion event"
            )

        candidate_events = candidate.execute(
            "SELECT * FROM event ORDER BY event_sequence"
        ).fetchall()
        active_events = connection.execute(
            "SELECT * FROM event ORDER BY event_sequence"
        ).fetchall()
        if [tuple(row) for row in active_events[:-1]] != [
            tuple(row) for row in candidate_events
        ]:
            raise RollbackCompletionRejectedError(
                "rollback completion did not preserve prepared history"
            )
        if len(active_events) != len(candidate_events) + 1:
            raise RollbackCompletionRejectedError(
                "rollback completion has an unexpected event count"
            )

        queued = int(
            candidate.execute(
                "SELECT COUNT(*) FROM inbox_event WHERE consumed = 0"
            ).fetchone()[0]
        )
        expected_payload = _completion_payload(
            manifest,
            candidate_organism=candidate_organism,
            queued_input_events=queued,
            transformed_candidate_manifest_sha256=context.manifest_sha256,
        )
        try:
            payload = json.loads(tip["payload_json"])
        except json.JSONDecodeError as exc:
            raise RollbackCompletionRejectedError(
                "rollback completion event payload is invalid JSON"
            ) from exc
        if payload != expected_payload:
            raise RollbackCompletionRejectedError(
                "rollback completion event payload does not match request"
            )

        active_snapshot = _canonical_sqlite_snapshot(connection)
        candidate_snapshot = _canonical_sqlite_snapshot(candidate)
        if active_snapshot["user_version"] != candidate_snapshot["user_version"]:
            raise RollbackCompletionRejectedError(
                "rollback completion changed SQLite user_version"
            )
        if active_snapshot["schema"] != candidate_snapshot["schema"]:
            raise RollbackCompletionRejectedError(
                "rollback completion changed protected schema"
            )
        active_tables = active_snapshot["tables"]
        candidate_tables = candidate_snapshot["tables"]
        if set(active_tables) != set(candidate_tables):
            raise RollbackCompletionRejectedError(
                "rollback completion changed the canonical table set"
            )
        for table_name in sorted(active_tables):
            if table_name in {"organism", "event"}:
                continue
            if active_tables[table_name] != candidate_tables[table_name]:
                raise RollbackCompletionRejectedError(
                    f"rollback completion changed protected table: {table_name}"
                )
        active_sequence = dict(active_snapshot["sqlite_sequence"])
        candidate_sequence = dict(candidate_snapshot["sqlite_sequence"])
        if set(active_sequence) != set(candidate_sequence):
            raise RollbackCompletionRejectedError(
                "rollback completion changed AUTOINCREMENT table set"
            )
        for name, candidate_value in candidate_sequence.items():
            expected_value = int(candidate_value) + 1 if name == "event" else int(candidate_value)
            if int(active_sequence[name]) != expected_value:
                raise RollbackCompletionRejectedError(
                    f"rollback completion AUTOINCREMENT mismatch: {name}"
                )
        return context, queued, tip
    finally:
        candidate.close()


def _result(
    transformed_candidate_id: str,
    context,
    *,
    queued_input_events: int,
    completion_event_sequence: int,
    recovered: bool,
) -> RollbackCompletionResult:
    manifest = context.manifest
    return RollbackCompletionResult(
        organism_id=str(manifest["organism_id"]),
        transformed_candidate_id=transformed_candidate_id,
        archive_id=str(manifest["archive_id"]),
        selected_checkpoint_id=str(manifest["selected_checkpoint_id"]),
        abandoned_lineage_generation=int(manifest["abandoned_lineage_generation"]),
        new_lineage_generation=int(manifest["new_lineage_generation"]),
        source_lifecycle_number=int(manifest["source_lifecycle_number"]),
        source_event_sequence=int(manifest["source_event_sequence"]),
        restoration_event_sequence=int(manifest["restoration_event_sequence"]),
        completion_event_sequence=completion_event_sequence,
        administrative_reason=str(manifest["administrative_reason"]),
        queued_input_events_preserved=queued_input_events,
        transformed_candidate_database_sha256=context.database_sha256,
        transformed_candidate_manifest_sha256=context.manifest_sha256,
        recovered_existing_completion=recovered,
        status="sleeping",
    )


def complete_rollback(
    runtime_root: Path | str,
    organism_id: str,
    transformed_candidate_id: str,
    *,
    clock: Clock | None = None,
    protected_test_fail_after_event_insert: bool = False,
) -> RollbackCompletionResult:
    """Atomically complete one fully validated active rollback replacement."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file() or paths.database.is_symlink():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")
    if not _TRANSFORMED_CANDIDATE_ID_RE.fullmatch(transformed_candidate_id):
        raise RollbackCompletionRejectedError(
            "transformed candidate identifier does not match the protected format"
        )

    connection = connect_database(paths.database)
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise RollbackCompletionBusyError(
                    "rollback completion is busy; this attempt was not queued"
                ) from exc
            raise
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        tip = connection.execute(
            "SELECT * FROM event ORDER BY event_sequence DESC LIMIT 1"
        ).fetchone()
        if organism is None or tip is None:
            raise RollbackCompletionRejectedError(
                "active rollback completion state is missing"
            )

        if (
            organism["status"] == "sleeping"
            and tip["event_type"] == "rollback_completed"
            and tip["source"] == "administration:rollback"
            and tip["lineage_generation"] == organism["lineage_generation"]
        ):
            context, queued, completed_tip = _validate_completed(
                connection, paths, transformed_candidate_id
            )
            connection.rollback()
            return _result(
                transformed_candidate_id,
                context,
                queued_input_events=queued,
                completion_event_sequence=int(completed_tip["event_sequence"]),
                recovered=True,
            )

        if not (
            organism["status"] == "rollback_in_progress"
            and int(organism["checkpoint_pending"]) == 0
            and tip["event_type"] == "rollback_lineage_prepared"
            and tip["source"] == "administration:rollback-candidate"
            and tip["lineage_generation"] == organism["lineage_generation"]
        ):
            raise RollbackCompletionRejectedError(
                "active database is not an exact replaced rollback body awaiting completion"
            )

        context = _validate_replaced(connection, paths, transformed_candidate_id)
        _candidate_organism, queued_before, payload = _candidate_completion_facts(context)
        queued_active = int(
            connection.execute(
                "SELECT COUNT(*) FROM inbox_event WHERE consumed = 0"
            ).fetchone()[0]
        )
        if queued_active != queued_before:
            raise RollbackCompletionRejectedError(
                "active queued input differs from the transformed candidate"
            )

        reading = (clock or RealClock()).read()
        updated = connection.execute(
            """UPDATE organism
               SET status = 'sleeping',
                   consecutive_failures = 0,
                   maintenance_reason = NULL,
                   last_sleep_wall_time_utc_us = ?
               WHERE singleton_id = 1
                 AND organism_id = ?
                 AND lineage_generation = ?
                 AND lifecycle_number = ?
                 AND status = 'rollback_in_progress'
                 AND checkpoint_pending = 0
                 AND latest_stable_checkpoint_id = ?
                 AND latest_stable_event_sequence = ?""",
            (
                reading.wall_time_utc_us,
                context.manifest["organism_id"],
                context.manifest["new_lineage_generation"],
                context.manifest["source_lifecycle_number"],
                context.manifest["selected_checkpoint_id"],
                context.manifest["source_event_sequence"],
            ),
        )
        if updated.rowcount != 1:
            raise RollbackCompletionRejectedError(
                "replaced active body changed before rollback completion"
            )

        cursor = connection.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               ) VALUES (?, ?, ?, ?, 'rollback_completed',
                         'administration:rollback', ?, ?, ?, ?)""",
            (
                context.manifest["organism_id"],
                context.manifest["new_lineage_generation"],
                context.manifest["source_lifecycle_number"],
                reading.wall_time_utc_us,
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
                context.manifest["schema_version"],
                context.manifest["environment_version"],
                context.manifest["budget_config_version"],
            ),
        )
        completion_event_sequence = int(cursor.lastrowid)
        expected_sequence = int(context.manifest["restoration_event_sequence"]) + 1
        if completion_event_sequence != expected_sequence:
            raise SchemaValidationError(
                "rollback_completed event did not append at the exact next sequence"
            )
        if protected_test_fail_after_event_insert:
            raise _InjectedRollbackCompletionFailure(
                "injected rollback completion failure after event insert"
            )

        queued_after = int(
            connection.execute(
                "SELECT COUNT(*) FROM inbox_event WHERE consumed = 0"
            ).fetchone()[0]
        )
        if queued_after != queued_before:
            raise SchemaValidationError(
                "rollback completion changed queued input state"
            )
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
        return _result(
            transformed_candidate_id,
            context,
            queued_input_events=queued_after,
            completion_event_sequence=completion_event_sequence,
            recovered=False,
        )
    except _InjectedRollbackCompletionFailure as exc:
        raise RollbackCompletionRejectedError(str(exc)) from exc
    except (RollbackCompletionBusyError, RollbackCompletionRejectedError):
        raise
    except SudachiError as exc:
        raise RollbackCompletionRejectedError(str(exc)) from exc
    finally:
        if connection.in_transaction:
            connection.rollback()
        connection.close()
