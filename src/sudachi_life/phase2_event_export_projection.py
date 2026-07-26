"""Validated semantic projection for deterministic noncanonical event exports."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Final

from .event_export import (
    EVENT_EXPORT_FORMAT,
    EVENT_EXPORT_FORMAT_VERSION,
    _canonical_json_line,
    _read_export_bytes,
)
from .paths import OrganismPaths
from .phase2_projection import SCHEMA_SENTINEL, ZeroCaregiverProjectionError
from .phase2_rollback_projection import (
    ZeroCaregiverRollbackEvidence,
    project_zero_caregiver_rollback_state,
)
from .phase2_schema import PHASE2_SCHEMA_VERSION
from .storage import connect_database

_MANIFEST_KEYS: Final[frozenset[str]] = frozenset(
    {
        "record_type",
        "organism_id",
        "lineage_generation",
        "source_checkpoint_id",
        "first_event_sequence",
        "last_event_sequence",
        "event_count",
        "export_format",
        "export_format_version",
        "contract_version",
        "schema_version",
        "environment_version",
        "budget_config_version",
    }
)
_EVENT_KEYS: Final[frozenset[str]] = frozenset(
    {
        "record_type",
        "event_sequence",
        "organism_id",
        "lineage_generation",
        "lifecycle_number",
        "wall_time_utc_us",
        "event_type",
        "source",
        "payload",
        "schema_version",
        "environment_version",
        "budget_config_version",
    }
)


@dataclass(frozen=True)
class ZeroCaregiverEventExportEvidence:
    """One independently validated raw export and its closed semantic projection."""

    organism_id: str
    lineage_generation: int
    source_checkpoint_id: str
    source_checkpoint_lineage_generation: int
    source_checkpoint_event_sequence: int
    export_path: str
    export_size_bytes: int
    export_sha256: str
    raw_records_json: str
    projected_manifest_json: str
    projected_events_json: str


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _strict_int(value: object, *, context: str) -> int:
    if type(value) is not int:
        raise ZeroCaregiverProjectionError(f"{context} is not an integer")
    return value


def _parse_canonical_jsonl(path: Path) -> tuple[bytes, list[dict[str, Any]]]:
    if path.is_symlink() or not path.is_file():
        raise ZeroCaregiverProjectionError("event export path is missing or unsafe")
    raw = path.read_bytes()
    if not raw or not raw.endswith(b"\n"):
        raise ZeroCaregiverProjectionError("event export is not complete canonical JSONL")
    records: list[dict[str, Any]] = []
    for line in raw.splitlines(keepends=True):
        try:
            value = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ZeroCaregiverProjectionError(
                "event export line is not valid UTF-8 JSON"
            ) from exc
        if not isinstance(value, dict):
            raise ZeroCaregiverProjectionError("event export record is not an object")
        if _canonical_json_line(value) != line:
            raise ZeroCaregiverProjectionError(
                "event export line is not canonical JSONL"
            )
        records.append(value)
    return raw, records


def _validate_record_structure(records: list[dict[str, Any]]) -> dict[str, Any]:
    if len(records) < 2:
        raise ZeroCaregiverProjectionError(
            "event export requires one manifest and at least one event"
        )
    manifest = records[0]
    if set(manifest) != _MANIFEST_KEYS:
        raise ZeroCaregiverProjectionError("event export manifest keys are not exact")
    if manifest.get("record_type") != "manifest":
        raise ZeroCaregiverProjectionError("event export first record is not the manifest")
    if manifest.get("export_format") != EVENT_EXPORT_FORMAT:
        raise ZeroCaregiverProjectionError("event export format changed")
    if manifest.get("export_format_version") != EVENT_EXPORT_FORMAT_VERSION:
        raise ZeroCaregiverProjectionError("event export format version changed")

    first_sequence = _strict_int(
        manifest.get("first_event_sequence"),
        context="event export first sequence",
    )
    last_sequence = _strict_int(
        manifest.get("last_event_sequence"),
        context="event export last sequence",
    )
    event_count = _strict_int(
        manifest.get("event_count"),
        context="event export count",
    )
    if first_sequence != 1 or last_sequence < first_sequence:
        raise ZeroCaregiverProjectionError("event export range is invalid")
    if event_count != last_sequence or event_count != len(records) - 1:
        raise ZeroCaregiverProjectionError("event export count does not match its range")

    expected_sequences = list(range(first_sequence, last_sequence + 1))
    actual_sequences: list[int] = []
    organism_id = manifest.get("organism_id")
    for record in records[1:]:
        if set(record) != _EVENT_KEYS:
            raise ZeroCaregiverProjectionError("event export event keys are not exact")
        if record.get("record_type") != "event":
            raise ZeroCaregiverProjectionError("event export contains a non-event record")
        if record.get("organism_id") != organism_id:
            raise ZeroCaregiverProjectionError(
                "event export contains a foreign organism identifier"
            )
        if not isinstance(record.get("payload"), dict):
            raise ZeroCaregiverProjectionError("event export payload is not an object")
        actual_sequences.append(
            _strict_int(
                record.get("event_sequence"),
                context="event export event sequence",
            )
        )
    if actual_sequences != expected_sequences:
        raise ZeroCaregiverProjectionError(
            "event export sequence order or completeness changed"
        )
    return manifest


def _source_checkpoint_artifact(
    projection_evidence: ZeroCaregiverRollbackEvidence,
    *,
    raw_checkpoint_id: object,
    lineage_generation: int,
    event_sequence: int,
):
    matches = [
        artifact
        for artifact in projection_evidence.retention.core.checkpoint_artifacts
        if artifact.checkpoint_id == raw_checkpoint_id
        and artifact.lineage_generation == lineage_generation
        and artifact.event_sequence == event_sequence
    ]
    if len(matches) != 1:
        raise ZeroCaregiverProjectionError(
            "event export source checkpoint does not resolve to one validated artifact"
        )
    if (lineage_generation, event_sequence) not in set(
        projection_evidence.retention.core.retained_checkpoint_boundaries
    ):
        raise ZeroCaregiverProjectionError(
            "event export source checkpoint is not in the active registry evidence"
        )
    return matches[0]


def _project_records(
    paths: OrganismPaths,
    *,
    records: list[dict[str, Any]],
    projection_evidence: ZeroCaregiverRollbackEvidence,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = records[0]
    lineage_generation = _strict_int(
        manifest.get("lineage_generation"),
        context="event export lineage",
    )
    last_sequence = _strict_int(
        manifest.get("last_event_sequence"),
        context="event export last sequence",
    )
    checkpoint = _source_checkpoint_artifact(
        projection_evidence,
        raw_checkpoint_id=manifest.get("source_checkpoint_id"),
        lineage_generation=lineage_generation,
        event_sequence=last_sequence,
    )

    projected_state = project_zero_caregiver_rollback_state(
        paths,
        evidence=projection_evidence,
    )
    event_rows = {
        int(row["event_sequence"]): row
        for row in projected_state["tables"]["event"]
        if int(row["event_sequence"]) <= last_sequence
    }
    if set(event_rows) != set(range(1, last_sequence + 1)):
        raise ZeroCaregiverProjectionError(
            "projected canonical event range differs from the export"
        )

    projected_manifest = dict(manifest)
    projected_manifest["source_checkpoint_id"] = checkpoint.token
    projected_manifest["schema_version"] = SCHEMA_SENTINEL

    projected_events: list[dict[str, Any]] = []
    for record in records[1:]:
        sequence = int(record["event_sequence"])
        row = event_rows[sequence]
        for export_key, database_key in (
            ("organism_id", "organism_id"),
            ("lineage_generation", "lineage_generation"),
            ("lifecycle_number", "lifecycle_number"),
            ("wall_time_utc_us", "wall_time_utc_us"),
            ("event_type", "event_type"),
            ("source", "source"),
            ("environment_version", "environment_version"),
            ("budget_config_version", "budget_config_version"),
        ):
            if record[export_key] != row[database_key]:
                raise ZeroCaregiverProjectionError(
                    f"event export {export_key} differs from projected canonical event"
                )
        projected = dict(record)
        projected["payload"] = row["payload_json"]
        projected["schema_version"] = row["schema_version"]
        projected_events.append(projected)
    return projected_manifest, projected_events


def capture_zero_caregiver_event_export_evidence(
    paths: OrganismPaths,
    export_path: Path | str,
    *,
    projection_evidence: ZeroCaregiverRollbackEvidence,
) -> ZeroCaregiverEventExportEvidence:
    """Validate one raw export completely before creating semantic evidence."""

    path = Path(export_path)
    raw, records = _parse_canonical_jsonl(path)
    manifest = _validate_record_structure(records)
    last_sequence = int(manifest["last_event_sequence"])
    try:
        expected_bytes, metadata = _read_export_bytes(paths, last_sequence)
    except Exception as exc:
        raise ZeroCaregiverProjectionError(str(exc)) from exc
    if raw != expected_bytes:
        raise ZeroCaregiverProjectionError(
            "event export bytes do not match canonical reconstruction"
        )
    for key in (
        "organism_id",
        "lineage_generation",
        "source_checkpoint_id",
        "first_event_sequence",
        "last_event_sequence",
        "event_count",
        "export_format",
        "export_format_version",
    ):
        if manifest[key] != metadata[key]:
            raise ZeroCaregiverProjectionError(
                f"event export manifest {key} differs from canonical reconstruction"
            )

    projected_manifest, projected_events = _project_records(
        paths,
        records=records,
        projection_evidence=projection_evidence,
    )
    return ZeroCaregiverEventExportEvidence(
        organism_id=str(manifest["organism_id"]),
        lineage_generation=int(manifest["lineage_generation"]),
        source_checkpoint_id=str(manifest["source_checkpoint_id"]),
        source_checkpoint_lineage_generation=int(manifest["lineage_generation"]),
        source_checkpoint_event_sequence=last_sequence,
        export_path=str(path),
        export_size_bytes=len(raw),
        export_sha256=hashlib.sha256(raw).hexdigest(),
        raw_records_json=_canonical_json(records),
        projected_manifest_json=_canonical_json(projected_manifest),
        projected_events_json=_canonical_json(projected_events),
    )


def _recapture(
    paths: OrganismPaths,
    evidence: ZeroCaregiverEventExportEvidence,
    *,
    projection_evidence: ZeroCaregiverRollbackEvidence,
) -> ZeroCaregiverEventExportEvidence:
    current = capture_zero_caregiver_event_export_evidence(
        paths,
        evidence.export_path,
        projection_evidence=projection_evidence,
    )
    if current != evidence:
        raise ZeroCaregiverProjectionError(
            "event export evidence changed after capture"
        )
    return current


def _require_schema(paths: OrganismPaths, expected_schema_version: int) -> None:
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT schema_version FROM organism WHERE singleton_id=1"
        ).fetchone()
    finally:
        connection.close()
    actual = None if row is None else int(row["schema_version"])
    if actual != expected_schema_version:
        side = "schema-v1" if expected_schema_version == 1 else "schema-v2-zero"
        raise ZeroCaregiverProjectionError(
            f"{side} control has schema version {actual}"
        )


def project_zero_caregiver_event_export(
    paths: OrganismPaths,
    evidence: ZeroCaregiverEventExportEvidence,
    *,
    projection_evidence: ZeroCaregiverRollbackEvidence,
) -> dict[str, Any]:
    """Return canonical event semantics while excluding presentation-only bytes."""

    current = _recapture(
        paths,
        evidence,
        projection_evidence=projection_evidence,
    )
    manifest = json.loads(current.projected_manifest_json)
    events = json.loads(current.projected_events_json)
    if not isinstance(manifest, dict) or not isinstance(events, list):
        raise ZeroCaregiverProjectionError(
            "event export projected evidence is invalid"
        )
    return {
        "projection_version": "phase1-projection-v2/event-export",
        "manifest": manifest,
        "events": events,
    }


def assert_zero_caregiver_event_exports_equivalent(
    schema_v1_paths: OrganismPaths,
    schema_v2_zero_paths: OrganismPaths,
    schema_v1_export_evidence: ZeroCaregiverEventExportEvidence,
    schema_v2_zero_export_evidence: ZeroCaregiverEventExportEvidence,
    *,
    schema_v1_projection_evidence: ZeroCaregiverRollbackEvidence,
    schema_v2_zero_projection_evidence: ZeroCaregiverRollbackEvidence,
) -> None:
    """Require exact semantic equality after independent raw-file validation."""

    _require_schema(schema_v1_paths, 1)
    _require_schema(schema_v2_zero_paths, PHASE2_SCHEMA_VERSION)
    left = project_zero_caregiver_event_export(
        schema_v1_paths,
        schema_v1_export_evidence,
        projection_evidence=schema_v1_projection_evidence,
    )
    right = project_zero_caregiver_event_export(
        schema_v2_zero_paths,
        schema_v2_zero_export_evidence,
        projection_evidence=schema_v2_zero_projection_evidence,
    )
    if left != right:
        raise ZeroCaregiverProjectionError(
            "event-export projected semantics differ"
        )


__all__ = [
    "SCHEMA_SENTINEL",
    "ZeroCaregiverEventExportEvidence",
    "ZeroCaregiverProjectionError",
    "assert_zero_caregiver_event_exports_equivalent",
    "capture_zero_caregiver_event_export_evidence",
    "project_zero_caregiver_event_export",
]
