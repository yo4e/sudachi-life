from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_projection import ZeroCaregiverProjectionError
from sudachi_life.phase2_rollback_projection import (
    BYTE_DERIVED_SENTINEL,
    SCHEMA_SENTINEL,
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


def _advance_one_water_wake(runtime_root: Path, paths: OrganismPaths) -> None:
    enqueue_garden_tick(
        paths,
        "water-before-rollback",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    wake = perform_garden_wake(
        runtime_root,
        "paired",
        seed=1,
        clock=_wake_clock(300),
    )
    assert wake.checkpoint.event_sequence == 13


def _prepared_pair(tmp_path: Path):
    v1_root, v1, v2_root, v2 = _paired(tmp_path)
    _advance_one_water_wake(v1_root, v1)
    _advance_one_water_wake(v2_root, v2)
    left = capture_zero_caregiver_rollback_evidence(v1)
    right = capture_zero_caregiver_rollback_evidence(v2)
    return v1_root, v1, v2_root, v2, left, right


def _event_payload(
    projection: dict[str, object],
    event_type: str,
    *,
    lineage_generation: int,
) -> dict[str, object]:
    rows = projection["rollback_event_evidence"]
    return next(
        row["payload_json"]
        for row in rows
        if row["event_type"] == event_type
        and row["lineage_generation"] == lineage_generation
    )


def _replace_event_payload(
    database: Path,
    *,
    event_type: str,
    lineage_generation: int,
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
            "UPDATE event SET payload_json=? "
            "WHERE event_type=? AND lineage_generation=?",
            (
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
                event_type,
                lineage_generation,
            ),
        )
        for row in triggers:
            connection.execute(row["sql"])
    finally:
        connection.close()


def test_paired_pre_rollback_archive_projects_ra_and_checkpoint_links(
    tmp_path: Path,
) -> None:
    v1_root, v1, v2_root, v2, left_before, right_before = _prepared_pair(tmp_path)
    prepare_rollback_archive(v1_root, "paired", 2)
    prepare_rollback_archive(v2_root, "paired", 2)

    left = capture_zero_caregiver_rollback_evidence(v1, previous=left_before)
    right = capture_zero_caregiver_rollback_evidence(v2, previous=right_before)
    assert_zero_caregiver_rollback_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )

    projection = project_zero_caregiver_rollback_state(v2, evidence=right)
    assert projection["projection_version"] == "phase1-projection-v2/rollback"
    assert len(projection["rollback_archives"]) == 1
    archive = projection["rollback_archives"][0]
    assert archive["archive"] == "RA(0,14,2)"
    assert archive["manifest"]["archive_id"] == "RA(0,14,2)"
    assert archive["manifest"]["latest_stable_checkpoint_id"] == "CP(0,13)"
    assert archive["manifest"]["selected_checkpoint_id"] == "CP(0,2)"
    assert archive["manifest"]["schema_version"] == SCHEMA_SENTINEL
    assert archive["manifest"]["database_sha256"] == BYTE_DERIVED_SENTINEL
    assert archive["manifest"]["database_size_bytes"] == BYTE_DERIVED_SENTINEL
    assert (
        archive["manifest"]["selected_checkpoint_manifest_sha256"]
        == BYTE_DERIVED_SENTINEL
    )
    assert (
        archive["manifest"]["selected_checkpoint_database_sha256"]
        == BYTE_DERIVED_SENTINEL
    )
    assert (
        archive["manifest"]["selected_checkpoint_database_size_bytes"]
        == BYTE_DERIVED_SENTINEL
    )


def test_paired_rollback_started_projects_exact_abandoned_chain(tmp_path: Path) -> None:
    v1_root, v1, v2_root, v2, left, right = _prepared_pair(tmp_path)
    archive1 = prepare_rollback_archive(v1_root, "paired", 2)
    archive2 = prepare_rollback_archive(v2_root, "paired", 2)
    begin_rollback(
        v1_root,
        "paired",
        archive1.archive_id,
        clock=FakeClock.fixed(1_710_000_000_000_000, 11_000_000),
    )
    begin_rollback(
        v2_root,
        "paired",
        archive2.archive_id,
        clock=FakeClock.fixed(1_710_000_000_000_000, 11_000_000),
    )

    left = capture_zero_caregiver_rollback_evidence(v1, previous=left)
    right = capture_zero_caregiver_rollback_evidence(v2, previous=right)
    assert_zero_caregiver_rollback_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )
    projection = project_zero_caregiver_rollback_state(v2, evidence=right)
    assert _event_payload(
        projection,
        "rollback_started",
        lineage_generation=0,
    ) == {
        "archive_database_sha256": BYTE_DERIVED_SENTINEL,
        "archive_id": "RA(0,14,2)",
        "archive_manifest_sha256": BYTE_DERIVED_SENTINEL,
        "latest_stable_checkpoint_id": "CP(0,13)",
        "latest_stable_event_sequence": 13,
        "pre_rollback_event_sequence": 14,
        "pre_rollback_lifecycle_number": 1,
        "pre_rollback_lineage_generation": 0,
        "pre_rollback_status": "sleeping",
        "selected_checkpoint_database_sha256": BYTE_DERIVED_SENTINEL,
        "selected_checkpoint_event_sequence": 2,
        "selected_checkpoint_id": "CP(0,2)",
        "selected_checkpoint_lineage_generation": 0,
        "selected_checkpoint_manifest_sha256": BYTE_DERIVED_SENTINEL,
    }


