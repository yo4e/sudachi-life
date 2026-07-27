from __future__ import annotations

import hashlib
from copy import deepcopy

import pytest

from sudachi_life.phase2_protocol import (
    ProtocolValidationError,
    canonical_json_bytes,
    protocol_digest_hex,
    request_id_from_identity,
    request_identity_from_envelope,
    validate_request_envelope,
)


DOMAIN = b"sudachi.consultation/v1\n"


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


def _identity() -> dict[str, object]:
    return {
        "allowed_action_ids": ["harvest_plot", "water_plot"],
        "budget_config_version": "phase1-v1",
        "configuration_version": "phase2-fixture-v1",
        "expiry_lifecycle_number": 3,
        "lineage_generation": 0,
        "lifecycle_number": 1,
        "objective_digest": "1" * 64,
        "observation_digest": "2" * 64,
        "organism_id": "request-schema",
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


def _envelope() -> dict[str, object]:
    identity = _identity()
    return {
        "allowed_action_ids": identity["allowed_action_ids"],
        "authority": {
            "source": "organism:consultation.request",
            "writer_category": "organism",
        },
        "budget_config_version": identity["budget_config_version"],
        "budget_snapshot": _budget_snapshot(),
        "configuration_version": identity["configuration_version"],
        "event_sequence": 12,
        "expiry_lifecycle_number": identity["expiry_lifecycle_number"],
        "lineage_generation": identity["lineage_generation"],
        "lifecycle_number": identity["lifecycle_number"],
        "objective_reference": {
            "digest": identity["objective_digest"],
            "objective_id": "seed-garden.harvest-fruit/v1",
        },
        "observation_reference": {
            "digest": identity["observation_digest"],
            "event_sequence": 5,
        },
        "organism_id": identity["organism_id"],
        "parent_event_sequences": [3, 4, 5, 6, 7, 8, 9, 10, 11],
        "permission_ids": identity["permission_ids"],
        "policy_version": identity["policy_version"],
        "protocol_version": identity["protocol_version"],
        "reason_code": identity["reason_code"],
        "request_id": request_id_from_identity(identity),
        "request_ordinal": identity["request_ordinal"],
        "request_schema": identity["request_schema"],
        "requested_proposal_types": identity["requested_proposal_types"],
    }


def test_canonical_json_and_domain_digest_have_exact_bytes() -> None:
    value = {"z": [3, 1], "a": {"b": "text", "a": 2}}
    expected = b'{"a":{"a":2,"b":"text"},"z":[3,1]}'
    assert canonical_json_bytes(value) == expected
    assert protocol_digest_hex("request-id", value) == hashlib.sha256(
        DOMAIN + b"request-id\n" + expected
    ).hexdigest()


@pytest.mark.parametrize(
    "value,match",
    [
        ({"value": None}, "null"),
        ({"value": 1.5}, "floating"),
        ({1: "value"}, "string keys"),
        ({"value": "e\u0301"}, "NFC"),
    ],
)
def test_canonical_json_rejects_noncanonical_values(
    value: object,
    match: str,
) -> None:
    with pytest.raises(ProtocolValidationError, match=match):
        canonical_json_bytes(value)


def test_protocol_digest_rejects_unknown_or_alternate_labels() -> None:
    value = {"value": 1}
    with pytest.raises(ProtocolValidationError, match="digest label"):
        protocol_digest_hex("Request-ID", value)
    with pytest.raises(ProtocolValidationError, match="digest label"):
        protocol_digest_hex("request-id\x00", value)


def test_request_identity_and_id_are_exact_and_event_independent() -> None:
    envelope = _envelope()
    identity = request_identity_from_envelope(envelope)
    assert identity == _identity()
    assert envelope["request_id"] == request_id_from_identity(identity)

    changed = deepcopy(envelope)
    changed["event_sequence"] = 999
    changed["parent_event_sequences"] = [3, 4, 5]
    assert request_identity_from_envelope(changed) == identity
    assert request_id_from_identity(request_identity_from_envelope(changed)) == (
        envelope["request_id"]
    )


def test_valid_request_envelope_is_canonical_and_bounded() -> None:
    envelope = _envelope()
    validated = validate_request_envelope(envelope)
    assert validated == envelope
    assert len(canonical_json_bytes(validated)) <= 16 * 1024


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda value: value.update({"free_text": "explain this"}), "field set"),
        (lambda value: value.pop("authority"), "field set"),
        (
            lambda value: value["authority"].update({"source": "caregiver"}),
            "authority",
        ),
        (
            lambda value: value.update(
                {"requested_proposal_types": ["action_candidate", "abstain", "defer"]}
            ),
            "proposal types",
        ),
        (
            lambda value: value.update(
                {"allowed_action_ids": ["water_plot", "harvest_plot"]}
            ),
            "sorted unique",
        ),
        (
            lambda value: value.update(
                {"request_schema": "sudachi.consultation.request/v2"}
            ),
            "request schema",
        ),
        (lambda value: value.update({"event_sequence": True}), "event sequence"),
        (
            lambda value: value.update({"context": {"note": "free text"}}),
            "field set",
        ),
    ],
)
def test_request_envelope_rejects_unknown_missing_spoofed_or_free_text_fields(
    mutation,
    match: str,
) -> None:
    envelope = _envelope()
    mutation(envelope)
    with pytest.raises(ProtocolValidationError, match=match):
        validate_request_envelope(envelope)
