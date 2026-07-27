from __future__ import annotations

from copy import deepcopy
import hashlib

import pytest

from sudachi_life.phase2_proposal import (
    ProposalValidationError,
    finalize_proposal,
    proposal_content_digest,
    proposal_id_from_identity,
    validate_proposal_envelope,
    validate_proposal_identity,
)
from sudachi_life.phase2_protocol import (
    canonical_json_bytes,
    request_id_from_identity,
)


DOMAIN = b"sudachi.consultation/v1\nproposal-content\n"
DISPATCH_ID = "consultation-dispatch:" + "3" * 64
RESPONSE_ID = "consultation-response:" + "4" * 64


def _budget_snapshot() -> dict[str, object]:
    limits = {
        "action_attempts": 1,
        "caregiver_consultations": 0,
        "environment_mutations": 1,
        "external_mutable_writes": 0,
        "input_events": 1,
        "network_calls": 0,
        "observations": 1,
        "subprocess_calls": 0,
    }
    consumed = {name: 0 for name in limits}
    consumed["input_events"] = 1
    consumed["observations"] = 1
    return {
        "canonical_records_limit": 16,
        "canonical_records_used": 10,
        "config_version": "phase1-v1",
        "consumed": consumed,
        "elapsed_monotonic_ns": 30_000_000,
        "lifecycle_wall_time_limit_ns": 5_000_000_000,
        "limits": limits,
        "remaining": {name: limits[name] - consumed[name] for name in limits},
        "semantic_steps_limit": 16,
        "semantic_steps_used": 12,
    }


def _request() -> dict[str, object]:
    identity = {
        "allowed_action_ids": ["harvest_plot", "water_plot"],
        "budget_config_version": "phase1-v1",
        "configuration_version": "phase2-fixture-v1",
        "expiry_lifecycle_number": 3,
        "lineage_generation": 0,
        "lifecycle_number": 1,
        "objective_digest": "1" * 64,
        "observation_digest": "2" * 64,
        "organism_id": "proposal-schema",
        "permission_ids": [
            "garden.action.execute:harvest_plot",
            "garden.action.execute:water_plot",
        ],
        "policy_version": "phase1-fixed-policy-v1",
        "protocol_version": 1,
        "reason_code": "no_applicable_action",
        "request_ordinal": 1,
        "request_schema": "sudachi.consultation.request/v1",
        "requested_proposal_types": ["abstain", "action_candidate", "defer"],
    }
    return {
        "allowed_action_ids": identity["allowed_action_ids"],
        "authority": {
            "source": "organism:consultation.request",
            "writer_category": "organism",
        },
        "budget_config_version": "phase1-v1",
        "budget_snapshot": _budget_snapshot(),
        "configuration_version": "phase2-fixture-v1",
        "event_sequence": 12,
        "expiry_lifecycle_number": 3,
        "lineage_generation": 0,
        "lifecycle_number": 1,
        "objective_reference": {
            "digest": "1" * 64,
            "objective_id": "seed-garden.harvest-fruit/v1",
        },
        "observation_reference": {"digest": "2" * 64, "event_sequence": 5},
        "organism_id": "proposal-schema",
        "parent_event_sequences": [3, 4, 5, 6, 7, 8, 9, 10, 11],
        "permission_ids": identity["permission_ids"],
        "policy_version": "phase1-fixed-policy-v1",
        "protocol_version": 1,
        "reason_code": "no_applicable_action",
        "request_id": request_id_from_identity(identity),
        "request_ordinal": 1,
        "request_schema": "sudachi.consultation.request/v1",
        "requested_proposal_types": ["abstain", "action_candidate", "defer"],
    }


def _common(proposal_type: str) -> dict[str, object]:
    return {
        "confidence_basis": {
            "basis_type": "deterministic_fixture_case",
            "fixture_case_id": f"valid-{proposal_type.replace('_', '-')}",
        },
        "dispatch_id": DISPATCH_ID,
        "expiry_lifecycle_number": 3,
        "proposal_ordinal": 1,
        "proposal_schema": "sudachi.consultation.proposal/v1",
        "proposal_type": proposal_type,
        "protocol_version": 1,
        "request_id": _request()["request_id"],
    }


def _action_identity() -> dict[str, object]:
    return {
        **_common("action_candidate"),
        "proposed_value": {"parameters": {"plot_id": "bed-a"}},
        "rationale_code": "existing_action_applicable",
        "required_evaluator_ids": [
            "action-schema-v1",
            "current-state-v1",
            "permission-v1",
        ],
        "subject_reference": {"action_id": "water_plot"},
    }


