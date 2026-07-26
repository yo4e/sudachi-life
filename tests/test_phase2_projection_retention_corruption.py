from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_retention_projection import (
    ZeroCaregiverProjectionError,
    capture_zero_caregiver_retention_evidence,
)
from sudachi_life.storage import connect_database


def _wake_clock(base: int) -> FakeClock:
    return FakeClock(
        [
            ClockReading(base, 10_000_000),
            ClockReading(base, 15_000_000),
            ClockReading(base + 1, 20_000_000),
            ClockReading(base + 2, 30_000_000),
            ClockReading(base + 3, 40_000_000),
        ]
    )


def _enqueue_and_wake(runtime_root: Path, paths: OrganismPaths, index: int) -> None:
    base = 200 + (index * 200)
    enqueue_garden_tick(
        paths,
        f"tick-{index}",
        clock=FakeClock([ClockReading(base - 100, base * 1_000)]),
    )
    perform_garden_wake(
        runtime_root,
        "retention-corruption",
        seed=index,
        clock=_wake_clock(base),
    )


def _replace_prune_payload(paths: OrganismPaths, payload: dict[str, object]) -> None:
    connection = connect_database(paths.database)
    try:
        triggers = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
            "AND name IN ('event_no_update','event_no_delete') ORDER BY name"
        ).fetchall()
        for row in triggers:
            connection.execute(f"DROP TRIGGER {row['name']}")
        connection.execute(
            "UPDATE event SET payload_json=? WHERE event_type='checkpoint_pruned'",
            (json.dumps(payload, sort_keys=True, separators=(",", ":")),),
        )
        for row in triggers:
            connection.execute(row["sql"])
    finally:
        connection.close()


def test_pruned_artifact_size_is_validated_before_projection(tmp_path: Path) -> None:
    initialize_organism(
        tmp_path,
        "retention-corruption",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_700_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
    )
    paths = OrganismPaths.build(tmp_path, "retention-corruption")
    for index in range(1, 4):
        _enqueue_and_wake(tmp_path, paths, index)
    before_prune = capture_zero_caregiver_retention_evidence(paths)
    _enqueue_and_wake(tmp_path, paths, 4)

    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT payload_json FROM event WHERE event_type='checkpoint_pruned'"
        ).fetchone()
    finally:
        connection.close()
    payload = json.loads(row["payload_json"])
    payload["pruned_artifact_size_bytes"] = (
        int(payload["pruned_artifact_size_bytes"]) + 1
    )
    _replace_prune_payload(paths, payload)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="checkpoint_pruned artifact size does not match pre-deletion evidence",
    ):
        capture_zero_caregiver_retention_evidence(
            paths,
            previous=before_prune,
        )
