"""Explicit administrative repair for one published pending checkpoint."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3

from .checkpoints import validate_checkpoint_directory
from .clock import Clock, RealClock
from .constants import (
    CHECKPOINT_STORE_MAX_BYTES,
    CONSECUTIVE_FAILURE_LIMIT,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from .errors import (
    CheckpointError,
    OrganismNotFoundError,
    SchemaValidationError,
    SudachiError,
)
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
    previous_latest_stable_checkpoint_id: str
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
            "previous_latest_stable_checkpoint_id": (
                self.previous_latest_stable_checkpoint_id
            ),
            "previous_latest_stable_event_sequence": (
                self.previous_latest_stable_event_sequence
            ),
            "registered_checkpoint_count": self.registered_checkpoint_count,
            "checkpoint_store_bytes": self.checkpoint_store_bytes,
            "audit_event_sequence": self.audit_event_sequence,
        }


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checkpoint_store_size(checkpoints_dir: Path) -> int:
    total = 0
    for path in checkpoints_dir.rglob("*"):
        if path.is_file() and not path.is_symlink():
            total += path.stat().st_size
    return total


def _rows(connection: sqlite3.Connection, query: str) -> tuple[tuple[object, ...], ...]:
    return tuple(tuple(row) for row in connection.execute(query).fetchall())


def _validate_snapshot_matches_pending_canonical(
    active: sqlite3.Connection,
    checkpoint_dir: Path,
) -> None:
    """Prove the published snapshot is the exact committed pending state."""

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
            if _rows(active, query) != _rows(snapshot, query):
                raise PendingCheckpointRepairRejectedError(
                    "published checkpoint snapshot differs from canonical pending state"
                )
    finally:
        snapshot.close()


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
            if _is_busy(exc):
                raise PendingCheckpointRepairBusyError(
                    "pending checkpoint repair is busy; this attempt was not queued"
                ) from exc
            raise

        validate_canonical_state(connection, expect_checkpoint_pending=True)
        organism = connection.execute(
            """SELECT organism_id, contract_version, schema_version,
                      environment_version, budget_config_version,
                      lineage_generation, lifecycle_number, status,
                      checkpoint_pending, pending_checkpoint_generation,
                      pending_checkpoint_event_sequence,
                      latest_stable_checkpoint_id,
                      latest_stable_event_sequence, consecutive_failures,
                      maintenance_reason
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise PendingCheckpointRepairRejectedError(
                "canonical organism state is missing"
            )
        if organism["status"] != "checkpoint_pending":
            raise PendingCheckpointRepairRejectedError(
                "organism is not eligible for pending checkpoint repair: "
                f"status={organism['status']}"
            )
        if organism["maintenance_reason"] is not None:
            raise PendingCheckpointRepairRejectedError(
                "Slice 15 does not repair a maintenance-bound pending checkpoint"
            )
        if int(organism["consecutive_failures"]) >= CONSECUTIVE_FAILURE_LIMIT:
            raise PendingCheckpointRepairRejectedError(
                "pending checkpoint already requires protected maintenance"
            )

        pending_generation = int(organism["pending_checkpoint_generation"])
        pending_boundary = int(organism["pending_checkpoint_event_sequence"])
        if pending_generation != int(organism["lineage_generation"]):
            raise PendingCheckpointRepairRejectedError(
                "pending checkpoint lineage does not match canonical lineage"
            )
        max_event = int(
            connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) FROM event"
            ).fetchone()[0]
        )
        if max_event != pending_boundary:
            raise PendingCheckpointRepairRejectedError(
                "canonical event history advanced beyond the pending checkpoint boundary"
            )

        previous_checkpoint_id = organism["latest_stable_checkpoint_id"]
        if previous_checkpoint_id is None:
            raise PendingCheckpointRepairRejectedError(
                "pending state has no previous stable checkpoint"
            )
        previous_boundary = int(organism["latest_stable_event_sequence"])
        if previous_boundary >= pending_boundary:
            raise PendingCheckpointRepairRejectedError(
                "pending checkpoint boundary does not follow the previous stable boundary"
            )

        registry_rows = connection.execute(
            """SELECT checkpoint_id, lineage_generation, event_sequence,
                      manifest_sha256, database_sha256, database_size_bytes,
                      created_wall_time_utc_us, registered_wall_time_utc_us,
                      protected
               FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"""
        ).fetchall()
        registered_ids = {str(row["checkpoint_id"]) for row in registry_rows}
        if str(previous_checkpoint_id) not in registered_ids:
            raise PendingCheckpointRepairRejectedError(
                "previous stable checkpoint is missing from the canonical registry"
            )

        if not paths.checkpoints.is_dir() or paths.checkpoints.is_symlink():
            raise PendingCheckpointRepairRejectedError(
                "checkpoint store is missing or unsafe"
            )
        entries = sorted(paths.checkpoints.iterdir(), key=lambda item: item.name)
        if any(entry.name.startswith(".") for entry in entries):
            raise PendingCheckpointRepairRejectedError(
                "checkpoint store contains unresolved staging artifacts"
            )
        if any(entry.is_symlink() or not entry.is_dir() for entry in entries):
            raise PendingCheckpointRepairRejectedError(
                "checkpoint store contains an unsafe visible entry"
            )

        visible_by_id = {entry.name: entry for entry in entries}
        if not registered_ids.issubset(visible_by_id):
            raise PendingCheckpointRepairRejectedError(
                "registered checkpoint artifact is missing"
            )
        orphan_dirs = [
            entry for entry in entries if entry.name not in registered_ids
        ]
        if len(orphan_dirs) != 1:
            raise PendingCheckpointRepairRejectedError(
                "pending checkpoint repair requires exactly one published orphan; "
                f"found {len(orphan_dirs)}"
            )

        for row in registry_rows:
            registered_dir = visible_by_id[str(row["checkpoint_id"])]
            registered_manifest = validate_checkpoint_directory(registered_dir)
            if (
                int(registered_manifest["lineage_generation"])
                != int(row["lineage_generation"])
                or int(registered_manifest["event_sequence"])
                != int(row["event_sequence"])
                or registered_manifest["database_sha256"] != row["database_sha256"]
                or int(registered_manifest["database_size_bytes"])
                != int(row["database_size_bytes"])
                or _sha256_file(registered_dir / "manifest.json")
                != row["manifest_sha256"]
                or int(row["protected"]) != 1
            ):
                raise PendingCheckpointRepairRejectedError(
                    "registered checkpoint artifact does not match canonical registry"
                )

        candidate_dir = orphan_dirs[0]
        candidate_manifest = validate_checkpoint_directory(candidate_dir)
        expected_checkpoint_id = (
            f"cp-g{pending_generation:06d}-e{pending_boundary:012d}-"
            f"{candidate_manifest['database_sha256'][:8]}"
        )
        expected_manifest_values = {
            "checkpoint_id": expected_checkpoint_id,
            "organism_id": organism["organism_id"],
            "lineage_generation": pending_generation,
            "lifecycle_number": int(organism["lifecycle_number"]),
            "contract_version": organism["contract_version"],
            "schema_version": int(organism["schema_version"]),
            "environment_version": organism["environment_version"],
            "budget_config_version": organism["budget_config_version"],
            "event_sequence": pending_boundary,
            "provenance": "lifecycle",
            "status": "published",
        }
        for field, expected in expected_manifest_values.items():
            if candidate_manifest.get(field) != expected:
                raise PendingCheckpointRepairRejectedError(
                    f"published checkpoint {field} does not match canonical pending state"
                )
        if candidate_dir.name != expected_checkpoint_id:
            raise PendingCheckpointRepairRejectedError(
                "published checkpoint directory identity is not canonical"
            )
        if connection.execute(
            "SELECT 1 FROM checkpoint_registry WHERE event_sequence = ?",
            (pending_boundary,),
        ).fetchone() is not None:
            raise PendingCheckpointRepairRejectedError(
                "pending checkpoint boundary is already registered"
            )

        _validate_snapshot_matches_pending_canonical(connection, candidate_dir)

        checkpoint_store_bytes = _checkpoint_store_size(paths.checkpoints)
        if checkpoint_store_bytes > CHECKPOINT_STORE_MAX_BYTES:
            raise PendingCheckpointRepairRejectedError(
                "checkpoint store exceeds the protected Phase 1 limit"
            )
        if (
            checkpoint_store_bytes + paths.database.stat().st_size
            > RUNTIME_WORKING_SET_MAX_BYTES
        ):
            raise PendingCheckpointRepairRejectedError(
                "runtime working set exceeds the protected Phase 1 limit"
            )

        reading = (clock or RealClock()).read()
        manifest_sha256 = _sha256_file(candidate_dir / "manifest.json")
        database_size_bytes = int(candidate_manifest["database_size_bytes"])
        database_sha256 = str(candidate_manifest["database_sha256"])
        created_wall_time_utc_us = int(
            candidate_manifest["creation_wall_time_utc_us"]
        )

        connection.execute(
            """INSERT INTO checkpoint_registry (
                   checkpoint_id, lineage_generation, event_sequence,
                   manifest_sha256, database_sha256, database_size_bytes,
                   created_wall_time_utc_us, registered_wall_time_utc_us, protected
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                expected_checkpoint_id,
                pending_generation,
                pending_boundary,
                manifest_sha256,
                database_sha256,
                database_size_bytes,
                created_wall_time_utc_us,
                reading.wall_time_utc_us,
            ),
        )
        updated = connection.execute(
            """UPDATE organism
               SET status = 'sleeping', checkpoint_pending = 0,
                   pending_checkpoint_generation = NULL,
                   pending_checkpoint_event_sequence = NULL,
                   latest_stable_checkpoint_id = ?,
                   latest_stable_event_sequence = ?,
                   maintenance_reason = NULL,
                   last_sleep_wall_time_utc_us = ?
               WHERE singleton_id = 1 AND status = 'checkpoint_pending'
                     AND checkpoint_pending = 1
                     AND pending_checkpoint_generation = ?
                     AND pending_checkpoint_event_sequence = ?
                     AND latest_stable_checkpoint_id = ?
                     AND latest_stable_event_sequence = ?
                     AND maintenance_reason IS NULL""",
            (
                expected_checkpoint_id,
                pending_boundary,
                reading.wall_time_utc_us,
                pending_generation,
                pending_boundary,
                previous_checkpoint_id,
                previous_boundary,
            ),
        )
        if updated.rowcount != 1:
            raise PendingCheckpointRepairRejectedError(
                "canonical pending state changed before checkpoint repair"
            )

        payload = {
            "checkpoint_id": expected_checkpoint_id,
            "checkpoint_store_bytes": checkpoint_store_bytes,
            "database_sha256": database_sha256,
            "database_size_bytes": database_size_bytes,
            "event_sequence": pending_boundary,
            "lineage_generation": pending_generation,
            "manifest_sha256": manifest_sha256,
            "previous_latest_stable_checkpoint_id": str(previous_checkpoint_id),
            "previous_latest_stable_event_sequence": previous_boundary,
            "reason": "published_checkpoint_registration_missing",
            "status_after": "sleeping",
            "status_before": "checkpoint_pending",
        }
        event_cursor = connection.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               ) VALUES (?, ?, ?, ?, 'checkpoint_registration_repaired',
                         'administration:checkpoint-repair', ?, ?, ?, ?)""",
            (
                organism["organism_id"],
                pending_generation,
                organism["lifecycle_number"],
                reading.wall_time_utc_us,
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
                organism["schema_version"],
                organism["environment_version"],
                organism["budget_config_version"],
            ),
        )
        audit_event_sequence = int(event_cursor.lastrowid)

        if _checkpoint_store_size(paths.checkpoints) != checkpoint_store_bytes:
            raise PendingCheckpointRepairRejectedError(
                "checkpoint repair changed immutable artifact byte accounting"
            )
        registered_count = int(
            connection.execute("SELECT COUNT(*) FROM checkpoint_registry").fetchone()[0]
        )
        if registered_count != len(registry_rows) + 1:
            raise PendingCheckpointRepairRejectedError(
                "checkpoint repair did not register exactly one artifact"
            )

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
        return PendingCheckpointRepairResult(
            organism_id=str(organism["organism_id"]),
            status_before="checkpoint_pending",
            status="sleeping",
            checkpoint_id=expected_checkpoint_id,
            lineage_generation=pending_generation,
            event_sequence=pending_boundary,
            previous_latest_stable_checkpoint_id=str(previous_checkpoint_id),
            previous_latest_stable_event_sequence=previous_boundary,
            registered_checkpoint_count=registered_count,
            checkpoint_store_bytes=checkpoint_store_bytes,
            audit_event_sequence=audit_event_sequence,
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
