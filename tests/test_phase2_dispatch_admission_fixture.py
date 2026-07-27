from __future__ import annotations

import inspect
import json
from pathlib import Path
import sqlite3

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_dispatch_runtime import (
    DispatchAdmissionBusyError,
    DispatchAdmissionRejectedError,
    FixtureExecutionError,
    admit_fixture_dispatch,
    build_dispatch_admission_payload,
    build_dispatch_charge,
    charge_id_from_dispatch_id,
    perform_fixture_dispatch,
)
from sudachi_life.phase2_fixture import run_deterministic_fixture
from sudachi_life.phase2_protocol import canonical_json_bytes
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
)
from sudachi_life.runtime_storage import (
    ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
    active_database_allocated_bytes,
)
from sudachi_life.storage import connect_database, read_status

from phase1_audit_helpers import _wake_clock


DISPATCH_EVENT_TYPE = "consultation_dispatch_admitted"
DISPATCH_SOURCE = "administration:consultation.dispatch"


def _init_request(tmp_path: Path, organism_id: str = "dispatch-runtime"):
    root = tmp_path / organism_id
    initialize_organism(
        root,
        organism_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_100_000_000_000_000,
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

    enqueue_garden_tick(
        paths,
        f"{organism_id}-tick",
        clock=FakeClock([ClockReading(2_101_000_000_000_000, 20_000_000)]),
    )
    wake = perform_garden_wake(
        root,
        organism_id,
        seed=1,
        clock=_wake_clock(2_102_000_000_000_000),
    )
    assert wake.consultation_request is not None
    assert wake.consultation_request.created is True
    return root, paths, wake


def _rows(paths: OrganismPaths) -> dict[str, list[sqlite3.Row]]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "dispatch": connection.execute(
                "SELECT * FROM consultation_dispatch ORDER BY event_sequence"
            ).fetchall(),
            "charge": connection.execute(
                "SELECT * FROM consultation_cost_charge ORDER BY event_sequence"
            ).fetchall(),
            "event": connection.execute(
                "SELECT * FROM event WHERE event_type=? ORDER BY event_sequence",
                (DISPATCH_EVENT_TYPE,),
            ).fetchall(),
            "checkpoint": connection.execute(
                "SELECT * FROM checkpoint_registry ORDER BY event_sequence"
            ).fetchall(),
        }
    finally:
        connection.close()


def test_adr0011_charge_id_ledger_and_payload_are_exact() -> None:
    dispatch_id = "consultation-dispatch:" + "a" * 64
    request = {"request_id": "consultation-request:" + "b" * 64}
    request_bytes = len(canonical_json_bytes(request))
    charge_id = charge_id_from_dispatch_id(dispatch_id)
    assert charge_id == "consultation-cost-charge:" + "a" * 64

    charge = build_dispatch_charge(
        dispatch_id=dispatch_id,
        request_canonical_size_bytes=request_bytes,
        request_envelope=request,
    )
    assert charge == {
        "attempt_count": 1,
        "charge_id": charge_id,
        "declared_latency_ms": 0,
        "fixture_invocation_count": 1,
        "human_minutes": 0,
        "model_units": 0,
        "money_microunits": 0,
        "request_bytes": request_bytes,
        "work_units": 1,
    }
    dispatch = {"dispatch_id": dispatch_id, "event_sequence": 13}
    assert build_dispatch_admission_payload(dispatch=dispatch, charge=charge) == {
        "charge": charge,
        "dispatch": dispatch,
    }

    with pytest.raises(DispatchAdmissionRejectedError, match="dispatch ID"):
        charge_id_from_dispatch_id("wrong:" + "a" * 64)
    with pytest.raises(DispatchAdmissionRejectedError, match="request bytes"):
        build_dispatch_charge(
            dispatch_id=dispatch_id,
            request_canonical_size_bytes=request_bytes + 1,
            request_envelope=request,
        )
    with pytest.raises(DispatchAdmissionRejectedError, match="field set"):
        build_dispatch_admission_payload(
            dispatch={**dispatch, "retry": True},
            charge=charge,
        )


