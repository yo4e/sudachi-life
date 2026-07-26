"""Closed zero-caregiver semantic projection for schema-v1/schema-v2 controls."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Final

from .checkpoint_core import validate_checkpoint_directory
from .errors import CheckpointError, SchemaValidationError
from .paths import OrganismPaths
from .phase2_schema import (
    OPERATIONAL_CONSULTATION_TABLES,
    PHASE2_SCHEMA_VERSION,
    ZERO_CAREGIVER_CONFIGURATION_VERSION,
)
from .runtime_storage import checkpoint_store_bytes
from .storage import connect_database, validate_canonical_state

SCHEMA_SENTINEL: Final = "<schema-version>"
BYTE_DERIVED_SENTINEL: Final = "<validated-byte-derived>"

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

_REPAIR_BASE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "checkpoint_id",
        "checkpoint_store_bytes",
        "database_sha256",
        "database_size_bytes",
        "event_sequence",
        "lineage_generation",
        "manifest_sha256",
        "previous_latest_stable_checkpoint_id",
        "previous_latest_stable_event_sequence",
        "reason",
        "status_after",
        "status_before",
    }
)


class ZeroCaregiverProjectionError(ValueError):
    """A run is invalid for, or differs under, phase1-projection-v2."""


@dataclass(frozen=True)
class CheckpointArtifactEvidence:
    """Validated immutable evidence for one checkpoint artifact boundary."""

    lineage_generation: int
    event_sequence: int
    checkpoint_id: str
    manifest_sha256: str
    database_sha256: str
    database_size_bytes: int
    artifact_size_bytes: int
    manifest_json: str
    projected_database_state_json: str

    @property
    def boundary(self) -> tuple[int, int]:
        return (self.lineage_generation, self.event_sequence)

    @property
    def token(self) -> str:
        return _checkpoint_token(*self.boundary)


@dataclass(frozen=True)
class EventPayloadEvidence:
    """Validated exact replacement for one canonical event payload."""

    event_sequence: int
    event_type: str
    raw_payload_json: str
    projected_payload_json: str


@dataclass(frozen=True)
class ZeroCaregiverEvidence:
    """Immutable cumulative evidence captured at deterministic operation boundaries."""

    organism_id: str
    checkpoint_artifacts: tuple[CheckpointArtifactEvidence, ...]
    event_payloads: tuple[EventPayloadEvidence, ...]
    retained_checkpoint_boundaries: tuple[tuple[int, int], ...]


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_size(path: Path) -> int:
    return sum(
        item.stat().st_size
        for item in path.rglob("*")
        if item.is_file() and not item.is_symlink()
    )


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


def _decode_payload(row: dict[str, Any]) -> dict[str, Any]:
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
    return payload


def _artifact_map(
    evidence: ZeroCaregiverEvidence | None,
) -> dict[tuple[int, int], CheckpointArtifactEvidence]:
    if evidence is None:
        return {}
    result: dict[tuple[int, int], CheckpointArtifactEvidence] = {}
    for artifact in evidence.checkpoint_artifacts:
        if artifact.boundary in result:
            raise ZeroCaregiverProjectionError(
                f"duplicate checkpoint evidence boundary: {artifact.boundary!r}"
            )
        result[artifact.boundary] = artifact
    return result


def _event_evidence_map(
    evidence: ZeroCaregiverEvidence | None,
) -> dict[int, EventPayloadEvidence]:
    if evidence is None:
        return {}
    result: dict[int, EventPayloadEvidence] = {}
    for item in evidence.event_payloads:
        if item.event_sequence in result:
            raise ZeroCaregiverProjectionError(
                f"duplicate event evidence sequence: {item.event_sequence}"
            )
        result[item.event_sequence] = item
    return result


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


def _inventory_visible_checkpoint_artifacts(
    paths: OrganismPaths,
) -> dict[tuple[int, int], CheckpointArtifactEvidence]:
    if not paths.checkpoints.is_dir() or paths.checkpoints.is_symlink():
        raise ZeroCaregiverProjectionError("checkpoint store is missing or unsafe")
    result: dict[tuple[int, int], CheckpointArtifactEvidence] = {}
    for checkpoint_dir in sorted(paths.checkpoints.iterdir(), key=lambda item: item.name):
        if checkpoint_dir.name.startswith("."):
            continue
        if checkpoint_dir.is_symlink() or not checkpoint_dir.is_dir():
            raise ZeroCaregiverProjectionError("checkpoint store has an unsafe visible entry")
        try:
            manifest = validate_checkpoint_directory(checkpoint_dir)
        except (CheckpointError, SchemaValidationError) as exc:
            raise ZeroCaregiverProjectionError(str(exc)) from exc
        boundary = (
            int(manifest["lineage_generation"]),
            int(manifest["event_sequence"]),
        )
        if boundary in result:
            raise ZeroCaregiverProjectionError(
                f"duplicate checkpoint semantic boundary: {boundary!r}"
            )
        manifest_path = checkpoint_dir / "manifest.json"
        database_path = checkpoint_dir / "organism.sqlite3"
        result[boundary] = CheckpointArtifactEvidence(
            lineage_generation=boundary[0],
            event_sequence=boundary[1],
            checkpoint_id=str(manifest["checkpoint_id"]),
            manifest_sha256=_sha256_file(manifest_path),
            database_sha256=_sha256_file(database_path),
            database_size_bytes=database_path.stat().st_size,
            artifact_size_bytes=_artifact_size(checkpoint_dir),
            manifest_json=_canonical_json(manifest),
            projected_database_state_json="",
        )
    return result


def _merge_artifact_evidence(
    prior: dict[tuple[int, int], CheckpointArtifactEvidence],
    current: dict[tuple[int, int], CheckpointArtifactEvidence],
) -> dict[tuple[int, int], CheckpointArtifactEvidence]:
    merged = dict(prior)
    for boundary, artifact in current.items():
        previous = merged.get(boundary)
        if previous is not None:
            comparable_previous = replace(previous, projected_database_state_json="")
            comparable_current = replace(artifact, projected_database_state_json="")
            if comparable_previous != comparable_current:
                raise ZeroCaregiverProjectionError(
                    f"checkpoint evidence changed for boundary: {boundary!r}"
                )
            if previous.projected_database_state_json:
                artifact = replace(
                    artifact,
                    projected_database_state_json=previous.projected_database_state_json,
                )
        merged[boundary] = artifact
    return merged


def _validate_repair_event(
    row: dict[str, Any],
    payload: dict[str, Any],
    *,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    measured_store_bytes: int,
) -> dict[str, Any]:
    expected_keys = set(_REPAIR_BASE_KEYS)
    if payload.get("status_after") == "maintenance_required":
        expected_keys.add("maintenance_reason")
    if set(payload) != expected_keys:
        raise ZeroCaregiverProjectionError(
            "checkpoint_registration_repaired payload keys are not exact"
        )
    boundary = (int(payload["lineage_generation"]), int(payload["event_sequence"]))
    artifact = artifacts.get(boundary)
    if artifact is None:
        raise ZeroCaregiverProjectionError(
            f"repair checkpoint boundary has no artifact: {boundary!r}"
        )
    if payload["checkpoint_id"] != artifact.checkpoint_id:
        raise ZeroCaregiverProjectionError(
            "repair checkpoint identity does not match artifact"
        )
    if payload["database_sha256"] != artifact.database_sha256:
        raise ZeroCaregiverProjectionError(
            "repair database digest does not match artifact"
        )
    if payload["manifest_sha256"] != artifact.manifest_sha256:
        raise ZeroCaregiverProjectionError(
            "repair manifest digest does not match artifact"
        )
    if int(payload["database_size_bytes"]) != artifact.database_size_bytes:
        raise ZeroCaregiverProjectionError(
            "repair database size does not match artifact"
        )
    if int(payload["checkpoint_store_bytes"]) != measured_store_bytes:
        raise ZeroCaregiverProjectionError(
            "repair checkpoint_store_bytes does not match measured store"
        )
    previous_id = payload["previous_latest_stable_checkpoint_id"]
    previous_event = int(payload["previous_latest_stable_event_sequence"])
    if previous_id is None:
        if previous_event != 0:
            raise ZeroCaregiverProjectionError(
                "repair previous checkpoint null boundary is inconsistent"
            )
        previous_token: str | None = None
    else:
        previous_boundary = (boundary[0], previous_event)
        previous = artifacts.get(previous_boundary)
        if previous is None:
            raise ZeroCaregiverProjectionError(
                f"repair previous checkpoint boundary has no artifact: {previous_boundary!r}"
            )
        if previous_id != previous.checkpoint_id:
            raise ZeroCaregiverProjectionError(
                "repair previous checkpoint identity does not match artifact"
            )
        previous_token = previous.token
    projected = dict(payload)
    projected["checkpoint_id"] = artifact.token
    projected["previous_latest_stable_checkpoint_id"] = previous_token
    for key in (
        "database_sha256",
        "manifest_sha256",
        "database_size_bytes",
        "checkpoint_store_bytes",
    ):
        projected[key] = BYTE_DERIVED_SENTINEL
    return projected


def _capture_new_event_evidence(
    connection: sqlite3.Connection,
    *,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    paths: OrganismPaths,
    prior: dict[int, EventPayloadEvidence],
) -> dict[int, EventPayloadEvidence]:
    result = dict(prior)
    measured_store_bytes = checkpoint_store_bytes(paths)
    for row_value in connection.execute(
        "SELECT * FROM event ORDER BY event_sequence"
    ).fetchall():
        row = dict(row_value)
        event_sequence = int(row["event_sequence"])
        event_type = str(row["event_type"])
        raw_payload = _decode_payload(row)
        raw_payload_json = _canonical_json(raw_payload)
        previous = result.get(event_sequence)
        if previous is not None:
            if previous.event_type != event_type or previous.raw_payload_json != raw_payload_json:
                raise ZeroCaregiverProjectionError(
                    f"captured event evidence changed at sequence {event_sequence}"
                )
            continue
        if event_type == "checkpoint_registration_repaired":
            projected = _validate_repair_event(
                row,
                raw_payload,
                artifacts=artifacts,
                measured_store_bytes=measured_store_bytes,
            )
            result[event_sequence] = EventPayloadEvidence(
                event_sequence=event_sequence,
                event_type=event_type,
                raw_payload_json=raw_payload_json,
                projected_payload_json=_canonical_json(projected),
            )
    return result


def _project_event_payload(
    row: dict[str, Any],
    *,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    event_evidence: dict[int, EventPayloadEvidence],
) -> dict[str, Any]:
    payload = _decode_payload(row)
    event_sequence = int(row["event_sequence"])
    event_type = str(row["event_type"])
    proof = event_evidence.get(event_sequence)
    if proof is not None:
        if proof.event_type != event_type or proof.raw_payload_json != _canonical_json(payload):
            raise ZeroCaregiverProjectionError(
                f"event evidence does not match canonical event {event_sequence}"
            )
        projected = json.loads(proof.projected_payload_json)
        if not isinstance(projected, dict):
            raise ZeroCaregiverProjectionError(
                f"projected event evidence is invalid at sequence {event_sequence}"
            )
        return projected

    projected = dict(payload)
    if "schema_version" in projected:
        projected["schema_version"] = SCHEMA_SENTINEL

    lineage_generation = int(row["lineage_generation"])
    if event_type == "checkpoint_stabilized":
        if not set(projected).issuperset({"checkpoint_id", "event_sequence"}):
            raise ZeroCaregiverProjectionError(
                "checkpoint_stabilized boundary is incomplete"
            )
        boundary = (lineage_generation, int(projected["event_sequence"]))
        artifact = artifacts.get(boundary)
        if artifact is None:
            raise ZeroCaregiverProjectionError(
                f"checkpoint_stabilized boundary has no artifact: {boundary!r}"
            )
        if projected["checkpoint_id"] != artifact.checkpoint_id:
            raise ZeroCaregiverProjectionError(
                "checkpoint_stabilized identity does not match artifact"
            )
        projected["checkpoint_id"] = artifact.token
    elif event_type == "maintenance_entered" and "checkpoint_event_sequence" in projected:
        if "checkpoint_id" not in projected:
            raise ZeroCaregiverProjectionError(
                "maintenance_entered checkpoint boundary lacks checkpoint_id"
            )
        boundary = (
            lineage_generation,
            int(projected["checkpoint_event_sequence"]),
        )
        artifact = artifacts.get(boundary)
        if artifact is None:
            raise ZeroCaregiverProjectionError(
                f"maintenance_entered boundary has no artifact: {boundary!r}"
            )
        if projected["checkpoint_id"] != artifact.checkpoint_id:
            raise ZeroCaregiverProjectionError(
                "maintenance_entered checkpoint identity does not match artifact"
            )
        projected["checkpoint_id"] = artifact.token
    return projected


def _project_table_rows(
    connection: sqlite3.Connection,
    *,
    table: str,
    order_by: str,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    event_evidence: dict[int, EventPayloadEvidence],
) -> list[dict[str, Any]]:
    projected_rows: list[dict[str, Any]] = []
    for original in _rows(connection, table, order_by):
        row = dict(original)
        if table == "organism":
            row["schema_version"] = SCHEMA_SENTINEL
            if row["latest_stable_checkpoint_id"] is not None:
                boundary = (
                    int(row["lineage_generation"]),
                    int(row["latest_stable_event_sequence"]),
                )
                artifact = artifacts.get(boundary)
                if artifact is None:
                    raise ZeroCaregiverProjectionError(
                        f"organism latest checkpoint boundary has no artifact: {boundary!r}"
                    )
                if row["latest_stable_checkpoint_id"] != artifact.checkpoint_id:
                    raise ZeroCaregiverProjectionError(
                        "organism latest checkpoint identity does not match artifact"
                    )
                row["latest_stable_checkpoint_id"] = artifact.token
        elif table == "event":
            row["schema_version"] = SCHEMA_SENTINEL
            row["payload_json"] = _project_event_payload(
                row,
                artifacts=artifacts,
                event_evidence=event_evidence,
            )
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
            if row["checkpoint_id"] != artifact.checkpoint_id:
                raise ZeroCaregiverProjectionError(
                    "registry checkpoint identity does not match artifact"
                )
            if row["database_sha256"] != artifact.database_sha256:
                raise ZeroCaregiverProjectionError(
                    "registry database digest does not match artifact"
                )
            if row["manifest_sha256"] != artifact.manifest_sha256:
                raise ZeroCaregiverProjectionError(
                    "registry manifest digest does not match artifact"
                )
            if int(row["database_size_bytes"]) != artifact.database_size_bytes:
                raise ZeroCaregiverProjectionError(
                    "registry database size does not match artifact"
                )
            row["checkpoint_id"] = artifact.token
            row["database_sha256"] = BYTE_DERIVED_SENTINEL
            row["manifest_sha256"] = BYTE_DERIVED_SENTINEL
            row["database_size_bytes"] = BYTE_DERIVED_SENTINEL
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


def _project_database_state(
    database_path: Path,
    *,
    expect_checkpoint_pending: bool,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    event_evidence: dict[int, EventPayloadEvidence],
) -> dict[str, Any]:
    connection = connect_database(database_path, read_only=True)
    try:
        try:
            validate_canonical_state(
                connection,
                expect_checkpoint_pending=expect_checkpoint_pending,
            )
        except SchemaValidationError as exc:
            raise ZeroCaregiverProjectionError(str(exc)) from exc
        tables = {
            table: _project_table_rows(
                connection,
                table=table,
                order_by=order_by,
                artifacts=artifacts,
                event_evidence=event_evidence,
            )
            for table, order_by in _ORIGINAL_TABLE_ORDER
        }
        return {
            "tables": tables,
            "sqlite_sequence": _project_original_sequences(connection),
        }
    finally:
        connection.close()


def _complete_current_artifact_evidence(
    paths: OrganismPaths,
    *,
    current: dict[tuple[int, int], CheckpointArtifactEvidence],
    all_artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    event_evidence: dict[int, EventPayloadEvidence],
) -> dict[tuple[int, int], CheckpointArtifactEvidence]:
    completed: dict[tuple[int, int], CheckpointArtifactEvidence] = {}
    for boundary, artifact in current.items():
        checkpoint_dir = paths.checkpoints / artifact.checkpoint_id
        projected = _project_database_state(
            checkpoint_dir / "organism.sqlite3",
            expect_checkpoint_pending=True,
            artifacts=all_artifacts,
            event_evidence=event_evidence,
        )
        projected_json = _canonical_json(projected)
        if (
            artifact.projected_database_state_json
            and artifact.projected_database_state_json != projected_json
        ):
            raise ZeroCaregiverProjectionError(
                f"checkpoint projected state changed for boundary: {boundary!r}"
            )
        completed[boundary] = replace(
            artifact,
            projected_database_state_json=projected_json,
        )
    return completed


def capture_zero_caregiver_evidence(
    paths: OrganismPaths,
    *,
    previous: ZeroCaregiverEvidence | None = None,
) -> ZeroCaregiverEvidence:
    """Capture cumulative validated evidence at one deterministic operation boundary."""

    if not paths.database.is_file():
        raise ZeroCaregiverProjectionError("organism database is missing")
    connection = connect_database(paths.database, read_only=True)
    try:
        try:
            validate_canonical_state(connection)
        except SchemaValidationError as exc:
            raise ZeroCaregiverProjectionError(str(exc)) from exc
        organism = connection.execute(
            "SELECT organism_id, schema_version FROM organism WHERE singleton_id=1"
        ).fetchone()
        if organism is None:
            raise ZeroCaregiverProjectionError("organism singleton is missing")
        organism_id = str(organism["organism_id"])
        if previous is not None and previous.organism_id != organism_id:
            raise ZeroCaregiverProjectionError("evidence organism identity mismatch")
        _validate_zero_caregiver_absence(
            connection,
            schema_version=int(organism["schema_version"]),
        )

        prior_artifacts = _artifact_map(previous)
        current_raw = _inventory_visible_checkpoint_artifacts(paths)
        all_artifacts = _merge_artifact_evidence(prior_artifacts, current_raw)
        prior_events = _event_evidence_map(previous)
        event_evidence = _capture_new_event_evidence(
            connection,
            artifacts=all_artifacts,
            paths=paths,
            prior=prior_events,
        )
        current_completed = _complete_current_artifact_evidence(
            paths,
            current=current_raw,
            all_artifacts=all_artifacts,
            event_evidence=event_evidence,
        )
        all_artifacts.update(current_completed)

        registry_boundaries = tuple(
            (int(row["lineage_generation"]), int(row["event_sequence"]))
            for row in connection.execute(
                "SELECT lineage_generation, event_sequence FROM checkpoint_registry "
                "ORDER BY event_sequence, checkpoint_id"
            ).fetchall()
        )
        if set(registry_boundaries) != set(current_raw):
            raise ZeroCaregiverProjectionError(
                "checkpoint registry and visible artifact boundary sets differ"
            )
        return ZeroCaregiverEvidence(
            organism_id=organism_id,
            checkpoint_artifacts=tuple(
                all_artifacts[key] for key in sorted(all_artifacts)
            ),
            event_payloads=tuple(
                event_evidence[key] for key in sorted(event_evidence)
            ),
            retained_checkpoint_boundaries=registry_boundaries,
        )
    finally:
        connection.close()


def _project_checkpoint_artifacts(
    evidence: ZeroCaregiverEvidence,
) -> list[dict[str, Any]]:
    artifacts = _artifact_map(evidence)
    projected: list[dict[str, Any]] = []
    for boundary in evidence.retained_checkpoint_boundaries:
        artifact = artifacts.get(boundary)
        if artifact is None:
            raise ZeroCaregiverProjectionError(
                f"retained checkpoint evidence is missing: {boundary!r}"
            )
        manifest = json.loads(artifact.manifest_json)
        if not isinstance(manifest, dict):
            raise ZeroCaregiverProjectionError("checkpoint manifest evidence is invalid")
        manifest["checkpoint_id"] = artifact.token
        manifest["schema_version"] = SCHEMA_SENTINEL
        manifest["database_sha256"] = BYTE_DERIVED_SENTINEL
        manifest["database_size_bytes"] = BYTE_DERIVED_SENTINEL
        database_state = json.loads(artifact.projected_database_state_json)
        projected.append(
            {
                "checkpoint": artifact.token,
                "manifest": manifest,
                "database_state": database_state,
            }
        )
    return projected


def _project_zero_caregiver_state(
    paths: OrganismPaths,
    *,
    expected_schema_version: int | None = None,
    evidence: ZeroCaregiverEvidence | None = None,
) -> dict[str, Any]:
    """Validate and project one run, optionally requiring its schema side."""

    evidence = capture_zero_caregiver_evidence(paths, previous=evidence)
    artifacts = _artifact_map(evidence)
    event_evidence = _event_evidence_map(evidence)
    connection = connect_database(paths.database, read_only=True)
    try:
        organism = connection.execute(
            "SELECT schema_version FROM organism WHERE singleton_id=1"
        ).fetchone()
        if organism is None:
            raise ZeroCaregiverProjectionError("organism singleton is missing")
        schema_version = int(organism["schema_version"])
        if (
            expected_schema_version is not None
            and schema_version != expected_schema_version
        ):
            side = "schema-v1" if expected_schema_version == 1 else "schema-v2-zero"
            raise ZeroCaregiverProjectionError(
                f"{side} control has schema version {schema_version}"
            )
        projected = _project_database_state(
            paths.database,
            expect_checkpoint_pending=False,
            artifacts=artifacts,
            event_evidence=event_evidence,
        )
        return {
            "projection_version": "phase1-projection-v2/core",
            **projected,
            "checkpoint_artifacts": _project_checkpoint_artifacts(evidence),
        }
    finally:
        connection.close()


def project_zero_caregiver_state(
    paths: OrganismPaths,
    *,
    evidence: ZeroCaregiverEvidence | None = None,
) -> dict[str, Any]:
    """Validate one run and return its closed phase1-projection-v2 state."""

    return _project_zero_caregiver_state(paths, evidence=evidence)


def assert_zero_caregiver_equivalent(
    schema_v1_paths: OrganismPaths,
    schema_v2_zero_paths: OrganismPaths,
    *,
    schema_v1_evidence: ZeroCaregiverEvidence | None = None,
    schema_v2_zero_evidence: ZeroCaregiverEvidence | None = None,
) -> None:
    """Require exact equality after independent validation and closed projection."""

    left = _project_zero_caregiver_state(
        schema_v1_paths,
        expected_schema_version=1,
        evidence=schema_v1_evidence,
    )
    right = _project_zero_caregiver_state(
        schema_v2_zero_paths,
        expected_schema_version=PHASE2_SCHEMA_VERSION,
        evidence=schema_v2_zero_evidence,
    )
    if left != right:
        raise ZeroCaregiverProjectionError("projected canonical state differs")
