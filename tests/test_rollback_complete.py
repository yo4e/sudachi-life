from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sudachi_life.cli import main
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake, perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_complete import (
    RollbackCompletionBusyError,
    RollbackCompletionRejectedError,
    complete_rollback,
)
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_replace import replace_active_with_candidate
from sudachi_life.rollback_transform import transform_restore_candidate
from sudachi_life.storage import connect_database, read_status, validate_canonical_state
from sudachi_life.wake import WakeRejectedError


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_snapshot(root: Path) -> dict[str, tuple[int, str]]:
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): (path.stat().st_size, _digest(path))
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _active_snapshot(paths: OrganismPaths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "database_size": paths.database.stat().st_size,
            "database_sha256": _digest(paths.database),
            "organism": tuple(
                connection.execute(
                    "SELECT * FROM organism WHERE singleton_id = 1"
                ).fetchone()
            ),
            "events": [
                tuple(row)
                for row in connection.execute(
                    "SELECT * FROM event ORDER BY event_sequence"
                ).fetchall()
            ],
            "inbox": [
                tuple(row)
                for row in connection.execute(
                    "SELECT * FROM inbox_event ORDER BY inbox_id"
                ).fetchall()
            ],
            "registry": [
                tuple(row)
                for row in connection.execute(
                    "SELECT * FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"
                ).fetchall()
            ],
            "environment": tuple(
                connection.execute(
                    "SELECT * FROM environment_state WHERE singleton_id = 1"
                ).fetchone()
            ),
        }
    finally:
        connection.close()


def _artifacts(paths: OrganismPaths) -> dict[str, object]:
    return {
        "checkpoints": _tree_snapshot(paths.checkpoints),
        "archives": _tree_snapshot(paths.rollback_archives),
        "candidates": _tree_snapshot(paths.restore_candidates),
    }


def _prepare_completion(initialized):
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
    begin = begin_rollback(
        runtime_root,
        initial.organism_id,
        archive.archive_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=1_710_000_000_000_000,
            monotonic_ns=11_000_000,
        ),
    )
    source = build_restore_candidate(runtime_root, initial.organism_id)
    transformed = transform_restore_candidate(
        runtime_root,
        initial.organism_id,
        source.candidate_id,
        "protected rollback completion",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_720_000_000_000_000,
            monotonic_ns=12_000_000,
        ),
    )
    replacement = replace_active_with_candidate(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
    )
    return (
        runtime_root,
        initial,
        genesis,
        paths,
        archive,
        begin,
        source,
        transformed,
        replacement,
    )


