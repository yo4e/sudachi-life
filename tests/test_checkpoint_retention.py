from __future__ import annotations

import json

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import CHECKPOINT_RETENTION_LIMIT
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status
from sudachi_life.wake import WakeTransaction


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


def test_fifth_stable_checkpoint_prunes_oldest_eligible_after_registration(initialized) -> None:
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
    before_store_size = sum(
        path.stat().st_size
        for path in paths.checkpoints.rglob("*")
        if path.is_file() and not path.is_symlink()
    )
    first_artifact_size = sum(
        path.stat().st_size
        for path in first.checkpoint.checkpoint_dir.rglob("*")
        if path.is_file() and not path.is_symlink()
    )
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
    assert first.checkpoint.checkpoint_dir.is_dir()

    enqueue_garden_tick(
        paths,
        "tick-4",
        clock=FakeClock([ClockReading(800, 800_000)]),
    )
    fourth = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=4,
        clock=_wake_clock(900),
    )

    status = read_status(paths)
    after_rows = _checkpoint_rows(paths)
    retained_ids = [row["checkpoint_id"] for row in after_rows]
    retained_boundaries = [row["event_sequence"] for row in after_rows]

    assert fourth.decision.as_dict() == {
        "decision_type": "abstention",
        "reason": "objective_already_complete",
    }
    assert fourth.checkpoint.event_sequence == 44
    assert status.lifecycle_number == 4
    assert status.status == "sleeping"
    assert status.checkpoint_pending is False
    assert status.objective_complete is True
    assert status.environment_step == 2
    assert status.water_units == 0
    assert status.harvested_fruit == 1
    assert status.consecutive_failures == 0
    assert status.latest_stable_checkpoint_id == fourth.checkpoint.checkpoint_id
    assert status.latest_stable_event_sequence == 44
    assert status.event_count == 46

    assert retained_boundaries == [2, 24, 34, 44]
    assert len(after_rows) == CHECKPOINT_RETENTION_LIMIT
    assert retained_ids == [
        genesis.checkpoint_id,
        second.checkpoint.checkpoint_id,
        third.checkpoint.checkpoint_id,
        fourth.checkpoint.checkpoint_id,
    ]
    assert _stable_checkpoint_dirs(paths) == sorted(retained_ids)
    assert genesis.checkpoint_dir.is_dir()
    assert not first.checkpoint.checkpoint_dir.exists()
    assert second.checkpoint.checkpoint_dir.is_dir()
    assert third.checkpoint.checkpoint_dir.is_dir()
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
            "checkpoint_pruned",
        ]
        assert lifecycle_events[-2]["event_sequence"] == 45
        assert lifecycle_events[-1]["event_sequence"] == 46
        assert lifecycle_events[-1]["source"] == "administration:checkpoint-retention"
        prune_payload = json.loads(lifecycle_events[-1]["payload_json"])
        assert prune_payload == {
            "latest_stable_checkpoint_id": fourth.checkpoint.checkpoint_id,
            "latest_stable_event_sequence": 44,
            "pruned_artifact_size_bytes": first_artifact_size,
            "pruned_checkpoint_id": first.checkpoint.checkpoint_id,
            "pruned_database_size_bytes": first.checkpoint.database_size_bytes,
            "pruned_event_sequence": 13,
            "pruned_lineage_generation": 0,
            "pruned_provenance": "lifecycle",
            "reason": "checkpoint_retention_limit",
            "retained_checkpoint_count": CHECKPOINT_RETENTION_LIMIT,
            "retained_checkpoint_store_bytes": before_store_size
            + sum(
                path.stat().st_size
                for path in fourth.checkpoint.checkpoint_dir.rglob("*")
                if path.is_file() and not path.is_symlink()
            )
            - first_artifact_size,
            "retention_limit": CHECKPOINT_RETENTION_LIMIT,
        }
        after_store_size = sum(
            path.stat().st_size
            for path in paths.checkpoints.rglob("*")
            if path.is_file() and not path.is_symlink()
        )
        assert first_artifact_size > 0
        assert prune_payload["retained_checkpoint_store_bytes"] == after_store_size
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

    with WakeTransaction.acquire(paths):
        pass
    assert read_status(paths).event_count == 46
