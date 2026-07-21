from __future__ import annotations

from sudachi_life.clock import FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database


def test_enqueue_tick_is_idempotent_without_second_clock_read(initialized) -> None:
    runtime_root, status, _ = initialized
    paths = OrganismPaths.build(runtime_root, status.organism_id)
    first_clock = FakeClock.fixed(wall_time_utc_us=200, monotonic_ns=20)

    first = enqueue_garden_tick(paths, "tick-1", clock=first_clock)
    duplicate = enqueue_garden_tick(paths, "tick-1", clock=FakeClock([]))

    assert first.inserted is True
    assert duplicate.inserted is False
    assert duplicate.inbox_id == first.inbox_id
    assert duplicate.received_wall_time_utc_us == first.received_wall_time_utc_us

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute("SELECT COUNT(*) FROM inbox_event").fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'input_enqueued'"
        ).fetchone()[0] == 1
    finally:
        connection.close()


def test_enqueue_order_is_stable_by_inbox_id(initialized) -> None:
    runtime_root, status, _ = initialized
    paths = OrganismPaths.build(runtime_root, status.organism_id)
    clock = FakeClock.fixed(wall_time_utc_us=300, monotonic_ns=30, reads=2)

    first = enqueue_garden_tick(paths, "tick-a", clock=clock)
    second = enqueue_garden_tick(paths, "tick-b", clock=clock)

    assert first.inbox_id < second.inbox_id
