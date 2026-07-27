"""ADR 0013 explicit bounded disposition wake."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Final

from .checkpoints import CheckpointResult, create_and_register_lifecycle_checkpoint
from .clock import Clock, RealClock
from .constants import CHECKPOINT_STORE_MAX_BYTES
from .errors import OrganismNotFoundError, SchemaValidationError, SudachiError
from .garden import build_garden_observation
from .paths import OrganismPaths
from .phase2_dispatch import validate_dispatch_envelope
from .phase2_disposition import (
    CURRENT_STATE_SCHEMA,
    DISPOSITION_EVENT_TYPE,
    DISPOSITION_LEDGER_EVENT_TYPE,
    DISPOSITION_SCHEMA,
    DISPOSITION_SOURCE,
    DISPOSITION_WORK_CLASS,
    current_state_digest,
    finalize_disposition,
    validate_disposition_envelope,
)
from .phase2_ingress_runtime import (
    INGRESS_EVENT_TYPE,
    INGRESS_SOURCE,
    completion_id_from_dispatch_id,
    receipt_id_from_package_digest,
)
from .phase2_protocol import canonical_json_bytes, validate_request_envelope
from .phase2_proposal import (
    proposal_content_digest,
    validate_proposal_envelope,
)
from .phase2_response import (
    external_package_digest,
    validate_response_envelope,
)
from .phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
    consultation_configuration_json,
)
from .runtime_storage import (
    active_database_allocated_bytes,
    checkpoint_store_bytes,
    ensure_active_database_has_wake_reserve,
    ensure_active_database_within_limit,
    ensure_checkpoint_store_within_limit,
    ensure_runtime_working_set_within_limit,
)
from .storage import connect_database, read_status, validate_canonical_state
from .wake import WakeTransaction


_DISPOSITION_FAULT_POINTS: Final = frozenset(
    {
        "after_wake_accepted",
        "after_disposition_event",
        "after_disposition_row",
        "after_budget_ledger",
        "after_checkpoint_pending",
        "before_commit",
    }
)

_DISPOSITION_LEDGER: Final = {
    "canonical_records_limit": 12,
    "canonical_records_used": 4,
    "configuration_version": FIXTURE_CONFIGURATION_VERSION,
    "phase1_budget_config_version": "phase1-v1",
    "semantic_steps_limit": 10,
    "semantic_steps_used": 8,
}


class DispositionError(SudachiError):
    """Base class for expected disposition-wake failures."""


class DispositionRejectedError(DispositionError):
    """Canonical state is not eligible for a disposition wake."""


class DispositionNoEligibleProposalError(DispositionError):
    """No current-lineage proposal remains eligible for disposition."""


class _InjectedDispositionFault(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DispositionWakeResult:
    organism_id: str
    lifecycle_number: int
    request_id: str
    dispatch_id: str
    response_id: str
    proposal_id: str
    disposition_id: str
    disposition: str
    reason_code: str
    event_sequence: int
    envelope: dict[str, object]
    current_state_reference: dict[str, object]
    outcome: dict[str, object]
    budget_ledger: dict[str, object]
    checkpoint: CheckpointResult
    status: str


@dataclass(frozen=True, slots=True)
class _LinkedProposal:
    request_row: sqlite3.Row
    dispatch_row: sqlite3.Row
    response_row: sqlite3.Row
    proposal_row: sqlite3.Row
    receipt_row: sqlite3.Row
    completion_row: sqlite3.Row
    request: dict[str, object]
    dispatch: dict[str, object]
    response: dict[str, object]
    proposal: dict[str, object]
    ingress_event_sequence: int


def _fault(protected_test_fault: str | None, point: str) -> None:
    if protected_test_fault == point:
        raise _InjectedDispositionFault(f"protected disposition fault: {point}")


def _decode_json(text: object, *, context: str) -> dict[str, object]:
    if not isinstance(text, str):
        raise DispositionRejectedError(f"{context} is not stored as text")
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DispositionRejectedError(f"{context} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise DispositionRejectedError(f"{context} must be an object")
    return value


def _require_configuration(connection: sqlite3.Connection) -> None:
    row = connection.execute(
        "SELECT protocol_version, configuration_version, configuration_json "
        "FROM consultation_configuration WHERE singleton_id=1"
    ).fetchone()
    if row is None:
        raise DispositionRejectedError("protected consultation configuration is missing")
    if int(row["protocol_version"]) != 1:
        raise DispositionRejectedError("consultation protocol version is not exact")
    if row["configuration_version"] != FIXTURE_CONFIGURATION_VERSION:
        raise DispositionRejectedError("disposition requires fixture configuration")
    if row["configuration_json"] != consultation_configuration_json(
        FIXTURE_CONFIGURATION_VERSION
    ):
        raise DispositionRejectedError("protected consultation configuration changed")


def _require_storage_capacity(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
    *,
    context: str,
) -> None:
    allocated = ensure_active_database_within_limit(connection, context=context)
    ensure_active_database_has_wake_reserve(connection, context=context)
    ensure_checkpoint_store_within_limit(paths, context=context)
    projected_checkpoint_bytes = allocated + 4096
    if checkpoint_store_bytes(paths) + projected_checkpoint_bytes > CHECKPOINT_STORE_MAX_BYTES:
        raise SchemaValidationError(
            f"{context}: checkpoint store would exceed protected Phase 1 limit"
        )
    ensure_runtime_working_set_within_limit(
        paths,
        context=context,
        additional_bytes=projected_checkpoint_bytes,
    )


def _canonical_row_envelope(
    row: sqlite3.Row,
    *,
    validator,
    context: str,
    validator_kwargs: dict[str, object] | None = None,
) -> dict[str, object]:
    decoded = _decode_json(row["envelope_json"], context=f"{context} envelope")
    try:
        envelope = validator(decoded, **(validator_kwargs or {}))
    except Exception as exc:
        raise DispositionRejectedError(str(exc)) from exc
    encoded = canonical_json_bytes(envelope)
    if row["envelope_json"] != encoded.decode("utf-8"):
        raise DispositionRejectedError(f"{context} envelope is not canonical")
    if int(row["canonical_size_bytes"]) != len(encoded):
        raise DispositionRejectedError(f"{context} canonical size mismatch")
    return envelope


def _select_proposal(
    connection: sqlite3.Connection,
    *,
    organism_id: str,
    lineage_generation: int,
) -> str:
    row = connection.execute(
        "SELECT p.proposal_id "
        "FROM consultation_proposal p "
        "JOIN consultation_response r ON r.response_id=p.response_id "
        "JOIN consultation_ingress_receipt i ON i.response_id=r.response_id "
        "WHERE p.organism_id=? AND p.lineage_generation=? "
        "AND NOT EXISTS ("
        "  SELECT 1 FROM consultation_disposition z WHERE z.proposal_id=p.proposal_id"
        ") "
        "ORDER BY i.event_sequence, p.proposal_id LIMIT 1",
        (organism_id, lineage_generation),
    ).fetchone()
    if row is None:
        raise DispositionNoEligibleProposalError(
            "no eligible current-lineage proposal is available"
        )
    return str(row["proposal_id"])


def _load_linked_proposal(
    connection: sqlite3.Connection,
    *,
    proposal_id: str,
) -> _LinkedProposal:
    proposal_row = connection.execute(
        "SELECT * FROM consultation_proposal WHERE proposal_id=?",
        (proposal_id,),
    ).fetchone()
    if proposal_row is None:
        raise DispositionRejectedError("selected proposal does not exist")
    request_row = connection.execute(
        "SELECT * FROM consultation_request WHERE request_id=?",
        (proposal_row["request_id"],),
    ).fetchone()
    dispatch_row = connection.execute(
        "SELECT * FROM consultation_dispatch WHERE dispatch_id=?",
        (proposal_row["dispatch_id"],),
    ).fetchone()
    response_row = connection.execute(
        "SELECT * FROM consultation_response WHERE response_id=?",
        (proposal_row["response_id"],),
    ).fetchone()
    receipt_row = connection.execute(
        "SELECT * FROM consultation_ingress_receipt WHERE response_id=?",
        (proposal_row["response_id"],),
    ).fetchone()
    completion_row = connection.execute(
        "SELECT * FROM consultation_cost_completion WHERE response_id=?",
        (proposal_row["response_id"],),
    ).fetchone()
    if any(
        row is None
        for row in (
            request_row,
            dispatch_row,
            response_row,
            receipt_row,
            completion_row,
        )
    ):
        raise DispositionRejectedError("selected proposal linkage is incomplete")
    assert request_row is not None
    assert dispatch_row is not None
    assert response_row is not None
    assert receipt_row is not None
    assert completion_row is not None

    request = _canonical_row_envelope(
        request_row,
        validator=validate_request_envelope,
        context="linked request",
    )
    dispatch = _canonical_row_envelope(
        dispatch_row,
        validator=validate_dispatch_envelope,
        context="linked dispatch",
        validator_kwargs={"request_envelope": request},
    )
    proposal = _canonical_row_envelope(
        proposal_row,
        validator=validate_proposal_envelope,
        context="linked proposal",
        validator_kwargs={
            "request_envelope": request,
            "fixture_case_id": dispatch["fixture_case_id"],
        },
    )
    response = _canonical_row_envelope(
        response_row,
        validator=validate_response_envelope,
        context="linked response",
        validator_kwargs={
            "request_envelope": request,
            "dispatch_envelope": dispatch,
            "proposal_envelopes": [proposal],
        },
    )

    for row, envelope, pairs, context in (
        (
            request_row,
            request,
            (
                ("request_id", "request_id"),
                ("organism_id", "organism_id"),
                ("lineage_generation", "lineage_generation"),
                ("request_ordinal", "request_ordinal"),
                ("lifecycle_number", "lifecycle_number"),
                ("event_sequence", "event_sequence"),
                ("expiry_lifecycle_number", "expiry_lifecycle_number"),
                ("configuration_version", "configuration_version"),
            ),
            "request",
        ),
        (
            dispatch_row,
            dispatch,
            (
                ("dispatch_id", "dispatch_id"),
                ("request_id", "request_id"),
                ("organism_id", "organism_id"),
                ("lineage_generation", "lineage_generation"),
                ("dispatch_ordinal", "dispatch_ordinal"),
                ("event_sequence", "event_sequence"),
                ("configuration_version", "configuration_version"),
            ),
            "dispatch",
        ),
        (
            proposal_row,
            proposal,
            (
                ("proposal_id", "proposal_id"),
                ("request_id", "request_id"),
                ("dispatch_id", "dispatch_id"),
                ("response_id", "response_id"),
                ("organism_id", "organism_id"),
                ("lineage_generation", "lineage_generation"),
                ("proposal_ordinal", "proposal_ordinal"),
                ("proposal_type", "proposal_type"),
                ("expiry_lifecycle_number", "expiry_lifecycle_number"),
            ),
            "proposal",
        ),
        (
            response_row,
            response,
            (
                ("response_id", "response_id"),
                ("request_id", "request_id"),
                ("dispatch_id", "dispatch_id"),
                ("organism_id", "organism_id"),
                ("lineage_generation", "lineage_generation"),
                ("status", "status"),
            ),
            "response",
        ),
    ):
        for column, field in pairs:
            if row[column] != envelope[field]:
                raise DispositionRejectedError(
                    f"linked {context} row/envelope mismatch at {column}"
                )

    if response["status"] != "proposals_returned":
        raise DispositionRejectedError("selected proposal response status is not exact")
    if proposal["proposal_id"] != proposal_id:
        raise DispositionRejectedError("selected proposal ID changed")
    proposal_identity = {
        key: deepcopy(value)
        for key, value in proposal.items()
        if key not in {"proposal_id", "response_id"}
    }
    expected_content_digest = proposal_content_digest(
        proposal_identity,
        request_envelope=request,
        fixture_case_id=str(dispatch["fixture_case_id"]),
    )
    if proposal_row["content_digest"] != expected_content_digest:
        raise DispositionRejectedError("selected proposal content digest mismatch")

    package = {"response": response, "proposals": [proposal]}
    package_digest = external_package_digest(
        package,
        request_envelope=request,
        dispatch_envelope=dispatch,
    )
    if response_row["package_digest"] != package_digest:
        raise DispositionRejectedError("selected response package digest mismatch")
    ingress_event_sequence = int(receipt_row["event_sequence"])
    if int(response_row["event_sequence"]) != ingress_event_sequence:
        raise DispositionRejectedError("response and receipt event linkage mismatch")
    if receipt_row["request_id"] != request["request_id"]:
        raise DispositionRejectedError("receipt request linkage mismatch")
    if receipt_row["dispatch_id"] != dispatch["dispatch_id"]:
        raise DispositionRejectedError("receipt dispatch linkage mismatch")
    if receipt_row["response_id"] != response["response_id"]:
        raise DispositionRejectedError("receipt response linkage mismatch")
    if receipt_row["package_digest"] != package_digest:
        raise DispositionRejectedError("receipt package digest mismatch")
    if receipt_row["receipt_id"] != receipt_id_from_package_digest(package_digest):
        raise DispositionRejectedError("receipt ID mismatch")
    if completion_row["completion_id"] != completion_id_from_dispatch_id(
        str(dispatch["dispatch_id"])
    ):
        raise DispositionRejectedError("completion ID mismatch")
    if completion_row["dispatch_id"] != dispatch["dispatch_id"]:
        raise DispositionRejectedError("completion dispatch linkage mismatch")
    if completion_row["response_id"] != response["response_id"]:
        raise DispositionRejectedError("completion response linkage mismatch")
    if completion_row["terminal_id"] is not None:
        raise DispositionRejectedError("response completion links a terminal")
    if int(completion_row["measured_package_bytes"]) != int(
        receipt_row["measured_package_bytes"]
    ):
        raise DispositionRejectedError("receipt and completion measured bytes mismatch")

    request_event = int(request["event_sequence"])
    dispatch_event = int(dispatch["event_sequence"])
    expected_receipt = {
        "authority": {
            "source": INGRESS_SOURCE,
            "writer_category": "administration",
        },
        "dispatch_id": dispatch["dispatch_id"],
        "event_sequence": ingress_event_sequence,
        "measured_package_bytes": int(receipt_row["measured_package_bytes"]),
        "package_digest": package_digest,
        "parent_event_sequences": [request_event, dispatch_event],
        "protocol_version": 1,
        "receipt_id": receipt_row["receipt_id"],
        "receipt_schema": "sudachi.consultation.ingress_receipt/v1",
        "request_id": request["request_id"],
        "response_id": response["response_id"],
    }
    expected_completion = {
        "completion_id": completion_row["completion_id"],
        "dispatch_id": dispatch["dispatch_id"],
        "measured_package_bytes": int(completion_row["measured_package_bytes"]),
        "response_id": response["response_id"],
    }
    ingress_event = connection.execute(
        "SELECT lineage_generation, event_type, source, payload_json FROM event "
        "WHERE event_sequence=?",
        (ingress_event_sequence,),
    ).fetchone()
    if ingress_event is None:
        raise DispositionRejectedError("selected proposal ingress event is missing")
    if ingress_event["event_type"] != INGRESS_EVENT_TYPE:
        raise DispositionRejectedError("selected proposal ingress event type mismatch")
    if ingress_event["source"] != INGRESS_SOURCE:
        raise DispositionRejectedError("selected proposal ingress event source mismatch")
    if int(ingress_event["lineage_generation"]) != int(request["lineage_generation"]):
        raise DispositionRejectedError("selected proposal ingress lineage mismatch")
    expected_payload = {
        "completion": expected_completion,
        "receipt": expected_receipt,
    }
    if ingress_event["payload_json"] != canonical_json_bytes(expected_payload).decode(
        "utf-8"
    ):
        raise DispositionRejectedError("selected proposal ingress payload mismatch")

    return _LinkedProposal(
        request_row=request_row,
        dispatch_row=dispatch_row,
        response_row=response_row,
        proposal_row=proposal_row,
        receipt_row=receipt_row,
        completion_row=completion_row,
        request=request,
        dispatch=dispatch,
        response=response,
        proposal=proposal,
        ingress_event_sequence=ingress_event_sequence,
    )


def _require_current_state(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
    *,
    organism: sqlite3.Row,
    wake_lifecycle_number: int,
    linked: _LinkedProposal,
) -> dict[str, object]:
    if int(organism["schema_version"]) != PHASE2_SCHEMA_VERSION:
        raise DispositionRejectedError("disposition requires schema-v2")
    if organism["status"] != "sleeping" or bool(organism["checkpoint_pending"]):
        raise DispositionRejectedError(
            "disposition requires sleeping status with no pending checkpoint"
        )
    if organism["maintenance_reason"] is not None:
        raise DispositionRejectedError("disposition cannot bypass maintenance")
    _require_configuration(connection)
    if linked.request["configuration_version"] != FIXTURE_CONFIGURATION_VERSION:
        raise DispositionRejectedError("linked request configuration is not exact")
    if int(linked.request["lineage_generation"]) != int(
        organism["lineage_generation"]
    ):
        raise DispositionRejectedError("selected proposal is not in the current lineage")
    if linked.request["organism_id"] != organism["organism_id"]:
        raise DispositionRejectedError("selected proposal organism linkage mismatch")

    checkpoint_id = organism["latest_stable_checkpoint_id"]
    checkpoint_sequence = int(organism["latest_stable_event_sequence"])
    if checkpoint_id is None or checkpoint_sequence < 1:
        raise DispositionRejectedError("disposition requires a stable checkpoint")
    registry = connection.execute(
        "SELECT lineage_generation, event_sequence FROM checkpoint_registry "
        "WHERE checkpoint_id=?",
        (checkpoint_id,),
    ).fetchone()
    if registry is None:
        raise DispositionRejectedError("latest stable checkpoint is not registered")
    if int(registry["lineage_generation"]) != int(organism["lineage_generation"]):
        raise DispositionRejectedError("latest stable checkpoint lineage mismatch")
    if int(registry["event_sequence"]) != checkpoint_sequence:
        raise DispositionRejectedError("latest stable checkpoint boundary mismatch")
    if not (paths.checkpoints / str(checkpoint_id)).is_dir():
        raise DispositionRejectedError("latest stable checkpoint artifact is missing")
    boundary_event = connection.execute(
        "SELECT lineage_generation, event_type FROM event WHERE event_sequence=?",
        (checkpoint_sequence,),
    ).fetchone()
    if boundary_event is None or boundary_event["event_type"] != "checkpoint_pending":
        raise DispositionRejectedError("latest stable boundary event is not exact")
    if int(boundary_event["lineage_generation"]) != int(organism["lineage_generation"]):
        raise DispositionRejectedError("latest stable boundary lineage mismatch")

    garden_observation = build_garden_observation(connection).as_dict()
    state = {
        "budget_config_version": "phase1-v1",
        "configuration_version": FIXTURE_CONFIGURATION_VERSION,
        "consecutive_failures": int(organism["consecutive_failures"]),
        "considering_lifecycle_number": wake_lifecycle_number,
        "current_state_schema": CURRENT_STATE_SCHEMA,
        "garden_observation": garden_observation,
        "latest_stable_checkpoint_id": str(checkpoint_id),
        "latest_stable_event_sequence": checkpoint_sequence,
        "lineage_generation": int(organism["lineage_generation"]),
        "organism_id": str(organism["organism_id"]),
        "organism_status": "sleeping",
        "proposal_reference": {
            "content_digest": str(linked.proposal_row["content_digest"]),
            "proposal_id": str(linked.proposal["proposal_id"]),
            "proposal_type": str(linked.proposal["proposal_type"]),
            "required_evaluator_ids": deepcopy(
                linked.proposal["required_evaluator_ids"]
            ),
        },
        "protocol_version": 1,
        "request_reference": {
            "expiry_lifecycle_number": int(
                linked.request["expiry_lifecycle_number"]
            ),
            "permission_ids": deepcopy(linked.request["permission_ids"]),
            "request_id": str(linked.request["request_id"]),
        },
    }
    current_state_digest(state)
    return state


def _evaluate_disposition(
    *,
    linked: _LinkedProposal,
    current_state: dict[str, object],
) -> tuple[str, str]:
    considering_lifecycle = int(current_state["considering_lifecycle_number"])
    expiry = int(linked.request["expiry_lifecycle_number"])
    if considering_lifecycle > expiry:
        return "rejected", "expired"

    proposal_type = str(linked.proposal["proposal_type"])
    observation = current_state["garden_observation"]
    assert isinstance(observation, dict)
    actions = observation["actions"]
    assert isinstance(actions, list)
    allowed = set(str(item) for item in linked.request["allowed_action_ids"])

    if proposal_type == "defer":
        return "deferred", "await_state_change"
    if proposal_type == "abstain":
        supported_action_exists = any(
            isinstance(action, dict)
            and action.get("action_id") in allowed
            and bool(action.get("applicable_targets"))
            for action in actions
        )
        if supported_action_exists:
            return "clarification_requested", "proposal_contradicts_current_state"
        return "accepted", "no_supported_action_confirmed"

    subject = linked.proposal["subject_reference"]
    proposed = linked.proposal["proposed_value"]
    assert isinstance(subject, dict)
    assert isinstance(proposed, dict)
    parameters = proposed["parameters"]
    assert isinstance(parameters, dict)
    action_id = str(subject["action_id"])
    plot_id = str(parameters["plot_id"])
    permission = f"garden.action.execute:{action_id}"
    if action_id not in allowed or permission not in linked.request["permission_ids"]:
        raise DispositionRejectedError("action candidate permission linkage changed")
    action = next(
        (
            item
            for item in actions
            if isinstance(item, dict) and item.get("action_id") == action_id
        ),
        None,
    )
    if action is None:
        raise DispositionRejectedError("action candidate names an unknown action")
    targets = action.get("applicable_targets")
    if not isinstance(targets, list):
        raise DispositionRejectedError("current action targets are invalid")
    if plot_id in targets:
        return "accepted", "required_evaluators_passed"
    return "rejected", "action_not_applicable_current_state"


def _append_event(
    connection: sqlite3.Connection,
    *,
    organism_id: str,
    lineage_generation: int,
    lifecycle_number: int,
    wall_time_utc_us: int,
    event_type: str,
    payload: dict[str, object],
) -> int:
    cursor = connection.execute(
        "INSERT INTO event ("
        "organism_id, lineage_generation, lifecycle_number, wall_time_utc_us, "
        "event_type, source, payload_json, schema_version, environment_version, "
        "budget_config_version"
        ") SELECT ?, ?, ?, ?, ?, ?, ?, schema_version, environment_version, "
        "budget_config_version FROM organism WHERE singleton_id=1",
        (
            organism_id,
            lineage_generation,
            lifecycle_number,
            wall_time_utc_us,
            event_type,
            DISPOSITION_SOURCE,
            canonical_json_bytes(payload).decode("utf-8"),
        ),
    )
    return int(cursor.lastrowid)


def perform_disposition_wake(
    runtime_root: Path | str,
    organism_id: str,
    *,
    clock: Clock | None = None,
    protected_test_fault: str | None = None,
    protected_test_retention_failure_after_stage: bool = False,
) -> DispositionWakeResult:
    """Consider one eligible proposal and stabilize one disposition checkpoint."""

    if protected_test_fault is not None and protected_test_fault not in _DISPOSITION_FAULT_POINTS:
        raise ValueError(f"unknown protected disposition fault: {protected_test_fault}")
    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    wake = WakeTransaction.acquire(paths)
    active_clock = clock or RealClock()
    committed = False
    try:
        organism = wake.connection.execute(
            "SELECT * FROM organism WHERE singleton_id=1"
        ).fetchone()
        if organism is None:
            raise DispositionRejectedError("canonical organism singleton is missing")
        proposal_id = _select_proposal(
            wake.connection,
            organism_id=organism_id,
            lineage_generation=int(organism["lineage_generation"]),
        )
        linked = _load_linked_proposal(
            wake.connection,
            proposal_id=proposal_id,
        )
        current_state = _require_current_state(
            wake.connection,
            paths,
            organism=organism,
            wake_lifecycle_number=wake.lifecycle_number,
            linked=linked,
        )
        _require_storage_capacity(
            wake.connection,
            paths,
            context="disposition wake preflight",
        )
        disposition, reason_code = _evaluate_disposition(
            linked=linked,
            current_state=current_state,
        )
        started = active_clock.read()

        wake_event_sequence = _append_event(
            wake.connection,
            organism_id=organism_id,
            lineage_generation=int(organism["lineage_generation"]),
            lifecycle_number=wake.lifecycle_number,
            wall_time_utc_us=started.wall_time_utc_us,
            event_type="wake_accepted",
            payload={"work_class": DISPOSITION_WORK_CLASS},
        )
        _fault(protected_test_fault, "after_wake_accepted")

        predicted_disposition_sequence = int(
            wake.connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM event"
            ).fetchone()[0]
        )
        parents = sorted(
            {
                linked.ingress_event_sequence,
                int(current_state["latest_stable_event_sequence"]),
                wake_event_sequence,
            }
        )
        if len(parents) != 3:
            raise DispositionRejectedError(
                "disposition direct parents are not three unique events"
            )
        identity = {
            "current_state_digest": current_state_digest(current_state),
            "dispatch_id": str(linked.dispatch["dispatch_id"]),
            "disposition": disposition,
            "disposition_lifecycle_number": wake.lifecycle_number,
            "disposition_schema": DISPOSITION_SCHEMA,
            "evaluator_versions": deepcopy(
                linked.proposal["required_evaluator_ids"]
            ),
            "lineage_generation": int(organism["lineage_generation"]),
            "organism_id": organism_id,
            "proposal_id": proposal_id,
            "protocol_version": 1,
            "reason_code": reason_code,
            "request_id": str(linked.request["request_id"]),
            "response_id": str(linked.response["response_id"]),
        }
        envelope = finalize_disposition(
            identity,
            current_state_reference=current_state,
            event_sequence=predicted_disposition_sequence,
            parent_event_sequences=parents,
        )
        outcome = {
            "disposition": disposition,
            "disposition_id": envelope["disposition_id"],
            "input_consumed": False,
            "proposal_id": proposal_id,
            "reason_code": reason_code,
        }
        disposition_event_sequence = _append_event(
            wake.connection,
            organism_id=organism_id,
            lineage_generation=int(organism["lineage_generation"]),
            lifecycle_number=wake.lifecycle_number,
            wall_time_utc_us=started.wall_time_utc_us,
            event_type=DISPOSITION_EVENT_TYPE,
            payload={"disposition": envelope, "outcome": outcome},
        )
        if disposition_event_sequence != predicted_disposition_sequence:
            raise DispositionRejectedError(
                "disposition event sequence prediction mismatch"
            )
        _fault(protected_test_fault, "after_disposition_event")

        validate_disposition_envelope(envelope)
        wake.connection.execute(
            "INSERT INTO consultation_disposition ("
            "disposition_id, request_id, dispatch_id, response_id, proposal_id, "
            "organism_id, lineage_generation, lifecycle_number, disposition, "
            "reason_code, event_sequence, envelope_json"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                envelope["disposition_id"],
                envelope["request_id"],
                envelope["dispatch_id"],
                envelope["response_id"],
                envelope["proposal_id"],
                envelope["organism_id"],
                envelope["lineage_generation"],
                envelope["disposition_lifecycle_number"],
                envelope["disposition"],
                envelope["reason_code"],
                disposition_event_sequence,
                canonical_json_bytes(envelope).decode("utf-8"),
            ),
        )
        _fault(protected_test_fault, "after_disposition_row")

        _append_event(
            wake.connection,
            organism_id=organism_id,
            lineage_generation=int(organism["lineage_generation"]),
            lifecycle_number=wake.lifecycle_number,
            wall_time_utc_us=started.wall_time_utc_us,
            event_type=DISPOSITION_LEDGER_EVENT_TYPE,
            payload=deepcopy(_DISPOSITION_LEDGER),
        )
        _fault(protected_test_fault, "after_budget_ledger")

        checkpoint_payload = {
            "final_status": "sleeping",
            "lifecycle_number": wake.lifecycle_number,
            "reason": "committed_disposition_wake",
        }
        checkpoint_boundary = _append_event(
            wake.connection,
            organism_id=organism_id,
            lineage_generation=int(organism["lineage_generation"]),
            lifecycle_number=wake.lifecycle_number,
            wall_time_utc_us=started.wall_time_utc_us,
            event_type="checkpoint_pending",
            payload=checkpoint_payload,
        )
        _fault(protected_test_fault, "after_checkpoint_pending")

        wake.connection.execute(
            "UPDATE organism SET lifecycle_number=?, status='checkpoint_pending', "
            "checkpoint_pending=1, pending_checkpoint_generation=lineage_generation, "
            "pending_checkpoint_event_sequence=? WHERE singleton_id=1",
            (wake.lifecycle_number, checkpoint_boundary),
        )
        validate_canonical_state(wake.connection, expect_checkpoint_pending=True)
        _require_storage_capacity(
            wake.connection,
            paths,
            context="disposition wake post-write",
        )
        _fault(protected_test_fault, "before_commit")
        wake.connection.commit()
        wake.close_committed()
        committed = True
    except (DispositionNoEligibleProposalError, DispositionRejectedError, _InjectedDispositionFault):
        wake.rollback_and_close()
        raise
    except (SchemaValidationError, sqlite3.Error, OSError, ValueError) as exc:
        wake.rollback_and_close()
        raise DispositionRejectedError(str(exc)) from exc
    except Exception:
        wake.rollback_and_close()
        raise

    if not committed:
        raise DispositionRejectedError("disposition wake did not commit")

    checkpoint = create_and_register_lifecycle_checkpoint(
        paths,
        clock=active_clock,
        protected_test_retention_failure_after_stage=(
            protected_test_retention_failure_after_stage
        ),
    )
    status = read_status(paths)
    return DispositionWakeResult(
        organism_id=organism_id,
        lifecycle_number=wake.lifecycle_number,
        request_id=str(linked.request["request_id"]),
        dispatch_id=str(linked.dispatch["dispatch_id"]),
        response_id=str(linked.response["response_id"]),
        proposal_id=proposal_id,
        disposition_id=str(envelope["disposition_id"]),
        disposition=disposition,
        reason_code=reason_code,
        event_sequence=disposition_event_sequence,
        envelope=deepcopy(envelope),
        current_state_reference=deepcopy(current_state),
        outcome=deepcopy(outcome),
        budget_ledger=deepcopy(_DISPOSITION_LEDGER),
        checkpoint=checkpoint,
        status=status.status,
    )


__all__ = [
    "DispositionError",
    "DispositionNoEligibleProposalError",
    "DispositionRejectedError",
    "DispositionWakeResult",
    "perform_disposition_wake",
]
