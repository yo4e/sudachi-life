from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudachi_life.checkpoints import reconcile_checkpoint_retention_staging
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_retention_projection import (
    BYTE_DERIVED_SENTINEL,
    ZeroCaregiverProjectionError,
    assert_zero_caregiver_retention_equivalent,
    capture_zero_caregiver_retention_evidence,
    project_zero_caregiver_retention_state,
)
from sudachi_life.phase2_schema import ZERO_CAREGIVER_CONFIGURATION_VERSION
from sudachi_life.storage import connect_database


def _clock() -> FakeClock:
    return FakeClock.fixed(
        wall_time_utc_us=1_700_000_000_000_000,
        monotonic_ns=10_000_000,
    )


def _wake_clock(base: int) -> FakeClock:
    return FakeClock(
        [
            ClockReading(base, 10_000_000),
            ClockReading(base, 15_000_000),
            ClockReading(base + 1, 20_000_000),
            ClockReading(base + 2, 30_000_000),
            ClockReading(base + 3, 40_000_000),
        ]
    )


def _paired(tmp_path: Path) -> tuple[Path, OrganismPaths, Path, OrganismPaths]:
    v1_root = tmp_path / "v1"
    v2_root = tmp_path / "v2"
    initialize_organism(v1_root, "paired", clock=_clock())
    initialize_organism(
        v2_root,
        "paired",
        clock=_clock(),
        schema_version=2,
        consultation_configuration_version=ZERO_CAREGIVER_CONFIGURATION_VERSION,
    )
    return (
        v1_root,
        OrganismPaths.build(v1_root, "paired"),
        v2_root,
        OrganismPaths.build(v2_root, "paired"),
    )


def _enqueue_and_wake(
    runtime_root: Path,
    paths: OrganismPaths,
    index: int,
    *,
    retention_failure_after_stage: bool = False,
    retention_cleanup_failure_after_commit: bool = False,
):
    base = 200 + (index * 200)
    enqueue_garden_tick(
        paths,
        f"tick-{index}",
        clock=FakeClock([ClockReading(base - 100, base * 1_000)]),
    )

    def perform():
        return perform_garden_wake(
            runtime_root,
            "paired",
            seed=index,
            clock=_wake_clock(base),
            protected_test_retention_failure_after_stage=retention_failure_after_stage,
        )

    if not retention_cleanup_failure_after_commit:
        return perform()

    import sudachi_life.checkpoint_retention_prune as retention_prune

    original_rmtree = retention_prune.shutil.rmtree

    def fail_staging_cleanup(path, *args, **kwargs):
        if Path(path).name.startswith(".pruning-"):
            raise OSError("protected post-commit cleanup failure")
        return original_rmtree(path, *args, **kwargs)

    retention_prune.shutil.rmtree = fail_staging_cleanup
    try:
        return perform()
    finally:
        retention_prune.shutil.rmtree = original_rmtree


def _prepare_retention_pair(tmp_path: Path):
    v1_root, v1, v2_root, v2 = _paired(tmp_path)
    for index in range(1, 4):
        _enqueue_and_wake(v1_root, v1, index)
        _enqueue_and_wake(v2_root, v2, index)
    left = capture_zero_caregiver_retention_evidence(v1)
    right = capture_zero_caregiver_retention_evidence(v2)
    assert left.core.retained_checkpoint_boundaries == ((0, 2), (0, 13), (0, 24), (0, 34))
    assert right.core.retained_checkpoint_boundaries == ((0, 2), (0, 13), (0, 24), (0, 34))
    return v1_root, v1, v2_root, v2, left, right


def _event_payload(projection: dict[str, object], event_type: str) -> dict[str, object]:
    rows = projection["tables"]["event"]
    return next(row["payload_json"] for row in rows if row["event_type"] == event_type)


def _replace_event_payload(
    database: Path,
    event_sequence: int,
    payload: dict[str, object],
) -> None:
    connection = connect_database(database)
    try:
        triggers = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
            "AND name IN ('event_no_update','event_no_delete') ORDER BY name"
        ).fetchall()
        for row in triggers:
            connection.execute(f"DROP TRIGGER {row['name']}")
        connection.execute(
            "UPDATE event SET payload_json=? WHERE event_sequence=?",
            (json.dumps(payload, sort_keys=True, separators=(",", ":")), event_sequence),
        )
        for row in triggers:
            connection.execute(row["sql"])
    finally:
        connection.close()


