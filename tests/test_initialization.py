from __future__ import annotations

import sqlite3

import pytest

from sudachi_life.constants import (
    BUDGET_CONFIG_VERSION,
    CONTRACT_VERSION,
    ENVIRONMENT_VERSION,
    PHASE1_BUDGETS,
    SCHEMA_VERSION,
)
from sudachi_life.errors import OrganismExistsError
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database


def test_initialization_creates_contract_v0_2_genesis(initialized) -> None:
    runtime_root, status, checkpoint = initialized

    assert status.organism_id == "sudachi-0"
    assert status.contract_version == CONTRACT_VERSION
    assert status.schema_version == SCHEMA_VERSION
    assert status.environment_version == ENVIRONMENT_VERSION
    assert status.budget_config_version == BUDGET_CONFIG_VERSION
    assert status.status == "sleeping"
    assert status.checkpoint_pending is False
    assert status.latest_stable_checkpoint_id == checkpoint.checkpoint_id
    assert status.latest_stable_event_sequence == 2
    assert status.event_count == 3
    assert status.environment_step == 0
    assert status.objective_complete is False
    assert status.water_units == 1
    assert status.harvested_fruit == 0
    assert status.plots == (
        {"plot_id": "bed-a", "stage": "sprout", "moisture": 0, "fruit": 0},
        {"plot_id": "bed-b", "stage": "mature", "moisture": 1, "fruit": 1},
    )

    paths = OrganismPaths.build(runtime_root, "sudachi-0")
    assert paths.database.is_file()
    assert checkpoint.checkpoint_dir.is_dir()


def test_protected_budget_defaults_are_stored_exactly(initialized) -> None:
    runtime_root, _, _ = initialized
    paths = OrganismPaths.build(runtime_root, "sudachi-0")
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT config_version, config_json FROM budget_config WHERE singleton_id = 1"
        ).fetchone()
        import json

        assert row["config_version"] == BUDGET_CONFIG_VERSION
        assert json.loads(row["config_json"]) == PHASE1_BUDGETS.as_dict()
    finally:
        connection.close()


def test_canonical_state_has_no_energy_column(initialized) -> None:
    runtime_root, _, _ = initialized
    paths = OrganismPaths.build(runtime_root, "sudachi-0")
    connection = connect_database(paths.database, read_only=True)
    try:
        columns = {
            row["name"] for row in connection.execute("PRAGMA table_info(organism)").fetchall()
        }
        assert "energy" not in columns
    finally:
        connection.close()


def test_foreign_keys_are_enabled_for_project_connections(initialized) -> None:
    runtime_root, _, _ = initialized
    connection = connect_database(
        OrganismPaths.build(runtime_root, "sudachi-0").database,
        read_only=True,
    )
    try:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        connection.close()


def test_event_history_rejects_update_and_delete(initialized) -> None:
    runtime_root, _, _ = initialized
    connection = connect_database(OrganismPaths.build(runtime_root, "sudachi-0").database)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE event SET event_type = 'rewritten' WHERE event_sequence = 1"
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("DELETE FROM event WHERE event_sequence = 1")
    finally:
        connection.close()


def test_initialization_refuses_to_overwrite_existing_organism(
    initialized, fixed_clock
) -> None:
    runtime_root, _, _ = initialized
    with pytest.raises(OrganismExistsError):
        initialize_organism(runtime_root, "sudachi-0", clock=fixed_clock)
