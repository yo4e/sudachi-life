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


def test_second_wake_harvests_and_completes_objective(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)

    enqueue_garden_tick(
        paths, "tick-1", clock=FakeClock([ClockReading(200, 2_000_000)])
    )
    first = perform_garden_wake(
        runtime_root, initial.organism_id, seed=1, clock=_wake_clock(300)
    )
    assert first.decision.action_id == "water_plot"

    enqueue_garden_tick(
        paths, "tick-2", clock=FakeClock([ClockReading(400, 4_000_000)])
    )
    second_clock = _wake_clock(500)
    second = perform_garden_wake(
        runtime_root, initial.organism_id, seed=2, clock=second_clock
    )
    status = read_status(paths)

    assert second_clock.read_count == 4
    assert second.decision.action_id == "harvest_plot"
    assert second.decision.as_dict()["parameters"] == {"plot_id": "bed-b"}
    assert second.evaluation.success is True
    assert second.evaluation.objective_complete_before is False
    assert second.evaluation.objective_complete_after is True
    assert second.evaluation.unresolved_needs_before == 1
    assert second.evaluation.unresolved_needs_after == 0
    assert second.budget_ledger["consumed"] == {
        "input_events": 1,
        "observations": 1,
        "action_attempts": 1,
        "environment_mutations": 1,
        "caregiver_consultations": 0,
        "network_calls": 0,
        "subprocess_calls": 0,
        "external_mutable_writes": 0,
    }

    assert (status.lifecycle_number, status.status, status.environment_step) == (
        2,
        "sleeping",
        2,
    )
    assert status.objective_complete is True
    assert (status.water_units, status.harvested_fruit, status.event_count) == (0, 1, 25)
    assert status.plots[1]["plot_id"] == "bed-b"
    assert status.plots[1]["fruit"] == 0
    assert status.latest_stable_event_sequence == second.checkpoint.event_sequence == 24

    connection = connect_database(paths.database, read_only=True)
    try:
        inbox = connection.execute(
            "SELECT external_event_id, claimed_lifecycle_number, consumed "
            "FROM inbox_event ORDER BY inbox_id"
        ).fetchall()
        assert [tuple(row) for row in inbox] == [
            ("tick-1", 1, 1),
            ("tick-2", 2, 1),
        ]
        completed = connection.execute(
            "SELECT payload_json FROM event "
            "WHERE lifecycle_number = 2 AND event_type = 'lifecycle_completed'"
        ).fetchone()
        assert json.loads(completed[0])["action_id"] == "harvest_plot"
    finally:
        connection.close()

    manifest = validate_checkpoint_directory(second.checkpoint.checkpoint_dir)
    assert manifest["provenance"] == "lifecycle"
    assert manifest["lifecycle_number"] == 2
    assert manifest["event_sequence"] == 24
