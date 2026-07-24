"""Canonical SQLite schema, initialization, and status reads."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any

from .clock import Clock, RealClock
from .constants import (
    ACTIVE_DATABASE_MAX_BYTES,
    BUDGET_CONFIG_VERSION,
    CONTRACT_VERSION,
    CONSECUTIVE_FAILURE_LIMIT,
    DEVELOPMENTAL_STAGE,
    ENVIRONMENT_VERSION,
    PHASE1_BUDGETS,
    SCHEMA_VERSION,
)
from .errors import OrganismExistsError, OrganismNotFoundError, SchemaValidationError
from .paths import OrganismPaths
from .runtime_storage import ensure_active_database_within_limit
from .schema_contract import SQL_SCHEMA, validate_protected_schema_and_configuration

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
    maintenance_reason: str | None
    environment_step: int
    objective_complete: bool
    water_units: int
    harvested_fruit: int
    plots: tuple[dict[str, Any], ...]
    event_count: int

    def as_dict(self) -> dict[str, Any]:
        payload = {
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
        if self.maintenance_reason is not None:
            payload["maintenance_reason"] = self.maintenance_reason
        return payload


def connect_database(path: Path, *, read_only: bool = False) -> sqlite3.Connection:
    if read_only:
        uri = f"{path.resolve().as_uri()}?mode=ro"
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
        ensure_active_database_within_limit(
            connection, context="initialization", limit=ACTIVE_DATABASE_MAX_BYTES
        )
        connection.commit()
    except Exception:
        if connection.in_transaction:
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
    validate_protected_schema_and_configuration(connection)

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

    status = str(row["status"])
    failure_streak = int(row["consecutive_failures"])
    maintenance_reason = row["maintenance_reason"]
    if status == "sleeping" and failure_streak >= CONSECUTIVE_FAILURE_LIMIT:
        raise SchemaValidationError(
            "sleeping organism has reached the protected maintenance threshold"
        )
    if status == "sleeping" and maintenance_reason is not None:
        raise SchemaValidationError("sleeping organism retains a maintenance reason")
    if status == "maintenance_required" and not maintenance_reason:
        raise SchemaValidationError("maintenance state requires a typed reason")
    if (
        status == "checkpoint_pending"
        and failure_streak >= CONSECUTIVE_FAILURE_LIMIT
        and not maintenance_reason
    ):
        raise SchemaValidationError(
            "threshold checkpoint pending state requires a maintenance reason"
        )

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
            maintenance_reason=organism["maintenance_reason"],
            environment_step=environment["environment_step"],
            objective_complete=bool(environment["objective_complete"]),
            water_units=inventory["water_units"],
            harvested_fruit=inventory["harvested_fruit"],
            plots=plots,
            event_count=event_count,
        )
    finally:
        connection.close()
