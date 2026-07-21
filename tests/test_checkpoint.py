from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.errors import CheckpointError
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database


def test_genesis_checkpoint_manifest_and_database_validate(initialized) -> None:
    _, status, checkpoint = initialized
    manifest = validate_checkpoint_directory(checkpoint.checkpoint_dir)

    assert manifest["checkpoint_id"] == checkpoint.checkpoint_id
    assert manifest["organism_id"] == status.organism_id
    assert manifest["lineage_generation"] == 0
    assert manifest["event_sequence"] == 2
    assert manifest["provenance"] == "genesis"
    assert manifest["database_sha256"] == checkpoint.database_sha256


def test_checkpoint_snapshot_is_pending_boundary_not_second_live_authority(initialized) -> None:
    _, _, checkpoint = initialized
    snapshot = connect_database(
        checkpoint.checkpoint_dir / "organism.sqlite3",
        read_only=True,
    )
    try:
        row = snapshot.execute(
            "SELECT status, checkpoint_pending, latest_stable_checkpoint_id FROM organism"
        ).fetchone()
        assert row["status"] == "checkpoint_pending"
        assert row["checkpoint_pending"] == 1
        assert row["latest_stable_checkpoint_id"] is None
        assert snapshot.execute("SELECT MAX(event_sequence) FROM event").fetchone()[0] == 2
    finally:
        snapshot.close()


def test_active_database_registers_checkpoint_without_mutating_snapshot(initialized) -> None:
    runtime_root, _, checkpoint = initialized
    paths = OrganismPaths.build(runtime_root, "sudachi-0")
    active = connect_database(paths.database, read_only=True)
    try:
        row = active.execute("SELECT * FROM checkpoint_registry").fetchone()
        assert row["checkpoint_id"] == checkpoint.checkpoint_id
        assert row["event_sequence"] == 2
        assert row["protected"] == 1
        assert active.execute("SELECT MAX(event_sequence) FROM event").fetchone()[0] == 3
    finally:
        active.close()


def test_checkpoint_digest_mismatch_is_rejected(initialized, tmp_path: Path) -> None:
    _, _, checkpoint = initialized
    copied = tmp_path / "bad-checkpoint"
    import shutil

    shutil.copytree(checkpoint.checkpoint_dir, copied)
    with (copied / "organism.sqlite3").open("ab") as handle:
        handle.write(b"tamper")

    with pytest.raises(CheckpointError, match="size mismatch|digest mismatch"):
        validate_checkpoint_directory(copied)


def test_checkpoint_directory_name_must_match_manifest(initialized, tmp_path: Path) -> None:
    _, _, checkpoint = initialized
    copied = tmp_path / "renamed-checkpoint"
    import shutil

    shutil.copytree(checkpoint.checkpoint_dir, copied)
    with pytest.raises(CheckpointError, match="directory name"):
        validate_checkpoint_directory(copied)
