from __future__ import annotations

import multiprocessing
from pathlib import Path
import shutil
import sqlite3

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
)
from sudachi_life.storage import connect_database
from sudachi_life.wake import WakeBusyError, WakeTransaction


def _initialize(tmp_path: Path, organism_id: str) -> tuple[Path, OrganismPaths]:
    root = tmp_path / "runtime"
    initialize_organism(
        root,
        organism_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_400_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
        schema_version=PHASE2_SCHEMA_VERSION,
        consultation_configuration_version=FIXTURE_CONFIGURATION_VERSION,
    )
    paths = OrganismPaths.build(root, organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE inventory SET water_units=0 WHERE singleton_id=1")
        connection.execute("UPDATE garden_plot SET moisture=1, fruit=0")
        connection.execute(
            "UPDATE environment_state SET objective_complete=0 WHERE singleton_id=1"
        )
        connection.commit()
    finally:
        connection.close()
    return root, paths


def _enqueue(paths: OrganismPaths, external_id: str) -> None:
    enqueue_garden_tick(
        paths,
        external_id,
        clock=FakeClock([ClockReading(2_401_000_000_000_000, 20_000_000)]),
    )


def _wake_clock(wall_times: tuple[int, int, int, int, int]) -> FakeClock:
    return FakeClock(
        [
            ClockReading(wall_times[0], 10_000_000),
            ClockReading(wall_times[1], 15_000_000),
            ClockReading(wall_times[2], 20_000_000),
            ClockReading(wall_times[3], 30_000_000),
            ClockReading(wall_times[4], 40_000_000),
        ]
    )


def _request_row(paths: OrganismPaths) -> tuple[object, ...]:
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT request_id, organism_id, lineage_generation, request_ordinal, "
            "lifecycle_number, event_sequence, expiry_lifecycle_number, "
            "configuration_version, envelope_json, canonical_size_bytes "
            "FROM consultation_request"
        ).fetchone()
        assert row is not None
        return tuple(row)
    finally:
        connection.close()


def _assert_no_attempt_mutation(paths: OrganismPaths) -> None:
    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM consultation_request"
        ).fetchone()[0] == 0
        assert connection.execute(
            "SELECT COUNT(*) FROM event "
            "WHERE source='organism:consultation.request'"
        ).fetchone()[0] == 0
        inbox = connection.execute(
            "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
            "WHERE external_event_id='request-concurrency-tick'"
        ).fetchone()
        assert inbox is not None
        assert tuple(inbox) == (None, 0)
    finally:
        connection.close()


def _hold_immediate_lock(
    database: str,
    ready,
    release,
) -> None:
    connection = sqlite3.connect(database, isolation_level=None, timeout=0.0)
    try:
        connection.execute("BEGIN IMMEDIATE")
        ready.set()
        release.wait(10)
        connection.rollback()
    finally:
        connection.close()


def test_backward_wall_time_does_not_change_request_identity_or_expiry(
    tmp_path: Path,
) -> None:
    base_root, base_paths = _initialize(tmp_path / "base", "request-backward-time")
    forward_root = tmp_path / "forward"
    backward_root = tmp_path / "backward"
    shutil.copytree(base_root, forward_root)
    shutil.copytree(base_root, backward_root)
    forward_paths = OrganismPaths.build(forward_root, base_paths.organism_id)
    backward_paths = OrganismPaths.build(backward_root, base_paths.organism_id)
    _enqueue(forward_paths, "request-time-tick")
    _enqueue(backward_paths, "request-time-tick")

    forward = perform_garden_wake(
        forward_root,
        forward_paths.organism_id,
        seed=5,
        clock=_wake_clock((1000, 1000, 1001, 1002, 1003)),
    )
    backward = perform_garden_wake(
        backward_root,
        backward_paths.organism_id,
        seed=5,
        clock=_wake_clock((1000, 999, 998, 997, 996)),
    )

    assert forward.consultation_request is not None
    assert backward.consultation_request is not None
    assert forward.consultation_request.created is True
    assert backward.consultation_request.created is True
    assert forward.consultation_request.request_id == backward.consultation_request.request_id
    assert forward.consultation_request.event_sequence == (
        backward.consultation_request.event_sequence
    )
    assert _request_row(forward_paths) == _request_row(backward_paths)
    assert _request_row(forward_paths)[6] == forward.lifecycle_number + 2


def test_nested_wake_is_fail_fast_and_not_queued_before_request_write(
    tmp_path: Path,
) -> None:
    root, paths = _initialize(tmp_path, "request-nested-wake")
    _enqueue(paths, "request-concurrency-tick")

    with WakeTransaction.acquire(paths):
        with pytest.raises(
            WakeBusyError,
            match="busy; this attempt was not queued",
        ):
            perform_garden_wake(
                root,
                paths.organism_id,
                seed=6,
                clock=_wake_clock((2000, 2000, 2001, 2002, 2003)),
            )
    _assert_no_attempt_mutation(paths)

    result = perform_garden_wake(
        root,
        paths.organism_id,
        seed=6,
        clock=_wake_clock((2000, 2000, 2001, 2002, 2003)),
    )
    assert result.consultation_request is not None
    assert result.consultation_request.created is True


def test_competing_process_wake_is_fail_fast_and_not_retried(
    tmp_path: Path,
) -> None:
    root, paths = _initialize(tmp_path, "request-competing-wake")
    _enqueue(paths, "request-concurrency-tick")
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    release = context.Event()
    process = context.Process(
        target=_hold_immediate_lock,
        args=(str(paths.database), ready, release),
    )
    process.start()
    try:
        assert ready.wait(10)
        with pytest.raises(
            WakeBusyError,
            match="busy; this attempt was not queued",
        ):
            perform_garden_wake(
                root,
                paths.organism_id,
                seed=7,
                clock=_wake_clock((3000, 3000, 3001, 3002, 3003)),
            )
        _assert_no_attempt_mutation(paths)
    finally:
        release.set()
        process.join(10)
        if process.is_alive():
            process.terminate()
            process.join(5)
    assert process.exitcode == 0

    result = perform_garden_wake(
        root,
        paths.organism_id,
        seed=7,
        clock=_wake_clock((3000, 3000, 3001, 3002, 3003)),
    )
    assert result.consultation_request is not None
    assert result.consultation_request.created is True
