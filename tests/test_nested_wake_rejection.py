from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status
from sudachi_life.wake import WakeBusyError, WakeTransaction


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


def test_nested_wake_and_hidden_writer_fail_without_queued_work(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(
        paths,
        "nested-wake-tick",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    before = _canonical_snapshot(paths)
    forbidden_clock = FakeClock([])

    outer = WakeTransaction.acquire(paths)
    hidden = None
    try:
        assert outer.lifecycle_number == 1
        assert outer.connection.in_transaction is True

        with pytest.raises(
            WakeBusyError,
            match="organism wake is busy; this attempt was not queued",
        ):
            WakeTransaction.acquire(paths)

        hidden = connect_database(paths.database)
        with pytest.raises(sqlite3.OperationalError) as exc_info:
            hidden.execute("BEGIN IMMEDIATE")
        error = exc_info.value
        assert getattr(error, "sqlite_errorcode", None) in {
            sqlite3.SQLITE_BUSY,
            sqlite3.SQLITE_LOCKED,
        } or "locked" in str(error).lower()
        assert hidden.in_transaction is False

        assert forbidden_clock.read_count == 0
        assert forbidden_clock.remaining_reads == 0
    finally:
        if hidden is not None:
            if hidden.in_transaction:
                hidden.rollback()
            hidden.close()
        outer.rollback_and_close()

    assert _canonical_snapshot(paths) == before

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute("SELECT COUNT(*) FROM inbox_event").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM event").fetchone()[0] == 4
        assert tuple(
            connection.execute(
                "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
                "WHERE external_event_id = 'nested-wake-tick'"
            ).fetchone()
        ) == (None, 0)
    finally:
        connection.close()

    clock = FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 40_000_000),
        ]
    )
    result = perform_first_water_wake(
        runtime_root,
        initial.organism_id,
        seed=41,
        clock=clock,
    )
    status = read_status(paths)

    assert clock.read_count == 5
    assert result.external_event_id == "nested-wake-tick"
    assert result.decision.as_dict()["parameters"] == {"plot_id": "bed-a"}
    assert result.evaluation.success is True
    assert (
        status.lifecycle_number,
        status.status,
        status.environment_step,
        status.water_units,
        status.event_count,
    ) == (1, "sleeping", 1, 0, 14)

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'wake_accepted'"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'action_completed'"
        ).fetchone()[0] == 1
        assert tuple(
            connection.execute(
                "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
                "WHERE external_event_id = 'nested-wake-tick'"
            ).fetchone()
        ) == (1, 1)
    finally:
        connection.close()
