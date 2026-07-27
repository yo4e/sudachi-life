"""Bounded schema-v2 fixture consultation-request construction."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Callable

from .constants import BUDGET_CONFIG_VERSION
from .errors import SchemaValidationError
from .phase2_schema import (
    CONSULTATION_PROTOCOL_VERSION,
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
    consultation_configuration_json,
)

REQUEST_SCHEMA = "sudachi.consultation.request/v1"
REQUEST_SOURCE = "organism:consultation.request"
REQUEST_POLICY_VERSION = "phase1-fixed-policy-v1"
REQUESTED_PROPOSAL_TYPES = ("abstain", "action_candidate", "defer")
OBJECTIVE_ID = "seed-garden.harvest-fruit/v1"
REQUEST_ID_PREFIX = "consultation-request:"
REQUEST_ID_DOMAIN = b"sudachi.consultation/v1\nrequest-id\n"

_AppendEvent = Callable[..., int]


@dataclass(frozen=True, slots=True)
class ConsultationRequestResult:
    created: bool
    reason: str | None
    request_id: str | None
    event_sequence: int | None
    canonical_size_bytes: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "created": self.created,
            "reason": self.reason,
            "request_id": self.request_id,
            "event_sequence": self.event_sequence,
            "canonical_size_bytes": self.canonical_size_bytes,
        }


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _canonical_text(value: object) -> str:
    return _canonical_bytes(value).decode("utf-8")


def _sha256_canonical(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _request_id(identity: dict[str, object]) -> str:
    return REQUEST_ID_PREFIX + hashlib.sha256(
        REQUEST_ID_DOMAIN + _canonical_bytes(identity)
    ).hexdigest()


def _configuration_limits(
    connection: sqlite3.Connection,
) -> tuple[str | None, dict[str, int] | None]:
    schema_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if schema_version != PHASE2_SCHEMA_VERSION:
        return None, None
    row = connection.execute(
        "SELECT configuration_version, configuration_json "
        "FROM consultation_configuration WHERE singleton_id=1"
    ).fetchone()
    if row is None:
        raise SchemaValidationError("protected consultation configuration is missing")
    version = str(row["configuration_version"])
    if version != FIXTURE_CONFIGURATION_VERSION:
        return version, None
    expected = consultation_configuration_json(version)
    if row["configuration_json"] != expected:
        raise SchemaValidationError("protected consultation configuration changed")
    decoded = json.loads(str(row["configuration_json"]))
    limits = decoded.get("limits")
    if not isinstance(limits, dict):
        raise SchemaValidationError("consultation limits are missing")
    return version, {str(name): int(value) for name, value in limits.items()}


def _current_lifecycle_payload(
    connection: sqlite3.Connection,
    *,
    lineage_generation: int,
    lifecycle_number: int,
    event_type: str,
) -> tuple[int, dict[str, object]] | None:
    rows = connection.execute(
        "SELECT event_sequence, payload_json FROM event "
        "WHERE lineage_generation=? AND lifecycle_number=? AND event_type=? "
        "ORDER BY event_sequence",
        (lineage_generation, lifecycle_number, event_type),
    ).fetchall()
    if not rows:
        return None
    if len(rows) != 1:
        raise SchemaValidationError(
            f"current lifecycle has {len(rows)} {event_type!r} events"
        )
    try:
        payload = json.loads(str(rows[0]["payload_json"]))
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(
            f"current lifecycle {event_type!r} payload is invalid"
        ) from exc
    if not isinstance(payload, dict):
        raise SchemaValidationError(
            f"current lifecycle {event_type!r} payload is not an object"
        )
    return int(rows[0]["event_sequence"]), payload


def _has_outstanding_request(
    connection: sqlite3.Connection,
    *,
    organism_id: str,
    lineage_generation: int,
    lifecycle_number: int,
) -> bool:
    row = connection.execute(
        """
        SELECT 1
        FROM consultation_request AS request
        LEFT JOIN consultation_dispatch_terminal AS terminal
          ON terminal.request_id = request.request_id
        LEFT JOIN consultation_response AS response
          ON response.request_id = request.request_id
        LEFT JOIN consultation_proposal AS proposal
          ON proposal.request_id = request.request_id
        LEFT JOIN consultation_disposition AS disposition
          ON disposition.proposal_id = proposal.proposal_id
        WHERE request.organism_id = ?
          AND request.lineage_generation = ?
          AND request.expiry_lifecycle_number >= ?
          AND terminal.terminal_id IS NULL
          AND (response.response_id IS NULL OR response.status != 'unavailable')
          AND disposition.disposition_id IS NULL
        LIMIT 1
        """,
        (organism_id, lineage_generation, lifecycle_number),
    ).fetchone()
    return row is not None


def maybe_create_fixture_request(
    connection: sqlite3.Connection,
    *,
    runtime_root: Path,
    organism_id: str,
    lineage_generation: int,
    lifecycle_number: int,
    wall_time_utc_us: int,
    checkpoint_payload: dict[str, Any],
    budget_snapshot: dict[str, Any] | None,
    append_event: _AppendEvent,
) -> ConsultationRequestResult | None:
    """Create one request after the unchanged Phase 1 core, or create nothing."""

    del runtime_root  # Reserved for the storage-safe extension in Slice 37a2.
    configuration_version, limits = _configuration_limits(connection)
    if configuration_version != FIXTURE_CONFIGURATION_VERSION or limits is None:
        return None
    if checkpoint_payload.get("final_status") == "maintenance_required":
        return None
    if budget_snapshot is None:
        raise SchemaValidationError("request extension has no pre-creation budget snapshot")

    decision_event = _current_lifecycle_payload(
        connection,
        lineage_generation=lineage_generation,
        lifecycle_number=lifecycle_number,
        event_type="action_abstained",
    )
    if decision_event is None:
        return None
    _decision_sequence, decision_payload = decision_event
    if decision_payload.get("reason") != "no_applicable_action":
        return None

    observation_event = _current_lifecycle_payload(
        connection,
        lineage_generation=lineage_generation,
        lifecycle_number=lifecycle_number,
        event_type="observation_created",
    )
    if observation_event is None:
        raise SchemaValidationError("request wake has no current observation")
    observation_event_sequence, observation = observation_event
    if bool(observation.get("objective_complete")):
        raise SchemaValidationError(
            "no-applicable-action request cannot reference a complete objective"
        )
    inventory = observation.get("inventory")
    if not isinstance(inventory, dict) or "harvested_fruit" not in inventory:
        raise SchemaValidationError("request observation inventory is invalid")

    request_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM consultation_request "
            "WHERE organism_id=? AND lineage_generation=?",
            (organism_id, lineage_generation),
        ).fetchone()[0]
    )
    if request_count >= int(limits["requests_per_lineage"]):
        return None
    if _has_outstanding_request(
        connection,
        organism_id=organism_id,
        lineage_generation=lineage_generation,
        lifecycle_number=lifecycle_number,
    ):
        return None

    request_ordinal = request_count + 1
    allowed_action_ids = tuple(
        str(row[0])
        for row in connection.execute(
            "SELECT action_id FROM action_definition "
            "WHERE protected=1 ORDER BY action_id"
        ).fetchall()
    )
    permission_ids = tuple(
        f"garden.action.execute:{action_id}" for action_id in allowed_action_ids
    )
    objective_identity = {
        "environment_version": observation["environment_version"],
        "harvested_fruit": inventory["harvested_fruit"],
        "objective_complete": observation["objective_complete"],
        "objective_id": OBJECTIVE_ID,
    }
    observation_digest = _sha256_canonical(observation)
    objective_digest = _sha256_canonical(objective_identity)
    expiry_lifecycle_number = lifecycle_number + 2

    identity: dict[str, object] = {
        "allowed_action_ids": list(allowed_action_ids),
        "budget_config_version": BUDGET_CONFIG_VERSION,
        "configuration_version": configuration_version,
        "expiry_lifecycle_number": expiry_lifecycle_number,
        "lineage_generation": lineage_generation,
        "lifecycle_number": lifecycle_number,
        "objective_digest": objective_digest,
        "observation_digest": observation_digest,
        "organism_id": organism_id,
        "permission_ids": list(permission_ids),
        "policy_version": REQUEST_POLICY_VERSION,
        "protocol_version": CONSULTATION_PROTOCOL_VERSION,
        "reason_code": "no_applicable_action",
        "request_ordinal": request_ordinal,
        "request_schema": REQUEST_SCHEMA,
        "requested_proposal_types": list(REQUESTED_PROPOSAL_TYPES),
    }
    request_id = _request_id(identity)
    event_sequence = int(
        connection.execute(
            "SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM event"
        ).fetchone()[0]
    )
    parent_event_sequences = [
        int(row[0])
        for row in connection.execute(
            "SELECT event_sequence FROM event "
            "WHERE lineage_generation=? AND lifecycle_number=? "
            "ORDER BY event_sequence",
            (lineage_generation, lifecycle_number),
        ).fetchall()
    ]
    envelope: dict[str, object] = {
        "allowed_action_ids": list(allowed_action_ids),
        "authority": {
            "source": REQUEST_SOURCE,
            "writer_category": "organism",
        },
        "budget_config_version": BUDGET_CONFIG_VERSION,
        "budget_snapshot": budget_snapshot,
        "configuration_version": configuration_version,
        "event_sequence": event_sequence,
        "expiry_lifecycle_number": expiry_lifecycle_number,
        "lineage_generation": lineage_generation,
        "lifecycle_number": lifecycle_number,
        "objective_reference": {
            "digest": objective_digest,
            "objective_id": OBJECTIVE_ID,
        },
        "observation_reference": {
            "digest": observation_digest,
            "event_sequence": observation_event_sequence,
        },
        "organism_id": organism_id,
        "parent_event_sequences": parent_event_sequences,
        "permission_ids": list(permission_ids),
        "policy_version": REQUEST_POLICY_VERSION,
        "protocol_version": CONSULTATION_PROTOCOL_VERSION,
        "reason_code": "no_applicable_action",
        "request_id": request_id,
        "request_ordinal": request_ordinal,
        "request_schema": REQUEST_SCHEMA,
        "requested_proposal_types": list(REQUESTED_PROPOSAL_TYPES),
    }
    envelope_bytes = _canonical_bytes(envelope)
    canonical_size_bytes = len(envelope_bytes)
    if canonical_size_bytes > int(limits["request_envelope_bytes"]):
        return ConsultationRequestResult(
            created=False,
            reason="consultation_request_not_created_storage_budget",
            request_id=None,
            event_sequence=None,
            canonical_size_bytes=None,
        )

    connection.execute("SAVEPOINT consultation_request_extension")
    try:
        inserted_event_sequence = append_event(
            connection,
            organism_id=organism_id,
            lineage_generation=lineage_generation,
            lifecycle_number=lifecycle_number,
            wall_time_utc_us=wall_time_utc_us,
            event_type="consultation_request_created",
            source=REQUEST_SOURCE,
            payload={
                "canonical_size_bytes": canonical_size_bytes,
                "request": envelope,
            },
        )
        if inserted_event_sequence != event_sequence:
            raise SchemaValidationError(
                "request event sequence changed during atomic extension"
            )
        connection.execute(
            """
            INSERT INTO consultation_request (
                request_id, organism_id, lineage_generation, request_ordinal,
                lifecycle_number, event_sequence, expiry_lifecycle_number,
                configuration_version, envelope_json, canonical_size_bytes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                organism_id,
                lineage_generation,
                request_ordinal,
                lifecycle_number,
                event_sequence,
                expiry_lifecycle_number,
                configuration_version,
                _canonical_text(envelope),
                canonical_size_bytes,
            ),
        )
        connection.execute("RELEASE SAVEPOINT consultation_request_extension")
    except Exception:
        connection.execute("ROLLBACK TO SAVEPOINT consultation_request_extension")
        connection.execute("RELEASE SAVEPOINT consultation_request_extension")
        raise

    return ConsultationRequestResult(
        created=True,
        reason=None,
        request_id=request_id,
        event_sequence=event_sequence,
        canonical_size_bytes=canonical_size_bytes,
    )
