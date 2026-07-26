"""Closed zero-caregiver semantic projection for schema-v1/schema-v2 controls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any

from .checkpoint_core import validate_checkpoint_directory
from .errors import CheckpointError, SchemaValidationError
from .paths import OrganismPaths
from .phase2_schema import (
    OPERATIONAL_CONSULTATION_TABLES,
    PHASE2_SCHEMA_VERSION,
    ZERO_CAREGIVER_CONFIGURATION_VERSION,
)
from .storage import connect_database, validate_canonical_state

_SCHEMA_SENTINEL = "<schema-version>"
_BYTE_DERIVED_SENTINEL = "<validated-byte-derived>"

_ORIGINAL_TABLE_ORDER: tuple[tuple[str, str], ...] = (
    ("organism", "singleton_id"),
    ("budget_config", "singleton_id"),
    ("environment_state", "singleton_id"),
    ("garden_plot", "plot_id"),
    ("inventory", "singleton_id"),
    ("action_definition", "action_id"),
    ("inbox_event", "inbox_id"),
    ("event", "event_sequence"),
    ("checkpoint_registry", "event_sequence, checkpoint_id"),
)


class ZeroCaregiverProjectionError(ValueError):
    """A run is invalid for, or differs under, phase1-projection-v2."""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _checkpoint_token(lineage_generation: int, event_sequence: int) -> str:
    return f"CP({lineage_generation},{event_sequence})"


def _rows(
    connection: sqlite3.Connection,
    table: str,
    order_by: str,
) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in connection.execute(
            f"SELECT * FROM {table} ORDER BY {order_by}"
        ).fetchall()
    ]


def _project_event_payload(row: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(str(row["payload_json"]))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ZeroCaregiverProjectionError(
            f"event {row['event_sequence']} payload is not valid JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise ZeroCaregiverProjectionError(
            f"event {row['event_sequence']} payload is not an object"
        )

    projected = dict(payload)
    if "schema_version" in projected:
        projected["schema_version"] = _SCHEMA_SENTINEL

    event_type = str(row["event_type"])
    lineage_generation = int(row["lineage_generation"])
    if event_type == "checkpoint_stabilized":
        if set(projected).issuperset({"checkpoint_id", "event_sequence"}):
            projected["checkpoint_id"] = _checkpoint_token(
                lineage_generation,
                int(projected["event_sequence"]),
            )
    elif event_type == "maintenance_entered" and "checkpoint_event_sequence" in projected:
        if "checkpoint_id" not in projected:
            raise ZeroCaregiverProjectionError(
                "maintenance_entered checkpoint boundary lacks checkpoint_id"
            )
        projected["checkpoint_id"] = _checkpoint_token(
            lineage_generation,
            int(projected["checkpoint_event_sequence"]),
        )
    return projected


def _validate_zero_caregiver_absence(
    connection: sqlite3.Connection,
    *,
    schema_version: int,
) -> None:
    if schema_version != PHASE2_SCHEMA_VERSION:
        return
    row = connection.execute(
        "SELECT configuration_version FROM consultation_configuration "
        "WHERE singleton_id=1"
    ).fetchone()
    if row is None or row["configuration_version"] != ZERO_CAREGIVER_CONFIGURATION_VERSION:
        raise ZeroCaregiverProjectionError(
            "phase1-projection-v2 requires phase2-zero-caregiver-v1"
        )
    for table in OPERATIONAL_CONSULTATION_TABLES:
        count = int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        if count != 0:
            raise ZeroCaregiverProjectionError(
                f"zero-caregiver operational table {table} is not empty"
            )
    sequence_names = {
        str(item[0])
        for item in connection.execute("SELECT name FROM sqlite_sequence").fetchall()
    }
    unexpected_sequences = sorted(sequence_names.intersection(OPERATIONAL_CONSULTATION_TABLES))
    if unexpected_sequences:
        raise ZeroCaregiverProjectionError(
            "zero-caregiver operational sqlite_sequence entries exist: "
            f"{unexpected_sequences!r}"
        )
    event = connection.execute(
        "SELECT event_sequence, event_type, source FROM event "
        "WHERE event_type LIKE '%consultation%' OR source LIKE '%consultation%' "
        "ORDER BY event_sequence LIMIT 1"
    ).fetchone()
    if event is not None:
        raise ZeroCaregiverProjectionError(
            "zero-caregiver canonical consultation event or source exists"
        )


def _validated_checkpoint_artifacts(
    paths: OrganismPaths,
) -> tuple[list[dict[str, Any]], dict[tuple[int, int], dict[str, Any]]]:
    if not paths.checkpoints.is_dir():
        raise ZeroCaregiverProjectionError("checkpoint store is missing")

    projected: list[dict[str, Any]] = []
    by_boundary: dict[tuple[int, int], dict[str, Any]] = {}
    directories = sorted(
        item for item in paths.checkpoints.iterdir() if item.is_dir()
    )
    for checkpoint_dir in directories:
        try:
            manifest = validate_checkpoint_directory(checkpoint_dir)
        except (CheckpointError, SchemaValidationError) as exc:
            raise ZeroCaregiverProjectionError(str(exc)) from exc
        lineage_generation = int(manifest["lineage_generation"])
        event_sequence = int(manifest["event_sequence"])
        boundary = (lineage_generation, event_sequence)
        if boundary in by_boundary:
            raise ZeroCaregiverProjectionError(
                f"duplicate checkpoint semantic boundary: {boundary!r}"
            )
        token = _checkpoint_token(*boundary)
        manifest_path = checkpoint_dir / "manifest.json"
        database_path = checkpoint_dir / "organism.sqlite3"
        validated = {
            "checkpoint_id": str(manifest["checkpoint_id"]),
            "manifest_sha256": _sha256_file(manifest_path),
            "database_sha256": _sha256_file(database_path),
            "database_size_bytes": database_path.stat().st_size,
            "token": token,
        }
        by_boundary[boundary] = validated

        projected_manifest = dict(manifest)
        projected_manifest["checkpoint_id"] = token
        projected_manifest["schema_version"] = _SCHEMA_SENTINEL
        projected_manifest["database_sha256"] = _BYTE_DERIVED_SENTINEL
        projected_manifest["database_size_bytes"] = _BYTE_DERIVED_SENTINEL
        projected.append(
            {
                "checkpoint": token,
                "manifest": projected_manifest,
            }
        )
    projected.sort(key=lambda item: item["checkpoint"])
    return projected, by_boundary


def _project_table_rows(
    connection: sqlite3.Connection,
    *,
    table: str,
    order_by: str,
    artifacts: dict[tuple[int, int], dict[str, Any]],
) -> list[dict[str, Any]]:
    projected_rows: list[dict[str, Any]] = []
    for original in _rows(connection, table, order_by):
        row = dict(original)
        if table == "organism":
            row["schema_version"] = _SCHEMA_SENTINEL
            if row["latest_stable_checkpoint_id"] is not None:
                row["latest_stable_checkpoint_id"] = _checkpoint_token(
                    int(row["lineage_generation"]),
                    int(row["latest_stable_event_sequence"]),
                )
        elif table == "event":
            row["schema_version"] = _SCHEMA_SENTINEL
            row["payload_json"] = _project_event_payload(row)
        elif table == "checkpoint_registry":
            boundary = (
                int(row["lineage_generation"]),
                int(row["event_sequence"]),
            )
            artifact = artifacts.get(boundary)
            if artifact is None:
                raise ZeroCaregiverProjectionError(
                    f"checkpoint registry boundary has no artifact: {boundary!r}"
                )
            if row["checkpoint_id"] != artifact["checkpoint_id"]:
                raise ZeroCaregiverProjectionError(
                    "registry checkpoint identity does not match artifact"
                )
            if row["database_sha256"] != artifact["database_sha256"]:
                raise ZeroCaregiverProjectionError(
                    "registry database digest does not match artifact"
                )
            if row["manifest_sha256"] != artifact["manifest_sha256"]:
                raise ZeroCaregiverProjectionError(
                    "registry manifest digest does not match artifact"
                )
            if int(row["database_size_bytes"]) != int(
                artifact["database_size_bytes"]
            ):
                raise ZeroCaregiverProjectionError(
                    "registry database size does not match artifact"
                )
            row["checkpoint_id"] = artifact["token"]
            row["database_sha256"] = _BYTE_DERIVED_SENTINEL
            row["manifest_sha256"] = _BYTE_DERIVED_SENTINEL
            row["database_size_bytes"] = _BYTE_DERIVED_SENTINEL
        projected_rows.append(row)
    return projected_rows


def _project_original_sequences(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    original_autoincrement_tables = {"event", "inbox_event"}
    return [
        dict(row)
        for row in connection.execute(
            "SELECT name, seq FROM sqlite_sequence ORDER BY name"
        ).fetchall()
        if str(row["name"]) in original_autoincrement_tables
    ]


def project_zero_caregiver_state(paths: OrganismPaths) -> dict[str, Any]:
    """Validate one run and return its closed phase1-projection-v2 core."""

    if not paths.database.is_file():
        raise ZeroCaregiverProjectionError("organism database is missing")

    connection = connect_database(paths.database, read_only=True)
    try:
        try:
            validate_canonical_state(connection)
        except SchemaValidationError as exc:
            raise ZeroCaregiverProjectionError(str(exc)) from exc
        organism = connection.execute(
            "SELECT schema_version FROM organism WHERE singleton_id=1"
        ).fetchone()
        if organism is None:
            raise ZeroCaregiverProjectionError("organism singleton is missing")
        schema_version = int(organism["schema_version"])
        _validate_zero_caregiver_absence(
            connection,
            schema_version=schema_version,
        )
        checkpoint_artifacts, artifacts_by_boundary = _validated_checkpoint_artifacts(
            paths
        )
        tables = {
            table: _project_table_rows(
                connection,
                table=table,
                order_by=order_by,
                artifacts=artifacts_by_boundary,
            )
            for table, order_by in _ORIGINAL_TABLE_ORDER
        }
        registry_boundaries = {
            (
                int(row["lineage_generation"]),
                int(row["event_sequence"]),
            )
            for row in _rows(
                connection,
                "checkpoint_registry",
                "event_sequence, checkpoint_id",
            )
        }
        if registry_boundaries != set(artifacts_by_boundary):
            raise ZeroCaregiverProjectionError(
                "checkpoint registry and artifact boundary sets differ"
            )
        return {
            "projection_version": "phase1-projection-v2/core",
            "tables": tables,
            "sqlite_sequence": _project_original_sequences(connection),
            "checkpoint_artifacts": checkpoint_artifacts,
        }
    finally:
        connection.close()


def assert_zero_caregiver_equivalent(
    schema_v1_paths: OrganismPaths,
    schema_v2_zero_paths: OrganismPaths,
) -> None:
    """Require exact equality after independent validation and closed projection."""

    left = project_zero_caregiver_state(schema_v1_paths)
    right = project_zero_caregiver_state(schema_v2_zero_paths)
    if left != right:
        raise ZeroCaregiverProjectionError("projected canonical state differs")
