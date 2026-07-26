from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.phase2_physical_projection import (
    ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES,
    METADATA_OVERHEAD_CAP_BYTES,
    PhysicalProjectionError,
    measure_zero_caregiver_physical_overhead,
)
from sudachi_life.phase2_rollback_projection import (
    capture_zero_caregiver_rollback_evidence,
)
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_complete import complete_rollback
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_replace import replace_active_with_candidate
from sudachi_life.rollback_transform import transform_restore_candidate

from test_phase2_projection_rollback import _prepared_pair, _rollback_clock


def test_paired_active_and_checkpoint_database_overhead_after_water(
    tmp_path: Path,
) -> None:
    _v1_root, v1, _v2_root, v2, left, right = _prepared_pair(tmp_path)
    report = measure_zero_caregiver_physical_overhead(v1, v2, left, right)

    assert 0 <= report.active_database_overhead_bytes <= 256 * 1024
    assert dict(report.checkpoint_database_overhead_bytes) == {
        "CP(0,2)": pytest.approx(
            dict(report.checkpoint_database_overhead_bytes)["CP(0,2)"], abs=0
        ),
        "CP(0,13)": pytest.approx(
            dict(report.checkpoint_database_overhead_bytes)["CP(0,13)"], abs=0
        ),
    }
    assert all(
        0 <= value <= ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES
        for _token, value in report.checkpoint_database_overhead_bytes
    )
    assert report.rollback_archive_database_overhead_bytes == ()
    assert report.source_candidate_database_overhead_bytes == ()
    assert report.transformed_candidate_database_overhead_bytes == ()
    assert 0 <= report.aggregate_metadata_overhead_bytes <= METADATA_OVERHEAD_CAP_BYTES


def _complete_full_rollback_pair(tmp_path: Path):
    v1_root, v1, v2_root, v2, left, right = _prepared_pair(tmp_path)
    archive1 = prepare_rollback_archive(v1_root, "paired", 2)
    archive2 = prepare_rollback_archive(v2_root, "paired", 2)
    begin_rollback(
        v1_root,
        "paired",
        archive1.archive_id,
        clock=_rollback_clock(1_710_000_000_000_000, 11_000_000),
    )
    begin_rollback(
        v2_root,
        "paired",
        archive2.archive_id,
        clock=_rollback_clock(1_710_000_000_000_000, 11_000_000),
    )
    source1 = build_restore_candidate(v1_root, "paired")
    source2 = build_restore_candidate(v2_root, "paired")
    transformed1 = transform_restore_candidate(
        v1_root,
        "paired",
        source1.candidate_id,
        "physical overhead pair",
        clock=_rollback_clock(1_720_000_000_000_000, 12_000_000),
    )
    transformed2 = transform_restore_candidate(
        v2_root,
        "paired",
        source2.candidate_id,
        "physical overhead pair",
        clock=_rollback_clock(1_720_000_000_000_000, 12_000_000),
    )
    replace_active_with_candidate(
        v1_root,
        "paired",
        transformed1.transformed_candidate_id,
    )
    replace_active_with_candidate(
        v2_root,
        "paired",
        transformed2.transformed_candidate_id,
    )
    left = capture_zero_caregiver_rollback_evidence(v1, previous=left)
    right = capture_zero_caregiver_rollback_evidence(v2, previous=right)
    complete_rollback(
        v1_root,
        "paired",
        transformed1.transformed_candidate_id,
        clock=_rollback_clock(1_730_000_000_000_000, 13_000_000),
    )
    complete_rollback(
        v2_root,
        "paired",
        transformed2.transformed_candidate_id,
        clock=_rollback_clock(1_730_000_000_000_000, 13_000_000),
    )
    left = capture_zero_caregiver_rollback_evidence(v1, previous=left)
    right = capture_zero_caregiver_rollback_evidence(v2, previous=right)
    return v1, v2, left, right


def test_full_retained_rollback_working_set_overhead_is_bounded(
    tmp_path: Path,
) -> None:
    v1, v2, left, right = _complete_full_rollback_pair(tmp_path)
    report = measure_zero_caregiver_physical_overhead(v1, v2, left, right)

    assert 0 <= report.active_database_overhead_bytes <= 256 * 1024
    assert {token for token, _value in report.checkpoint_database_overhead_bytes} == {
        "CP(0,2)",
        "CP(0,13)",
    }
    assert dict(report.rollback_archive_database_overhead_bytes).keys() == {
        "RA(0,14,2)"
    }
    assert dict(report.source_candidate_database_overhead_bytes).keys() == {
        "RC(0,15,2)"
    }
    assert dict(report.transformed_candidate_database_overhead_bytes).keys() == {
        "TC(1,3)"
    }
    for group in (
        report.checkpoint_database_overhead_bytes,
        report.rollback_archive_database_overhead_bytes,
        report.source_candidate_database_overhead_bytes,
        report.transformed_candidate_database_overhead_bytes,
    ):
        assert all(
            0 <= value <= ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES
            for _token, value in group
        )
    assert 0 <= report.aggregate_metadata_overhead_bytes <= METADATA_OVERHEAD_CAP_BYTES
    assert report.schema_v2_total_artifact_metadata_bytes >= 0
    assert report.schema_v1_total_artifact_metadata_bytes >= 0


def test_real_overhead_measurements_enforce_the_declared_caps(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    v1, v2, left, right = _complete_full_rollback_pair(tmp_path)
    report = measure_zero_caregiver_physical_overhead(v1, v2, left, right)
    largest_artifact_overhead = max(
        value
        for group in (
            report.checkpoint_database_overhead_bytes,
            report.rollback_archive_database_overhead_bytes,
            report.source_candidate_database_overhead_bytes,
            report.transformed_candidate_database_overhead_bytes,
        )
        for _token, value in group
    )

    import sudachi_life.phase2_physical_projection as physical

    monkeypatch.setattr(
        physical,
        "ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES",
        largest_artifact_overhead - 1,
    )
    with pytest.raises(
        PhysicalProjectionError,
        match="artifact database overhead exceeds the accepted cap",
    ):
        measure_zero_caregiver_physical_overhead(v1, v2, left, right)

    monkeypatch.setattr(
        physical,
        "ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES",
        ARTIFACT_DATABASE_OVERHEAD_CAP_BYTES,
    )
    monkeypatch.setattr(
        physical,
        "METADATA_OVERHEAD_CAP_BYTES",
        report.aggregate_metadata_overhead_bytes - 1,
    )
    with pytest.raises(
        PhysicalProjectionError,
        match="aggregate metadata overhead exceeds the accepted cap",
    ):
        measure_zero_caregiver_physical_overhead(v1, v2, left, right)
