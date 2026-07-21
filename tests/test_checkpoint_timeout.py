from __future__ import annotations

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import read_status


def test_checkpoint_timeout_preserves_committed_pending_boundary(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(paths, "tick-1", clock=FakeClock([ClockReading(200, 2_000_000)]))
    clock = FakeClock([
        ClockReading(300, 10_000_000), ClockReading(301, 20_000_000),
        ClockReading(302, 30_000_000), ClockReading(303, 5_030_000_001),
    ])

    with pytest.raises(CheckpointError, match="deadline"):
        perform_first_water_wake(runtime_root, initial.organism_id, seed=1, clock=clock)

    status = read_status(paths)
    assert status.status == "checkpoint_pending"
    assert status.checkpoint_pending is True
    assert (status.lifecycle_number, status.environment_step, status.water_units) == (1, 1, 0)
    assert status.latest_stable_event_sequence == 2
