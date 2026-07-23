from __future__ import annotations

import hashlib
import json
import multiprocessing
from multiprocessing.connection import Connection
import os
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status, validate_canonical_state
from sudachi_life.wake import WakeTransaction


_CRASH_EXIT_CODE = 73


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


def _crash_with_uncommitted_wake(
    runtime_root: str,
    organism_id: str,
    signal: Connection,
) -> None:
    paths = OrganismPaths.build(Path(runtime_root), organism_id)
    wake = WakeTransaction.acquire(paths)
    claimed = wake.claim_oldest_garden_tick()
    connection = wake.connection
    organism = connection.execute(
        "SELECT organism_id, lineage_generation, schema_version, "
        "environment_version, budget_config_version "
        "FROM organism WHERE singleton_id = 1"
    ).fetchone()
    cursor = connection.execute(
        """
        INSERT INTO event (
            organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
            event_type, source, payload_json, schema_version,
            environment_version, budget_config_version
        ) VALUES (?, ?, ?, 999, 'protected_test_uncommitted_process_crash',
                  'administration:protected-test-harness', ?, ?, ?, ?)
        """,
        (
            organism["organism_id"],
            organism["lineage_generation"],
            wake.lifecycle_number,
            json.dumps(
                {
                    "external_event_id": claimed.external_event_id,
                    "inbox_id": claimed.inbox_id,
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
            organism["schema_version"],
            organism["environment_version"],
            organism["budget_config_version"],
        ),
    )
    event_sequence = int(cursor.lastrowid)
    connection.execute(
        "UPDATE garden_plot SET moisture = 1 WHERE plot_id = 'bed-a'"
    )
    connection.execute(
        "UPDATE inventory SET water_units = 0 WHERE singleton_id = 1"
    )
    connection.execute(
        "UPDATE environment_state SET environment_step = 1 WHERE singleton_id = 1"
    )
    connection.execute(
        """
        UPDATE organism
        SET lifecycle_number = ?, status = 'checkpoint_pending',
            checkpoint_pending = 1,
            pending_checkpoint_generation = lineage_generation,
            pending_checkpoint_event_sequence = ?, last_wake_wall_time_utc_us = 999
        WHERE singleton_id = 1
        """,
        (wake.lifecycle_number, event_sequence),
    )

    proof = {
        "claimed": tuple(
            connection.execute(
                "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
                "WHERE inbox_id = ?",
                (claimed.inbox_id,),
            ).fetchone()
        ),
        "event_count": int(
            connection.execute("SELECT COUNT(*) FROM event").fetchone()[0]
        ),
        "event_sequence": event_sequence,
        "organism": tuple(
            connection.execute(
                "SELECT lifecycle_number, status, checkpoint_pending "
                "FROM organism WHERE singleton_id = 1"
            ).fetchone()
        ),
        "bed_a_moisture": int(
            connection.execute(
                "SELECT moisture FROM garden_plot WHERE plot_id = 'bed-a'"
            ).fetchone()[0]
        ),
        "water_units": int(
            connection.execute(
                "SELECT water_units FROM inventory WHERE singleton_id = 1"
            ).fetchone()[0]
        ),
        "environment_step": int(
            connection.execute(
                "SELECT environment_step FROM environment_state WHERE singleton_id = 1"
            ).fetchone()[0]
        ),
    }
    signal.send(proof)
    os._exit(_CRASH_EXIT_CODE)


def test_process_exit_rolls_back_uncommitted_wake_and_releases_lock(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(
        paths,
        "process-crash-tick",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    before = _canonical_snapshot(paths)

    context = multiprocessing.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(
        target=_crash_with_uncommitted_wake,
        args=(str(runtime_root), initial.organism_id, sender),
    )
    process.start()
    sender.close()
    try:
        assert receiver.poll(10), "child did not reach the uncommitted crash boundary"
        proof = receiver.recv()
    finally:
        receiver.close()

    process.join(10)
    if process.is_alive():
        process.terminate()
        process.join(5)
        pytest.fail("child process did not exit within the protected timeout")
    assert process.exitcode == _CRASH_EXIT_CODE
    assert proof == {
        "claimed": (1, 0),
        "event_count": 5,
        "event_sequence": 5,
        "organism": (1, "checkpoint_pending", 1),
        "bed_a_moisture": 1,
        "water_units": 0,
        "environment_step": 1,
    }

    recovery = connect_database(paths.database)
    try:
        recovery.execute("BEGIN IMMEDIATE")
        validate_canonical_state(recovery, expect_checkpoint_pending=False)
        assert tuple(
            recovery.execute(
                "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
                "WHERE external_event_id = 'process-crash-tick'"
            ).fetchone()
        ) == (None, 0)
        recovery.rollback()
    finally:
        recovery.close()

    assert _canonical_snapshot(paths) == before

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
        seed=31,
        clock=clock,
    )
    status = read_status(paths)

    assert clock.read_count == 5
    assert result.external_event_id == "process-crash-tick"
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
            "SELECT COUNT(*) FROM event "
            "WHERE event_type = 'protected_test_uncommitted_process_crash'"
        ).fetchone()[0] == 0
        assert tuple(
            connection.execute(
                "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
                "WHERE external_event_id = 'process-crash-tick'"
            ).fetchone()
        ) == (1, 1)
    finally:
        connection.close()