def test_paired_normal_checkpoint_prune_projects_exactly(tmp_path: Path) -> None:
    v1_root, v1, v2_root, v2, left_before, right_before = _prepare_retention_pair(
        tmp_path
    )
    _enqueue_and_wake(v1_root, v1, 4)
    _enqueue_and_wake(v2_root, v2, 4)

    left = capture_zero_caregiver_retention_evidence(v1, previous=left_before)
    right = capture_zero_caregiver_retention_evidence(v2, previous=right_before)
    assert_zero_caregiver_retention_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )

    projection = project_zero_caregiver_retention_state(v2, evidence=right)
    payload = _event_payload(projection, "checkpoint_pruned")
    assert payload == {
        "latest_stable_checkpoint_id": "CP(0,44)",
        "latest_stable_event_sequence": 44,
        "pruned_artifact_size_bytes": BYTE_DERIVED_SENTINEL,
        "pruned_checkpoint_id": "CP(0,13)",
        "pruned_database_size_bytes": BYTE_DERIVED_SENTINEL,
        "pruned_event_sequence": 13,
        "pruned_lineage_generation": 0,
        "pruned_provenance": "lifecycle",
        "reason": "checkpoint_retention_limit",
        "retained_checkpoint_count": 4,
        "retained_checkpoint_store_bytes": BYTE_DERIVED_SENTINEL,
        "retention_limit": 4,
    }
    assert projection["retention_staging_artifacts"] == []


def test_normal_prune_requires_a_predeletion_artifact_witness(tmp_path: Path) -> None:
    v1_root, v1, _v2_root, _v2, _left_before, _right_before = _prepare_retention_pair(
        tmp_path
    )
    _enqueue_and_wake(v1_root, v1, 4)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="pruned checkpoint boundary has no artifact evidence",
    ):
        capture_zero_caregiver_retention_evidence(v1)


def test_paired_precommit_retention_failure_restores_candidate(tmp_path: Path) -> None:
    v1_root, v1, v2_root, v2, left_before, right_before = _prepare_retention_pair(
        tmp_path
    )
    _enqueue_and_wake(v1_root, v1, 4, retention_failure_after_stage=True)
    _enqueue_and_wake(v2_root, v2, 4, retention_failure_after_stage=True)

    left = capture_zero_caregiver_retention_evidence(v1, previous=left_before)
    right = capture_zero_caregiver_retention_evidence(v2, previous=right_before)
    assert_zero_caregiver_retention_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )

    projection = project_zero_caregiver_retention_state(v2, evidence=right)
    payload = _event_payload(projection, "checkpoint_retention_failed")
    assert payload == {
        "candidate_checkpoint_id": "CP(0,13)",
        "candidate_event_sequence": 13,
        "candidate_restored": True,
        "checkpoint_store_bytes": BYTE_DERIVED_SENTINEL,
        "injection_point": "after_artifact_stage_before_registry_mutation",
        "latest_stable_checkpoint_id": "CP(0,44)",
        "latest_stable_event_sequence": 44,
        "maintenance_reason": MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
        "reason": "protected_test_injected_checkpoint_retention_failure",
        "registered_checkpoint_boundaries": [2, 13, 24, 34, 44],
        "registered_checkpoint_count": 5,
        "retention_limit": 4,
        "stable_checkpoint_count": 5,
        "status_after": "maintenance_required",
    }
    assert projection["retention_staging_artifacts"] == []


def test_paired_postcommit_cleanup_failure_projects_exact_stage(tmp_path: Path) -> None:
    v1_root, v1, v2_root, v2, left_before, right_before = _prepare_retention_pair(
        tmp_path
    )
    _enqueue_and_wake(v1_root, v1, 4, retention_cleanup_failure_after_commit=True)
    _enqueue_and_wake(v2_root, v2, 4, retention_cleanup_failure_after_commit=True)

    left = capture_zero_caregiver_retention_evidence(v1, previous=left_before)
    right = capture_zero_caregiver_retention_evidence(v2, previous=right_before)
    assert_zero_caregiver_retention_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )

    projection = project_zero_caregiver_retention_state(v2, evidence=right)
    payload = _event_payload(projection, "checkpoint_retention_failed")
    assert payload == {
        "candidate_checkpoint_id": "CP(0,13)",
        "candidate_event_sequence": 13,
        "candidate_restored": False,
        "checkpoint_store_bytes": BYTE_DERIVED_SENTINEL,
        "injection_point": "after_registry_commit_before_staging_cleanup",
        "latest_stable_checkpoint_id": "CP(0,44)",
        "latest_stable_event_sequence": 44,
        "maintenance_reason": MAINTENANCE_REASON_CHECKPOINT_RETENTION_FAILED,
        "reason": "post_commit_staging_cleanup_failed",
        "registered_checkpoint_boundaries": [2, 24, 34, 44],
        "registered_checkpoint_count": 4,
        "retention_limit": 4,
        "stable_checkpoint_count": 4,
        "staging_directory": "STAGE(CP(0,13))",
        "status_after": "maintenance_required",
    }
    assert projection["retention_staging_artifacts"] == [
        {
            "checkpoint": "CP(0,13)",
            "staging_directory": "STAGE(CP(0,13))",
        }
    ]


