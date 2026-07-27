from __future__ import annotations

from copy import deepcopy
import hashlib

import pytest

from sudachi_life.phase2_dispatch import (
    DispatchValidationError,
    dispatch_id_from_identity,
    finalize_dispatch,
    validate_dispatch_envelope,
    validate_dispatch_identity,
)
from sudachi_life.phase2_proposal import (
    finalize_proposal,
    proposal_content_digest,
    proposal_id_from_identity,
)
from sudachi_life.phase2_protocol import canonical_json_bytes, request_id_from_identity
from sudachi_life.phase2_response import (
    ResponseValidationError,
    external_package_digest,
    finalize_external_package,
    response_id_from_identity,
    validate_external_package,
    validate_external_provenance,
    validate_response_envelope,
    validate_response_identity,
)


DISPATCH_DOMAIN = b"sudachi.consultation/v1\ndispatch-id\n"
PROPOSAL_DOMAIN = b"sudachi.consultation/v1\nproposal-content\n"
RESPONSE_DOMAIN = b"sudachi.consultation/v1\nresponse-id\n"
PACKAGE_DOMAIN = b"sudachi.consultation/v1\nexternal-package\n"


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
        "organism_id": "dispatch-package",
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
        "organism_id": "dispatch-package",
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


def _dispatch_identity(case_id: str = "valid-action-candidate") -> dict[str, object]:
    request = _request()
    return {
        "adapter_version": "deterministic-fixture-v1",
        "configuration_version": "phase2-fixture-v1",
        "dispatch_ordinal": 1,
        "dispatch_schema": "sudachi.consultation.dispatch/v1",
        "fixture_case_id": case_id,
        "lineage_generation": 0,
        "organism_id": "dispatch-package",
        "protocol_version": 1,
        "request_id": request["request_id"],
        "work_class": "fixture-constant-v1",
    }


def _dispatch(case_id: str = "valid-action-candidate") -> dict[str, object]:
    return finalize_dispatch(
        _dispatch_identity(case_id),
        event_sequence=13,
        request_envelope=_request(),
    )


def _proposal_identity(dispatch_id: str, case_id: str) -> dict[str, object]:
    request = _request()
    return {
        "confidence_basis": {
            "basis_type": "deterministic_fixture_case",
            "fixture_case_id": case_id,
        },
        "dispatch_id": dispatch_id,
        "expiry_lifecycle_number": 3,
        "proposal_ordinal": 1,
        "proposal_schema": "sudachi.consultation.proposal/v1",
        "proposal_type": "action_candidate",
        "protocol_version": 1,
        "proposed_value": {"parameters": {"plot_id": "bed-a"}},
        "rationale_code": "existing_action_applicable",
        "request_id": request["request_id"],
        "required_evaluator_ids": [
            "action-schema-v1",
            "current-state-v1",
            "permission-v1",
        ],
        "subject_reference": {"action_id": "water_plot"},
    }


def _provenance(case_id: str) -> dict[str, object]:
    return {
        "fixture_case_id": case_id,
        "provenance_schema": "sudachi.consultation.provenance/v1",
        "source_type": "deterministic-fixture",
    }


def _response_identity(
    dispatch: dict[str, object],
    proposal_identity: dict[str, object] | None,
) -> dict[str, object]:
    request = _request()
    if proposal_identity is None:
        proposal_ids: list[str] = []
        content_digests: list[str] = []
        status = "unavailable"
    else:
        case_id = str(dispatch["fixture_case_id"])
        proposal_ids = [
            proposal_id_from_identity(
                proposal_identity,
                request_envelope=request,
                fixture_case_id=case_id,
            )
        ]
        content_digests = [
            proposal_content_digest(
                proposal_identity,
                request_envelope=request,
                fixture_case_id=case_id,
            )
        ]
        status = "proposals_returned"
    return {
        "adapter_instance_id": "deterministic-fixture-instance-v1",
        "adapter_type": "deterministic-fixture",
        "adapter_version": "deterministic-fixture-v1",
        "dispatch_id": dispatch["dispatch_id"],
        "external_provenance": _provenance(str(dispatch["fixture_case_id"])),
        "proposal_content_digests": content_digests,
        "proposal_ids": proposal_ids,
        "protocol_version": 1,
        "request_id": request["request_id"],
        "response_schema": "sudachi.consultation.response/v1",
        "status": status,
    }


