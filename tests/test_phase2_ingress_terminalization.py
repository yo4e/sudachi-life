from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.phase2_dispatch_runtime import perform_fixture_dispatch
from sudachi_life.phase2_ingress_runtime import (
    IngressBusyError,
    IngressRejectedError,
    TerminalizationRejectedError,
    completion_id_from_dispatch_id,
    ingress_external_package,
    receipt_id_from_package_digest,
    reconcile_interrupted_dispatch,
    rejected_package_digest,
    terminal_id_from_dispatch_id,
    terminalize_fixture_dispatch,
)
from sudachi_life.phase2_protocol import canonical_json_bytes
from sudachi_life.phase2_response import external_package_digest
from sudachi_life.runtime_storage import ACTIVE_DATABASE_WAKE_RESERVE_BYTES, active_database_allocated_bytes
from sudachi_life.storage import connect_database, read_status

from phase1_audit_helpers import _wake_clock
from test_phase2_dispatch_admission_fixture import _init_request


INGRESS_EVENT = "consultation_response_ingressed"
INGRESS_SOURCE = "administration:consultation.response_ingress"
TERMINAL_EVENT = "consultation_dispatch_terminalized"
TERMINAL_SOURCE = "administration:consultation.dispatch_terminal"
RAW_REJECT_DOMAIN = b"sudachi.consultation/v1\nrejected-package-bytes\n"


def _fixture_dispatch(
    tmp_path: Path,
    *,
    organism_id: str,
    case_id: str = "valid-action-candidate",
):
    root, paths, wake = _init_request(tmp_path, organism_id=organism_id)
    dispatched = perform_fixture_dispatch(
        root,
        organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id=case_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_200_000_000_000_000,
            monotonic_ns=100_000_000,
        ),
    )
    assert dispatched.fixture_invoked is True
    assert dispatched.fixture_output is not None
    return root, paths, wake, dispatched


def _counts(paths) -> dict[str, int]:
    connection = connect_database(paths.database, read_only=True)
    try:
        names = (
            "consultation_response",
            "consultation_proposal",
            "consultation_ingress_receipt",
            "consultation_cost_completion",
            "consultation_dispatch_terminal",
        )
        result = {
            name: int(connection.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])
            for name in names
        }
        result["ingress_event"] = int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type=?", (INGRESS_EVENT,)
            ).fetchone()[0]
        )
        result["terminal_event"] = int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type=?", (TERMINAL_EVENT,)
            ).fetchone()[0]
        )
        return result
    finally:
        connection.close()


def test_adr0012_typed_aliases_and_raw_rejected_digest_are_exact() -> None:
    dispatch_id = "consultation-dispatch:" + "a" * 64
    package_digest = "b" * 64
    raw = b"{not-json\xff"
    assert completion_id_from_dispatch_id(dispatch_id) == (
        "consultation-cost-completion:" + "a" * 64
    )
    assert terminal_id_from_dispatch_id(dispatch_id) == (
        "consultation-dispatch-terminal:" + "a" * 64
    )
    assert receipt_id_from_package_digest(package_digest) == (
        "consultation-ingress-receipt:" + package_digest
    )
    assert rejected_package_digest(raw) == hashlib.sha256(RAW_REJECT_DOMAIN + raw).hexdigest()

    with pytest.raises(IngressRejectedError, match="dispatch ID"):
        completion_id_from_dispatch_id("wrong:" + "a" * 64)
    with pytest.raises(IngressRejectedError, match="package digest"):
        receipt_id_from_package_digest("A" * 64)


