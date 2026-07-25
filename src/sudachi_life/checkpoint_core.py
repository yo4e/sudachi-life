"""Shared immutable-checkpoint structures and validation primitives."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from typing import Any

from .constants import (
    BUDGET_CONFIG_VERSION,
    CHECKPOINT_FORMAT_VERSION,
    CHECKPOINT_RETENTION_LIMIT,
    CONTRACT_VERSION,
    ENVIRONMENT_VERSION,
    MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
    SCHEMA_VERSION,
)
from .errors import CheckpointError, SchemaValidationError
from .paths import OrganismPaths
from .runtime_storage import checkpoint_store_bytes
from .storage import connect_database, validate_canonical_state


@dataclass(frozen=True, slots=True)
class CheckpointResult:
    checkpoint_id: str
    checkpoint_dir: Path
    database_sha256: str
    manifest_sha256: str
    database_size_bytes: int
    event_sequence: int
    lineage_generation: int


@dataclass(frozen=True, slots=True)
class CheckpointRetentionFailure:
    reason: str
    injection_point: str
    candidate_checkpoint_id: str
    candidate_event_sequence: int
    candidate_restored: bool
    latest_stable_checkpoint_id: str
    latest_stable_event_sequence: int
    stable_checkpoint_count: int
    checkpoint_store_bytes: int

    def as_dict(self) -> dict[str, object]:
        return {
            "reason": self.reason,
            "injection_point": self.injection_point,
            "candidate_checkpoint_id": self.candidate_checkpoint_id,
            "candidate_event_sequence": self.candidate_event_sequence,
            "candidate_restored": self.candidate_restored,
            "latest_stable_checkpoint_id": self.latest_stable_checkpoint_id,
            "latest_stable_event_sequence": self.latest_stable_event_sequence,
            "stable_checkpoint_count": self.stable_checkpoint_count,
            "checkpoint_store_bytes": self.checkpoint_store_bytes,
            "retention_limit": CHECKPOINT_RETENTION_LIMIT,
        }


class _InjectedRetentionPruningFailure(Exception):
    """Protected test-only failure after artifact staging."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _fsync_file(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())


