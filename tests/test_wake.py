from __future__ import annotations

import pytest

from sudachi_life.clock import FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database
from sudachi_life.wake import WakeBusyError, WakeRejectedError, WakeTransaction


def _paths(initialized) -> OrganismPaths:
    runtime_root, status, _ = initialized
    return OrganismPaths.build(runtime_root, status.organism_id)


def test_competing_wake_is_rejected_and_not_queued(initialized) -> None:
    paths = _paths(initialized)
    enqueue_garden_tick(
        paths,
        "tick-1",
        clock=FakeClock.fixed(wall_time_utc_us=200, monotonic_ns=20),
    )

    winner = WakeTransaction.acquire(paths)
    try:
        with pytest.raises(WakeBusyError, match="not queued"):
            WakeTransaction.acquire(paths)
    finally:
        winner.rollback_and_close()

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT claimed_lifecycle_number FROM inbox_event WHERE external_event_id = 'tick-1'"
        ).fetchone()[0] is None
    finally:
        connection.close()

    explicit_retry = WakeTransaction.acquire(paths)
    explicit_retry.rollback_and_close()


def test_busy_rejection_occurs_before_canonical_validation(initialized, monkeypatch) -> None:
    paths = _paths(initialized)
    holder = connect_database(paths.database)
    holder.execute("BEGIN IMMEDIATE")
    try:
        def forbidden_validation(*args, **kwargs):
            raise AssertionError("mutable validation occurred before lock acquisition")

        monkeypatch.setattr("sudachi_life.wake.validate_canonical_state", forbidden_validation)
        with pytest.raises(WakeBusyError):
            WakeTransaction.acquire(paths)
    finally:
        holder.rollback()
        holder.close()


def test_claims_only_oldest_tick_and_rolls_back_on_context_exit(initialized) -> None:
    paths = _paths(initialized)
    clock = FakeClock.fixed(wall_time_utc_us=200, monotonic_ns=20, reads=2)
    enqueue_garden_tick(paths, "tick-a", clock=clock)
    enqueue_garden_tick(paths, "tick-b", clock=clock)

    with WakeTransaction.acquire(paths) as wake:
        claimed = wake.claim_oldest_garden_tick()
        assert claimed.external_event_id == "tick-a"
        assert claimed.lifecycle_number == 1
        with pytest.raises(WakeRejectedError, match="already claimed"):
            wake.claim_oldest_garden_tick()

    connection = connect_database(paths.database, read_only=True)
    try:
        rows = connection.execute(
            "SELECT external_event_id, claimed_lifecycle_number FROM inbox_event ORDER BY inbox_id"
        ).fetchall()
        assert [(row[0], row[1]) for row in rows] == [
            ("tick-a", None),
            ("tick-b", None),
        ]
    finally:
        connection.close()


def test_observation_is_sorted_and_declares_applicable_actions(initialized) -> None:
    paths = _paths(initialized)
    enqueue_garden_tick(
        paths,
        "tick-1",
        clock=FakeClock.fixed(wall_time_utc_us=200, monotonic_ns=20),
    )

    with WakeTransaction.acquire(paths) as wake:
        wake.claim_oldest_garden_tick()
        observation = wake.build_observation().as_dict()

    assert [plot["plot_id"] for plot in observation["plots"]] == ["bed-a", "bed-b"]
    assert observation["inventory"] == {"water_units": 1, "harvested_fruit": 0}
    assert observation["objective_complete"] is False
    assert observation["actions"][0]["action_id"] == "water_plot"
    assert observation["actions"][0]["applicable_targets"] == ["bed-a"]
    assert observation["actions"][1]["action_id"] == "harvest_plot"
    assert observation["actions"][1]["applicable_targets"] == ["bed-b"]


def test_observation_requires_claimed_input(initialized) -> None:
    paths = _paths(initialized)
    with WakeTransaction.acquire(paths) as wake:
        with pytest.raises(WakeRejectedError, match="must be claimed"):
            wake.build_observation()
