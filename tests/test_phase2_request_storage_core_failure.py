from __future__ import annotations

from pathlib import Path
import shutil
import sqlite3

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import ACTIVE_DATABASE_MAX_BYTES
from sudachi_life.errors import SchemaValidationError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import _original_perform_garden_wake, perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    OPERATIONAL_CONSULTATION_TABLES,
    PHASE2_SCHEMA_VERSION,
)
from sudachi_life.storage import connect_database, read_status, validate_canonical_state

from phase1_audit_helpers import _wake_clock

_TABLES = (
    "organism",
    "budget_config",
    "environment_state",
    "garden_plot",
    "inventory",
    "action_definition",
    "inbox_event",
    "event",
    "checkpoint_registry",
    *OPERATIONAL_CONSULTATION_TABLES,
)


def _initialize(tmp_path: Path) -> tuple[Path, OrganismPaths]:
    root = tmp_path / "runtime"
    initialize_organism(
        root,
        "request-core-over-limit",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_200_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
        schema_version=PHASE2_SCHEMA_VERSION,
        consultation_configuration_version=FIXTURE_CONFIGURATION_VERSION,
    )
    paths = OrganismPaths.build(root, "request-core-over-limit")
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE inventory SET water_units=0 WHERE singleton_id=1")
        connection.execute("UPDATE garden_plot SET moisture=1, fruit=0")
        connection.execute(
            "UPDATE environment_state SET objective_complete=0 WHERE singleton_id=1"
        )
        connection.commit()
    finally:
        connection.close()
    enqueue_garden_tick(
        paths,
        "request-core-over-limit-tick",
        clock=FakeClock([ClockReading(2_201_000_000_000_000, 20_000_000)]),
    )
    return root, paths


def _inflate_one_page_over(database: Path) -> None:
    connection = sqlite3.connect(database, isolation_level=None)
    try:
        connection.execute("PRAGMA journal_mode=DELETE")
        connection.execute(
            "CREATE TABLE request_core_over_limit_padding (value BLOB NOT NULL)"
        )
        while True:
            page_count = int(connection.execute("PRAGMA page_count").fetchone()[0])
            page_size = int(connection.execute("PRAGMA page_size").fetchone()[0])
            if page_count * page_size > ACTIVE_DATABASE_MAX_BYTES:
                break
            connection.execute(
                "INSERT INTO request_core_over_limit_padding(value) VALUES (zeroblob(?))",
                (64 * 1024,),
            )
        connection.execute("DROP TABLE request_core_over_limit_padding")
    finally:
        connection.close()
    assert database.stat().st_size > ACTIVE_DATABASE_MAX_BYTES


def _snapshot(paths: OrganismPaths) -> tuple[object, ...]:
    connection = connect_database(paths.database, read_only=True)
    try:
        tables = tuple(
            (
                table,
                tuple(
                    tuple(row)
                    for row in connection.execute(
                        f"SELECT * FROM {table} ORDER BY rowid"
                    ).fetchall()
                ),
            )
            for table in _TABLES
        )
        sequences = tuple(
            tuple(row)
            for row in connection.execute(
                "SELECT name, seq FROM sqlite_sequence ORDER BY name"
            ).fetchall()
        )
        validate_canonical_state(connection, expect_checkpoint_pending=False)
    finally:
        connection.close()
    return tables, sequences, read_status(paths)


def test_core_over_limit_failure_is_not_converted_to_optional_refusal(
    tmp_path: Path,
) -> None:
    base_root, base_paths = _initialize(tmp_path / "base")
    _inflate_one_page_over(base_paths.database)
    control_root = tmp_path / "control"
    public_root = tmp_path / "public"
    shutil.copytree(base_root, control_root)
    shutil.copytree(base_root, public_root)
    control_paths = OrganismPaths.build(control_root, base_paths.organism_id)
    public_paths = OrganismPaths.build(public_root, base_paths.organism_id)
    before = _snapshot(base_paths)

    with pytest.raises(SchemaValidationError) as control_error:
        _original_perform_garden_wake(
            control_root,
            control_paths.organism_id,
            seed=3,
            clock=_wake_clock(2_202_000_000_000_000),
        )
    with pytest.raises(SchemaValidationError) as public_error:
        perform_garden_wake(
            public_root,
            public_paths.organism_id,
            seed=3,
            clock=_wake_clock(2_202_000_000_000_000),
        )

    assert type(public_error.value) is type(control_error.value)
    assert str(public_error.value) == str(control_error.value)
    assert "active database would exceed protected Phase 1 limit" in str(
        public_error.value
    )
    assert _snapshot(control_paths) == before
    assert _snapshot(public_paths) == before
