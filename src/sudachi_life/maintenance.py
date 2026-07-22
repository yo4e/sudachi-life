"""Read-only administrative inspection for protected maintenance state."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state


class MaintenanceInspectionRejectedError(SudachiError):
    """The organism is not in a stable maintenance state that may be inspected."""


@dataclass(frozen=True, slots=True)
class StableCheckpointInspection:
    checkpoint_id: str
    lineage_generation: int
    event_sequence: int
    protected: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "lineage_generation": self.lineage_generation,
            "event_sequence": self.event_sequence,
            "protected": self.protected,
        }


@dataclass(frozen=True, slots=True)
class PendingInputInspection:
    inbox_id: int
    external_event_id: str
    event_type: str
    source: str
    claimed_lifecycle_number: int | None
    consumed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "inbox_id": self.inbox_id,
            "external_event_id": self.external_event_id,
            "event_type": self.event_type,
            "source": self.source,
            "claimed_lifecycle_number": self.claimed_lifecycle_number,
            "consumed": self.consumed,
        }


@dataclass(frozen=True, slots=True)
class MaintenanceInspection:
    organism_id: str
    lineage_generation: int
    lifecycle_number: int
    status: str
    maintenance_reason: str
    consecutive_failures: int
    checkpoint_pending: bool
    latest_stable_checkpoint: StableCheckpointInspection
    total_input_events: int
    consumed_input_events: int
    queued_unclaimed_input_events: int
    claimed_unconsumed_input_events: int
    pending_inputs: tuple[PendingInputInspection, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "organism_id": self.organism_id,
            "lineage_generation": self.lineage_generation,
            "lifecycle_number": self.lifecycle_number,
            "status": self.status,
            "maintenance_reason": self.maintenance_reason,
            "consecutive_failures": self.consecutive_failures,
            "checkpoint_pending": self.checkpoint_pending,
            "latest_stable_checkpoint": self.latest_stable_checkpoint.as_dict(),
            "input_state": {
                "total": self.total_input_events,
                "consumed": self.consumed_input_events,
                "queued_unclaimed": self.queued_unclaimed_input_events,
                "claimed_unconsumed": self.claimed_unconsumed_input_events,
                "pending": [item.as_dict() for item in self.pending_inputs],
            },
        }


def inspect_maintenance(
    runtime_root: Path | str,
    organism_id: str,
) -> MaintenanceInspection:
    """Inspect stable maintenance state without clocks, claims, events, or writes."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database, read_only=True)
    try:
        connection.execute("BEGIN")
        validate_canonical_state(connection, expect_checkpoint_pending=False)

        organism = connection.execute(
            """SELECT organism_id, lineage_generation, lifecycle_number, status,
                      checkpoint_pending, latest_stable_checkpoint_id,
                      latest_stable_event_sequence, consecutive_failures,
                      maintenance_reason
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism["status"] != "maintenance_required":
            raise MaintenanceInspectionRejectedError(
                "organism is not in maintenance_required: "
                f"status={organism['status']}"
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
            int(checkpoint["lineage_generation"])
            != int(organism["lineage_generation"])
            or int(checkpoint["event_sequence"])
            != int(organism["latest_stable_event_sequence"])
        ):
            raise SchemaValidationError(
                "latest stable checkpoint registry row does not match organism state"
            )

        counts = connection.execute(
            """SELECT COUNT(*) AS total,
                      COALESCE(SUM(CASE WHEN consumed = 1 THEN 1 ELSE 0 END), 0)
                          AS consumed,
                      COALESCE(SUM(CASE WHEN consumed = 0
                                             AND claimed_lifecycle_number IS NULL
                                        THEN 1 ELSE 0 END), 0)
                          AS queued_unclaimed,
                      COALESCE(SUM(CASE WHEN consumed = 0
                                             AND claimed_lifecycle_number IS NOT NULL
                                        THEN 1 ELSE 0 END), 0)
                          AS claimed_unconsumed
               FROM inbox_event"""
        ).fetchone()
        pending_rows = connection.execute(
            """SELECT inbox_id, external_event_id, event_type, source,
                      claimed_lifecycle_number, consumed
               FROM inbox_event
               WHERE consumed = 0
               ORDER BY inbox_id"""
        ).fetchall()

        total = int(counts["total"])
        consumed = int(counts["consumed"])
        queued_unclaimed = int(counts["queued_unclaimed"])
        claimed_unconsumed = int(counts["claimed_unconsumed"])
        if total != consumed + queued_unclaimed + claimed_unconsumed:
            raise SchemaValidationError("canonical inbox accounting is inconsistent")

        return MaintenanceInspection(
            organism_id=str(organism["organism_id"]),
            lineage_generation=int(organism["lineage_generation"]),
            lifecycle_number=int(organism["lifecycle_number"]),
            status=str(organism["status"]),
            maintenance_reason=str(organism["maintenance_reason"]),
            consecutive_failures=int(organism["consecutive_failures"]),
            checkpoint_pending=bool(organism["checkpoint_pending"]),
            latest_stable_checkpoint=StableCheckpointInspection(
                checkpoint_id=str(checkpoint["checkpoint_id"]),
                lineage_generation=int(checkpoint["lineage_generation"]),
                event_sequence=int(checkpoint["event_sequence"]),
                protected=bool(checkpoint["protected"]),
            ),
            total_input_events=total,
            consumed_input_events=consumed,
            queued_unclaimed_input_events=queued_unclaimed,
            claimed_unconsumed_input_events=claimed_unconsumed,
            pending_inputs=tuple(
                PendingInputInspection(
                    inbox_id=int(row["inbox_id"]),
                    external_event_id=str(row["external_event_id"]),
                    event_type=str(row["event_type"]),
                    source=str(row["source"]),
                    claimed_lifecycle_number=(
                        None
                        if row["claimed_lifecycle_number"] is None
                        else int(row["claimed_lifecycle_number"])
                    ),
                    consumed=bool(row["consumed"]),
                )
                for row in pending_rows
            ),
        )
    finally:
        connection.close()
