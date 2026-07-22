from __future__ import annotations

import json

from sudachi_life.checkpoints import (
    create_and_register_lifecycle_checkpoint,
    validate_checkpoint_directory,
)
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import (
    connect_database,
    read_status,
    validate_canonical_state,
)


def _append_administrative_event(
    connection,
    *,
    wall_time_utc_us: int,
    event_type: str,
    payload: dict[str, object],
) -> int:
    organism = connection.execute(
        "SELECT organism_id, lineage_generation, lifecycle_number, schema_version, "
        "environment_version, budget_config_version "
        "FROM organism WHERE singleton_id = 1"
    ).fetchone()
    cursor = connection.execute(
        """
        INSERT INTO event (
            organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
            event_type, source, payload_json, schema_version,
            environment_version, budget_config_version
        ) VALUES (?, ?, ?, ?, ?, 'administration:protected-test-fixture', ?, ?, ?, ?)
        """,
        (
            organism["organism_id"],
            organism["lineage_generation"],
            organism["lifecycle_number"],
            wall_time_utc_us,
            event_type,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
            organism["schema_version"],
            organism["environment_version"],
            organism["budget_config_version"],
        ),
    )
    return int(cursor.lastrowid)


def _prepare_resource_recovery_fixture(paths: OrganismPaths) -> None:
    """Publish a stable failed state with harvest available but watering impossible."""

    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE garden_plot SET moisture = 0, fruit = 0 WHERE plot_id = 'bed-a'"
        )
        connection.execute(
            "UPDATE garden_plot SET moisture = 1, fruit = 1 WHERE plot_id = 'bed-b'"
        )
        connection.execute(
            "UPDATE inventory SET water_units = 0, harvested_fruit = 0 "
            "WHERE singleton_id = 1"
        )
        connection.execute(
            "UPDATE environment_state SET environment_step = 0, objective_complete = 0 "
            "WHERE singleton_id = 1"
        )
        _append_administrative_event(
            connection,
            wall_time_utc_us=100,
            event_type="protected_test_fixture_prepared",
            payload={
                "fixture_id": "resource-aware-harvest-recovery-v1",
                "objective_complete": False,
                "water_units": 0,
                "harvested_fruit": 0,
                "bed_a_moisture": 0,
                "bed_b_fruit": 1,
                "consecutive_failures": 1,
            },
        )
        boundary = _append_administrative_event(
            connection,
            wall_time_utc_us=100,
            event_type="checkpoint_pending",
            payload={
                "reason": "protected_test_fixture",
                "fixture_id": "resource-aware-harvest-recovery-v1",
            },
        )
        connection.execute(
            """
            UPDATE organism
            SET status = 'checkpoint_pending', checkpoint_pending = 1,
                pending_checkpoint_generation = lineage_generation,
                pending_checkpoint_event_sequence = ?, consecutive_failures = 1,
                maintenance_reason = NULL
            WHERE singleton_id = 1
            """,
            (boundary,),
        )
        validate_canonical_state(connection, expect_checkpoint_pending=True)
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()

    checkpoint = create_and_register_lifecycle_checkpoint(
        paths,
        clock=FakeClock(
            [
                ClockReading(101, 1_000_000),
                ClockReading(102, 2_000_000),
            ]
        ),
    )
    assert checkpoint.event_sequence == 5


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


def test_resource_aware_harvest_recovers_and_resets_failure_streak(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_resource_recovery_fixture(paths)

    enqueue_garden_tick(
        paths,
        "recovery-tick-1",
        clock=FakeClock([ClockReading(200, 5_000_000)]),
    )
    result = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=23,
        clock=_wake_clock(),
    )
    status = read_status(paths)

    assert result.decision.as_dict() == {
        "decision_type": "action",
        "action_id": "harvest_plot",
        "action_version": 1,
        "parameters": {"plot_id": "bed-b"},
        "reason": "fixed_policy_first_executable_harvest",
    }
    assert result.evaluation.success is True
    assert result.evaluation.objective_complete_before is False
    assert result.evaluation.objective_complete_after is False
    assert result.evaluation.progress == "positive"
    assert result.evaluation.unresolved_needs_before == 2
    assert result.evaluation.unresolved_needs_after == 1
    assert result.evaluation.environment_step_before == 0
    assert result.evaluation.environment_step_after == 1
    assert result.budget_ledger["consumed"] == {
        "input_events": 1,
        "observations": 1,
        "action_attempts": 1,
        "environment_mutations": 1,
        "caregiver_consultations": 0,
        "network_calls": 0,
        "subprocess_calls": 0,
        "external_mutable_writes": 0,
    }
    assert result.budget_ledger["canonical_records_used"] == 10

    assert (status.lifecycle_number, status.status, status.consecutive_failures) == (
        1,
        "sleeping",
        0,
    )
    assert status.environment_step == 1
    assert status.objective_complete is False
    assert (status.water_units, status.harvested_fruit) == (0, 1)
    assert status.plots == (
        {"plot_id": "bed-a", "stage": "sprout", "moisture": 0, "fruit": 0},
        {"plot_id": "bed-b", "stage": "mature", "moisture": 1, "fruit": 0},
    )
    assert status.latest_stable_event_sequence == result.checkpoint.event_sequence == 17
    assert status.event_count == 18

    connection = connect_database(paths.database, read_only=True)
    try:
        lifecycle_events = connection.execute(
            "SELECT event_type, payload_json FROM event "
            "WHERE lifecycle_number = 1 ORDER BY event_sequence"
        ).fetchall()
        assert [row["event_type"] for row in lifecycle_events] == [
            "wake_accepted",
            "input_claimed",
            "observation_created",
            "action_proposed",
            "action_completed",
            "evaluation_completed",
            "failure_streak_updated",
            "lifecycle_completed",
            "budget_ledger",
            "checkpoint_pending",
            "checkpoint_stabilized",
        ]
        observation = json.loads(lifecycle_events[2]["payload_json"])
        assert observation["inventory"]["water_units"] == 0
        assert observation["actions"][0]["action_id"] == "water_plot"
        assert observation["actions"][0]["applicable_targets"] == []
        assert observation["actions"][1]["action_id"] == "harvest_plot"
        assert observation["actions"][1]["applicable_targets"] == ["bed-b"]
        assert json.loads(lifecycle_events[6]["payload_json"]) == {
            "after": 0,
            "before": 1,
            "maintenance_threshold": 3,
            "reason": "successful_action",
        }
        assert json.loads(lifecycle_events[7]["payload_json"]) == {
            "action_id": "harvest_plot",
            "input_consumed": True,
            "outcome": "action_success",
            "plot_id": "bed-b",
        }
        inbox = connection.execute(
            "SELECT external_event_id, claimed_lifecycle_number, consumed "
            "FROM inbox_event"
        ).fetchone()
        assert tuple(inbox) == ("recovery-tick-1", 1, 1)
    finally:
        connection.close()

    manifest = validate_checkpoint_directory(result.checkpoint.checkpoint_dir)
    assert manifest["provenance"] == "lifecycle"
    assert manifest["lifecycle_number"] == 1
    assert manifest["event_sequence"] == 17
