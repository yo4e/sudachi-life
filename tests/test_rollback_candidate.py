from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

import sudachi_life.rollback_candidate as candidate_module
from sudachi_life.cli import main
from sudachi_life.clock import FakeClock
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import (
    RestoreCandidateBusyError,
    RestoreCandidateError,
    RestoreCandidateRejectedError,
    build_restore_candidate,
)
from sudachi_life.rollback_intent import _canonical_sqlite_snapshot, begin_rollback
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


def _start_rollback(initialized):
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
    return runtime_root, initial, genesis, paths, archive, begin


def test_build_restore_candidate_publishes_exact_source_without_active_mutation(
    initialized,
    capsys,
) -> None:
    runtime_root, initial, genesis, paths, archive, begin = _start_rollback(initialized)
    before = _active_snapshot(paths)

    result = build_restore_candidate(runtime_root, initial.organism_id)

    assert result.organism_id == initial.organism_id
    assert result.rollback_started_event_sequence == begin.rollback_started_event_sequence
    assert result.archive_id == archive.archive_id
    assert result.selected_checkpoint_id == genesis.checkpoint_id
    assert result.source_lineage_generation == 0
    assert result.source_lifecycle_number == 0
    assert result.source_event_sequence == genesis.event_sequence
    assert result.candidate_dir.parent == paths.restore_candidates
    assert {entry.name for entry in result.candidate_dir.iterdir()} == {
        "organism.sqlite3",
        "manifest.json",
    }
    assert result.database_sha256 == _digest(result.candidate_dir / "organism.sqlite3")
    assert result.manifest_sha256 == _digest(result.candidate_dir / "manifest.json")

    manifest = json.loads(
        (result.candidate_dir / "manifest.json").read_text(encoding="utf-8")
    )
    assert manifest == {
        "active_lineage_generation": 0,
        "archive_database_sha256": archive.database_sha256,
        "archive_id": archive.archive_id,
        "archive_manifest_sha256": archive.manifest_sha256,
        "budget_config_version": "phase1-v1",
        "candidate_id": result.candidate_id,
        "candidate_state": "source_restored_untransformed",
        "contract_version": "0.2",
        "database_filename": "organism.sqlite3",
        "database_sha256": result.database_sha256,
        "database_size_bytes": result.database_size_bytes,
        "environment_version": "seed-garden-v1",
        "implementation_version": "0.1.0",
        "organism_id": initial.organism_id,
        "provenance": "restore_candidate",
        "restore_candidate_format_version": 1,
        "rollback_started_event_sequence": begin.rollback_started_event_sequence,
        "schema_version": 1,
        "selected_checkpoint_id": genesis.checkpoint_id,
        "snapshot_method": "python-sqlite3-connection-backup",
        "source_checkpoint_database_sha256": genesis.database_sha256,
        "source_checkpoint_database_size_bytes": genesis.database_size_bytes,
        "source_checkpoint_manifest_sha256": genesis.manifest_sha256,
        "source_checkpoint_provenance": "genesis",
        "source_event_sequence": genesis.event_sequence,
        "source_lifecycle_number": 0,
        "source_lineage_generation": 0,
        "status": "published",
    }

    candidate = connect_database(result.candidate_dir / "organism.sqlite3", read_only=True)
    source = connect_database(genesis.checkpoint_dir / "organism.sqlite3", read_only=True)
    try:
        validate_canonical_state(candidate, expect_checkpoint_pending=True)
        assert _canonical_sqlite_snapshot(candidate) == _canonical_sqlite_snapshot(source)
    finally:
        source.close()
        candidate.close()

    assert _active_snapshot(paths) == before
    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "rollback",
            "build-candidate",
            initial.organism_id,
            "--json",
        ]
    ) == 0
    assert json.loads(capsys.readouterr().out) == {
        "authority_category": "administration",
        "authority_source": "administration:rollback-candidate",
        **result.as_dict(),
    }
    assert _active_snapshot(paths) == before


