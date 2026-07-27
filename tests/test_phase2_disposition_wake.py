from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import pytest

from sudachi_life.checkpoint_repair import repair_pending_checkpoint_registration
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import CheckpointError
from sudachi_life.phase2_disposition import (
    DISPOSITION_SOURCE,
    current_state_digest,
    disposition_id_from_identity,
    finalize_disposition,
    validate_disposition_envelope,
)
from sudachi_life.phase2_disposition_runtime import (
    DispositionNoEligibleProposalError,
    perform_disposition_wake,
)
from sudachi_life.phase2_ingress_runtime import ingress_external_package
from sudachi_life.phase2_protocol import canonical_json_bytes
from sudachi_life.runtime_storage import active_database_allocated_bytes
from sudachi_life.storage import connect_database, read_status
from sudachi_life.wake import WakeBusyError

from test_phase2_dispatch_admission_matrix import _advance_with_successful_water_wake
from test_phase2_ingress_terminalization import _fixture_dispatch


DISPOSITION_EVENT = "consultation_disposition_created"
LEDGER_EVENT = "consultation_disposition_budget_ledger"
DIGEST_DOMAIN = b"sudachi.consultation/v1\n"


def _clock(base: int) -> FakeClock:
    return FakeClock(
        [
            ClockReading(base, 100_000_000),
            ClockReading(base + 1, 110_000_000),
            ClockReading(base + 2, 120_000_000),
        ]
    )


def _ingressed(tmp_path: Path, *, organism_id: str, case_id: str):
    root, paths, wake, dispatched = _fixture_dispatch(
        tmp_path,
        organism_id=organism_id,
        case_id=case_id,
    )
    ingress = ingress_external_package(
        root,
        organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        raw_package_bytes=dispatched.fixture_output,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_400_000_000_000_000,
            monotonic_ns=90_000_000,
        ),
    )
    assert ingress.proposal_id is not None
    return root, paths, wake, dispatched, ingress


def _make_water_applicable(paths) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE inventory SET water_units=1 WHERE singleton_id=1")
        connection.execute("UPDATE garden_plot SET moisture=0 WHERE plot_id='bed-a'")
        connection.commit()
    finally:
        connection.close()


def _garden_snapshot(paths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "environment": [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM environment_state ORDER BY singleton_id"
                ).fetchall()
            ],
            "inventory": [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM inventory ORDER BY singleton_id"
                ).fetchall()
            ],
            "plots": [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM garden_plot ORDER BY plot_id"
                ).fetchall()
            ],
            "inbox": [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM inbox_event ORDER BY inbox_id"
                ).fetchall()
            ],
        }
    finally:
        connection.close()


def _request_expiry(paths, request_id: str) -> int:
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT expiry_lifecycle_number FROM consultation_request WHERE request_id=?",
            (request_id,),
        ).fetchone()
        assert row is not None
        return int(row["expiry_lifecycle_number"])
    finally:
        connection.close()


def _synthetic_state() -> dict[str, object]:
    return {
        "budget_config_version": "phase1-v1",
        "configuration_version": "phase2-fixture-v1",
        "consecutive_failures": 2,
        "considering_lifecycle_number": 3,
        "current_state_schema": "sudachi.consultation.current_state/v1",
        "garden_observation": {
            "actions": [
                {
                    "action_id": "water_plot",
                    "applicable_targets": ["bed-a"],
                    "preconditions": [
                        "plot_exists",
                        "living_stage",
                        "moisture_is_zero",
                        "water_unit_available",
                        "action_and_mutation_budget_available",
                    ],
                    "version": 1,
                },
                {
                    "action_id": "harvest_plot",
                    "applicable_targets": [],
                    "preconditions": [
                        "plot_exists",
                        "stage_is_mature",
                        "fruit_is_positive",
                        "action_and_mutation_budget_available",
                    ],
                    "version": 1,
                },
            ],
            "environment_step": 0,
            "environment_version": "seed-garden-v1",
            "inventory": {"harvested_fruit": 0, "water_units": 1},
            "objective_complete": False,
            "plots": [
                {
                    "fruit": 0,
                    "moisture": 0,
                    "plot_id": "bed-a",
                    "stage": "sprout",
                }
            ],
        },
        "latest_stable_checkpoint_id": "cp-g000000-e000000000010-deadbeef",
        "latest_stable_event_sequence": 10,
        "lineage_generation": 0,
        "organism_id": "golden-disposition",
        "organism_status": "sleeping",
        "proposal_reference": {
            "content_digest": "d" * 64,
            "proposal_id": "consultation-proposal:" + "e" * 64,
            "proposal_type": "action_candidate",
            "required_evaluator_ids": [
                "action-schema-v1",
                "current-state-v1",
                "permission-v1",
            ],
        },
        "protocol_version": 1,
        "request_reference": {
            "expiry_lifecycle_number": 3,
            "permission_ids": ["garden.action.execute:water_plot"],
            "request_id": "consultation-request:" + "a" * 64,
        },
    }


