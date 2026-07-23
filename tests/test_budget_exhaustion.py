from __future__ import annotations

import json

from sudachi_life.checkpoints import (
    create_and_register_lifecycle_checkpoint,
    validate_checkpoint_directory,
)
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import PHASE1_BUDGETS
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


def _prepare_single_water_action_fixture(paths: OrganismPaths) -> None:
    """Publish one stable state with only water_plot executable."""

    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE garden_plot SET moisture = 0, fruit = 0 WHERE plot_id = 'bed-a'"
        )
        connection.execute(
            "UPDATE garden_plot SET moisture = 1, fruit = 0 WHERE plot_id = 'bed-b'"
        )
        connection.execute(
            "UPDATE inventory SET water_units = 1, harvested_fruit = 0 "
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
                "fixture_id": "single-water-lifecycle-budget-exhaustion-v1",
                "objective_complete": False,
                "water_units": 1,
                "harvested_fruit": 0,
                "bed_a_moisture": 0,
                "bed_b_fruit": 0,
                "consecutive_failures": 0,
                "exhausted_budget": "lifecycle_wall_time_ms",
                "protected_budget_configuration_changed": False,
            },
        )
        boundary = _append_administrative_event(
            connection,
            wall_time_utc_us=100,
            event_type="checkpoint_pending",
            payload={
                "reason": "protected_test_fixture",
                "fixture_id": "single-water-lifecycle-budget-exhaustion-v1",
            },
        )
        connection.execute(
            """
            UPDATE organism
            SET status = 'checkpoint_pending', checkpoint_pending = 1,
                pending_checkpoint_generation = lineage_generation,
                pending_checkpoint_event_sequence = ?, consecutive_failures = 0,
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


def _exhausted_wake_clock() -> FakeClock:
    return FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(301, 2_011_000_000),
            ClockReading(302, 2_020_000_000),
            ClockReading(303, 2_030_000_000),
            ClockReading(304, 2_040_000_000),
        ]
    )


def test_lifecycle_budget_exhaustion_prevents_action_and_checkpoints(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_single_water_action_fixture(paths)

    enqueue_garden_tick(
        paths,
        "budget-exhausted-water-tick-1",
        clock=FakeClock([ClockReading(200, 5_000_000)]),
    )
    clock = _exhausted_wake_clock()
    result = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=31,
        clock=clock,
    )
    status = read_status(paths)

    assert clock.read_count == 5
    assert result.decision.as_dict() == {
        "decision_type": "action",
        "action_id": "water_plot",
        "action_version": 1,
        "parameters": {"plot_id": "bed-a"},
        "reason": "fixed_policy_first_executable_dry_plot",
    }
    assert result.budget_exhaustion is not None
    assert result.budget_exhaustion.as_dict() == {
        "budget_name": "lifecycle_wall_time_ms",
        "configured_initial_value": 2_000,
        "consumed_amount": 2_001,
        "remaining_amount": 0,
        "unit": "ms",
        "attempted_forbidden_operation": "execute_garden_action",
        "environment_step": 0,
        "state_mutation_occurred": False,
        "observed_elapsed_monotonic_ns": 2_001_000_000,
        "reason": "lifecycle_wall_time_exhausted_before_action",
        "success": False,
    }
    assert result.evaluation.success is False
    assert result.evaluation.progress == "budget_exhausted_before_action"
    assert result.evaluation.objective_complete_before is False
    assert result.evaluation.objective_complete_after is False
    assert result.evaluation.unresolved_needs_before == 2
    assert result.evaluation.unresolved_needs_after == 2
    assert result.evaluation.environment_step_before == 0
    assert result.evaluation.environment_step_after == 0

    assert result.budget_ledger["consumed"] == {
        "input_events": 1,
        "observations": 1,
        "action_attempts": 0,
        "environment_mutations": 0,
        "caregiver_consultations": 0,
        "network_calls": 0,
        "subprocess_calls": 0,
        "external_mutable_writes": 0,
    }
    assert result.budget_ledger["remaining"] == {
        "input_events": 0,
        "observations": 0,
        "action_attempts": 1,
        "environment_mutations": 1,
        "caregiver_consultations": 0,
        "network_calls": 0,
        "subprocess_calls": 0,
        "external_mutable_writes": 0,
    }
    assert result.budget_ledger["canonical_records_used"] == 9
    assert result.budget_ledger["elapsed_monotonic_ns"] == 2_010_000_000
    assert result.budget_ledger["exhaustion"] == result.budget_exhaustion.as_dict()

    assert (status.lifecycle_number, status.status, status.consecutive_failures) == (
        1,
        "sleeping",
        1,
    )
    assert status.environment_step == 0
    assert status.objective_complete is False
    assert (status.water_units, status.harvested_fruit) == (1, 0)
    assert status.plots == (
        {"plot_id": "bed-a", "stage": "sprout", "moisture": 0, "fruit": 0},
        {"plot_id": "bed-b", "stage": "mature", "moisture": 1, "fruit": 0},
    )
    assert status.latest_stable_event_sequence == result.checkpoint.event_sequence == 16
    assert status.event_count == 17

    connection = connect_database(paths.database, read_only=True)
    try:
        budget_config = connection.execute(
            "SELECT config_json FROM budget_config WHERE singleton_id = 1"
        ).fetchone()
        assert json.loads(budget_config["config_json"]) == PHASE1_BUDGETS.as_dict()

        lifecycle_events = connection.execute(
            "SELECT event_type, payload_json FROM event "
            "WHERE lifecycle_number = 1 ORDER BY event_sequence"
        ).fetchall()
        assert [row["event_type"] for row in lifecycle_events] == [
            "wake_accepted",
            "input_claimed",
            "observation_created",
            "budget_exhausted",
            "evaluation_completed",
            "failure_streak_updated",
            "lifecycle_completed",
            "budget_ledger",
            "checkpoint_pending",
            "checkpoint_stabilized",
        ]
        observation = json.loads(lifecycle_events[2]["payload_json"])
        assert observation["actions"][0]["applicable_targets"] == ["bed-a"]
        assert observation["actions"][1]["applicable_targets"] == []

        exhausted_payload = json.loads(lifecycle_events[3]["payload_json"])
        assert exhausted_payload["decision"] == result.decision.as_dict()
        del exhausted_payload["decision"]
        assert exhausted_payload == result.budget_exhaustion.as_dict()
        assert json.loads(lifecycle_events[5]["payload_json"]) == {
            "after": 1,
            "before": 0,
            "maintenance_threshold": 3,
            "reason": "lifecycle_wall_time_exhausted_before_action",
        }
        assert json.loads(lifecycle_events[6]["payload_json"]) == {
            "attempted_forbidden_operation": "execute_garden_action",
            "budget_name": "lifecycle_wall_time_ms",
            "input_consumed": True,
            "outcome": "budget_exhaustion",
            "reason": "lifecycle_wall_time_exhausted_before_action",
        }
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE lifecycle_number = 1 "
            "AND event_type IN ('action_proposed', 'action_completed', 'action_failed')"
        ).fetchone()[0] == 0
        inbox = connection.execute(
            "SELECT external_event_id, claimed_lifecycle_number, consumed "
            "FROM inbox_event"
        ).fetchone()
        assert tuple(inbox) == ("budget-exhausted-water-tick-1", 1, 1)
    finally:
        connection.close()

    manifest = validate_checkpoint_directory(result.checkpoint.checkpoint_dir)
    assert manifest["provenance"] == "lifecycle"
    assert manifest["lifecycle_number"] == 1
    assert manifest["event_sequence"] == 16
