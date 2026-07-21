from __future__ import annotations

import pytest

from sudachi_life.actions import ActionRejectedError
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


def test_objective_complete_state_refuses_a_third_mutation_without_abstention(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)

    for event_id, seed, base in (("tick-1", 1, 300), ("tick-2", 2, 500)):
        enqueue_garden_tick(
            paths,
            event_id,
            clock=FakeClock([ClockReading(base - 100, base * 1_000)]),
        )
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=seed,
            clock=_wake_clock(base),
        )

    enqueue_garden_tick(
        paths, "tick-3", clock=FakeClock([ClockReading(700, 7_000_000)])
    )
    before = read_status(paths)

    with pytest.raises(ActionRejectedError, match="abstention is not implemented"):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=3,
            clock=FakeClock([ClockReading(800, 8_000_000)]),
        )

    after = read_status(paths)
    assert after == before

    connection = connect_database(paths.database, read_only=True)
    try:
        pending = connection.execute(
            "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
            "WHERE external_event_id = 'tick-3'"
        ).fetchone()
        assert tuple(pending) == (None, 0)
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE lifecycle_number = 3"
        ).fetchone()[0] == 0
    finally:
        connection.close()
