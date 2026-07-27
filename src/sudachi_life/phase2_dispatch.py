"""Exact ADR 0010 dispatch identities, IDs, and final envelopes."""

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


DispatchValidationError = ProtocolValidationError

DISPATCH_SCHEMA: Final = "sudachi.consultation.dispatch/v1"
DISPATCH_SOURCE: Final = "administration:consultation.dispatch"
DISPATCH_CONFIGURATION_VERSION: Final = "phase2-fixture-v1"
DISPATCH_ADAPTER_VERSION: Final = "deterministic-fixture-v1"
DISPATCH_WORK_CLASS: Final = "fixture-constant-v1"

DECLARED_FIXTURE_CASE_IDS: Final = frozenset(
    {
        "abandoned-lineage-package",
        "conflicting-duplicate",
        "contradictory-state",
        "crash-after-admission",
        "expiry-after-ingress",
        "expiry-before-ingress",
        "fixture-exception",
        "identical-duplicate",
        "invalid-parameters",
        "malformed-response",
        "over-budget",
        "stale-observation",
        "unavailable",
        "unknown-action",
        "unknown-schema",
        "valid-abstain",
        "valid-action-candidate",
        "valid-defer",
    }
)

_IDENTIFIER_RE: Final = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
_DIGEST_ID_RE: Final = re.compile(r"^consultation-(?:request|dispatch):[0-9a-f]{64}$")
_IDENTITY_FIELDS: Final = frozenset(
    {
        "adapter_version",
        "configuration_version",
        "dispatch_ordinal",
        "dispatch_schema",
        "fixture_case_id",
        "lineage_generation",
        "organism_id",
        "protocol_version",
        "request_id",
        "work_class",
    }
)
_ENVELOPE_FIELDS: Final = frozenset(
    {*_IDENTITY_FIELDS, "authority", "dispatch_id", "event_sequence"}
)


def _exact_fields(value: object, fields: frozenset[str], *, context: str) -> dict:
    if not isinstance(value, dict):
        raise DispatchValidationError(f"{context} must be an object")
    actual = frozenset(value)
    if actual != fields:
        raise DispatchValidationError(
            f"{context} field set mismatch: "
            f"missing={sorted(fields - actual)!r}, extra={sorted(actual - fields)!r}"
        )
    return value


def _integer(value: object, *, context: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise DispatchValidationError(
            f"{context} must be an integer greater than or equal to {minimum}"
        )
    return value


def _identifier(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER_RE.fullmatch(value) is None:
        raise DispatchValidationError(f"{context} is not a protected identifier")
    return value


def _exact_string(value: object, expected: str, *, context: str) -> str:
    if not isinstance(value, str) or value != expected:
        raise DispatchValidationError(f"{context} must equal {expected!r}")
    return value


def _digest_identifier(value: object, prefix: str, *, context: str) -> str:
    if not isinstance(value, str) or _DIGEST_ID_RE.fullmatch(value) is None:
        raise DispatchValidationError(f"{context} is not a protected digest identifier")
    if not value.startswith(prefix + ":"):
        raise DispatchValidationError(f"{context} has the wrong identifier prefix")
    return value


def validate_dispatch_identity(
    value: object,
    *,
    request_envelope: object,
) -> dict[str, object]:
    """Validate the exact ADR 0010 dispatch-ID digest preimage."""

    request = validate_request_envelope(request_envelope)
    identity = _exact_fields(value, _IDENTITY_FIELDS, context="dispatch identity")
    _exact_string(identity["dispatch_schema"], DISPATCH_SCHEMA, context="dispatch schema")
    if identity["protocol_version"] != 1 or isinstance(identity["protocol_version"], bool):
        raise DispatchValidationError("dispatch protocol version must equal 1")
    organism_id = _identifier(identity["organism_id"], context="dispatch organism ID")
    if organism_id != request["organism_id"]:
        raise DispatchValidationError("dispatch organism does not match request")
    lineage = _integer(identity["lineage_generation"], context="dispatch lineage")
    if lineage != request["lineage_generation"]:
        raise DispatchValidationError("dispatch lineage does not match request")
    request_id = _digest_identifier(
        identity["request_id"],
        "consultation-request",
        context="dispatch request ID",
    )
    if request_id != request["request_id"]:
        raise DispatchValidationError("dispatch request linkage does not match")
    if identity["dispatch_ordinal"] != 1 or isinstance(identity["dispatch_ordinal"], bool):
        raise DispatchValidationError("dispatch ordinal must equal 1")
    configuration = _exact_string(
        identity["configuration_version"],
        DISPATCH_CONFIGURATION_VERSION,
        context="dispatch configuration version",
    )
    if configuration != request["configuration_version"]:
        raise DispatchValidationError("dispatch configuration does not match request")
    _exact_string(
        identity["adapter_version"],
        DISPATCH_ADAPTER_VERSION,
        context="dispatch adapter version",
    )
    _exact_string(
        identity["work_class"],
        DISPATCH_WORK_CLASS,
        context="dispatch work class",
    )
    case_id = _identifier(identity["fixture_case_id"], context="dispatch fixture case")
    if case_id not in DECLARED_FIXTURE_CASE_IDS:
        raise DispatchValidationError("dispatch fixture case is not declared")
    canonical_json_bytes(identity)
    return deepcopy(identity)


def dispatch_id_from_identity(
    identity: object,
    *,
    request_envelope: object,
) -> str:
    validated = validate_dispatch_identity(identity, request_envelope=request_envelope)
    return "consultation-dispatch:" + protocol_digest_hex("dispatch-id", validated)


def finalize_dispatch(
    identity: object,
    *,
    event_sequence: int,
    request_envelope: object,
) -> dict[str, object]:
    validated = validate_dispatch_identity(identity, request_envelope=request_envelope)
    final = {
        **validated,
        "authority": {
            "source": DISPATCH_SOURCE,
            "writer_category": "administration",
        },
        "dispatch_id": dispatch_id_from_identity(
            validated,
            request_envelope=request_envelope,
        ),
        "event_sequence": _integer(
            event_sequence,
            context="dispatch event sequence",
            minimum=1,
        ),
    }
    return validate_dispatch_envelope(final, request_envelope=request_envelope)


def validate_dispatch_envelope(
    value: object,
    *,
    request_envelope: object,
) -> dict[str, object]:
    envelope = _exact_fields(value, _ENVELOPE_FIELDS, context="dispatch envelope")
    identity = {key: deepcopy(envelope[key]) for key in _IDENTITY_FIELDS}
    validated = validate_dispatch_identity(identity, request_envelope=request_envelope)
    dispatch_id = _digest_identifier(
        envelope["dispatch_id"],
        "consultation-dispatch",
        context="dispatch ID",
    )
    expected = dispatch_id_from_identity(validated, request_envelope=request_envelope)
    if dispatch_id != expected:
        raise DispatchValidationError("dispatch ID does not match identity")
    _integer(envelope["event_sequence"], context="dispatch event sequence", minimum=1)
    authority = _exact_fields(
        envelope["authority"],
        frozenset({"source", "writer_category"}),
        context="dispatch authority",
    )
    _exact_string(authority["source"], DISPATCH_SOURCE, context="dispatch source")
    _exact_string(
        authority["writer_category"],
        "administration",
        context="dispatch writer category",
    )
    canonical_json_bytes(envelope)
    return deepcopy(envelope)