def test_dispatch_identity_id_and_final_envelope_are_exact() -> None:
    request = _request()
    identity = _dispatch_identity()
    expected_digest = hashlib.sha256(
        DISPATCH_DOMAIN + canonical_json_bytes(identity)
    ).hexdigest()
    expected_id = f"consultation-dispatch:{expected_digest}"

    assert validate_dispatch_identity(identity, request_envelope=request) == identity
    assert dispatch_id_from_identity(identity, request_envelope=request) == expected_id

    envelope = finalize_dispatch(identity, event_sequence=13, request_envelope=request)
    assert envelope == {
        **identity,
        "authority": {
            "source": "administration:consultation.dispatch",
            "writer_category": "administration",
        },
        "dispatch_id": expected_id,
        "event_sequence": 13,
    }
    assert validate_dispatch_envelope(envelope, request_envelope=request) == envelope


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda value: value.pop("configuration_version"), "field set"),
        (lambda value: value.update({"wall_time_utc_us": 1}), "field set"),
        (
            lambda value: value.update({"configuration_version": "phase2-zero-caregiver-v1"}),
            "configuration",
        ),
        (lambda value: value.update({"request_id": "consultation-request:" + "0" * 64}), "request"),
        (lambda value: value.update({"organism_id": "other"}), "organism"),
        (lambda value: value.update({"fixture_case_id": "unknown-case"}), "fixture case"),
        (lambda value: value.update({"dispatch_ordinal": True}), "ordinal"),
        (lambda value: value.update({"work_class": "other"}), "work class"),
    ],
)
def test_dispatch_rejects_undeclared_fields_and_linkage(
    mutation,
    match: str,
) -> None:
    identity = _dispatch_identity()
    mutation(identity)
    with pytest.raises(DispatchValidationError, match=match):
        validate_dispatch_identity(identity, request_envelope=_request())


def test_proposals_returned_graph_and_package_are_exact_and_reproducible() -> None:
    request = _request()
    dispatch = _dispatch()
    case_id = str(dispatch["fixture_case_id"])
    proposal_identity = _proposal_identity(str(dispatch["dispatch_id"]), case_id)
    response_identity = _response_identity(dispatch, proposal_identity)

    proposal_digest = hashlib.sha256(
        PROPOSAL_DOMAIN + canonical_json_bytes(proposal_identity)
    ).hexdigest()
    assert response_identity["proposal_content_digests"] == [proposal_digest]
    assert response_identity["proposal_ids"] == [f"consultation-proposal:{proposal_digest}"]

    expected_response_digest = hashlib.sha256(
        RESPONSE_DOMAIN + canonical_json_bytes(response_identity)
    ).hexdigest()
    expected_response_id = f"consultation-response:{expected_response_digest}"
    assert response_id_from_identity(
        response_identity,
        request_envelope=request,
        dispatch_envelope=dispatch,
        proposal_identities=[proposal_identity],
    ) == expected_response_id

    package = finalize_external_package(
        response_identity,
        proposal_identities=[proposal_identity],
        request_envelope=request,
        dispatch_envelope=dispatch,
    )
    assert set(package) == {"response", "proposals"}
    assert package["response"]["response_id"] == expected_response_id
    assert len(package["proposals"]) == 1
    assert package["proposals"][0]["proposal_id"] == f"consultation-proposal:{proposal_digest}"
    assert package["proposals"][0]["response_id"] == expected_response_id
    assert validate_external_package(
        package,
        request_envelope=request,
        dispatch_envelope=dispatch,
    ) == package

    expected_package_digest = hashlib.sha256(
        PACKAGE_DOMAIN + canonical_json_bytes(package)
    ).hexdigest()
    assert external_package_digest(
        package,
        request_envelope=request,
        dispatch_envelope=dispatch,
    ) == expected_package_digest

    second = finalize_external_package(
        deepcopy(response_identity),
        proposal_identities=[deepcopy(proposal_identity)],
        request_envelope=deepcopy(request),
        dispatch_envelope=deepcopy(dispatch),
    )
    assert canonical_json_bytes(second) == canonical_json_bytes(package)


