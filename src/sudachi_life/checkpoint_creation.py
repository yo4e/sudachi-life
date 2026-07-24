"""Audited Phase 1 checkpoint creation and registration repairs."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from typing import Any

from .checkpoint_retention import enforce_checkpoint_retention
from .checkpoint_core import (
    CheckpointResult,
    _canonical_json_bytes,
    _fsync_dir,
    _fsync_file,
    _sha256_file,
    validate_checkpoint_directory,
)
from .clock import Clock
from .constants import (
    CHECKPOINT_ARTIFACT_MAX_BYTES,
    CHECKPOINT_FORMAT_VERSION,
    CHECKPOINT_STORE_MAX_BYTES,
    CONSECUTIVE_FAILURE_LIMIT,
    MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
    PHASE1_BUDGETS,
)
from .errors import CheckpointError, SchemaValidationError
from .paths import OrganismPaths
from .runtime_storage import (
    active_database_allocated_bytes,
    checkpoint_store_bytes,
    ensure_checkpoint_store_within_limit,
    ensure_runtime_working_set_within_limit,
)
from .storage import connect_database, validate_canonical_state


def create_and_register_genesis_checkpoint(
    paths: OrganismPaths,
    *,
    created_wall_time_utc_us: int,
    event_sequence: int,
) -> CheckpointResult:
    return _create_and_register_pending_checkpoint(
        paths,
        created_wall_time_utc_us=created_wall_time_utc_us,
        registered_wall_time_utc_us=created_wall_time_utc_us,
        event_sequence=event_sequence,
        provenance="genesis",
        registration_source="administration:init",
    )


def create_and_register_lifecycle_checkpoint(
    paths: OrganismPaths,
    *,
    clock: Clock,
    protected_test_retention_failure_after_stage: bool = False,
    protected_test_retention_cleanup_failure_after_commit: bool = False,
) -> CheckpointResult:
    started = clock.read()
    return _create_and_register_pending_checkpoint(
        paths,
        created_wall_time_utc_us=started.wall_time_utc_us,
        registered_wall_time_utc_us=None,
        event_sequence=None,
        provenance="lifecycle",
        registration_source="administration:checkpoint",
        deadline_start_monotonic_ns=started.monotonic_ns,
        completion_clock=clock,
        protected_test_retention_failure_after_stage=(
            protected_test_retention_failure_after_stage
        ),
        protected_test_retention_cleanup_failure_after_commit=(
            protected_test_retention_cleanup_failure_after_commit
        ),
    )


def _manifest_for_pending(
    pending: sqlite3.Row,
    *,
    checkpoint_id: str,
    event_sequence: int,
    created_wall_time_utc_us: int,
    size: int,
    database_sha: str,
    provenance: str,
) -> dict[str, Any]:
    return {
        "checkpoint_format_version": CHECKPOINT_FORMAT_VERSION,
        "checkpoint_id": checkpoint_id,
        "organism_id": pending["organism_id"],
        "lineage_generation": pending["lineage_generation"],
        "lifecycle_number": pending["lifecycle_number"],
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
        "provenance": provenance,
    }


def _create_and_register_pending_checkpoint(
    paths: OrganismPaths,
    *,
    created_wall_time_utc_us: int,
    registered_wall_time_utc_us: int | None,
    event_sequence: int | None,
    provenance: str,
    registration_source: str,
    deadline_start_monotonic_ns: int | None = None,
    completion_clock: Clock | None = None,
    protected_test_retention_failure_after_stage: bool = False,
    protected_test_retention_cleanup_failure_after_commit: bool = False,
) -> CheckpointResult:
    paths.checkpoints.mkdir(parents=True, exist_ok=True)
    if paths.checkpoints.is_symlink():
        raise CheckpointError("checkpoint directory may not be a symlink")

    source = connect_database(paths.database, read_only=True)
    try:
        validate_canonical_state(source, expect_checkpoint_pending=True)
        pending = source.execute(
            """SELECT organism_id, lineage_generation, lifecycle_number,
                      schema_version, contract_version, environment_version,
                      budget_config_version, pending_checkpoint_generation,
                      pending_checkpoint_event_sequence, checkpoint_pending
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if pending is None or pending["checkpoint_pending"] != 1:
            raise CheckpointError("checkpoint boundary is not pending")
        actual_boundary = int(pending["pending_checkpoint_event_sequence"])
        if event_sequence is not None and actual_boundary != event_sequence:
            raise CheckpointError("pending event boundary changed before checkpoint creation")
        event_sequence = actual_boundary
        projected_database_size = active_database_allocated_bytes(source)
    finally:
        source.close()

    if projected_database_size > CHECKPOINT_ARTIFACT_MAX_BYTES:
        raise CheckpointError(
            f"checkpoint database exceeds {CHECKPOINT_ARTIFACT_MAX_BYTES} bytes"
        )
    if checkpoint_store_bytes(paths) + projected_database_size > CHECKPOINT_STORE_MAX_BYTES:
        raise CheckpointError("checkpoint store would exceed protected Phase 1 limit")
    try:
        ensure_runtime_working_set_within_limit(
            paths,
            context="checkpoint preflight",
            additional_bytes=projected_database_size + 4096,
        )
    except SchemaValidationError as exc:
        raise CheckpointError(str(exc)) from exc

    source = connect_database(paths.database, read_only=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=".tmp-checkpoint-", dir=paths.checkpoints))
    destination_path = temp_dir / "organism.sqlite3"
    manifest_path = temp_dir / "manifest.json"
    try:
        validate_canonical_state(source, expect_checkpoint_pending=True)
        current_boundary = int(
            source.execute(
                "SELECT pending_checkpoint_event_sequence FROM organism WHERE singleton_id = 1"
            ).fetchone()[0]
        )
        if current_boundary != event_sequence:
            raise CheckpointError("pending event boundary changed before checkpoint backup")
        destination = sqlite3.connect(destination_path, isolation_level=None)
        try:
            source.backup(destination)
        finally:
            destination.close()
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    finally:
        source.close()

    size = destination_path.stat().st_size
    if size > CHECKPOINT_ARTIFACT_MAX_BYTES:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise CheckpointError(f"checkpoint database exceeds {CHECKPOINT_ARTIFACT_MAX_BYTES} bytes")
    database_sha = _sha256_file(destination_path)
    checkpoint_id = (
        f"cp-g{pending['lineage_generation']:06d}-e{event_sequence:012d}-"
        f"{database_sha[:8]}"
    )
    final_dir = paths.checkpoints / checkpoint_id
    manifest = _manifest_for_pending(
        pending,
        checkpoint_id=checkpoint_id,
        event_sequence=event_sequence,
        created_wall_time_utc_us=created_wall_time_utc_us,
        size=size,
        database_sha=database_sha,
        provenance=provenance,
    )
    manifest_bytes = _canonical_json_bytes(manifest)
    manifest_path.write_bytes(manifest_bytes)
    manifest_sha = _sha256_file(manifest_path)

    validate_checkpoint_directory(temp_dir, expected_manifest=manifest)
    try:
        ensure_checkpoint_store_within_limit(paths, context="checkpoint publication")
        ensure_runtime_working_set_within_limit(paths, context="checkpoint publication")
    except SchemaValidationError as exc:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise CheckpointError(str(exc)) from exc

    _fsync_file(destination_path)
    _fsync_file(manifest_path)
    _fsync_dir(temp_dir)
    if final_dir.exists():
        existing_manifest = validate_checkpoint_directory(final_dir)
        identity_fields = (
            "checkpoint_id",
            "organism_id",
            "lineage_generation",
            "lifecycle_number",
            "schema_version",
            "contract_version",
            "environment_version",
            "budget_config_version",
            "event_sequence",
            "database_size_bytes",
            "database_sha256",
            "provenance",
            "status",
        )
        if any(existing_manifest.get(field) != manifest.get(field) for field in identity_fields):
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise CheckpointError(f"checkpoint already exists with different content: {checkpoint_id}")
        shutil.rmtree(temp_dir)
        manifest = existing_manifest
        manifest_sha = _sha256_file(final_dir / "manifest.json")
        size = int(manifest["database_size_bytes"])
        database_sha = str(manifest["database_sha256"])
        created_wall_time_utc_us = int(manifest["creation_wall_time_utc_us"])
    else:
        os.replace(temp_dir, final_dir)
        _fsync_dir(paths.checkpoints)

    try:
        ensure_checkpoint_store_within_limit(paths, context="checkpoint publication")
        ensure_runtime_working_set_within_limit(paths, context="checkpoint publication")
    except SchemaValidationError as exc:
        raise CheckpointError(str(exc)) from exc

    if completion_clock is not None:
        completed = completion_clock.read()
        if deadline_start_monotonic_ns is None:
            raise CheckpointError("checkpoint deadline start is missing")
        elapsed_ns = completed.monotonic_ns - deadline_start_monotonic_ns
        if elapsed_ns < 0:
            raise CheckpointError("checkpoint monotonic clock moved backward")
        if elapsed_ns > PHASE1_BUDGETS.checkpoint_wall_time_ms * 1_000_000:
            raise CheckpointError("checkpoint stabilization deadline exhausted")
        registered_wall_time_utc_us = completed.wall_time_utc_us
    if registered_wall_time_utc_us is None:
        raise CheckpointError("checkpoint registration time is missing")

    registration = connect_database(paths.database)
    try:
        registration.execute("BEGIN IMMEDIATE")
        validate_canonical_state(registration, expect_checkpoint_pending=True)
        current = registration.execute(
            """SELECT checkpoint_pending, pending_checkpoint_generation,
                      pending_checkpoint_event_sequence, lineage_generation,
                      consecutive_failures, maintenance_reason
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if (
            current is None
            or current["checkpoint_pending"] != 1
            or current["pending_checkpoint_generation"] != pending["lineage_generation"]
            or current["pending_checkpoint_event_sequence"] != event_sequence
        ):
            raise CheckpointError("active pending boundary changed before registration")
        registration.execute(
            """INSERT INTO checkpoint_registry (
                   checkpoint_id, lineage_generation, event_sequence,
                   manifest_sha256, database_sha256, database_size_bytes,
                   created_wall_time_utc_us, registered_wall_time_utc_us, protected
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
            (
                checkpoint_id,
                pending["lineage_generation"],
                event_sequence,
                manifest_sha,
                database_sha,
                size,
                created_wall_time_utc_us,
                registered_wall_time_utc_us,
            ),
        )
        failure_streak = int(current["consecutive_failures"])
        maintenance_reason = current["maintenance_reason"]
        if failure_streak >= CONSECUTIVE_FAILURE_LIMIT:
            if maintenance_reason != MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT:
                raise CheckpointError(
                    "failure-threshold checkpoint has no protected maintenance reason"
                )
            final_status = "maintenance_required"
        elif maintenance_reason is not None:
            final_status = "maintenance_required"
        else:
            final_status = "sleeping"

        if final_status == "maintenance_required":
            registration.execute(
                """UPDATE organism
                   SET status = 'maintenance_required', checkpoint_pending = 0,
                       pending_checkpoint_generation = NULL,
                       pending_checkpoint_event_sequence = NULL,
                       latest_stable_checkpoint_id = ?, latest_stable_event_sequence = ?
                   WHERE singleton_id = 1""",
                (checkpoint_id, event_sequence),
            )
        else:
            registration.execute(
                """UPDATE organism
                   SET status = 'sleeping', checkpoint_pending = 0,
                       pending_checkpoint_generation = NULL,
                       pending_checkpoint_event_sequence = NULL,
                       latest_stable_checkpoint_id = ?, latest_stable_event_sequence = ?,
                       maintenance_reason = NULL, last_sleep_wall_time_utc_us = ?
                   WHERE singleton_id = 1""",
                (checkpoint_id, event_sequence, registered_wall_time_utc_us),
            )

        stabilized_payload: dict[str, object] = {
            "checkpoint_id": checkpoint_id,
            "event_sequence": event_sequence,
        }
        if final_status == "maintenance_required":
            stabilized_payload.update(
                {"final_status": final_status, "maintenance_reason": maintenance_reason}
            )
        registration.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               )
               SELECT organism_id, lineage_generation, lifecycle_number, ?,
                      'checkpoint_stabilized', ?, ?,
                      schema_version, environment_version, budget_config_version
               FROM organism WHERE singleton_id = 1""",
            (
                registered_wall_time_utc_us,
                registration_source,
                json.dumps(stabilized_payload, sort_keys=True, separators=(",", ":")),
            ),
        )
        if final_status == "maintenance_required":
            registration.execute(
                """INSERT INTO event (
                       organism_id, lineage_generation, lifecycle_number,
                       wall_time_utc_us, event_type, source, payload_json,
                       schema_version, environment_version, budget_config_version
                   )
                   SELECT organism_id, lineage_generation, lifecycle_number, ?,
                          'maintenance_entered', ?, ?,
                          schema_version, environment_version, budget_config_version
                   FROM organism WHERE singleton_id = 1""",
                (
                    registered_wall_time_utc_us,
                    registration_source,
                    json.dumps(
                        {
                            "checkpoint_event_sequence": event_sequence,
                            "checkpoint_id": checkpoint_id,
                            "consecutive_failures": failure_streak,
                            "maintenance_threshold": CONSECUTIVE_FAILURE_LIMIT,
                            "reason": maintenance_reason,
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                ),
            )
        validate_canonical_state(registration, expect_checkpoint_pending=False)
        registration.commit()
    except Exception:
        if registration.in_transaction:
            registration.rollback()
        raise
    finally:
        registration.close()

    enforce_checkpoint_retention(
        paths,
        latest_checkpoint_id=checkpoint_id,
        latest_event_sequence=event_sequence,
        wall_time_utc_us=registered_wall_time_utc_us,
        protected_test_retention_failure_after_stage=(
            protected_test_retention_failure_after_stage
        ),
        protected_test_retention_cleanup_failure_after_commit=(
            protected_test_retention_cleanup_failure_after_commit
        ),
    )

    return CheckpointResult(
        checkpoint_id=checkpoint_id,
        checkpoint_dir=final_dir,
        database_sha256=database_sha,
        manifest_sha256=manifest_sha,
        database_size_bytes=size,
        event_sequence=event_sequence,
        lineage_generation=int(pending["lineage_generation"]),
    )
