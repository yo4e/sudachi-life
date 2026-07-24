"""Shared fixtures for Phase 1 independent-audit regression tests."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sqlite3

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import CHECKPOINT_FORMAT_VERSION
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _wake_clock(base: int, *, timeout_checkpoint: bool = False) -> FakeClock:
    completed_monotonic = 5_030_000_001 if timeout_checkpoint else 40_000_000
    return FakeClock(
        [
            ClockReading(base, 10_000_000),
            ClockReading(base, 15_000_000),
            ClockReading(base + 1, 20_000_000),
            ClockReading(base + 2, 30_000_000),
            ClockReading(base + 3, completed_monotonic),
        ]
    )


def _enqueue_and_wake(
    runtime_root: Path,
    organism_id: str,
    index: int,
    *,
    timeout_checkpoint: bool = False,
    cleanup_failure: bool = False,
):
    paths = OrganismPaths.build(runtime_root, organism_id)
    base = 300 + index * 100
    enqueue_garden_tick(
        paths,
        f"audit-tick-{index}",
        clock=FakeClock([ClockReading(base - 1, base * 1000)]),
    )
    return perform_garden_wake(
        runtime_root,
        organism_id,
        seed=index,
        clock=_wake_clock(base, timeout_checkpoint=timeout_checkpoint),
        protected_test_retention_cleanup_failure_after_commit=cleanup_failure,
    )


def _publish_pending_snapshot(
    paths: OrganismPaths,
    *,
    provenance: str,
    creation_wall_time_utc_us: int,
) -> Path:
    source = connect_database(paths.database, read_only=True)
    try:
        pending = source.execute(
            """SELECT organism_id, lineage_generation, lifecycle_number,
                      schema_version, contract_version, environment_version,
                      budget_config_version, pending_checkpoint_event_sequence
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        boundary = int(pending["pending_checkpoint_event_sequence"])
        temp = paths.checkpoints / ".test-pending-snapshot"
        temp.mkdir()
        database = temp / "organism.sqlite3"
        destination = sqlite3.connect(database, isolation_level=None)
        try:
            source.backup(destination)
        finally:
            destination.close()
    finally:
        source.close()

    database_sha = _sha256(database)
    checkpoint_id = (
        f"cp-g{int(pending['lineage_generation']):06d}-e{boundary:012d}-"
        f"{database_sha[:8]}"
    )
    manifest = {
        "checkpoint_format_version": CHECKPOINT_FORMAT_VERSION,
        "checkpoint_id": checkpoint_id,
        "organism_id": pending["organism_id"],
        "lineage_generation": int(pending["lineage_generation"]),
        "lifecycle_number": int(pending["lifecycle_number"]),
        "schema_version": int(pending["schema_version"]),
        "contract_version": pending["contract_version"],
        "environment_version": pending["environment_version"],
        "budget_config_version": pending["budget_config_version"],
        "event_sequence": boundary,
        "creation_wall_time_utc_us": creation_wall_time_utc_us,
        "database_filename": "organism.sqlite3",
        "database_size_bytes": database.stat().st_size,
        "database_sha256": database_sha,
        "snapshot_method": "python-sqlite3-connection-backup",
        "implementation_version": "0.1.0",
        "status": "published",
        "provenance": provenance,
    }
    (temp / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    final = paths.checkpoints / checkpoint_id
    os.replace(temp, final)
    validate_checkpoint_directory(final)
    return final


def _checkpoint_boundaries(paths: OrganismPaths) -> list[int]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return [
            int(row[0])
            for row in connection.execute(
                "SELECT event_sequence FROM checkpoint_registry "
                "ORDER BY event_sequence, checkpoint_id"
            ).fetchall()
        ]
    finally:
        connection.close()
