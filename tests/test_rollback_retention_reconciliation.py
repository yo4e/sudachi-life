from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_complete import complete_rollback
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_replace import replace_active_with_candidate
from sudachi_life.rollback_transform import (
    CandidateTransformError,
    transform_restore_candidate,
)
from sudachi_life.storage import connect_database, read_status


class _ClockPlan:
    def __init__(self) -> None:
        self.wall_time_utc_us = 1_800_000_000_000_000
        self.monotonic_ns = 100_000_000

    def fixed(self) -> FakeClock:
        reading = ClockReading(self.wall_time_utc_us, self.monotonic_ns)
        self.wall_time_utc_us += 1_000
        self.monotonic_ns += 1_000_000
        return FakeClock([reading])

    def wake(self) -> FakeClock:
        wall = self.wall_time_utc_us
        mono = self.monotonic_ns
        self.wall_time_utc_us += 10_000
        self.monotonic_ns += 50_000_000
        return FakeClock(
            [
                ClockReading(wall, mono),
                ClockReading(wall + 1, mono + 5_000_000),
                ClockReading(wall + 2, mono + 10_000_000),
                ClockReading(wall + 3, mono + 20_000_000),
                ClockReading(wall + 4, mono + 30_000_000),
            ]
        )


def _registry(database: Path) -> list[tuple[object, ...]]:
    connection = connect_database(database, read_only=True)
    try:
        return [
            tuple(row)
            for row in connection.execute(
                "SELECT * FROM checkpoint_registry "
                "ORDER BY event_sequence, checkpoint_id"
            ).fetchall()
        ]
    finally:
        connection.close()


def _checkpoint_ids(database: Path) -> set[str]:
    return {str(row[0]) for row in _registry(database)}


def _prepare_post_retention_source(initialized):
    runtime_root, initial, _genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    plan = _ClockPlan()
    wakes = []
    for ordinal in range(1, 5):
        enqueue_garden_tick(
            paths,
            f"post-retention-{ordinal}",
            clock=plan.fixed(),
        )
        wakes.append(
            perform_garden_wake(
                runtime_root,
                initial.organism_id,
                seed=ordinal,
                clock=plan.wake(),
            )
        )

    selected = wakes[-1].checkpoint
    assert selected is not None
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        selected.event_sequence,
    )
    begin_rollback(
        runtime_root,
        initial.organism_id,
        archive.archive_id,
        clock=plan.fixed(),
    )
    source = build_restore_candidate(runtime_root, initial.organism_id)

    source_database = source.candidate_dir / "organism.sqlite3"
    archive_database = archive.archive_dir / "organism.sqlite3"
    missing = _checkpoint_ids(source_database) - _checkpoint_ids(archive_database)
    assert len(missing) == 1
    missing_checkpoint_id = next(iter(missing))
    assert not (paths.checkpoints / missing_checkpoint_id).exists()
    assert not (paths.checkpoints / f".pruning-{missing_checkpoint_id}").exists()
    return (
        runtime_root,
        initial,
        paths,
        plan,
        selected,
        archive,
        source,
        missing_checkpoint_id,
    )


def test_post_retention_rollback_reconciles_registry_and_allows_next_checkpoint(
    initialized,
) -> None:
    (
        runtime_root,
        initial,
        paths,
        plan,
        selected,
        archive,
        source,
        missing_checkpoint_id,
    ) = _prepare_post_retention_source(initialized)

    transformed = transform_restore_candidate(
        runtime_root,
        initial.organism_id,
        source.candidate_id,
        "reconcile retained rollback source",
        clock=plan.fixed(),
    )
    no_clock = FakeClock([])
    repeated = transform_restore_candidate(
        runtime_root,
        initial.organism_id,
        source.candidate_id,
        "reconcile retained rollback source",
        clock=no_clock,
    )
    assert repeated.as_dict() == transformed.as_dict()
    assert no_clock.read_count == 0

    source_database = source.candidate_dir / "organism.sqlite3"
    archive_database = archive.archive_dir / "organism.sqlite3"
    transformed_database = transformed.transformed_candidate_dir / "organism.sqlite3"
    assert missing_checkpoint_id in _checkpoint_ids(source_database)
    assert missing_checkpoint_id not in _checkpoint_ids(transformed_database)
    assert _registry(transformed_database) == _registry(archive_database)

    replace_active_with_candidate(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
    )
    completion = complete_rollback(
        runtime_root,
        initial.organism_id,
        transformed.transformed_candidate_id,
        clock=plan.fixed(),
    )
    assert completion.new_lineage_generation == 1
    assert completion.selected_checkpoint_id == selected.checkpoint_id
    assert _registry(paths.database) == _registry(archive_database)

    enqueue_garden_tick(paths, "first-post-retention-rollback", clock=plan.fixed())
    wake = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=5,
        clock=plan.wake(),
    )
    assert wake.checkpoint is not None
    assert wake.checkpoint.lineage_generation == 1
    status = read_status(paths)
    assert status.status == "sleeping"
    assert status.lineage_generation == 1
    assert status.lifecycle_number == 5
    for checkpoint_id in _checkpoint_ids(paths.database):
        assert (paths.checkpoints / checkpoint_id).is_dir()


def test_post_retention_transform_rejects_reappeared_staged_artifact(
    initialized,
) -> None:
    (
        runtime_root,
        initial,
        paths,
        plan,
        _selected,
        _archive,
        source,
        missing_checkpoint_id,
    ) = _prepare_post_retention_source(initialized)

    staged = paths.checkpoints / f".pruning-{missing_checkpoint_id}"
    staged.mkdir()
    (staged / "unexpected.txt").write_text("stale staged artifact", encoding="utf-8")
    clock = plan.fixed()
    with pytest.raises(CandidateTransformError, match="still has a staged artifact"):
        transform_restore_candidate(
            runtime_root,
            initial.organism_id,
            source.candidate_id,
            "reject unexplained staged artifact",
            clock=clock,
        )
    assert clock.read_count == 1
    assert {entry.name for entry in paths.restore_candidates.iterdir()} == {
        source.candidate_id
    }
