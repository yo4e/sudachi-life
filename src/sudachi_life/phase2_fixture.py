"""Pure deterministic fixture receiving only a request envelope and declared case ID."""

from __future__ import annotations

from copy import deepcopy
from typing import Final

from .phase2_dispatch import (
    DECLARED_FIXTURE_CASE_IDS,
    DISPATCH_ADAPTER_VERSION,
    DISPATCH_CONFIGURATION_VERSION,
    DISPATCH_SCHEMA,
    DISPATCH_WORK_CLASS,
    finalize_dispatch,
)
from .phase2_proposal import proposal_content_digest, proposal_id_from_identity
from .phase2_protocol import ProtocolValidationError, canonical_json_bytes, validate_request_envelope
from .phase2_response import finalize_external_package


_FIXTURE_OUTPUT_SCHEMA: Final = "sudachi.consultation.fixture_output/v1"


def _dispatch_identity(
    request: dict[str, object],
    fixture_case_id: str,
) -> dict[str, object]:
    return {
        "adapter_version": DISPATCH_ADAPTER_VERSION,
        "configuration_version": DISPATCH_CONFIGURATION_VERSION,
        "dispatch_ordinal": 1,
        "dispatch_schema": DISPATCH_SCHEMA,
        "fixture_case_id": fixture_case_id,
        "lineage_generation": request["lineage_generation"],
        "organism_id": request["organism_id"],
        "protocol_version": 1,
        "request_id": request["request_id"],
        "work_class": DISPATCH_WORK_CLASS,
    }


def _proposal_identity(
    request: dict[str, object],
    dispatch_id: str,
    fixture_case_id: str,
) -> dict[str, object]:
    common: dict[str, object] = {
        "confidence_basis": {
            "basis_type": "deterministic_fixture_case",
            "fixture_case_id": fixture_case_id,
        },
        "dispatch_id": dispatch_id,
        "expiry_lifecycle_number": request["expiry_lifecycle_number"],
        "proposal_ordinal": 1,
        "proposal_schema": "sudachi.consultation.proposal/v1",
        "protocol_version": 1,
        "request_id": request["request_id"],
    }
    if fixture_case_id == "valid-action-candidate":
        allowed = list(request["allowed_action_ids"])
        action_id = "water_plot" if "water_plot" in allowed else str(allowed[0])
        return {
            **common,
            "proposal_type": "action_candidate",
            "proposed_value": {"parameters": {"plot_id": "bed-a"}},
            "rationale_code": "existing_action_applicable",
            "required_evaluator_ids": [
                "action-schema-v1",
                "current-state-v1",
                "permission-v1",
            ],
            "subject_reference": {"action_id": action_id},
        }
    if fixture_case_id == "valid-abstain":
        return {
            **common,
            "proposal_type": "abstain",
            "proposed_value": {"reason_code": "no_supported_action"},
            "rationale_code": "no_supported_action",
            "required_evaluator_ids": ["abstain-policy-v1", "current-state-v1"],
            "subject_reference": deepcopy(request["objective_reference"]),
        }
    if fixture_case_id == "valid-defer":
        return {
            **common,
            "proposal_type": "defer",
            "proposed_value": {"reason_code": "await_state_change"},
            "rationale_code": "await_state_change",
            "required_evaluator_ids": ["current-state-v1", "defer-policy-v1"],
            "subject_reference": deepcopy(request["objective_reference"]),
        }
    raise ProtocolValidationError("fixture case does not define a valid proposal")


def _external_package(
    request: dict[str, object],
    fixture_case_id: str,
) -> bytes:
    # The final dispatch event sequence is intentionally excluded from dispatch ID and
    # every response/proposal identity. A local sentinel can therefore reconstruct the
    # exact package bytes without receiving the database or actual event sequence.
    dispatch = finalize_dispatch(
        _dispatch_identity(request, fixture_case_id),
        event_sequence=1,
        request_envelope=request,
    )
    if fixture_case_id == "unavailable":
        proposal_identities: list[dict[str, object]] = []
        proposal_ids: list[str] = []
        proposal_digests: list[str] = []
        status = "unavailable"
    else:
        proposal = _proposal_identity(
            request,
            str(dispatch["dispatch_id"]),
            fixture_case_id,
        )
        proposal_identities = [proposal]
        proposal_ids = [
            proposal_id_from_identity(
                proposal,
                request_envelope=request,
                fixture_case_id=fixture_case_id,
            )
        ]
        proposal_digests = [
            proposal_content_digest(
                proposal,
                request_envelope=request,
                fixture_case_id=fixture_case_id,
            )
        ]
        status = "proposals_returned"

    response_identity = {
        "adapter_instance_id": "deterministic-fixture-instance-v1",
        "adapter_type": "deterministic-fixture",
        "adapter_version": "deterministic-fixture-v1",
        "dispatch_id": dispatch["dispatch_id"],
        "external_provenance": {
            "fixture_case_id": fixture_case_id,
            "provenance_schema": "sudachi.consultation.provenance/v1",
            "source_type": "deterministic-fixture",
        },
        "proposal_content_digests": proposal_digests,
        "proposal_ids": proposal_ids,
        "protocol_version": 1,
        "request_id": request["request_id"],
        "response_schema": "sudachi.consultation.response/v1",
        "status": status,
    }
    package = finalize_external_package(
        response_identity,
        proposal_identities=proposal_identities,
        request_envelope=request,
        dispatch_envelope=dispatch,
    )
    return canonical_json_bytes(package)


def run_deterministic_fixture(
    request_envelope: dict[str, object],
    fixture_case_id: str,
) -> bytes:
    """Return deterministic noncanonical bytes without ambient authority handles."""

    request = validate_request_envelope(request_envelope)
    if fixture_case_id not in DECLARED_FIXTURE_CASE_IDS:
        raise ProtocolValidationError("fixture case is not declared")
    if fixture_case_id in {
        "valid-action-candidate",
        "valid-abstain",
        "valid-defer",
        "unavailable",
    }:
        output = _external_package(request, fixture_case_id)
    else:
        # Adversarial cases are deterministic typed fixture bytes. Slice 40 owns
        # their raw-package parsing, ingress rejection, or terminalization meaning.
        output = canonical_json_bytes(
            {
                "fixture_case_id": fixture_case_id,
                "fixture_output_schema": _FIXTURE_OUTPUT_SCHEMA,
                "result_code": "declared_adversarial_case",
            }
        )
    if len(output) > 16 * 1024:
        raise ProtocolValidationError("deterministic fixture output exceeds 16 KiB")
    return bytes(output)


__all__ = ["run_deterministic_fixture"]
