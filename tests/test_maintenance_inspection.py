from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sudachi_life.checkpoints import create_and_register_lifecycle_checkpoint
from sudachi_life.cli import main
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import (
    CONSECUTIVE_FAILURE_LIMIT,
    MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
)
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.maintenance import (
    MaintenanceInspectionRejectedError,
    inspect_maintenance,
)
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status, validate_canonical_state
from sudachi_life.wake import WakeRejectedError


def _append_administrative_event(
    connection,
    *,
    wall_time_utc_us: int,
    event_type: str,
    payload: dict[str, object],
) -> int:
    organism = connection.execute(
        "SELECT organism_id, lineage_generation, lifecycle_number, schema_version, "
        "environment_version, budget_config_version "
        "FROM organism WHERE singleton_id = 1"
    ).fetchone()
    cursor = connection.execute(
        """
        INSERT INTO event (
            organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
            event_type, source, payload_json, schema_version,
            environment_version, budget_config_version
        ) VALUES (?, ?, ?, ?, ?, 'administration:protected-test-fixture', ?, ?, ?, ?)
        """,
        (
            organism["organism_id"],
            organism["lineage_generation"],
            organism["lifecycle_number"],
            wall_time_utc_us,
            event_type,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
            organism["schema_version"],
            organism["environment_version"],
            organism["budget_config_version"],
        ),
    )
    return int(cursor.lastrowid)


