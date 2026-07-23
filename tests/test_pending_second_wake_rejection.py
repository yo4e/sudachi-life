from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from sudachi_life.checkpoint_repair import repair_pending_checkpoint_registration
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status
from sudachi_life.wake import CheckpointRequiredError


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checkpoint_files(paths: OrganismPaths) -> list[tuple[str, int, str]]:
    return [
        (
            str(path.relative_to(paths.checkpoints)),
            path.stat().st_size,
            _sha256(path),
        )
        for path in sorted(paths.checkpoints.rglob("*"))
        if path.is_file() and not path.is_symlink()
    ]


def _canonical_snapshot(paths: OrganismPaths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "database_sha256": _sha256(paths.database),
            "status": read_status(paths).as_dict(),
            "organism": tuple(
                connection.execute(
                    "SELECT * FROM organism WHERE singleton_id = 1"
                ).fetchone()
            ),
            "environment": tuple(
                connection.execute(
                    "SELECT * FROM environment_state WHERE singleton_id = 1"
                ).fetchone()
            ),
            "plots": [
                tuple(row)
                for row in connection.execute(
                    "SELECT plot_id, stage, moisture, fruit "
                    "FROM garden_plot ORDER BY plot_id"
                ).fetchall()
            ],
            "inventory": tuple(
                connection.execute(
                    "SELECT * FROM inventory WHERE singleton_id = 1"
                ).fetchone()
            ),
            "inbox": [
                tuple(row)
                for row in connection.execute(
                    "SELECT inbox_id, external_event_id, event_type, source, "
                    "source_wall_time_utc_us, received_wall_time_utc_us, "
                    "claimed_lifecycle_number, consumed "
                    "FROM inbox_event ORDER BY inbox_id"
                ).fetchall()
            ],
            "events": [
                tuple(row)
                for row in connection.execute(
                    "SELECT event_sequence, organism_id, lineage_generation, "
                    "lifecycle_number, wall_time_utc_us, event_type, source, "
                    "payload_json, schema_version, environment_version, "
                    "budget_config_version FROM event ORDER BY event_sequence"
                ).fetchall()
            ],
            "checkpoint_registry": [
                tuple(row)
                for row in connection.execute(
                    "SELECT checkpoint_id, lineage_generation, event_sequence, "
                    "manifest_sha256, database_sha256, database_size_bytes, "
                    "created_wall_time_utc_us, registered_wall_time_utc_us, protected "
                    "FROM checkpoint_registry ORDER BY event_sequence"
                ).fetchall()
            ],
            "sqlite_sequence": [
                tuple(row)
                for row in connection.execute(
                    "SELECT name, seq FROM sqlite_sequence ORDER BY name"
                ).fetchall()
            ],
            "checkpoint_files": _checkpoint_files(paths),
        }
    finally:
        connection.close()


def _wake_clock(base_wall: int, base_monotonic: int) -> FakeClock:
    return FakeClock(
        [
            ClockReading(base_wall, base_monotonic),
            ClockReading(base_wall, base_monotonic + 5_000_000),
            ClockReading(base_wall + 1, base_monotonic + 10_000_000),
            ClockReading(base_wall + 2, base_monotonic + 20_000_000),
            ClockReading(base_wall + 3, base_monotonic + 30_000_000),
        ]
    )


