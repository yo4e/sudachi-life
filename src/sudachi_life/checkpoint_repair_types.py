"""Types and validation helpers for pending-checkpoint registration repair."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sqlite3

from .constants import (
    CONSECUTIVE_FAILURE_LIMIT,
    MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
)
from .errors import SudachiError
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state


class PendingCheckpointRepairBusyError(SudachiError):
    """The administrative checkpoint-repair transaction could not acquire ownership."""


class PendingCheckpointRepairRejectedError(SudachiError):
    """Canonical state or published artifacts are not eligible for exact repair."""


@dataclass(frozen=True, slots=True)
class PendingCheckpointRepairResult:
    organism_id: str
    status_before: str
    status: str
    checkpoint_id: str
    lineage_generation: int
    event_sequence: int
    previous_latest_stable_checkpoint_id: str | None
    previous_latest_stable_event_sequence: int
    registered_checkpoint_count: int
    checkpoint_store_bytes: int
    audit_event_sequence: int

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "status_before": self.status_before,
            "status": self.status,
            "checkpoint_id": self.checkpoint_id,
            "lineage_generation": self.lineage_generation,
            "event_sequence": self.event_sequence,
            "previous_latest_stable_checkpoint_id": self.previous_latest_stable_checkpoint_id,
            "previous_latest_stable_event_sequence": self.previous_latest_stable_event_sequence,
            "registered_checkpoint_count": self.registered_checkpoint_count,
            "checkpoint_store_bytes": self.checkpoint_store_bytes,
            "audit_event_sequence": self.audit_event_sequence,
        }


@dataclass(frozen=True, slots=True)
class PendingCheckpointCandidate:
    organism: sqlite3.Row
    pending_generation: int
    pending_boundary: int
    previous_checkpoint_id: str | None
    previous_boundary: int
    final_status: str
    candidate_dir: Path
    candidate_manifest: dict[str, object]
    expected_checkpoint_id: str
    checkpoint_store_bytes_before: int


def is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(connection: sqlite3.Connection, query: str) -> tuple[tuple[object, ...], ...]:
    return tuple(tuple(row) for row in connection.execute(query).fetchall())


def validate_snapshot_matches_pending_canonical(
    active: sqlite3.Connection,
    checkpoint_dir: Path,
) -> None:
    snapshot = connect_database(checkpoint_dir / "organism.sqlite3", read_only=True)
    try:
        validate_canonical_state(snapshot, expect_checkpoint_pending=True)
        organism_query = """
            SELECT organism_id, contract_version, schema_version, environment_version,
                   budget_config_version, lineage_generation, developmental_stage,
                   created_wall_time_utc_us, lifecycle_number, status,
                   checkpoint_pending, pending_checkpoint_generation,
                   pending_checkpoint_event_sequence, latest_stable_checkpoint_id,
                   latest_stable_event_sequence, consecutive_failures,
                   maintenance_reason, last_wake_wall_time_utc_us,
                   last_sleep_wall_time_utc_us
            FROM organism WHERE singleton_id = 1
        """
        active_organism = active.execute(organism_query).fetchone()
        snapshot_organism = snapshot.execute(organism_query).fetchone()
        if active_organism is None or snapshot_organism is None:
            raise PendingCheckpointRepairRejectedError(
                "pending checkpoint snapshot has no canonical organism row"
            )
        if tuple(active_organism) != tuple(snapshot_organism):
            raise PendingCheckpointRepairRejectedError(
                "published checkpoint does not match the exact canonical pending organism state"
            )
        table_queries = (
            "SELECT singleton_id, config_version, config_json FROM budget_config ORDER BY singleton_id",
            "SELECT singleton_id, environment_version, environment_step, objective_complete "
            "FROM environment_state ORDER BY singleton_id",
            "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id",
            "SELECT singleton_id, water_units, harvested_fruit FROM inventory ORDER BY singleton_id",
            "SELECT action_id, version, deterministic, protected FROM action_definition ORDER BY action_id",
            "SELECT inbox_id, external_event_id, event_type, source, source_wall_time_utc_us, "
            "received_wall_time_utc_us, claimed_lifecycle_number, consumed "
            "FROM inbox_event ORDER BY inbox_id",
            "SELECT event_sequence, organism_id, lineage_generation, lifecycle_number, "
            "wall_time_utc_us, event_type, source, payload_json, schema_version, "
            "environment_version, budget_config_version FROM event ORDER BY event_sequence",
            "SELECT checkpoint_id, lineage_generation, event_sequence, manifest_sha256, "
            "database_sha256, database_size_bytes, created_wall_time_utc_us, "
            "registered_wall_time_utc_us, protected FROM checkpoint_registry "
            "ORDER BY event_sequence, checkpoint_id",
        )
        for query in table_queries:
            if rows(active, query) != rows(snapshot, query):
                raise PendingCheckpointRepairRejectedError(
                    "published checkpoint snapshot differs from canonical pending state"
                )
    finally:
        snapshot.close()


def final_status(organism: sqlite3.Row) -> str:
    failure_streak = int(organism["consecutive_failures"])
    maintenance_reason = organism["maintenance_reason"]
    if failure_streak >= CONSECUTIVE_FAILURE_LIMIT:
        if maintenance_reason != MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT:
            raise PendingCheckpointRepairRejectedError(
                "failure-threshold pending checkpoint has no protected maintenance reason"
            )
        return "maintenance_required"
    if maintenance_reason is not None:
        return "maintenance_required"
    return "sleeping"
