from __future__ import annotations

import json
import sqlite3

import pytest

from sudachi_life.checkpoints import (
    create_and_register_lifecycle_checkpoint,
    validate_checkpoint_directory,
)
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import (
    CONSECUTIVE_FAILURE_LIMIT,
    MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
)
from sudachi_life.wake import WakeRejectedError
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


def _prepare_threshold_fixture(paths: OrganismPaths) -> None:
    """Publish a stable blocked state one failure below maintenance."""

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
                "fixture_id": "maintenance-threshold-blocked-v1",
                "objective_complete": False,
                "water_units": 0,
                "harvested_fruit": 0,
                "bed_a_moisture": 0,
                "bed_b_fruit": 0,
                "consecutive_failures": 2,
            },
        )
        boundary = _append_administrative_event(
            connection,
            wall_time_utc_us=100,
            event_type="checkpoint_pending",
            payload={
                "reason": "protected_test_fixture",
                "fixture_id": "maintenance-threshold-blocked-v1",
            },
        )
        connection.execute(
            """
            UPDATE organism
            SET status = 'checkpoint_pending', checkpoint_pending = 1,
                pending_checkpoint_generation = lineage_generation,
                pending_checkpoint_event_sequence = ?, consecutive_failures = 2,
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


def test_third_classified_failure_enters_maintenance_and_blocks_later_wake(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_threshold_fixture(paths)

    enqueue_garden_tick(
        paths,
        "maintenance-threshold-tick-1",
        clock=FakeClock([ClockReading(200, 5_000_000)]),
    )
    enqueue_garden_tick(
        paths,
        "maintenance-threshold-tick-2",
        clock=FakeClock([ClockReading(201, 6_000_000)]),
    )

    result = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=37,
        clock=_wake_clock(),
    )
    status = read_status(paths)

    assert result.decision.as_dict() == {
        "decision_type": "abstention",
        "reason": "no_applicable_action",
    }
    assert result.evaluation.success is False
    assert result.evaluation.progress == "blocked_no_applicable_action"
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
    assert result.budget_ledger["canonical_records_used"] == 9

    assert result.status == "maintenance_required"
    assert (
        status.lifecycle_number,
        status.status,
        status.consecutive_failures,
    ) == (1, "maintenance_required", CONSECUTIVE_FAILURE_LIMIT)
    assert status.maintenance_reason == MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT
    assert status.checkpoint_pending is False
    assert status.environment_step == 0
    assert status.objective_complete is False
    assert (status.water_units, status.harvested_fruit) == (0, 0)
    assert status.plots == (
        {"plot_id": "bed-a", "stage": "sprout", "moisture": 0, "fruit": 0},
        {"plot_id": "bed-b", "stage": "mature", "moisture": 1, "fruit": 0},
    )
    assert status.latest_stable_event_sequence == result.checkpoint.event_sequence == 17
    assert status.event_count == 19

    connection = connect_database(paths.database, read_only=True)
    try:
        lifecycle_events = connection.execute(
            "SELECT event_type, source, payload_json FROM event "
            "WHERE lifecycle_number = 1 ORDER BY event_sequence"
        ).fetchall()
        assert [row["event_type"] for row in lifecycle_events] == [
            "wake_accepted",
            "input_claimed",
            "observation_created",
            "action_abstained",
            "evaluation_completed",
            "failure_streak_updated",
            "lifecycle_completed",
            "budget_ledger",
            "checkpoint_pending",
            "checkpoint_stabilized",
            "maintenance_entered",
        ]
        assert json.loads(lifecycle_events[5]["payload_json"]) == {
            "after": 3,
            "before": 2,
            "maintenance_reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            "maintenance_required": True,
            "maintenance_threshold": 3,
            "reason": "no_applicable_action",
        }
        assert json.loads(lifecycle_events[8]["payload_json"]) == {
            "final_status": "maintenance_required",
            "lifecycle_number": 1,
            "maintenance_reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            "reason": "committed_wake",
        }
        stabilized_payload = json.loads(lifecycle_events[9]["payload_json"])
        assert stabilized_payload == {
            "checkpoint_id": result.checkpoint.checkpoint_id,
            "event_sequence": 17,
            "final_status": "maintenance_required",
            "maintenance_reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
        }
        assert lifecycle_events[9]["source"] == "administration:checkpoint"
        assert json.loads(lifecycle_events[10]["payload_json"]) == {
            "checkpoint_event_sequence": 17,
            "checkpoint_id": result.checkpoint.checkpoint_id,
            "consecutive_failures": 3,
            "maintenance_threshold": 3,
            "reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
        }
        assert lifecycle_events[10]["source"] == "administration:checkpoint"

        inbox = connection.execute(
            "SELECT external_event_id, claimed_lifecycle_number, consumed "
            "FROM inbox_event ORDER BY inbox_id"
        ).fetchall()
        assert [tuple(row) for row in inbox] == [
            ("maintenance-threshold-tick-1", 1, 1),
            ("maintenance-threshold-tick-2", None, 0),
        ]
    finally:
        connection.close()

    manifest = validate_checkpoint_directory(result.checkpoint.checkpoint_dir)
    assert manifest["provenance"] == "lifecycle"
    assert manifest["lifecycle_number"] == 1
    assert manifest["event_sequence"] == 17

    snapshot = sqlite3.connect(result.checkpoint.checkpoint_dir / "organism.sqlite3")
    snapshot.row_factory = sqlite3.Row
    try:
        pending = snapshot.execute(
            "SELECT status, checkpoint_pending, consecutive_failures, maintenance_reason "
            "FROM organism WHERE singleton_id = 1"
        ).fetchone()
        assert tuple(pending) == (
            "checkpoint_pending",
            1,
            3,
            MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
        )
    finally:
        snapshot.close()

    rejected_clock = FakeClock([])
    before_rejection = read_status(paths)
    with pytest.raises(
        WakeRejectedError,
        match="organism is not wakeable: status=maintenance_required",
    ):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=38,
            clock=rejected_clock,
        )
    after_rejection = read_status(paths)

    assert rejected_clock.read_count == 0
    assert after_rejection == before_rejection

    connection = connect_database(paths.database, read_only=True)
    try:
        queued = connection.execute(
            "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
            "WHERE external_event_id = 'maintenance-threshold-tick-2'"
        ).fetchone()
        assert tuple(queued) == (None, 0)
        assert connection.execute("SELECT COUNT(*) FROM event").fetchone()[0] == 19
    finally:
        connection.close()
