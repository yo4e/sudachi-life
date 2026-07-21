"""Canonical SQLite schema, initialization, and status reads."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any

from .clock import Clock, RealClock
from .constants import (
    BUDGET_CONFIG_VERSION,
    CONTRACT_VERSION,
    DEVELOPMENTAL_STAGE,
    ENVIRONMENT_VERSION,
    PHASE1_BUDGETS,
    SCHEMA_VERSION,
)
from .errors import OrganismExistsError, OrganismNotFoundError, SchemaValidationError
from .paths import OrganismPaths

SQL_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE organism (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    organism_id TEXT NOT NULL UNIQUE,
    contract_version TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    environment_version TEXT NOT NULL,
    budget_config_version TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    developmental_stage TEXT NOT NULL,
    created_wall_time_utc_us INTEGER NOT NULL,
    lifecycle_number INTEGER NOT NULL CHECK (lifecycle_number >= 0),
    status TEXT NOT NULL CHECK (status IN (
        'sleeping',
        'checkpoint_pending',
        'maintenance_required',
        'rollback_in_progress',
        'quarantined'
    )),
    checkpoint_pending INTEGER NOT NULL CHECK (checkpoint_pending IN (0, 1)),
    pending_checkpoint_generation INTEGER CHECK (pending_checkpoint_generation >= 0),
    pending_checkpoint_event_sequence INTEGER CHECK (pending_checkpoint_event_sequence >= 0),
    latest_stable_checkpoint_id TEXT,
    latest_stable_event_sequence INTEGER NOT NULL CHECK (latest_stable_event_sequence >= 0),
    consecutive_failures INTEGER NOT NULL CHECK (consecutive_failures >= 0),
    maintenance_reason TEXT,
    last_wake_wall_time_utc_us INTEGER,
    last_sleep_wall_time_utc_us INTEGER,
    CHECK (
        (checkpoint_pending = 1 AND pending_checkpoint_generation IS NOT NULL
         AND pending_checkpoint_event_sequence IS NOT NULL)
        OR
        (checkpoint_pending = 0 AND pending_checkpoint_generation IS NULL
         AND pending_checkpoint_event_sequence IS NULL)
    )
);

CREATE TABLE budget_config (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    config_version TEXT NOT NULL UNIQUE,
    config_json TEXT NOT NULL
);

CREATE TABLE environment_state (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    environment_version TEXT NOT NULL,
    environment_step INTEGER NOT NULL CHECK (environment_step >= 0),
    objective_complete INTEGER NOT NULL CHECK (objective_complete IN (0, 1))
);

CREATE TABLE garden_plot (
    plot_id TEXT PRIMARY KEY,
    stage TEXT NOT NULL CHECK (stage IN ('sprout', 'mature')),
    moisture INTEGER NOT NULL CHECK (moisture IN (0, 1)),
    fruit INTEGER NOT NULL CHECK (fruit >= 0)
);

CREATE TABLE inventory (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    water_units INTEGER NOT NULL CHECK (water_units >= 0),
    harvested_fruit INTEGER NOT NULL CHECK (harvested_fruit >= 0)
);

CREATE TABLE action_definition (
    action_id TEXT PRIMARY KEY,
    version INTEGER NOT NULL CHECK (version > 0),
    deterministic INTEGER NOT NULL CHECK (deterministic = 1),
    protected INTEGER NOT NULL CHECK (protected = 1)
);

CREATE TABLE inbox_event (
    inbox_id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_event_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    source_wall_time_utc_us INTEGER,
    received_wall_time_utc_us INTEGER NOT NULL,
    claimed_lifecycle_number INTEGER,
    consumed INTEGER NOT NULL DEFAULT 0 CHECK (consumed IN (0, 1))
);

CREATE TABLE event (
    event_sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    organism_id TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    lifecycle_number INTEGER NOT NULL CHECK (lifecycle_number >= 0),
    wall_time_utc_us INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    source TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    environment_version TEXT NOT NULL,
    budget_config_version TEXT NOT NULL
);

CREATE TRIGGER event_no_update
BEFORE UPDATE ON event
BEGIN
    SELECT RAISE(ABORT, 'canonical events are append-only');
END;

CREATE TRIGGER event_no_delete
BEFORE DELETE ON event
BEGIN
    SELECT RAISE(ABORT, 'canonical events are append-only');
END;

CREATE TABLE checkpoint_registry (
    checkpoint_id TEXT PRIMARY KEY,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    event_sequence INTEGER NOT NULL CHECK (event_sequence >= 0),
    manifest_sha256 TEXT NOT NULL,
    database_sha256 TEXT NOT NULL,
    database_size_bytes INTEGER NOT NULL CHECK (database_size_bytes >= 0),
    created_wall_time_utc_us INTEGER NOT NULL,
    registered_wall_time_utc_us INTEGER NOT NULL,
    protected INTEGER NOT NULL DEFAULT 0 CHECK (protected IN (0, 1))
);
"""