def test_complete_rollback_atomically_records_completion_and_enables_wake(
    initialized,
    capsys,
) -> None:
    (
        runtime_root,
        initial,
        genesis,
        paths,
        archive,
        begin,
        source,
        transformed,
        replacement,
    ) = _prepare_completion(initialized)
    active_before = _active_snapshot(paths)
    artifacts_before = _artifacts(paths)

    blocked_clock = FakeClock([])
    with pytest.raises(
        WakeRejectedError,
        match="organism is not wakeable: status=rollback_in_progress",
    ):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=1,
            clock=blocked_clock,
        )
    assert blocked_clock.read_count == 0

    clock = FakeClock.fixed(
        wall_time_utc_us=1_730_000_000_000_000,
        monotonic_ns=13_000_000,
    )
    result = complete_rollback(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
        clock=clock,
    )

    assert clock.read_count == 1
    assert result.organism_id == initial.organism_id
    assert result.transformed_candidate_id == transformed.transformed_candidate_id
    assert result.archive_id == archive.archive_id
    assert result.selected_checkpoint_id == genesis.checkpoint_id
    assert result.abandoned_lineage_generation == 0
    assert result.new_lineage_generation == 1
    assert result.source_lifecycle_number == 0
    assert result.source_event_sequence == genesis.event_sequence
    assert result.restoration_event_sequence == genesis.event_sequence + 1
    assert result.completion_event_sequence == genesis.event_sequence + 2
    assert result.administrative_reason == "protected rollback completion"
    assert result.queued_input_events_preserved == 0
    assert result.transformed_candidate_database_sha256 == transformed.database_sha256
    assert result.transformed_candidate_manifest_sha256 == transformed.manifest_sha256
    assert result.recovered_existing_completion is False
    assert result.status == "sleeping"

    connection = connect_database(paths.database, read_only=True)
    try:
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        assert organism["lineage_generation"] == 1
        assert organism["lifecycle_number"] == 0
        assert organism["status"] == "sleeping"
        assert organism["checkpoint_pending"] == 0
        assert organism["consecutive_failures"] == 0
        assert organism["maintenance_reason"] is None
        assert organism["last_sleep_wall_time_utc_us"] == 1_730_000_000_000_000
        assert organism["latest_stable_checkpoint_id"] == genesis.checkpoint_id
        assert organism["latest_stable_event_sequence"] == genesis.event_sequence

        tip = connection.execute(
            "SELECT * FROM event ORDER BY event_sequence DESC LIMIT 1"
        ).fetchone()
        assert tip["event_sequence"] == genesis.event_sequence + 2
        assert tip["event_type"] == "rollback_completed"
        assert tip["source"] == "administration:rollback"
        assert tip["lineage_generation"] == 1
        assert tip["lifecycle_number"] == 0
        assert tip["wall_time_utc_us"] == 1_730_000_000_000_000
        assert json.loads(tip["payload_json"]) == {
            "administrative_reason": "protected rollback completion",
            "archive_database_sha256": archive.database_sha256,
            "archive_id": archive.archive_id,
            "archive_manifest_sha256": archive.manifest_sha256,
            "abandoned_event_sequence": archive.active_event_sequence,
            "abandoned_lifecycle_number": 0,
            "abandoned_lineage_generation": 0,
            "completion_event_sequence": genesis.event_sequence + 2,
            "consecutive_failures_after": 0,
            "consecutive_failures_before": 0,
            "implementation_version": "0.1.0",
            "maintenance_reason_before": None,
            "new_lineage_generation": 1,
            "queued_input_events_preserved": 0,
            "replacement_validated": True,
            "restoration_event_sequence": genesis.event_sequence + 1,
            "rollback_started_event_sequence": begin.rollback_started_event_sequence,
            "selected_checkpoint_database_sha256": genesis.database_sha256,
            "selected_checkpoint_event_sequence": genesis.event_sequence,
            "selected_checkpoint_id": genesis.checkpoint_id,
            "selected_checkpoint_lineage_generation": 0,
            "selected_checkpoint_manifest_sha256": genesis.manifest_sha256,
            "source_lifecycle_number": 0,
            "source_restore_candidate_database_sha256": source.database_sha256,
            "source_restore_candidate_id": source.candidate_id,
            "source_restore_candidate_manifest_sha256": source.manifest_sha256,
            "status_after": "sleeping",
            "status_before": "rollback_in_progress",
            "transformed_candidate_database_sha256": transformed.database_sha256,
            "transformed_candidate_id": transformed.transformed_candidate_id,
            "transformed_candidate_manifest_sha256": transformed.manifest_sha256,
        }
    finally:
        connection.close()

    assert _active_snapshot(paths) != active_before
    assert _artifacts(paths) == artifacts_before

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "rollback",
            "complete",
            initial.organism_id,
            "--candidate-id",
            transformed.transformed_candidate_id,
            "--json",
        ]
    ) == 0
    repeated_payload = json.loads(capsys.readouterr().out)
    assert repeated_payload["recovered_existing_completion"] is True
    assert repeated_payload["completion_event_sequence"] == result.completion_event_sequence

    enqueue_garden_tick(
        paths,
        "first-post-rollback-tick",
        clock=FakeClock([ClockReading(1_740_000_000_000_000, 14_000_000)]),
    )
    wake_clock = FakeClock(
        [
            ClockReading(1_740_000_000_000_001, 20_000_000),
            ClockReading(1_740_000_000_000_001, 25_000_000),
            ClockReading(1_740_000_000_000_002, 30_000_000),
            ClockReading(1_740_000_000_000_003, 40_000_000),
            ClockReading(1_740_000_000_000_004, 50_000_000),
        ]
    )
    wake = perform_first_water_wake(
        runtime_root,
        initial.organism_id,
        seed=1,
        clock=wake_clock,
    )
    status = read_status(paths)
    assert wake_clock.read_count == 5
    assert wake.decision.as_dict()["parameters"] == {"plot_id": "bed-a"}
    assert wake.checkpoint.lineage_generation == 1
    assert status.lineage_generation == 1
    assert status.lifecycle_number == 1
    assert status.status == "sleeping"
    assert status.latest_stable_checkpoint_id == wake.checkpoint.checkpoint_id
    assert _artifacts(paths)["archives"] == artifacts_before["archives"]
    assert _artifacts(paths)["candidates"] == artifacts_before["candidates"]


