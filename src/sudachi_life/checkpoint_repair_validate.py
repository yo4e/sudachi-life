"""Exact validation for one published pending-checkpoint orphan."""

from __future__ import annotations

import sqlite3

from .checkpoint_core import validate_checkpoint_directory
from .checkpoint_repair_types import (
    PendingCheckpointCandidate,
    PendingCheckpointRepairRejectedError,
    final_status,
    sha256_file,
    validate_snapshot_matches_pending_canonical,
)
from .paths import OrganismPaths
from .runtime_storage import (
    checkpoint_store_bytes,
    ensure_checkpoint_store_within_limit,
    ensure_runtime_working_set_within_limit,
)
from .storage import validate_canonical_state


def validate_pending_checkpoint_candidate(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
) -> PendingCheckpointCandidate:
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
        raise PendingCheckpointRepairRejectedError("canonical organism state is missing")
    if organism["status"] != "checkpoint_pending":
        raise PendingCheckpointRepairRejectedError(
            "organism is not eligible for pending checkpoint repair: "
            f"status={organism['status']}"
        )
    status_after = final_status(organism)
    pending_generation = int(organism["pending_checkpoint_generation"])
    pending_boundary = int(organism["pending_checkpoint_event_sequence"])
    if pending_generation != int(organism["lineage_generation"]):
        raise PendingCheckpointRepairRejectedError(
            "pending checkpoint lineage does not match canonical lineage"
        )
    max_event = int(
        connection.execute("SELECT COALESCE(MAX(event_sequence), 0) FROM event").fetchone()[0]
    )
    if max_event != pending_boundary:
        raise PendingCheckpointRepairRejectedError(
            "canonical event history advanced beyond the pending checkpoint boundary"
        )

    previous = organism["latest_stable_checkpoint_id"]
    previous_checkpoint_id = None if previous is None else str(previous)
    previous_boundary = int(organism["latest_stable_event_sequence"])
    registry_rows = connection.execute(
        """SELECT checkpoint_id, lineage_generation, event_sequence,
                  manifest_sha256, database_sha256, database_size_bytes,
                  created_wall_time_utc_us, registered_wall_time_utc_us,
                  protected
           FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"""
    ).fetchall()
    registered_ids = {str(row["checkpoint_id"]) for row in registry_rows}
    if previous_checkpoint_id is None:
        if registry_rows or previous_boundary != 0 or int(organism["lifecycle_number"]) != 0:
            raise PendingCheckpointRepairRejectedError(
                "genesis pending state has inconsistent prior checkpoint metadata"
            )
        expected_provenance = "genesis"
    else:
        if previous_boundary >= pending_boundary:
            raise PendingCheckpointRepairRejectedError(
                "pending checkpoint boundary does not follow the previous stable boundary"
            )
        if previous_checkpoint_id not in registered_ids:
            raise PendingCheckpointRepairRejectedError(
                "previous stable checkpoint is missing from the canonical registry"
            )
        expected_provenance = "lifecycle"

    if not paths.checkpoints.is_dir() or paths.checkpoints.is_symlink():
        raise PendingCheckpointRepairRejectedError("checkpoint store is missing or unsafe")
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
    orphan_dirs = [entry for entry in entries if entry.name not in registered_ids]
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
            or int(registered_manifest["event_sequence"]) != int(row["event_sequence"])
            or registered_manifest["database_sha256"] != row["database_sha256"]
            or int(registered_manifest["database_size_bytes"])
            != int(row["database_size_bytes"])
            or sha256_file(registered_dir / "manifest.json") != row["manifest_sha256"]
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
        "provenance": expected_provenance,
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
    validate_snapshot_matches_pending_canonical(connection, candidate_dir)

    store_bytes = checkpoint_store_bytes(paths)
    ensure_checkpoint_store_within_limit(paths, context="pending checkpoint repair")
    ensure_runtime_working_set_within_limit(paths, context="pending checkpoint repair")
    return PendingCheckpointCandidate(
        organism=organism,
        pending_generation=pending_generation,
        pending_boundary=pending_boundary,
        previous_checkpoint_id=previous_checkpoint_id,
        previous_boundary=previous_boundary,
        final_status=status_after,
        candidate_dir=candidate_dir,
        candidate_manifest=candidate_manifest,
        expected_checkpoint_id=expected_checkpoint_id,
        checkpoint_store_bytes_before=store_bytes,
    )
