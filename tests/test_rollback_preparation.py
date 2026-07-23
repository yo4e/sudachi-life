from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sudachi_life.cli import main
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import (
    RollbackArchiveError,
    RollbackPreparationBusyError,
    RollbackPreparationRejectedError,
    prepare_rollback_archive,
)
from sudachi_life.storage import connect_database, read_status, validate_canonical_state
from sudachi_life.wake import WakeTransaction


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _checkpoint_files(paths: OrganismPaths) -> dict[str, tuple[int, str]]:
    return {
        str(path.relative_to(paths.checkpoints)): (path.stat().st_size, _file_digest(path))
        for path in sorted(paths.checkpoints.rglob("*"))
        if path.is_file()
    }


def _canonical_snapshot(paths: OrganismPaths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "database_size": paths.database.stat().st_size,
            "database_sha256": _file_digest(paths.database),
            "status": read_status(paths),
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
            "checkpoint_files": _checkpoint_files(paths),
        }
    finally:
        connection.close()


def test_prepare_rollback_archive_validates_source_and_preserves_active_state(
    initialized,
    capsys,
) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _canonical_snapshot(paths)

    result = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )

    assert result.organism_id == initial.organism_id
    assert result.active_lineage_generation == 0
    assert result.active_lifecycle_number == 0
    assert result.active_status == "sleeping"
    assert result.active_event_sequence == 3
    assert result.latest_stable_checkpoint_id == genesis.checkpoint_id
    assert result.latest_stable_event_sequence == 2
    assert result.selected_checkpoint_id == genesis.checkpoint_id
    assert result.selected_checkpoint_event_sequence == 2
    assert result.archive_dir.parent == paths.rollback_archives
    assert {path.name for path in result.archive_dir.iterdir()} == {
        "organism.sqlite3",
        "manifest.json",
    }
    assert result.database_sha256 == _file_digest(result.archive_dir / "organism.sqlite3")
    assert result.manifest_sha256 == _file_digest(result.archive_dir / "manifest.json")

    manifest = json.loads((result.archive_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest == {
        "active_event_sequence": 3,
        "active_lifecycle_number": 0,
        "active_lineage_generation": 0,
        "active_status": "sleeping",
        "archive_id": result.archive_id,
        "budget_config_version": "phase1-v1",
        "contract_version": "0.2",
        "database_filename": "organism.sqlite3",
        "database_sha256": result.database_sha256,
        "database_size_bytes": result.database_size_bytes,
        "environment_version": "seed-garden-v1",
        "implementation_version": "0.1.0",
        "latest_stable_checkpoint_id": genesis.checkpoint_id,
        "latest_stable_event_sequence": 2,
        "organism_id": initial.organism_id,
        "provenance": "pre_rollback",
        "rollback_archive_format_version": 1,
        "schema_version": 1,
        "selected_checkpoint_database_sha256": genesis.database_sha256,
        "selected_checkpoint_database_size_bytes": genesis.database_size_bytes,
        "selected_checkpoint_event_sequence": 2,
        "selected_checkpoint_id": genesis.checkpoint_id,
        "selected_checkpoint_lineage_generation": 0,
        "selected_checkpoint_manifest_sha256": genesis.manifest_sha256,
        "selected_checkpoint_provenance": "genesis",
        "snapshot_method": "python-sqlite3-connection-backup",
        "status": "published",
    }

    archived = connect_database(result.archive_dir / "organism.sqlite3", read_only=True)
    try:
        validate_canonical_state(archived, expect_checkpoint_pending=False)
        assert archived.execute(
            "SELECT COALESCE(MAX(event_sequence), 0) FROM event"
        ).fetchone()[0] == 3
        assert archived.execute(
            "SELECT checkpoint_id FROM checkpoint_registry WHERE event_sequence = 2"
        ).fetchone()[0] == genesis.checkpoint_id
    finally:
        archived.close()

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "rollback",
            "prepare",
            initial.organism_id,
            "--event-sequence",
            "2",
            "--json",
        ]
    ) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    assert cli_payload == {
        "authority_category": "administration",
        "authority_source": "administration:rollback-prepare",
        **result.as_dict(),
    }
    assert _canonical_snapshot(paths) == before

    with WakeTransaction.acquire(paths):
        pass
    assert _canonical_snapshot(paths) == before