def test_rollback_completion_requires_replaced_body(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _active_snapshot(paths)
    clock = FakeClock([])

    with pytest.raises(
        RollbackCompletionRejectedError,
        match="not an exact replaced rollback body awaiting completion",
    ):
        complete_rollback(
            runtime_root,
            initial.organism_id,
            "rtc-g000001-rb-e000000000004-from-e000000000002-deadbeef",
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before


def test_rollback_completion_rejects_transformed_candidate_drift(initialized) -> None:
    runtime_root, initial, _, paths, _, _, _, transformed, _ = _prepare_completion(
        initialized
    )
    (transformed.transformed_candidate_dir / "unexpected.txt").write_text(
        "transformed candidate drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)
    artifacts_before = _artifacts(paths)
    clock = FakeClock([])

    with pytest.raises(RollbackCompletionRejectedError, match="unexpected entries"):
        complete_rollback(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before
    assert _artifacts(paths) == artifacts_before


def test_rollback_completion_rejects_archive_drift(initialized) -> None:
    runtime_root, initial, _, paths, archive, _, _, transformed, _ = (
        _prepare_completion(initialized)
    )
    (archive.archive_dir / "unexpected.txt").write_text(
        "archive drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)
    artifacts_before = _artifacts(paths)
    clock = FakeClock([])

    with pytest.raises(RollbackCompletionRejectedError, match="unexpected entries"):
        complete_rollback(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before
    assert _artifacts(paths) == artifacts_before


def test_rollback_completion_is_fail_fast_busy(initialized) -> None:
    runtime_root, initial, _, paths, _, _, _, transformed, _ = _prepare_completion(
        initialized
    )
    before = _active_snapshot(paths)
    artifacts_before = _artifacts(paths)
    competing = connect_database(paths.database)
    competing.execute("BEGIN IMMEDIATE")
    clock = FakeClock([])
    try:
        with pytest.raises(
            RollbackCompletionBusyError,
            match="busy; this attempt was not queued",
        ):
            complete_rollback(
                runtime_root,
                initial.organism_id,
                transformed.transformed_candidate_id,
                clock=clock,
            )
    finally:
        competing.rollback()
        competing.close()

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before
    assert _artifacts(paths) == artifacts_before


def test_rollback_completion_failure_rolls_back_status_and_event(initialized) -> None:
    runtime_root, initial, _, paths, _, _, _, transformed, _ = _prepare_completion(
        initialized
    )
    before = _active_snapshot(paths)
    artifacts_before = _artifacts(paths)
    clock = FakeClock.fixed(
        wall_time_utc_us=1_730_000_000_000_001,
        monotonic_ns=13_000_001,
    )

    with pytest.raises(
        RollbackCompletionRejectedError,
        match="injected rollback completion failure after event insert",
    ):
        complete_rollback(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
            clock=clock,
            protected_test_fail_after_event_insert=True,
        )

    assert clock.read_count == 1
    assert _active_snapshot(paths) == before
    assert _artifacts(paths) == artifacts_before
    blocked_clock = FakeClock([])
    with pytest.raises(WakeRejectedError, match="status=rollback_in_progress"):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=1,
            clock=blocked_clock,
        )
    assert blocked_clock.read_count == 0


def test_rollback_completion_repeat_is_read_only_and_zero_clock(initialized) -> None:
    runtime_root, initial, _, paths, _, _, _, transformed, _ = _prepare_completion(
        initialized
    )
    first = complete_rollback(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=1_730_000_000_000_002,
            monotonic_ns=13_000_002,
        ),
    )
    active_before = _active_snapshot(paths)
    artifacts_before = _artifacts(paths)
    no_clock = FakeClock([])

    repeated = complete_rollback(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
        clock=no_clock,
    )

    assert repeated.recovered_existing_completion is True
    assert repeated.completion_event_sequence == first.completion_event_sequence
    assert no_clock.read_count == 0
    assert _active_snapshot(paths) == active_before
    assert _artifacts(paths) == artifacts_before


def test_rollback_completion_rejects_incompatible_completed_history(initialized) -> None:
    runtime_root, initial, _, paths, _, _, _, transformed, _ = _prepare_completion(
        initialized
    )
    complete_rollback(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=1_730_000_000_000_003,
            monotonic_ns=13_000_003,
        ),
    )
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               )
               SELECT organism_id, lineage_generation, lifecycle_number,
                      999, 'administrative_drift', 'administration:test', '{}',
                      schema_version, environment_version, budget_config_version
               FROM organism WHERE singleton_id = 1"""
        )
        connection.commit()
    finally:
        connection.close()
    drifted = _active_snapshot(paths)
    artifacts_before = _artifacts(paths)
    clock = FakeClock([])

    with pytest.raises(
        RollbackCompletionRejectedError,
        match="not an exact replaced rollback body awaiting completion",
    ):
        complete_rollback(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == drifted
    assert _artifacts(paths) == artifacts_before
