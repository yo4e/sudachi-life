from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

import sudachi_life.rollback_transform as transform_module
from sudachi_life.cli import main
from sudachi_life.clock import FakeClock
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_transform import (
    CandidateTransformBusyError,
    CandidateTransformError,
    CandidateTransformRejectedError,
    transform_restore_candidate,
)
from sudachi_life.storage import connect_database, read_status, validate_canonical_state


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
            "status": read_status(paths),
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
            "checkpoints": _tree_snapshot(paths.checkpoints),
            "archives": _tree_snapshot(paths.rollback_archives),
        }
    finally:
        connection.close()


def _start_transform(initialized):
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
    return runtime_root, initial, genesis, paths, archive, begin, source


def test_transform_restore_candidate_prepares_new_lineage_without_active_mutation(
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
    ) = _start_transform(initialized)
    active_before = _active_snapshot(paths)
    source_before = _tree_snapshot(source.candidate_dir)
    clock = FakeClock.fixed(
        wall_time_utc_us=1_720_000_000_000_000,
        monotonic_ns=12_000_000,
    )

    result = transform_restore_candidate(
        runtime_root,
        initial.organism_id,
        source.candidate_id,
        "explicit protected rollback",
        clock=clock,
    )

    assert clock.read_count == 1
    assert result.organism_id == initial.organism_id
    assert result.source_candidate_id == source.candidate_id
    assert result.archive_id == archive.archive_id
    assert result.selected_checkpoint_id == genesis.checkpoint_id
    assert result.abandoned_lineage_generation == 0
    assert result.new_lineage_generation == 1
    assert result.source_lifecycle_number == 0
    assert result.source_event_sequence == genesis.event_sequence
    assert result.restoration_event_sequence == genesis.event_sequence + 1
    assert result.administrative_reason == "explicit protected rollback"
    assert result.transformed_candidate_dir.parent == paths.restore_candidates
    assert result.transformed_candidate_id.startswith("rtc-g000001-")
    assert result.database_sha256 == _digest(
        result.transformed_candidate_dir / "organism.sqlite3"
    )
    assert result.manifest_sha256 == _digest(
        result.transformed_candidate_dir / "manifest.json"
    )

    manifest = json.loads(
        (result.transformed_candidate_dir / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["candidate_state"] == "lineage_transformed_replacement_ready"
    assert manifest["new_lineage_generation"] == 1
    assert manifest["abandoned_lineage_generation"] == 0
    assert manifest["abandoned_event_sequence"] == archive.active_event_sequence
    assert manifest["rollback_started_event_sequence"] == (
        begin.rollback_started_event_sequence
    )
    assert manifest["source_restore_candidate_id"] == source.candidate_id
    assert manifest["source_restore_candidate_manifest_sha256"] == (
        source.manifest_sha256
    )
    assert manifest["source_restore_candidate_database_sha256"] == (
        source.database_sha256
    )
    assert manifest["selected_checkpoint_id"] == genesis.checkpoint_id
    assert manifest["selected_checkpoint_event_sequence"] == genesis.event_sequence
    assert manifest["restoration_event_sequence"] == genesis.event_sequence + 1
    assert manifest["restoration_wall_time_utc_us"] == 1_720_000_000_000_000
    assert manifest["administrative_reason"] == "explicit protected rollback"
    assert manifest["status"] == "published"
    assert manifest["provenance"] == "rollback_transformed_candidate"

    transformed = connect_database(
        result.transformed_candidate_dir / "organism.sqlite3",
        read_only=True,
    )
    source_database = connect_database(
        source.candidate_dir / "organism.sqlite3",
        read_only=True,
    )
    active = connect_database(paths.database, read_only=True)
    try:
        validate_canonical_state(transformed, expect_checkpoint_pending=False)
        organism = transformed.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        assert organism["organism_id"] == initial.organism_id
        assert organism["lineage_generation"] == 1
        assert organism["lifecycle_number"] == 0
        assert organism["status"] == "rollback_in_progress"
        assert organism["checkpoint_pending"] == 0
        assert organism["pending_checkpoint_generation"] is None
        assert organism["pending_checkpoint_event_sequence"] is None
        assert organism["latest_stable_checkpoint_id"] == genesis.checkpoint_id
        assert organism["latest_stable_event_sequence"] == genesis.event_sequence

        source_events = source_database.execute(
            "SELECT * FROM event ORDER BY event_sequence"
        ).fetchall()
        transformed_events = transformed.execute(
            "SELECT * FROM event ORDER BY event_sequence"
        ).fetchall()
        assert [tuple(row) for row in transformed_events[:-1]] == [
            tuple(row) for row in source_events
        ]
        restoration = transformed_events[-1]
        assert restoration["event_sequence"] == genesis.event_sequence + 1
        assert restoration["lineage_generation"] == 1
        assert restoration["lifecycle_number"] == 0
        assert restoration["event_type"] == "rollback_lineage_prepared"
        assert restoration["source"] == "administration:rollback-candidate"
        assert restoration["wall_time_utc_us"] == 1_720_000_000_000_000
        assert json.loads(restoration["payload_json"]) == {
            "administrative_reason": "explicit protected rollback",
            "archive_database_sha256": archive.database_sha256,
            "archive_id": archive.archive_id,
            "archive_manifest_sha256": archive.manifest_sha256,
            "abandoned_event_sequence": archive.active_event_sequence,
            "abandoned_lifecycle_number": 0,
            "abandoned_lineage_generation": 0,
            "new_lineage_generation": 1,
            "rollback_started_event_sequence": begin.rollback_started_event_sequence,
            "selected_checkpoint_database_sha256": genesis.database_sha256,
            "selected_checkpoint_event_sequence": genesis.event_sequence,
            "selected_checkpoint_id": genesis.checkpoint_id,
            "selected_checkpoint_lineage_generation": 0,
            "selected_checkpoint_manifest_sha256": genesis.manifest_sha256,
            "source_restore_candidate_database_sha256": source.database_sha256,
            "source_restore_candidate_id": source.candidate_id,
            "source_restore_candidate_manifest_sha256": source.manifest_sha256,
            "status_after": "rollback_in_progress",
        }

        selected_active = active.execute(
            "SELECT * FROM checkpoint_registry WHERE checkpoint_id = ?",
            (genesis.checkpoint_id,),
        ).fetchone()
        selected_transformed = transformed.execute(
            "SELECT * FROM checkpoint_registry WHERE checkpoint_id = ?",
            (genesis.checkpoint_id,),
        ).fetchone()
        assert tuple(selected_transformed) == tuple(selected_active)
    finally:
        active.close()
        source_database.close()
        transformed.close()

    assert _active_snapshot(paths) == active_before
    assert _tree_snapshot(source.candidate_dir) == source_before

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "rollback",
            "transform-candidate",
            initial.organism_id,
            "--candidate-id",
            source.candidate_id,
            "--reason",
            "explicit protected rollback",
            "--json",
        ]
    ) == 0
    assert json.loads(capsys.readouterr().out) == result.as_dict()
    assert _active_snapshot(paths) == active_before
    assert _tree_snapshot(source.candidate_dir) == source_before


