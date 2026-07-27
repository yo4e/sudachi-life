from __future__ import annotations

import multiprocessing
from pathlib import Path

import pytest

from sudachi_life.clock import FakeClock
from sudachi_life.constants import (
    CHECKPOINT_STORE_MAX_BYTES,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from sudachi_life.phase2_disposition import DISPOSITION_SOURCE
from sudachi_life.phase2_disposition_runtime import (
    DispositionRejectedError,
    perform_disposition_wake,
)
from sudachi_life.storage import connect_database
from sudachi_life.wake import WakeBusyError

from test_phase2_disposition_wake import _clock, _ingressed


def _hold_write_lock(database: str, ready, release) -> None:
    connection = connect_database(Path(database))
    try:
        connection.execute("BEGIN IMMEDIATE")
        ready.set()
        if not release.wait(timeout=30):
            raise RuntimeError("lock-release signal timed out")
        connection.rollback()
    finally:
        connection.close()


def _consultation_counts(paths) -> tuple[int, int]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return (
            int(
                connection.execute(
                    "SELECT COUNT(*) FROM consultation_disposition"
                ).fetchone()[0]
            ),
            int(
                connection.execute(
                    "SELECT COUNT(*) FROM event WHERE source=?",
                    (DISPOSITION_SOURCE,),
                ).fetchone()[0]
            ),
        )
    finally:
        connection.close()


def test_spawned_competing_writer_fails_fast_then_explicit_wake_succeeds(
    tmp_path: Path,
) -> None:
    root, paths, _wake, _dispatch, ingress = _ingressed(
        tmp_path,
        organism_id="disposition-process-busy",
        case_id="valid-defer",
    )
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    release = context.Event()
    process = context.Process(
        target=_hold_write_lock,
        args=(str(paths.database), ready, release),
    )
    process.start()
    assert ready.wait(timeout=20)
    no_clock = FakeClock([])
    try:
        with pytest.raises(WakeBusyError, match="busy"):
            perform_disposition_wake(root, paths.organism_id, clock=no_clock)
        assert no_clock.read_count == 0
        assert _consultation_counts(paths) == (0, 0)
    finally:
        release.set()
        process.join(timeout=30)
    assert process.exitcode == 0

    result = perform_disposition_wake(
        root,
        paths.organism_id,
        clock=_clock(2_450_000_000_000_000),
    )
    assert result.proposal_id == ingress.proposal_id
    assert _consultation_counts(paths) == (1, 4)

    connection = connect_database(paths.database, read_only=True)
    try:
        rows = connection.execute(
            "SELECT schema_version, budget_config_version FROM event "
            "WHERE source=? ORDER BY event_sequence",
            (DISPOSITION_SOURCE,),
        ).fetchall()
        assert [(int(row[0]), row[1]) for row in rows] == [(2, "phase1-v1")] * 4
    finally:
        connection.close()


def test_real_checkpoint_store_refusal_is_nonmutating(tmp_path: Path) -> None:
    root, paths, _wake, _dispatch, _ingress = _ingressed(
        tmp_path,
        organism_id="disposition-checkpoint-store-limit",
        case_id="valid-defer",
    )
    padding = paths.checkpoints / "disposition-store-padding.bin"
    with padding.open("wb") as handle:
        handle.truncate(CHECKPOINT_STORE_MAX_BYTES + 1)

    no_clock = FakeClock([])
    with pytest.raises(DispositionRejectedError, match="checkpoint store"):
        perform_disposition_wake(root, paths.organism_id, clock=no_clock)
    assert no_clock.read_count == 0
    assert _consultation_counts(paths) == (0, 0)


def test_real_working_set_refusal_is_nonmutating(tmp_path: Path) -> None:
    root, paths, _wake, _dispatch, _ingress = _ingressed(
        tmp_path,
        organism_id="disposition-working-set-limit",
        case_id="valid-defer",
    )
    paths.rollback_archives.mkdir(parents=True, exist_ok=True)
    padding = paths.rollback_archives / "disposition-working-padding.bin"
    with padding.open("wb") as handle:
        handle.truncate(RUNTIME_WORKING_SET_MAX_BYTES + 1)

    no_clock = FakeClock([])
    with pytest.raises(DispositionRejectedError, match="working set"):
        perform_disposition_wake(root, paths.organism_id, clock=no_clock)
    assert no_clock.read_count == 0
    assert _consultation_counts(paths) == (0, 0)
