"""Paired physical-overhead evidence for the zero-caregiver projection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .paths import OrganismPaths
from .phase2_rollback_projection import (
    ZeroCaregiverRollbackEvidence,
    ZeroCaregiverProjectionError,
    assert_zero_caregiver_rollback_equivalent,
    capture_zero_caregiver_rollback_evidence,
)

ACTIVE_DATABASE_OVERHEAD_CAP_BYTES = 256 * 1024
ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES = 256 * 1024
METADATA_OVERHEAD_CAP_BYTES = 1 * 1024 * 1024


class PhysicalProjectionError(ZeroCaregiverProjectionError):
    """Physical paired evidence is incomplete, mismatched, or over budget."""


@dataclass(frozen=True)
class PhysicalOverheadReport:
    active_database_overhead_bytes: int
    checkpoint_database_overhead_bytes: tuple[tuple[str, int], ...]
    rollback_archive_database_overhead_bytes: tuple[tuple[str, int], ...]
    source_candidate_database_overhead_bytes: tuple[tuple[str, int], ...]
    transformed_candidate_database_overhead_bytes: tuple[tuple[str, int], ...]
    schema_v1_total_artifact_metadata_bytes: int
    schema_v2_total_artifact_metadata_bytes: int
    aggregate_metadata_overhead_bytes: int


def _safe_file_size(path: Path, *, context: str) -> int:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise PhysicalProjectionError(f"{context} is missing") from exc
    if path.is_symlink() or not path.is_file():
        raise PhysicalProjectionError(f"{context} is not a safe regular file")
    return int(metadata.st_size)


def _items_by_token(items: Iterable[Any], *, context: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in items:
        token = str(item.token)
        if token in result:
            raise PhysicalProjectionError(f"duplicate {context} token: {token}")
        result[token] = item
    return result


def _paired_database_overhead(
    schema_v1_items: Iterable[Any],
    schema_v2_items: Iterable[Any],
    *,
    context: str,
) -> tuple[tuple[str, int], ...]:
    left = _items_by_token(schema_v1_items, context=context)
    right = _items_by_token(schema_v2_items, context=context)
    if set(left) != set(right):
        raise PhysicalProjectionError(
            f"{context} semantic token sets differ before byte comparison"
        )
    overhead: list[tuple[str, int]] = []
    for token in sorted(left):
        delta = int(right[token].database_size_bytes) - int(
            left[token].database_size_bytes
        )
        if delta < 0:
            raise PhysicalProjectionError(
                f"{context} schema-v2 database is smaller than its paired schema-v1 artifact"
            )
        if delta > ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES:
            raise PhysicalProjectionError(
                f"{context} artifact database overhead exceeds the accepted cap"
            )
        overhead.append((token, delta))
    return tuple(overhead)


def _artifact_metadata_bytes(evidence: ZeroCaregiverRollbackEvidence) -> int:
    items = (
        *evidence.retention.core.checkpoint_artifacts,
        *evidence.rollback_archives,
        *evidence.restore_candidates,
        *evidence.transformed_candidates,
    )
    total = 0
    for item in items:
        metadata_bytes = int(item.artifact_size_bytes) - int(item.database_size_bytes)
        if metadata_bytes < 0:
            raise PhysicalProjectionError(
                f"artifact metadata accounting is negative for {item.token}"
            )
        total += metadata_bytes
    return total


def measure_zero_caregiver_physical_overhead(
    schema_v1_paths: OrganismPaths,
    schema_v2_zero_paths: OrganismPaths,
    schema_v1_evidence: ZeroCaregiverRollbackEvidence,
    schema_v2_zero_evidence: ZeroCaregiverRollbackEvidence,
) -> PhysicalOverheadReport:
    """Validate paired semantic identity, then measure real physical overhead."""

    left = capture_zero_caregiver_rollback_evidence(
        schema_v1_paths,
        previous=schema_v1_evidence,
    )
    right = capture_zero_caregiver_rollback_evidence(
        schema_v2_zero_paths,
        previous=schema_v2_zero_evidence,
    )
    assert_zero_caregiver_rollback_equivalent(
        schema_v1_paths,
        schema_v2_zero_paths,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )

    active_overhead = _safe_file_size(
        schema_v2_zero_paths.database,
        context="schema-v2 active database",
    ) - _safe_file_size(
        schema_v1_paths.database,
        context="schema-v1 active database",
    )
    if active_overhead < 0:
        raise PhysicalProjectionError(
            "schema-v2 active database is smaller than paired schema-v1 state"
        )
    if active_overhead > ACTIVE_DATABASE_OVERHEAD_CAP_BYTES:
        raise PhysicalProjectionError(
            "active database overhead exceeds the accepted cap"
        )

    checkpoint_overhead = _paired_database_overhead(
        left.retention.core.checkpoint_artifacts,
        right.retention.core.checkpoint_artifacts,
        context="checkpoint",
    )
    archive_overhead = _paired_database_overhead(
        left.rollback_archives,
        right.rollback_archives,
        context="rollback archive",
    )
    source_overhead = _paired_database_overhead(
        left.restore_candidates,
        right.restore_candidates,
        context="source candidate",
    )
    transformed_overhead = _paired_database_overhead(
        left.transformed_candidates,
        right.transformed_candidates,
        context="transformed candidate",
    )

    left_metadata = _artifact_metadata_bytes(left)
    right_metadata = _artifact_metadata_bytes(right)
    metadata_overhead = right_metadata - left_metadata
    if metadata_overhead < 0:
        raise PhysicalProjectionError(
            "schema-v2 aggregate artifact metadata is smaller than schema-v1"
        )
    if metadata_overhead > METADATA_OVERHEAD_CAP_BYTES:
        raise PhysicalProjectionError(
            "aggregate metadata overhead exceeds the accepted cap"
        )

    return PhysicalOverheadReport(
        active_database_overhead_bytes=active_overhead,
        checkpoint_database_overhead_bytes=checkpoint_overhead,
        rollback_archive_database_overhead_bytes=archive_overhead,
        source_candidate_database_overhead_bytes=source_overhead,
        transformed_candidate_database_overhead_bytes=transformed_overhead,
        schema_v1_total_artifact_metadata_bytes=left_metadata,
        schema_v2_total_artifact_metadata_bytes=right_metadata,
        aggregate_metadata_overhead_bytes=metadata_overhead,
    )


__all__ = [
    "ACTIVE_DATABASE_OVERHEAD_CAP_BYTES",
    "ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES",
    "METADATA_OVERHEAD_CAP_BYTES",
    "PhysicalOverheadReport",
    "PhysicalProjectionError",
    "measure_zero_caregiver_physical_overhead",
]