def test_adr0013_digest_identity_and_final_envelope_are_exact() -> None:
    state = _synthetic_state()
    state_digest = hashlib.sha256(
        DIGEST_DOMAIN
        + b"current-state-reference\n"
        + canonical_json_bytes(state)
    ).hexdigest()
    assert current_state_digest(state) == state_digest
    identity = {
        "current_state_digest": state_digest,
        "dispatch_id": "consultation-dispatch:" + "b" * 64,
        "disposition": "accepted",
        "disposition_lifecycle_number": 3,
        "disposition_schema": "sudachi.consultation.disposition/v1",
        "evaluator_versions": [
            "action-schema-v1",
            "current-state-v1",
            "permission-v1",
        ],
        "lineage_generation": 0,
        "organism_id": "golden-disposition",
        "proposal_id": "consultation-proposal:" + "e" * 64,
        "protocol_version": 1,
        "reason_code": "required_evaluators_passed",
        "request_id": "consultation-request:" + "a" * 64,
        "response_id": "consultation-response:" + "c" * 64,
    }
    expected_id = "consultation-disposition:" + hashlib.sha256(
        DIGEST_DOMAIN + b"disposition-id\n" + canonical_json_bytes(identity)
    ).hexdigest()
    assert disposition_id_from_identity(
        identity,
        current_state_reference=state,
    ) == expected_id
    envelope = finalize_disposition(
        identity,
        current_state_reference=state,
        event_sequence=12,
        parent_event_sequences=[7, 10, 11],
    )
    assert envelope == {
        **identity,
        "authority": {
            "source": "organism:consultation.disposition",
            "writer_category": "organism",
        },
        "current_state_reference": state,
        "disposition_id": expected_id,
        "event_sequence": 12,
        "parent_event_sequences": [7, 10, 11],
    }
    assert validate_disposition_envelope(envelope) == envelope
    with pytest.raises(Exception, match="field set"):
        validate_disposition_envelope({**envelope, "command": "water"})
    with pytest.raises(Exception, match="reason|combination"):
        disposition_id_from_identity(
            {**identity, "reason_code": "await_state_change"},
            current_state_reference=state,
        )


def test_accepted_action_candidate_writes_exact_four_event_checkpointed_wake(
    tmp_path: Path,
) -> None:
    root, paths, _wake, _dispatch, ingress = _ingressed(
        tmp_path,
        organism_id="disposition-accepted",
        case_id="valid-action-candidate",
    )
    _make_water_applicable(paths)
    before_status = read_status(paths)
    before_garden = _garden_snapshot(paths)
    connection = connect_database(paths.database, read_only=True)
    try:
        before_failures = int(
            connection.execute(
                "SELECT consecutive_failures FROM organism WHERE singleton_id=1"
            ).fetchone()[0]
        )
        ingress_sequence = int(
            connection.execute(
                "SELECT event_sequence FROM consultation_response WHERE response_id=?",
                (ingress.response_id,),
            ).fetchone()[0]
        )
    finally:
        connection.close()

    clock = _clock(2_401_000_000_000_000)
    result = perform_disposition_wake(root, paths.organism_id, clock=clock)
    assert clock.read_count == 3
    assert (result.disposition, result.reason_code) == (
        "accepted",
        "required_evaluators_passed",
    )
    assert result.lifecycle_number == before_status.lifecycle_number + 1
    assert result.status == "sleeping"

    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute("SELECT * FROM consultation_disposition").fetchone()
        assert row is not None
        assert row["disposition_id"] == result.disposition_id
        assert row["proposal_id"] == ingress.proposal_id
        assert int(row["lifecycle_number"]) == result.lifecycle_number
        assert int(row["event_sequence"]) == result.event_sequence
        assert json.loads(row["envelope_json"]) == result.envelope

        events = connection.execute(
            "SELECT * FROM event WHERE source=? AND lifecycle_number=? "
            "ORDER BY event_sequence",
            (DISPOSITION_SOURCE, result.lifecycle_number),
        ).fetchall()
        assert [event["event_type"] for event in events] == [
            "wake_accepted",
            DISPOSITION_EVENT,
            LEDGER_EVENT,
            "checkpoint_pending",
        ]
        assert json.loads(events[0]["payload_json"]) == {
            "work_class": "consultation_disposition"
        }
        payload = json.loads(events[1]["payload_json"])
        assert frozenset(payload) == frozenset({"disposition", "outcome"})
        assert payload["disposition"] == result.envelope
        assert payload["outcome"] == {
            "disposition": "accepted",
            "disposition_id": result.disposition_id,
            "input_consumed": False,
            "proposal_id": ingress.proposal_id,
            "reason_code": "required_evaluators_passed",
        }
        assert json.loads(events[2]["payload_json"]) == {
            "canonical_records_limit": 12,
            "canonical_records_used": 4,
            "configuration_version": "phase2-fixture-v1",
            "phase1_budget_config_version": "phase1-v1",
            "semantic_steps_limit": 10,
            "semantic_steps_used": 8,
        }
        assert json.loads(events[3]["payload_json"]) == {
            "final_status": "sleeping",
            "lifecycle_number": result.lifecycle_number,
            "reason": "committed_disposition_wake",
        }
        assert result.envelope["parent_event_sequences"] == sorted(
            [
                ingress_sequence,
                before_status.latest_stable_event_sequence,
                int(events[0]["event_sequence"]),
            ]
        )
        assert int(events[1]["event_sequence"]) == result.event_sequence
        assert int(events[3]["event_sequence"]) == result.checkpoint.event_sequence
        organism = connection.execute(
            "SELECT consecutive_failures, checkpoint_pending, status, "
            "latest_stable_event_sequence FROM organism WHERE singleton_id=1"
        ).fetchone()
        assert int(organism["consecutive_failures"]) == before_failures
        assert int(organism["checkpoint_pending"]) == 0
        assert organism["status"] == "sleeping"
        assert int(organism["latest_stable_event_sequence"]) == int(
            events[3]["event_sequence"]
        )
    finally:
        connection.close()
    assert _garden_snapshot(paths) == before_garden


