from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

import sudachi_life.rollback_replace as replace_module
from sudachi_life.cli import main
from sudachi_life.clock import FakeClock
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_intent import _canonical_sqlite_snapshot, begin_rollback
from sudachi_life.rollback_replace import (
    ActiveReplacementBusyError,
    ActiveReplacementError,
    ActiveReplacementIncompleteError,
    ActiveReplacementRejectedError,
    replace_active_with_candidate,
)
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
        }
    finally:
        connection.close()


def _prepare_replacement(initialized):
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
        "protected active replacement",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_720_000_000_000_000,
            monotonic_ns=12_000_000,
        ),
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
    )


def _artifact_snapshot(paths: OrganismPaths) -> dict[str, object]:
    return {
        "checkpoints": _tree_snapshot(paths.checkpoints),
        "archives": _tree_snapshot(paths.rollback_archives),
        "candidates": _tree_snapshot(paths.restore_candidates),
    }


def _assert_no_replacement_temp(paths: OrganismPaths) -> None:
    assert not any(
        entry.name.startswith(".tmp-active-replacement-")
        for entry in paths.organism_dir.iterdir()
    )


def test_replace_active_publishes_exact_transformed_body_and_blocks_wake(
    initialized,
    capsys,
) -> None:
    (
        runtime_root,
        initial,
        genesis,
        paths,
        archive,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    active_before = _active_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)

    result = replace_active_with_candidate(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
    )

    assert result.organism_id == initial.organism_id
    assert result.transformed_candidate_id == transformed.transformed_candidate_id
    assert result.archive_id == archive.archive_id
    assert result.selected_checkpoint_id == genesis.checkpoint_id
    assert result.abandoned_lineage_generation == 0
    assert result.new_lineage_generation == 1
    assert result.source_lifecycle_number == 0
    assert result.source_event_sequence == genesis.event_sequence
    assert result.restoration_event_sequence == genesis.event_sequence + 1
    assert result.recovered_existing_replacement is False
    assert result.status == "rollback_in_progress"
    assert result.active_database == paths.database
    assert result.active_database_sha256 == _digest(paths.database)
    assert result.transformed_candidate_database_sha256 == transformed.database_sha256
    assert result.transformed_candidate_manifest_sha256 == transformed.manifest_sha256

    active = connect_database(paths.database, read_only=True)
    candidate = connect_database(
        transformed.transformed_candidate_dir / "organism.sqlite3",
        read_only=True,
    )
    try:
        validate_canonical_state(active, expect_checkpoint_pending=False)
        assert _canonical_sqlite_snapshot(active) == _canonical_sqlite_snapshot(candidate)
        organism = active.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        assert organism["lineage_generation"] == 1
        assert organism["status"] == "rollback_in_progress"
        assert organism["latest_stable_checkpoint_id"] == genesis.checkpoint_id
        assert organism["latest_stable_event_sequence"] == genesis.event_sequence
        tip = active.execute(
            "SELECT * FROM event ORDER BY event_sequence DESC LIMIT 1"
        ).fetchone()
        assert tip["event_type"] == "rollback_lineage_prepared"
        assert tip["lineage_generation"] == 1
        assert tip["event_sequence"] == genesis.event_sequence + 1
    finally:
        candidate.close()
        active.close()

    assert _active_snapshot(paths) != active_before
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)

    rejected_clock = FakeClock([])
    with pytest.raises(
        WakeRejectedError,
        match="organism is not wakeable: status=rollback_in_progress",
    ):
        perform_garden_wake(
            runtime_root,
            initial.organism_id,
            seed=1,
            clock=rejected_clock,
        )
    assert rejected_clock.read_count == 0

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "rollback",
            "replace-active",
            initial.organism_id,
            "--candidate-id",
            transformed.transformed_candidate_id,
            "--json",
        ]
    ) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload["transformed_candidate_id"] == transformed.transformed_candidate_id
    assert cli_payload["recovered_existing_replacement"] is True
    assert cli_payload["active_database_sha256"] == _digest(paths.database)
    assert _artifact_snapshot(paths) == artifacts_before