def test_unavailable_response_has_exact_empty_cardinality() -> None:
    request = _request()
    dispatch = _dispatch("unavailable")
    identity = _response_identity(dispatch, None)
    assert validate_response_identity(
        identity,
        request_envelope=request,
        dispatch_envelope=dispatch,
        proposal_identities=[],
    ) == identity
    package = finalize_external_package(
        identity,
        proposal_identities=[],
        request_envelope=request,
        dispatch_envelope=dispatch,
    )
    assert package["proposals"] == []
    assert package["response"]["proposal_ids"] == []
    assert package["response"]["proposal_content_digests"] == []
    assert validate_external_package(
        package,
        request_envelope=request,
        dispatch_envelope=dispatch,
    ) == package


@pytest.mark.parametrize(
    "mutation,match",
    [
        (
            lambda identity, package: identity["external_provenance"].update(
                {"writer_category": "administration"}
            ),
            "provenance field set",
        ),
        (lambda identity, package: identity.update({"adapter_type": "model"}), "adapter type"),
        (
            lambda identity, package: identity["external_provenance"].update(
                {"fixture_case_id": "valid-defer"}
            ),
            "fixture case",
        ),
        (lambda identity, package: identity.update({"proposal_ids": []}), "cardinality"),
        (lambda identity, package: identity.update({"status": "unavailable"}), "cardinality"),
        (lambda identity, package: identity.update({"free_text": "trust me"}), "field set"),
        (lambda identity, package: package.update({"authority": {}}), "package field set"),
    ],
)
def test_response_provenance_and_package_reject_spoofing_and_extra_fields(
    mutation,
    match: str,
) -> None:
    request = _request()
    dispatch = _dispatch()
    case_id = str(dispatch["fixture_case_id"])
    proposal_identity = _proposal_identity(str(dispatch["dispatch_id"]), case_id)
    identity = _response_identity(dispatch, proposal_identity)
    package = finalize_external_package(
        identity,
        proposal_identities=[proposal_identity],
        request_envelope=request,
        dispatch_envelope=dispatch,
    )
    changed_identity = deepcopy(identity)
    changed_package = deepcopy(package)
    mutation(changed_identity, changed_package)

    if changed_package != package:
        with pytest.raises(ResponseValidationError, match=match):
            validate_external_package(
                changed_package,
                request_envelope=request,
                dispatch_envelope=dispatch,
            )
    else:
        with pytest.raises(ResponseValidationError, match=match):
            validate_response_identity(
                changed_identity,
                request_envelope=request,
                dispatch_envelope=dispatch,
                proposal_identities=[proposal_identity],
            )


def test_final_response_and_provenance_are_closed_and_bounded() -> None:
    request = _request()
    dispatch = _dispatch()
    case_id = str(dispatch["fixture_case_id"])
    proposal_identity = _proposal_identity(str(dispatch["dispatch_id"]), case_id)
    identity = _response_identity(dispatch, proposal_identity)
    provenance = validate_external_provenance(
        identity["external_provenance"],
        dispatch_envelope=dispatch,
    )
    assert provenance == _provenance(case_id)
    assert len(canonical_json_bytes(provenance)) <= 8 * 1024

    package = finalize_external_package(
        identity,
        proposal_identities=[proposal_identity],
        request_envelope=request,
        dispatch_envelope=dispatch,
    )
    response = package["response"]
    assert validate_response_envelope(
        response,
        request_envelope=request,
        dispatch_envelope=dispatch,
        proposal_envelopes=package["proposals"],
    ) == response
    assert len(canonical_json_bytes(package)) <= 16 * 1024

    forbidden = {
        "authority",
        "budget",
        "checkpoint",
        "command",
        "credential",
        "evaluator_command",
        "execution",
        "human_identity",
        "model_identity",
        "path",
        "permission_command",
        "sql",
        "tool",
        "url",
    }
    assert forbidden.isdisjoint(provenance)