def test_candidate_transform_requires_durable_intent(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _active_snapshot(paths)
    clock = FakeClock([])

    with pytest.raises(
        CandidateTransformRejectedError,
        match="requires rollback_in_progress",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            "rc-g000000-rb-e000000000004-from-e000000000002-deadbeef",
            "test rollback",
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before


def test_candidate_transform_rejects_missing_source_before_clock_use(initialized) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    shutil.rmtree(source.candidate_dir)
    before = _active_snapshot(paths)
    clock = FakeClock([])

    with pytest.raises(
        CandidateTransformRejectedError,
        match="restore candidate directory is missing or unsafe",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "test rollback",
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before


def test_candidate_transform_rejects_source_candidate_drift(initialized) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    (source.candidate_dir / "unexpected.txt").write_text(
        "source candidate drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)
    clock = FakeClock([])

    with pytest.raises(
        CandidateTransformRejectedError,
        match="unexpected entries",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "test rollback",
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before


def test_candidate_transform_rejects_selected_checkpoint_drift(initialized) -> None:
    (
        runtime_root,
        initial,
        genesis,
        paths,
        _,
        _,
        source,
    ) = _start_transform(initialized)
    (genesis.checkpoint_dir / "unexpected.txt").write_text(
        "selected checkpoint drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)
    source_before = _tree_snapshot(source.candidate_dir)
    clock = FakeClock([])

    with pytest.raises(
        CandidateTransformRejectedError,
        match="unexpected entries",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "test rollback",
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before
    assert _tree_snapshot(source.candidate_dir) == source_before


def test_candidate_transform_is_fail_fast_busy(initialized) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    before = _active_snapshot(paths)
    source_before = _tree_snapshot(source.candidate_dir)
    competing = connect_database(paths.database)
    competing.execute("BEGIN IMMEDIATE")
    clock = FakeClock([])
    try:
        with pytest.raises(
            CandidateTransformBusyError,
            match="busy; this attempt was not queued",
        ):
            transform_restore_candidate(
                runtime_root,
                initial.organism_id,
                source.candidate_id,
                "test rollback",
                clock=clock,
            )
    finally:
        competing.rollback()
        competing.close()

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before
    assert _tree_snapshot(source.candidate_dir) == source_before


def test_candidate_transform_transaction_failure_leaves_no_candidate(initialized) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    before = _active_snapshot(paths)
    source_before = _tree_snapshot(source.candidate_dir)
    clock = FakeClock.fixed(
        wall_time_utc_us=1_720_000_000_000_001,
        monotonic_ns=12_000_001,
    )

    with pytest.raises(
        CandidateTransformError,
        match="injected candidate transformation failure after event insert",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "test rollback",
            clock=clock,
            protected_test_fail_after_event_insert=True,
        )

    assert clock.read_count == 1
    assert {entry.name for entry in paths.restore_candidates.iterdir()} == {
        source.candidate_id
    }
    assert _active_snapshot(paths) == before
    assert _tree_snapshot(source.candidate_dir) == source_before


def test_candidate_transform_prepublication_failure_leaves_no_candidate(initialized) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    before = _active_snapshot(paths)
    source_before = _tree_snapshot(source.candidate_dir)

    with pytest.raises(
        CandidateTransformError,
        match="injected candidate transformation failure before publication",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "test rollback",
            clock=FakeClock.fixed(
                wall_time_utc_us=1_720_000_000_000_002,
                monotonic_ns=12_000_002,
            ),
            protected_test_fail_before_publish=True,
        )

    assert {entry.name for entry in paths.restore_candidates.iterdir()} == {
        source.candidate_id
    }
    assert _active_snapshot(paths) == before
    assert _tree_snapshot(source.candidate_dir) == source_before


def test_candidate_transform_publication_failure_cleans_temporary_candidate(
    initialized,
    monkeypatch,
) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    before = _active_snapshot(paths)
    source_before = _tree_snapshot(source.candidate_dir)

    def fail_replace(source_path: Path, destination_path: Path) -> None:
        raise OSError("injected transformed candidate publication failure")

    monkeypatch.setattr(transform_module.os, "replace", fail_replace)
    with pytest.raises(
        CandidateTransformError,
        match="injected transformed candidate publication failure",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "test rollback",
            clock=FakeClock.fixed(
                wall_time_utc_us=1_720_000_000_000_003,
                monotonic_ns=12_000_003,
            ),
        )

    assert {entry.name for entry in paths.restore_candidates.iterdir()} == {
        source.candidate_id
    }
    assert _active_snapshot(paths) == before
    assert _tree_snapshot(source.candidate_dir) == source_before


def test_candidate_transform_repeated_request_is_idempotent_and_reason_is_bound(
    initialized,
) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    first = transform_restore_candidate(
        runtime_root,
        initial.organism_id,
        source.candidate_id,
        "first reason",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_720_000_000_000_004,
            monotonic_ns=12_000_004,
        ),
    )
    before = _active_snapshot(paths)
    transformed_before = _tree_snapshot(first.transformed_candidate_dir)
    source_before = _tree_snapshot(source.candidate_dir)
    no_clock = FakeClock([])

    repeated = transform_restore_candidate(
        runtime_root,
        initial.organism_id,
        source.candidate_id,
        "first reason",
        clock=no_clock,
    )
    assert repeated.as_dict() == first.as_dict()
    assert no_clock.read_count == 0

    with pytest.raises(
        CandidateTransformError,
        match="administrative_reason",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "different reason",
            clock=no_clock,
        )

    assert no_clock.read_count == 0
    assert _active_snapshot(paths) == before
    assert _tree_snapshot(first.transformed_candidate_dir) == transformed_before
    assert _tree_snapshot(source.candidate_dir) == source_before


def test_candidate_transform_rejects_corrupted_existing_candidate(initialized) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    result = transform_restore_candidate(
        runtime_root,
        initial.organism_id,
        source.candidate_id,
        "test rollback",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_720_000_000_000_005,
            monotonic_ns=12_000_005,
        ),
    )
    (result.transformed_candidate_dir / "unexpected.txt").write_text(
        "transformed candidate drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)
    source_before = _tree_snapshot(source.candidate_dir)
    clock = FakeClock([])

    with pytest.raises(
        CandidateTransformError,
        match="unexpected entries",
    ):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "test rollback",
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before
    assert _tree_snapshot(source.candidate_dir) == source_before


@pytest.mark.parametrize(
    "reason, message",
    [
        ("", "non-empty"),
        (" surrounding ", "surrounding whitespace"),
        ("line\nbreak", "control characters"),
        ("x" * 257, "256-character"),
    ],
)
def test_candidate_transform_rejects_invalid_reason_without_mutation(
    initialized,
    reason: str,
    message: str,
) -> None:
    runtime_root, initial, _, paths, _, _, source = _start_transform(initialized)
    before = _active_snapshot(paths)
    root_before = _tree_snapshot(paths.restore_candidates)
    clock = FakeClock([])

    with pytest.raises(CandidateTransformRejectedError, match=message):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            reason,
            clock=clock,
        )

    assert clock.read_count == 0
    assert _active_snapshot(paths) == before
    assert _tree_snapshot(paths.restore_candidates) == root_before