def test_rollback_preparation_rejects_missing_or_pruned_boundary(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _canonical_snapshot(paths)

    with pytest.raises(
        RollbackPreparationRejectedError,
        match="exactly one retained stable checkpoint.*found 0",
    ):
        prepare_rollback_archive(runtime_root, initial.organism_id, 1)

    assert not paths.rollback_archives.exists()
    assert _canonical_snapshot(paths) == before


def test_rollback_preparation_rejects_ambiguous_boundary(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT * FROM checkpoint_registry WHERE checkpoint_id = ?",
            (genesis.checkpoint_id,),
        ).fetchone()
        connection.execute(
            """INSERT INTO checkpoint_registry (
                   checkpoint_id, lineage_generation, event_sequence,
                   manifest_sha256, database_sha256, database_size_bytes,
                   created_wall_time_utc_us, registered_wall_time_utc_us, protected
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "cp-g000000-e000000000002-ambiguous",
                row["lineage_generation"],
                row["event_sequence"],
                row["manifest_sha256"],
                row["database_sha256"],
                row["database_size_bytes"],
                row["created_wall_time_utc_us"],
                row["registered_wall_time_utc_us"],
                row["protected"],
            ),
        )
        connection.commit()
    finally:
        connection.close()
    before = _canonical_snapshot(paths)

    with pytest.raises(
        RollbackPreparationRejectedError,
        match="exactly one retained stable checkpoint.*found 2",
    ):
        prepare_rollback_archive(runtime_root, initial.organism_id, 2)

    assert _canonical_snapshot(paths) == before


def test_rollback_preparation_rejects_unsafe_checkpoint_artifact(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    unexpected = genesis.checkpoint_dir / "unexpected.txt"
    unexpected.write_text("not part of a checkpoint", encoding="utf-8")
    before = _canonical_snapshot(paths)

    with pytest.raises(
        RollbackPreparationRejectedError,
        match="unexpected entries",
    ):
        prepare_rollback_archive(runtime_root, initial.organism_id, 2)

    assert _canonical_snapshot(paths) == before


def test_rollback_preparation_is_fail_fast_busy(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _canonical_snapshot(paths)
    competing = connect_database(paths.database)
    competing.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(
            RollbackPreparationBusyError,
            match="busy; this attempt was not queued",
        ):
            prepare_rollback_archive(runtime_root, initial.organism_id, 2)
    finally:
        competing.rollback()
        competing.close()

    assert not paths.rollback_archives.exists()
    assert _canonical_snapshot(paths) == before


def test_archive_failure_leaves_no_partial_artifact_and_preserves_wakeability(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _canonical_snapshot(paths)

    with pytest.raises(
        RollbackArchiveError,
        match="injected pre-rollback archive failure",
    ):
        prepare_rollback_archive(
            runtime_root,
            initial.organism_id,
            2,
            protected_test_fail_after_snapshot=True,
        )

    assert paths.rollback_archives.is_dir()
    assert list(paths.rollback_archives.iterdir()) == []
    assert _canonical_snapshot(paths) == before
    with WakeTransaction.acquire(paths):
        pass
    assert _canonical_snapshot(paths) == before


def test_rollback_preparation_rejects_pending_checkpoint_state(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        boundary = connection.execute(
            "SELECT COALESCE(MAX(event_sequence), 0) FROM event"
        ).fetchone()[0]
        connection.execute(
            """UPDATE organism
               SET status = 'checkpoint_pending', checkpoint_pending = 1,
                   pending_checkpoint_generation = lineage_generation,
                   pending_checkpoint_event_sequence = ?
               WHERE singleton_id = 1""",
            (boundary,),
        )
        validate_canonical_state(connection, expect_checkpoint_pending=True)
        connection.commit()
    finally:
        connection.close()
    before = _canonical_snapshot(paths)

    with pytest.raises(
        RollbackPreparationRejectedError,
        match="checkpoint_pending mismatch",
    ):
        prepare_rollback_archive(runtime_root, initial.organism_id, 2)

    assert _canonical_snapshot(paths) == before
