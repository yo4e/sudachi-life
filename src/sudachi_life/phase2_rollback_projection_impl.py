"""Closed rollback artifact-graph extension for phase1-projection-v2."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import sqlite3
from typing import Any, Final, Iterable

from .errors import CheckpointError, SchemaValidationError
from .paths import OrganismPaths
from .phase2_projection import (
    BYTE_DERIVED_SENTINEL,
    SCHEMA_SENTINEL,
    CheckpointArtifactEvidence,
    EventPayloadEvidence,
    ZeroCaregiverEvidence,
    ZeroCaregiverProjectionError,
    _artifact_map as _core_artifact_map,
    _capture_new_event_evidence,
    _canonical_json,
    _complete_current_artifact_evidence,
    _inventory_visible_checkpoint_artifacts,
    _merge_artifact_evidence,
    _project_checkpoint_artifacts,
    _project_database_state,
    _validate_zero_caregiver_absence,
)
from .phase2_retention_projection import (
    ZeroCaregiverRetentionEvidence,
    _apply_event_projection as _apply_retention_event_projection,
    _capture_events as _capture_retention_events,
    _inventory_current_staging,
    _merge_staging,
    _staging_map,
)
from .phase2_schema import PHASE2_SCHEMA_VERSION
from .rollback import RollbackArchiveError, _sha256_file, _validate_archive_directory
from .rollback_candidate import RestoreCandidateError, _validate_candidate_directory
from .rollback_replace import (
    ActiveReplacementRejectedError,
    _read_manifest,
    _validate_artifact_chain,
)
from .rollback_transform import CandidateTransformError
from .runtime_storage import checkpoint_store_bytes
from .storage import connect_database, validate_canonical_state

_ROLLBACK_STARTED: Final = "rollback_started"
_ROLLBACK_PREPARED: Final = "rollback_lineage_prepared"
_ROLLBACK_COMPLETED: Final = "rollback_completed"

_STARTED_KEYS: Final[frozenset[str]] = frozenset(
    {
        "archive_database_sha256",
        "archive_id",
        "archive_manifest_sha256",
        "latest_stable_checkpoint_id",
        "latest_stable_event_sequence",
        "pre_rollback_event_sequence",
        "pre_rollback_lifecycle_number",
        "pre_rollback_lineage_generation",
        "pre_rollback_status",
        "selected_checkpoint_database_sha256",
        "selected_checkpoint_event_sequence",
        "selected_checkpoint_id",
        "selected_checkpoint_lineage_generation",
        "selected_checkpoint_manifest_sha256",
    }
)
_PREPARED_KEYS: Final[frozenset[str]] = frozenset(
    {
        "administrative_reason",
        "archive_database_sha256",
        "archive_id",
        "archive_manifest_sha256",
        "abandoned_event_sequence",
        "abandoned_lifecycle_number",
        "abandoned_lineage_generation",
        "new_lineage_generation",
        "rollback_started_event_sequence",
        "selected_checkpoint_database_sha256",
        "selected_checkpoint_event_sequence",
        "selected_checkpoint_id",
        "selected_checkpoint_lineage_generation",
        "selected_checkpoint_manifest_sha256",
        "source_restore_candidate_database_sha256",
        "source_restore_candidate_id",
        "source_restore_candidate_manifest_sha256",
        "status_after",
    }
)
_COMPLETED_KEYS: Final[frozenset[str]] = frozenset(
    {
        "administrative_reason",
        "archive_database_sha256",
        "archive_id",
        "archive_manifest_sha256",
        "abandoned_event_sequence",
        "abandoned_lifecycle_number",
        "abandoned_lineage_generation",
        "completion_event_sequence",
        "consecutive_failures_after",
        "consecutive_failures_before",
        "implementation_version",
        "maintenance_reason_before",
        "new_lineage_generation",
        "queued_input_events_preserved",
        "replacement_validated",
        "restoration_event_sequence",
        "rollback_started_event_sequence",
        "selected_checkpoint_database_sha256",
        "selected_checkpoint_event_sequence",
        "selected_checkpoint_id",
        "selected_checkpoint_lineage_generation",
        "selected_checkpoint_manifest_sha256",
        "source_lifecycle_number",
        "source_restore_candidate_database_sha256",
        "source_restore_candidate_id",
        "source_restore_candidate_manifest_sha256",
        "status_after",
        "status_before",
        "transformed_candidate_database_sha256",
        "transformed_candidate_id",
        "transformed_candidate_manifest_sha256",
    }
)


def _artifact_size(path: Path) -> int:
    return sum(
        item.stat().st_size
        for item in path.rglob("*")
        if item.is_file() and not item.is_symlink()
    )


def _read_json_object(path: Path, *, context: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ZeroCaregiverProjectionError(f"{context} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ZeroCaregiverProjectionError(f"{context} is not an object")
    return value


def _strict_int(value: object, *, context: str) -> int:
    if type(value) is not int:
        raise ZeroCaregiverProjectionError(f"{context} is not an integer")
    return value


def _checkpoint_token(lineage_generation: int, event_sequence: int) -> str:
    return f"CP({lineage_generation},{event_sequence})"


def _archive_token(lineage: int, abandoned_event: int, selected_event: int) -> str:
    return f"RA({lineage},{abandoned_event},{selected_event})"


def _source_candidate_token(lineage: int, rollback_event: int, selected_event: int) -> str:
    return f"RC({lineage},{rollback_event},{selected_event})"


def _transformed_candidate_token(new_lineage: int, restoration_event: int) -> str:
    return f"TC({new_lineage},{restoration_event})"


@dataclass(frozen=True)
class RollbackArchiveEvidence:
    lineage_generation: int
    abandoned_event_sequence: int
    selected_event_sequence: int
    archive_id: str
    manifest_sha256: str
    database_sha256: str
    database_size_bytes: int
    artifact_size_bytes: int
    manifest_json: str
    projected_database_state_json: str

    @property
    def semantic_key(self) -> tuple[int, int, int]:
        return (
            self.lineage_generation,
            self.abandoned_event_sequence,
            self.selected_event_sequence,
        )

    @property
    def token(self) -> str:
        return _archive_token(*self.semantic_key)


@dataclass(frozen=True)
class RestoreCandidateEvidence:
    abandoned_lineage_generation: int
    rollback_started_event_sequence: int
    selected_event_sequence: int
    candidate_id: str
    manifest_sha256: str
    database_sha256: str
    database_size_bytes: int
    artifact_size_bytes: int
    manifest_json: str
    projected_database_state_json: str

    @property
    def semantic_key(self) -> tuple[int, int, int]:
        return (
            self.abandoned_lineage_generation,
            self.rollback_started_event_sequence,
            self.selected_event_sequence,
        )

    @property
    def token(self) -> str:
        return _source_candidate_token(*self.semantic_key)


@dataclass(frozen=True)
class TransformedCandidateEvidence:
    new_lineage_generation: int
    restoration_event_sequence: int
    transformed_candidate_id: str
    manifest_sha256: str
    database_sha256: str
    database_size_bytes: int
    artifact_size_bytes: int
    manifest_json: str
    projected_database_state_json: str

    @property
    def semantic_key(self) -> tuple[int, int]:
        return (self.new_lineage_generation, self.restoration_event_sequence)

    @property
    def token(self) -> str:
        return _transformed_candidate_token(*self.semantic_key)


@dataclass(frozen=True)
class RollbackEventEvidence:
    lineage_generation: int
    event_sequence: int
    event_type: str
    raw_row_json: str
    projected_row_json: str

    @property
    def semantic_key(self) -> tuple[int, int, str]:
        return (self.lineage_generation, self.event_sequence, self.event_type)


@dataclass(frozen=True)
class ZeroCaregiverRollbackEvidence:
    retention: ZeroCaregiverRetentionEvidence
    rollback_archives: tuple[RollbackArchiveEvidence, ...]
    restore_candidates: tuple[RestoreCandidateEvidence, ...]
    transformed_candidates: tuple[TransformedCandidateEvidence, ...]
    rollback_events: tuple[RollbackEventEvidence, ...]


def _map_items(items: Iterable[Any], *, context: str) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for item in items:
        key = item.semantic_key
        if key in result:
            raise ZeroCaregiverProjectionError(f"duplicate {context}: {key!r}")
        result[key] = item
    return result


def _archive_map(evidence: ZeroCaregiverRollbackEvidence | None) -> dict[Any, Any]:
    return {} if evidence is None else _map_items(
        evidence.rollback_archives,
        context="rollback archive evidence",
    )


def _source_map(evidence: ZeroCaregiverRollbackEvidence | None) -> dict[Any, Any]:
    return {} if evidence is None else _map_items(
        evidence.restore_candidates,
        context="source candidate evidence",
    )


def _transformed_map(evidence: ZeroCaregiverRollbackEvidence | None) -> dict[Any, Any]:
    return {} if evidence is None else _map_items(
        evidence.transformed_candidates,
        context="transformed candidate evidence",
    )


def _rollback_event_map(evidence: ZeroCaregiverRollbackEvidence | None) -> dict[Any, Any]:
    return {} if evidence is None else _map_items(
        evidence.rollback_events,
        context="rollback event evidence",
    )


def _merge_immutable(
    prior: dict[Any, Any],
    current: dict[Any, Any],
    *,
    context: str,
) -> dict[Any, Any]:
    merged = dict(prior)
    for key, item in current.items():
        previous = merged.get(key)
        if previous is not None:
            comparable_previous = replace(previous, projected_database_state_json="")
            comparable_current = replace(item, projected_database_state_json="")
            if comparable_previous != comparable_current:
                raise ZeroCaregiverProjectionError(f"{context} changed: {key!r}")
            if previous.projected_database_state_json:
                item = replace(
                    item,
                    projected_database_state_json=previous.projected_database_state_json,
                )
        merged[key] = item
    missing = set(prior) - set(current)
    if missing:
        raise ZeroCaregiverProjectionError(
            f"{context} disappeared despite Phase 1 evidence retention: {sorted(missing)!r}"
        )
    return merged


def _capture_core_with_preserved_artifacts(
    paths: OrganismPaths,
    *,
    previous: ZeroCaregiverEvidence | None,
) -> ZeroCaregiverEvidence:
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
        current_raw = _inventory_visible_checkpoint_artifacts(paths)
        all_artifacts = _merge_artifact_evidence(
            _core_artifact_map(previous),
            current_raw,
        )
        event_evidence = _capture_new_event_evidence(
            connection,
            artifacts=all_artifacts,
            paths=paths,
            prior={},
        )
        all_artifacts.update(
            _complete_current_artifact_evidence(
                paths,
                current=current_raw,
                all_artifacts=all_artifacts,
                event_evidence=event_evidence,
            )
        )
        registry_boundaries = tuple(
            (int(row["lineage_generation"]), int(row["event_sequence"]))
            for row in connection.execute(
                "SELECT lineage_generation, event_sequence FROM checkpoint_registry "
                "ORDER BY event_sequence, checkpoint_id"
            )
        )
        if not set(registry_boundaries).issubset(set(current_raw)):
            raise ZeroCaregiverProjectionError(
                "active checkpoint registry is not backed by visible artifacts"
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


def _capture_retention_with_preserved_artifacts(
    paths: OrganismPaths,
    *,
    previous: ZeroCaregiverRetentionEvidence | None,
) -> ZeroCaregiverRetentionEvidence:
    core = _capture_core_with_preserved_artifacts(
        paths,
        previous=previous.core if previous is not None else None,
    )
    artifacts = _core_artifact_map(core)
    current_staging, current_order = _inventory_current_staging(
        paths,
        artifacts=artifacts,
    )
    all_staging = _merge_staging(_staging_map(previous), current_staging)
    connection = connect_database(paths.database, read_only=True)
    try:
        registry_rows = connection.execute(
            "SELECT checkpoint_id, lineage_generation, event_sequence "
            "FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"
        ).fetchall()
        registry_boundaries = tuple(
            (int(row["lineage_generation"]), int(row["event_sequence"]))
            for row in registry_rows
        )
        events = _capture_retention_events(
            connection,
            artifacts=artifacts,
            all_staging=all_staging,
            current_staging=current_staging,
            registry_boundaries=registry_boundaries,
            registry_event_sequences=[int(row["event_sequence"]) for row in registry_rows],
            measured_store_bytes=checkpoint_store_bytes(paths),
            prior={},
        )
    finally:
        connection.close()
    return ZeroCaregiverRetentionEvidence(
        core=core,
        staging_artifacts=tuple(all_staging[key] for key in sorted(all_staging)),
        event_payloads=tuple(events[key] for key in sorted(events)),
        current_staging_boundaries=current_order,
    )


def _inventory_archives(paths: OrganismPaths) -> dict[Any, RollbackArchiveEvidence]:
    root = paths.rollback_archives
    if not root.exists():
        return {}
    if not root.is_dir() or root.is_symlink():
        raise ZeroCaregiverProjectionError("rollback archive root is missing or unsafe")
    result: dict[Any, RollbackArchiveEvidence] = {}
    for directory in sorted(root.iterdir(), key=lambda item: item.name):
        if directory.name.startswith("."):
            continue
        if directory.is_symlink() or not directory.is_dir():
            raise ZeroCaregiverProjectionError("rollback archive root has an unsafe entry")
        try:
            manifest = _validate_archive_directory(directory)
        except RollbackArchiveError as exc:
            raise ZeroCaregiverProjectionError(str(exc)) from exc
        key = (
            _strict_int(manifest.get("active_lineage_generation"), context="archive lineage"),
            _strict_int(manifest.get("active_event_sequence"), context="archive event"),
            _strict_int(
                manifest.get("selected_checkpoint_event_sequence"),
                context="archive selected event",
            ),
        )
        if key in result:
            raise ZeroCaregiverProjectionError(
                f"duplicate rollback archive semantic identity: {key!r}"
            )
        result[key] = RollbackArchiveEvidence(
            lineage_generation=key[0],
            abandoned_event_sequence=key[1],
            selected_event_sequence=key[2],
            archive_id=str(manifest["archive_id"]),
            manifest_sha256=_sha256_file(directory / "manifest.json"),
            database_sha256=_sha256_file(directory / "organism.sqlite3"),
            database_size_bytes=(directory / "organism.sqlite3").stat().st_size,
            artifact_size_bytes=_artifact_size(directory),
            manifest_json=_canonical_json(manifest),
            projected_database_state_json="",
        )
    return result


def _candidate_manifests(paths: OrganismPaths) -> Iterable[tuple[Path, dict[str, Any]]]:
    root = paths.restore_candidates
    if not root.exists():
        return ()
    if not root.is_dir() or root.is_symlink():
        raise ZeroCaregiverProjectionError("restore candidate root is missing or unsafe")
    items: list[tuple[Path, dict[str, Any]]] = []
    for directory in sorted(root.iterdir(), key=lambda item: item.name):
        if directory.name.startswith("."):
            continue
        if directory.is_symlink() or not directory.is_dir():
            raise ZeroCaregiverProjectionError("restore candidate root has an unsafe entry")
        if {entry.name for entry in directory.iterdir()} != {
            "organism.sqlite3",
            "manifest.json",
        }:
            raise ZeroCaregiverProjectionError("rollback candidate has unexpected entries")
        items.append(
            (
                directory,
                _read_json_object(
                    directory / "manifest.json",
                    context="rollback candidate manifest",
                ),
            )
        )
    return items


def _inventory_candidates(
    paths: OrganismPaths,
    *,
    checkpoint_artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
) -> tuple[dict[Any, RestoreCandidateEvidence], dict[Any, TransformedCandidateEvidence]]:
    sources: dict[Any, RestoreCandidateEvidence] = {}
    transformed: dict[Any, TransformedCandidateEvidence] = {}
    active = connect_database(paths.database, read_only=True)
    try:
        for directory, manifest in _candidate_manifests(paths):
            provenance = manifest.get("provenance")
            if provenance == "restore_candidate":
                boundary = (
                    _strict_int(
                        manifest.get("source_lineage_generation"),
                        context="source candidate lineage",
                    ),
                    _strict_int(
                        manifest.get("source_event_sequence"),
                        context="source candidate event",
                    ),
                )
                checkpoint = checkpoint_artifacts.get(boundary)
                if checkpoint is None:
                    raise ZeroCaregiverProjectionError(
                        f"source candidate has no checkpoint evidence: {boundary!r}"
                    )
                try:
                    validated = _validate_candidate_directory(
                        directory,
                        source_checkpoint_dir=paths.checkpoints / checkpoint.checkpoint_id,
                    )
                except RestoreCandidateError as exc:
                    raise ZeroCaregiverProjectionError(str(exc)) from exc
                key = (
                    int(validated["active_lineage_generation"]),
                    int(validated["rollback_started_event_sequence"]),
                    boundary[1],
                )
                sources[key] = RestoreCandidateEvidence(
                    abandoned_lineage_generation=key[0],
                    rollback_started_event_sequence=key[1],
                    selected_event_sequence=key[2],
                    candidate_id=str(validated["candidate_id"]),
                    manifest_sha256=_sha256_file(directory / "manifest.json"),
                    database_sha256=_sha256_file(directory / "organism.sqlite3"),
                    database_size_bytes=(directory / "organism.sqlite3").stat().st_size,
                    artifact_size_bytes=_artifact_size(directory),
                    manifest_json=_canonical_json(validated),
                    projected_database_state_json="",
                )
            elif provenance == "rollback_transformed_candidate":
                transformed_id = str(manifest.get("transformed_candidate_id"))
                try:
                    candidate_dir, read_manifest = _read_manifest(paths, transformed_id)
                    context = _validate_artifact_chain(
                        paths,
                        active,
                        candidate_dir,
                        read_manifest,
                    )
                except (
                    ActiveReplacementRejectedError,
                    CandidateTransformError,
                    RestoreCandidateError,
                    RollbackArchiveError,
                    CheckpointError,
                    SchemaValidationError,
                ) as exc:
                    raise ZeroCaregiverProjectionError(str(exc)) from exc
                key = (
                    int(context.manifest["new_lineage_generation"]),
                    int(context.manifest["restoration_event_sequence"]),
                )
                transformed[key] = TransformedCandidateEvidence(
                    new_lineage_generation=key[0],
                    restoration_event_sequence=key[1],
                    transformed_candidate_id=transformed_id,
                    manifest_sha256=context.manifest_sha256,
                    database_sha256=context.database_sha256,
                    database_size_bytes=(candidate_dir / "organism.sqlite3").stat().st_size,
                    artifact_size_bytes=_artifact_size(candidate_dir),
                    manifest_json=_canonical_json(context.manifest),
                    projected_database_state_json="",
                )
            else:
                raise ZeroCaregiverProjectionError(
                    f"unknown rollback candidate provenance: {provenance!r}"
                )
    finally:
        active.close()
    return sources, transformed


def _validate_preserved_checkpoint_artifacts(
    paths: OrganismPaths,
    *,
    core: ZeroCaregiverEvidence,
    archives: dict[Any, RollbackArchiveEvidence],
) -> None:
    artifacts = _core_artifact_map(core)
    extras = set(artifacts) - set(core.retained_checkpoint_boundaries)
    if not extras:
        return
    archived_rows: dict[tuple[int, int], list[sqlite3.Row]] = {}
    for archive in archives.values():
        connection = connect_database(
            paths.rollback_archives / archive.archive_id / "organism.sqlite3",
            read_only=True,
        )
        try:
            rows = connection.execute(
                "SELECT * FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"
            ).fetchall()
        finally:
            connection.close()
        for row in rows:
            boundary = (int(row["lineage_generation"]), int(row["event_sequence"]))
            archived_rows.setdefault(boundary, []).append(row)
    for boundary in sorted(extras):
        artifact = artifacts[boundary]
        if not any(
            row["checkpoint_id"] == artifact.checkpoint_id
            and row["manifest_sha256"] == artifact.manifest_sha256
            and row["database_sha256"] == artifact.database_sha256
            and int(row["database_size_bytes"]) == artifact.database_size_bytes
            for row in archived_rows.get(boundary, [])
        ):
            raise ZeroCaregiverProjectionError(
                "unregistered visible checkpoint is not preserved by a rollback archive: "
                f"{boundary!r}"
            )


def _require_checkpoint(
    artifacts: dict[Any, CheckpointArtifactEvidence],
    boundary: tuple[int, int],
    raw_id: object,
    *,
    context: str,
) -> CheckpointArtifactEvidence:
    artifact = artifacts.get(boundary)
    if artifact is None:
        raise ZeroCaregiverProjectionError(
            f"{context} has no checkpoint evidence: {boundary!r}"
        )
    if raw_id != artifact.checkpoint_id:
        raise ZeroCaregiverProjectionError(
            f"{context} identity does not match checkpoint evidence"
        )
    return artifact


def _require_archive(archives: dict[Any, Any], key: Any, raw_id: object, *, context: str):
    artifact = archives.get(key)
    if artifact is None:
        raise ZeroCaregiverProjectionError(f"{context} has no archive evidence: {key!r}")
    if raw_id != artifact.archive_id:
        raise ZeroCaregiverProjectionError(f"{context} identity does not match archive evidence")
    return artifact


def _require_source(sources: dict[Any, Any], key: Any, raw_id: object, *, context: str):
    artifact = sources.get(key)
    if artifact is None:
        raise ZeroCaregiverProjectionError(
            f"{context} has no source candidate evidence: {key!r}"
        )
    if raw_id != artifact.candidate_id:
        raise ZeroCaregiverProjectionError(
            f"{context} identity does not match source candidate evidence"
        )
    return artifact


def _require_transformed(
    transformed: dict[Any, Any],
    key: Any,
    raw_id: object | None,
    *,
    context: str,
):
    artifact = transformed.get(key)
    if artifact is None:
        raise ZeroCaregiverProjectionError(
            f"{context} has no transformed candidate evidence: {key!r}"
        )
    if raw_id is not None and raw_id != artifact.transformed_candidate_id:
        raise ZeroCaregiverProjectionError(
            f"{context} identity does not match transformed candidate evidence"
        )
    return artifact


def _event_row_dict(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    try:
        payload = json.loads(str(result["payload_json"]))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ZeroCaregiverProjectionError(
            f"{result.get('event_type')} payload is not valid JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise ZeroCaregiverProjectionError(
            f"{result.get('event_type')} payload is not an object"
        )
    result["payload_json"] = payload
    return result


def _validate_event_columns(row: dict[str, Any], *, event_type: str) -> None:
    source = (
        "administration:rollback-candidate"
        if event_type == _ROLLBACK_PREPARED
        else "administration:rollback"
    )
    if row.get("event_type") != event_type or row.get("source") != source:
        raise ZeroCaregiverProjectionError(
            f"{event_type} event authority columns are invalid"
        )


def _validate_started(row, *, artifacts, archives) -> dict[str, Any]:
    payload = row["payload_json"]
    if set(payload) != _STARTED_KEYS:
        raise ZeroCaregiverProjectionError("rollback_started payload keys are not exact")
    lineage = _strict_int(
        payload.get("pre_rollback_lineage_generation"),
        context="rollback_started abandoned lineage",
    )
    abandoned = _strict_int(
        payload.get("pre_rollback_event_sequence"),
        context="rollback_started abandoned event",
    )
    selected_event = _strict_int(
        payload.get("selected_checkpoint_event_sequence"),
        context="rollback_started selected event",
    )
    if int(row["lineage_generation"]) != lineage or int(row["event_sequence"]) != abandoned + 1:
        raise ZeroCaregiverProjectionError("rollback_started event boundary is invalid")
    latest = _require_checkpoint(
        artifacts,
        (lineage, int(payload["latest_stable_event_sequence"])),
        payload.get("latest_stable_checkpoint_id"),
        context="rollback_started latest checkpoint",
    )
    selected = _require_checkpoint(
        artifacts,
        (int(payload["selected_checkpoint_lineage_generation"]), selected_event),
        payload.get("selected_checkpoint_id"),
        context="rollback_started selected checkpoint",
    )
    archive = _require_archive(
        archives,
        (lineage, abandoned, selected_event),
        payload.get("archive_id"),
        context="rollback_started archive",
    )
    checks = {
        "archive_database_sha256": archive.database_sha256,
        "archive_manifest_sha256": archive.manifest_sha256,
        "selected_checkpoint_database_sha256": selected.database_sha256,
        "selected_checkpoint_manifest_sha256": selected.manifest_sha256,
    }
    for key, expected in checks.items():
        if payload.get(key) != expected:
            if key == "archive_database_sha256":
                raise ZeroCaregiverProjectionError(
                    "rollback_started archive database digest does not match archive"
                )
            raise ZeroCaregiverProjectionError(f"rollback_started {key} does not match artifact")
    projected = dict(payload)
    projected["latest_stable_checkpoint_id"] = latest.token
    projected["selected_checkpoint_id"] = selected.token
    projected["archive_id"] = archive.token
    for key in checks:
        projected[key] = BYTE_DERIVED_SENTINEL
    return projected


def _validate_prepared(row, *, artifacts, archives, sources, transformed) -> dict[str, Any]:
    payload = row["payload_json"]
    if set(payload) != _PREPARED_KEYS:
        raise ZeroCaregiverProjectionError(
            "rollback_lineage_prepared payload keys are not exact"
        )
    abandoned_lineage = int(payload["abandoned_lineage_generation"])
    abandoned_event = int(payload["abandoned_event_sequence"])
    selected_event = int(payload["selected_checkpoint_event_sequence"])
    rollback_started = int(payload["rollback_started_event_sequence"])
    new_lineage = int(payload["new_lineage_generation"])
    if (
        new_lineage != abandoned_lineage + 1
        or rollback_started != abandoned_event + 1
        or int(row["lineage_generation"]) != new_lineage
        or int(row["event_sequence"]) != selected_event + 1
    ):
        raise ZeroCaregiverProjectionError(
            "rollback_lineage_prepared event boundary is invalid"
        )
    selected = _require_checkpoint(
        artifacts,
        (int(payload["selected_checkpoint_lineage_generation"]), selected_event),
        payload.get("selected_checkpoint_id"),
        context="rollback prepared selected checkpoint",
    )
    archive = _require_archive(
        archives,
        (abandoned_lineage, abandoned_event, selected_event),
        payload.get("archive_id"),
        context="rollback prepared archive",
    )
    source = _require_source(
        sources,
        (abandoned_lineage, rollback_started, selected_event),
        payload.get("source_restore_candidate_id"),
        context="rollback prepared source candidate",
    )
    _require_transformed(
        transformed,
        (new_lineage, int(row["event_sequence"])),
        None,
        context="rollback prepared transformed candidate",
    )
    checks = {
        "archive_database_sha256": archive.database_sha256,
        "archive_manifest_sha256": archive.manifest_sha256,
        "selected_checkpoint_database_sha256": selected.database_sha256,
        "selected_checkpoint_manifest_sha256": selected.manifest_sha256,
        "source_restore_candidate_database_sha256": source.database_sha256,
        "source_restore_candidate_manifest_sha256": source.manifest_sha256,
    }
    for key, expected in checks.items():
        if payload.get(key) != expected:
            raise ZeroCaregiverProjectionError(
                f"rollback_lineage_prepared {key} does not match artifact"
            )
    projected = dict(payload)
    projected["selected_checkpoint_id"] = selected.token
    projected["archive_id"] = archive.token
    projected["source_restore_candidate_id"] = source.token
    for key in checks:
        projected[key] = BYTE_DERIVED_SENTINEL
    return projected


def _validate_completed(row, *, artifacts, archives, sources, transformed) -> dict[str, Any]:
    payload = row["payload_json"]
    if set(payload) != _COMPLETED_KEYS:
        raise ZeroCaregiverProjectionError("rollback_completed payload keys are not exact")
    abandoned_lineage = int(payload["abandoned_lineage_generation"])
    abandoned_event = int(payload["abandoned_event_sequence"])
    selected_event = int(payload["selected_checkpoint_event_sequence"])
    rollback_started = int(payload["rollback_started_event_sequence"])
    new_lineage = int(payload["new_lineage_generation"])
    restoration_event = int(payload["restoration_event_sequence"])
    completion_event = int(payload["completion_event_sequence"])
    if (
        new_lineage != abandoned_lineage + 1
        or rollback_started != abandoned_event + 1
        or completion_event != restoration_event + 1
        or int(row["lineage_generation"]) != new_lineage
        or int(row["event_sequence"]) != completion_event
    ):
        raise ZeroCaregiverProjectionError("rollback_completed event boundary is invalid")
    selected = _require_checkpoint(
        artifacts,
        (int(payload["selected_checkpoint_lineage_generation"]), selected_event),
        payload.get("selected_checkpoint_id"),
        context="rollback completed selected checkpoint",
    )
    archive = _require_archive(
        archives,
        (abandoned_lineage, abandoned_event, selected_event),
        payload.get("archive_id"),
        context="rollback completed archive",
    )
    source = _require_source(
        sources,
        (abandoned_lineage, rollback_started, selected_event),
        payload.get("source_restore_candidate_id"),
        context="rollback completed source candidate",
    )
    transformed_item = _require_transformed(
        transformed,
        (new_lineage, restoration_event),
        payload.get("transformed_candidate_id"),
        context="rollback completed transformed candidate",
    )
    checks = {
        "archive_database_sha256": archive.database_sha256,
        "archive_manifest_sha256": archive.manifest_sha256,
        "selected_checkpoint_database_sha256": selected.database_sha256,
        "selected_checkpoint_manifest_sha256": selected.manifest_sha256,
        "source_restore_candidate_database_sha256": source.database_sha256,
        "source_restore_candidate_manifest_sha256": source.manifest_sha256,
        "transformed_candidate_database_sha256": transformed_item.database_sha256,
        "transformed_candidate_manifest_sha256": transformed_item.manifest_sha256,
    }
    for key, expected in checks.items():
        if payload.get(key) != expected:
            raise ZeroCaregiverProjectionError(
                f"rollback_completed {key} does not match artifact"
            )
    projected = dict(payload)
    projected["selected_checkpoint_id"] = selected.token
    projected["archive_id"] = archive.token
    projected["source_restore_candidate_id"] = source.token
    projected["transformed_candidate_id"] = transformed_item.token
    for key in checks:
        projected[key] = BYTE_DERIVED_SENTINEL
    return projected


def _capture_rollback_events_from_database(
    database_path: Path,
    *,
    artifacts,
    archives,
    sources,
    transformed,
) -> dict[Any, RollbackEventEvidence]:
    connection = connect_database(database_path, read_only=True)
    try:
        rows = connection.execute(
            "SELECT * FROM event WHERE event_type IN (?, ?, ?) "
            "ORDER BY lineage_generation, event_sequence, event_type",
            (_ROLLBACK_STARTED, _ROLLBACK_PREPARED, _ROLLBACK_COMPLETED),
        ).fetchall()
    finally:
        connection.close()
    result: dict[Any, RollbackEventEvidence] = {}
    for row_value in rows:
        row = _event_row_dict(row_value)
        event_type = str(row["event_type"])
        _validate_event_columns(row, event_type=event_type)
        if event_type == _ROLLBACK_STARTED:
            projected_payload = _validate_started(
                row,
                artifacts=artifacts,
                archives=archives,
            )
        elif event_type == _ROLLBACK_PREPARED:
            projected_payload = _validate_prepared(
                row,
                artifacts=artifacts,
                archives=archives,
                sources=sources,
                transformed=transformed,
            )
        else:
            projected_payload = _validate_completed(
                row,
                artifacts=artifacts,
                archives=archives,
                sources=sources,
                transformed=transformed,
            )
        projected = dict(row)
        projected["schema_version"] = SCHEMA_SENTINEL
        projected["payload_json"] = projected_payload
        key = (int(row["lineage_generation"]), int(row["event_sequence"]), event_type)
        result[key] = RollbackEventEvidence(
            lineage_generation=key[0],
            event_sequence=key[1],
            event_type=key[2],
            raw_row_json=_canonical_json(row),
            projected_row_json=_canonical_json(projected),
        )
    return result


def _capture_rollback_events(
    paths: OrganismPaths,
    *,
    prior,
    artifacts,
    archives,
    sources,
    transformed,
) -> dict[Any, RollbackEventEvidence]:
    current = _capture_rollback_events_from_database(
        paths.database,
        artifacts=artifacts,
        archives=archives,
        sources=sources,
        transformed=transformed,
    )
    for item in transformed.values():
        candidate_events = _capture_rollback_events_from_database(
            paths.restore_candidates / item.transformed_candidate_id / "organism.sqlite3",
            artifacts=artifacts,
            archives=archives,
            sources=sources,
            transformed=transformed,
        )
        for key, proof in candidate_events.items():
            existing = current.get(key)
            if existing is not None and existing != proof:
                raise ZeroCaregiverProjectionError(
                    f"active/candidate rollback event differs: {key!r}"
                )
            current[key] = proof
    merged = dict(prior)
    for key, proof in current.items():
        existing = merged.get(key)
        if existing is not None and existing != proof:
            raise ZeroCaregiverProjectionError(
                f"captured rollback event changed: {key!r}"
            )
        merged[key] = proof
    return merged


def _matching_core_event_evidence(database_path: Path, evidence) -> dict[int, Any]:
    if not evidence:
        return {}
    connection = connect_database(database_path, read_only=True)
    try:
        rows = {
            int(row["event_sequence"]): row
            for row in connection.execute(
                "SELECT event_sequence, event_type, payload_json FROM event"
            )
        }
    finally:
        connection.close()
    result: dict[int, Any] = {}
    for item in evidence:
        row = rows.get(item.event_sequence)
        if row is None or row["event_type"] != item.event_type:
            continue
        try:
            payload = json.loads(str(row["payload_json"]))
        except json.JSONDecodeError:
            continue
        if _canonical_json(payload) == item.raw_payload_json:
            result[item.event_sequence] = item
    return result


def _apply_rollback_projection(rows: list[dict[str, Any]], *, evidence) -> None:
    for row in rows:
        key = (
            int(row["lineage_generation"]),
            int(row["event_sequence"]),
            str(row["event_type"]),
        )
        proof = evidence.get(key)
        if proof is None:
            continue
        captured_raw = json.loads(proof.raw_row_json)
        comparable = dict(row)
        comparable["schema_version"] = captured_raw["schema_version"]
        if _canonical_json(comparable) != proof.raw_row_json:
            raise ZeroCaregiverProjectionError(
                f"rollback event changed before projection: {key!r}"
            )
        projected = json.loads(proof.projected_row_json)
        row.clear()
        row.update(projected)


def _project_database(
    database_path: Path,
    *,
    expect_checkpoint_pending: bool,
    core: ZeroCaregiverEvidence,
    retention_events,
    rollback_events,
) -> dict[str, Any]:
    projected = _project_database_state(
        database_path,
        expect_checkpoint_pending=expect_checkpoint_pending,
        artifacts=_core_artifact_map(core),
        event_evidence=_matching_core_event_evidence(database_path, core.event_payloads),
    )
    matching_retention: dict[int, Any] = {}
    for row in projected["tables"]["event"]:
        item = retention_events.get(int(row["event_sequence"]))
        if item is None or row["event_type"] != item.event_type:
            continue
        payload = row.get("payload_json")
        if isinstance(payload, dict) and _canonical_json(payload) == item.raw_payload_json:
            matching_retention[item.event_sequence] = item
    _apply_retention_event_projection(
        projected["tables"]["event"],
        evidence=matching_retention,
    )
    _apply_rollback_projection(
        projected["tables"]["event"],
        evidence=rollback_events,
    )
    return projected


def _complete_artifact_projections(
    paths,
    *,
    core,
    retention,
    archives,
    sources,
    transformed,
    rollback_events,
):
    retention_events = {item.event_sequence: item for item in retention.event_payloads}
    completed_archives = {}
    for key, item in archives.items():
        state = _project_database(
            paths.rollback_archives / item.archive_id / "organism.sqlite3",
            expect_checkpoint_pending=False,
            core=core,
            retention_events=retention_events,
            rollback_events=rollback_events,
        )
        value = _canonical_json(state)
        if item.projected_database_state_json and item.projected_database_state_json != value:
            raise ZeroCaregiverProjectionError(
                f"rollback archive projected state changed: {key!r}"
            )
        completed_archives[key] = replace(item, projected_database_state_json=value)
    completed_sources = {}
    for key, item in sources.items():
        state = _project_database(
            paths.restore_candidates / item.candidate_id / "organism.sqlite3",
            expect_checkpoint_pending=True,
            core=core,
            retention_events=retention_events,
            rollback_events=rollback_events,
        )
        value = _canonical_json(state)
        if item.projected_database_state_json and item.projected_database_state_json != value:
            raise ZeroCaregiverProjectionError(
                f"source candidate projected state changed: {key!r}"
            )
        completed_sources[key] = replace(item, projected_database_state_json=value)
    completed_transformed = {}
    for key, item in transformed.items():
        state = _project_database(
            paths.restore_candidates / item.transformed_candidate_id / "organism.sqlite3",
            expect_checkpoint_pending=False,
            core=core,
            retention_events=retention_events,
            rollback_events=rollback_events,
        )
        value = _canonical_json(state)
        if item.projected_database_state_json and item.projected_database_state_json != value:
            raise ZeroCaregiverProjectionError(
                f"transformed candidate projected state changed: {key!r}"
            )
        completed_transformed[key] = replace(item, projected_database_state_json=value)
    return completed_archives, completed_sources, completed_transformed


def capture_zero_caregiver_rollback_evidence(
    paths: OrganismPaths,
    *,
    previous: ZeroCaregiverRollbackEvidence | None = None,
) -> ZeroCaregiverRollbackEvidence:
    """Capture cumulative validated rollback artifacts and lineage-aware events."""

    retention = _capture_retention_with_preserved_artifacts(
        paths,
        previous=previous.retention if previous is not None else None,
    )
    artifacts = _core_artifact_map(retention.core)
    current_archives = _inventory_archives(paths)
    current_sources, current_transformed = _inventory_candidates(
        paths,
        checkpoint_artifacts=artifacts,
    )
    archives = _merge_immutable(
        _archive_map(previous),
        current_archives,
        context="rollback archive evidence",
    )
    sources = _merge_immutable(
        _source_map(previous),
        current_sources,
        context="source candidate evidence",
    )
    transformed = _merge_immutable(
        _transformed_map(previous),
        current_transformed,
        context="transformed candidate evidence",
    )
    _validate_preserved_checkpoint_artifacts(
        paths,
        core=retention.core,
        archives=archives,
    )
    rollback_events = _capture_rollback_events(
        paths,
        prior=_rollback_event_map(previous),
        artifacts=artifacts,
        archives=archives,
        sources=sources,
        transformed=transformed,
    )
    archives, sources, transformed = _complete_artifact_projections(
        paths,
        core=retention.core,
        retention=retention,
        archives=archives,
        sources=sources,
        transformed=transformed,
        rollback_events=rollback_events,
    )
    return ZeroCaregiverRollbackEvidence(
        retention=retention,
        rollback_archives=tuple(archives[key] for key in sorted(archives)),
        restore_candidates=tuple(sources[key] for key in sorted(sources)),
        transformed_candidates=tuple(transformed[key] for key in sorted(transformed)),
        rollback_events=tuple(
            rollback_events[key] for key in sorted(rollback_events)
        ),
    )


def _project_archive_manifest(item, *, artifacts) -> dict[str, Any]:
    manifest = json.loads(item.manifest_json)
    latest = _require_checkpoint(
        artifacts,
        (
            int(manifest["active_lineage_generation"]),
            int(manifest["latest_stable_event_sequence"]),
        ),
        manifest["latest_stable_checkpoint_id"],
        context="archive latest checkpoint",
    )
    selected = _require_checkpoint(
        artifacts,
        (
            int(manifest["selected_checkpoint_lineage_generation"]),
            int(manifest["selected_checkpoint_event_sequence"]),
        ),
        manifest["selected_checkpoint_id"],
        context="archive selected checkpoint",
    )
    if (
        manifest["database_sha256"] != item.database_sha256
        or int(manifest["database_size_bytes"]) != item.database_size_bytes
        or manifest["selected_checkpoint_manifest_sha256"] != selected.manifest_sha256
        or manifest["selected_checkpoint_database_sha256"] != selected.database_sha256
        or int(manifest["selected_checkpoint_database_size_bytes"])
        != selected.database_size_bytes
    ):
        raise ZeroCaregiverProjectionError("archive byte evidence changed")
    manifest["archive_id"] = item.token
    manifest["latest_stable_checkpoint_id"] = latest.token
    manifest["selected_checkpoint_id"] = selected.token
    manifest["schema_version"] = SCHEMA_SENTINEL
    for key in (
        "database_sha256",
        "database_size_bytes",
        "selected_checkpoint_manifest_sha256",
        "selected_checkpoint_database_sha256",
        "selected_checkpoint_database_size_bytes",
    ):
        manifest[key] = BYTE_DERIVED_SENTINEL
    return manifest


def _project_source_manifest(item, *, artifacts, archives) -> dict[str, Any]:
    manifest = json.loads(item.manifest_json)
    selected = _require_checkpoint(
        artifacts,
        (int(manifest["source_lineage_generation"]), int(manifest["source_event_sequence"])),
        manifest["selected_checkpoint_id"],
        context="source candidate selected checkpoint",
    )
    archive = _require_archive(
        archives,
        (
            int(manifest["active_lineage_generation"]),
            int(manifest["rollback_started_event_sequence"]) - 1,
            int(manifest["source_event_sequence"]),
        ),
        manifest["archive_id"],
        context="source candidate archive",
    )
    checks = {
        "archive_manifest_sha256": archive.manifest_sha256,
        "archive_database_sha256": archive.database_sha256,
        "source_checkpoint_manifest_sha256": selected.manifest_sha256,
        "source_checkpoint_database_sha256": selected.database_sha256,
        "source_checkpoint_database_size_bytes": selected.database_size_bytes,
        "database_sha256": item.database_sha256,
        "database_size_bytes": item.database_size_bytes,
    }
    for key, expected in checks.items():
        if manifest[key] != expected:
            raise ZeroCaregiverProjectionError(f"source candidate {key} evidence changed")
    manifest["candidate_id"] = item.token
    manifest["archive_id"] = archive.token
    manifest["selected_checkpoint_id"] = selected.token
    manifest["schema_version"] = SCHEMA_SENTINEL
    for key in checks:
        manifest[key] = BYTE_DERIVED_SENTINEL
    return manifest


def _project_transformed_manifest(item, *, artifacts, archives, sources) -> dict[str, Any]:
    manifest = json.loads(item.manifest_json)
    selected_event = int(manifest["selected_checkpoint_event_sequence"])
    selected = _require_checkpoint(
        artifacts,
        (int(manifest["selected_checkpoint_lineage_generation"]), selected_event),
        manifest["selected_checkpoint_id"],
        context="transformed candidate selected checkpoint",
    )
    archive = _require_archive(
        archives,
        (
            int(manifest["abandoned_lineage_generation"]),
            int(manifest["abandoned_event_sequence"]),
            selected_event,
        ),
        manifest["archive_id"],
        context="transformed candidate archive",
    )
    source = _require_source(
        sources,
        (
            int(manifest["abandoned_lineage_generation"]),
            int(manifest["rollback_started_event_sequence"]),
            selected_event,
        ),
        manifest["source_restore_candidate_id"],
        context="transformed candidate source",
    )
    checks = {
        "source_restore_candidate_manifest_sha256": source.manifest_sha256,
        "source_restore_candidate_database_sha256": source.database_sha256,
        "source_restore_candidate_database_size_bytes": source.database_size_bytes,
        "archive_manifest_sha256": archive.manifest_sha256,
        "archive_database_sha256": archive.database_sha256,
        "selected_checkpoint_manifest_sha256": selected.manifest_sha256,
        "selected_checkpoint_database_sha256": selected.database_sha256,
        "selected_checkpoint_database_size_bytes": selected.database_size_bytes,
        "database_sha256": item.database_sha256,
        "database_size_bytes": item.database_size_bytes,
    }
    for key, expected in checks.items():
        if manifest[key] != expected:
            raise ZeroCaregiverProjectionError(
                f"transformed candidate {key} evidence changed"
            )
    manifest["transformed_candidate_id"] = item.token
    manifest["source_restore_candidate_id"] = source.token
    manifest["archive_id"] = archive.token
    manifest["selected_checkpoint_id"] = selected.token
    manifest["schema_version"] = SCHEMA_SENTINEL
    for key in checks:
        manifest[key] = BYTE_DERIVED_SENTINEL
    return manifest


def _project_checkpoint_artifact(item) -> dict[str, Any]:
    manifest = json.loads(item.manifest_json)
    manifest["checkpoint_id"] = item.token
    manifest["schema_version"] = SCHEMA_SENTINEL
    manifest["database_sha256"] = BYTE_DERIVED_SENTINEL
    manifest["database_size_bytes"] = BYTE_DERIVED_SENTINEL
    return {
        "checkpoint": item.token,
        "manifest": manifest,
        "database_state": json.loads(item.projected_database_state_json),
    }


def _require_schema(paths: OrganismPaths, expected: int) -> None:
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT schema_version FROM organism WHERE singleton_id=1"
        ).fetchone()
    finally:
        connection.close()
    actual = None if row is None else int(row["schema_version"])
    if actual != expected:
        side = "schema-v1" if expected == 1 else "schema-v2-zero"
        raise ZeroCaregiverProjectionError(
            f"{side} control has schema version {actual}"
        )


def _project(
    paths: OrganismPaths,
    *,
    evidence: ZeroCaregiverRollbackEvidence | None,
    expected_schema_version: int | None = None,
) -> dict[str, Any]:
    captured = capture_zero_caregiver_rollback_evidence(paths, previous=evidence)
    if expected_schema_version is not None:
        _require_schema(paths, expected_schema_version)
    core = captured.retention.core
    artifacts = _core_artifact_map(core)
    retention_events = {
        item.event_sequence: item for item in captured.retention.event_payloads
    }
    rollback_events = {item.semantic_key: item for item in captured.rollback_events}
    projected = _project_database(
        paths.database,
        expect_checkpoint_pending=False,
        core=core,
        retention_events=retention_events,
        rollback_events=rollback_events,
    )
    retained_artifacts = _project_checkpoint_artifacts(core)
    registry = set(core.retained_checkpoint_boundaries)
    preserved = [artifacts[key] for key in sorted(set(artifacts) - registry)]
    archive_map = _archive_map(captured)
    source_map = _source_map(captured)
    staging = {
        item.boundary: item for item in captured.retention.staging_artifacts
    }
    projected.update(
        {
            "projection_version": "phase1-projection-v2/rollback",
            "checkpoint_artifacts": retained_artifacts,
            "preserved_abandoned_checkpoints": [item.token for item in preserved],
            "preserved_abandoned_checkpoint_artifacts": [
                _project_checkpoint_artifact(item) for item in preserved
            ],
            "retention_staging_artifacts": [
                {
                    "checkpoint": staging[boundary].checkpoint_token,
                    "staging_directory": staging[boundary].staging_token,
                }
                for boundary in captured.retention.current_staging_boundaries
            ],
            "rollback_archives": [
                {
                    "archive": item.token,
                    "manifest": _project_archive_manifest(item, artifacts=artifacts),
                    "database_state": json.loads(item.projected_database_state_json),
                }
                for item in captured.rollback_archives
            ],
            "restore_candidates": [
                {
                    "candidate": item.token,
                    "manifest": _project_source_manifest(
                        item,
                        artifacts=artifacts,
                        archives=archive_map,
                    ),
                    "database_state": json.loads(item.projected_database_state_json),
                }
                for item in captured.restore_candidates
            ],
            "transformed_candidates": [
                {
                    "candidate": item.token,
                    "manifest": _project_transformed_manifest(
                        item,
                        artifacts=artifacts,
                        archives=archive_map,
                        sources=source_map,
                    ),
                    "database_state": json.loads(item.projected_database_state_json),
                }
                for item in captured.transformed_candidates
            ],
            "rollback_event_evidence": [
                json.loads(item.projected_row_json)
                for item in captured.rollback_events
            ],
        }
    )
    return projected


def project_zero_caregiver_rollback_state(
    paths: OrganismPaths,
    *,
    evidence: ZeroCaregiverRollbackEvidence | None = None,
) -> dict[str, Any]:
    """Validate and project one complete rollback artifact graph."""

    return _project(paths, evidence=evidence)


def assert_zero_caregiver_rollback_equivalent(
    schema_v1_paths: OrganismPaths,
    schema_v2_zero_paths: OrganismPaths,
    *,
    schema_v1_evidence: ZeroCaregiverRollbackEvidence | None = None,
    schema_v2_zero_evidence: ZeroCaregiverRollbackEvidence | None = None,
) -> None:
    """Require exact paired equality after rollback-specific validation."""

    left = _project(
        schema_v1_paths,
        evidence=schema_v1_evidence,
        expected_schema_version=1,
    )
    right = _project(
        schema_v2_zero_paths,
        evidence=schema_v2_zero_evidence,
        expected_schema_version=PHASE2_SCHEMA_VERSION,
    )
    if left != right:
        raise ZeroCaregiverProjectionError(
            "rollback-projected canonical state differs"
        )


__all__ = [
    "BYTE_DERIVED_SENTINEL",
    "SCHEMA_SENTINEL",
    "RollbackArchiveEvidence",
    "RestoreCandidateEvidence",
    "TransformedCandidateEvidence",
    "RollbackEventEvidence",
    "ZeroCaregiverProjectionError",
    "ZeroCaregiverRollbackEvidence",
    "assert_zero_caregiver_rollback_equivalent",
    "capture_zero_caregiver_rollback_evidence",
    "project_zero_caregiver_rollback_state",
]
