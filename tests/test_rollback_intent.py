from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil

import pytest

from sudachi_life.cli import main
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_intent import (
    RollbackBeginBusyError,
    RollbackBeginRejectedError,
    begin_rollback,
)
from sudachi_life.storage import connect_database, read_status, validate_canonical_state
from sudachi_life.wake import WakeRejectedError, WakeTransaction


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
            "status": read_status(paths),
            "organism": tuple(
                connection.execute(
                    "SELECT * FROM organism WHERE singleton_id = 1"
                ).fetchone()
            ),
            "environment": tuple(
                connection.execute(
                    "SELECT * FROM environment_state WHERE singleton_id = 1"
                ).fetchone()
            ),
            "plots": [
                tuple(row)
                for row in connection.execute(
                    "SELECT * FROM garden_plot ORDER BY plot_id"
                ).fetchall()
            ],
            "inventory": tuple(
                connection.execute(
                    "SELECT * FROM inventory WHERE singleton_id = 1"
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
            "checkpoints": _tree_snapshot(paths.checkpoints),
        }
    finally:
        connection.close()


def _protected_rows(paths: OrganismPaths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "environment": tuple(
                connection.execute(
                    "SELECT * FROM environment_state WHERE singleton_id = 1"
                ).fetchone()
            ),
            "plots": [
                tuple(row)
                for row in connection.execute(
                    "SELECT * FROM garden_plot ORDER BY plot_id"
                ).fetchall()
            ],
            "inventory": tuple(
                connection.execute(
                    "SELECT * FROM inventory WHERE singleton_id = 1"
                ).fetchone()
            ),
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
            "checkpoints": _tree_snapshot(paths.checkpoints),
        }
    finally:
        connection.close()


def test_begin_rollback_atomically_records_intent_and_blocks_normal_wake(
    initialized,
) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(
        paths,
        "rollback-intent-queued-tick",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
    archive_before = _tree_snapshot(archive.archive_dir)
    protected_before = _protected_rows(paths)
    status_before = read_status(paths)

    clock = FakeClock([ClockReading(300, 3_000_000)])
    result = begin_rollback(
        runtime_root,
        initial.organism_id,
        archive.archive_id,
        clock=clock,
    )

    assert clock.read_count == 1
    assert result.as_dict() == {
        "organism_id": initial.organism_id,
        "archive_id": archive.archive_id,
        "archive_manifest_sha256": archive.manifest_sha256,
        "selected_checkpoint_id": genesis.checkpoint_id,
        "selected_checkpoint_event_sequence": 2,
        "lineage_generation": 0,
        "lifecycle_number": 0,
        "pre_rollback_status": "sleeping",
        "status": "rollback_in_progress",
        "pre_rollback_event_sequence": 3,
        "rollback_started_event_sequence": 4,
        "latest_stable_checkpoint_id": genesis.checkpoint_id,
        "latest_stable_event_sequence": 2,
    }

    status = read_status(paths)
    assert status.status == "rollback_in_progress"
    assert status.event_count == status_before.event_count + 1
    assert status.lineage_generation == status_before.lineage_generation
    assert status.lifecycle_number == status_before.lifecycle_number
    assert status.environment_step == status_before.environment_step
    assert status.latest_stable_checkpoint_id == genesis.checkpoint_id
    assert status.latest_stable_event_sequence == 2
    assert _protected_rows(paths) == protected_before
    assert _tree_snapshot(archive.archive_dir) == archive_before

    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT * FROM event WHERE event_sequence = 4"
        ).fetchone()
        assert row["event_type"] == "rollback_started"
        assert row["source"] == "administration:rollback"
        assert row["wall_time_utc_us"] == 300
        assert row["lineage_generation"] == 0
        assert row["lifecycle_number"] == 0
        assert json.loads(row["payload_json"]) == {
            "archive_database_sha256": archive.database_sha256,
            "archive_id": archive.archive_id,
            "archive_manifest_sha256": archive.manifest_sha256,
            "latest_stable_checkpoint_id": genesis.checkpoint_id,
            "latest_stable_event_sequence": 2,
            "pre_rollback_event_sequence": 3,
            "pre_rollback_lifecycle_number": 0,
            "pre_rollback_lineage_generation": 0,
            "pre_rollback_status": "sleeping",
            "selected_checkpoint_database_sha256": genesis.database_sha256,
            "selected_checkpoint_event_sequence": 2,
            "selected_checkpoint_id": genesis.checkpoint_id,
            "selected_checkpoint_lineage_generation": 0,
            "selected_checkpoint_manifest_sha256": genesis.manifest_sha256,
        }
        inbox = connection.execute(
            "SELECT claimed_lifecycle_number, consumed FROM inbox_event"
        ).fetchone()
        assert tuple(inbox) == (None, 0)
    finally:
        connection.close()

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
    assert _protected_rows(paths) == protected_before


def test_rollback_begin_cli_adopts_verified_archive(initialized, capsys) -> None:
    runtime_root, initial, genesis = initialized
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "rollback",
            "begin",
            initial.organism_id,
            "--archive-id",
            archive.archive_id,
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["archive_id"] == archive.archive_id
    assert payload["selected_checkpoint_id"] == genesis.checkpoint_id
    assert payload["pre_rollback_event_sequence"] == 3
    assert payload["rollback_started_event_sequence"] == 4
    assert payload["status"] == "rollback_in_progress"
    assert read_status(
        OrganismPaths.build(runtime_root, initial.organism_id)
    ).status == "rollback_in_progress"


def test_begin_rollback_rejects_active_drift_before_clock_use(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
    enqueue_garden_tick(
        paths,
        "post-archive-drift",
        clock=FakeClock([ClockReading(210, 2_100_000)]),
    )
    before = _canonical_snapshot(paths)
    clock = FakeClock([])

    with pytest.raises(
        RollbackBeginRejectedError,
        match="active database .* drifted from rollback archive",
    ):
        begin_rollback(
            runtime_root,
            initial.organism_id,
            archive.archive_id,
            clock=clock,
        )

    assert clock.read_count == 0
    assert _canonical_snapshot(paths) == before


def test_begin_rollback_rejects_foreign_archive_before_clock_use(initialized) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _, foreign_genesis = initialize_organism(
        runtime_root,
        "foreign-rollback-intent",
        clock=FakeClock([ClockReading(500, 5_000_000)]),
    )
    foreign_archive = prepare_rollback_archive(
        runtime_root,
        "foreign-rollback-intent",
        foreign_genesis.event_sequence,
    )
    paths.rollback_archives.mkdir(mode=0o700, exist_ok=True)
    copied = paths.rollback_archives / foreign_archive.archive_id
    shutil.copytree(foreign_archive.archive_dir, copied)
    before = _canonical_snapshot(paths)
    clock = FakeClock([])

    with pytest.raises(
        RollbackBeginRejectedError,
        match="belongs to a different organism",
    ):
        begin_rollback(
            runtime_root,
            initial.organism_id,
            foreign_archive.archive_id,
            clock=clock,
        )

    assert clock.read_count == 0
    assert _canonical_snapshot(paths) == before


def test_begin_rollback_rejects_selected_checkpoint_artifact_drift(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
    (genesis.checkpoint_dir / "unexpected.txt").write_text(
        "checkpoint artifact drift",
        encoding="utf-8",
    )
    before = _canonical_snapshot(paths)
    clock = FakeClock([])

    with pytest.raises(
        RollbackBeginRejectedError,
        match="unexpected entries",
    ):
        begin_rollback(
            runtime_root,
            initial.organism_id,
            archive.archive_id,
            clock=clock,
        )

    assert clock.read_count == 0
    assert _canonical_snapshot(paths) == before


def test_begin_rollback_is_fail_fast_busy(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
    before = _canonical_snapshot(paths)
    competing = connect_database(paths.database)
    competing.execute("BEGIN IMMEDIATE")
    clock = FakeClock([])
    try:
        with pytest.raises(
            RollbackBeginBusyError,
            match="busy; this attempt was not queued",
        ):
            begin_rollback(
                runtime_root,
                initial.organism_id,
                archive.archive_id,
                clock=clock,
            )
    finally:
        competing.rollback()
        competing.close()

    assert clock.read_count == 0
    assert _canonical_snapshot(paths) == before


def test_begin_rollback_rejects_pending_checkpoint_before_clock_use(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
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
    clock = FakeClock([])

    with pytest.raises(
        RollbackBeginRejectedError,
        match="requires no pending checkpoint",
    ):
        begin_rollback(
            runtime_root,
            initial.organism_id,
            archive.archive_id,
            clock=clock,
        )

    assert clock.read_count == 0
    assert _canonical_snapshot(paths) == before


def test_begin_failure_rolls_back_status_and_audit_event_together(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
    archive_before = _tree_snapshot(archive.archive_dir)
    before = _canonical_snapshot(paths)
    clock = FakeClock([ClockReading(320, 3_200_000)])

    with pytest.raises(
        RollbackBeginRejectedError,
        match="injected rollback begin failure after event insert",
    ):
        begin_rollback(
            runtime_root,
            initial.organism_id,
            archive.archive_id,
            clock=clock,
            protected_test_fail_after_event_insert=True,
        )

    assert clock.read_count == 1
    assert _canonical_snapshot(paths) == before
    assert _tree_snapshot(archive.archive_dir) == archive_before
    with WakeTransaction.acquire(paths):
        pass
    assert _canonical_snapshot(paths) == before


def test_repeated_rollback_begin_is_rejected_without_second_event(initialized) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    archive = prepare_rollback_archive(
        runtime_root,
        initial.organism_id,
        genesis.event_sequence,
    )
    begin_rollback(
        runtime_root,
        initial.organism_id,
        archive.archive_id,
        clock=FakeClock([ClockReading(330, 3_300_000)]),
    )
    before = _canonical_snapshot(paths)

    same_clock = FakeClock([])
    with pytest.raises(
        RollbackBeginRejectedError,
        match="already active for archive",
    ):
        begin_rollback(
            runtime_root,
            initial.organism_id,
            archive.archive_id,
            clock=same_clock,
        )
    assert same_clock.read_count == 0

    other_clock = FakeClock([])
    with pytest.raises(
        RollbackBeginRejectedError,
        match="different archive",
    ):
        begin_rollback(
            runtime_root,
            initial.organism_id,
            "pre-rb-g000000-e000000000003-to-e000000000002-deadbeef",
            clock=other_clock,
        )
    assert other_clock.read_count == 0
    assert _canonical_snapshot(paths) == before