def _fsync_dir(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _record_retention_failure_maintenance(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
    *,
    failure: CheckpointRetentionFailure,
    wall_time_utc_us: int,
) -> None:
    connection.execute("BEGIN IMMEDIATE")
    try:
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            """SELECT organism_id, lineage_generation, lifecycle_number, status,
                      latest_stable_checkpoint_id, latest_stable_event_sequence,
                      maintenance_reason, schema_version, environment_version,
                      budget_config_version
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise CheckpointError(
                "canonical organism state is missing during retention failure classification"
            )
        if organism["status"] != "sleeping" or organism["maintenance_reason"] is not None:
            raise CheckpointError(
                "retention failure classification requires stable sleeping state"
            )
        if (
            organism["latest_stable_checkpoint_id"]
            != failure.latest_stable_checkpoint_id
            or int(organism["latest_stable_event_sequence"])
            != failure.latest_stable_event_sequence
        ):
            raise CheckpointError(
                "latest stable checkpoint changed during retention failure classification"
            )
        rows = connection.execute(
            "SELECT checkpoint_id, event_sequence FROM checkpoint_registry "
            "ORDER BY event_sequence, checkpoint_id"
        ).fetchall()
        registered_ids = [str(row["checkpoint_id"]) for row in rows]
        if failure.candidate_checkpoint_id not in registered_ids:
            raise CheckpointError(
                "restored retention candidate is missing from the canonical registry"
            )
        if failure.latest_stable_checkpoint_id not in registered_ids:
            raise CheckpointError(
                "newest stable checkpoint is missing from the canonical registry"
            )
        stable_dirs = sorted(
            path.name
            for path in paths.checkpoints.iterdir()
            if path.is_dir() and not path.name.startswith(".")
        )
        if stable_dirs != sorted(registered_ids):
            raise CheckpointError(
                "restored checkpoint artifacts do not match the canonical registry"
            )
        if any(path.name.startswith(".pruning-") for path in paths.checkpoints.iterdir()):
            raise CheckpointError(
                "retention staging artifact remains after protected restoration"
            )
        for checkpoint_id in registered_ids:
            validate_checkpoint_directory(paths.checkpoints / checkpoint_id)
        store_bytes = checkpoint_store_bytes(paths)
        if store_bytes != failure.checkpoint_store_bytes:
            raise CheckpointError(
                "checkpoint store byte accounting changed after retention restoration"
            )
        updated = connection.execute(
            """UPDATE organism
               SET status = 'maintenance_required', maintenance_reason = ?
               WHERE singleton_id = 1 AND status = 'sleeping'
                     AND checkpoint_pending = 0 AND maintenance_reason IS NULL
                     AND latest_stable_checkpoint_id = ?
                     AND latest_stable_event_sequence = ?""",
            (
                MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
                failure.latest_stable_checkpoint_id,
                failure.latest_stable_event_sequence,
            ),
        )
        if updated.rowcount != 1:
            raise CheckpointError(
                "canonical state changed before retention maintenance entry"
            )
        payload = {
            **failure.as_dict(),
            "maintenance_reason": MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
            "registered_checkpoint_boundaries": [
                int(row["event_sequence"]) for row in rows
            ],
            "registered_checkpoint_count": len(rows),
            "status_after": "maintenance_required",
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


def validate_checkpoint_directory(
    checkpoint_dir: Path,
    *,
    expected_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    database_path = checkpoint_dir / "organism.sqlite3"
    manifest_path = checkpoint_dir / "manifest.json"
    if not database_path.is_file() or database_path.is_symlink():
        raise CheckpointError("checkpoint database is missing or unsafe")
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise CheckpointError("checkpoint manifest is missing or unsafe")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckpointError("checkpoint manifest is not valid JSON") from exc
    if expected_manifest is not None and manifest != expected_manifest:
        raise CheckpointError("checkpoint manifest changed during publication")
    if manifest.get("checkpoint_format_version") != CHECKPOINT_FORMAT_VERSION:
        raise CheckpointError("unsupported checkpoint format")
    if manifest.get("contract_version") != CONTRACT_VERSION:
        raise CheckpointError("checkpoint contract version mismatch")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise CheckpointError("checkpoint schema version mismatch")
    if manifest.get("environment_version") != ENVIRONMENT_VERSION:
        raise CheckpointError("checkpoint environment version mismatch")
    if manifest.get("budget_config_version") != BUDGET_CONFIG_VERSION:
        raise CheckpointError("checkpoint budget configuration mismatch")
    if manifest.get("database_filename") != "organism.sqlite3":
        raise CheckpointError("checkpoint database filename mismatch")
    if manifest.get("snapshot_method") != "python-sqlite3-connection-backup":
        raise CheckpointError("checkpoint snapshot method mismatch")
    if manifest.get("status") != "published":
        raise CheckpointError("checkpoint manifest status mismatch")
    if manifest.get("provenance") not in {"genesis", "lifecycle"}:
        raise CheckpointError("checkpoint provenance mismatch")
    if expected_manifest is None and checkpoint_dir.name != manifest.get("checkpoint_id"):
        raise CheckpointError("checkpoint directory name does not match manifest")
    size = database_path.stat().st_size
    if size != manifest.get("database_size_bytes"):
        raise CheckpointError("checkpoint database size mismatch")
    if _sha256_file(database_path) != manifest.get("database_sha256"):
        raise CheckpointError("checkpoint database digest mismatch")
    connection = connect_database(database_path, read_only=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        if len(integrity) != 1 or integrity[0][0] != "ok":
            raise CheckpointError(f"checkpoint integrity check failed: {integrity!r}")
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_keys:
            raise CheckpointError(f"checkpoint foreign-key check failed: {foreign_keys!r}")
        validate_canonical_state(connection, expect_checkpoint_pending=True)
        organism = connection.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        max_event = connection.execute(
            "SELECT COALESCE(MAX(event_sequence), 0) FROM event"
        ).fetchone()[0]
        if organism["organism_id"] != manifest.get("organism_id"):
            raise CheckpointError("checkpoint organism identity mismatch")
        if organism["lineage_generation"] != manifest.get("lineage_generation"):
            raise CheckpointError("checkpoint lineage mismatch")
        if organism["lifecycle_number"] != manifest.get("lifecycle_number"):
            raise CheckpointError("checkpoint lifecycle mismatch")
        if organism["budget_config_version"] != manifest.get("budget_config_version"):
            raise CheckpointError("snapshot budget configuration mismatch")
        if organism["pending_checkpoint_generation"] != manifest.get(
            "lineage_generation"
        ):
            raise CheckpointError("snapshot pending generation mismatch")
        if max_event != manifest.get("event_sequence"):
            raise CheckpointError("checkpoint event boundary mismatch")
        if organism["pending_checkpoint_event_sequence"] != max_event:
            raise CheckpointError("snapshot pending boundary mismatch")
    except SchemaValidationError as exc:
        raise CheckpointError(str(exc)) from exc
    finally:
        connection.close()
    return manifest