def test_success_ingress_atomically_commits_exact_rows_event_and_parents(
    tmp_path: Path,
) -> None:
    root, paths, wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id="ingress-success",
    )
    raw = dispatched.fixture_output
    before = read_status(paths)
    clock = FakeClock.fixed(
        wall_time_utc_us=2_201_000_000_000_000,
        monotonic_ns=110_000_000,
    )
    result = ingress_external_package(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        raw_package_bytes=raw,
        clock=clock,
    )
    assert result.created is True
    assert clock.read_count == 1
    assert result.measured_package_bytes == len(raw)
    package = json.loads(raw)
    expected_digest = external_package_digest(
        package,
        request_envelope=dispatched.admission.request_envelope,
        dispatch_envelope=dispatched.admission.dispatch_envelope,
    )
    assert result.package_digest == expected_digest
    assert result.receipt_id == "consultation-ingress-receipt:" + expected_digest
    dispatch_digest = dispatched.admission.dispatch_id.split(":", 1)[1]
    assert result.completion_id == "consultation-cost-completion:" + dispatch_digest

    connection = connect_database(paths.database, read_only=True)
    try:
        response = connection.execute("SELECT * FROM consultation_response").fetchone()
        proposal = connection.execute("SELECT * FROM consultation_proposal").fetchone()
        receipt = connection.execute("SELECT * FROM consultation_ingress_receipt").fetchone()
        completion = connection.execute("SELECT * FROM consultation_cost_completion").fetchone()
        event = connection.execute(
            "SELECT * FROM event WHERE event_type=?", (INGRESS_EVENT,)
        ).fetchone()
        request_event = int(
            connection.execute(
                "SELECT event_sequence FROM consultation_request WHERE request_id=?",
                (result.request_id,),
            ).fetchone()[0]
        )
        dispatch_event = int(
            connection.execute(
                "SELECT event_sequence FROM consultation_dispatch WHERE dispatch_id=?",
                (result.dispatch_id,),
            ).fetchone()[0]
        )
        assert response is not None and proposal is not None
        assert receipt is not None and completion is not None and event is not None
        assert int(response["event_sequence"]) == result.event_sequence
        assert int(receipt["event_sequence"]) == result.event_sequence
        assert int(event["event_sequence"]) == result.event_sequence
        assert response["response_id"] == result.response_id
        assert response["package_digest"] == expected_digest
        assert int(response["canonical_size_bytes"]) == len(
            canonical_json_bytes(package["response"])
        )
        assert proposal["proposal_id"] == package["proposals"][0]["proposal_id"]
        assert receipt["receipt_id"] == result.receipt_id
        assert receipt["package_digest"] == expected_digest
        assert int(receipt["measured_package_bytes"]) == len(raw)
        assert completion["completion_id"] == result.completion_id
        assert completion["response_id"] == result.response_id
        assert completion["terminal_id"] is None
        assert int(completion["measured_package_bytes"]) == len(raw)
        payload = json.loads(event["payload_json"])
        assert set(payload) == {"completion", "receipt"}
        assert payload["completion"] == {
            "completion_id": result.completion_id,
            "dispatch_id": result.dispatch_id,
            "measured_package_bytes": len(raw),
            "response_id": result.response_id,
        }
        assert payload["receipt"] == {
            "authority": {
                "source": INGRESS_SOURCE,
                "writer_category": "administration",
            },
            "dispatch_id": result.dispatch_id,
            "event_sequence": result.event_sequence,
            "measured_package_bytes": len(raw),
            "package_digest": expected_digest,
            "parent_event_sequences": sorted([request_event, dispatch_event]),
            "protocol_version": 1,
            "receipt_id": result.receipt_id,
            "receipt_schema": "sudachi.consultation.ingress_receipt/v1",
            "request_id": result.request_id,
            "response_id": result.response_id,
        }
        assert event["source"] == INGRESS_SOURCE
        assert int(event["lifecycle_number"]) == before.lifecycle_number
        allocated = active_database_allocated_bytes(connection)
        assert allocated + ACTIVE_DATABASE_WAKE_RESERVE_BYTES <= 8 * 1024 * 1024
    finally:
        connection.close()

    after = read_status(paths)
    assert after.lifecycle_number == before.lifecycle_number
    assert after.environment_step == before.environment_step
    assert after.consecutive_failures == before.consecutive_failures
    assert after.latest_stable_checkpoint_id == before.latest_stable_checkpoint_id


@pytest.mark.parametrize(
    "fault",
    [
        "after_event",
        "after_response",
        "after_proposal",
        "after_receipt",
        "after_completion",
        "before_commit",
    ],
)
def test_success_ingress_faults_roll_back_whole_branch(
    tmp_path: Path,
    fault: str,
) -> None:
    root, paths, _wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id=f"ingress-fault-{fault}",
    )
    with pytest.raises(RuntimeError, match="protected ingress fault"):
        ingress_external_package(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            raw_package_bytes=dispatched.fixture_output,
            clock=FakeClock.fixed(
                wall_time_utc_us=2_202_000_000_000_000,
                monotonic_ns=120_000_000,
            ),
            protected_test_fault=fault,
        )
    assert _counts(paths) == {
        "consultation_response": 0,
        "consultation_proposal": 0,
        "consultation_ingress_receipt": 0,
        "consultation_cost_completion": 0,
        "consultation_dispatch_terminal": 0,
        "ingress_event": 0,
        "terminal_event": 0,
    }


