from __future__ import annotations

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def test_first_water_wake_commits_evaluates_and_checkpoints(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(paths, "tick-1", clock=FakeClock([ClockReading(200, 2_000_000)]))
    clock = FakeClock([
        ClockReading(300, 10_000_000), ClockReading(300, 15_000_000),
        ClockReading(301, 20_000_000), ClockReading(302, 30_000_000),
        ClockReading(303, 40_000_000),
    ])
    result = perform_first_water_wake(runtime_root, initial.organism_id, seed=1, clock=clock)
    status = read_status(paths)

    assert clock.read_count == 5
    assert result.decision.as_dict()["parameters"] == {"plot_id": "bed-a"}
    assert result.evaluation.success is True
    assert result.evaluation.progress == "positive"
    assert result.budget_ledger["consumed"] == {
        "input_events": 1, "observations": 1, "action_attempts": 1,
        "environment_mutations": 1, "caregiver_consultations": 0,
        "network_calls": 0, "subprocess_calls": 0, "external_mutable_writes": 0,
    }
    assert (status.lifecycle_number, status.status, status.environment_step) == (1, "sleeping", 1)
    assert (status.water_units, status.event_count) == (0, 14)
    assert status.plots[0]["plot_id"] == "bed-a"
    assert status.plots[0]["moisture"] == 1
    assert status.latest_stable_event_sequence == result.checkpoint.event_sequence == 13

    connection = connect_database(paths.database, read_only=True)
    try:
        assert tuple(connection.execute(
            "SELECT claimed_lifecycle_number, consumed FROM inbox_event"
        ).fetchone()) == (1, 1)
        types = [row[0] for row in connection.execute(
            "SELECT event_type FROM event ORDER BY event_sequence"
        ).fetchall()]
        assert types[-2:] == ["checkpoint_pending", "checkpoint_stabilized"]
    finally:
        connection.close()

    manifest = validate_checkpoint_directory(result.checkpoint.checkpoint_dir)
    assert manifest["provenance"] == "lifecycle"
    assert manifest["lifecycle_number"] == 1
