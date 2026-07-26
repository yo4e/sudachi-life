from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.event_export import export_stable_events
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_event_export_projection import (
    SCHEMA_SENTINEL,
    ZeroCaregiverProjectionError,
    assert_zero_caregiver_event_exports_equivalent,
    capture_zero_caregiver_event_export_evidence,
    project_zero_caregiver_event_export,
)
from sudachi_life.phase2_rollback_projection import (
    capture_zero_caregiver_rollback_evidence,
)
from sudachi_life.phase2_schema import ZERO_CAREGIVER_CONFIGURATION_VERSION


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


def _paired_water_exports(tmp_path: Path):
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
    v1 = OrganismPaths.build(v1_root, "paired")
    v2 = OrganismPaths.build(v2_root, "paired")
    checkpoints = []
    for root, paths in ((v1_root, v1), (v2_root, v2)):
        enqueue_garden_tick(
            paths,
            "export-water",
            clock=FakeClock([ClockReading(200, 2_000_000)]),
        )
        wake = perform_garden_wake(
            root,
            "paired",
            seed=1,
            clock=_wake_clock(300),
        )
        checkpoints.append(wake.checkpoint)
    left_projection = capture_zero_caregiver_rollback_evidence(v1)
    right_projection = capture_zero_caregiver_rollback_evidence(v2)
    left_export = export_stable_events(
        v1_root,
        "paired",
        checkpoints[0].event_sequence,
    )
    right_export = export_stable_events(
        v2_root,
        "paired",
        checkpoints[1].event_sequence,
    )
    return (
        v1,
        v2,
        left_projection,
        right_projection,
        left_export,
        right_export,
    )


def _canonical_line(value: dict[str, object]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def test_paired_water_exports_compare_semantically_after_independent_validation(
    tmp_path: Path,
) -> None:
    (
        v1,
        v2,
        left_projection,
        right_projection,
        left_export,
        right_export,
    ) = _paired_water_exports(tmp_path)
    assert left_export.export_path.read_bytes() != right_export.export_path.read_bytes()

    left = capture_zero_caregiver_event_export_evidence(
        v1,
        left_export.export_path,
        projection_evidence=left_projection,
    )
    right = capture_zero_caregiver_event_export_evidence(
        v2,
        right_export.export_path,
        projection_evidence=right_projection,
    )
    assert_zero_caregiver_event_exports_equivalent(
        v1,
        v2,
        left,
        right,
        schema_v1_projection_evidence=left_projection,
        schema_v2_zero_projection_evidence=right_projection,
    )

    projected = project_zero_caregiver_event_export(
        v2,
        right,
        projection_evidence=right_projection,
    )
    assert projected["projection_version"] == "phase1-projection-v2/event-export"
    assert projected["manifest"]["source_checkpoint_id"] == "CP(0,13)"
    assert projected["manifest"]["schema_version"] == SCHEMA_SENTINEL
    assert projected["manifest"]["event_count"] == 13
    assert [record["event_sequence"] for record in projected["events"]] == list(
        range(1, 14)
    )
    stabilized = next(
        record
        for record in projected["events"]
        if record["event_type"] == "checkpoint_stabilized"
    )
    assert stabilized["payload"]["checkpoint_id"] == "CP(0,2)"
    assert all(record["schema_version"] == SCHEMA_SENTINEL for record in projected["events"])


def test_export_projection_rejects_canonical_tampering_before_semantic_replacement(
    tmp_path: Path,
) -> None:
    (
        _v1,
        v2,
        _left_projection,
        right_projection,
        _left_export,
        right_export,
    ) = _paired_water_exports(tmp_path)
    records = [
        json.loads(line)
        for line in right_export.export_path.read_bytes().splitlines()
    ]
    stabilized = next(
        record
        for record in records[1:]
        if record["event_type"] == "checkpoint_stabilized"
    )
    stabilized["payload"]["checkpoint_id"] = "checkpoint:wrong"
    right_export.export_path.write_bytes(b"".join(_canonical_line(record) for record in records))

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="event export bytes do not match canonical reconstruction",
    ):
        capture_zero_caregiver_event_export_evidence(
            v2,
            right_export.export_path,
            projection_evidence=right_projection,
        )


def test_export_path_and_wrapper_bytes_are_noncanonical_only_after_file_validation(
    tmp_path: Path,
) -> None:
    (
        _v1,
        v2,
        _left_projection,
        right_projection,
        _left_export,
        right_export,
    ) = _paired_water_exports(tmp_path)
    original = capture_zero_caregiver_event_export_evidence(
        v2,
        right_export.export_path,
        projection_evidence=right_projection,
    )
    copied_path = right_export.export_path.parent / "presentation-copy.jsonl"
    copied_path.write_bytes(right_export.export_path.read_bytes())
    copied = capture_zero_caregiver_event_export_evidence(
        v2,
        copied_path,
        projection_evidence=right_projection,
    )
    assert project_zero_caregiver_event_export(
        v2,
        original,
        projection_evidence=right_projection,
    ) == project_zero_caregiver_event_export(
        v2,
        copied,
        projection_evidence=right_projection,
    )

    copied_path.write_bytes(copied_path.read_bytes().replace(b"\n", b" \n", 1))
    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="event export line is not canonical JSONL",
    ):
        capture_zero_caregiver_event_export_evidence(
            v2,
            copied_path,
            projection_evidence=right_projection,
        )
