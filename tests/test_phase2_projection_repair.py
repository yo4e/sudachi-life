from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudachi_life.checkpoint_repair import repair_pending_checkpoint_registration
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_projection import (
    BYTE_DERIVED_SENTINEL,
    ZeroCaregiverProjectionError,
    assert_zero_caregiver_equivalent,
    capture_zero_caregiver_evidence,
    project_zero_caregiver_state,
)
from sudachi_life.phase2_schema import ZERO_CAREGIVER_CONFIGURATION_VERSION
from sudachi_life.storage import connect_database, read_status


def _clock() -> FakeClock:
    return FakeClock.fixed(
        wall_time_utc_us=1_700_000_000_000_000,
        monotonic_ns=10_000_000,
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


def _prepare_pending_orphan(runtime_root: Path, paths: OrganismPaths) -> None:
    enqueue_garden_tick(
        paths,
        "repair-tick",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    timeout_clock = FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 5_030_000_001),
        ]
    )
    with pytest.raises(CheckpointError, match="deadline"):
        perform_garden_wake(
            runtime_root,
            "paired",
            seed=1,
            clock=timeout_clock,
        )
    assert read_status(paths).status == "checkpoint_pending"


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
            (
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
                event_sequence,
            ),
        )
        for row in triggers:
            connection.execute(row["sql"])
    finally:
        connection.close()


def _repair_pair(tmp_path: Path):
    v1_root, v1, v2_root, v2 = _paired(tmp_path)
    _prepare_pending_orphan(v1_root, v1)
    _prepare_pending_orphan(v2_root, v2)
    repair_clock = FakeClock([ClockReading(400, 6_000_000_000)])
    repair_pending_checkpoint_registration(v1_root, "paired", clock=repair_clock)
    repair_clock = FakeClock([ClockReading(400, 6_000_000_000)])
    repair_pending_checkpoint_registration(v2_root, "paired", clock=repair_clock)
    left = capture_zero_caregiver_evidence(v1)
    right = capture_zero_caregiver_evidence(v2)
    return v1, v2, left, right


def test_paired_pending_checkpoint_repair_projects_exactly(tmp_path: Path) -> None:
    v1, v2, left, right = _repair_pair(tmp_path)

    assert_zero_caregiver_equivalent(
        v1,
        v2,
        schema_v1_evidence=left,
        schema_v2_zero_evidence=right,
    )
    projection = project_zero_caregiver_state(v2, evidence=right)
    repaired = next(
        row
        for row in projection["tables"]["event"]
        if row["event_type"] == "checkpoint_registration_repaired"
    )
    assert repaired["payload_json"] == {
        "checkpoint_id": "CP(0,13)",
        "checkpoint_store_bytes": BYTE_DERIVED_SENTINEL,
        "database_sha256": BYTE_DERIVED_SENTINEL,
        "database_size_bytes": BYTE_DERIVED_SENTINEL,
        "event_sequence": 13,
        "lineage_generation": 0,
        "manifest_sha256": BYTE_DERIVED_SENTINEL,
        "previous_latest_stable_checkpoint_id": "CP(0,2)",
        "previous_latest_stable_event_sequence": 2,
        "reason": "published_checkpoint_registration_missing",
        "status_after": "sleeping",
        "status_before": "checkpoint_pending",
    }


def test_repair_evidence_recomputes_all_projected_byte_fields(tmp_path: Path) -> None:
    _v1, v2, _left, _right = _repair_pair(tmp_path)
    connection = connect_database(v2.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT event_sequence, payload_json FROM event "
            "WHERE event_type='checkpoint_registration_repaired'"
        ).fetchone()
    finally:
        connection.close()
    payload = json.loads(row["payload_json"])
    payload["checkpoint_store_bytes"] = int(payload["checkpoint_store_bytes"]) + 1
    _replace_event_payload(v2.database, int(row["event_sequence"]), payload)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="repair checkpoint_store_bytes does not match measured store",
    ):
        capture_zero_caregiver_evidence(v2)


def test_repair_checkpoint_identity_is_linked_before_projection(tmp_path: Path) -> None:
    _v1, v2, _left, _right = _repair_pair(tmp_path)
    connection = connect_database(v2.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT event_sequence, payload_json FROM event "
            "WHERE event_type='checkpoint_registration_repaired'"
        ).fetchone()
    finally:
        connection.close()
    payload = json.loads(row["payload_json"])
    payload["checkpoint_id"] = "checkpoint:wrong"
    _replace_event_payload(v2.database, int(row["event_sequence"]), payload)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="repair checkpoint identity does not match artifact",
    ):
        capture_zero_caregiver_evidence(v2)