@pytest.mark.parametrize(
    ("case_id", "applicable", "expected"),
    [
        (
            "valid-action-candidate",
            False,
            ("rejected", "action_not_applicable_current_state"),
        ),
        (
            "valid-abstain",
            False,
            ("accepted", "no_supported_action_confirmed"),
        ),
        (
            "valid-abstain",
            True,
            ("clarification_requested", "proposal_contradicts_current_state"),
        ),
        ("valid-defer", False, ("deferred", "await_state_change")),
    ],
)
def test_nonexpired_mapping(
    tmp_path: Path,
    case_id: str,
    applicable: bool,
    expected: tuple[str, str],
) -> None:
    root, paths, _wake, _dispatch, _ingress = _ingressed(
        tmp_path,
        organism_id=f"mapping-{case_id}-{int(applicable)}",
        case_id=case_id,
    )
    if applicable:
        _make_water_applicable(paths)
    result = perform_disposition_wake(
        root,
        paths.organism_id,
        clock=_clock(2_410_000_000_000_000),
    )
    assert (result.disposition, result.reason_code) == expected


def test_expiry_uses_considering_lifecycle_not_wall_time(tmp_path: Path) -> None:
    root, paths, wake, _dispatch, _ingress = _ingressed(
        tmp_path,
        organism_id="disposition-expired",
        case_id="valid-defer",
    )
    assert wake.consultation_request is not None
    assert wake.consultation_request.request_id is not None
    expiry = _request_expiry(paths, wake.consultation_request.request_id)
    while read_status(paths).lifecycle_number < expiry:
        _advance_with_successful_water_wake(
            root,
            paths,
            ordinal=read_status(paths).lifecycle_number + 1,
        )
    assert read_status(paths).lifecycle_number == expiry
    result = perform_disposition_wake(
        root,
        paths.organism_id,
        clock=FakeClock(
            [
                ClockReading(1, 200_000_000),
                ClockReading(2, 210_000_000),
                ClockReading(3, 220_000_000),
            ]
        ),
    )
    assert result.lifecycle_number == expiry + 1
    assert (result.disposition, result.reason_code) == ("rejected", "expired")


@pytest.mark.parametrize(
    "fault",
    [
        "after_wake_accepted",
        "after_disposition_event",
        "after_disposition_row",
        "after_budget_ledger",
        "after_checkpoint_pending",
        "before_commit",
    ],
)
def test_precommit_fault_rolls_back_and_restores_selection(
    tmp_path: Path,
    fault: str,
) -> None:
    root, paths, _wake, _dispatch, ingress = _ingressed(
        tmp_path,
        organism_id=f"disposition-fault-{fault}",
        case_id="valid-defer",
    )
    before = read_status(paths)
    before_garden = _garden_snapshot(paths)
    with pytest.raises(RuntimeError, match="protected disposition fault"):
        perform_disposition_wake(
            root,
            paths.organism_id,
            clock=FakeClock.fixed(
                wall_time_utc_us=2_420_000_000_000_000,
                monotonic_ns=300_000_000,
            ),
            protected_test_fault=fault,
        )
    after = read_status(paths)
    assert (after.lifecycle_number, after.status) == (
        before.lifecycle_number,
        before.status,
    )
    assert after.latest_stable_event_sequence == before.latest_stable_event_sequence
    assert _garden_snapshot(paths) == before_garden
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM consultation_disposition"
            ).fetchone()[0]
        ) == 0
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE source=?",
                (DISPOSITION_SOURCE,),
            ).fetchone()[0]
        ) == 0
    finally:
        connection.close()
    result = perform_disposition_wake(
        root,
        paths.organism_id,
        clock=_clock(2_421_000_000_000_000),
    )
    assert result.proposal_id == ingress.proposal_id


