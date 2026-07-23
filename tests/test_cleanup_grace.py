from __future__ import annotations

import json

import pytest

from sudachi_life.budgets import BudgetExhaustedError
from sudachi_life.checkpoints import create_and_register_lifecycle_checkpoint
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
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


def _prepare_single_water_action_fixture(paths: OrganismPaths) -> None:
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
            "UPDATE inventory SET water_units = 1, harvested_fruit = 0 "
            "WHERE singleton_id = 1"
        )
        connection.execute(
            "UPDATE environment_state SET environment_step = 0, objective_complete = 0 "
            "WHERE singleton_id = 1"
        )
        _append_administrative_event(
            connection,
            wall_time_utc_us=100,
            event_type="protected_test_fixture_prepared",
            payload={"fixture_id": "cleanup-grace-single-water-v1"},
        )
        boundary = _append_administrative_event(
            connection,
            wall_time_utc_us=100,
            event_type="checkpoint_pending",
            payload={
                "reason": "protected_test_fixture",
                "fixture_id": "cleanup-grace-single-water-v1",
            },
        )
        connection.execute(
            """
            UPDATE organism
            SET status = 'checkpoint_pending', checkpoint_pending = 1,
                pending_checkpoint_generation = lineage_generation,
                pending_checkpoint_event_sequence = ?, consecutive_failures = 0,
                maintenance_reason = NULL
            WHERE singleton_id = 1
            """,
            (boundary,),
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
                ClockReading(101, 1_000_000),
                ClockReading(102, 2_000_000),
            ]
        ),
    )
    assert checkpoint.event_sequence == 5


def _canonical_snapshot(paths: OrganismPaths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "status": read_status(paths).as_dict(),
            "events": [
                tuple(row)
                for row in connection.execute(
                    "SELECT event_sequence, organism_id, lineage_generation, "
                    "lifecycle_number, wall_time_utc_us, event_type, source, payload_json, "
                    "schema_version, environment_version, budget_config_version "
                    "FROM event ORDER BY event_sequence"
                ).fetchall()
            ],
            "inbox": [
                tuple(row)
                for row in connection.execute(
                    "SELECT inbox_id, external_event_id, event_type, source, "
                    "source_wall_time_utc_us, received_wall_time_utc_us, "
                    "claimed_lifecycle_number, consumed "
                    "FROM inbox_event ORDER BY inbox_id"
                ).fetchall()
            ],
            "plots": [
                tuple(row)
                for row in connection.execute(
                    "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id"
                ).fetchall()
            ],
            "inventory": tuple(
                connection.execute(
                    "SELECT singleton_id, water_units, harvested_fruit "
                    "FROM inventory WHERE singleton_id = 1"
                ).fetchone()
            ),
            "environment": tuple(
                connection.execute(
                    "SELECT singleton_id, environment_version, environment_step, "
                    "objective_complete FROM environment_state WHERE singleton_id = 1"
                ).fetchone()
            ),
            "sqlite_sequence": [
                tuple(row)
                for row in connection.execute(
                    "SELECT name, seq FROM sqlite_sequence ORDER BY name"
                ).fetchall()
            ],
        }
    finally:
        connection.close()


def test_cleanup_grace_allows_terminalization_at_exact_upper_boundary(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_single_water_action_fixture(paths)
    enqueue_garden_tick(
        paths,
        "cleanup-grace-exact-boundary-tick",
        clock=FakeClock([ClockReading(200, 5_000_000)]),
    )
    clock = FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(301, 2_011_000_000),
            ClockReading(302, 2_260_000_000),
            ClockReading(303, 2_270_000_000),
            ClockReading(304, 2_280_000_000),
        ]
    )

    result = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=41,
        clock=clock,
    )

    assert clock.read_count == 5
    assert result.budget_exhaustion is not None
    assert result.budget_exhaustion.observed_elapsed_monotonic_ns == 2_001_000_000
    assert result.budget_ledger["elapsed_monotonic_ns"] == 2_250_000_000
    assert result.budget_ledger["consumed"]["action_attempts"] == 0
    assert result.budget_ledger["consumed"]["environment_mutations"] == 0
    assert result.budget_ledger["consumed"]["caregiver_consultations"] == 0

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE lifecycle_number = 1 "
            "AND event_type IN ('action_proposed', 'action_completed', 'action_failed')"
        ).fetchone()[0] == 0
    finally:
        connection.close()


def test_cleanup_grace_overrun_rolls_back_uncommitted_terminalization(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_single_water_action_fixture(paths)
    enqueue_garden_tick(
        paths,
        "cleanup-grace-overrun-tick",
        clock=FakeClock([ClockReading(200, 5_000_000)]),
    )
    before = _canonical_snapshot(paths)
    clock = FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(301, 2_011_000_000),
            ClockReading(302, 2_260_000_001),
        ]
    )

    with pytest.raises(
        BudgetExhaustedError,
        match="protected cleanup grace exhausted before lifecycle terminalization",
    ):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=42,
            clock=clock,
        )

    assert clock.read_count == 3
    assert _canonical_snapshot(paths) == before

    connection = connect_database(paths.database, read_only=True)
    try:
        inbox = connection.execute(
            "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
            "WHERE external_event_id = 'cleanup-grace-overrun-tick'"
        ).fetchone()
        assert tuple(inbox) == (None, 0)
        assert connection.execute(
            "SELECT COUNT(*) FROM event WHERE lifecycle_number = 1"
        ).fetchone()[0] == 0
    finally:
        connection.close()
