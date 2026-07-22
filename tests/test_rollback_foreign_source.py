from __future__ import annotations

import hashlib
from pathlib import Path
import shutil

import pytest

from sudachi_life.clock import FakeClock
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import (
    RollbackPreparationRejectedError,
    prepare_rollback_archive,
)
from sudachi_life.storage import connect_database, read_status


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_rollback_preparation_rejects_foreign_checkpoint_artifact(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _, foreign = initialize_organism(
        runtime_root,
        "foreign-organism",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_800_000_000_000_000,
            monotonic_ns=20_000_000,
        ),
    )
    shutil.copytree(
        foreign.checkpoint_dir,
        paths.checkpoints / foreign.checkpoint_id,
    )

    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            """UPDATE checkpoint_registry
               SET checkpoint_id = ?, manifest_sha256 = ?, database_sha256 = ?,
                   database_size_bytes = ?
               WHERE checkpoint_id = ?""",
            (
                foreign.checkpoint_id,
                foreign.manifest_sha256,
                foreign.database_sha256,
                foreign.database_size_bytes,
                genesis.checkpoint_id,
            ),
        )
        connection.execute(
            "UPDATE organism SET latest_stable_checkpoint_id = ? WHERE singleton_id = 1",
            (foreign.checkpoint_id,),
        )
        connection.commit()
    finally:
        connection.close()

    before_status = read_status(paths)
    before_database = (paths.database.stat().st_size, _digest(paths.database))
    before_checkpoint_files = {
        str(path.relative_to(paths.checkpoints)): _digest(path)
        for path in sorted(paths.checkpoints.rglob("*"))
        if path.is_file()
    }

    with pytest.raises(
        RollbackPreparationRejectedError,
        match="does not match the canonical registry",
    ):
        prepare_rollback_archive(runtime_root, initial.organism_id, 2)

    assert read_status(paths) == before_status
    assert (paths.database.stat().st_size, _digest(paths.database)) == before_database
    assert {
        str(path.relative_to(paths.checkpoints)): _digest(path)
        for path in sorted(paths.checkpoints.rglob("*"))
        if path.is_file()
    } == before_checkpoint_files
    assert not paths.rollback_archives.exists()
