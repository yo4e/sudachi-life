"""Exact canonical bytes, domain-separated digests, and request schema validation."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
import unicodedata
from typing import Final

from .errors import SudachiError


class ProtocolValidationError(SudachiError):
    """A consultation protocol value is not exact or canonical."""


_PROTOCOL_DOMAIN: Final = b"sudachi.consultation/v1\n"
_DIGEST_LABELS: Final = frozenset(
    {
        "request-id",
        "dispatch-id",
        "proposal-content",
        "response-id",
        "external-package",
        "current-state-reference",
        "disposition-id",
    }
)
_IDENTIFIER_RE: Final = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
_DIGEST_RE: Final = re.compile(r"^[0-9a-f]{64}$")

REQUEST_SCHEMA: Final = "sudachi.consultation.request/v1"
REQUEST_SOURCE: Final = "organism:consultation.request"
REQUEST_POLICY_VERSION: Final = "phase1-fixed-policy-v1"
REQUEST_CONFIGURATION_VERSION: Final = "phase2-fixture-v1"
REQUEST_REASON: Final = "no_applicable_action"
REQUESTED_PROPOSAL_TYPES: Final = ("abstain", "action_candidate", "defer")
OBJECTIVE_ID: Final = "seed-garden.harvest-fruit/v1"

_REQUEST_IDENTITY_FIELDS: Final = frozenset(
    {
        "allowed_action_ids",
        "budget_config_version",
        "configuration_version",
        "expiry_lifecycle_number",
        "lineage_generation",
        "lifecycle_number",
        "objective_digest",
        "observation_digest",
        "organism_id",
        "permission_ids",
        "policy_version",
        "protocol_version",
        "reason_code",
        "request_ordinal",
        "request_schema",
        "requested_proposal_types",
    }
)
_REQUEST_ENVELOPE_FIELDS: Final = frozenset(
    {
        "allowed_action_ids",
        "authority",
        "budget_config_version",
        "budget_snapshot",
        "configuration_version",
        "event_sequence",
        "expiry_lifecycle_number",
        "lineage_generation",
        "lifecycle_number",
        "objective_reference",
        "observation_reference",
        "organism_id",
        "parent_event_sequences",
        "permission_ids",
        "policy_version",
        "protocol_version",
        "reason_code",
        "request_id",
        "request_ordinal",
        "request_schema",
        "requested_proposal_types",
    }
)
_BUDGET_VECTOR_FIELDS: Final = frozenset(
    {
        "input_events",
        "observations",
        "action_attempts",
        "environment_mutations",
        "caregiver_consultations",
        "network_calls",
        "subprocess_calls",
        "external_mutable_writes",
    }
)
_BUDGET_SNAPSHOT_FIELDS: Final = frozenset(
    {
        "canonical_records_limit",
        "canonical_records_used",
        "config_version",
        "consumed",
        "elapsed_monotonic_ns",
        "lifecycle_wall_time_limit_ns",
        "limits",
        "remaining",
        "semantic_steps_limit",
        "semantic_steps_used",
    }
)


def _validate_canonical_value(value: object, *, path: str) -> None:
    if value is None:
        raise ProtocolValidationError(f"{path}: null is not declared")
    if isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        raise ProtocolValidationError(f"{path}: floating point is forbidden")
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise ProtocolValidationError(f"{path}: strings must be NFC-normalized")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_canonical_value(item, path=f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ProtocolValidationError(f"{path}: objects require string keys")
            if unicodedata.normalize("NFC", key) != key:
                raise ProtocolValidationError(f"{path}: object keys must be NFC-normalized")
            _validate_canonical_value(item, path=f"{path}.{key}")
        return
    raise ProtocolValidationError(
        f"{path}: unsupported canonical value type {type(value).__name__}"
    )


def canonical_json_bytes(value: object) -> bytes:
    """Return exact compact sorted UTF-8 JSON after canonical-value validation."""

    _validate_canonical_value(value, path="value")
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ProtocolValidationError("value is not canonical JSON") from exc
    return text.encode("utf-8")


def protocol_digest_hex(label: str, value: object) -> str:
    """Return the exact protocol-v1 domain-separated SHA-256 digest."""

    if label not in _DIGEST_LABELS:
        raise ProtocolValidationError(f"unsupported protocol digest label: {label!r}")
    return hashlib.sha256(
        _PROTOCOL_DOMAIN + label.encode("ascii") + b"\n" + canonical_json_bytes(value)
    ).hexdigest()


def _exact_fields(value: object, expected: frozenset[str], *, context: str) -> dict:
    if not isinstance(value, dict):
        raise ProtocolValidationError(f"{context} must be an object")
    actual = frozenset(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ProtocolValidationError(
            f"{context} field set mismatch: missing={missing!r}, extra={extra!r}"
        )
    return value


def _integer(value: object, *, context: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ProtocolValidationError(
            f"{context} must be an integer greater than or equal to {minimum}"
        )
    return value


def _exact_string(value: object, expected: str, *, context: str) -> str:
    if value != expected or not isinstance(value, str):
        raise ProtocolValidationError(f"{context} must equal {expected!r}")
    return value


def _identifier(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER_RE.fullmatch(value) is None:
        raise ProtocolValidationError(f"{context} is not a protected identifier")
    return value


def _digest(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _DIGEST_RE.fullmatch(value) is None:
        raise ProtocolValidationError(f"{context} is not a lowercase SHA-256 digest")
    return value


def _sorted_unique_identifiers(value: object, *, context: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ProtocolValidationError(f"{context} must be a nonempty array")
    items = [_identifier(item, context=context) for item in value]
    if items != sorted(set(items)):
        raise ProtocolValidationError(f"{context} must be sorted unique identifiers")
    return items


def _validate_budget_snapshot(value: object) -> dict[str, object]:
    snapshot = _exact_fields(
        value,
        _BUDGET_SNAPSHOT_FIELDS,
        context="request budget snapshot",
    )
    _exact_string(snapshot["config_version"], "phase1-v1", context="budget config version")
    vectors: dict[str, dict[str, int]] = {}
    for name in ("limits", "consumed", "remaining"):
        vector = _exact_fields(
            snapshot[name],
            _BUDGET_VECTOR_FIELDS,
            context=f"budget {name}",
        )
        vectors[name] = {
            key: _integer(vector[key], context=f"budget {name}.{key}")
            for key in sorted(_BUDGET_VECTOR_FIELDS)
        }
    for key in _BUDGET_VECTOR_FIELDS:
        if vectors["consumed"][key] > vectors["limits"][key]:
            raise ProtocolValidationError(f"budget consumed.{key} exceeds its limit")
        if vectors["remaining"][key] != (
            vectors["limits"][key] - vectors["consumed"][key]
        ):
            raise ProtocolValidationError(f"budget remaining.{key} is inconsistent")
    for used, limit, context in (
        (snapshot["canonical_records_used"], snapshot["canonical_records_limit"], "records"),
        (snapshot["semantic_steps_used"], snapshot["semantic_steps_limit"], "steps"),
    ):
        used_value = _integer(used, context=f"budget {context} used")
        limit_value = _integer(limit, context=f"budget {context} limit")
        if used_value > limit_value:
            raise ProtocolValidationError(f"budget {context} used exceeds its limit")
    _integer(snapshot["elapsed_monotonic_ns"], context="budget elapsed monotonic")
    _integer(
        snapshot["lifecycle_wall_time_limit_ns"],
        context="budget lifecycle wall-time limit",
    )
    return snapshot


def validate_request_identity(value: object) -> dict[str, object]:
    identity = _exact_fields(value, _REQUEST_IDENTITY_FIELDS, context="request identity")
    _exact_string(identity["request_schema"], REQUEST_SCHEMA, context="request schema")
    if identity["protocol_version"] != 1 or isinstance(identity["protocol_version"], bool):
        raise ProtocolValidationError("request protocol version must equal 1")
    _identifier(identity["organism_id"], context="request organism ID")
    _integer(identity["lineage_generation"], context="request lineage")
    lifecycle = _integer(identity["lifecycle_number"], context="request lifecycle")
    ordinal = _integer(identity["request_ordinal"], context="request ordinal", minimum=1)
    if ordinal > 4:
        raise ProtocolValidationError("request ordinal exceeds the current-lineage limit")
    expiry = _integer(identity["expiry_lifecycle_number"], context="request expiry")
    if expiry != lifecycle + 2:
        raise ProtocolValidationError("request expiry must equal lifecycle plus two")
    _exact_string(identity["reason_code"], REQUEST_REASON, context="request reason")
    if identity["requested_proposal_types"] != list(REQUESTED_PROPOSAL_TYPES):
        raise ProtocolValidationError("request proposal types are not exact")
    allowed = _sorted_unique_identifiers(
        identity["allowed_action_ids"], context="request allowed action IDs"
    )
    permissions = _sorted_unique_identifiers(
        identity["permission_ids"], context="request permission IDs"
    )
    expected_permissions = [f"garden.action.execute:{item}" for item in allowed]
    if permissions != expected_permissions:
        raise ProtocolValidationError("request permissions do not match allowed actions")
    _exact_string(
        identity["policy_version"],
        REQUEST_POLICY_VERSION,
        context="request policy version",
    )
    _exact_string(
        identity["budget_config_version"],
        "phase1-v1",
        context="request budget configuration version",
    )
    _exact_string(
        identity["configuration_version"],
        REQUEST_CONFIGURATION_VERSION,
        context="request consultation configuration version",
    )
    _digest(identity["observation_digest"], context="request observation digest")
    _digest(identity["objective_digest"], context="request objective digest")
    canonical_json_bytes(identity)
    return deepcopy(identity)


def request_id_from_identity(identity: object) -> str:
    validated = validate_request_identity(identity)
    return "consultation-request:" + protocol_digest_hex("request-id", validated)


def validate_request_envelope(value: object) -> dict[str, object]:
    envelope = _exact_fields(value, _REQUEST_ENVELOPE_FIELDS, context="request envelope")
    _exact_string(envelope["request_schema"], REQUEST_SCHEMA, context="request schema")
    if envelope["protocol_version"] != 1 or isinstance(envelope["protocol_version"], bool):
        raise ProtocolValidationError("request protocol version must equal 1")
    _identifier(envelope["organism_id"], context="request organism ID")
    _integer(envelope["lineage_generation"], context="request lineage")
    lifecycle = _integer(envelope["lifecycle_number"], context="request lifecycle")
    event_sequence = _integer(
        envelope["event_sequence"], context="request event sequence", minimum=1
    )
    ordinal = _integer(envelope["request_ordinal"], context="request ordinal", minimum=1)
    if ordinal > 4:
        raise ProtocolValidationError("request ordinal exceeds the current-lineage limit")
    expiry = _integer(envelope["expiry_lifecycle_number"], context="request expiry")
    if expiry != lifecycle + 2:
        raise ProtocolValidationError("request expiry must equal lifecycle plus two")
    _exact_string(envelope["reason_code"], REQUEST_REASON, context="request reason")
    if envelope["requested_proposal_types"] != list(REQUESTED_PROPOSAL_TYPES):
        raise ProtocolValidationError("request proposal types are not exact")
    allowed = _sorted_unique_identifiers(
        envelope["allowed_action_ids"], context="request allowed action IDs"
    )
    permissions = _sorted_unique_identifiers(
        envelope["permission_ids"], context="request permission IDs"
    )
    if permissions != [f"garden.action.execute:{item}" for item in allowed]:
        raise ProtocolValidationError("request permissions do not match allowed actions")
    _exact_string(
        envelope["policy_version"], REQUEST_POLICY_VERSION, context="request policy version"
    )
    _exact_string(
        envelope["budget_config_version"],
        "phase1-v1",
        context="request budget configuration version",
    )
    _exact_string(
        envelope["configuration_version"],
        REQUEST_CONFIGURATION_VERSION,
        context="request consultation configuration version",
    )
    authority = _exact_fields(
        envelope["authority"],
        frozenset({"source", "writer_category"}),
        context="request authority",
    )
    if authority != {"source": REQUEST_SOURCE, "writer_category": "organism"}:
        raise ProtocolValidationError("request authority is not exact")
    observation = _exact_fields(
        envelope["observation_reference"],
        frozenset({"digest", "event_sequence"}),
        context="request observation reference",
    )
    _digest(observation["digest"], context="request observation digest")
    observation_sequence = _integer(
        observation["event_sequence"],
        context="request observation event sequence",
        minimum=1,
    )
    objective = _exact_fields(
        envelope["objective_reference"],
        frozenset({"digest", "objective_id"}),
        context="request objective reference",
    )
    _digest(objective["digest"], context="request objective digest")
    _exact_string(objective["objective_id"], OBJECTIVE_ID, context="request objective ID")
    parents = envelope["parent_event_sequences"]
    if not isinstance(parents, list) or not parents:
        raise ProtocolValidationError("request parent events must be a nonempty array")
    parent_values = [
        _integer(item, context="request parent event sequence", minimum=1)
        for item in parents
    ]
    if parent_values != sorted(set(parent_values)):
        raise ProtocolValidationError("request parent events must be sorted unique")
    if any(item >= event_sequence for item in parent_values):
        raise ProtocolValidationError("request parent events must precede the request event")
    if observation_sequence not in parent_values:
        raise ProtocolValidationError("request observation event must be an existing parent")
    _validate_budget_snapshot(envelope["budget_snapshot"])

    identity = request_identity_from_envelope(envelope, _already_validated=True)
    request_id = _identifier(envelope["request_id"], context="request ID")
    if request_id != request_id_from_identity(identity):
        raise ProtocolValidationError("request ID does not match its exact identity")
    encoded = canonical_json_bytes(envelope)
    if len(encoded) > 16 * 1024:
        raise ProtocolValidationError("request envelope exceeds the protected 16 KiB limit")
    return deepcopy(envelope)


def request_identity_from_envelope(
    value: object,
    *,
    _already_validated: bool = False,
) -> dict[str, object]:
    envelope = value if _already_validated else validate_request_envelope(value)
    assert isinstance(envelope, dict)
    identity = {
        "allowed_action_ids": deepcopy(envelope["allowed_action_ids"]),
        "budget_config_version": envelope["budget_config_version"],
        "configuration_version": envelope["configuration_version"],
        "expiry_lifecycle_number": envelope["expiry_lifecycle_number"],
        "lineage_generation": envelope["lineage_generation"],
        "lifecycle_number": envelope["lifecycle_number"],
        "objective_digest": envelope["objective_reference"]["digest"],
        "observation_digest": envelope["observation_reference"]["digest"],
        "organism_id": envelope["organism_id"],
        "permission_ids": deepcopy(envelope["permission_ids"]),
        "policy_version": envelope["policy_version"],
        "protocol_version": envelope["protocol_version"],
        "reason_code": envelope["reason_code"],
        "request_ordinal": envelope["request_ordinal"],
        "request_schema": envelope["request_schema"],
        "requested_proposal_types": deepcopy(envelope["requested_proposal_types"]),
    }
    return validate_request_identity(identity)
