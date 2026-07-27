"""Exact ADR 0010/0013 current-state and disposition identities."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Final

from .phase2_protocol import (
    ProtocolValidationError,
    canonical_json_bytes,
    protocol_digest_hex,
)


DispositionValidationError = ProtocolValidationError

CURRENT_STATE_SCHEMA: Final = "sudachi.consultation.current_state/v1"
DISPOSITION_SCHEMA: Final = "sudachi.consultation.disposition/v1"
DISPOSITION_SOURCE: Final = "organism:consultation.disposition"
DISPOSITION_EVENT_TYPE: Final = "consultation_disposition_created"
DISPOSITION_LEDGER_EVENT_TYPE: Final = "consultation_disposition_budget_ledger"
DISPOSITION_WORK_CLASS: Final = "consultation_disposition"

_IDENTIFIER_RE: Final = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")
_DIGEST_RE: Final = re.compile(r"^[0-9a-f]{64}$")
_DIGEST_ID_RE: Final = re.compile(
    r"^consultation-(?:request|dispatch|response|proposal|disposition):[0-9a-f]{64}$"
)

_CURRENT_STATE_FIELDS: Final = frozenset(
    {
        "budget_config_version",
        "configuration_version",
        "consecutive_failures",
        "considering_lifecycle_number",
        "current_state_schema",
        "garden_observation",
        "latest_stable_checkpoint_id",
        "latest_stable_event_sequence",
        "lineage_generation",
        "organism_id",
        "organism_status",
        "proposal_reference",
        "protocol_version",
        "request_reference",
    }
)
_REQUEST_REFERENCE_FIELDS: Final = frozenset(
    {"expiry_lifecycle_number", "permission_ids", "request_id"}
)
_PROPOSAL_REFERENCE_FIELDS: Final = frozenset(
    {"content_digest", "proposal_id", "proposal_type", "required_evaluator_ids"}
)
_GARDEN_FIELDS: Final = frozenset(
    {
        "actions",
        "environment_step",
        "environment_version",
        "inventory",
        "objective_complete",
        "plots",
    }
)
_INVENTORY_FIELDS: Final = frozenset({"harvested_fruit", "water_units"})
_PLOT_FIELDS: Final = frozenset({"fruit", "moisture", "plot_id", "stage"})
_ACTION_FIELDS: Final = frozenset(
    {"action_id", "applicable_targets", "preconditions", "version"}
)

_DISPOSITION_IDENTITY_FIELDS: Final = frozenset(
    {
        "current_state_digest",
        "dispatch_id",
        "disposition",
        "disposition_lifecycle_number",
        "disposition_schema",
        "evaluator_versions",
        "lineage_generation",
        "organism_id",
        "proposal_id",
        "protocol_version",
        "reason_code",
        "request_id",
        "response_id",
    }
)
_DISPOSITION_ENVELOPE_FIELDS: Final = frozenset(
    {
        *_DISPOSITION_IDENTITY_FIELDS,
        "authority",
        "current_state_reference",
        "disposition_id",
        "event_sequence",
        "parent_event_sequences",
    }
)

_TYPE_EVALUATORS: Final = {
    "action_candidate": [
        "action-schema-v1",
        "current-state-v1",
        "permission-v1",
    ],
    "abstain": ["abstain-policy-v1", "current-state-v1"],
    "defer": ["current-state-v1", "defer-policy-v1"],
}

_DISPOSITION_REASON_PAIRS: Final = frozenset(
    {
        ("accepted", "required_evaluators_passed"),
        ("rejected", "action_not_applicable_current_state"),
        ("accepted", "no_supported_action_confirmed"),
        ("clarification_requested", "proposal_contradicts_current_state"),
        ("deferred", "await_state_change"),
        ("rejected", "expired"),
    }
)


def _exact_fields(value: object, fields: frozenset[str], *, context: str) -> dict:
    if not isinstance(value, dict):
        raise DispositionValidationError(f"{context} must be an object")
    actual = frozenset(value)
    if actual != fields:
        raise DispositionValidationError(
            f"{context} field set mismatch: "
            f"missing={sorted(fields - actual)!r}, extra={sorted(actual - fields)!r}"
        )
    return value


def _integer(value: object, *, context: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise DispositionValidationError(
            f"{context} must be an integer greater than or equal to {minimum}"
        )
    return value


def _identifier(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _IDENTIFIER_RE.fullmatch(value) is None:
        raise DispositionValidationError(f"{context} is not a protected identifier")
    return value


def _digest(value: object, *, context: str) -> str:
    if not isinstance(value, str) or _DIGEST_RE.fullmatch(value) is None:
        raise DispositionValidationError(f"{context} is not a lowercase SHA-256 digest")
    return value


def _digest_identifier(value: object, prefix: str, *, context: str) -> str:
    if not isinstance(value, str) or _DIGEST_ID_RE.fullmatch(value) is None:
        raise DispositionValidationError(f"{context} is not a protected digest identifier")
    if not value.startswith(prefix + ":"):
        raise DispositionValidationError(f"{context} has the wrong identifier prefix")
    return value


def _string_list(
    value: object,
    *,
    context: str,
    nonempty: bool = False,
    sorted_unique: bool = False,
) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value):
        suffix = "nonempty " if nonempty else ""
        raise DispositionValidationError(f"{context} must be a {suffix}string array")
    items: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise DispositionValidationError(f"{context} must contain only strings")
        items.append(item)
    if sorted_unique and items != sorted(set(items)):
        raise DispositionValidationError(f"{context} must be sorted unique")
    return items


def _validate_garden_observation(value: object) -> dict[str, object]:
    garden = _exact_fields(value, _GARDEN_FIELDS, context="current garden observation")
    if garden["environment_version"] != "seed-garden-v1":
        raise DispositionValidationError("current garden environment version is not exact")
    _integer(garden["environment_step"], context="current garden environment step")
    if not isinstance(garden["objective_complete"], bool):
        raise DispositionValidationError("current garden objective flag must be boolean")

    inventory = _exact_fields(
        garden["inventory"],
        _INVENTORY_FIELDS,
        context="current garden inventory",
    )
    _integer(inventory["water_units"], context="current garden water units")
    _integer(inventory["harvested_fruit"], context="current garden harvested fruit")

    plots = garden["plots"]
    if not isinstance(plots, list) or not plots:
        raise DispositionValidationError("current garden plots must be a nonempty array")
    plot_ids: list[str] = []
    for raw_plot in plots:
        plot = _exact_fields(raw_plot, _PLOT_FIELDS, context="current garden plot")
        plot_ids.append(_identifier(plot["plot_id"], context="current garden plot ID"))
        _identifier(plot["stage"], context="current garden plot stage")
        _integer(plot["moisture"], context="current garden plot moisture")
        _integer(plot["fruit"], context="current garden plot fruit")
    if plot_ids != sorted(set(plot_ids)):
        raise DispositionValidationError("current garden plots must be sorted unique")

    actions = garden["actions"]
    if not isinstance(actions, list) or len(actions) != 2:
        raise DispositionValidationError("current garden actions must contain two actions")
    action_ids: list[str] = []
    for raw_action in actions:
        action = _exact_fields(raw_action, _ACTION_FIELDS, context="current garden action")
        action_ids.append(_identifier(action["action_id"], context="current action ID"))
        if _integer(action["version"], context="current action version", minimum=1) != 1:
            raise DispositionValidationError("current action version must equal 1")
        _string_list(
            action["preconditions"],
            context="current action preconditions",
            nonempty=True,
        )
        targets = _string_list(
            action["applicable_targets"],
            context="current action applicable targets",
            sorted_unique=True,
        )
        for target in targets:
            _identifier(target, context="current action target")
    if action_ids != ["water_plot", "harvest_plot"]:
        raise DispositionValidationError("current garden action order is not exact")

    canonical_json_bytes(garden)
    return deepcopy(garden)


def validate_current_state_identity(value: object) -> dict[str, object]:
    """Validate ADR 0010's complete current-state digest preimage."""

    state = _exact_fields(value, _CURRENT_STATE_FIELDS, context="current-state identity")
    if state["current_state_schema"] != CURRENT_STATE_SCHEMA:
        raise DispositionValidationError("current-state schema is not exact")
    if state["protocol_version"] != 1 or isinstance(state["protocol_version"], bool):
        raise DispositionValidationError("current-state protocol version must equal 1")
    if state["configuration_version"] != "phase2-fixture-v1":
        raise DispositionValidationError("current-state configuration version is not exact")
    if state["budget_config_version"] != "phase1-v1":
        raise DispositionValidationError("current-state budget version is not exact")
    _identifier(state["organism_id"], context="current-state organism ID")
    _integer(state["lineage_generation"], context="current-state lineage")
    _integer(
        state["considering_lifecycle_number"],
        context="current-state considering lifecycle",
        minimum=1,
    )
    if state["organism_status"] != "sleeping":
        raise DispositionValidationError("current-state organism status must equal sleeping")
    _integer(state["consecutive_failures"], context="current-state failure streak")
    _identifier(
        state["latest_stable_checkpoint_id"],
        context="current-state latest checkpoint ID",
    )
    latest_sequence = _integer(
        state["latest_stable_event_sequence"],
        context="current-state latest stable event sequence",
        minimum=1,
    )
    if latest_sequence < 1:
        raise DispositionValidationError("current-state latest event sequence is invalid")
    _validate_garden_observation(state["garden_observation"])

    request = _exact_fields(
        state["request_reference"],
        _REQUEST_REFERENCE_FIELDS,
        context="current-state request reference",
    )
    _integer(request["expiry_lifecycle_number"], context="current-state request expiry")
    _digest_identifier(
        request["request_id"],
        "consultation-request",
        context="current-state request ID",
    )
    permissions = _string_list(
        request["permission_ids"],
        context="current-state permission IDs",
        nonempty=True,
        sorted_unique=True,
    )
    for permission in permissions:
        _identifier(permission, context="current-state permission ID")

    proposal = _exact_fields(
        state["proposal_reference"],
        _PROPOSAL_REFERENCE_FIELDS,
        context="current-state proposal reference",
    )
    _digest(proposal["content_digest"], context="current-state proposal digest")
    _digest_identifier(
        proposal["proposal_id"],
        "consultation-proposal",
        context="current-state proposal ID",
    )
    proposal_type = proposal["proposal_type"]
    if proposal_type not in _TYPE_EVALUATORS:
        raise DispositionValidationError("current-state proposal type is not supported")
    if proposal["required_evaluator_ids"] != _TYPE_EVALUATORS[proposal_type]:
        raise DispositionValidationError("current-state proposal evaluator set is not exact")

    canonical_json_bytes(state)
    return deepcopy(state)


