from __future__ import annotations

import json

import pytest

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import (
    CHECKPOINT_RETENTION_LIMIT,
    MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
)
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.maintenance import inspect_maintenance
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status
from sudachi_life.wake import WakeRejectedError


def _wake_clock(base: int) -> FakeClock:
    return FakeClock(
        [
            ClockReading(base, 10_000_000),
            ClockReading(base, 15_000_000),
            ClockReading(base + 1, 20_000_000),
            ClockReading(base + 2, 30_000_000),
            ClockReading(base + 3, 40_000_000),
        ]
    )


def _checkpoint_rows(paths: OrganismPaths):
    connection = connect_database(paths.database, read_only=True)
    try:
        return connection.execute(
            "SELECT checkpoint_id, lineage_generation, event_sequence, "
            "database_size_bytes FROM checkpoint_registry "
            "ORDER BY event_sequence, checkpoint_id"
        ).fetchall()
    finally:
        connection.close()


def _stable_checkpoint_dirs(paths: OrganismPaths) -> list[str]:
    return sorted(
        path.name
        for path in paths.checkpoints.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    )


def _checkpoint_store_size(paths: OrganismPaths) -> int:
    return sum(
        path.stat().st_size
        for path in paths.checkpoints.rglob("*")
        if path.is_file() and not path.is_symlink()
    )


def test_retention_failure_restores_candidate_and_enters_maintenance(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)

    results = []
    for index, base in enumerate((300, 500, 700), start=1):
        enqueue_garden_tick(
            paths,
            f"tick-{index}",
            clock=FakeClock([ClockReading(base - 100, base * 1_000)]),
        )
        results.append(
            perform_garden_wake(
                runtime_root,
                initial.organism_id,
                seed=index,
                clock=_wake_clock(base),
            )
        )

    first, second, third = results
    before_rows = _checkpoint_rows(paths)
    assert [row["event_sequence"] for row in before_rows] == [2, 13, 24, 34]
    assert len(before_rows) == CHECKPOINT_RETENTION_LIMIT
    assert _stable_checkpoint_dirs(paths) == sorted(
        [
            genesis.checkpoint_id,
            first.checkpoint.checkpoint_id,
            second.checkpoint.checkpoint_id,
            third.checkpoint.checkpoint_id,
        ]
    )

    enqueue_garden_tick(
        paths,
        "tick-4",
        clock=FakeClock([ClockReading(800, 800_000)]),
    )
    fourth_clock = _wake_clock(900)
    fourth = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=4,
        clock=fourth_clock,
        protected_test_retention_failure_after_stage=True,
    )

    status = read_status(paths)
    after_rows = _checkpoint_rows(paths)
    retained_ids = [str(row["checkpoint_id"]) for row in after_rows]
    retained_boundaries = [int(row["event_sequence"]) for row in after_rows]
    store_bytes = _checkpoint_store_size(paths)

    assert fourth_clock.read_count == 5
    assert fourth.decision.as_dict() == {
        "decision_type": "abstention",
        "reason": "objective_already_complete",
    }
    assert fourth.checkpoint.event_sequence == 44
    assert fourth.status == "maintenance_required"

    assert status.lifecycle_number == 4
    assert status.status == "maintenance_required"
    assert status.maintenance_reason == MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED
    assert status.checkpoint_pending is False
    assert status.consecutive_failures == 0
    assert status.objective_complete is True
    assert status.environment_step == 2
    assert status.water_units == 0
    assert status.harvested_fruit == 1
    assert status.latest_stable_checkpoint_id == fourth.checkpoint.checkpoint_id
    assert status.latest_stable_event_sequence == 44
    assert status.event_count == 46

    assert retained_boundaries == [2, 13, 24, 34, 44]
    assert len(after_rows) == CHECKPOINT_RETENTION_LIMIT + 1
    assert retained_ids == [
        genesis.checkpoint_id,
        first.checkpoint.checkpoint_id,
        second.checkpoint.checkpoint_id,
        third.checkpoint.checkpoint_id,
        fourth.checkpoint.checkpoint_id,
    ]
    assert _stable_checkpoint_dirs(paths) == sorted(retained_ids)
    assert first.checkpoint.checkpoint_dir.is_dir()
    assert fourth.checkpoint.checkpoint_dir.is_dir()
    assert not any(path.name.startswith(".pruning-") for path in paths.checkpoints.iterdir())

    for checkpoint_id in retained_ids:
        manifest = validate_checkpoint_directory(paths.checkpoints / checkpoint_id)
        assert manifest["checkpoint_id"] == checkpoint_id

    connection = connect_database(paths.database, read_only=True)
    try:
        lifecycle_events = connection.execute(
            "SELECT event_sequence, event_type, source, payload_json "
            "FROM event WHERE lifecycle_number = 4 ORDER BY event_sequence"
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
            "checkpoint_retention_failed",
        ]
        assert lifecycle_events[-2]["event_sequence"] == 45
        assert lifecycle_events[-1]["event_sequence"] == 46
        assert lifecycle_events[-1]["source"] == "administration:checkpoint-retention"
        failure_payload = json.loads(lifecycle_events[-1]["payload_json"])
        assert failure_payload == {
            "candidate_checkpoint_id": first.checkpoint.checkpoint_id,
            "candidate_event_sequence": 13,
            "candidate_restored": True,
            "checkpoint_store_bytes": store_bytes,
            "injection_point": "after_artifact_stage_before_registry_mutation",
            "latest_stable_checkpoint_id": fourth.checkpoint.checkpoint_id,
            "latest_stable_event_sequence": 44,
            "maintenance_reason": MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
            "reason": "protected_test_injected_checkpoint_retention_failure",
            "registered_checkpoint_boundaries": [2, 13, 24, 34, 44],
            "registered_checkpoint_count": CHECKPOINT_RETENTION_LIMIT + 1,
            "retention_limit": CHECKPOINT_RETENTION_LIMIT,
            "stable_checkpoint_count": CHECKPOINT_RETENTION_LIMIT + 1,
            "status_after": "maintenance_required",
        }
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'checkpoint_pruned'"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'checkpoint_retention_failed'"
        ).fetchone()[0] == 1
        inbox = connection.execute(
            "SELECT external_event_id, claimed_lifecycle_number, consumed "
            "FROM inbox_event ORDER BY inbox_id"
        ).fetchall()
        assert [tuple(row) for row in inbox] == [
            ("tick-1", 1, 1),
            ("tick-2", 2, 1),
            ("tick-3", 3, 1),
            ("tick-4", 4, 1),
        ]
    finally:
        connection.close()

    inspection = inspect_maintenance(runtime_root, initial.organism_id)
    assert inspection.maintenance_reason == MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED
    assert inspection.consecutive_failures == 0
    assert inspection.latest_stable_checkpoint.checkpoint_id == fourth.checkpoint.checkpoint_id
    assert inspection.latest_stable_checkpoint.event_sequence == 44
    assert inspection.total_input_events == 4
    assert inspection.consumed_input_events == 4
    assert inspection.pending_inputs == ()

    rejected_clock = FakeClock([])
    before_rejection = read_status(paths)
    with pytest.raises(
        WakeRejectedError,
        match="organism is not wakeable: status=maintenance_required",
    ):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=5,
            clock=rejected_clock,
        )
    after_rejection = read_status(paths)
    assert rejected_clock.read_count == 0
    assert after_rejection == before_rejection