def _abstain_identity() -> dict[str, object]:
    return {
        **_common("abstain"),
        "proposed_value": {"reason_code": "no_supported_action"},
        "rationale_code": "no_supported_action",
        "required_evaluator_ids": ["abstain-policy-v1", "current-state-v1"],
        "subject_reference": deepcopy(_request()["objective_reference"]),
    }


def _defer_identity() -> dict[str, object]:
    return {
        **_common("defer"),
        "proposed_value": {"reason_code": "await_state_change"},
        "rationale_code": "await_state_change",
        "required_evaluator_ids": ["current-state-v1", "defer-policy-v1"],
        "subject_reference": deepcopy(_request()["objective_reference"]),
    }


@pytest.mark.parametrize(
    "identity",
    [_action_identity(), _abstain_identity(), _defer_identity()],
)
def test_exact_proposal_identity_digest_id_and_final_envelope(
    identity: dict[str, object],
) -> None:
    request = _request()
    case_id = identity["confidence_basis"]["fixture_case_id"]
    validated = validate_proposal_identity(
        identity,
        request_envelope=request,
        fixture_case_id=case_id,
    )
    expected_digest = hashlib.sha256(DOMAIN + canonical_json_bytes(identity)).hexdigest()
    assert proposal_content_digest(
        identity,
        request_envelope=request,
        fixture_case_id=case_id,
    ) == expected_digest
    assert proposal_id_from_identity(
        identity,
        request_envelope=request,
        fixture_case_id=case_id,
    ) == f"consultation-proposal:{expected_digest}"

    final = finalize_proposal(
        validated,
        response_id=RESPONSE_ID,
        request_envelope=request,
        fixture_case_id=case_id,
    )
    assert final["proposal_id"] == f"consultation-proposal:{expected_digest}"
    assert final["response_id"] == RESPONSE_ID
    assert validate_proposal_envelope(
        final,
        request_envelope=request,
        fixture_case_id=case_id,
    ) == final


def test_proposal_identity_excludes_response_id_without_changing_content_id() -> None:
    identity = _action_identity()
    request = _request()
    case_id = "valid-action-candidate"
    first = finalize_proposal(
        identity,
        response_id=RESPONSE_ID,
        request_envelope=request,
        fixture_case_id=case_id,
    )
    second = finalize_proposal(
        identity,
        response_id="consultation-response:" + "5" * 64,
        request_envelope=request,
        fixture_case_id=case_id,
    )
    assert first["proposal_id"] == second["proposal_id"]
    assert proposal_content_digest(
        identity,
        request_envelope=request,
        fixture_case_id=case_id,
    ) == first["proposal_id"].split(":", 1)[1]

    invalid_identity = {**identity, "response_id": RESPONSE_ID}
    with pytest.raises(ProposalValidationError, match="field set"):
        validate_proposal_identity(
            invalid_identity,
            request_envelope=request,
            fixture_case_id=case_id,
        )


@pytest.mark.parametrize(
    "base,mutation,match",
    [
        (_action_identity, lambda value: value.update({"free_text": "do it"}), "field set"),
        (
            _action_identity,
            lambda value: value["subject_reference"].update({"action_id": "unknown"}),
            "allowed action",
        ),
        (
            _action_identity,
            lambda value: value["proposed_value"]["parameters"].update(
                {"shell": "rm -rf /"}
            ),
            "parameters",
        ),
        (
            _action_identity,
            lambda value: value.update({"rationale_code": "because I said so"}),
            "rationale",
        ),
        (
            _action_identity,
            lambda value: value.update(
                {"required_evaluator_ids": ["current-state-v1"]}
            ),
            "evaluator",
        ),
        (
            _abstain_identity,
            lambda value: value["proposed_value"].update({"command": "water"}),
            "field set",
        ),
        (
            _defer_identity,
            lambda value: value["proposed_value"].update({"retry_at": 99}),
            "field set",
        ),
        (
            _defer_identity,
            lambda value: value.update({"expiry_lifecycle_number": 4}),
            "expiry",
        ),
        (
            _defer_identity,
            lambda value: value["confidence_basis"].update(
                {"fixture_case_id": "different-case"}
            ),
            "fixture case",
        ),
        (
            _defer_identity,
            lambda value: value.update({"proposal_type": "question"}),
            "proposal type",
        ),
    ],
)
def test_proposal_rejects_extra_free_text_commands_linkage_and_type_errors(
    base,
    mutation,
    match: str,
) -> None:
    identity = base()
    case_id = identity["confidence_basis"]["fixture_case_id"]
    mutation(identity)
    with pytest.raises(ProposalValidationError, match=match):
        validate_proposal_identity(
            identity,
            request_envelope=_request(),
            fixture_case_id=case_id,
        )