def test_admission_atomically_commits_exact_dispatch_charge_and_single_event(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path)
    request_id = wake.consultation_request.request_id
    before = read_status(paths)
    before_rows = _rows(paths)

    clock = FakeClock.fixed(
        wall_time_utc_us=2_103_000_000_000_000,
        monotonic_ns=40_000_000,
    )
    result = admit_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=request_id,
        fixture_case_id="valid-action-candidate",
        clock=clock,
    )
    assert result.created is True
    assert clock.read_count == 1
    assert result.charge_id == charge_id_from_dispatch_id(result.dispatch_id)
    assert result.charge["request_bytes"] == len(
        canonical_json_bytes(result.request_envelope)
    )
    assert result.dispatch_envelope["event_sequence"] == result.event_sequence

    rows = _rows(paths)
    assert len(rows["dispatch"]) == 1
    assert len(rows["charge"]) == 1
    assert len(rows["event"]) == 1
    dispatch_row = rows["dispatch"][0]
    charge_row = rows["charge"][0]
    event_row = rows["event"][0]
    assert int(dispatch_row["event_sequence"]) == result.event_sequence
    assert int(charge_row["event_sequence"]) == result.event_sequence
    assert int(event_row["event_sequence"]) == result.event_sequence
    assert dispatch_row["dispatch_id"] == result.dispatch_id
    assert dispatch_row["request_id"] == request_id
    assert dispatch_row["configuration_version"] == FIXTURE_CONFIGURATION_VERSION
    assert json.loads(dispatch_row["envelope_json"]) == result.dispatch_envelope
    assert int(dispatch_row["canonical_size_bytes"]) == len(
        canonical_json_bytes(result.dispatch_envelope)
    )
    assert charge_row["charge_id"] == result.charge_id
    for key in (
        "attempt_count",
        "fixture_invocation_count",
        "work_units",
        "request_bytes",
        "human_minutes",
        "model_units",
        "money_microunits",
        "declared_latency_ms",
    ):
        assert int(charge_row[key]) == result.charge[key]
    assert event_row["source"] == DISPATCH_SOURCE
    assert int(event_row["lifecycle_number"]) == before.lifecycle_number
    assert json.loads(event_row["payload_json"]) == {
        "charge": result.charge,
        "dispatch": result.dispatch_envelope,
    }

    after = read_status(paths)
    assert after.lifecycle_number == before.lifecycle_number
    assert after.consecutive_failures == before.consecutive_failures
    assert after.environment_step == before.environment_step
    assert after.latest_stable_checkpoint_id == before.latest_stable_checkpoint_id
    assert after.latest_stable_event_sequence == before.latest_stable_event_sequence
    assert len(rows["checkpoint"]) == len(before_rows["checkpoint"])

    connection = connect_database(paths.database, read_only=True)
    try:
        request_row = connection.execute(
            "SELECT canonical_size_bytes, envelope_json FROM consultation_request "
            "WHERE request_id=?",
            (request_id,),
        ).fetchone()
        assert request_row is not None
        assert int(request_row["canonical_size_bytes"]) == result.charge["request_bytes"]
        assert len(request_row["envelope_json"].encode("utf-8")) == result.charge[
            "request_bytes"
        ]
        allocated = active_database_allocated_bytes(connection)
        assert allocated + ACTIVE_DATABASE_WAKE_RESERVE_BYTES <= 8 * 1024 * 1024
    finally:
        connection.close()


@pytest.mark.parametrize(
    "fault",
    ["after_event", "after_dispatch", "after_charge", "before_commit"],
)
def test_admission_faults_roll_back_event_dispatch_and_charge(
    tmp_path: Path,
    fault: str,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id=f"dispatch-fault-{fault}")
    with pytest.raises(RuntimeError, match="protected dispatch admission fault"):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="valid-action-candidate",
            clock=FakeClock.fixed(
                wall_time_utc_us=2_104_000_000_000_000,
                monotonic_ns=50_000_000,
            ),
            protected_test_fault=fault,
        )
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []


def test_repeated_admission_is_idempotent_and_reads_no_clock(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-idempotent")
    first = admit_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-abstain",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_105_000_000_000_000,
            monotonic_ns=60_000_000,
        ),
    )
    no_clock = FakeClock([])
    second = admit_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-abstain",
        clock=no_clock,
    )
    assert second.created is False
    assert second.dispatch_id == first.dispatch_id
    assert second.charge_id == first.charge_id
    assert second.event_sequence == first.event_sequence
    assert no_clock.read_count == 0
    rows = _rows(paths)
    assert len(rows["dispatch"]) == len(rows["charge"]) == len(rows["event"]) == 1

    with pytest.raises(DispatchAdmissionRejectedError, match="conflicting fixture case"):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="valid-defer",
            clock=FakeClock([]),
        )