@dataclass(frozen=True, slots=True)
class OrganismStatus:
    organism_id: str
    contract_version: str
    schema_version: int
    environment_version: str
    budget_config_version: str
    lineage_generation: int
    lifecycle_number: int
    status: str
    checkpoint_pending: bool
    latest_stable_checkpoint_id: str | None
    latest_stable_event_sequence: int
    consecutive_failures: int
    environment_step: int
    objective_complete: bool
    water_units: int
    harvested_fruit: int
    plots: tuple[dict[str, Any], ...]
    event_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "organism_id": self.organism_id,
            "contract_version": self.contract_version,
            "schema_version": self.schema_version,
            "environment_version": self.environment_version,
            "budget_config_version": self.budget_config_version,
            "lineage_generation": self.lineage_generation,
            "lifecycle_number": self.lifecycle_number,
            "status": self.status,
            "checkpoint_pending": self.checkpoint_pending,
            "latest_stable_checkpoint_id": self.latest_stable_checkpoint_id,
            "latest_stable_event_sequence": self.latest_stable_event_sequence,
            "consecutive_failures": self.consecutive_failures,
            "environment_step": self.environment_step,
            "objective_complete": self.objective_complete,
            "water_units": self.water_units,
            "harvested_fruit": self.harvested_fruit,
            "plots": list(self.plots),
            "event_count": self.event_count,
        }


