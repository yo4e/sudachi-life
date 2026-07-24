"""Bounded checkpoint pruning shared by normal and repaired registration."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sqlite3
from typing import Any

from .checkpoint_core import (
    CheckpointRetentionFailure,
    _InjectedRetentionPruningFailure,
    _fsync_dir,
    _record_retention_failure_maintenance,
    validate_checkpoint_directory,
)
from .checkpoint_retention_warning import _record_post_commit_cleanup_warning
from .constants import CHECKPOINT_RETENTION_LIMIT
from .errors import CheckpointError, SchemaValidationError
from .paths import OrganismPaths
from .runtime_storage import (
    checkpoint_store_bytes,
    ensure_runtime_working_set_within_limit,
)
from .storage import connect_database, validate_canonical_state


def _prune_one_checkpoint(
    paths: OrganismPaths,
    *,
    latest_checkpoint_id: str,
    latest_event_sequence: int,
    wall_time_utc_us: int,
    protected_test_retention_failure_after_stage: bool,
    protected_test_retention_cleanup_failure_after_commit: bool,
) -> tuple[bool, bool]:
    connection = connect_database(paths.database)
    staged_dir: Path | None = None
    original_dir: Path | None = None
    candidate: sqlite3.Row | None = None
    retained_store_size = 0
    committed = False
    try:
        connection.execute("BEGIN IMMEDIATE")
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            """SELECT latest_stable_checkpoint_id, latest_stable_event_sequence
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise CheckpointError("canonical organism state is missing during retention")
        if (
            organism["latest_stable_checkpoint_id"] != latest_checkpoint_id
            or int(organism["latest_stable_event_sequence"]) != latest_event_sequence
        ):
            raise CheckpointError("latest stable checkpoint changed before retention")

        rows = connection.execute(
            """SELECT checkpoint_id, lineage_generation, event_sequence,
                      database_sha256, database_size_bytes, protected
               FROM checkpoint_registry
               ORDER BY event_sequence, checkpoint_id"""
        ).fetchall()
        if len(rows) <= CHECKPOINT_RETENTION_LIMIT:
            connection.commit()
            return False, False

        latest_rows = [row for row in rows if row["checkpoint_id"] == latest_checkpoint_id]
        if len(latest_rows) != 1:
            raise CheckpointError("latest stable checkpoint is missing from retention registry")

        candidate_manifest: dict[str, Any] | None = None
        for row in rows:
            checkpoint_id = str(row["checkpoint_id"])
            if checkpoint_id == latest_checkpoint_id:
                continue
            checkpoint_dir = paths.checkpoints / checkpoint_id
            manifest = validate_checkpoint_directory(checkpoint_dir)
            if manifest["provenance"] == "genesis":
                continue
            candidate = row
            candidate_manifest = manifest
            break
        if candidate is None or candidate_manifest is None:
            raise CheckpointError(
                "retention would require genesis removal without an explicit archive policy"
            )
        if int(candidate["protected"]) != 1:
            raise CheckpointError("retention candidate is not a protected stable checkpoint")
        if (
            int(candidate_manifest["lineage_generation"])
            != int(candidate["lineage_generation"])
            or int(candidate_manifest["event_sequence"]) != int(candidate["event_sequence"])
            or candidate_manifest["database_sha256"] != candidate["database_sha256"]
        ):
            raise CheckpointError("retention candidate manifest does not match registry")

        original_dir = paths.checkpoints / str(candidate["checkpoint_id"])
        pruned_artifact_size = sum(
            path.stat().st_size
            for path in original_dir.rglob("*")
            if path.is_file() and not path.is_symlink()
        )
        retained_store_size = checkpoint_store_bytes(paths) - pruned_artifact_size
        if pruned_artifact_size <= 0 or retained_store_size < 0:
            raise CheckpointError("retention candidate storage accounting is invalid")

        staged_dir = paths.checkpoints / f".pruning-{candidate['checkpoint_id']}"
        if staged_dir.exists():
            raise CheckpointError("checkpoint retention staging path already exists")
        os.replace(original_dir, staged_dir)
        _fsync_dir(paths.checkpoints)
        if protected_test_retention_failure_after_stage:
            raise _InjectedRetentionPruningFailure(
                "protected test injected retention failure after artifact staging"
            )

        deleted = connection.execute(
            "DELETE FROM checkpoint_registry WHERE checkpoint_id = ?",
            (candidate["checkpoint_id"],),
        )
        if deleted.rowcount != 1:
            raise CheckpointError("retention candidate registry row changed unexpectedly")
        retained_count = int(
            connection.execute("SELECT COUNT(*) FROM checkpoint_registry").fetchone()[0]
        )
        if retained_count < CHECKPOINT_RETENTION_LIMIT:
            raise CheckpointError("retention removed too many protected checkpoints")

        connection.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               )
               SELECT organism_id, lineage_generation, lifecycle_number, ?,
                      'checkpoint_pruned', 'administration:checkpoint-retention', ?,
                      schema_version, environment_version, budget_config_version
               FROM organism WHERE singleton_id = 1""",
            (
                wall_time_utc_us,
                json.dumps(
                    {
                        "latest_stable_checkpoint_id": latest_checkpoint_id,
                        "latest_stable_event_sequence": latest_event_sequence,
                        "pruned_artifact_size_bytes": pruned_artifact_size,
                        "pruned_checkpoint_id": candidate["checkpoint_id"],
                        "pruned_database_size_bytes": int(candidate["database_size_bytes"]),
                        "pruned_event_sequence": int(candidate["event_sequence"]),
                        "pruned_lineage_generation": int(candidate["lineage_generation"]),
                        "pruned_provenance": candidate_manifest["provenance"],
                        "reason": "checkpoint_retention_limit",
                        "retained_checkpoint_count": retained_count,
                        "retained_checkpoint_store_bytes": retained_store_size,
                        "retention_limit": CHECKPOINT_RETENTION_LIMIT,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ),
        )
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
        committed = True
    except _InjectedRetentionPruningFailure:
        if connection.in_transaction:
            connection.rollback()
        if (
            staged_dir is None
            or original_dir is None
            or candidate is None
            or not staged_dir.exists()
        ):
            raise CheckpointError(
                "protected retention failure did not reach the declared staging point"
            )
        os.replace(staged_dir, original_dir)
        _fsync_dir(paths.checkpoints)
        if not original_dir.is_dir() or staged_dir.exists():
            raise CheckpointError(
                "protected retention candidate restoration did not complete"
            )
        stable_count = int(
            connection.execute("SELECT COUNT(*) FROM checkpoint_registry").fetchone()[0]
        )
        failure = CheckpointRetentionFailure(
            reason="protected_test_injected_checkpoint_retention_failure",
            injection_point="after_artifact_stage_before_registry_mutation",
            candidate_checkpoint_id=str(candidate["checkpoint_id"]),
            candidate_event_sequence=int(candidate["event_sequence"]),
            candidate_restored=True,
            latest_stable_checkpoint_id=latest_checkpoint_id,
            latest_stable_event_sequence=latest_event_sequence,
            stable_checkpoint_count=stable_count,
            checkpoint_store_bytes=checkpoint_store_bytes(paths),
        )
        _record_retention_failure_maintenance(
            connection,
            paths,
            failure=failure,
            wall_time_utc_us=wall_time_utc_us,
        )
        return False, True
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        if staged_dir is not None and original_dir is not None and staged_dir.exists():
            os.replace(staged_dir, original_dir)
            _fsync_dir(paths.checkpoints)
        raise
    finally:
        connection.close()

    if not committed or staged_dir is None or candidate is None:
        raise CheckpointError("checkpoint retention did not commit")
    try:
        if protected_test_retention_cleanup_failure_after_commit:
            raise OSError("protected test injected post-commit cleanup failure")
        shutil.rmtree(staged_dir)
        _fsync_dir(paths.checkpoints)
    except OSError:
        _record_post_commit_cleanup_warning(
            paths,
            staged_dir=staged_dir,
            candidate=candidate,
            latest_checkpoint_id=latest_checkpoint_id,
            latest_event_sequence=latest_event_sequence,
            wall_time_utc_us=wall_time_utc_us,
        )
        return False, True
    if checkpoint_store_bytes(paths) != retained_store_size:
        raise CheckpointError("retained checkpoint store byte accounting changed unexpectedly")
    try:
        ensure_runtime_working_set_within_limit(paths, context="checkpoint retention")
    except SchemaValidationError as exc:
        raise CheckpointError(str(exc)) from exc
    return True, False


def enforce_checkpoint_retention(
    paths: OrganismPaths,
    *,
    latest_checkpoint_id: str,
    latest_event_sequence: int,
    wall_time_utc_us: int,
    protected_test_retention_failure_after_stage: bool = False,
    protected_test_retention_cleanup_failure_after_commit: bool = False,
) -> None:
    """Prune oldest eligible checkpoints until the protected limit is restored."""

    first = True
    while True:
        pruned, stopped = _prune_one_checkpoint(
            paths,
            latest_checkpoint_id=latest_checkpoint_id,
            latest_event_sequence=latest_event_sequence,
            wall_time_utc_us=wall_time_utc_us,
            protected_test_retention_failure_after_stage=(
                protected_test_retention_failure_after_stage and first
            ),
            protected_test_retention_cleanup_failure_after_commit=(
                protected_test_retention_cleanup_failure_after_commit and first
            ),
        )
        first = False
        if stopped or not pruned:
            return
