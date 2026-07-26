"""Closed retention extension for the zero-caregiver semantic projection."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Final

from .checkpoint_core import validate_checkpoint_directory
from .constants import (
    CHECKPOINT_RETENTION_LIMIT,
    MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
)
from .errors import CheckpointError, SchemaValidationError
from .paths import OrganismPaths
from .phase2_projection import (
    BYTE_DERIVED_SENTINEL,
    CheckpointArtifactEvidence,
    EventPayloadEvidence,
    ZeroCaregiverEvidence,
    ZeroCaregiverProjectionError,
    capture_zero_caregiver_evidence,
    project_zero_caregiver_state,
)
from .phase2_schema import PHASE2_SCHEMA_VERSION
from .runtime_storage import checkpoint_store_bytes
from .storage import connect_database

_PRUNED_EVENT: Final = "checkpoint_pruned"
_FAILED_EVENT: Final = "checkpoint_retention_failed"
_PENDING_EVENT: Final = "checkpoint_retention_cleanup_reconciliation_pending"
_RECONCILED_EVENT: Final = "checkpoint_retention_cleanup_reconciled"

_PRUNED_KEYS: Final[frozenset[str]] = frozenset(
    {
        "latest_stable_checkpoint_id",
        "latest_stable_event_sequence",
        "pruned_artifact_size_bytes",
        "pruned_checkpoint_id",
        "pruned_database_size_bytes",
        "pruned_event_sequence",
        "pruned_lineage_generation",
        "pruned_provenance",
        "reason",
        "retained_checkpoint_count",
        "retained_checkpoint_store_bytes",
        "retention_limit",
    }
)
_FAILED_KEYS: Final[frozenset[str]] = frozenset(
    {
        "candidate_checkpoint_id",
        "candidate_event_sequence",
        "candidate_restored",
        "checkpoint_store_bytes",
        "injection_point",
        "latest_stable_checkpoint_id",
        "latest_stable_event_sequence",
        "maintenance_reason",
        "reason",
        "registered_checkpoint_boundaries",
        "registered_checkpoint_count",
        "retention_limit",
        "stable_checkpoint_count",
        "status_after",
    }
)
_PENDING_KEYS: Final[frozenset[str]] = frozenset(
    {
        "checkpoint_ids",
        "reason",
        "staging_directories",
        "status_before",
    }
)
_RECONCILED_KEYS: Final[frozenset[str]] = frozenset(
    {
        "reason",
        "reconciliation_pending_event_sequence",
        "removed_staging_directories",
        "status_after",
    }
)


@dataclass(frozen=True)
class RetentionStagingEvidence:
    """Validated immutable witness for one committed-prune staging directory."""

    lineage_generation: int
    event_sequence: int
    checkpoint_id: str
    staging_directory: str
    manifest_sha256: str
    database_sha256: str
    database_size_bytes: int
    artifact_size_bytes: int
    manifest_json: str

    @property
    def boundary(self) -> tuple[int, int]:
        return (self.lineage_generation, self.event_sequence)

    @property
    def checkpoint_token(self) -> str:
        return _checkpoint_token(*self.boundary)

    @property
    def staging_token(self) -> str:
        return _staging_token(*self.boundary)


@dataclass(frozen=True)
class ZeroCaregiverRetentionEvidence:
    """Cumulative retention evidence layered over the accepted core ledger."""

    core: ZeroCaregiverEvidence
    staging_artifacts: tuple[RetentionStagingEvidence, ...]
    event_payloads: tuple[EventPayloadEvidence, ...]
    current_staging_boundaries: tuple[tuple[int, int], ...]


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _decode_object(raw: object, *, context: str) -> dict[str, Any]:
    try:
        value = json.loads(str(raw))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ZeroCaregiverProjectionError(f"{context} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ZeroCaregiverProjectionError(f"{context} is not an object")
    return value


def _strict_int(value: object, *, context: str) -> int:
    if type(value) is not int:
        raise ZeroCaregiverProjectionError(f"{context} is not an integer")
    return value


def _strict_bool(value: object, *, context: str) -> bool:
    if type(value) is not bool:
        raise ZeroCaregiverProjectionError(f"{context} is not a boolean")
    return value


def _strict_string_list(value: object, *, context: str) -> list[str]:
    if not isinstance(value, list) or any(type(item) is not str for item in value):
        raise ZeroCaregiverProjectionError(f"{context} is not a string list")
    return list(value)


def _strict_int_list(value: object, *, context: str) -> list[int]:
    if not isinstance(value, list) or any(type(item) is not int for item in value):
        raise ZeroCaregiverProjectionError(f"{context} is not an integer list")
    return list(value)


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


def _staging_token(lineage_generation: int, event_sequence: int) -> str:
    return f"STAGE({_checkpoint_token(lineage_generation, event_sequence)})"


def _artifact_map(
    evidence: ZeroCaregiverEvidence,
) -> dict[tuple[int, int], CheckpointArtifactEvidence]:
    result: dict[tuple[int, int], CheckpointArtifactEvidence] = {}
    for artifact in evidence.checkpoint_artifacts:
        if artifact.boundary in result:
            raise ZeroCaregiverProjectionError(
                f"duplicate checkpoint artifact evidence: {artifact.boundary!r}"
            )
        result[artifact.boundary] = artifact
    return result


def _staging_map(
    evidence: ZeroCaregiverRetentionEvidence | None,
) -> dict[tuple[int, int], RetentionStagingEvidence]:
    if evidence is None:
        return {}
    result: dict[tuple[int, int], RetentionStagingEvidence] = {}
    for item in evidence.staging_artifacts:
        if item.boundary in result:
            raise ZeroCaregiverProjectionError(
                f"duplicate retention staging evidence: {item.boundary!r}"
            )
        result[item.boundary] = item
    return result


def _retention_event_map(
    evidence: ZeroCaregiverRetentionEvidence | None,
) -> dict[int, EventPayloadEvidence]:
    if evidence is None:
        return {}
    result: dict[int, EventPayloadEvidence] = {}
    for item in evidence.event_payloads:
        if item.event_sequence in result:
            raise ZeroCaregiverProjectionError(
                f"duplicate retention event evidence: {item.event_sequence}"
            )
        result[item.event_sequence] = item
    return result


def _require_artifact(
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    boundary: tuple[int, int],
    *,
    context: str,
) -> CheckpointArtifactEvidence:
    artifact = artifacts.get(boundary)
    if artifact is None:
        raise ZeroCaregiverProjectionError(
            f"{context} has no artifact evidence: {boundary!r}"
        )
    return artifact


def _inventory_current_staging(
    paths: OrganismPaths,
    *,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
) -> tuple[
    dict[tuple[int, int], RetentionStagingEvidence],
    tuple[tuple[int, int], ...],
]:
    if not paths.checkpoints.is_dir() or paths.checkpoints.is_symlink():
        raise ZeroCaregiverProjectionError("checkpoint store is missing or unsafe")

    current: dict[tuple[int, int], RetentionStagingEvidence] = {}
    ordered: list[tuple[int, int]] = []
    for staged_dir in sorted(paths.checkpoints.iterdir(), key=lambda item: item.name):
        if not staged_dir.name.startswith(".pruning-"):
            continue
        if staged_dir.is_symlink() or not staged_dir.is_dir():
            raise ZeroCaregiverProjectionError("retention staging entry is unsafe")
        try:
            manifest = validate_checkpoint_directory(staged_dir)
        except (CheckpointError, SchemaValidationError) as exc:
            raise ZeroCaregiverProjectionError(str(exc)) from exc

        boundary = (
            _strict_int(
                manifest.get("lineage_generation"),
                context="retention staging lineage_generation",
            ),
            _strict_int(
                manifest.get("event_sequence"),
                context="retention staging event_sequence",
            ),
        )
        if boundary in current:
            raise ZeroCaregiverProjectionError(
                f"duplicate retention staging boundary: {boundary!r}"
            )
        artifact = _require_artifact(
            artifacts,
            boundary,
            context="retention staging boundary",
        )
        expected_name = f".pruning-{artifact.checkpoint_id}"
        if staged_dir.name != expected_name:
            raise ZeroCaregiverProjectionError(
                "retention staging directory does not match witnessed artifact"
            )
        if manifest.get("checkpoint_id") != artifact.checkpoint_id:
            raise ZeroCaregiverProjectionError(
                "retention staging checkpoint identity does not match witnessed artifact"
            )

        manifest_path = staged_dir / "manifest.json"
        database_path = staged_dir / "organism.sqlite3"
        item = RetentionStagingEvidence(
            lineage_generation=boundary[0],
            event_sequence=boundary[1],
            checkpoint_id=artifact.checkpoint_id,
            staging_directory=staged_dir.name,
            manifest_sha256=_sha256_file(manifest_path),
            database_sha256=_sha256_file(database_path),
            database_size_bytes=database_path.stat().st_size,
            artifact_size_bytes=_artifact_size(staged_dir),
            manifest_json=_canonical_json(manifest),
        )
        if (
            item.manifest_sha256 != artifact.manifest_sha256
            or item.database_sha256 != artifact.database_sha256
            or item.database_size_bytes != artifact.database_size_bytes
            or item.artifact_size_bytes != artifact.artifact_size_bytes
            or item.manifest_json != artifact.manifest_json
        ):
            raise ZeroCaregiverProjectionError(
                "retention staging bytes changed from the pre-deletion witness"
            )
        current[boundary] = item
        ordered.append(boundary)
    return current, tuple(ordered)


def _merge_staging_evidence(
    prior: dict[tuple[int, int], RetentionStagingEvidence],
    current: dict[tuple[int, int], RetentionStagingEvidence],
) -> dict[tuple[int, int], RetentionStagingEvidence]:
    merged = dict(prior)
    for boundary, item in current.items():
        previous = merged.get(boundary)
        if previous is not None and previous != item:
            raise ZeroCaregiverProjectionError(
                f"retention staging evidence changed: {boundary!r}"
            )
        merged[boundary] = item
    return merged


def _validate_linked_checkpoint(
    payload: dict[str, Any],
    *,
    id_key: str,
    boundary: tuple[int, int],
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    context: str,
) -> CheckpointArtifactEvidence:
    artifact = _require_artifact(artifacts, boundary, context=context)
    if payload.get(id_key) != artifact.checkpoint_id:
        raise ZeroCaregiverProjectionError(
            f"{context} identity does not match artifact evidence"
        )
    return artifact


def _validate_pruned_event(
    row: dict[str, Any],
    payload: dict[str, Any],
    *,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    current_staging: dict[tuple[int, int], RetentionStagingEvidence],
    registry_boundaries: tuple[tuple[int, int], ...],
    measured_store_bytes: int,
) -> dict[str, Any]:
    if set(payload) != _PRUNED_KEYS:
        raise ZeroCaregiverProjectionError("checkpoint_pruned payload keys are not exact")
    if payload.get("reason") != "checkpoint_retention_limit":
        raise ZeroCaregiverProjectionError("checkpoint_pruned reason is not protected")
    if _strict_int(payload.get("retention_limit"), context="retention_limit") != CHECKPOINT_RETENTION_LIMIT:
        raise ZeroCaregiverProjectionError("checkpoint_pruned retention limit changed")

    lineage_generation = _strict_int(
        row.get("lineage_generation"),
        context="checkpoint_pruned event lineage",
    )
    latest_boundary = (
        lineage_generation,
        _strict_int(
            payload.get("latest_stable_event_sequence"),
            context="checkpoint_pruned latest event sequence",
        ),
    )
    latest = _validate_linked_checkpoint(
        payload,
        id_key="latest_stable_checkpoint_id",
        boundary=latest_boundary,
        artifacts=artifacts,
        context="checkpoint_pruned latest checkpoint",
    )
    pruned_boundary = (
        _strict_int(
            payload.get("pruned_lineage_generation"),
            context="checkpoint_pruned pruned lineage",
        ),
        _strict_int(
            payload.get("pruned_event_sequence"),
            context="checkpoint_pruned pruned event sequence",
        ),
    )
    pruned = _validate_linked_checkpoint(
        payload,
        id_key="pruned_checkpoint_id",
        boundary=pruned_boundary,
        artifacts=artifacts,
        context="pruned checkpoint boundary",
    )
    if pruned_boundary in registry_boundaries:
        raise ZeroCaregiverProjectionError(
            "checkpoint_pruned boundary still exists in the canonical registry"
        )
    if latest_boundary not in registry_boundaries:
        raise ZeroCaregiverProjectionError(
            "checkpoint_pruned latest boundary is absent from the canonical registry"
        )
    if _strict_int(
        payload.get("pruned_artifact_size_bytes"),
        context="checkpoint_pruned artifact size",
    ) != pruned.artifact_size_bytes:
        raise ZeroCaregiverProjectionError(
            "checkpoint_pruned artifact size does not match pre-deletion evidence"
        )
    if _strict_int(
        payload.get("pruned_database_size_bytes"),
        context="checkpoint_pruned database size",
    ) != pruned.database_size_bytes:
        raise ZeroCaregiverProjectionError(
            "checkpoint_pruned database size does not match pre-deletion evidence"
        )
    if _strict_int(
        payload.get("retained_checkpoint_count"),
        context="checkpoint_pruned retained count",
    ) != len(registry_boundaries):
        raise ZeroCaregiverProjectionError(
            "checkpoint_pruned retained count does not match the registry"
        )

    expected_store_bytes = measured_store_bytes
    staged = current_staging.get(pruned_boundary)
    if staged is not None:
        expected_store_bytes -= staged.artifact_size_bytes
    if expected_store_bytes < 0 or _strict_int(
        payload.get("retained_checkpoint_store_bytes"),
        context="checkpoint_pruned retained store bytes",
    ) != expected_store_bytes:
        raise ZeroCaregiverProjectionError(
            "checkpoint_pruned retained store bytes do not match measured evidence"
        )

    projected = dict(payload)
    projected["latest_stable_checkpoint_id"] = latest.token
    projected["pruned_checkpoint_id"] = pruned.token
    for key in (
        "pruned_artifact_size_bytes",
        "pruned_database_size_bytes",
        "retained_checkpoint_store_bytes",
    ):
        projected[key] = BYTE_DERIVED_SENTINEL
    return projected


def _validate_failed_event(
    row: dict[str, Any],
    payload: dict[str, Any],
    *,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    current_staging: dict[tuple[int, int], RetentionStagingEvidence],
    registry_boundaries: tuple[tuple[int, int], ...],
    registry_event_sequences: list[int],
    measured_store_bytes: int,
) -> dict[str, Any]:
    candidate_restored = _strict_bool(
        payload.get("candidate_restored"),
        context="checkpoint_retention_failed candidate_restored",
    )
    expected_keys = set(_FAILED_KEYS)
    if not candidate_restored:
        expected_keys.add("staging_directory")
    if set(payload) != expected_keys:
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed payload keys are not exact"
        )
    if payload.get("maintenance_reason") != MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED:
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed maintenance reason changed"
        )
    if payload.get("status_after") != "maintenance_required":
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed status is not maintenance_required"
        )
    if _strict_int(payload.get("retention_limit"), context="retention_limit") != CHECKPOINT_RETENTION_LIMIT:
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed retention limit changed"
        )

    lineage_generation = _strict_int(
        row.get("lineage_generation"),
        context="checkpoint_retention_failed event lineage",
    )
    candidate_boundary = (
        lineage_generation,
        _strict_int(
            payload.get("candidate_event_sequence"),
            context="checkpoint_retention_failed candidate event sequence",
        ),
    )
    candidate = _validate_linked_checkpoint(
        payload,
        id_key="candidate_checkpoint_id",
        boundary=candidate_boundary,
        artifacts=artifacts,
        context="checkpoint_retention_failed candidate checkpoint",
    )
    latest_boundary = (
        lineage_generation,
        _strict_int(
            payload.get("latest_stable_event_sequence"),
            context="checkpoint_retention_failed latest event sequence",
        ),
    )
    latest = _validate_linked_checkpoint(
        payload,
        id_key="latest_stable_checkpoint_id",
        boundary=latest_boundary,
        artifacts=artifacts,
        context="checkpoint_retention_failed latest checkpoint",
    )
    if latest_boundary not in registry_boundaries:
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed latest boundary is absent from registry"
        )
    if _strict_int(
        payload.get("checkpoint_store_bytes"),
        context="checkpoint_retention_failed checkpoint store bytes",
    ) != measured_store_bytes:
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed checkpoint_store_bytes does not match measured store"
        )
    if _strict_int(
        payload.get("registered_checkpoint_count"),
        context="checkpoint_retention_failed registered count",
    ) != len(registry_boundaries):
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed registered count does not match registry"
        )
    if _strict_int(
        payload.get("stable_checkpoint_count"),
        context="checkpoint_retention_failed stable count",
    ) != len(registry_boundaries):
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed stable count does not match registry"
        )
    if _strict_int_list(
        payload.get("registered_checkpoint_boundaries"),
        context="checkpoint_retention_failed registered boundaries",
    ) != registry_event_sequences:
        raise ZeroCaregiverProjectionError(
            "checkpoint_retention_failed registered boundaries do not match registry"
        )

    projected = dict(payload)
    projected["candidate_checkpoint_id"] = candidate.token
    projected["latest_stable_checkpoint_id"] = latest.token
    projected["checkpoint_store_bytes"] = BYTE_DERIVED_SENTINEL
    if candidate_restored:
        if candidate_boundary not in registry_boundaries:
            raise ZeroCaregiverProjectionError(
                "restored retention candidate is absent from registry"
            )
        if candidate_boundary in current_staging:
            raise ZeroCaregiverProjectionError(
                "restored retention candidate still has staging evidence"
            )
        if (
            payload.get("injection_point")
            != "after_artifact_stage_before_registry_mutation"
            or payload.get("reason")
            != "protected_test_injected_checkpoint_retention_failure"
        ):
            raise ZeroCaregiverProjectionError(
                "restored retention failure classification changed"
            )
    else:
        if candidate_boundary in registry_boundaries:
            raise ZeroCaregiverProjectionError(
                "committed prune candidate still exists in registry"
            )
        staged = current_staging.get(candidate_boundary)
        if staged is None:
            raise ZeroCaregiverProjectionError(
                "committed retention cleanup failure has no current staging witness"
            )
        if payload.get("staging_directory") != staged.staging_directory:
            raise ZeroCaregiverProjectionError(
                "retention staging directory does not match witnessed artifact"
            )
        if (
            payload.get("injection_point")
            != "after_registry_commit_before_staging_cleanup"
            or payload.get("reason") != "post_commit_staging_cleanup_failed"
        ):
            raise ZeroCaregiverProjectionError(
                "post-commit retention failure classification changed"
            )
        projected["staging_directory"] = staged.staging_token
    return projected


def _validate_pending_event(
    payload: dict[str, Any],
    *,
    staging: dict[tuple[int, int], RetentionStagingEvidence],
) -> dict[str, Any]:
    if set(payload) != _PENDING_KEYS:
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup pending payload keys are not exact"
        )
    if payload.get("reason") != "committed_prune_cleanup_reconciliation":
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup pending reason changed"
        )
    checkpoint_ids = _strict_string_list(
        payload.get("checkpoint_ids"),
        context="checkpoint retention cleanup pending checkpoint_ids",
    )
    staging_directories = _strict_string_list(
        payload.get("staging_directories"),
        context="checkpoint retention cleanup pending staging_directories",
    )
    if not checkpoint_ids or len(checkpoint_ids) != len(staging_directories):
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup pending lists are not aligned"
        )
    if staging_directories != sorted(set(staging_directories)):
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup pending staging order is not canonical"
        )

    staging_by_name = {item.staging_directory: item for item in staging.values()}
    projected_ids: list[str] = []
    projected_directories: list[str] = []
    seen_boundaries: set[tuple[int, int]] = set()
    for checkpoint_id, directory in zip(
        checkpoint_ids,
        staging_directories,
        strict=True,
    ):
        witness = staging_by_name.get(directory)
        if witness is None:
            raise ZeroCaregiverProjectionError(
                "checkpoint retention cleanup pending directory has no prior witness"
            )
        if checkpoint_id != witness.checkpoint_id:
            raise ZeroCaregiverProjectionError(
                "checkpoint retention cleanup pending checkpoint does not match staging witness"
            )
        if witness.boundary in seen_boundaries:
            raise ZeroCaregiverProjectionError(
                "checkpoint retention cleanup pending boundary is duplicated"
            )
        seen_boundaries.add(witness.boundary)
        projected_ids.append(witness.checkpoint_token)
        projected_directories.append(witness.staging_token)

    projected = dict(payload)
    projected["checkpoint_ids"] = projected_ids
    projected["staging_directories"] = projected_directories
    return projected


def _validate_reconciled_event(
    row: dict[str, Any],
    payload: dict[str, Any],
    *,
    event_evidence: dict[int, EventPayloadEvidence],
) -> dict[str, Any]:
    if set(payload) != _RECONCILED_KEYS:
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup reconciled payload keys are not exact"
        )
    if payload.get("reason") != "committed_prune_cleanup_reconciled":
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup reconciled reason changed"
        )
    pending_sequence = _strict_int(
        payload.get("reconciliation_pending_event_sequence"),
        context="checkpoint retention cleanup reconciled pending sequence",
    )
    if pending_sequence >= _strict_int(
        row.get("event_sequence"),
        context="checkpoint retention cleanup reconciled event sequence",
    ):
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup completion does not follow pending audit"
        )
    pending = event_evidence.get(pending_sequence)
    if pending is None or pending.event_type != _PENDING_EVENT:
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup completion has no pending-event evidence"
        )
    pending_raw = _decode_object(
        pending.raw_payload_json,
        context="checkpoint retention cleanup pending raw evidence",
    )
    pending_projected = _decode_object(
        pending.projected_payload_json,
        context="checkpoint retention cleanup pending projected evidence",
    )
    removed = _strict_string_list(
        payload.get("removed_staging_directories"),
        context="checkpoint retention cleanup reconciled removed directories",
    )
    if removed != _strict_string_list(
        pending_raw.get("staging_directories"),
        context="checkpoint retention cleanup pending raw directories",
    ):
        raise ZeroCaregiverProjectionError(
            "checkpoint retention cleanup completion differs from pending audit"
        )

    projected = dict(payload)
    projected["removed_staging_directories"] = _strict_string_list(
        pending_projected.get("staging_directories"),
        context="checkpoint retention cleanup pending projected directories",
    )
    return projected


def _capture_retention_event_evidence(
    connection: sqlite3.Connection,
    *,
    artifacts: dict[tuple[int, int], CheckpointArtifactEvidence],
    all_staging: dict[tuple[int, int], RetentionStagingEvidence],
    current_staging: dict[tuple[int, int], RetentionStagingEvidence],
    registry_boundaries: tuple[tuple[int, int], ...],
    registry_event_sequences: list[int],
    measured_store_bytes: int,
    prior: dict[int, EventPayloadEvidence],
) -> dict[int, EventPayloadEvidence]:
    result = dict(prior)
    for row_value in connection.execute("SELECT * FROM event ORDER BY event_sequence"):
        row = dict(row_value)
        event_sequence = _strict_int(
            row.get("event_sequence"),
            context="retention event sequence",
        )
        event_type = str(row.get("event_type"))
        if event_type not in {
            _PRUNED_EVENT,
            _FAILED_EVENT,
            _PENDING_EVENT,
            _RECONCILED_EVENT,
        }:
            continue
        payload = _decode_object(
            row.get("payload_json"),
            context=f"{event_type} payload",
        )
        raw_payload_json = _canonical_json(payload)
        previous = result.get(event_sequence)
        if previous is not None:
            if previous.event_type != event_type or previous.raw_payload_json != raw_payload_json:
                raise ZeroCaregiverProjectionError(
                    f"captured retention event evidence changed at sequence {event_sequence}"
                )
            continue

        if event_type == _PRUNED_EVENT:
            projected = _validate_pruned_event(
                row,
                payload,
                artifacts=artifacts,
                current_staging=current_staging,
                registry_boundaries=registry_boundaries,
                measured_store_bytes=measured_store_bytes,
            )
        elif event_type == _FAILED_EVENT:
            projected = _validate_failed_event(
                row,
                payload,
                artifacts=artifacts,
                current_staging=current_staging,
                registry_boundaries=registry_boundaries,
                registry_event_sequences=registry_event_sequences,
                measured_store_bytes=measured_store_bytes,
            )
        elif event_type == _PENDING_EVENT:
            projected = _validate_pending_event(payload, staging=all_staging)
        else:
            projected = _validate_reconciled_event(
                row,
                payload,
                event_evidence=result,
            )
        result[event_sequence] = EventPayloadEvidence(
            event_sequence=event_sequence,
            event_type=event_type,
            raw_payload_json=raw_payload_json,
            projected_payload_json=_canonical_json(projected),
        )
    return result


def capture_zero_caregiver_retention_evidence(
    paths: OrganismPaths,
    *,
    previous: ZeroCaregiverRetentionEvidence | None = None,
) -> ZeroCaregiverRetentionEvidence:
    """Capture cumulative pre-deletion, staging, and retention-event evidence."""

    core = capture_zero_caregiver_evidence(
        paths,
        previous=previous.core if previous is not None else None,
    )
    artifacts = _artifact_map(core)
    current_staging, current_order = _inventory_current_staging(
        paths,
        artifacts=artifacts,
    )
    all_staging = _merge_staging_evidence(
        _staging_map(previous),
        current_staging,
    )

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
        if registry_boundaries != core.retained_checkpoint_boundaries:
            raise ZeroCaregiverProjectionError(
                "retention core registry boundaries changed during capture"
            )
        registry_event_sequences = [
            int(row["event_sequence"]) for row in registry_rows
        ]
        events = _capture_retention_event_evidence(
            connection,
            artifacts=artifacts,
            all_staging=all_staging,
            current_staging=current_staging,
            registry_boundaries=registry_boundaries,
            registry_event_sequences=registry_event_sequences,
            measured_store_bytes=checkpoint_store_bytes(paths),
            prior=_retention_event_map(previous),
        )
    finally:
        connection.close()

    return ZeroCaregiverRetentionEvidence(
        core=core,
        staging_artifacts=tuple(all_staging[key] for key in sorted(all_staging)),
        event_payloads=tuple(events[key] for key in sorted(events)),
        current_staging_boundaries=current_order,
    )


def _apply_retention_event_projection(
    rows: list[dict[str, Any]],
    *,
    evidence: dict[int, EventPayloadEvidence],
) -> None:
    for row in rows:
        event_sequence = int(row["event_sequence"])
        proof = evidence.get(event_sequence)
        if proof is None:
            continue
        if row["event_type"] != proof.event_type:
            raise ZeroCaregiverProjectionError(
                f"retention projection event type changed at sequence {event_sequence}"
            )
        payload = row.get("payload_json")
        if not isinstance(payload, dict) or _canonical_json(payload) != proof.raw_payload_json:
            raise ZeroCaregiverProjectionError(
                f"retention projection raw payload changed at sequence {event_sequence}"
            )
        projected = _decode_object(
            proof.projected_payload_json,
            context=f"retention projected event {event_sequence}",
        )
        row["payload_json"] = projected


def _expected_schema_version(paths: OrganismPaths, expected: int) -> None:
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT schema_version FROM organism WHERE singleton_id=1"
        ).fetchone()
    finally:
        connection.close()
    if row is None or int(row["schema_version"]) != expected:
        side = "schema-v1" if expected == 1 else "schema-v2-zero"
        actual = None if row is None else int(row["schema_version"])
        raise ZeroCaregiverProjectionError(
            f"{side} control has schema version {actual}"
        )


def _project_retention_state(
    paths: OrganismPaths,
    *,
    evidence: ZeroCaregiverRetentionEvidence | None,
    expected_schema_version: int | None = None,
) -> dict[str, Any]:
    captured = capture_zero_caregiver_retention_evidence(paths, previous=evidence)
    if expected_schema_version is not None:
        _expected_schema_version(paths, expected_schema_version)
    projected = project_zero_caregiver_state(paths, evidence=captured.core)
    event_evidence = {
        item.event_sequence: item for item in captured.event_payloads
    }
    _apply_retention_event_projection(
        projected["tables"]["event"],
        evidence=event_evidence,
    )
    for checkpoint in projected["checkpoint_artifacts"]:
        _apply_retention_event_projection(
            checkpoint["database_state"]["tables"]["event"],
            evidence=event_evidence,
        )

    staging = {item.boundary: item for item in captured.staging_artifacts}
    projected["projection_version"] = "phase1-projection-v2/retention"
    projected["retention_staging_artifacts"] = [
        {
            "checkpoint": staging[boundary].checkpoint_token,
            "staging_directory": staging[boundary].staging_token,
        }
        for boundary in captured.current_staging_boundaries
    ]
    return projected


def project_zero_caregiver_retention_state(
    paths: OrganismPaths,
    *,
    evidence: ZeroCaregiverRetentionEvidence | None = None,
) -> dict[str, Any]:
    """Validate one run and return its exact retention-extended projection."""

    return _project_retention_state(paths, evidence=evidence)


def assert_zero_caregiver_retention_equivalent(
    schema_v1_paths: OrganismPaths,
    schema_v2_zero_paths: OrganismPaths,
    *,
    schema_v1_evidence: ZeroCaregiverRetentionEvidence | None = None,
    schema_v2_zero_evidence: ZeroCaregiverRetentionEvidence | None = None,
) -> None:
    """Require paired equality after retention-specific independent validation."""

    left = _project_retention_state(
        schema_v1_paths,
        evidence=schema_v1_evidence,
        expected_schema_version=1,
    )
    right = _project_retention_state(
        schema_v2_zero_paths,
        evidence=schema_v2_zero_evidence,
        expected_schema_version=PHASE2_SCHEMA_VERSION,
    )
    if left != right:
        raise ZeroCaregiverProjectionError(
            "retention-projected canonical state differs"
        )


__all__ = [
    "BYTE_DERIVED_SENTINEL",
    "RetentionStagingEvidence",
    "ZeroCaregiverProjectionError",
    "ZeroCaregiverRetentionEvidence",
    "assert_zero_caregiver_retention_equivalent",
    "capture_zero_caregiver_retention_evidence",
    "project_zero_caregiver_retention_state",
]