def test_active_replacement_requires_prepared_rollback_or_exact_recovery(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _active_snapshot(paths)

    with pytest.raises(
        ActiveReplacementRejectedError,
        match="neither the protected pre-replacement intent nor the exact replaced candidate",
    ):
        replace_active_with_candidate(
            runtime_root,
            initial.organism_id,
            "rtc-g000001-rb-e000000000004-from-e000000000002-deadbeef",
        )

    assert _active_snapshot(paths) == before
    _assert_no_replacement_temp(paths)


def test_active_replacement_rejects_missing_transformed_candidate(initialized) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    shutil.rmtree(transformed.transformed_candidate_dir)
    before = _active_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)

    with pytest.raises(
        ActiveReplacementRejectedError,
        match="transformed candidate directory is missing or unsafe",
    ):
        replace_active_with_candidate(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
        )

    assert _active_snapshot(paths) == before
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)


def test_active_replacement_rejects_transformed_candidate_drift(initialized) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    (transformed.transformed_candidate_dir / "unexpected.txt").write_text(
        "transformed candidate drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)

    with pytest.raises(
        ActiveReplacementRejectedError,
        match="unexpected entries",
    ):
        replace_active_with_candidate(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
        )

    assert _active_snapshot(paths) == before
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)


def test_active_replacement_rejects_source_candidate_drift(initialized) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        source,
        transformed,
    ) = _prepare_replacement(initialized)
    (source.candidate_dir / "unexpected.txt").write_text(
        "source candidate drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)

    with pytest.raises(
        ActiveReplacementRejectedError,
        match="unexpected entries",
    ):
        replace_active_with_candidate(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
        )

    assert _active_snapshot(paths) == before
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)


def test_active_replacement_is_fail_fast_busy(initialized) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    before = _active_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)
    competing = connect_database(paths.database)
    competing.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(
            ActiveReplacementBusyError,
            match="busy; this attempt was not queued",
        ):
            replace_active_with_candidate(
                runtime_root,
                initial.organism_id,
                transformed.transformed_candidate_id,
            )
    finally:
        competing.rollback()
        competing.close()

    assert _active_snapshot(paths) == before
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)


def test_active_replacement_injected_pretransfer_failure_preserves_old_active(
    initialized,
) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    before = _active_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)

    with pytest.raises(
        ActiveReplacementError,
        match="injected active replacement failure before authority transfer",
    ):
        replace_active_with_candidate(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
            protected_test_fail_before_replace=True,
        )

    assert _active_snapshot(paths) == before
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)


def test_active_replacement_atomic_replace_failure_preserves_old_active(
    initialized,
    monkeypatch,
) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    before = _active_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("injected active database atomic replacement failure")

    monkeypatch.setattr(replace_module.os, "replace", fail_replace)
    with pytest.raises(
        ActiveReplacementError,
        match="injected active database atomic replacement failure",
    ):
        replace_active_with_candidate(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
        )

    assert _active_snapshot(paths) == before
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)


def test_active_replacement_posttransfer_interruption_is_recoverable(
    initialized,
) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    artifacts_before = _artifact_snapshot(paths)

    with pytest.raises(
        ActiveReplacementIncompleteError,
        match="post-replacement validation was interrupted",
    ):
        replace_active_with_candidate(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
            protected_test_fail_after_replace=True,
        )

    active_after_interruption = _active_snapshot(paths)
    assert active_after_interruption["status"].lineage_generation == 1
    assert active_after_interruption["status"].status == "rollback_in_progress"
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)

    recovered = replace_active_with_candidate(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
    )
    assert recovered.recovered_existing_replacement is True
    assert _active_snapshot(paths) == active_after_interruption
    assert _artifact_snapshot(paths) == artifacts_before


def test_active_replacement_exact_repeat_is_read_only_recovery(initialized) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    first = replace_active_with_candidate(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
    )
    active_before = _active_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)

    second = replace_active_with_candidate(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
    )

    assert first.recovered_existing_replacement is False
    assert second.recovered_existing_replacement is True
    assert second.active_database_sha256 == first.active_database_sha256
    assert _active_snapshot(paths) == active_before
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)


def test_active_replacement_rejects_drifted_postreplacement_active(initialized) -> None:
    (
        runtime_root,
        initial,
        _,
        paths,
        _,
        _,
        _,
        transformed,
    ) = _prepare_replacement(initialized)
    replace_active_with_candidate(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
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
    artifacts_before = _artifact_snapshot(paths)

    with pytest.raises(
        ActiveReplacementRejectedError,
        match="neither the protected pre-replacement intent nor the exact replaced candidate",
    ):
        replace_active_with_candidate(
            runtime_root,
            initial.organism_id,
            transformed.transformed_candidate_id,
        )

    assert _active_snapshot(paths) == drifted
    assert _artifact_snapshot(paths) == artifacts_before
    _assert_no_replacement_temp(paths)