def test_checkpoint_deadline_leaves_one_repairable_final_disposition(
    tmp_path: Path,
) -> None:
    root, paths, _wake, _dispatch, ingress = _ingressed(
        tmp_path,
        organism_id="disposition-checkpoint-repair",
        case_id="valid-defer",
    )
    with pytest.raises(CheckpointError, match="deadline"):
        perform_disposition_wake(
            root,
            paths.organism_id,
            clock=FakeClock(
                [
                    ClockReading(2_430_000_000_000_000, 10_000_000),
                    ClockReading(2_430_000_000_000_001, 20_000_000),
                    ClockReading(2_430_000_000_000_002, 5_020_000_001),
                ]
            ),
        )
    assert read_status(paths).status == "checkpoint_pending"
    connection = connect_database(paths.database, read_only=True)
    try:
        rows = connection.execute(
            "SELECT proposal_id FROM consultation_disposition"
        ).fetchall()
        assert [row["proposal_id"] for row in rows] == [ingress.proposal_id]
    finally:
        connection.close()
    repaired = repair_pending_checkpoint_registration(
        root,
        paths.organism_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_430_000_000_000_100,
            monotonic_ns=6_000_000_000,
        ),
    )
    assert repaired.status == "sleeping"
    with pytest.raises(DispositionNoEligibleProposalError, match="eligible"):
        perform_disposition_wake(root, paths.organism_id, clock=FakeClock([]))


def test_busy_and_final_attempts_read_no_clock_and_queue_nothing(tmp_path: Path) -> None:
    root, paths, _wake, _dispatch, _ingress = _ingressed(
        tmp_path,
        organism_id="disposition-busy-final",
        case_id="valid-defer",
    )
    blocker = connect_database(paths.database)
    try:
        blocker.execute("BEGIN IMMEDIATE")
        no_clock = FakeClock([])
        with pytest.raises(WakeBusyError, match="busy"):
            perform_disposition_wake(root, paths.organism_id, clock=no_clock)
        assert no_clock.read_count == 0
    finally:
        blocker.rollback()
        blocker.close()
    perform_disposition_wake(
        root,
        paths.organism_id,
        clock=_clock(2_440_000_000_000_000),
    )
    no_clock = FakeClock([])
    with pytest.raises(DispositionNoEligibleProposalError, match="eligible"):
        perform_disposition_wake(root, paths.organism_id, clock=no_clock)
    assert no_clock.read_count == 0
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM consultation_disposition"
            ).fetchone()[0]
        ) == 1
    finally:
        connection.close()


def test_real_active_reserve_refusal_is_nonmutating(tmp_path: Path) -> None:
    root, paths, _wake, _dispatch, _ingress = _ingressed(
        tmp_path,
        organism_id="disposition-real-reserve",
        case_id="valid-defer",
    )
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("CREATE TABLE disposition_padding (value BLOB NOT NULL)")
        while active_database_allocated_bytes(connection) <= 7 * 1024 * 1024:
            connection.execute(
                "INSERT INTO disposition_padding(value) VALUES (zeroblob(65536))"
            )
        connection.execute("DROP TABLE disposition_padding")
        connection.commit()
    finally:
        connection.close()
    with pytest.raises(Exception, match="reserve"):
        perform_disposition_wake(root, paths.organism_id, clock=FakeClock([]))
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM consultation_disposition"
            ).fetchone()[0]
        ) == 0
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE source=?",
                (DISPOSITION_SOURCE,),
            ).fetchone()[0]
        ) == 0
    finally:
        connection.close()


def test_runtime_has_no_fixture_action_network_subprocess_or_adaptive_state_surface() -> None:
    module = inspect.getmodule(perform_disposition_wake)
    assert module is not None
    source = inspect.getsource(module)
    for token in (
        "phase2_fixture",
        "perform_fixture_dispatch",
        "run_deterministic_fixture",
        "execute_garden_action",
        "import socket",
        "import subprocess",
        "import requests",
        "urllib",
        "open(",
        "memory",
        "skill",
    ):
        assert token not in source