def test_paired_source_and_transformed_candidates_project_rc_tc_and_event(
    tmp_path: Path,
) -> None:
    v1_root, v1, v2_root, v2, left, right = _prepared_pair(tmp_path)
    archive1 = prepare_rollback_archive(v1_root, "paired", 2)
    archive2 = prepare_rollback_archive(v2_root, "paired", 2)
    begin_rollback(
        v1_root,
        "paired",
        archive1.archive_id,
        clock=FakeClock.fixed(1_710_000_000_000_000, 11_000_000),
    )
    begin_rollback(
        v2_root,
        "paired",
        archive2.archive_id,
        clock=FakeClock.fixed(1_710_000_000_000_000, 11_000_000),
    )
    source1 = build_restore_candidate(v1_root, "paired")
    source2 = build_restore_candidate(v2_root, "paired")
    transform_restore_candidate(
        v1_root,
        "paired",
        source1.candidate_id,
        "paired rollback",
        clock=FakeClock.fixed(1_720_000_000_000_000, 12_000_000),
    )
    transform_restore_candidate(
        v2_root,
        "paired",
        source2.candidate_id,
        "paired rollback",
        clock=FakeClock.fixed(1_720_000_000_000_000, 12_000_000),
    )

    left = capture_zero_caregiver_rollback_evidence(v1, previous=left)
    right = capture_zero_caregiver_rollback_evidence(v2, previous=right)
    assert_zero_caregiver_rollback_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )
    projection = project_zero_caregiver_rollback_state(v2, evidence=right)
    assert [item["candidate"] for item in projection["restore_candidates"]] == [
        "RC(0,15,2)"
    ]
    assert [item["candidate"] for item in projection["transformed_candidates"]] == [
        "TC(1,3)"
    ]
    transformed = projection["transformed_candidates"][0]
    assert transformed["manifest"]["source_restore_candidate_id"] == "RC(0,15,2)"
    assert transformed["manifest"]["archive_id"] == "RA(0,14,2)"
    assert transformed["manifest"]["selected_checkpoint_id"] == "CP(0,2)"
    assert _event_payload(
        projection,
        "rollback_lineage_prepared",
        lineage_generation=1,
    ) == {
        "administrative_reason": "paired rollback",
        "archive_database_sha256": BYTE_DERIVED_SENTINEL,
        "archive_id": "RA(0,14,2)",
        "archive_manifest_sha256": BYTE_DERIVED_SENTINEL,
        "abandoned_event_sequence": 14,
        "abandoned_lifecycle_number": 1,
        "abandoned_lineage_generation": 0,
        "new_lineage_generation": 1,
        "rollback_started_event_sequence": 15,
        "selected_checkpoint_database_sha256": BYTE_DERIVED_SENTINEL,
        "selected_checkpoint_event_sequence": 2,
        "selected_checkpoint_id": "CP(0,2)",
        "selected_checkpoint_lineage_generation": 0,
        "selected_checkpoint_manifest_sha256": BYTE_DERIVED_SENTINEL,
        "source_restore_candidate_database_sha256": BYTE_DERIVED_SENTINEL,
        "source_restore_candidate_id": "RC(0,15,2)",
        "source_restore_candidate_manifest_sha256": BYTE_DERIVED_SENTINEL,
        "status_after": "rollback_in_progress",
    }


