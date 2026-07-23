from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake, perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status
from sudachi_life.wake import NoInputEventError


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
        if path.is_file()
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


def test_consumed_external_event_replay_never_creates_duplicate_action(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)

    first_enqueue = enqueue_garden_tick(
        paths,
        "consumed-replay-tick",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    first_clock = _wake_clock(300, 10_000_000)
    first = perform_first_water_wake(
        runtime_root,
        initial.organism_id,
        seed=11,
        clock=first_clock,
    )
    assert first_clock.read_count == 5
    assert first.decision.as_dict()["parameters"] == {"plot_id": "bed-a"}
    assert read_status(paths).status == "sleeping"

    before_replay = _canonical_snapshot(paths)
    replay_clock = FakeClock([])
    replay = enqueue_garden_tick(
        paths,
        "consumed-replay-tick",
        clock=replay_clock,
    )

    assert replay_clock.read_count == 0
    assert replay.inserted is False
    assert replay.inbox_id == first_enqueue.inbox_id == 1
    assert replay.received_wall_time_utc_us == first_enqueue.received_wall_time_utc_us
    assert _canonical_snapshot(paths) == before_replay

    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
            "WHERE external_event_id = 'consumed-replay-tick'"
        ).fetchone()
        assert tuple(row) == (1, 1)
        assert connection.execute(
            "SELECT COUNT(*) FROM inbox_event"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'input_enqueued'"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'action_completed'"
        ).fetchone()[0] == 1
    finally:
        connection.close()

    no_input_clock = FakeClock([ClockReading(400, 40_000_000)])
    with pytest.raises(
        NoInputEventError,
        match="no unclaimed synthetic:garden_tick is available",
    ):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=12,
            clock=no_input_clock,
        )
    assert no_input_clock.read_count == 1
    assert _canonical_snapshot(paths) == before_replay

    second_enqueue = enqueue_garden_tick(
        paths,
        "distinct-followup-tick",
        clock=FakeClock([ClockReading(500, 50_000_000)]),
    )
    assert second_enqueue.inserted is True
    assert second_enqueue.inbox_id == 2

    second_clock = _wake_clock(600, 60_000_000)
    second = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=13,
        clock=second_clock,
    )
    status = read_status(paths)

    assert second_clock.read_count == 5
    assert second.external_event_id == "distinct-followup-tick"
    assert second.decision.as_dict()["action_id"] == "harvest_plot"
    assert second.decision.as_dict()["parameters"] == {"plot_id": "bed-b"}
    assert second.evaluation.success is True
    assert (
        status.lifecycle_number,
        status.status,
        status.environment_step,
        status.harvested_fruit,
        status.objective_complete,
        status.event_count,
    ) == (2, "sleeping", 2, 1, True, 25)

    connection = connect_database(paths.database, read_only=True)
    try:
        action_events = connection.execute(
            "SELECT event_sequence, payload_json FROM event "
            "WHERE event_type = 'action_completed' ORDER BY event_sequence"
        ).fetchall()
        assert len(action_events) == 2
        assert [
            json.loads(row["payload_json"])["parameters"]["plot_id"]
            for row in action_events
        ] == ["bed-a", "bed-b"]
        replay_rows = connection.execute(
            "SELECT inbox_id, external_event_id, claimed_lifecycle_number, consumed "
            "FROM inbox_event ORDER BY inbox_id"
        ).fetchall()
        assert [tuple(row) for row in replay_rows] == [
            (1, "consumed-replay-tick", 1, 1),
            (2, "distinct-followup-tick", 2, 1),
        ]
    finally:
        connection.close()