def test_competing_admission_fails_fast_without_queueing(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-busy")
    blocker = connect_database(paths.database)
    try:
        blocker.execute("BEGIN IMMEDIATE")
        with pytest.raises(DispatchAdmissionBusyError, match="busy"):
            admit_fixture_dispatch(
                root,
                paths.organism_id,
                request_id=wake.consultation_request.request_id,
                fixture_case_id="valid-action-candidate",
                clock=FakeClock([]),
            )
    finally:
        blocker.rollback()
        blocker.close()
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []


def test_fixture_runs_only_after_commit_and_without_sqlite_ownership(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-lock-release")
    calls: list[tuple[dict[str, object], str]] = []

    def fixture(request_envelope: dict[str, object], fixture_case_id: str) -> bytes:
        calls.append((request_envelope, fixture_case_id))
        probe = connect_database(paths.database)
        try:
            probe.execute("BEGIN IMMEDIATE")
            counts = probe.execute(
                "SELECT (SELECT COUNT(*) FROM consultation_dispatch), "
                "(SELECT COUNT(*) FROM consultation_cost_charge), "
                "(SELECT COUNT(*) FROM event WHERE event_type=?)",
                (DISPATCH_EVENT_TYPE,),
            ).fetchone()
            assert tuple(counts) == (1, 1, 1)
            probe.rollback()
        finally:
            probe.close()
        return b"fixture-bytes"

    result = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-action-candidate",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_106_000_000_000_000,
            monotonic_ns=70_000_000,
        ),
        fixture_runner=fixture,
    )
    assert result.admission.created is True
    assert result.fixture_invoked is True
    assert result.fixture_output == b"fixture-bytes"
    assert calls == [(result.admission.request_envelope, "valid-action-candidate")]

    second = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-action-candidate",
        clock=FakeClock([]),
        fixture_runner=lambda *_: pytest.fail("fixture retry was authorized"),
    )
    assert second.admission.created is False
    assert second.fixture_invoked is False
    assert second.fixture_output is None


def test_fixture_exception_preserves_single_conservative_charge(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-fixture-error")

    def failing_fixture(_request: dict[str, object], _case: str) -> bytes:
        raise ValueError("fixture failure")

    with pytest.raises(FixtureExecutionError, match="fixture failure"):
        perform_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="fixture-exception",
            clock=FakeClock.fixed(
                wall_time_utc_us=2_107_000_000_000_000,
                monotonic_ns=80_000_000,
            ),
            fixture_runner=failing_fixture,
        )
    rows = _rows(paths)
    assert len(rows["dispatch"]) == len(rows["charge"]) == len(rows["event"]) == 1


def test_default_fixture_is_two_argument_deterministic_and_noncanonical(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-default-fixture")
    signature = inspect.signature(run_deterministic_fixture)
    assert tuple(signature.parameters) == ("request_envelope", "fixture_case_id")

    request_connection = connect_database(paths.database, read_only=True)
    try:
        request = json.loads(
            request_connection.execute(
                "SELECT envelope_json FROM consultation_request WHERE request_id=?",
                (wake.consultation_request.request_id,),
            ).fetchone()[0]
        )
    finally:
        request_connection.close()

    first = run_deterministic_fixture(request, "valid-defer")
    second = run_deterministic_fixture(
        json.loads(json.dumps(request)),
        "valid-defer",
    )
    assert isinstance(first, bytes)
    assert first == second
    assert len(first) <= 16 * 1024

    before = _rows(paths)
    result = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-defer",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_108_000_000_000_000,
            monotonic_ns=90_000_000,
        ),
    )
    assert result.fixture_output == first
    after = _rows(paths)
    assert len(after["dispatch"]) == 1
    assert len(after["charge"]) == 1
    assert len(after["event"]) == 1
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_response").fetchone()[0]) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_proposal").fetchone()[0]) == 0
        assert int(connection.execute("SELECT COUNT(*) FROM consultation_ingress_receipt").fetchone()[0]) == 0
    finally:
        connection.close()
    assert len(before["checkpoint"]) == len(after["checkpoint"])