def current_state_digest(value: object) -> str:
    validated = validate_current_state_identity(value)
    return protocol_digest_hex("current-state-reference", validated)


def validate_disposition_identity(
    value: object,
    *,
    current_state_reference: object,
) -> dict[str, object]:
    """Validate ADR 0010's exact disposition-ID digest preimage."""

    state = validate_current_state_identity(current_state_reference)
    identity = _exact_fields(
        value,
        _DISPOSITION_IDENTITY_FIELDS,
        context="disposition identity",
    )
    if identity["disposition_schema"] != DISPOSITION_SCHEMA:
        raise DispositionValidationError("disposition schema is not exact")
    if identity["protocol_version"] != 1 or isinstance(identity["protocol_version"], bool):
        raise DispositionValidationError("disposition protocol version must equal 1")
    if identity["organism_id"] != state["organism_id"]:
        raise DispositionValidationError("disposition organism linkage does not match")
    if identity["lineage_generation"] != state["lineage_generation"]:
        raise DispositionValidationError("disposition lineage linkage does not match")
    if identity["disposition_lifecycle_number"] != state["considering_lifecycle_number"]:
        raise DispositionValidationError("disposition lifecycle does not match current state")
    if identity["request_id"] != state["request_reference"]["request_id"]:
        raise DispositionValidationError("disposition request linkage does not match")
    if identity["proposal_id"] != state["proposal_reference"]["proposal_id"]:
        raise DispositionValidationError("disposition proposal linkage does not match")
    _digest_identifier(
        identity["dispatch_id"],
        "consultation-dispatch",
        context="disposition dispatch ID",
    )
    _digest_identifier(
        identity["response_id"],
        "consultation-response",
        context="disposition response ID",
    )
    _digest_identifier(
        identity["proposal_id"],
        "consultation-proposal",
        context="disposition proposal ID",
    )
    digest = _digest(identity["current_state_digest"], context="disposition current-state digest")
    if digest != current_state_digest(state):
        raise DispositionValidationError("disposition current-state digest does not match")
    if identity["evaluator_versions"] != state["proposal_reference"]["required_evaluator_ids"]:
        raise DispositionValidationError("disposition evaluator versions do not match")
    pair = (identity["disposition"], identity["reason_code"])
    if pair not in _DISPOSITION_REASON_PAIRS:
        raise DispositionValidationError("disposition/reason combination is not supported")
    canonical_json_bytes(identity)
    return deepcopy(identity)


