"""Protected SQLite schema and immutable Phase 1 registry validation."""

from __future__ import annotations

from functools import lru_cache
import json
import sqlite3

from .constants import BUDGET_CONFIG_VERSION, ENVIRONMENT_VERSION, PHASE1_BUDGETS
from .errors import SchemaValidationError

SQL_SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE organism (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1), organism_id TEXT NOT NULL UNIQUE,
    contract_version TEXT NOT NULL, schema_version INTEGER NOT NULL,
    environment_version TEXT NOT NULL, budget_config_version TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    developmental_stage TEXT NOT NULL, created_wall_time_utc_us INTEGER NOT NULL,
    lifecycle_number INTEGER NOT NULL CHECK (lifecycle_number >= 0),
    status TEXT NOT NULL CHECK (status IN ('sleeping','checkpoint_pending','maintenance_required','rollback_in_progress','quarantined')),
    checkpoint_pending INTEGER NOT NULL CHECK (checkpoint_pending IN (0, 1)),
    pending_checkpoint_generation INTEGER CHECK (pending_checkpoint_generation >= 0),
    pending_checkpoint_event_sequence INTEGER CHECK (pending_checkpoint_event_sequence >= 0),
    latest_stable_checkpoint_id TEXT,
    latest_stable_event_sequence INTEGER NOT NULL CHECK (latest_stable_event_sequence >= 0),
    consecutive_failures INTEGER NOT NULL CHECK (consecutive_failures >= 0),
    maintenance_reason TEXT, last_wake_wall_time_utc_us INTEGER,
    last_sleep_wall_time_utc_us INTEGER,
    CHECK ((checkpoint_pending = 1 AND pending_checkpoint_generation IS NOT NULL AND pending_checkpoint_event_sequence IS NOT NULL) OR (checkpoint_pending = 0 AND pending_checkpoint_generation IS NULL AND pending_checkpoint_event_sequence IS NULL))
);
CREATE TABLE budget_config (singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1), config_version TEXT NOT NULL UNIQUE, config_json TEXT NOT NULL);
CREATE TABLE environment_state (singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1), environment_version TEXT NOT NULL, environment_step INTEGER NOT NULL CHECK (environment_step >= 0), objective_complete INTEGER NOT NULL CHECK (objective_complete IN (0, 1)));
CREATE TABLE garden_plot (plot_id TEXT PRIMARY KEY, stage TEXT NOT NULL CHECK (stage IN ('sprout', 'mature')), moisture INTEGER NOT NULL CHECK (moisture IN (0, 1)), fruit INTEGER NOT NULL CHECK (fruit >= 0));
CREATE TABLE inventory (singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1), water_units INTEGER NOT NULL CHECK (water_units >= 0), harvested_fruit INTEGER NOT NULL CHECK (harvested_fruit >= 0));
CREATE TABLE action_definition (action_id TEXT PRIMARY KEY, version INTEGER NOT NULL CHECK (version > 0), deterministic INTEGER NOT NULL CHECK (deterministic = 1), protected INTEGER NOT NULL CHECK (protected = 1));
CREATE TABLE inbox_event (inbox_id INTEGER PRIMARY KEY AUTOINCREMENT, external_event_id TEXT NOT NULL UNIQUE, event_type TEXT NOT NULL, source TEXT NOT NULL, source_wall_time_utc_us INTEGER, received_wall_time_utc_us INTEGER NOT NULL, claimed_lifecycle_number INTEGER, consumed INTEGER NOT NULL DEFAULT 0 CHECK (consumed IN (0, 1)));
CREATE TABLE event (event_sequence INTEGER PRIMARY KEY AUTOINCREMENT, organism_id TEXT NOT NULL, lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0), lifecycle_number INTEGER NOT NULL CHECK (lifecycle_number >= 0), wall_time_utc_us INTEGER NOT NULL, event_type TEXT NOT NULL, source TEXT NOT NULL, payload_json TEXT NOT NULL, schema_version INTEGER NOT NULL, environment_version TEXT NOT NULL, budget_config_version TEXT NOT NULL);
CREATE TRIGGER event_no_update BEFORE UPDATE ON event BEGIN SELECT RAISE(ABORT, 'canonical events are append-only'); END;
CREATE TRIGGER event_no_delete BEFORE DELETE ON event BEGIN SELECT RAISE(ABORT, 'canonical events are append-only'); END;
CREATE TABLE checkpoint_registry (checkpoint_id TEXT PRIMARY KEY, lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0), event_sequence INTEGER NOT NULL CHECK (event_sequence >= 0), manifest_sha256 TEXT NOT NULL, database_sha256 TEXT NOT NULL, database_size_bytes INTEGER NOT NULL CHECK (database_size_bytes >= 0), created_wall_time_utc_us INTEGER NOT NULL, registered_wall_time_utc_us INTEGER NOT NULL, protected INTEGER NOT NULL DEFAULT 0 CHECK (protected IN (0, 1)));
"""


def _normalize_schema_sql(sql: object) -> str:
    return " ".join(str(sql).split())


def _schema_signature(connection: sqlite3.Connection) -> dict[tuple[str, str], tuple[str, str]]:
    rows = connection.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%' AND sql IS NOT NULL ORDER BY type, name, tbl_name"
    ).fetchall()
    return {(str(row[0]), str(row[1])): (str(row[2]), _normalize_schema_sql(row[3])) for row in rows}


@lru_cache(maxsize=1)
def _expected_schema_signature() -> dict[tuple[str, str], tuple[str, str]]:
    reference = sqlite3.connect(":memory:", isolation_level=None)
    try:
        reference.executescript(SQL_SCHEMA)
        return _schema_signature(reference)
    finally:
        reference.close()


def _is_side_effect_free_abort_guard(definition: tuple[str, str]) -> bool:
    _table_name, sql = definition
    upper = _normalize_schema_sql(sql).upper()
    if " BEGIN " not in upper:
        return False
    body = upper.split(" BEGIN ", 1)[1].strip()
    if not body.startswith("SELECT RAISE(ABORT"):
        return False
    forbidden = (" INSERT ", " UPDATE ", " DELETE ", " REPLACE ", " CREATE ", " DROP ", " ALTER ", " ATTACH ", " DETACH ", " PRAGMA ")
    padded_body = f" {body} "
    return not any(token in padded_body for token in forbidden)


def _require_singleton_count(connection: sqlite3.Connection, table: str) -> None:
    count = int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
    if count != 1:
        raise SchemaValidationError(f"protected singleton table {table} has {count} rows instead of 1")


def validate_protected_schema_and_configuration(connection: sqlite3.Connection) -> None:
    actual = _schema_signature(connection)
    expected = _expected_schema_signature()
    for key, expected_definition in expected.items():
        if actual.get(key) != expected_definition:
            raise SchemaValidationError("protected SQLite schema fingerprint mismatch: " f"required object {key!r} is missing or changed")
    for key, definition in actual.items():
        if key in expected:
            continue
        if key[0] != "trigger" or not _is_side_effect_free_abort_guard(definition):
            raise SchemaValidationError("protected SQLite schema fingerprint mismatch: " f"unexpected mutable object {key!r}")
    for table in ("organism", "budget_config", "environment_state", "inventory"):
        _require_singleton_count(connection, table)
    budget_row = connection.execute("SELECT config_version, config_json FROM budget_config WHERE singleton_id = 1").fetchone()
    if budget_row is None or budget_row["config_version"] != BUDGET_CONFIG_VERSION:
        raise SchemaValidationError("missing or invalid protected budget configuration")
    try:
        budget_values = json.loads(budget_row["config_json"])
    except (TypeError, json.JSONDecodeError) as exc:
        raise SchemaValidationError("protected budget configuration is not valid JSON") from exc
    if budget_values != PHASE1_BUDGETS.as_dict():
        raise SchemaValidationError("protected budget values do not match Contract v0.2")
    environment = connection.execute("SELECT * FROM environment_state WHERE singleton_id = 1").fetchone()
    if environment is None or environment["environment_version"] != ENVIRONMENT_VERSION:
        raise SchemaValidationError("missing or invalid seed environment")
    plot_layout = tuple(tuple(row) for row in connection.execute("SELECT plot_id, stage FROM garden_plot ORDER BY plot_id").fetchall())
    if plot_layout != (("bed-a", "sprout"), ("bed-b", "mature")):
        raise SchemaValidationError(f"protected seed-garden layout mismatch: {plot_layout!r}")
    actions = tuple(tuple(row) for row in connection.execute("SELECT action_id, version, deterministic, protected FROM action_definition ORDER BY action_id").fetchall())
    if actions != (("harvest_plot", 1, 1, 1), ("water_plot", 1, 1, 1)):
        raise SchemaValidationError(f"protected action registry mismatch: {actions!r}")