def _prepare_stable_maintenance_fixture(paths: OrganismPaths):
    enqueue_garden_tick(
        paths,
        "maintenance-inspection-queued-tick-1",
        clock=FakeClock([ClockReading(100, 1_000_000)]),
    )

    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE garden_plot SET moisture = 0, fruit = 0 WHERE plot_id = 'bed-a'"
        )
        connection.execute(
            "UPDATE garden_plot SET moisture = 1, fruit = 0 WHERE plot_id = 'bed-b'"
        )
        connection.execute(
            "UPDATE inventory SET water_units = 0, harvested_fruit = 0 "
            "WHERE singleton_id = 1"
        )
        connection.execute(
            "UPDATE environment_state SET environment_step = 0, objective_complete = 0 "
            "WHERE singleton_id = 1"
        )
        _append_administrative_event(
            connection,
            wall_time_utc_us=200,
            event_type="protected_test_fixture_prepared",
            payload={
                "fixture_id": "maintenance-inspection-stable-v1",
                "consecutive_failures": CONSECUTIVE_FAILURE_LIMIT,
                "maintenance_reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
                "queued_input_count": 1,
            },
        )
        boundary = _append_administrative_event(
            connection,
            wall_time_utc_us=200,
            event_type="checkpoint_pending",
            payload={
                "reason": "protected_test_fixture",
                "fixture_id": "maintenance-inspection-stable-v1",
                "final_status": "maintenance_required",
                "maintenance_reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            },
        )
        connection.execute(
            """
            UPDATE organism
            SET status = 'checkpoint_pending', checkpoint_pending = 1,
                pending_checkpoint_generation = lineage_generation,
                pending_checkpoint_event_sequence = ?,
                consecutive_failures = ?, maintenance_reason = ?
            WHERE singleton_id = 1
            """,
            (
                boundary,
                CONSECUTIVE_FAILURE_LIMIT,
                MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            ),
        )
        validate_canonical_state(connection, expect_checkpoint_pending=True)
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()

    checkpoint = create_and_register_lifecycle_checkpoint(
        paths,
        clock=FakeClock(
            [
                ClockReading(300, 2_000_000),
                ClockReading(301, 3_000_000),
            ]
        ),
    )
    assert checkpoint.event_sequence == 6
    return checkpoint


def _file_snapshot(root: Path) -> dict[str, tuple[int, int, str]]:
    snapshot: dict[str, tuple[int, int, str]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        stat = path.stat()
        snapshot[str(path.relative_to(root))] = (
            stat.st_size,
            stat.st_mtime_ns,
            hashlib.sha256(data).hexdigest(),
        )
    return snapshot


def test_read_only_maintenance_inspection_reports_without_mutation(
    initialized,
    capsys,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    checkpoint = _prepare_stable_maintenance_fixture(paths)

    before_status = read_status(paths)
    before_files = _file_snapshot(paths.organism_dir)
    connection = connect_database(paths.database, read_only=True)
    try:
        before_events = connection.execute("SELECT COUNT(*) FROM event").fetchone()[0]
        before_inbox = [
            tuple(row)
            for row in connection.execute(
                "SELECT inbox_id, external_event_id, claimed_lifecycle_number, consumed "
                "FROM inbox_event ORDER BY inbox_id"
            ).fetchall()
        ]
        before_registry = [
            tuple(row)
            for row in connection.execute(
                "SELECT checkpoint_id, lineage_generation, event_sequence, protected "
                "FROM checkpoint_registry ORDER BY event_sequence"
            ).fetchall()
        ]
    finally:
        connection.close()

    inspection = inspect_maintenance(runtime_root, initial.organism_id)
    assert inspection.as_dict() == {
        "organism_id": initial.organism_id,
        "lineage_generation": 0,
        "lifecycle_number": 0,
        "status": "maintenance_required",
        "maintenance_reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
        "consecutive_failures": CONSECUTIVE_FAILURE_LIMIT,
        "checkpoint_pending": False,
        "latest_stable_checkpoint": {
            "checkpoint_id": checkpoint.checkpoint_id,
            "lineage_generation": 0,
            "event_sequence": 6,
            "protected": True,
        },
        "input_state": {
            "total": 1,
            "consumed": 0,
            "queued_unclaimed": 1,
            "claimed_unconsumed": 0,
            "pending": [
                {
                    "inbox_id": 1,
                    "external_event_id": "maintenance-inspection-queued-tick-1",
                    "event_type": "synthetic:garden_tick",
                    "source": "administration:cli",
                    "claimed_lifecycle_number": None,
                    "consumed": False,
                }
            ],
        },
    }

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "maintenance",
            "inspect",
            initial.organism_id,
            "--json",
        ]
    ) == 0
    assert json.loads(capsys.readouterr().out) == {
        "authority_category": "administration",
        "authority_source": "administration:maintenance-inspect",
        **inspection.as_dict(),
    }

    after_status = read_status(paths)
    after_files = _file_snapshot(paths.organism_dir)
    assert after_status == before_status
    assert after_files == before_files

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute("SELECT COUNT(*) FROM event").fetchone()[0] == before_events
        assert [
            tuple(row)
            for row in connection.execute(
                "SELECT inbox_id, external_event_id, claimed_lifecycle_number, consumed "
                "FROM inbox_event ORDER BY inbox_id"
            ).fetchall()
        ] == before_inbox
        assert [
            tuple(row)
            for row in connection.execute(
                "SELECT checkpoint_id, lineage_generation, event_sequence, protected "
                "FROM checkpoint_registry ORDER BY event_sequence"
            ).fetchall()
        ] == before_registry
    finally:
        connection.close()

    rejected_clock = FakeClock([])
    with pytest.raises(
        WakeRejectedError,
        match="organism is not wakeable: status=maintenance_required",
    ):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=41,
            clock=rejected_clock,
        )
    assert rejected_clock.read_count == 0
    assert read_status(paths) == before_status
    assert _file_snapshot(paths.organism_dir) == before_files


def test_maintenance_inspection_rejects_nonmaintenance_state(initialized, capsys) -> None:
    runtime_root, initial, _ = initialized

    with pytest.raises(
        MaintenanceInspectionRejectedError,
        match="organism is not in maintenance_required: status=sleeping",
    ):
        inspect_maintenance(runtime_root, initial.organism_id)

    result = main(
        [
            "--runtime-dir",
            str(runtime_root),
            "maintenance",
            "inspect",
            initial.organism_id,
            "--json",
        ]
    )
    captured = capsys.readouterr()
    assert result == 1
    assert "organism is not in maintenance_required: status=sleeping" in captured.err