def disposition_id_from_identity(
    identity: object,
    *,
    current_state_reference: object,
) -> str:
    validated = validate_disposition_identity(
        identity,
        current_state_reference=current_state_reference,
    )
    return "consultation-disposition:" + protocol_digest_hex("disposition-id", validated)


def finalize_disposition(
    identity: object,
    *,
    current_state_reference: object,
    event_sequence: int,
    parent_event_sequences: object,
) -> dict[str, object]:
    state = validate_current_state_identity(current_state_reference)
    validated = validate_disposition_identity(
        identity,
        current_state_reference=state,
    )
    final = {
        **validated,
        "authority": {
            "source": DISPOSITION_SOURCE,
            "writer_category": "organism",
        },
        "current_state_reference": state,
        "disposition_id": disposition_id_from_identity(
            validated,
            current_state_reference=state,
        ),
        "event_sequence": event_sequence,
        "parent_event_sequences": deepcopy(parent_event_sequences),
    }
    return validate_disposition_envelope(final)


def validate_disposition_envelope(value: object) -> dict[str, object]:
    envelope = _exact_fields(
        value,
        _DISPOSITION_ENVELOPE_FIELDS,
        context="disposition envelope",
    )
    state = validate_current_state_identity(envelope["current_state_reference"])
    identity = {
        key: deepcopy(envelope[key])
        for key in _DISPOSITION_IDENTITY_FIELDS
    }
    validated_identity = validate_disposition_identity(
        identity,
        current_state_reference=state,
    )
    authority = _exact_fields(
        envelope["authority"],
        frozenset({"source", "writer_category"}),
        context="disposition authority",
    )
    if authority != {
        "source": DISPOSITION_SOURCE,
        "writer_category": "organism",
    }:
        raise DispositionValidationError("disposition authority is not exact")
    disposition_id = _digest_identifier(
        envelope["disposition_id"],
        "consultation-disposition",
        context="disposition ID",
    )
    expected = disposition_id_from_identity(
        validated_identity,
        current_state_reference=state,
    )
    if disposition_id != expected:
        raise DispositionValidationError("disposition ID does not match identity")
    event_sequence = _integer(
        envelope["event_sequence"],
        context="disposition event sequence",
        minimum=1,
    )
    parents = envelope["parent_event_sequences"]
    if not isinstance(parents, list) or len(parents) != 3:
        raise DispositionValidationError("disposition parents must contain exactly three events")
    parent_values = [
        _integer(item, context="disposition parent event sequence", minimum=1)
        for item in parents
    ]
    if parent_values != sorted(set(parent_values)):
        raise DispositionValidationError("disposition parents must be sorted unique")
    if any(parent >= event_sequence for parent in parent_values):
        raise DispositionValidationError("disposition parents must precede the event")
    if state["latest_stable_event_sequence"] not in parent_values:
        raise DispositionValidationError("disposition latest stable boundary is not a parent")
    canonical_json_bytes(envelope)
    return deepcopy(envelope)


__all__ = [
    "CURRENT_STATE_SCHEMA",
    "DISPOSITION_EVENT_TYPE",
    "DISPOSITION_LEDGER_EVENT_TYPE",
    "DISPOSITION_SCHEMA",
    "DISPOSITION_SOURCE",
    "DISPOSITION_WORK_CLASS",
    "DispositionValidationError",
    "current_state_digest",
    "disposition_id_from_identity",
    "finalize_disposition",
    "validate_current_state_identity",
    "validate_disposition_envelope",
    "validate_disposition_identity",
]
