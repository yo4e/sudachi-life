"""Atomic canonical registration of one validated checkpoint-repair candidate."""

from __future__ import annotations

import json
import sqlite3

from .checkpoint_repair_types import (
    PendingCheckpointCandidate,
    PendingCheckpointRepairRejectedError,
    sha256_file,
)
from .clock import Clock
from .constants import CONSECUTIVE_FAILURE_LIMIT
from .storage import validate_canonical_state


def commit_pending_checkpoint_candidate(
    connection: sqlite3.Connection,
    candidate: PendingCheckpointCandidate,
    *,
    clock: Clock,
) -> tuple[int, int]:
    organism = candidate.organism
    manifest = candidate.candidate_manifest
    reading = clock.read()
    manifest_sha256 = sha256_file(candidate.candidate_dir / "manifest.json")
    database_size_bytes = int(manifest["database_size_bytes"])
    database_sha256 = str(manifest["database_sha256"])
    created_wall_time_utc_us = int(manifest["creation_wall_time_utc_us"])
    connection.execute(
        """INSERT INTO checkpoint_registry (
               checkpoint_id, lineage_generation, event_sequence,
               manifest_sha256, database_sha256, database_size_bytes,
               created_wall_time_utc_us, registered_wall_time_utc_us, protected
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
        (
            candidate.expected_checkpoint_id,
            candidate.pending_generation,
            candidate.pending_boundary,
            manifest_sha256,
            database_sha256,
            database_size_bytes,
            created_wall_time_utc_us,
            reading.wall_time_utc_us,
        ),
    )
    if candidate.final_status == "maintenance_required":
        updated = connection.execute(
            """UPDATE organism
               SET status = 'maintenance_required', checkpoint_pending = 0,
                   pending_checkpoint_generation = NULL,
                   pending_checkpoint_event_sequence = NULL,
                   latest_stable_checkpoint_id = ?, latest_stable_event_sequence = ?
               WHERE singleton_id = 1 AND status = 'checkpoint_pending'
                     AND checkpoint_pending = 1
                     AND pending_checkpoint_generation = ?
                     AND pending_checkpoint_event_sequence = ?""",
            (
                candidate.expected_checkpoint_id,
                candidate.pending_boundary,
                candidate.pending_generation,
                candidate.pending_boundary,
            ),
        )
    else:
        updated = connection.execute(
            """UPDATE organism
               SET status = 'sleeping', checkpoint_pending = 0,
                   pending_checkpoint_generation = NULL,
                   pending_checkpoint_event_sequence = NULL,
                   latest_stable_checkpoint_id = ?, latest_stable_event_sequence = ?,
                   maintenance_reason = NULL, last_sleep_wall_time_utc_us = ?
               WHERE singleton_id = 1 AND status = 'checkpoint_pending'
                     AND checkpoint_pending = 1
                     AND pending_checkpoint_generation = ?
                     AND pending_checkpoint_event_sequence = ?""",
            (
                candidate.expected_checkpoint_id,
                candidate.pending_boundary,
                reading.wall_time_utc_us,
                candidate.pending_generation,
                candidate.pending_boundary,
            ),
        )
    if updated.rowcount != 1:
        raise PendingCheckpointRepairRejectedError(
            "canonical pending state changed before checkpoint repair"
        )

    payload: dict[str, object] = {
        "checkpoint_id": candidate.expected_checkpoint_id,
        "checkpoint_store_bytes": candidate.checkpoint_store_bytes_before,
        "database_sha256": database_sha256,
        "database_size_bytes": database_size_bytes,
        "event_sequence": candidate.pending_boundary,
        "lineage_generation": candidate.pending_generation,
        "manifest_sha256": manifest_sha256,
        "previous_latest_stable_checkpoint_id": candidate.previous_checkpoint_id,
        "previous_latest_stable_event_sequence": candidate.previous_boundary,
        "reason": "published_checkpoint_registration_missing",
        "status_after": candidate.final_status,
        "status_before": "checkpoint_pending",
    }
    if candidate.final_status == "maintenance_required":
        payload["maintenance_reason"] = organism["maintenance_reason"]
    event_cursor = connection.execute(
        """INSERT INTO event (
               organism_id, lineage_generation, lifecycle_number,
               wall_time_utc_us, event_type, source, payload_json,
               schema_version, environment_version, budget_config_version
           ) VALUES (?, ?, ?, ?, 'checkpoint_registration_repaired',
                     'administration:checkpoint-repair', ?, ?, ?, ?)""",
        (
            organism["organism_id"],
            candidate.pending_generation,
            organism["lifecycle_number"],
            reading.wall_time_utc_us,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
            organism["schema_version"],
            organism["environment_version"],
            organism["budget_config_version"],
        ),
    )
    audit_event_sequence = int(event_cursor.lastrowid)
    if candidate.final_status == "maintenance_required":
        connection.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               ) VALUES (?, ?, ?, ?, 'maintenance_entered',
                         'administration:checkpoint-repair', ?, ?, ?, ?)""",
            (
                organism["organism_id"],
                candidate.pending_generation,
                organism["lifecycle_number"],
                reading.wall_time_utc_us,
                json.dumps(
                    {
                        "checkpoint_event_sequence": candidate.pending_boundary,
                        "checkpoint_id": candidate.expected_checkpoint_id,
                        "consecutive_failures": int(organism["consecutive_failures"]),
                        "maintenance_threshold": CONSECUTIVE_FAILURE_LIMIT,
                        "reason": organism["maintenance_reason"],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                organism["schema_version"],
                organism["environment_version"],
                organism["budget_config_version"],
            ),
        )
    validate_canonical_state(connection, expect_checkpoint_pending=False)
    connection.commit()
    return audit_event_sequence, reading.wall_time_utc_us
