from __future__ import annotations

import multiprocessing
import os
from pathlib import Path

import pytest

from sudachi_life.clock import FakeClock
from sudachi_life.phase2_dispatch_runtime import perform_fixture_dispatch
from sudachi_life.phase2_ingress_runtime import (
    IngressRejectedError,
    TerminalizationRejectedError,
    ingress_external_package,
    reconcile_interrupted_dispatch,
    terminalize_fixture_dispatch,
)
from sudachi_life.runtime_storage import active_database_allocated_bytes
from sudachi_life.storage import connect_database

from test_phase2_dispatch_admission_fixture import _init_request


def _pad_active_database_beyond_reserve(paths, *, table_name: str) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(f"CREATE TABLE {table_name} (value BLOB NOT NULL)")
        while active_database_allocated_bytes(connection) <= 7 * 1024 * 1024:
            connection.execute(
                f"INSERT INTO {table_name}(value) VALUES (zeroblob(65536))"
            )
        connection.execute(f"DROP TABLE {table_name}")
        connection.commit()
        allocated = active_database_allocated_bytes(connection)
        assert 7 * 1024 * 1024 < allocated <= 8 * 1024 * 1024
    finally:
        connection.close()


def _exit_fixture(_request: dict[str, object], _case: str) -> bytes:
    os._exit(23)


def _crash_after_admission_worker(
    root: str,
    organism_id: str,
    request_id: str,
) -> None:
    perform_fixture_dispatch(
        Path(root),
        organism_id,
        request_id=request_id,
        fixture_case_id="crash-after-admission",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_300_000_000_000_000,
            monotonic_ns=300_000_000,
        ),
        fixture_runner=_exit_fixture,
    )


def test_success_ingress_refuses_real_reserve_without_partial_state(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="ingress-real-reserve")
    dispatched = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-defer",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_301_000_000_000_000,
            monotonic_ns=310_000_000,
        ),
    )
    _pad_active_database_beyond_reserve(paths, table_name="ingress_padding")

    with pytest.raises(IngressRejectedError, match="reserve"):
        ingress_external_package(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            raw_package_bytes=dispatched.fixture_output,
            clock=FakeClock([]),
        )
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_response").fetchone()[0]) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_proposal").fetchone()[0]) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_ingress_receipt").fetchone()[0]) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_cost_completion").fetchone()[0]) == 0
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type='consultation_response_ingressed'"
            ).fetchone()[0]
        ) == 0
    finally:
        connection.close()


def test_terminalization_refuses_real_reserve_without_partial_state(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="terminal-real-reserve")
    dispatched = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="malformed-response",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_302_000_000_000_000,
            monotonic_ns=320_000_000,
        ),
    )
    _pad_active_database_beyond_reserve(paths, table_name="terminal_padding")

    with pytest.raises(TerminalizationRejectedError, match="reserve"):
        terminalize_fixture_dispatch(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            reason_code="fixture_output_invalid",
            raw_package_bytes=dispatched.fixture_output,
            clock=FakeClock([]),
        )
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(
            connection.execute("SELECT COUNT(*) FROM consultation_dispatch_terminal").fetchone()[0]
        ) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_cost_completion").fetchone()[0]) == 0
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type='consultation_dispatch_terminalized'"
            ).fetchone()[0]
        ) == 0
    finally:
        connection.close()


def test_spawned_exit_after_admission_leaves_charge_then_reconciles_without_fixture(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="ingress-spawn-crash")
    context = multiprocessing.get_context("spawn")
    process = context.Process(
        target=_crash_after_admission_worker,
        args=(str(root), paths.organism_id, wake.consultation_request.request_id),
    )
    process.start()
    process.join(timeout=30)
    assert process.exitcode == 23

    connection = connect_database(paths.database, read_only=True)
    try:
        dispatch = connection.execute("SELECT dispatch_id FROM consultation_dispatch").fetchone()
        assert dispatch is not None
        dispatch_id = str(dispatch["dispatch_id"])
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_cost_charge").fetchone()[0]) == 1
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_response").fetchone()[0]) == 0
        assert int(
            connection.execute("SELECT COUNT(*) FROM consultation_dispatch_terminal").fetchone()[0]
        ) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_cost_completion").fetchone()[0]) == 0
    finally:
        connection.close()

    result = reconcile_interrupted_dispatch(
        root,
        paths.organism_id,
        dispatch_id=dispatch_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_303_000_000_000_000,
            monotonic_ns=330_000_000,
        ),
    )
    assert result.reason_code == "dispatch_interrupted"
    assert result.measured_package_bytes == 0
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_cost_charge").fetchone()[0]) == 1
        assert int(
            connection.execute("SELECT COUNT(*) FROM consultation_dispatch_terminal").fetchone()[0]
        ) == 1
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_cost_completion").fetchone()[0]) == 1
    finally:
        connection.close()


def test_lineage_logical_payload_is_request_plus_successful_package_only(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="ingress-logical-ledger")
    dispatched = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-action-candidate",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_304_000_000_000_000,
            monotonic_ns=340_000_000,
        ),
    )
    ingress_external_package(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        raw_package_bytes=dispatched.fixture_output,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_305_000_000_000_000,
            monotonic_ns=350_000_000,
        ),
    )
    connection = connect_database(paths.database, read_only=True)
    try:
        request_bytes = int(
            connection.execute(
                "SELECT SUM(canonical_size_bytes) FROM consultation_request WHERE lineage_generation=0"
            ).fetchone()[0]
        )
        package_bytes = int(
            connection.execute(
                "SELECT SUM(measured_package_bytes) FROM consultation_ingress_receipt"
            ).fetchone()[0]
        )
        logical = request_bytes + package_bytes
        assert logical == len(dispatched.admission.request_envelope_json) if False else logical
        assert request_bytes == len(
            connection.execute(
                "SELECT envelope_json FROM consultation_request"
            ).fetchone()[0].encode("utf-8")
        )
        assert package_bytes == len(dispatched.fixture_output)
        metadata_bytes = int(
            connection.execute(
                "SELECT canonical_size_bytes FROM consultation_response"
            ).fetchone()[0]
        ) + int(
            connection.execute(
                "SELECT canonical_size_bytes FROM consultation_proposal"
            ).fetchone()[0]
        )
        assert logical + metadata_bytes > logical
        assert logical <= 64 * 1024
    finally:
        connection.close()


def test_invalid_terminal_bytes_do_not_enter_logical_payload(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="terminal-logical-ledger")
    dispatched = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="malformed-response",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_306_000_000_000_000,
            monotonic_ns=360_000_000,
        ),
    )
    terminalize_fixture_dispatch(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        reason_code="fixture_output_invalid",
        raw_package_bytes=dispatched.fixture_output,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_307_000_000_000_000,
            monotonic_ns=370_000_000,
        ),
    )
    connection = connect_database(paths.database, read_only=True)
    try:
        request_bytes = int(
            connection.execute(
                "SELECT SUM(canonical_size_bytes) FROM consultation_request WHERE lineage_generation=0"
            ).fetchone()[0]
        )
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_ingress_receipt").fetchone()[0]) == 0
        assert request_bytes <= 64 * 1024
        completion = connection.execute(
            "SELECT measured_package_bytes FROM consultation_cost_completion"
        ).fetchone()
        assert int(completion["measured_package_bytes"]) == len(dispatched.fixture_output)
    finally:
        connection.close()