def test_paired_replacement_and_completion_preserve_abandoned_checkpoint_evidence(
    tmp_path: Path,
) -> None:
    v1_root, v1, v2_root, v2, left, right = _prepared_pair(tmp_path)
    archive1 = prepare_rollback_archive(v1_root, "paired", 2)
    archive2 = prepare_rollback_archive(v2_root, "paired", 2)
    begin_rollback(
        v1_root,
        "paired",
        archive1.archive_id,
        clock=FakeClock.fixed(1_710_000_000_000_000, 11_000_000),
    )
    begin_rollback(
        v2_root,
        "paired",
        archive2.archive_id,
        clock=FakeClock.fixed(1_710_000_000_000_000, 11_000_000),
    )
    source1 = build_restore_candidate(v1_root, "paired")
    source2 = build_restore_candidate(v2_root, "paired")
    transformed1 = transform_restore_candidate(
        v1_root,
        "paired",
        source1.candidate_id,
        "paired rollback",
        clock=FakeClock.fixed(1_720_000_000_000_000, 12_000_000),
    )
    transformed2 = transform_restore_candidate(
        v2_root,
        "paired",
        source2.candidate_id,
        "paired rollback",
        clock=FakeClock.fixed(1_720_000_000_000_000, 12_000_000),
    )
    replace_active_with_candidate(v1_root, "paired", transformed1.transformed_candidate_id)
    replace_active_with_candidate(v2_root, "paired", transformed2.transformed_candidate_id)

    left = capture_zero_caregiver_rollback_evidence(v1, previous=left)
    right = capture_zero_caregiver_rollback_evidence(v2, previous=right)
    assert_zero_caregiver_rollback_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )
    replaced_projection = project_zero_caregiver_rollback_state(v2, evidence=right)
    assert replaced_projection["preserved_abandoned_checkpoints"] == ["CP(0,13)"]
    assert replaced_projection["tables"]["organism"][0][
        "latest_stable_checkpoint_id"
    ] == "CP(0,2)"

    complete_rollback(
        v1_root,
        "paired",
        transformed1.transformed_candidate_id,
        clock=FakeClock.fixed(1_730_000_000_000_000, 13_000_000),
    )
    complete_rollback(
        v2_root,
        "paired",
        transformed2.transformed_candidate_id,
        clock=FakeClock.fixed(1_730_000_000_000_000, 13_000_000),
    )
    left = capture_zero_caregiver_rollback_evidence(v1, previous=left)
    right = capture_zero_caregiver_rollback_evidence(v2, previous=right)
    assert_zero_caregiver_rollback_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )
    projection = project_zero_caregiver_rollback_state(v2, evidence=right)
    completion = _event_payload(
        projection,
        "rollback_completed",
        lineage_generation=1,
    )
    assert completion["archive_id"] == "RA(0,14,2)"
    assert completion["selected_checkpoint_id"] == "CP(0,2)"
    assert completion["source_restore_candidate_id"] == "RC(0,15,2)"
    assert completion["transformed_candidate_id"] == "TC(1,3)"
    assert completion["rollback_started_event_sequence"] == 15
    assert completion["restoration_event_sequence"] == 3
    assert completion["completion_event_sequence"] == 4
    for key in (
        "archive_database_sha256",
        "archive_manifest_sha256",
        "selected_checkpoint_database_sha256",
        "selected_checkpoint_manifest_sha256",
        "source_restore_candidate_database_sha256",
        "source_restore_candidate_manifest_sha256",
        "transformed_candidate_database_sha256",
        "transformed_candidate_manifest_sha256",
    ):
        assert completion[key] == BYTE_DERIVED_SENTINEL


def test_rollback_started_digest_is_validated_before_projection(tmp_path: Path) -> None:
    v1_root, v1, _v2_root, _v2, left, _right = _prepared_pair(tmp_path)
    archive = prepare_rollback_archive(v1_root, "paired", 2)
    begin_rollback(
        v1_root,
        "paired",
        archive.archive_id,
        clock=FakeClock.fixed(1_710_000_000_000_000, 11_000_000),
    )
    connection = connect_database(v1.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT payload_json FROM event WHERE event_type='rollback_started'"
        ).fetchone()
    finally:
        connection.close()
    payload = json.loads(row["payload_json"])
    payload["archive_database_sha256"] = "0" * 64
    _replace_event_payload(
        v1.database,
        event_type="rollback_started",
        lineage_generation=0,
        payload=payload,
    )

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="rollback_started archive database digest does not match archive",
    ):
        capture_zero_caregiver_rollback_evidence(v1, previous=left)
