from __future__ import annotations

import json

from sudachi_life.checkpoints import (
    create_and_register_lifecycle_checkpoint,
    validate_checkpoint_directory,
)
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status, validate_canonical_state


def _append_fixture_event(
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


def _prepare_reverse_inserted_water_tie(paths: OrganismPaths) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("DELETE FROM garden_plot")
        connection.executemany(
            "INSERT INTO garden_plot (plot_id, stage, moisture, fruit) "
            "VALUES (?, ?, ?, ?)",
            [
                ("bed-b", "mature", 0, 0),
                ("bed-a", "sprout", 0, 0),
            ],
        )
        connection.execute(
            "UPDATE inventory SET water_units = 1, harvested_fruit = 0 "
            "WHERE singleton_id = 1"
        )
        connection.execute(
            "UPDATE environment_state SET environment_step = 0, objective_complete = 0 "
            "WHERE singleton_id = 1"
        )
        _append_fixture_event(
            connection,
            wall_time_utc_us=100,
            event_type="protected_test_fixture_prepared",
            payload={
                "fixture_id": "reverse-inserted-water-tie-v1",
                "physical_plot_order": ["bed-b", "bed-a"],
                "executable_water_targets": ["bed-a", "bed-b"],
            },
        )
        boundary = _append_fixture_event(
            connection,
            wall_time_utc_us=100,
            event_type="checkpoint_pending",
            payload={
                "reason": "protected_test_fixture",
                "fixture_id": "reverse-inserted-water-tie-v1",
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


def _plot_order(paths: OrganismPaths, order_by: str) -> list[str]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return [
            str(row[0])
            for row in connection.execute(
                f"SELECT plot_id FROM garden_plot ORDER BY {order_by}"
            ).fetchall()
        ]
    finally:
        connection.close()


def test_complete_wake_uses_lexicographic_tie_break_after_reverse_insertion(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_reverse_inserted_water_tie(paths)

    assert _plot_order(paths, "rowid") == ["bed-b", "bed-a"]
    assert _plot_order(paths, "plot_id") == ["bed-a", "bed-b"]

    enqueue_garden_tick(
        paths,
        "reverse-insertion-tie-tick",
        clock=FakeClock([ClockReading(200, 5_000_000)]),
    )
    clock = FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 40_000_000),
        ]
    )

    result = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=97,
        clock=clock,
    )
    status = read_status(paths)

    assert clock.read_count == 5
    assert result.decision.as_dict() == {
        "decision_type": "action",
        "action_id": "water_plot",
        "action_version": 1,
        "parameters": {"plot_id": "bed-a"},
        "reason": "fixed_policy_first_executable_dry_plot",
    }
    assert result.evaluation.success is True
    assert result.evaluation.progress == "positive"
    assert result.budget_ledger["consumed"] == {
        "input_events": 1,
        "observations": 1,
        "action_attempts": 1,
        "environment_mutations": 1,
        "caregiver_consultations": 0,
        "network_calls": 0,
        "subprocess_calls": 0,
        "external_mutable_writes": 0,
    }
    assert (
        status.lifecycle_number,
        status.status,
        status.environment_step,
        status.water_units,
        status.event_count,
    ) == (1, "sleeping", 1, 0, 17)
    assert status.latest_stable_event_sequence == result.checkpoint.event_sequence == 16
    assert [plot["plot_id"] for plot in status.plots] == ["bed-a", "bed-b"]
    assert [plot["moisture"] for plot in status.plots] == [1, 0]
    assert _plot_order(paths, "rowid") == ["bed-b", "bed-a"]

    connection = connect_database(paths.database, read_only=True)
    try:
        lifecycle_events = connection.execute(
            "SELECT event_sequence, event_type, payload_json FROM event "
            "WHERE event_sequence BETWEEN 8 AND 17 ORDER BY event_sequence"
        ).fetchall()
        assert [str(row["event_type"]) for row in lifecycle_events] == [
            "wake_accepted",
            "input_claimed",
            "observation_created",
            "action_proposed",
            "action_completed",
            "evaluation_completed",
            "lifecycle_completed",
            "budget_ledger",
            "checkpoint_pending",
            "checkpoint_stabilized",
        ]
        observation = json.loads(lifecycle_events[2]["payload_json"])
        assert [plot["plot_id"] for plot in observation["plots"]] == [
            "bed-a",
            "bed-b",
        ]
        water = next(
            action
            for action in observation["actions"]
            if action["action_id"] == "water_plot"
        )
        assert water["applicable_targets"] == ["bed-a", "bed-b"]
        proposed = json.loads(lifecycle_events[3]["payload_json"])
        assert proposed["parameters"] == {"plot_id": "bed-a"}
        assert json.loads(lifecycle_events[0]["payload_json"]) == {"seed": 97}
    finally:
        connection.close()

    manifest = validate_checkpoint_directory(result.checkpoint.checkpoint_dir)
    assert manifest["provenance"] == "lifecycle"
    assert manifest["event_sequence"] == 16

    later = enqueue_garden_tick(
        paths,
        "reverse-insertion-later-tick",
        clock=FakeClock([ClockReading(400, 50_000_000)]),
    )
    assert later.inserted is True
    assert later.inbox_id == 2
    assert read_status(paths).status == "sleeping"
