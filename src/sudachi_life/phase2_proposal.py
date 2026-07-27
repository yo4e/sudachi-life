"""Exact proposal identities, IDs, and type-specific envelopes."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Final

from .phase2_protocol import (
    ProtocolValidationError,
    canonical_json_bytes,
    protocol_digest_hex,
    validate_request_envelope,
)


ProposalValidationError = ProtocolValidationError

PROPOSAL_SCHEMA: Final = "sudachi.consultation.proposal/v1"
PROPOSAL_TYPES: Final = frozenset({"action_candidate", "abstain", "defer"})

_IDENTIFIER_RE: Final = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
_DIGEST_ID_RE: Final = re.compile(
    r"^(consultation-(?:request|dispatch|response|proposal)):[0-9a-f]{64}$"
)
_IDENTITY_FIELDS: Final = frozenset(
    {
        "confidence_basis",
        "dispatch_id",
        "expiry_lifecycle_number",
        "proposal_ordinal",
        "proposal_schema",
        "proposal_type",
        "protocol_version",
        "proposed_value",
        "rationale_code",
        "request_id",
        "required_evaluator_ids",
        "subject_reference",
    }
)
_ENVELOPE_FIELDS: Final = frozenset({*_IDENTITY_FIELDS, "proposal_id", "response_id"})

_TYPE_RULES: Final = {
    "action_candidate": {
        "rationale": "existing_action_applicable",
        "evaluators": [
            "action-schema-v1",
            "current-state-v1",
            "permission-v1",
        ],
    },
    "abstain": {
        "rationale": "no_supported_action",
        "evaluators": ["abstain-policy-v1", "current-state-v1"],
    },
    "defer": {
        "rationale": "await_state_change",
        "evaluators": ["current-state-v1", "defer-policy-v1"],
    },
}


def _exact_fields(value: object, fields: frozenset[str], *, context: str) -> dict:
    if not isinstance(value, dict):
        raise ProposalValidationError(f"{context} must be an object")
    actual = frozenset(value)
    if actual != fields:
        raise ProposalValidationError(
            f"{context} field set mismatch: "
            f"missing={sorted(fields - actual)!r}, extra={sorted(actual - fields)!r}"
        )
    return value


def _integer(value: object, *, context: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ProposalValidationError(
            f"{context} must be an integer greater than or equal to {minimum}"
        )
    return value


def _identifier(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER_RE.fullmatch(value) is None:
        raise ProposalValidationError(f"{context} is not a protected identifier")
    return value


def _digest_identifier(value: object, prefix: str, *, context: str) -> str:
    if not isinstance(value, str) or _DIGEST_ID_RE.fullmatch(value) is None:
        raise ProposalValidationError(f"{context} is not a protected digest identifier")
    if not value.startswith(prefix + ":"):
        raise ProposalValidationError(f"{context} has the wrong identifier prefix")
    return value


def _confidence_basis(value: object, fixture_case_id: str) -> dict:
    basis = _exact_fields(
        value,
        frozenset({"basis_type", "fixture_case_id"}),
        context="proposal confidence basis",
    )
    if basis["basis_type"] != "deterministic_fixture_case":
        raise ProposalValidationError("proposal confidence basis type is not exact")
    if basis["fixture_case_id"] != fixture_case_id:
        raise ProposalValidationError("proposal fixture case does not match dispatch")
    _identifier(basis["fixture_case_id"], context="proposal fixture case")
    return basis


def _validate_action_candidate(identity: dict, request: dict) -> None:
    subject = _exact_fields(
        identity["subject_reference"],
        frozenset({"action_id"}),
        context="action candidate subject",
    )
    action_id = _identifier(subject["action_id"], context="proposal action ID")
    if action_id not in request["allowed_action_ids"]:
        raise ProposalValidationError("proposal action is not an allowed action")
    proposed = _exact_fields(
        identity["proposed_value"],
        frozenset({"parameters"}),
        context="action candidate proposed value",
    )
    parameters = _exact_fields(
        proposed["parameters"],
        frozenset({"plot_id"}),
        context="action candidate parameters",
    )
    _identifier(parameters["plot_id"], context="action candidate plot ID")


def _validate_abstain_or_defer(
    identity: dict,
    request: dict,
    *,
    reason_code: str,
) -> None:
    subject = _exact_fields(
        identity["subject_reference"],
        frozenset({"digest", "objective_id"}),
        context=f"{identity['proposal_type']} subject",
    )
    if subject != request["objective_reference"]:
        raise ProposalValidationError("proposal objective reference does not match request")
    proposed = _exact_fields(
        identity["proposed_value"],
        frozenset({"reason_code"}),
        context=f"{identity['proposal_type']} proposed value",
    )
    if proposed["reason_code"] != reason_code:
        raise ProposalValidationError(
            f"{identity['proposal_type']} reason code is not exact"
        )


def validate_proposal_identity(
    value: object,
    *,
    request_envelope: object,
    fixture_case_id: str,
) -> dict[str, object]:
    """Validate one exact proposal-content digest preimage."""

    request = validate_request_envelope(request_envelope)
    identity = _exact_fields(value, _IDENTITY_FIELDS, context="proposal identity")
    if identity["proposal_schema"] != PROPOSAL_SCHEMA:
        raise ProposalValidationError("proposal schema is not exact")
    if identity["protocol_version"] != 1 or isinstance(identity["protocol_version"], bool):
        raise ProposalValidationError("proposal protocol version must equal 1")
    if identity["proposal_ordinal"] != 1 or isinstance(identity["proposal_ordinal"], bool):
        raise ProposalValidationError("proposal ordinal must equal 1")
    proposal_type = identity["proposal_type"]
    if proposal_type not in PROPOSAL_TYPES:
        raise ProposalValidationError("proposal type is not supported")
    if proposal_type not in request["requested_proposal_types"]:
        raise ProposalValidationError("proposal type was not requested")
    if identity["request_id"] != request["request_id"]:
        raise ProposalValidationError("proposal request linkage does not match")
    _digest_identifier(
        identity["dispatch_id"],
        "consultation-dispatch",
        context="proposal dispatch ID",
    )
    expiry = _integer(identity["expiry_lifecycle_number"], context="proposal expiry")
    if expiry != request["expiry_lifecycle_number"]:
        raise ProposalValidationError("proposal expiry does not match request expiry")
    _confidence_basis(identity["confidence_basis"], fixture_case_id)

    rules = _TYPE_RULES[proposal_type]
    if identity["rationale_code"] != rules["rationale"]:
        raise ProposalValidationError("proposal rationale is not exact")
    if identity["required_evaluator_ids"] != rules["evaluators"]:
        raise ProposalValidationError("proposal evaluator set is not exact")

    if proposal_type == "action_candidate":
        _validate_action_candidate(identity, request)
    elif proposal_type == "abstain":
        _validate_abstain_or_defer(identity, request, reason_code="no_supported_action")
    else:
        _validate_abstain_or_defer(identity, request, reason_code="await_state_change")

    canonical_json_bytes(identity)
    return deepcopy(identity)


def proposal_content_digest(
    identity: object,
    *,
    request_envelope: object,
    fixture_case_id: str,
) -> str:
    validated = validate_proposal_identity(
        identity,
        request_envelope=request_envelope,
        fixture_case_id=fixture_case_id,
    )
    return protocol_digest_hex("proposal-content", validated)


def proposal_id_from_identity(
    identity: object,
    *,
    request_envelope: object,
    fixture_case_id: str,
) -> str:
    return "consultation-proposal:" + proposal_content_digest(
        identity,
        request_envelope=request_envelope,
        fixture_case_id=fixture_case_id,
    )


def finalize_proposal(
    identity: object,
    *,
    response_id: str,
    request_envelope: object,
    fixture_case_id: str,
) -> dict[str, object]:
    """Insert derived proposal/response linkage after both identities exist."""

    validated = validate_proposal_identity(
        identity,
        request_envelope=request_envelope,
        fixture_case_id=fixture_case_id,
    )
    _digest_identifier(
        response_id,
        "consultation-response",
        context="proposal response ID",
    )
    final = {
        **validated,
        "proposal_id": proposal_id_from_identity(
            validated,
            request_envelope=request_envelope,
            fixture_case_id=fixture_case_id,
        ),
        "response_id": response_id,
    }
    return validate_proposal_envelope(
        final,
        request_envelope=request_envelope,
        fixture_case_id=fixture_case_id,
    )


def validate_proposal_envelope(
    value: object,
    *,
    request_envelope: object,
    fixture_case_id: str,
) -> dict[str, object]:
    envelope = _exact_fields(value, _ENVELOPE_FIELDS, context="proposal envelope")
    identity = {key: deepcopy(envelope[key]) for key in _IDENTITY_FIELDS}
    validated = validate_proposal_identity(
        identity,
        request_envelope=request_envelope,
        fixture_case_id=fixture_case_id,
    )
    proposal_id = _digest_identifier(
        envelope["proposal_id"],
        "consultation-proposal",
        context="proposal ID",
    )
    expected_id = proposal_id_from_identity(
        validated,
        request_envelope=request_envelope,
        fixture_case_id=fixture_case_id,
    )
    if proposal_id != expected_id:
        raise ProposalValidationError("proposal ID does not match content digest")
    _digest_identifier(
        envelope["response_id"],
        "consultation-response",
        context="proposal response ID",
    )
    encoded = canonical_json_bytes(envelope)
    if len(encoded) > 16 * 1024:
        raise ProposalValidationError("proposal envelope exceeds 16 KiB")
    return deepcopy(envelope)
