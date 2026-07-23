from __future__ import annotations

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def test_backward_wall_time_does_not_reorder_complete_first_wake(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)

    enqueue_garden_tick(
        paths,
        "backward-wall-time-tick",
        clock=FakeClock(
            [ClockReading(1_600_000_000_000_000, 9_000_000)]
        ),
    )
    clock = FakeClock(
        [
            ClockReading(1_500_000_000_000_000, 10_000_000),
            ClockReading(1_400_000_000_000_000, 15_000_000),
            ClockReading(1_300_000_000_000_000, 20_000_000),
            ClockReading(1_200_000_000_000_000, 30_000_000),
            ClockReading(1_100_000_000_000_000, 40_000_000),
        ]
    )

    result = perform_first_water_wake(
        runtime_root,
        initial.organism_id,
        seed=1,
        clock=clock,
    )
    status = read_status(paths)

    assert clock.read_count == 5
    assert result.decision.as_dict()["parameters"] == {"plot_id": "bed-a"}
    assert result.evaluation.success is True
    assert result.checkpoint.event_sequence == 13
    assert status.status == "sleeping"
    assert status.lifecycle_number == 1
    assert status.environment_step == 1
    assert status.event_count == 14

    connection = connect_database(paths.database, read_only=True)
    try:
        events = connection.execute(
            "SELECT event_sequence, event_type, wall_time_utc_us "
            "FROM event ORDER BY event_sequence"
        ).fetchall()
    finally:
        connection.close()

    assert [int(row["event_sequence"]) for row in events] == list(range(1, 15))
    assert [str(row["event_type"]) for row in events] == [
        "organism_initialized",
        "checkpoint_pending",
        "checkpoint_stabilized",
        "input_enqueued",
        "wake_accepted",
        "input_claimed",
        "observation_created",
        "action_proposed",
        "action_completed",
        "evaluation_completed",
        "lifecycle_completed",
        "budget_ledger",
        "checkpoint_pending",
        "checkpoint_stabilized",
    ]

    wall_times = [int(row["wall_time_utc_us"]) for row in events]
    assert wall_times[2] > wall_times[3] > wall_times[4]
    assert wall_times[4] > wall_times[11] > wall_times[13]
    assert any(later < earlier for earlier, later in zip(wall_times, wall_times[1:]))
