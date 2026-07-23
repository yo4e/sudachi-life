from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import WakeResult, perform_first_water_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def _wake_clock() -> FakeClock:
    return FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 40_000_000),
        ]
    )


def _run_first_wake(runtime_root: Path, *, seed: int) -> tuple[OrganismPaths, WakeResult]:
    initial, _ = initialize_organism(
        runtime_root,
        "sudachi-0",
        clock=FakeClock.fixed(wall_time_utc_us=100, monotonic_ns=1_000_000),
    )
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(
        paths,
        "seed-independence-tick",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    clock = _wake_clock()
    result = perform_first_water_wake(
        runtime_root,
        initial.organism_id,
        seed=seed,
        clock=clock,
    )
    assert clock.read_count == 5
    return paths, result


def _normalized_events(connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT event_sequence, organism_id, lineage_generation, lifecycle_number,
               wall_time_utc_us, event_type, source, payload_json, schema_version,
               environment_version, budget_config_version
        FROM event
        ORDER BY event_sequence
        """
    ).fetchall()
    normalized = []
    for row in rows:
        payload = json.loads(row["payload_json"])
        if row["event_type"] == "wake_accepted":
            assert set(payload) == {"seed"}
            payload = {"seed": "<declared-seed>"}
        elif row["event_type"] == "checkpoint_stabilized":
            payload = dict(payload)
            assert "checkpoint_id" in payload
            payload["checkpoint_id"] = "<digest-derived-checkpoint-id>"
        normalized.append(
            {
                "event_sequence": int(row["event_sequence"]),
                "organism_id": str(row["organism_id"]),
                "lineage_generation": int(row["lineage_generation"]),
                "lifecycle_number": int(row["lifecycle_number"]),
                "wall_time_utc_us": int(row["wall_time_utc_us"]),
                "event_type": str(row["event_type"]),
                "source": str(row["source"]),
                "payload": payload,
                "schema_version": int(row["schema_version"]),
                "environment_version": str(row["environment_version"]),
                "budget_config_version": str(row["budget_config_version"]),
            }
        )
    return normalized


def _canonical_behavior_projection(database: Path) -> dict[str, Any]:
    connection = connect_database(database, read_only=True)
    try:
        organism = tuple(
            connection.execute(
                """
                SELECT organism_id, contract_version, schema_version,
                       environment_version, budget_config_version,
                       lineage_generation, developmental_stage,
                       created_wall_time_utc_us, lifecycle_number, status,
                       checkpoint_pending, pending_checkpoint_generation,
                       pending_checkpoint_event_sequence,
                       latest_stable_event_sequence, consecutive_failures,
                       maintenance_reason, last_wake_wall_time_utc_us,
                       last_sleep_wall_time_utc_us
                FROM organism
                WHERE singleton_id = 1
                """
            ).fetchone()
        )
        return {
            "organism": organism,
            "budget_config": [
                tuple(row)
                for row in connection.execute(
                    "SELECT singleton_id, config_version, config_json "
                    "FROM budget_config ORDER BY singleton_id"
                ).fetchall()
            ],
            "environment_state": [
                tuple(row)
                for row in connection.execute(
                    "SELECT singleton_id, environment_version, environment_step, "
                    "objective_complete FROM environment_state ORDER BY singleton_id"
                ).fetchall()
            ],
            "garden_plot": [
                tuple(row)
                for row in connection.execute(
                    "SELECT plot_id, stage, moisture, fruit "
                    "FROM garden_plot ORDER BY plot_id"
                ).fetchall()
            ],
            "inventory": [
                tuple(row)
                for row in connection.execute(
                    "SELECT singleton_id, water_units, harvested_fruit "
                    "FROM inventory ORDER BY singleton_id"
                ).fetchall()
            ],
            "action_definition": [
                tuple(row)
                for row in connection.execute(
                    "SELECT action_id, version, deterministic, protected "
                    "FROM action_definition ORDER BY action_id"
                ).fetchall()
            ],
            "inbox_event": [
                tuple(row)
                for row in connection.execute(
                    """
                    SELECT inbox_id, external_event_id, event_type, source,
                           source_wall_time_utc_us, received_wall_time_utc_us,
                           claimed_lifecycle_number, consumed
                    FROM inbox_event
                    ORDER BY inbox_id
                    """
                ).fetchall()
            ],
            "events": _normalized_events(connection),
            "checkpoint_registry": [
                tuple(row)
                for row in connection.execute(
                    """
                    SELECT lineage_generation, event_sequence,
                           database_size_bytes, created_wall_time_utc_us,
                           registered_wall_time_utc_us, protected
                    FROM checkpoint_registry
                    ORDER BY event_sequence
                    """
                ).fetchall()
            ],
            "sqlite_sequence": [
                tuple(row)
                for row in connection.execute(
                    "SELECT name, seq FROM sqlite_sequence ORDER BY name"
                ).fetchall()
            ],
        }
    finally:
        connection.close()


def _declared_seed(database: Path) -> int:
    connection = connect_database(database, read_only=True)
    try:
        rows = connection.execute(
            "SELECT payload_json FROM event WHERE event_type = 'wake_accepted'"
        ).fetchall()
    finally:
        connection.close()
    assert len(rows) == 1
    return int(json.loads(rows[0]["payload_json"])["seed"])


def test_different_declared_seeds_preserve_first_wake_behavior(tmp_path: Path) -> None:
    paths_one, result_one = _run_first_wake(tmp_path / "seed-one", seed=1)
    paths_two, result_two = _run_first_wake(tmp_path / "seed-two", seed=2)

    assert result_one.seed == _declared_seed(paths_one.database) == 1
    assert result_two.seed == _declared_seed(paths_two.database) == 2
    assert result_one.decision.as_dict() == result_two.decision.as_dict()
    assert result_one.evaluation.as_dict() == result_two.evaluation.as_dict()
    assert result_one.budget_ledger == result_two.budget_ledger
    assert (
        result_one.lifecycle_number,
        result_one.external_event_id,
        result_one.checkpoint.event_sequence,
        result_one.checkpoint.lineage_generation,
        result_one.checkpoint.database_size_bytes,
        result_one.status,
    ) == (
        result_two.lifecycle_number,
        result_two.external_event_id,
        result_two.checkpoint.event_sequence,
        result_two.checkpoint.lineage_generation,
        result_two.checkpoint.database_size_bytes,
        result_two.status,
    )

    status_one = read_status(paths_one).as_dict()
    status_two = read_status(paths_two).as_dict()
    checkpoint_id_one = status_one.pop("latest_stable_checkpoint_id")
    checkpoint_id_two = status_two.pop("latest_stable_checkpoint_id")
    assert status_one == status_two
    assert checkpoint_id_one == result_one.checkpoint.checkpoint_id
    assert checkpoint_id_two == result_two.checkpoint.checkpoint_id

    assert result_one.checkpoint.database_sha256 != result_two.checkpoint.database_sha256
    assert result_one.checkpoint.manifest_sha256 != result_two.checkpoint.manifest_sha256
    assert result_one.checkpoint.checkpoint_id != result_two.checkpoint.checkpoint_id

    manifest_one = validate_checkpoint_directory(result_one.checkpoint.checkpoint_dir)
    manifest_two = validate_checkpoint_directory(result_two.checkpoint.checkpoint_dir)
    assert {
        key for key in manifest_one if manifest_one[key] != manifest_two[key]
    } == {"checkpoint_id", "database_sha256"}

    assert _canonical_behavior_projection(paths_one.database) == (
        _canonical_behavior_projection(paths_two.database)
    )
    assert _canonical_behavior_projection(
        result_one.checkpoint.checkpoint_dir / "organism.sqlite3"
    ) == _canonical_behavior_projection(
        result_two.checkpoint.checkpoint_dir / "organism.sqlite3"
    )
