from __future__ import annotations

from pathlib import Path

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_rollback_projection import (
    assert_zero_caregiver_rollback_equivalent,
    capture_zero_caregiver_rollback_evidence,
    project_zero_caregiver_rollback_state,
)
from sudachi_life.phase2_schema import ZERO_CAREGIVER_CONFIGURATION_VERSION
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_complete import complete_rollback
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_replace import replace_active_with_candidate
from sudachi_life.rollback_transform import transform_restore_candidate


def _fixed(wall: int, monotonic: int) -> FakeClock:
    return FakeClock.fixed(wall_time_utc_us=wall, monotonic_ns=monotonic)


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


def _initialize_pair(tmp_path: Path):
    v1_root = tmp_path / "v1"
    v2_root = tmp_path / "v2"
    initialize_organism(v1_root, "paired", clock=_fixed(100, 1_000_000))
    initialize_organism(
        v2_root,
        "paired",
        clock=_fixed(100, 1_000_000),
        schema_version=2,
        consultation_configuration_version=ZERO_CAREGIVER_CONFIGURATION_VERSION,
    )
    v1 = OrganismPaths.build(v1_root, "paired")
    v2 = OrganismPaths.build(v2_root, "paired")
    for root, paths in ((v1_root, v1), (v2_root, v2)):
        enqueue_garden_tick(
            paths,
            "water-before-latest-rollback",
            clock=FakeClock([ClockReading(200, 2_000_000)]),
        )
        wake = perform_garden_wake(
            root,
            "paired",
            seed=1,
            clock=_wake_clock(300),
        )
        assert wake.checkpoint.event_sequence == 13
    return v1_root, v1, v2_root, v2


def _complete_latest_rollback(root: Path, paths: OrganismPaths, previous):
    archive = prepare_rollback_archive(root, "paired", 13)
    begin_rollback(
        root,
        "paired",
        archive.archive_id,
        clock=_fixed(1_710_000_000_000_000, 11_000_000),
    )
    source = build_restore_candidate(root, "paired")
    transformed = transform_restore_candidate(
        root,
        "paired",
        source.candidate_id,
        "latest checkpoint collision",
        clock=_fixed(1_720_000_000_000_000, 12_000_000),
    )
    before_replace = capture_zero_caregiver_rollback_evidence(
        paths,
        previous=previous,
    )
    replace_active_with_candidate(
        root,
        "paired",
        transformed.transformed_candidate_id,
    )
    complete_rollback(
        root,
        "paired",
        transformed.transformed_candidate_id,
        clock=_fixed(1_730_000_000_000_000, 13_000_000),
    )
    return capture_zero_caregiver_rollback_evidence(
        paths,
        previous=before_replace,
    )


def test_rollback_event_evidence_is_lineage_keyed_when_sequences_reuse(
    tmp_path: Path,
) -> None:
    v1_root, v1, v2_root, v2 = _initialize_pair(tmp_path)
    left_initial = capture_zero_caregiver_rollback_evidence(v1)
    right_initial = capture_zero_caregiver_rollback_evidence(v2)
    left = _complete_latest_rollback(v1_root, v1, left_initial)
    right = _complete_latest_rollback(v2_root, v2, right_initial)

    assert_zero_caregiver_rollback_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )
    projection = project_zero_caregiver_rollback_state(v2, evidence=right)
    boundaries = {
        (
            row["lineage_generation"],
            row["event_sequence"],
            row["event_type"],
        )
        for row in projection["rollback_event_evidence"]
    }
    assert (0, 15, "rollback_started") in boundaries
    assert (1, 15, "rollback_completed") in boundaries
