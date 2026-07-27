from __future__ import annotations

import inspect
import json
from pathlib import Path
import shutil

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.phase2_dispatch_runtime import (
    DispatchAdmissionRejectedError,
    admit_fixture_dispatch,
    perform_fixture_dispatch,
)
from sudachi_life.phase2_fixture import run_deterministic_fixture
from sudachi_life.phase2_response import validate_external_package
from sudachi_life.runtime_storage import active_database_allocated_bytes
from sudachi_life.storage import connect_database, read_status

from phase1_audit_helpers import _wake_clock
from test_phase2_dispatch_admission_fixture import _init_request, _rows


def _set_pending_checkpoint(paths, *, request_event_sequence: int) -> None:
    connection = connect_database(paths.database)
    try:
        organism = connection.execute(
            "SELECT lineage_generation FROM organism WHERE singleton_id=1"
        ).fetchone()
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE organism SET status='checkpoint_pending', checkpoint_pending=1, "
            "pending_checkpoint_generation=?, pending_checkpoint_event_sequence=? "
            "WHERE singleton_id=1",
            (int(organism["lineage_generation"]), request_event_sequence),
        )
        connection.commit()
    finally:
        connection.close()


def _advance_with_successful_water_wake(
    root: Path,
    paths,
    *,
    ordinal: int,
) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE inventory SET water_units=1 WHERE singleton_id=1")
        connection.execute(
            "UPDATE garden_plot SET moisture=0, fruit=0 WHERE plot_id='bed-a'"
        )
        connection.commit()
    finally:
        connection.close()
    enqueue_garden_tick(
        paths,
        f"advance-water-{ordinal}",
        clock=FakeClock(
            [ClockReading(2_200_000_000_000_000 + ordinal, 100_000_000 + ordinal)]
        ),
    )
    result = perform_garden_wake(
        root,
        paths.organism_id,
        seed=100 + ordinal,
        clock=_wake_clock(2_201_000_000_000_000 + ordinal),
    )
    assert result.evaluation.success is True
    assert result.checkpoint is not None


def test_pending_checkpoint_rejects_before_clock_or_consultation_mutation(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-pending")
    request_id = wake.consultation_request.request_id
    connection = connect_database(paths.database, read_only=True)
    try:
        request_event = int(
            connection.execute(
                "SELECT event_sequence FROM consultation_request WHERE request_id=?",
                (request_id,),
            ).fetchone()[0]
        )
    finally:
        connection.close()
    _set_pending_checkpoint(paths, request_event_sequence=request_event)

    no_clock = FakeClock([])
    with pytest.raises(DispatchAdmissionRejectedError, match="sleeping|pending"):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=request_id,
            fixture_case_id="valid-action-candidate",
            clock=no_clock,
        )
    assert no_clock.read_count == 0
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []


def test_request_must_be_inside_the_registered_stable_checkpoint(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-unstable")
    request_id = wake.consultation_request.request_id
    connection = connect_database(paths.database)
    try:
        request_event = int(
            connection.execute(
                "SELECT event_sequence FROM consultation_request WHERE request_id=?",
                (request_id,),
            ).fetchone()[0]
        )
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE organism SET latest_stable_event_sequence=? WHERE singleton_id=1",
            (request_event - 1,),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(DispatchAdmissionRejectedError, match="checkpoint-stable"):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=request_id,
            fixture_case_id="valid-action-candidate",
            clock=FakeClock([]),
        )
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []


def test_missing_stable_checkpoint_artifact_rejects_without_mutation(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-missing-cp")
    status = read_status(paths)
    assert status.latest_stable_checkpoint_id is not None
    shutil.rmtree(paths.checkpoints / status.latest_stable_checkpoint_id)

    with pytest.raises(DispatchAdmissionRejectedError, match="artifact is missing"):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="valid-action-candidate",
            clock=FakeClock([]),
        )
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []


def test_lifecycle_expiry_uses_legitimate_later_wakes_not_wall_time(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-expired")
    request_id = wake.consultation_request.request_id
    expiry = wake.lifecycle_number + 2
    for ordinal in range(1, 4):
        _advance_with_successful_water_wake(root, paths, ordinal=ordinal)
    assert read_status(paths).lifecycle_number == expiry + 1

    backward_clock = FakeClock(
        [ClockReading(1, 1)]
    )
    with pytest.raises(DispatchAdmissionRejectedError, match="expired"):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=request_id,
            fixture_case_id="valid-action-candidate",
            clock=backward_clock,
        )
    assert backward_clock.read_count == 0
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []


def test_forced_precommit_failure_never_calls_fixture(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-no-early-call")
    called = False

    def fixture(_request, _case):
        nonlocal called
        called = True
        return b"should-not-run"

    with pytest.raises(RuntimeError, match="protected dispatch admission fault"):
        perform_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="valid-action-candidate",
            clock=FakeClock.fixed(
                wall_time_utc_us=2_210_000_000_000_000,
                monotonic_ns=110_000_000,
            ),
            fixture_runner=fixture,
            protected_test_fault="before_commit",
        )
    assert called is False
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []


def test_real_active_database_reserve_refusal_is_nonmutating(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-real-reserve")
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("CREATE TABLE dispatch_padding (value BLOB NOT NULL)")
        while active_database_allocated_bytes(connection) <= 7 * 1024 * 1024:
            connection.execute(
                "INSERT INTO dispatch_padding(value) VALUES (zeroblob(65536))"
            )
        connection.execute("DROP TABLE dispatch_padding")
        connection.commit()
        allocated = active_database_allocated_bytes(connection)
        assert 7 * 1024 * 1024 < allocated <= 8 * 1024 * 1024
    finally:
        connection.close()

    with pytest.raises(DispatchAdmissionRejectedError, match="reserve"):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="valid-action-candidate",
            clock=FakeClock([]),
        )
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []


def test_fixture_has_no_database_path_network_subprocess_or_randomness_surface() -> None:
    module = inspect.getmodule(run_deterministic_fixture)
    assert module is not None
    source = inspect.getsource(module)
    forbidden = (
        "import os",
        "import pathlib",
        "from pathlib",
        "import random",
        "import socket",
        "import sqlite3",
        "import subprocess",
        "import requests",
        "urllib",
        "open(",
    )
    for token in forbidden:
        assert token not in source
    assert tuple(inspect.signature(run_deterministic_fixture).parameters) == (
        "request_envelope",
        "fixture_case_id",
    )


@pytest.mark.parametrize(
    "case_id",
    ["valid-action-candidate", "valid-abstain", "valid-defer", "unavailable"],
)
def test_fixture_bytes_validate_against_the_actual_committed_dispatch(
    tmp_path: Path,
    case_id: str,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id=f"dispatch-package-{case_id}",
    )
    result = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id=case_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_220_000_000_000_000,
            monotonic_ns=120_000_000,
        ),
    )
    assert result.fixture_output is not None
    package = json.loads(result.fixture_output)
    validated = validate_external_package(
        package,
        request_envelope=result.admission.request_envelope,
        dispatch_envelope=result.admission.dispatch_envelope,
    )
    assert validated == package
    assert run_deterministic_fixture(
        result.admission.request_envelope,
        case_id,
    ) == result.fixture_output

    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_response").fetchone()[0]) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_proposal").fetchone()[0]) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_ingress_receipt").fetchone()[0]) == 0
    finally:
        connection.close()