def test_second_wake_cannot_advance_while_prior_checkpoint_is_pending(
    initialized,
) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)

    first_enqueue = enqueue_garden_tick(
        paths,
        "pending-first-tick",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    second_enqueue = enqueue_garden_tick(
        paths,
        "pending-second-tick",
        clock=FakeClock([ClockReading(201, 3_000_000)]),
    )
    assert (first_enqueue.inbox_id, second_enqueue.inbox_id) == (1, 2)

    timeout_clock = FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 5_030_000_001),
        ]
    )
    with pytest.raises(CheckpointError, match="deadline"):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=51,
            clock=timeout_clock,
        )
    assert timeout_clock.read_count == 5

    pending = read_status(paths)
    assert (
        pending.lifecycle_number,
        pending.status,
        pending.checkpoint_pending,
        pending.environment_step,
        pending.water_units,
        pending.latest_stable_checkpoint_id,
        pending.latest_stable_event_sequence,
        pending.event_count,
    ) == (
        1,
        "checkpoint_pending",
        True,
        1,
        0,
        genesis.checkpoint_id,
        2,
        14,
    )

    connection = connect_database(paths.database, read_only=True)
    try:
        inbox = connection.execute(
            "SELECT inbox_id, external_event_id, claimed_lifecycle_number, consumed "
            "FROM inbox_event ORDER BY inbox_id"
        ).fetchall()
        assert [tuple(row) for row in inbox] == [
            (1, "pending-first-tick", 1, 1),
            (2, "pending-second-tick", None, 0),
        ]
        assert connection.execute(
            "SELECT event_type FROM event WHERE event_sequence = 14"
        ).fetchone()[0] == "checkpoint_pending"
        assert connection.execute(
            "SELECT COUNT(*) FROM checkpoint_registry"
        ).fetchone()[0] == 1
    finally:
        connection.close()

    pending_snapshot = _canonical_snapshot(paths)
    rejected_clock = FakeClock([])
    with pytest.raises(
        CheckpointRequiredError,
        match="committed checkpoint boundary that must be stabilized",
    ):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=52,
            clock=rejected_clock,
        )
    assert rejected_clock.read_count == 0
    assert _canonical_snapshot(paths) == pending_snapshot

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'wake_accepted'"
        ).fetchone()[0] == 1
        assert tuple(
            connection.execute(
                "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
                "WHERE external_event_id = 'pending-second-tick'"
            ).fetchone()
        ) == (None, 0)
    finally:
        connection.close()

    repair_clock = FakeClock([ClockReading(400, 6_000_000_000)])
    repair = repair_pending_checkpoint_registration(
        runtime_root,
        initial.organism_id,
        clock=repair_clock,
    )
    assert repair_clock.read_count == 1
    assert repair.event_sequence == 14
    assert repair.audit_event_sequence == 15
    assert repair.status == "sleeping"
    assert repair.previous_latest_stable_checkpoint_id == genesis.checkpoint_id

    repaired = read_status(paths)
    assert repaired.checkpoint_pending is False
    assert repaired.latest_stable_event_sequence == 14
    assert repaired.event_count == 15

    second_clock = _wake_clock(500, 10_000_000_000)
    second = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=53,
        clock=second_clock,
    )
    final = read_status(paths)

    assert second_clock.read_count == 5
    assert second.external_event_id == "pending-second-tick"
    assert second.decision.as_dict() == {
        "decision_type": "action",
        "action_id": "harvest_plot",
        "action_version": 1,
        "parameters": {"plot_id": "bed-b"},
        "reason": "fixed_policy_first_executable_harvest",
    }
    assert second.evaluation.success is True
    assert second.checkpoint.event_sequence == 24
    assert (
        final.lifecycle_number,
        final.status,
        final.checkpoint_pending,
        final.environment_step,
        final.harvested_fruit,
        final.objective_complete,
        final.latest_stable_event_sequence,
        final.event_count,
    ) == (2, "sleeping", False, 2, 1, True, 24, 25)

    connection = connect_database(paths.database, read_only=True)
    try:
        assert [
            tuple(row)
            for row in connection.execute(
                "SELECT inbox_id, external_event_id, claimed_lifecycle_number, consumed "
                "FROM inbox_event ORDER BY inbox_id"
            ).fetchall()
        ] == [
            (1, "pending-first-tick", 1, 1),
            (2, "pending-second-tick", 2, 1),
        ]
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'action_completed'"
        ).fetchone()[0] == 2
    finally:
        connection.close()
