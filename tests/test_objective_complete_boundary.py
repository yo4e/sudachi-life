from __future__ import annotations

import json

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def _wake_clock(base: int) -> FakeClock:
    return FakeClock(
        [
            ClockReading(base, 10_000_000),
            ClockReading(base + 1, 20_000_000),
            ClockReading(base + 2, 30_000_000),
            ClockReading(base + 3, 40_000_000),
        ]
    )


def test_third_wake_abstains_after_objective_completion(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)

    results = []
    for event_id, seed, base in (
        ("tick-1", 1, 300),
        ("tick-2", 2, 500),
        ("tick-3", 3, 700),
    ):
        enqueue_garden_tick(
            paths,
            event_id,
            clock=FakeClock([ClockReading(base - 100, base * 1_000)]),
        )
        results.append(
            perform_garden_wake(
                runtime_root,
                initial.organism_id,
                seed=seed,
                clock=_wake_clock(base),
            )
        )

    first, second, third = results
    status = read_status(paths)

    assert first.decision.as_dict()["action_id"] == "water_plot"
    assert second.decision.as_dict()["action_id"] == "harvest_plot"
    assert third.decision.as_dict() == {
        "decision_type": "abstention",
        "reason": "objective_already_complete",
    }
    assert third.evaluation.success is True
    assert third.evaluation.objective_complete_before is True
    assert third.evaluation.objective_complete_after is True
    assert third.evaluation.progress == "objective_complete_unchanged"
    assert third.evaluation.unresolved_needs_before == 0
    assert third.evaluation.unresolved_needs_after == 0
    assert third.evaluation.environment_step_before == 2
    assert third.evaluation.environment_step_after == 2
    assert third.budget_ledger["consumed"] == {
        "input_events": 1,
        "observations": 1,
        "action_attempts": 0,
        "environment_mutations": 0,
        "caregiver_consultations": 0,
        "network_calls": 0,
        "subprocess_calls": 0,
        "external_mutable_writes": 0,
    }

    assert (status.lifecycle_number, status.status, status.environment_step) == (
        3,
        "sleeping",
        2,
    )
    assert status.objective_complete is True
    assert status.consecutive_failures == 0
    assert (status.water_units, status.harvested_fruit, status.event_count) == (0, 1, 35)
    assert status.plots[0]["moisture"] == 1
    assert status.plots[1]["fruit"] == 0
    assert status.latest_stable_event_sequence == third.checkpoint.event_sequence == 34

    connection = connect_database(paths.database, read_only=True)
    try:
        inbox = connection.execute(
            "SELECT external_event_id, claimed_lifecycle_number, consumed "
            "FROM inbox_event ORDER BY inbox_id"
        ).fetchall()
        assert [tuple(row) for row in inbox] == [
            ("tick-1", 1, 1),
            ("tick-2", 2, 1),
            ("tick-3", 3, 1),
        ]
        lifecycle_events = connection.execute(
            "SELECT event_type, payload_json FROM event "
            "WHERE lifecycle_number = 3 ORDER BY event_sequence"
        ).fetchall()
        assert [row["event_type"] for row in lifecycle_events] == [
            "wake_accepted",
            "input_claimed",
            "observation_created",
            "action_abstained",
            "evaluation_completed",
            "lifecycle_completed",
            "budget_ledger",
            "checkpoint_pending",
            "checkpoint_stabilized",
        ]
        assert json.loads(lifecycle_events[3]["payload_json"]) == {
            "decision_type": "abstention",
            "reason": "objective_already_complete",
        }
        assert json.loads(lifecycle_events[5]["payload_json"]) == {
            "input_consumed": True,
            "outcome": "abstention",
            "reason": "objective_already_complete",
        }
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE lifecycle_number = 3 "
            "AND event_type IN ('action_proposed', 'action_completed')"
        ).fetchone()[0] == 0
    finally:
        connection.close()

    manifest = validate_checkpoint_directory(third.checkpoint.checkpoint_dir)
    assert manifest["provenance"] == "lifecycle"
    assert manifest["lifecycle_number"] == 3
    assert manifest["event_sequence"] == 34
