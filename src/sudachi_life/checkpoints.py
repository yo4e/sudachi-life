"""Verified immutable SQLite checkpoints for genesis and later lifecycle boundaries."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from typing import Any

from .constants import (
    BUDGET_CONFIG_VERSION,
    CHECKPOINT_ARTIFACT_MAX_BYTES,
    CHECKPOINT_FORMAT_VERSION,
    CHECKPOINT_STORE_MAX_BYTES,
    CONTRACT_VERSION,
    ENVIRONMENT_VERSION,
    RUNTIME_WORKING_SET_MAX_BYTES,
    SCHEMA_VERSION,
)
from .errors import CheckpointError, SchemaValidationError
from .paths import OrganismPaths
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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


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


def _checkpoint_store_size(checkpoints_dir: Path) -> int:
    total = 0
    for path in checkpoints_dir.rglob("*"):
        if path.is_file() and not path.is_symlink():
            total += path.stat().st_size
    return total


def create_and_register_genesis_checkpoint(
    paths: OrganismPaths,
    *,
    created_wall_time_utc_us: int,
    event_sequence: int,
) -> CheckpointResult:
    """Create, publish, validate, and register the pending genesis boundary."""

    paths.checkpoints.mkdir(parents=True, exist_ok=True)
    if paths.checkpoints.is_symlink():
        raise CheckpointError("checkpoint directory may not be a symlink")

    source = connect_database(paths.database, read_only=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=".tmp-checkpoint-", dir=paths.checkpoints))
    destination_path = temp_dir / "organism.sqlite3"
    manifest_path = temp_dir / "manifest.json"

    try:
        pending = source.execute(
            """
            SELECT organism_id, lineage_generation, schema_version, contract_version,
                   environment_version, budget_config_version,
                   pending_checkpoint_generation, pending_checkpoint_event_sequence,
                   checkpoint_pending
            FROM organism WHERE singleton_id = 1
            """
        ).fetchone()
        if pending is None or pending["checkpoint_pending"] != 1:
            raise CheckpointError("genesis checkpoint boundary is not pending")
        if pending["pending_checkpoint_event_sequence"] != event_sequence:
            raise CheckpointError("pending event boundary changed before checkpoint creation")

        destination = sqlite3.connect(destination_path, isolation_level=None)
        try:
            source.backup(destination)
        finally:
            destination.close()
    except Exception:
        source.close()
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    finally:
        source.close()

    size = destination_path.stat().st_size
    if size > CHECKPOINT_ARTIFACT_MAX_BYTES:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise CheckpointError(
            f"checkpoint database exceeds {CHECKPOINT_ARTIFACT_MAX_BYTES} bytes"
        )
    database_sha = _sha256_file(destination_path)
    checkpoint_id = (
        f"cp-g{pending['lineage_generation']:06d}-"
        f"e{event_sequence:012d}-{database_sha[:8]}"
    )
    final_dir = paths.checkpoints / checkpoint_id
    if final_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise CheckpointError(f"checkpoint already exists: {checkpoint_id}")

    manifest: dict[str, Any] = {
        "checkpoint_format_version": CHECKPOINT_FORMAT_VERSION,
        "checkpoint_id": checkpoint_id,
        "organism_id": pending["organism_id"],
        "lineage_generation": pending["lineage_generation"],
        "schema_version": pending["schema_version"],
        "contract_version": pending["contract_version"],
        "environment_version": pending["environment_version"],
        "budget_config_version": pending["budget_config_version"],
        "event_sequence": event_sequence,
        "creation_wall_time_utc_us": created_wall_time_utc_us,
        "database_filename": "organism.sqlite3",
        "database_size_bytes": size,
        "database_sha256": database_sha,
        "snapshot_method": "python-sqlite3-connection-backup",
        "implementation_version": "0.1.0",
        "status": "published",
        "provenance": "genesis",
    }
    manifest_bytes = _canonical_json_bytes(manifest)
    manifest_path.write_bytes(manifest_bytes)
    manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()

    validate_checkpoint_directory(temp_dir, expected_manifest=manifest)
    _fsync_file(destination_path)
    _fsync_file(manifest_path)
    _fsync_dir(temp_dir)
    os.replace(temp_dir, final_dir)
    _fsync_dir(paths.checkpoints)

    store_size = _checkpoint_store_size(paths.checkpoints)
    if store_size > CHECKPOINT_STORE_MAX_BYTES:
        raise CheckpointError("checkpoint store exceeds protected Phase 1 limit")
    working_set = store_size + paths.database.stat().st_size
    if working_set > RUNTIME_WORKING_SET_MAX_BYTES:
        raise CheckpointError("runtime working set exceeds protected Phase 1 limit")

    registration = connect_database(paths.database)
    try:
        registration.execute("BEGIN IMMEDIATE")
        current = registration.execute(
            """
            SELECT checkpoint_pending, pending_checkpoint_generation,
                   pending_checkpoint_event_sequence, lineage_generation
            FROM organism WHERE singleton_id = 1
            """
        ).fetchone()
        if (
            current is None
            or current["checkpoint_pending"] != 1
            or current["pending_checkpoint_generation"] != pending["lineage_generation"]
            or current["pending_checkpoint_event_sequence"] != event_sequence
        ):
            raise CheckpointError("active pending boundary changed before registration")

        registration.execute(
            """
            INSERT INTO checkpoint_registry (
                checkpoint_id, lineage_generation, event_sequence,
                manifest_sha256, database_sha256, database_size_bytes,
                created_wall_time_utc_us, registered_wall_time_utc_us, protected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                checkpoint_id,
                pending["lineage_generation"],
                event_sequence,
                manifest_sha,
                database_sha,
                size,
                created_wall_time_utc_us,
                created_wall_time_utc_us,
            ),
        )
        registration.execute(
            """
            UPDATE organism
            SET status = 'sleeping',
                checkpoint_pending = 0,
                pending_checkpoint_generation = NULL,
                pending_checkpoint_event_sequence = NULL,
                latest_stable_checkpoint_id = ?,
                latest_stable_event_sequence = ?,
                last_sleep_wall_time_utc_us = ?
            WHERE singleton_id = 1
            """,
            (checkpoint_id, event_sequence, created_wall_time_utc_us),
        )
        registration.execute(
            """
            INSERT INTO event (
                organism_id, lineage_generation, lifecycle_number,
                wall_time_utc_us, event_type, source, payload_json,
                schema_version, environment_version, budget_config_version
            )
            SELECT organism_id, lineage_generation, lifecycle_number, ?,
                   'checkpoint_stabilized', 'administration:init', ?,
                   schema_version, environment_version, budget_config_version
            FROM organism WHERE singleton_id = 1
            """,
            (
                created_wall_time_utc_us,
                json.dumps(
                    {"checkpoint_id": checkpoint_id, "event_sequence": event_sequence},
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ),
        )
        validate_canonical_state(registration, expect_checkpoint_pending=False)
        registration.commit()
    except Exception:
        registration.rollback()
        raise
    finally:
        registration.close()

    return CheckpointResult(
        checkpoint_id=checkpoint_id,
        checkpoint_dir=final_dir,
        database_sha256=database_sha,
        manifest_sha256=manifest_sha,
        database_size_bytes=size,
        event_sequence=event_sequence,
        lineage_generation=pending["lineage_generation"],
    )


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
        organism = connection.execute("SELECT * FROM organism WHERE singleton_id = 1").fetchone()
        max_event = connection.execute("SELECT COALESCE(MAX(event_sequence), 0) FROM event").fetchone()[0]
        if organism["organism_id"] != manifest.get("organism_id"):
            raise CheckpointError("checkpoint organism identity mismatch")
        if organism["lineage_generation"] != manifest.get("lineage_generation"):
            raise CheckpointError("checkpoint lineage mismatch")
        if organism["budget_config_version"] != manifest.get("budget_config_version"):
            raise CheckpointError("snapshot budget configuration mismatch")
        if organism["pending_checkpoint_generation"] != manifest.get("lineage_generation"):
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
