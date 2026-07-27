"""Exact ADR 0010 response identities, provenance, and package graph."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Final

from .phase2_dispatch import (
    DECLARED_FIXTURE_CASE_IDS,
    validate_dispatch_envelope,
)
from .phase2_proposal import (
    proposal_content_digest,
    proposal_id_from_identity,
    finalize_proposal,
    validate_proposal_envelope,
    validate_proposal_identity,
)
from .phase2_protocol import (
    ProtocolValidationError,
    canonical_json_bytes,
    protocol_digest_hex,
    validate_request_envelope,
)


ResponseValidationError = ProtocolValidationError

PROVENANCE_SCHEMA: Final = "sudachi.consultation.provenance/v1"
PROVENANCE_SOURCE_TYPE: Final = "deterministic-fixture"
RESPONSE_SCHEMA: Final = "sudachi.consultation.response/v1"
RESPONSE_ADAPTER_TYPE: Final = "deterministic-fixture"
RESPONSE_ADAPTER_VERSION: Final = "deterministic-fixture-v1"
RESPONSE_ADAPTER_INSTANCE_ID: Final = "deterministic-fixture-instance-v1"

_IDENTIFIER_RE: Final = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
_DIGEST_RE: Final = re.compile(r"^[0-9a-f]{64}$")
_DIGEST_ID_RE: Final = re.compile(
    r"^consultation-(?:request|dispatch|response|proposal):[0-9a-f]{64}$"
)
_PROVENANCE_FIELDS: Final = frozenset(
    {"fixture_case_id", "provenance_schema", "source_type"}
)
_RESPONSE_IDENTITY_FIELDS: Final = frozenset(
    {
        "adapter_instance_id",
        "adapter_type",
        "adapter_version",
        "dispatch_id",
        "external_provenance",
        "proposal_content_digests",
        "proposal_ids",
        "protocol_version",
        "request_id",
        "response_schema",
        "status",
    }
)
_RESPONSE_ENVELOPE_FIELDS: Final = frozenset(
    {*_RESPONSE_IDENTITY_FIELDS, "response_id"}
)
_PACKAGE_FIELDS: Final = frozenset({"response", "proposals"})


def _exact_fields(value: object, fields: frozenset[str], *, context: str) -> dict:
    if not isinstance(value, dict):
        raise ResponseValidationError(f"{context} must be an object")
    actual = frozenset(value)
    if actual != fields:
        raise ResponseValidationError(
            f"{context} field set mismatch: "
            f"missing={sorted(fields - actual)!r}, extra={sorted(actual - fields)!r}"
        )
    return value


def _exact_string(value: object, expected: str, *, context: str) -> str:
    if not isinstance(value, str) or value != expected:
        raise ResponseValidationError(f"{context} must equal {expected!r}")
    return value


def _identifier(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER_RE.fullmatch(value) is None:
        raise ResponseValidationError(f"{context} is not a protected identifier")
    return value


def _digest(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _DIGEST_RE.fullmatch(value) is None:
        raise ResponseValidationError(f"{context} is not a lowercase SHA-256 digest")
    return value


def _digest_identifier(value: object, prefix: str, *, context: str) -> str:
    if not isinstance(value, str) or _DIGEST_ID_RE.fullmatch(value) is None:
        raise ResponseValidationError(f"{context} is not a protected digest identifier")
    if not value.startswith(prefix + ":"):
        raise ResponseValidationError(f"{context} has the wrong identifier prefix")
    return value


def validate_external_provenance(
    value: object,
    *,
    dispatch_envelope: object,
) -> dict[str, object]:
    """Validate the exact closed ADR 0010 three-field provenance object."""

    if not isinstance(dispatch_envelope, dict):
        raise ResponseValidationError("linked dispatch envelope must be an object")
    provenance = _exact_fields(
        value,
        _PROVENANCE_FIELDS,
        context="external provenance",
    )
    _exact_string(
        provenance["provenance_schema"],
        PROVENANCE_SCHEMA,
        context="external provenance schema",
    )
    _exact_string(
        provenance["source_type"],
        PROVENANCE_SOURCE_TYPE,
        context="external provenance source type",
    )
    case_id = _identifier(
        provenance["fixture_case_id"],
        context="external provenance fixture case",
    )
    if case_id not in DECLARED_FIXTURE_CASE_IDS:
        raise ResponseValidationError("external provenance fixture case is not declared")
    if case_id != dispatch_envelope.get("fixture_case_id"):
        raise ResponseValidationError("external provenance fixture case does not match dispatch")
    encoded = canonical_json_bytes(provenance)
    if len(encoded) > 8 * 1024:
        raise ResponseValidationError("external provenance exceeds 8 KiB")
    return deepcopy(provenance)


def _proposal_identities_from_envelopes(
    proposal_envelopes: object,
    *,
    request_envelope: object,
    dispatch_envelope: dict[str, object],
    response_id: str,
) -> list[dict[str, object]]:
    if not isinstance(proposal_envelopes, list):
        raise ResponseValidationError("package proposals must be an array")
    case_id = str(dispatch_envelope["fixture_case_id"])
    identities: list[dict[str, object]] = []
    for proposal in proposal_envelopes:
        validated = validate_proposal_envelope(
            proposal,
            request_envelope=request_envelope,
            fixture_case_id=case_id,
        )
        if validated["dispatch_id"] != dispatch_envelope["dispatch_id"]:
            raise ResponseValidationError("proposal dispatch linkage does not match")
        if validated["response_id"] != response_id:
            raise ResponseValidationError("proposal response linkage does not match")
        identities.append(
            {
                key: deepcopy(value)
                for key, value in validated.items()
                if key not in {"proposal_id", "response_id"}
            }
        )
    return identities


def validate_response_identity(
    value: object,
    *,
    request_envelope: object,
    dispatch_envelope: object,
    proposal_identities: object,
) -> dict[str, object]:
    """Validate the exact ADR 0010 response-ID digest preimage."""

    request = validate_request_envelope(request_envelope)
    dispatch = validate_dispatch_envelope(
        dispatch_envelope,
        request_envelope=request,
    )
    identity = _exact_fields(
        value,
        _RESPONSE_IDENTITY_FIELDS,
        context="response identity",
    )
    _exact_string(identity["response_schema"], RESPONSE_SCHEMA, context="response schema")
    if identity["protocol_version"] != 1 or isinstance(identity["protocol_version"], bool):
        raise ResponseValidationError("response protocol version must equal 1")
    request_id = _digest_identifier(
        identity["request_id"],
        "consultation-request",
        context="response request ID",
    )
    if request_id != request["request_id"]:
        raise ResponseValidationError("response request linkage does not match")
    dispatch_id = _digest_identifier(
        identity["dispatch_id"],
        "consultation-dispatch",
        context="response dispatch ID",
    )
    if dispatch_id != dispatch["dispatch_id"]:
        raise ResponseValidationError("response dispatch linkage does not match")
    _exact_string(
        identity["adapter_type"],
        RESPONSE_ADAPTER_TYPE,
        context="response adapter type",
    )
    _exact_string(
        identity["adapter_version"],
        RESPONSE_ADAPTER_VERSION,
        context="response adapter version",
    )
    _exact_string(
        identity["adapter_instance_id"],
        RESPONSE_ADAPTER_INSTANCE_ID,
        context="response adapter instance ID",
    )
    validate_external_provenance(
        identity["external_provenance"],
        dispatch_envelope=dispatch,
    )

    if not isinstance(proposal_identities, list):
        raise ResponseValidationError("response proposal identities must be an array")
    status = identity["status"]
    if status not in {"proposals_returned", "unavailable"}:
        raise ResponseValidationError("response status is not supported")
    expected_count = 1 if status == "proposals_returned" else 0
    if len(proposal_identities) != expected_count:
        raise ResponseValidationError("response status/proposal cardinality is inconsistent")
    if not isinstance(identity["proposal_ids"], list) or not isinstance(
        identity["proposal_content_digests"], list
    ):
        raise ResponseValidationError("response proposal linkage must use arrays")
    if len(identity["proposal_ids"]) != expected_count or len(
        identity["proposal_content_digests"]
    ) != expected_count:
        raise ResponseValidationError("response status/proposal cardinality is inconsistent")

    case_id = str(dispatch["fixture_case_id"])
    expected_ids: list[str] = []
    expected_digests: list[str] = []
    for proposal_identity in proposal_identities:
        validated_proposal = validate_proposal_identity(
            proposal_identity,
            request_envelope=request,
            fixture_case_id=case_id,
        )
        if validated_proposal["dispatch_id"] != dispatch["dispatch_id"]:
            raise ResponseValidationError("proposal dispatch linkage does not match response")
        expected_ids.append(
            proposal_id_from_identity(
                validated_proposal,
                request_envelope=request,
                fixture_case_id=case_id,
            )
        )
        expected_digests.append(
            proposal_content_digest(
                validated_proposal,
                request_envelope=request,
                fixture_case_id=case_id,
            )
        )
    if identity["proposal_ids"] != expected_ids:
        raise ResponseValidationError("response proposal ID cardinality or linkage is inconsistent")
    if identity["proposal_content_digests"] != expected_digests:
        raise ResponseValidationError(
            "response proposal digest cardinality or linkage is inconsistent"
        )
    for proposal_id in identity["proposal_ids"]:
        _digest_identifier(
            proposal_id,
            "consultation-proposal",
            context="response proposal ID",
        )
    for digest in identity["proposal_content_digests"]:
        _digest(digest, context="response proposal content digest")
    canonical_json_bytes(identity)
    return deepcopy(identity)


def response_id_from_identity(
    identity: object,
    *,
    request_envelope: object,
    dispatch_envelope: object,
    proposal_identities: object,
) -> str:
    validated = validate_response_identity(
        identity,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch_envelope,
        proposal_identities=proposal_identities,
    )
    return "consultation-response:" + protocol_digest_hex("response-id", validated)


def validate_response_envelope(
    value: object,
    *,
    request_envelope: object,
    dispatch_envelope: object,
    proposal_envelopes: object,
) -> dict[str, object]:
    envelope = _exact_fields(
        value,
        _RESPONSE_ENVELOPE_FIELDS,
        context="response envelope",
    )
    response_id = _digest_identifier(
        envelope["response_id"],
        "consultation-response",
        context="response ID",
    )
    dispatch = validate_dispatch_envelope(
        dispatch_envelope,
        request_envelope=request_envelope,
    )
    proposal_identities = _proposal_identities_from_envelopes(
        proposal_envelopes,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch,
        response_id=response_id,
    )
    identity = {key: deepcopy(envelope[key]) for key in _RESPONSE_IDENTITY_FIELDS}
    validated = validate_response_identity(
        identity,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch,
        proposal_identities=proposal_identities,
    )
    expected = response_id_from_identity(
        validated,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch,
        proposal_identities=proposal_identities,
    )
    if response_id != expected:
        raise ResponseValidationError("response ID does not match identity")
    encoded = canonical_json_bytes(envelope)
    if len(encoded) > 16 * 1024:
        raise ResponseValidationError("response envelope exceeds 16 KiB")
    return deepcopy(envelope)


def finalize_external_package(
    response_identity: object,
    *,
    proposal_identities: object,
    request_envelope: object,
    dispatch_envelope: object,
) -> dict[str, object]:
    """Build the cycle-free final response/proposal package preimage."""

    if not isinstance(proposal_identities, list):
        raise ResponseValidationError("response proposal identities must be an array")
    dispatch = validate_dispatch_envelope(
        dispatch_envelope,
        request_envelope=request_envelope,
    )
    validated_identity = validate_response_identity(
        response_identity,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch,
        proposal_identities=proposal_identities,
    )
    response_id = response_id_from_identity(
        validated_identity,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch,
        proposal_identities=proposal_identities,
    )
    case_id = str(dispatch["fixture_case_id"])
    proposals = [
        finalize_proposal(
            identity,
            response_id=response_id,
            request_envelope=request_envelope,
            fixture_case_id=case_id,
        )
        for identity in proposal_identities
    ]
    response = {**validated_identity, "response_id": response_id}
    validate_response_envelope(
        response,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch,
        proposal_envelopes=proposals,
    )
    package = {"response": response, "proposals": proposals}
    return validate_external_package(
        package,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch,
    )


def validate_external_package(
    value: object,
    *,
    request_envelope: object,
    dispatch_envelope: object,
) -> dict[str, object]:
    package = _exact_fields(value, _PACKAGE_FIELDS, context="external package")
    if not isinstance(package["proposals"], list):
        raise ResponseValidationError("package proposals must be an array")
    response = package["response"]
    if not isinstance(response, dict):
        raise ResponseValidationError("package response must be an object")
    validate_response_envelope(
        response,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch_envelope,
        proposal_envelopes=package["proposals"],
    )
    status = response["status"]
    expected = 1 if status == "proposals_returned" else 0
    if len(package["proposals"]) != expected:
        raise ResponseValidationError("package status/proposal cardinality is inconsistent")
    encoded = canonical_json_bytes(package)
    if len(encoded) > 16 * 1024:
        raise ResponseValidationError("external package exceeds 16 KiB")
    return deepcopy(package)


def external_package_digest(
    value: object,
    *,
    request_envelope: object,
    dispatch_envelope: object,
) -> str:
    validated = validate_external_package(
        value,
        request_envelope=request_envelope,
        dispatch_envelope=dispatch_envelope,
    )
    return protocol_digest_hex("external-package", validated)