def test_interrupted_reconciliation_reuses_witness_and_retry_completes(
    tmp_path: Path,
) -> None:
    v1_root, v1, v2_root, v2, left_before, right_before = _prepare_retention_pair(
        tmp_path
    )
    _enqueue_and_wake(v1_root, v1, 4, retention_cleanup_failure_after_commit=True)
    _enqueue_and_wake(v2_root, v2, 4, retention_cleanup_failure_after_commit=True)
    left_staged = capture_zero_caregiver_retention_evidence(v1, previous=left_before)
    right_staged = capture_zero_caregiver_retention_evidence(v2, previous=right_before)

    with pytest.raises(CheckpointError, match="after deletion before completion"):
        reconcile_checkpoint_retention_staging(
            v1_root,
            "paired",
            clock=FakeClock([ClockReading(1300, 13_000_000)]),
            protected_test_failure_after_delete_before_completion=True,
        )
    with pytest.raises(CheckpointError, match="after deletion before completion"):
        reconcile_checkpoint_retention_staging(
            v2_root,
            "paired",
            clock=FakeClock([ClockReading(1300, 13_000_000)]),
            protected_test_failure_after_delete_before_completion=True,
        )

    left_pending = capture_zero_caregiver_retention_evidence(v1, previous=left_staged)
    right_pending = capture_zero_caregiver_retention_evidence(v2, previous=right_staged)
    assert_zero_caregiver_retention_equivalent(
        v1,
        v2,
        schema_v1_evidence=left_pending,
        schema_v2_zero_evidence=right_pending,
    )
    pending_projection = project_zero_caregiver_retention_state(
        v2,
        evidence=right_pending,
    )
    assert _event_payload(
        pending_projection,
        "checkpoint_retention_cleanup_reconciliation_pending",
    ) == {
        "checkpoint_ids": ["CP(0,13)"],
        "reason": "committed_prune_cleanup_reconciliation",
        "staging_directories": ["STAGE(CP(0,13))"],
        "status_before": "maintenance_required",
    }
    assert pending_projection["retention_staging_artifacts"] == []

    reconcile_checkpoint_retention_staging(v1_root, "paired", clock=FakeClock([]))
    reconcile_checkpoint_retention_staging(v2_root, "paired", clock=FakeClock([]))
    left_done = capture_zero_caregiver_retention_evidence(v1, previous=left_pending)
    right_done = capture_zero_caregiver_retention_evidence(v2, previous=right_pending)
    assert_zero_caregiver_retention_equivalent(
        v1,
        v2,
        schema_v1_evidence=left_done,
        schema_v2_zero_evidence=right_done,
    )
    done_projection = project_zero_caregiver_retention_state(v2, evidence=right_done)
    assert _event_payload(
        done_projection,
        "checkpoint_retention_cleanup_reconciled",
    ) == {
        "reason": "committed_prune_cleanup_reconciled",
        "reconciliation_pending_event_sequence": 48,
        "removed_staging_directories": ["STAGE(CP(0,13))"],
        "status_after": "maintenance_required",
    }


def test_retention_stage_path_is_validated_before_projection(tmp_path: Path) -> None:
    v1_root, v1, _v2_root, _v2, left_before, _right_before = _prepare_retention_pair(
        tmp_path
    )
    _enqueue_and_wake(v1_root, v1, 4, retention_cleanup_failure_after_commit=True)
    connection = connect_database(v1.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT event_sequence, payload_json FROM event "
            "WHERE event_type='checkpoint_retention_failed'"
        ).fetchone()
    finally:
        connection.close()
    payload = json.loads(row["payload_json"])
    payload["staging_directory"] = ".pruning-wrong"
    _replace_event_payload(v1.database, int(row["event_sequence"]), payload)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="retention staging directory does not match witnessed artifact",
    ):
        capture_zero_caregiver_retention_evidence(v1, previous=left_before)
