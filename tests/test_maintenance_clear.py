from __future__ import annotations

import json
import sqlite3

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
from sudachi_life.maintenance_recovery import (
    InvalidMaintenanceRecoveryReasonError,
    MaintenanceClearBusyError,
    MaintenanceClearRejectedError,
    clear_maintenance,
)
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status, validate_canonical_state


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
        "maintenance-clear-queued-tick-1",
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
                "fixture_id": "maintenance-clear-stable-v1",
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
                "fixture_id": "maintenance-clear-stable-v1",
                "final_status": "maintenance_required",
                "maintenance_reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            },
        )
        connection.execute(
            """
            UPDATE organism
            SET status = 'checkpoint_pending', checkpoint_pending = 1,
                pending_checkpoint_generation = lineage_generation,
                pending_checkpoint_event_sequence = ?, consecutive_failures = ?,
                maintenance_reason = ?
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
            [ClockReading(300, 2_000_000), ClockReading(301, 3_000_000)]
        ),
    )
    assert checkpoint.event_sequence == 6
    return checkpoint


def _canonical_snapshot(paths: OrganismPaths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "environment": tuple(
                connection.execute(
                    "SELECT environment_step, objective_complete FROM environment_state"
                ).fetchone()
            ),
            "plots": [
                tuple(row)
                for row in connection.execute(
                    "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id"
                ).fetchall()
            ],
            "inventory": tuple(
                connection.execute(
                    "SELECT water_units, harvested_fruit FROM inventory"
                ).fetchone()
            ),
            "checkpoint_registry": [
                tuple(row)
                for row in connection.execute(
                    "SELECT checkpoint_id, lineage_generation, event_sequence, protected "
                    "FROM checkpoint_registry ORDER BY event_sequence"
                ).fetchall()
            ],
            "inbox": [
                tuple(row)
                for row in connection.execute(
                    "SELECT inbox_id, external_event_id, claimed_lifecycle_number, consumed "
                    "FROM inbox_event ORDER BY inbox_id"
                ).fetchall()
            ],
        }
    finally:
        connection.close()


def _wake_clock() -> FakeClock:
    return FakeClock(
        [
            ClockReading(500, 10_000_000),
            ClockReading(500, 15_000_000),
            ClockReading(501, 20_000_000),
            ClockReading(502, 30_000_000),
            ClockReading(503, 40_000_000),
        ]
    )


def test_explicit_maintenance_clear_preserves_state_and_allows_queued_wake(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    checkpoint = _prepare_stable_maintenance_fixture(paths)
    before = _canonical_snapshot(paths)

    clear_clock = FakeClock([ClockReading(400, 4_000_000)])
    result = clear_maintenance(
        runtime_root,
        initial.organism_id,
        "operator_verified_stable_state",
        clock=clear_clock,
    )
    assert clear_clock.read_count == 1
    assert result.as_dict() == {
        "organism_id": initial.organism_id,
        "previous_status": "maintenance_required",
        "status": "sleeping",
        "previous_maintenance_reason": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
        "recovery_reason": "operator_verified_stable_state",
        "consecutive_failures_before": 3,
        "consecutive_failures_after": 0,
        "latest_stable_checkpoint_id": checkpoint.checkpoint_id,
        "latest_stable_event_sequence": 6,
        "queued_input_events_preserved": 1,
        "audit_event_sequence": 9,
    }

    status = read_status(paths)
    assert status.status == "sleeping"
    assert status.consecutive_failures == 0
    assert status.maintenance_reason is None
    assert status.latest_stable_checkpoint_id == checkpoint.checkpoint_id
    assert status.latest_stable_event_sequence == 6
    assert status.event_count == 9
    assert _canonical_snapshot(paths) == before

    connection = connect_database(paths.database, read_only=True)
    try:
        audit = connection.execute(
            "SELECT event_type, source, payload_json FROM event WHERE event_sequence = 9"
        ).fetchone()
        assert tuple(audit[:2]) == (
            "maintenance_cleared",
            "administration:maintenance-clear",
        )
        assert json.loads(audit["payload_json"]) == {
            "checkpoint_event_sequence": 6,
            "checkpoint_id": checkpoint.checkpoint_id,
            "consecutive_failures_after": 0,
            "consecutive_failures_before": 3,
            "maintenance_reason_before": MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,
            "recovery_reason": "operator_verified_stable_state",
            "status_after": "sleeping",
            "status_before": "maintenance_required",
        }
    finally:
        connection.close()

    wake = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=43,
        clock=_wake_clock(),
    )
    assert wake.decision.as_dict() == {
        "decision_type": "abstention",
        "reason": "no_applicable_action",
    }
    assert wake.checkpoint.event_sequence == 18
    final = read_status(paths)
    assert final.status == "sleeping"
    assert final.lifecycle_number == 1
    assert final.consecutive_failures == 1
    assert final.latest_stable_event_sequence == 18
    assert final.event_count == 19

    connection = connect_database(paths.database, read_only=True)
    try:
        queued = connection.execute(
            "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
            "WHERE external_event_id = 'maintenance-clear-queued-tick-1'"
        ).fetchone()
        assert tuple(queued) == (1, 1)
    finally:
        connection.close()


def test_maintenance_clear_cli_records_reason_and_rejects_repeat(
    initialized,
    capsys,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_stable_maintenance_fixture(paths)

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "maintenance",
            "clear",
            initial.organism_id,
            "--reason",
            "operator_verified_stable_state",
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "sleeping"
    assert payload["recovery_reason"] == "operator_verified_stable_state"
    assert payload["audit_event_sequence"] == 9

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "maintenance",
            "clear",
            initial.organism_id,
            "--reason",
            "repeat_clear",
            "--json",
        ]
    ) == 1
    assert "status=sleeping" in capsys.readouterr().err


def test_maintenance_clear_rejects_invalid_reason_and_busy_without_clock_read(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_stable_maintenance_fixture(paths)
    before = read_status(paths)

    invalid_clock = FakeClock([])
    with pytest.raises(InvalidMaintenanceRecoveryReasonError):
        clear_maintenance(
            runtime_root,
            initial.organism_id,
            "contains spaces",
            clock=invalid_clock,
        )
    assert invalid_clock.read_count == 0
    assert read_status(paths) == before

    owner = connect_database(paths.database)
    try:
        owner.execute("BEGIN IMMEDIATE")
        busy_clock = FakeClock([])
        with pytest.raises(
            MaintenanceClearBusyError,
            match="maintenance clear is busy; this attempt was not queued",
        ):
            clear_maintenance(
                runtime_root,
                initial.organism_id,
                "operator_verified_stable_state",
                clock=busy_clock,
            )
        assert busy_clock.read_count == 0
    finally:
        owner.rollback()
        owner.close()
    assert read_status(paths) == before


def test_maintenance_clear_rolls_back_when_audit_event_fails(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_stable_maintenance_fixture(paths)
    before = read_status(paths)

    connection = connect_database(paths.database)
    try:
        connection.execute(
            """CREATE TRIGGER reject_maintenance_clear_event
               BEFORE INSERT ON event
               WHEN NEW.event_type = 'maintenance_cleared'
               BEGIN
                   SELECT RAISE(ABORT, 'injected audit failure');
               END"""
        )
    finally:
        connection.close()

    with pytest.raises(sqlite3.IntegrityError, match="injected audit failure"):
        clear_maintenance(
            runtime_root,
            initial.organism_id,
            "operator_verified_stable_state",
            clock=FakeClock([ClockReading(400, 4_000_000)]),
        )

    assert read_status(paths) == before
    connection = connect_database(paths.database)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE event_type = 'maintenance_cleared'"
        ).fetchone()[0] == 0
        connection.execute("DROP TRIGGER reject_maintenance_clear_event")
    finally:
        connection.close()


def test_maintenance_clear_rejects_sleeping_state_without_clock_read(initialized) -> None:
    runtime_root, initial, _ = initialized
    clock = FakeClock([])
    with pytest.raises(
        MaintenanceClearRejectedError,
        match="organism is not eligible for maintenance clear: status=sleeping",
    ):
        clear_maintenance(
            runtime_root,
            initial.organism_id,
            "operator_verified_stable_state",
            clock=clock,
        )
    assert clock.read_count == 0
