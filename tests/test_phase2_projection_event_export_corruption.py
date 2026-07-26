from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudachi_life.phase2_event_export_projection import (
    ZeroCaregiverProjectionError,
    capture_zero_caregiver_event_export_evidence,
    project_zero_caregiver_event_export,
)

from test_phase2_projection_event_export import (
    _canonical_line,
    _paired_water_exports,
)


def test_export_projection_rejects_a_missing_event_record(tmp_path: Path) -> None:
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
    del records[6]
    right_export.export_path.write_bytes(b"".join(_canonical_line(record) for record in records))

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="event export count does not match its range",
    ):
        capture_zero_caregiver_event_export_evidence(
            v2,
            right_export.export_path,
            projection_evidence=right_projection,
        )


def test_captured_export_is_revalidated_before_projection(tmp_path: Path) -> None:
    (
        _v1,
        v2,
        _left_projection,
        right_projection,
        _left_export,
        right_export,
    ) = _paired_water_exports(tmp_path)
    evidence = capture_zero_caregiver_event_export_evidence(
        v2,
        right_export.export_path,
        projection_evidence=right_projection,
    )
    records = [
        json.loads(line)
        for line in right_export.export_path.read_bytes().splitlines()
    ]
    records[-1]["payload"]["post_capture_tamper"] = True
    right_export.export_path.write_bytes(b"".join(_canonical_line(record) for record in records))

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="event export bytes do not match canonical reconstruction",
    ):
        project_zero_caregiver_event_export(
            v2,
            evidence,
            projection_evidence=right_projection,
        )