def test_restore_candidate_requires_durable_rollback_intent(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _active_snapshot(paths)

    with pytest.raises(
        RestoreCandidateRejectedError,
        match="requires rollback_in_progress",
    ):
        build_restore_candidate(runtime_root, initial.organism_id)

    assert not paths.restore_candidates.exists()
    assert _active_snapshot(paths) == before


def test_restore_candidate_rejects_missing_archive_without_mutation(initialized) -> None:
    runtime_root, initial, _, paths, archive, _ = _start_rollback(initialized)
    shutil.rmtree(archive.archive_dir)
    before = _active_snapshot(paths)

    with pytest.raises(
        RestoreCandidateRejectedError,
        match="rollback archive directory is missing or unsafe",
    ):
        build_restore_candidate(runtime_root, initial.organism_id)

    assert not paths.restore_candidates.exists()
    assert _active_snapshot(paths) == before


def test_restore_candidate_rejects_non_intent_event_tip(initialized) -> None:
    runtime_root, initial, _, paths, _, _ = _start_rollback(initialized)
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
    before = _active_snapshot(paths)

    with pytest.raises(
        RestoreCandidateRejectedError,
        match="active event tip is not the protected rollback_started intent",
    ):
        build_restore_candidate(runtime_root, initial.organism_id)

    assert not paths.restore_candidates.exists()
    assert _active_snapshot(paths) == before


def test_restore_candidate_rejects_selected_checkpoint_drift(initialized) -> None:
    runtime_root, initial, genesis, paths, _, _ = _start_rollback(initialized)
    (genesis.checkpoint_dir / "unexpected.txt").write_text(
        "selected source drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)

    with pytest.raises(
        RestoreCandidateRejectedError,
        match="unexpected entries",
    ):
        build_restore_candidate(runtime_root, initial.organism_id)

    assert not paths.restore_candidates.exists()
    assert _active_snapshot(paths) == before


def test_restore_candidate_is_fail_fast_busy(initialized) -> None:
    runtime_root, initial, _, paths, _, _ = _start_rollback(initialized)
    before = _active_snapshot(paths)
    competing = connect_database(paths.database)
    competing.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(
            RestoreCandidateBusyError,
            match="busy; this attempt was not queued",
        ):
            build_restore_candidate(runtime_root, initial.organism_id)
    finally:
        competing.rollback()
        competing.close()

    assert not paths.restore_candidates.exists()
    assert _active_snapshot(paths) == before


def test_restore_candidate_injected_failure_cleans_temporary_artifact(initialized) -> None:
    runtime_root, initial, _, paths, _, _ = _start_rollback(initialized)
    before = _active_snapshot(paths)

    with pytest.raises(
        RestoreCandidateError,
        match="injected restore candidate failure before publication",
    ):
        build_restore_candidate(
            runtime_root,
            initial.organism_id,
            protected_test_fail_before_publish=True,
        )

    assert paths.restore_candidates.is_dir()
    assert list(paths.restore_candidates.iterdir()) == []
    assert _active_snapshot(paths) == before


def test_restore_candidate_publication_failure_cleans_temporary_artifact(
    initialized,
    monkeypatch,
) -> None:
    runtime_root, initial, _, paths, _, _ = _start_rollback(initialized)
    before = _active_snapshot(paths)

    def fail_replace(source: Path, destination: Path) -> None:
        raise OSError("injected restore candidate publication failure")

    monkeypatch.setattr(candidate_module.os, "replace", fail_replace)
    with pytest.raises(
        RestoreCandidateError,
        match="injected restore candidate publication failure",
    ):
        build_restore_candidate(runtime_root, initial.organism_id)

    assert paths.restore_candidates.is_dir()
    assert list(paths.restore_candidates.iterdir()) == []
    assert _active_snapshot(paths) == before


def test_restore_candidate_rejects_corrupted_existing_candidate(initialized) -> None:
    runtime_root, initial, _, paths, _, _ = _start_rollback(initialized)
    result = build_restore_candidate(runtime_root, initial.organism_id)
    (result.candidate_dir / "unexpected.txt").write_text(
        "candidate drift",
        encoding="utf-8",
    )
    before = _active_snapshot(paths)

    with pytest.raises(
        RestoreCandidateError,
        match="unexpected entries",
    ):
        build_restore_candidate(runtime_root, initial.organism_id)

    assert _active_snapshot(paths) == before