def test_unavailable_ingress_has_no_proposal_and_duplicate_is_idempotent(
    tmp_path: Path,
) -> None:
    root, paths, _wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id="ingress-unavailable",
        case_id="unavailable",
    )
    first = ingress_external_package(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        raw_package_bytes=dispatched.fixture_output,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_203_000_000_000_000,
            monotonic_ns=130_000_000,
        ),
    )
    no_clock = FakeClock([])
    second = ingress_external_package(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        raw_package_bytes=bytes(dispatched.fixture_output),
        clock=no_clock,
    )
    assert second.created is False
    assert second.response_id == first.response_id
    assert second.receipt_id == first.receipt_id
    assert no_clock.read_count == 0
    counts = _counts(paths)
    assert counts["consultation_response"] == 1
    assert counts["consultation_proposal"] == 0
    assert counts["consultation_ingress_receipt"] == 1
    assert counts["consultation_cost_completion"] == 1
    assert counts["ingress_event"] == 1

    changed = dispatched.fixture_output + b" "
    with pytest.raises(IngressRejectedError, match="conflicting|canonical"):
        ingress_external_package(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            raw_package_bytes=changed,
            clock=FakeClock([]),
        )


def test_busy_rejection_and_invalid_raw_bytes_write_nothing_and_permit_resubmission(
    tmp_path: Path,
) -> None:
    root, paths, _wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id="ingress-busy-invalid",
    )
    blocker = connect_database(paths.database)
    try:
        blocker.execute("BEGIN IMMEDIATE")
        with pytest.raises(IngressBusyError, match="busy"):
            ingress_external_package(
                root,
                paths.organism_id,
                dispatch_id=dispatched.admission.dispatch_id,
                raw_package_bytes=dispatched.fixture_output,
                clock=FakeClock([]),
            )
    finally:
        blocker.rollback()
        blocker.close()
    assert _counts(paths)["consultation_response"] == 0

    with pytest.raises(IngressRejectedError, match="16 KiB"):
        ingress_external_package(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            raw_package_bytes=b"x" * (16 * 1024 + 1),
            clock=FakeClock([]),
        )
    with pytest.raises(IngressRejectedError, match="JSON|UTF-8"):
        ingress_external_package(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            raw_package_bytes=b"{\xff",
            clock=FakeClock([]),
        )
    with pytest.raises(IngressRejectedError, match="canonical"):
        ingress_external_package(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            raw_package_bytes=dispatched.fixture_output + b"\n",
            clock=FakeClock([]),
        )
    assert _counts(paths)["consultation_response"] == 0

    accepted = ingress_external_package(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        raw_package_bytes=dispatched.fixture_output,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_204_000_000_000_000,
            monotonic_ns=140_000_000,
        ),
    )
    assert accepted.created is True


def test_invalid_terminalization_is_exact_atomic_and_idempotent(tmp_path: Path) -> None:
    root, paths, _wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id="terminal-invalid",
        case_id="malformed-response",
    )
    raw = dispatched.fixture_output
    clock = FakeClock.fixed(
        wall_time_utc_us=2_205_000_000_000_000,
        monotonic_ns=150_000_000,
    )
    first = terminalize_fixture_dispatch(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        reason_code="fixture_output_invalid",
        raw_package_bytes=raw,
        clock=clock,
    )
    assert first.created is True
    assert clock.read_count == 1
    digest = hashlib.sha256(RAW_REJECT_DOMAIN + raw).hexdigest()
    dispatch_digest = dispatched.admission.dispatch_id.split(":", 1)[1]
    assert first.terminal_id == "consultation-dispatch-terminal:" + dispatch_digest
    assert first.completion_id == "consultation-cost-completion:" + dispatch_digest
    assert first.rejected_package_digest == digest
    assert first.rejected_package_size_bytes == len(raw)

    connection = connect_database(paths.database, read_only=True)
    try:
        terminal = connection.execute("SELECT * FROM consultation_dispatch_terminal").fetchone()
        completion = connection.execute("SELECT * FROM consultation_cost_completion").fetchone()
        event = connection.execute(
            "SELECT * FROM event WHERE event_type=?", (TERMINAL_EVENT,)
        ).fetchone()
        request_event = int(
            connection.execute(
                "SELECT event_sequence FROM consultation_request WHERE request_id=?",
                (first.request_id,),
            ).fetchone()[0]
        )
        dispatch_event = int(
            connection.execute(
                "SELECT event_sequence FROM consultation_dispatch WHERE dispatch_id=?",
                (first.dispatch_id,),
            ).fetchone()[0]
        )
        assert terminal is not None and completion is not None and event is not None
        assert int(terminal["event_sequence"]) == first.event_sequence
        assert terminal["reason_code"] == "fixture_output_invalid"
        assert terminal["rejected_package_digest"] == digest
        assert int(terminal["rejected_package_size_bytes"]) == len(raw)
        assert completion["terminal_id"] == first.terminal_id
        assert completion["response_id"] is None
        payload = json.loads(event["payload_json"])
        assert set(payload) == {"completion", "terminal"}
        assert payload["completion"] == {
            "completion_id": first.completion_id,
            "dispatch_id": first.dispatch_id,
            "measured_package_bytes": len(raw),
            "terminal_id": first.terminal_id,
        }
        assert payload["terminal"] == {
            "authority": {
                "source": TERMINAL_SOURCE,
                "writer_category": "administration",
            },
            "dispatch_id": first.dispatch_id,
            "event_sequence": first.event_sequence,
            "lineage_generation": 0,
            "organism_id": paths.organism_id,
            "parent_event_sequences": sorted([request_event, dispatch_event]),
            "protocol_version": 1,
            "reason_code": "fixture_output_invalid",
            "rejected_package_digest": digest,
            "rejected_package_size_bytes": len(raw),
            "request_id": first.request_id,
            "terminal_id": first.terminal_id,
            "terminal_schema": "sudachi.consultation.dispatch_terminal/v1",
        }
        assert event["source"] == TERMINAL_SOURCE
    finally:
        connection.close()

    no_clock = FakeClock([])
    repeated = terminalize_fixture_dispatch(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        reason_code="fixture_output_invalid",
        raw_package_bytes=bytes(raw),
        clock=no_clock,
    )
    assert repeated.created is False
    assert repeated.terminal_id == first.terminal_id
    assert no_clock.read_count == 0
    with pytest.raises(TerminalizationRejectedError, match="conflicting"):
        terminalize_fixture_dispatch(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            reason_code="dispatch_interrupted",
            raw_package_bytes=None,
            clock=FakeClock([]),
        )