def connect_database(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    if read_only:
        uri = f"file:{path.resolve().as_posix()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True, timeout=0.0, isolation_level=None)
    else:
        connection = sqlite3.connect(path, timeout=0.0, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        connection.close()
        raise SchemaValidationError("SQLite foreign-key enforcement is not enabled")
    return connection


def _insert_event(
    connection: sqlite3.Connection,
    *,
    organism_id: str,
    lineage_generation: int,
    lifecycle_number: int,
    wall_time_utc_us: int,
    event_type: str,
    source: str,
    payload: dict[str, Any],
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO event (
            organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
            event_type, source, payload_json, schema_version,
            environment_version, budget_config_version
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            organism_id,
            lineage_generation,
            lifecycle_number,
            wall_time_utc_us,
            event_type,
            source,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
            SCHEMA_VERSION,
            ENVIRONMENT_VERSION,
            BUDGET_CONFIG_VERSION,
        ),
    )
    return int(cursor.lastrowid)


def initialize_database(
    paths: OrganismPaths,
    *,
    clock: Clock | None = None,
) -> tuple[int, int]:
    """Create canonical genesis state and return (wall_time, event boundary)."""

    clock = clock or RealClock()

    if paths.organism_dir.exists():
        raise OrganismExistsError(f"organism already exists: {paths.organism_dir}")

    reading = clock.read()
    paths.runtime_root.mkdir(parents=True, exist_ok=True)
    if paths.runtime_root.is_symlink():
        raise SchemaValidationError("runtime root may not be a symlink")

    paths.organism_dir.mkdir(mode=0o700)
    paths.checkpoints.mkdir(mode=0o700)
    paths.exports.mkdir(mode=0o700)
    paths.diagnostics.mkdir(mode=0o700)

    connection = connect_database(paths.database)
    try:
        connection.execute("PRAGMA journal_mode = DELETE")
        connection.execute("PRAGMA synchronous = FULL")
        connection.executescript(SQL_SCHEMA)
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        connection.execute("BEGIN IMMEDIATE")

        connection.execute(
            """
            INSERT INTO organism (
                singleton_id, organism_id, contract_version, schema_version,
                environment_version, budget_config_version, lineage_generation,
                developmental_stage, created_wall_time_utc_us, lifecycle_number,
                status, checkpoint_pending, pending_checkpoint_generation,
                pending_checkpoint_event_sequence, latest_stable_checkpoint_id,
                latest_stable_event_sequence, consecutive_failures,
                maintenance_reason, last_wake_wall_time_utc_us,
                last_sleep_wall_time_utc_us
            ) VALUES (1, ?, ?, ?, ?, ?, 0, ?, ?, 0,
                      'checkpoint_pending', 1, 0, 0, NULL, 0, 0, NULL, NULL, NULL)
            """,
            (
                paths.organism_id,
                CONTRACT_VERSION,
                SCHEMA_VERSION,
                ENVIRONMENT_VERSION,
                BUDGET_CONFIG_VERSION,
                DEVELOPMENTAL_STAGE,
                reading.wall_time_utc_us,
            ),
        )
        connection.execute(
            "INSERT INTO budget_config (singleton_id, config_version, config_json) VALUES (1, ?, ?)",
            (
                BUDGET_CONFIG_VERSION,
                json.dumps(PHASE1_BUDGETS.as_dict(), sort_keys=True, separators=(",", ":")),
            ),
        )
        connection.execute(
            "INSERT INTO environment_state VALUES (1, ?, 0, 0)",
            (ENVIRONMENT_VERSION,),
        )
        connection.executemany(
            "INSERT INTO garden_plot (plot_id, stage, moisture, fruit) VALUES (?, ?, ?, ?)",
            [
                ("bed-a", "sprout", 0, 0),
                ("bed-b", "mature", 1, 1),
            ],
        )
        connection.execute("INSERT INTO inventory VALUES (1, 1, 0)")
        connection.executemany(
            "INSERT INTO action_definition VALUES (?, 1, 1, 1)",
            [("water_plot",), ("harvest_plot",)],
        )

        _insert_event(
            connection,
            organism_id=paths.organism_id,
            lineage_generation=0,
            lifecycle_number=0,
            wall_time_utc_us=reading.wall_time_utc_us,
            event_type="organism_initialized",
            source="administration:init",
            payload={
                "contract_version": CONTRACT_VERSION,
                "schema_version": SCHEMA_VERSION,
                "environment_version": ENVIRONMENT_VERSION,
                "budget_config_version": BUDGET_CONFIG_VERSION,
            },
        )
        boundary = _insert_event(
            connection,
            organism_id=paths.organism_id,
            lineage_generation=0,
            lifecycle_number=0,
            wall_time_utc_us=reading.wall_time_utc_us,
            event_type="checkpoint_pending",
            source="administration:init",
            payload={"reason": "genesis"},
        )
        connection.execute(
            "UPDATE organism SET pending_checkpoint_event_sequence = ? WHERE singleton_id = 1",
            (boundary,),
        )
        validate_canonical_state(connection, expect_checkpoint_pending=True)
        connection.commit()
    except Exception:
        connection.rollback()
        connection.close()
        _remove_partial_organism(paths)
        raise
    finally:
        connection.close()

    return reading.wall_time_utc_us, boundary


def _remove_partial_organism(paths: OrganismPaths) -> None:
    import shutil

    if paths.organism_dir.exists():
        shutil.rmtree(paths.organism_dir)


def validate_canonical_state(
    connection: sqlite3.Connection,
    *,
    expect_checkpoint_pending: bool | None = None,
) -> None:
    row = connection.execute("SELECT * FROM organism WHERE singleton_id = 1").fetchone()
    if row is None:
        raise SchemaValidationError("missing organism singleton")

    expected = {
        "contract_version": CONTRACT_VERSION,
        "schema_version": SCHEMA_VERSION,
        "environment_version": ENVIRONMENT_VERSION,
        "budget_config_version": BUDGET_CONFIG_VERSION,
        "developmental_stage": DEVELOPMENTAL_STAGE,
    }
    for column, value in expected.items():
        if row[column] != value:
            raise SchemaValidationError(
                f"protected {column} mismatch: expected {value!r}, found {row[column]!r}"
            )

    user_version = connection.execute("PRAGMA user_version").fetchone()[0]
    if user_version != SCHEMA_VERSION:
        raise SchemaValidationError(
            f"SQLite user_version mismatch: expected {SCHEMA_VERSION}, found {user_version}"
        )

    pending = bool(row["checkpoint_pending"])
    if expect_checkpoint_pending is not None and pending is not expect_checkpoint_pending:
        raise SchemaValidationError(
            f"checkpoint_pending mismatch: expected {expect_checkpoint_pending}, found {pending}"
        )

    budget_row = connection.execute(
        "SELECT config_version, config_json FROM budget_config WHERE singleton_id = 1"
    ).fetchone()
    if budget_row is None or budget_row["config_version"] != BUDGET_CONFIG_VERSION:
        raise SchemaValidationError("missing or invalid protected budget configuration")
    if json.loads(budget_row["config_json"]) != PHASE1_BUDGETS.as_dict():
        raise SchemaValidationError("protected budget values do not match Contract v0.2")

    environment = connection.execute(
        "SELECT * FROM environment_state WHERE singleton_id = 1"
    ).fetchone()
    if environment is None or environment["environment_version"] != ENVIRONMENT_VERSION:
        raise SchemaValidationError("missing or invalid seed environment")

    plots = connection.execute(
        "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id"
    ).fetchall()
    if not plots:
        raise SchemaValidationError("seed garden has no plots")

    foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()
    if foreign_key_errors:
        raise SchemaValidationError(f"foreign-key errors: {foreign_key_errors!r}")


def read_status(paths: OrganismPaths) -> OrganismStatus:
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database, read_only=True)
    try:
        validate_canonical_state(connection)
        organism = connection.execute("SELECT * FROM organism WHERE singleton_id = 1").fetchone()
        environment = connection.execute(
            "SELECT environment_step, objective_complete FROM environment_state WHERE singleton_id = 1"
        ).fetchone()
        inventory = connection.execute(
            "SELECT water_units, harvested_fruit FROM inventory WHERE singleton_id = 1"
        ).fetchone()
        plots = tuple(
            dict(row)
            for row in connection.execute(
                "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id"
            ).fetchall()
        )
        event_count = connection.execute("SELECT COUNT(*) FROM event").fetchone()[0]
        return OrganismStatus(
            organism_id=organism["organism_id"],
            contract_version=organism["contract_version"],
            schema_version=organism["schema_version"],
            environment_version=organism["environment_version"],
            budget_config_version=organism["budget_config_version"],
            lineage_generation=organism["lineage_generation"],
            lifecycle_number=organism["lifecycle_number"],
            status=organism["status"],
            checkpoint_pending=bool(organism["checkpoint_pending"]),
            latest_stable_checkpoint_id=organism["latest_stable_checkpoint_id"],
            latest_stable_event_sequence=organism["latest_stable_event_sequence"],
            consecutive_failures=organism["consecutive_failures"],
            environment_step=environment["environment_step"],
            objective_complete=bool(environment["objective_complete"]),
            water_units=inventory["water_units"],
            harvested_fruit=inventory["harvested_fruit"],
            plots=plots,
            event_count=event_count,
        )
    finally:
        connection.close()
