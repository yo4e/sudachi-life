"""Rollback-specific original-state projection with cross-lineage checkpoint links."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import SchemaValidationError
from .phase2_projection import (
    SCHEMA_SENTINEL,
    CheckpointArtifactEvidence,
    EventPayloadEvidence,
    ZeroCaregiverProjectionError,
    _ORIGINAL_TABLE_ORDER,
    _project_original_sequences,
    _project_table_rows,
    _rows,
)
from .storage import connect_database, validate_canonical_state


def _project_organism_rows(
    connection,
    *,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
) -> list[dict[str, Any]]:
    projected: list[dict[str, Any]] = []
    for original in _rows(connection, "organism", "singleton_id"):
        row = dict(original)
        row["schema_version"] = SCHEMA_SENTINEL
        raw_checkpoint_id = row["latest_stable_checkpoint_id"]
        if raw_checkpoint_id is not None:
            event_sequence = int(row["latest_stable_event_sequence"])
            matches = [
                artifact
                for artifact in artifacts.values()
                if artifact.checkpoint_id == raw_checkpoint_id
                and artifact.event_sequence == event_sequence
            ]
            if len(matches) != 1:
                raise ZeroCaregiverProjectionError(
                    "rollback organism latest checkpoint does not resolve to exactly "
                    "one validated artifact"
                )
            row["latest_stable_checkpoint_id"] = matches[0].token
        projected.append(row)
    return projected


def project_database_state(
    database_path: Path,
    *,
    expect_checkpoint_pending: bool,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    event_evidence: dict[int, EventPayloadEvidence],
) -> dict[str, Any]:
    """Project one validated database while honoring old-lineage checkpoint refs."""

    connection = connect_database(database_path, read_only=True)
    try:
        try:
            validate_canonical_state(
                connection,
                expect_checkpoint_pending=expect_checkpoint_pending,
            )
        except SchemaValidationError as exc:
            raise ZeroCaregiverProjectionError(str(exc)) from exc
        tables: dict[str, list[dict[str, Any]]] = {}
        for table, order_by in _ORIGINAL_TABLE_ORDER:
            if table == "organism":
                tables[table] = _project_organism_rows(
                    connection,
                    artifacts=artifacts,
                )
            else:
                tables[table] = _project_table_rows(
                    connection,
                    table=table,
                    order_by=order_by,
                    artifacts=artifacts,
                    event_evidence=event_evidence,
                )
        return {
            "tables": tables,
            "sqlite_sequence": _project_original_sequences(connection),
        }
    finally:
        connection.close()