@pytest.mark.parametrize(
    "fault",
    ["after_event", "after_terminal", "after_completion", "before_commit"],
)
def test_terminal_faults_roll_back_whole_branch(tmp_path: Path, fault: str) -> None:
    root, paths, _wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id=f"terminal-fault-{fault}",
        case_id="malformed-response",
    )
    with pytest.raises(RuntimeError, match="protected terminal fault"):
        terminalize_fixture_dispatch(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            reason_code="fixture_output_invalid",
            raw_package_bytes=dispatched.fixture_output,
            clock=FakeClock.fixed(
                wall_time_utc_us=2_206_000_000_000_000,
                monotonic_ns=160_000_000,
            ),
            protected_test_fault=fault,
        )
    counts = _counts(paths)
    assert counts["consultation_dispatch_terminal"] == 0
    assert counts["consultation_cost_completion"] == 0
    assert counts["terminal_event"] == 0


def test_interrupted_reconciliation_records_zero_byte_terminal_without_fixture(
    tmp_path: Path,
) -> None:
    root, paths, _wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id="terminal-interrupted",
        case_id="crash-after-admission",
    )
    result = reconcile_interrupted_dispatch(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_207_000_000_000_000,
            monotonic_ns=170_000_000,
        ),
    )
    assert result.reason_code == "dispatch_interrupted"
    assert result.rejected_package_digest is None
    assert result.rejected_package_size_bytes is None
    assert result.measured_package_bytes == 0
    counts = _counts(paths)
    assert counts["consultation_dispatch_terminal"] == 1
    assert counts["consultation_cost_completion"] == 1
    assert counts["terminal_event"] == 1
    assert counts["consultation_response"] == 0


def test_expired_before_ingress_requires_lifecycle_crossing_and_raw_bytes(
    tmp_path: Path,
) -> None:
    root, paths, wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id="terminal-expired",
    )
    for index in range(3):
        connection = connect_database(paths.database)
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("UPDATE inventory SET water_units=1 WHERE singleton_id=1")
            connection.execute("UPDATE garden_plot SET moisture=0 WHERE plot_id='bed-a'")
            connection.commit()
        finally:
            connection.close()
        enqueue_garden_tick(
            paths,
            f"expiry-action-{index}",
            clock=FakeClock([ClockReading(2_210_000_000_000_000 + index, 200_000_000 + index)]),
        )
        perform_garden_wake(
            root,
            paths.organism_id,
            seed=50 + index,
            clock=_wake_clock(2_211_000_000_000_000 + index),
        )
    assert read_status(paths).lifecycle_number > wake.consultation_request.expiry_lifecycle_number

    with pytest.raises(IngressRejectedError, match="expired"):
        ingress_external_package(
            root,
            paths.organism_id,
            dispatch_id=dispatched.admission.dispatch_id,
            raw_package_bytes=dispatched.fixture_output,
            clock=FakeClock([]),
        )
    result = terminalize_fixture_dispatch(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        reason_code="expired_before_ingress",
        raw_package_bytes=dispatched.fixture_output,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_212_000_000_000_000,
            monotonic_ns=210_000_000,
        ),
    )
    assert result.reason_code == "expired_before_ingress"
    assert result.rejected_package_size_bytes == len(dispatched.fixture_output)
