from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from sudachi_life import rollback as rollback_module
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import RollbackPreparationRejectedError
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_complete import complete_rollback
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_replace import replace_active_with_candidate
from sudachi_life.rollback_transform import transform_restore_candidate
from sudachi_life.storage import connect_database


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


def _canonical_snapshot(paths: OrganismPaths) -> dict[str, object]:
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


def _artifact_snapshot(paths: OrganismPaths) -> dict[str, object]:
    return {
        "checkpoints": _tree_snapshot(paths.checkpoints),
        "archives": _tree_snapshot(paths.rollback_archives),
        "candidates": _tree_snapshot(paths.restore_candidates),
    }


def _complete_first_rollback(initialized):
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    archive = rollback_module.prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
    begin_rollback(
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
        "protected single rollback retention",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_720_000_000_000_000,
            monotonic_ns=12_000_000,
        ),
    )
    replace_active_with_candidate(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
    )
    complete_rollback(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=1_730_000_000_000_000,
            monotonic_ns=13_000_000,
        ),
    )
    return runtime_root, initial, genesis, paths


def test_second_rollback_preparation_rejects_before_source_selection_or_archive_creation(
    initialized,
    monkeypatch,
) -> None:
    runtime_root, initial, _, paths = _complete_first_rollback(initialized)

    enqueue_garden_tick(
        paths,
        "first-post-rollback-tick-for-retention",
        clock=FakeClock([ClockReading(1_740_000_000_000_000, 14_000_000)]),
    )
    wake = perform_first_water_wake(
        runtime_root,
        initial.organism_id,
        seed=1,
        clock=FakeClock(
            [
                ClockReading(1_740_000_000_000_001, 20_000_000),
                ClockReading(1_740_000_000_000_001, 25_000_000),
                ClockReading(1_740_000_000_000_002, 30_000_000),
                ClockReading(1_740_000_000_000_003, 40_000_000),
                ClockReading(1_740_000_000_000_004, 50_000_000),
            ]
        ),
    )
    canonical_before = _canonical_snapshot(paths)
    artifacts_before = _artifact_snapshot(paths)
    selected_source = False

    def fail_if_source_selection_begins(*args, **kwargs):
        nonlocal selected_source
        selected_source = True
        raise AssertionError("completed rollback guard ran after source selection")

    monkeypatch.setattr(
        rollback_module,
        "_validate_selected_checkpoint",
        fail_if_source_selection_begins,
    )

    with pytest.raises(
        RollbackPreparationRejectedError,
        match=r"requires no completed rollback history; found 1 rollback_completed event\(s\)",
    ):
        rollback_module.prepare_rollback_archive(
            runtime_root,
            initial.organism_id,
            wake.checkpoint.event_sequence,
        )

    assert selected_source is False
    assert _canonical_snapshot(paths) == canonical_before
    assert _artifact_snapshot(paths) == artifacts_before
    assert len([entry for entry in paths.rollback_archives.iterdir() if entry.is_dir()]) == 1


def test_separate_new_organism_remains_eligible_for_first_rollback(initialized) -> None:
    runtime_root, initial, _, first_paths = _complete_first_rollback(initialized)
    first_canonical_before = _canonical_snapshot(first_paths)
    first_artifacts_before = _artifact_snapshot(first_paths)

    second_status, second_genesis = initialize_organism(
        runtime_root,
        "sudachi-1",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_750_000_000_000_000,
            monotonic_ns=15_000_000,
        ),
    )
    second_paths = OrganismPaths.build(runtime_root, second_status.organism_id)
    result = rollback_module.prepare_rollback_archive(
        runtime_root,
        second_status.organism_id,
        second_genesis.event_sequence,
    )

    assert result.organism_id == second_status.organism_id
    assert result.active_lineage_generation == 0
    assert result.selected_checkpoint_id == second_genesis.checkpoint_id
    assert result.archive_dir.parent == second_paths.rollback_archives
    assert _canonical_snapshot(first_paths) == first_canonical_before
    assert _artifact_snapshot(first_paths) == first_artifacts_before
    assert initial.organism_id != second_status.organism_id
