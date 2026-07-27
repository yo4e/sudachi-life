"""ADR 0012 package ingress, terminalization, and interruption reconciliation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Final

from .clock import Clock, RealClock
from .constants import BUDGET_CONFIG_VERSION, ENVIRONMENT_VERSION
from .errors import OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .phase2_dispatch import DISPATCH_SOURCE, validate_dispatch_envelope
from .phase2_protocol import canonical_json_bytes, validate_request_envelope
from .phase2_proposal import proposal_content_digest
from .phase2_response import (
    external_package_digest,
    validate_external_package,
)
from .phase2_schema import FIXTURE_CONFIGURATION_VERSION, PHASE2_SCHEMA_VERSION
from .runtime_storage import (
    ensure_active_database_has_wake_reserve,
    ensure_active_database_within_limit,
    ensure_checkpoint_store_within_limit,
    ensure_runtime_working_set_within_limit,
)
from .storage import connect_database, validate_canonical_state


INGRESS_EVENT_TYPE: Final = "consultation_response_ingressed"
INGRESS_SOURCE: Final = "administration:consultation.response_ingress"
INGRESS_RECEIPT_SCHEMA: Final = "sudachi.consultation.ingress_receipt/v1"
TERMINAL_EVENT_TYPE: Final = "consultation_dispatch_terminalized"
TERMINAL_SOURCE: Final = "administration:consultation.dispatch_terminal"
TERMINAL_SCHEMA: Final = "sudachi.consultation.dispatch_terminal/v1"

_COMPLETION_ID_PREFIX: Final = "consultation-cost-completion:"
_RECEIPT_ID_PREFIX: Final = "consultation-ingress-receipt:"
_TERMINAL_ID_PREFIX: Final = "consultation-dispatch-terminal:"
_REJECTED_PACKAGE_DOMAIN: Final = b"sudachi.consultation/v1\nrejected-package-bytes\n"

_DISPATCH_ID_RE: Final = re.compile(r"^consultation-dispatch:([0-9a-f]{64})$")
_PACKAGE_DIGEST_RE: Final = re.compile(r"^[0-9a-f]{64}$")
_INGRESS_FAULT_POINTS: Final = frozenset(
    {
        "after_event",
        "after_response",
        "after_proposal",
        "after_receipt",
        "after_completion",
        "before_commit",
    }
)
_TERMINAL_FAULT_POINTS: Final = frozenset(
    {"after_event", "after_terminal", "after_completion", "before_commit"}
)
_TERMINAL_REASONS: Final = frozenset(
    {"dispatch_interrupted", "fixture_output_invalid", "expired_before_ingress"}
)
_LOGICAL_PAYLOAD_LIMIT_BYTES: Final = 64 * 1024

_RECEIPT_FIELDS: Final = frozenset(
    {
        "authority",
        "dispatch_id",
        "event_sequence",
        "measured_package_bytes",
        "package_digest",
        "parent_event_sequences",
        "protocol_version",
        "receipt_id",
        "receipt_schema",
        "request_id",
        "response_id",
    }
)
_TERMINAL_FIELDS: Final = frozenset(
    {
        "authority",
        "dispatch_id",
        "event_sequence",
        "lineage_generation",
        "organism_id",
        "parent_event_sequences",
        "protocol_version",
        "reason_code",
        "rejected_package_digest",
        "rejected_package_size_bytes",
        "request_id",
        "terminal_id",
        "terminal_schema",
    }
)


class IngressError(SudachiError):
    """Base class for expected package-ingress failures."""


class IngressBusyError(IngressError):
    """Raised when fail-fast ingress ownership is unavailable."""


class IngressRejectedError(IngressError):
    """Raised when package bytes or canonical state are not ingress-eligible."""


class TerminalizationError(SudachiError):
    """Base class for expected dispatch-terminalization failures."""


class TerminalizationBusyError(TerminalizationError):
    """Raised when fail-fast terminal ownership is unavailable."""


class TerminalizationRejectedError(TerminalizationError):
    """Raised when a terminal outcome is not eligible or conflicts."""


class _InjectedIngressFault(RuntimeError):
    pass


class _InjectedTerminalFault(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class IngressResult:
    created: bool
    organism_id: str
    request_id: str
    dispatch_id: str
    response_id: str
    receipt_id: str
    completion_id: str
    event_sequence: int
    package_digest: str
    measured_package_bytes: int
    status: str
    proposal_id: str | None


@dataclass(frozen=True, slots=True)
class TerminalizationResult:
    created: bool
    organism_id: str
    request_id: str
    dispatch_id: str
    terminal_id: str
    completion_id: str
    event_sequence: int
    reason_code: str
    rejected_package_digest: str | None
    rejected_package_size_bytes: int | None
    measured_package_bytes: int


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    text = str(exc).lower()
    return "locked" in text or "busy" in text


def _integer(value: object, *, context: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise IngressRejectedError(
            f"{context} must be an integer greater than or equal to {minimum}"
        )
    return value


def _exact_fields(value: object, expected: frozenset[str], *, context: str) -> dict:
    if not isinstance(value, dict):
        raise IngressRejectedError(f"{context} must be an object")
    actual = frozenset(value)
    if actual != expected:
        raise IngressRejectedError(
            f"{context} field set mismatch: "
            f"missing={sorted(expected - actual)!r}, extra={sorted(actual - expected)!r}"
        )
    return value


def _dispatch_digest(dispatch_id: object) -> str:
    if not isinstance(dispatch_id, str):
        raise IngressRejectedError("dispatch ID is not an exact digest identifier")
    match = _DISPATCH_ID_RE.fullmatch(dispatch_id)
    if match is None:
        raise IngressRejectedError("dispatch ID is not an exact digest identifier")
    return match.group(1)


def completion_id_from_dispatch_id(dispatch_id: object) -> str:
    return _COMPLETION_ID_PREFIX + _dispatch_digest(dispatch_id)


def terminal_id_from_dispatch_id(dispatch_id: object) -> str:
    return _TERMINAL_ID_PREFIX + _dispatch_digest(dispatch_id)


def receipt_id_from_package_digest(package_digest: object) -> str:
    if not isinstance(package_digest, str) or _PACKAGE_DIGEST_RE.fullmatch(package_digest) is None:
        raise IngressRejectedError("package digest is not a lowercase SHA-256 digest")
    return _RECEIPT_ID_PREFIX + package_digest


def rejected_package_digest(raw_package_bytes: object) -> str:
    if not isinstance(raw_package_bytes, bytes):
        raise IngressRejectedError("rejected package bytes must be bytes")
    return hashlib.sha256(_REJECTED_PACKAGE_DOMAIN + raw_package_bytes).hexdigest()


def _load_request(
    connection: sqlite3.Connection,
    request_id: str,
) -> tuple[sqlite3.Row, dict[str, object]]:
    row = connection.execute(
        "SELECT * FROM consultation_request WHERE request_id=?",
        (request_id,),
    ).fetchone()
    if row is None:
        raise IngressRejectedError("linked request does not exist")
    try:
        decoded = json.loads(str(row["envelope_json"]))
    except (TypeError, json.JSONDecodeError) as exc:
        raise IngressRejectedError("linked request envelope is not valid JSON") from exc
    envelope = validate_request_envelope(decoded)
    encoded = canonical_json_bytes(envelope)
    if encoded.decode("utf-8") != row["envelope_json"]:
        raise IngressRejectedError("linked request envelope is not canonical")
    if int(row["canonical_size_bytes"]) != len(encoded):
        raise IngressRejectedError("linked request canonical size mismatch")
    for column, field in (
        ("request_id", "request_id"),
        ("organism_id", "organism_id"),
        ("lineage_generation", "lineage_generation"),
        ("request_ordinal", "request_ordinal"),
        ("lifecycle_number", "lifecycle_number"),
        ("event_sequence", "event_sequence"),
        ("expiry_lifecycle_number", "expiry_lifecycle_number"),
        ("configuration_version", "configuration_version"),
    ):
        if row[column] != envelope[field]:
            raise IngressRejectedError(f"linked request row/envelope mismatch at {column}")
    return row, envelope


def _load_dispatch(
    connection: sqlite3.Connection,
    dispatch_id: str,
) -> tuple[sqlite3.Row, sqlite3.Row, dict[str, object], dict[str, object]]:
    row = connection.execute(
        "SELECT * FROM consultation_dispatch WHERE dispatch_id=?",
        (dispatch_id,),
    ).fetchone()
    if row is None:
        raise IngressRejectedError("linked dispatch does not exist")
    request_row, request = _load_request(connection, str(row["request_id"]))
    try:
        decoded = json.loads(str(row["envelope_json"]))
    except (TypeError, json.JSONDecodeError) as exc:
        raise IngressRejectedError("linked dispatch envelope is not valid JSON") from exc
    dispatch = validate_dispatch_envelope(decoded, request_envelope=request)
    encoded = canonical_json_bytes(dispatch)
    if encoded.decode("utf-8") != row["envelope_json"]:
        raise IngressRejectedError("linked dispatch envelope is not canonical")
    if int(row["canonical_size_bytes"]) != len(encoded):
        raise IngressRejectedError("linked dispatch canonical size mismatch")
    for column, field in (
        ("dispatch_id", "dispatch_id"),
        ("request_id", "request_id"),
        ("organism_id", "organism_id"),
        ("lineage_generation", "lineage_generation"),
        ("dispatch_ordinal", "dispatch_ordinal"),
        ("event_sequence", "event_sequence"),
        ("configuration_version", "configuration_version"),
    ):
        if row[column] != dispatch[field]:
            raise IngressRejectedError(f"linked dispatch row/envelope mismatch at {column}")
    if dispatch["dispatch_id"] != dispatch_id:
        raise IngressRejectedError("linked dispatch ID mismatch")
    return request_row, row, request, dispatch


def _require_common_state(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
    *,
    organism: sqlite3.Row,
    request: dict[str, object],
    dispatch: dict[str, object],
) -> None:
    if int(organism["schema_version"]) != PHASE2_SCHEMA_VERSION:
        raise IngressRejectedError("consultation ingress requires schema-v2")
    if organism["status"] != "sleeping" or bool(organism["checkpoint_pending"]):
        raise IngressRejectedError(
            "consultation ingress requires sleeping status with no pending checkpoint"
        )
    if organism["maintenance_reason"] is not None:
        raise IngressRejectedError("consultation ingress cannot bypass maintenance")
    if request["configuration_version"] != FIXTURE_CONFIGURATION_VERSION:
        raise IngressRejectedError("consultation ingress requires fixture configuration")
    if int(request["lineage_generation"]) != int(organism["lineage_generation"]):
        raise IngressRejectedError("consultation work is not in the current lineage")
    if dispatch["lineage_generation"] != request["lineage_generation"]:
        raise IngressRejectedError("dispatch lineage does not match request")
    if dispatch["organism_id"] != organism["organism_id"]:
        raise IngressRejectedError("dispatch organism does not match canonical organism")
    if dispatch["request_id"] != request["request_id"]:
        raise IngressRejectedError("dispatch request linkage does not match")
    ensure_active_database_within_limit(
        connection,
        context="consultation ingress preflight",
    )
    ensure_active_database_has_wake_reserve(
        connection,
        context="consultation ingress preflight",
    )
    ensure_checkpoint_store_within_limit(
        paths,
        context="consultation ingress preflight",
    )
    ensure_runtime_working_set_within_limit(
        paths,
        context="consultation ingress preflight",
    )


def _direct_parent_sequences(
    connection: sqlite3.Connection,
    *,
    request: dict[str, object],
    dispatch: dict[str, object],
) -> list[int]:
    request_sequence = int(request["event_sequence"])
    dispatch_sequence = int(dispatch["event_sequence"])
    if request_sequence >= dispatch_sequence:
        raise IngressRejectedError("consultation direct parent order is invalid")
    rows = connection.execute(
        "SELECT event_sequence, lineage_generation, event_type, source FROM event "
        "WHERE event_sequence IN (?, ?) ORDER BY event_sequence",
        (request_sequence, dispatch_sequence),
    ).fetchall()
    if len(rows) != 2:
        raise IngressRejectedError("consultation direct parent event is missing")
    if int(rows[0]["event_sequence"]) != request_sequence:
        raise IngressRejectedError("request parent event sequence mismatch")
    if rows[0]["event_type"] != "consultation_request_created":
        raise IngressRejectedError("request parent event type mismatch")
    if int(rows[1]["event_sequence"]) != dispatch_sequence:
        raise IngressRejectedError("dispatch parent event sequence mismatch")
    if rows[1]["event_type"] != "consultation_dispatch_admitted":
        raise IngressRejectedError("dispatch parent event type mismatch")
    if rows[1]["source"] != DISPATCH_SOURCE:
        raise IngressRejectedError("dispatch parent event source mismatch")
    expected_lineage = int(request["lineage_generation"])
    if any(int(row["lineage_generation"]) != expected_lineage for row in rows):
        raise IngressRejectedError("consultation direct parent lineage mismatch")
    return [request_sequence, dispatch_sequence]


def _parse_external_package(
    raw_package_bytes: bytes,
    *,
    request: dict[str, object],
    dispatch: dict[str, object],
) -> tuple[dict[str, object], bytes, str]:
    try:
        text = raw_package_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IngressRejectedError("external package is not valid UTF-8") from exc
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IngressRejectedError("external package is not valid JSON") from exc
    try:
        package = validate_external_package(
            decoded,
            request_envelope=request,
            dispatch_envelope=dispatch,
        )
        canonical = canonical_json_bytes(package)
        digest = external_package_digest(
            package,
            request_envelope=request,
            dispatch_envelope=dispatch,
        )
    except Exception as exc:
        raise IngressRejectedError(str(exc)) from exc
    if raw_package_bytes != canonical:
        raise IngressRejectedError("external package bytes are not exact canonical bytes")
    return package, canonical, digest


def _require_logical_payload_capacity(
    connection: sqlite3.Connection,
    *,
    organism_id: str,
    lineage_generation: int,
    new_package_bytes: int,
) -> None:
    request_bytes = int(
        connection.execute(
            "SELECT COALESCE(SUM(canonical_size_bytes), 0) FROM consultation_request "
            "WHERE organism_id=? AND lineage_generation=?",
            (organism_id, lineage_generation),
        ).fetchone()[0]
    )
    package_bytes = int(
        connection.execute(
            "SELECT COALESCE(SUM(r.measured_package_bytes), 0) "
            "FROM consultation_ingress_receipt r "
            "JOIN consultation_request q ON q.request_id=r.request_id "
            "WHERE q.organism_id=? AND q.lineage_generation=?",
            (organism_id, lineage_generation),
        ).fetchone()[0]
    )
    if request_bytes + package_bytes + new_package_bytes > _LOGICAL_PAYLOAD_LIMIT_BYTES:
        raise IngressRejectedError("current lineage logical consultation payload exceeds 64 KiB")


def _receipt_envelope(
    *,
    request: dict[str, object],
    dispatch: dict[str, object],
    response_id: str,
    event_sequence: int,
    package_digest: str,
    measured_package_bytes: int,
    parents: list[int],
) -> dict[str, object]:
    value = {
        "authority": {
            "source": INGRESS_SOURCE,
            "writer_category": "administration",
        },
        "dispatch_id": dispatch["dispatch_id"],
        "event_sequence": event_sequence,
        "measured_package_bytes": measured_package_bytes,
        "package_digest": package_digest,
        "parent_event_sequences": list(parents),
        "protocol_version": 1,
        "receipt_id": receipt_id_from_package_digest(package_digest),
        "receipt_schema": INGRESS_RECEIPT_SCHEMA,
        "request_id": request["request_id"],
        "response_id": response_id,
    }
    _exact_fields(value, _RECEIPT_FIELDS, context="ingress receipt envelope")
    canonical_json_bytes(value)
    return value


def _success_completion(
    *,
    dispatch_id: str,
    response_id: str,
    measured_package_bytes: int,
) -> dict[str, object]:
    value = {
        "completion_id": completion_id_from_dispatch_id(dispatch_id),
        "dispatch_id": dispatch_id,
        "measured_package_bytes": measured_package_bytes,
        "response_id": response_id,
    }
    canonical_json_bytes(value)
    return value


def _terminal_envelope_bytes(value: dict[str, object]) -> bytes:
    terminal = _exact_fields(value, _TERMINAL_FIELDS, context="terminal envelope")
    for key, item in terminal.items():
        if key in {"rejected_package_digest", "rejected_package_size_bytes"}:
            continue
        canonical_json_bytes({key: item})
    try:
        return json.dumps(
            terminal,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise TerminalizationRejectedError("terminal envelope is not canonical JSON") from exc


def _terminal_payload_bytes(payload: dict[str, object]) -> bytes:
    if frozenset(payload) != frozenset({"completion", "terminal"}):
        raise TerminalizationRejectedError("terminal event payload field set mismatch")
    _terminal_envelope_bytes(payload["terminal"])
    canonical_json_bytes(payload["completion"])
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _fault_ingress(protected_test_fault: str | None, point: str) -> None:
    if protected_test_fault == point:
        raise _InjectedIngressFault(f"protected ingress fault: {point}")


def _fault_terminal(protected_test_fault: str | None, point: str) -> None:
    if protected_test_fault == point:
        raise _InjectedTerminalFault(f"protected terminal fault: {point}")


def _existing_ingress_result(
    connection: sqlite3.Connection,
    *,
    organism_id: str,
    request: dict[str, object],
    dispatch: dict[str, object],
    package: dict[str, object],
    canonical_package: bytes,
    package_digest: str,
    parents: list[int],
) -> IngressResult | None:
    response_row = connection.execute(
        "SELECT * FROM consultation_response WHERE dispatch_id=?",
        (dispatch["dispatch_id"],),
    ).fetchone()
    if response_row is None:
        return None
    if connection.execute(
        "SELECT 1 FROM consultation_dispatch_terminal WHERE dispatch_id=?",
        (dispatch["dispatch_id"],),
    ).fetchone() is not None:
        raise IngressRejectedError("dispatch has conflicting response and terminal state")
    response = package["response"]
    if response_row["response_id"] != response["response_id"]:
        raise IngressRejectedError("conflicting duplicate response ID")
    if response_row["package_digest"] != package_digest:
        raise IngressRejectedError("conflicting duplicate package digest")
    if int(response_row["canonical_size_bytes"]) != len(canonical_json_bytes(response)):
        raise IngressRejectedError("existing response canonical size mismatch")
    if response_row["envelope_json"] != canonical_json_bytes(response).decode("utf-8"):
        raise IngressRejectedError("existing response envelope mismatch")

    receipt_row = connection.execute(
        "SELECT * FROM consultation_ingress_receipt WHERE dispatch_id=?",
        (dispatch["dispatch_id"],),
    ).fetchone()
    completion_row = connection.execute(
        "SELECT * FROM consultation_cost_completion WHERE dispatch_id=?",
        (dispatch["dispatch_id"],),
    ).fetchone()
    if receipt_row is None or completion_row is None:
        raise IngressRejectedError("existing response is missing receipt or completion")
    if receipt_row["package_digest"] != package_digest:
        raise IngressRejectedError("conflicting duplicate receipt digest")
    if int(receipt_row["measured_package_bytes"]) != len(canonical_package):
        raise IngressRejectedError("conflicting duplicate measured package bytes")
    event_sequence = int(response_row["event_sequence"])
    if int(receipt_row["event_sequence"]) != event_sequence:
        raise IngressRejectedError("existing response/receipt event linkage mismatch")
    receipt = _receipt_envelope(
        request=request,
        dispatch=dispatch,
        response_id=str(response["response_id"]),
        event_sequence=event_sequence,
        package_digest=package_digest,
        measured_package_bytes=len(canonical_package),
        parents=parents,
    )
    completion = _success_completion(
        dispatch_id=str(dispatch["dispatch_id"]),
        response_id=str(response["response_id"]),
        measured_package_bytes=len(canonical_package),
    )
    if receipt_row["receipt_id"] != receipt["receipt_id"]:
        raise IngressRejectedError("existing receipt ID mismatch")
    if completion_row["completion_id"] != completion["completion_id"]:
        raise IngressRejectedError("existing completion ID mismatch")
    if completion_row["response_id"] != response["response_id"]:
        raise IngressRejectedError("existing completion response linkage mismatch")
    if completion_row["terminal_id"] is not None:
        raise IngressRejectedError("existing response completion links a terminal")
    if int(completion_row["measured_package_bytes"]) != len(canonical_package):
        raise IngressRejectedError("existing completion measured bytes mismatch")

    event = connection.execute(
        "SELECT event_type, source, payload_json FROM event WHERE event_sequence=?",
        (event_sequence,),
    ).fetchone()
    expected_payload = {"completion": completion, "receipt": receipt}
    if event is None or event["event_type"] != INGRESS_EVENT_TYPE or event["source"] != INGRESS_SOURCE:
        raise IngressRejectedError("existing ingress event mismatch")
    if event["payload_json"] != canonical_json_bytes(expected_payload).decode("utf-8"):
        raise IngressRejectedError("existing ingress event payload mismatch")

    proposals = package["proposals"]
    proposal_id = None if not proposals else str(proposals[0]["proposal_id"])
    proposal_rows = connection.execute(
        "SELECT proposal_id, envelope_json, canonical_size_bytes FROM consultation_proposal "
        "WHERE dispatch_id=?",
        (dispatch["dispatch_id"],),
    ).fetchall()
    if len(proposal_rows) != len(proposals):
        raise IngressRejectedError("existing proposal cardinality mismatch")
    if proposals:
        proposal_bytes = canonical_json_bytes(proposals[0])
        if proposal_rows[0]["proposal_id"] != proposal_id:
            raise IngressRejectedError("existing proposal ID mismatch")
        if proposal_rows[0]["envelope_json"] != proposal_bytes.decode("utf-8"):
            raise IngressRejectedError("existing proposal envelope mismatch")
        if int(proposal_rows[0]["canonical_size_bytes"]) != len(proposal_bytes):
            raise IngressRejectedError("existing proposal size mismatch")

    return IngressResult(
        created=False,
        organism_id=organism_id,
        request_id=str(request["request_id"]),
        dispatch_id=str(dispatch["dispatch_id"]),
        response_id=str(response["response_id"]),
        receipt_id=str(receipt["receipt_id"]),
        completion_id=str(completion["completion_id"]),
        event_sequence=event_sequence,
        package_digest=package_digest,
        measured_package_bytes=len(canonical_package),
        status=str(response["status"]),
        proposal_id=proposal_id,
    )


def ingress_external_package(
    runtime_root: Path | str,
    organism_id: str,
    *,
    dispatch_id: str,
    raw_package_bytes: bytes,
    clock: Clock | None = None,
    protected_test_fault: str | None = None,
) -> IngressResult:
    """Atomically ingress one exact canonical external package."""

    if protected_test_fault is not None and protected_test_fault not in _INGRESS_FAULT_POINTS:
        raise ValueError(f"unknown protected ingress fault: {protected_test_fault}")
    if not isinstance(raw_package_bytes, bytes):
        raise IngressRejectedError("external package must be bytes")
    if len(raw_package_bytes) > 16 * 1024:
        raise IngressRejectedError("external package exceeds 16 KiB before JSON parse")
    _dispatch_digest(dispatch_id)

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")
    connection = connect_database(paths.database)
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise IngressBusyError("package ingress is busy; this attempt was not queued") from exc
            raise

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            "SELECT * FROM organism WHERE singleton_id=1"
        ).fetchone()
        if organism is None:
            raise IngressRejectedError("ingress organism singleton is missing")
        _request_row, _dispatch_row, request, dispatch = _load_dispatch(
            connection,
            dispatch_id,
        )
        _require_common_state(
            connection,
            paths,
            organism=organism,
            request=request,
            dispatch=dispatch,
        )
        parents = _direct_parent_sequences(
            connection,
            request=request,
            dispatch=dispatch,
        )

        if connection.execute(
            "SELECT 1 FROM consultation_dispatch_terminal WHERE dispatch_id=?",
            (dispatch_id,),
        ).fetchone() is not None:
            raise IngressRejectedError("dispatch is already terminal")

        existing_response = connection.execute(
            "SELECT 1 FROM consultation_response WHERE dispatch_id=?",
            (dispatch_id,),
        ).fetchone()
        if existing_response is None and int(organism["lifecycle_number"]) > int(
            request["expiry_lifecycle_number"]
        ):
            raise IngressRejectedError("dispatch package expired before ingress")

        package, canonical_package, package_digest = _parse_external_package(
            raw_package_bytes,
            request=request,
            dispatch=dispatch,
        )
        existing = _existing_ingress_result(
            connection,
            organism_id=organism_id,
            request=request,
            dispatch=dispatch,
            package=package,
            canonical_package=canonical_package,
            package_digest=package_digest,
            parents=parents,
        )
        if existing is not None:
            connection.rollback()
            return existing

        _require_logical_payload_capacity(
            connection,
            organism_id=organism_id,
            lineage_generation=int(organism["lineage_generation"]),
            new_package_bytes=len(canonical_package),
        )

        reading = (clock or RealClock()).read()
        predicted_event_sequence = int(
            connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM event"
            ).fetchone()[0]
        )
        response = package["response"]
        proposals = package["proposals"]
        response_id = str(response["response_id"])
        receipt = _receipt_envelope(
            request=request,
            dispatch=dispatch,
            response_id=response_id,
            event_sequence=predicted_event_sequence,
            package_digest=package_digest,
            measured_package_bytes=len(canonical_package),
            parents=parents,
        )
        completion = _success_completion(
            dispatch_id=dispatch_id,
            response_id=response_id,
            measured_package_bytes=len(canonical_package),
        )
        payload = {"completion": completion, "receipt": receipt}

        cursor = connection.execute(
            """
            INSERT INTO event (
                organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
                event_type, source, payload_json, schema_version,
                environment_version, budget_config_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                organism_id,
                organism["lineage_generation"],
                organism["lifecycle_number"],
                reading.wall_time_utc_us,
                INGRESS_EVENT_TYPE,
                INGRESS_SOURCE,
                canonical_json_bytes(payload).decode("utf-8"),
                PHASE2_SCHEMA_VERSION,
                ENVIRONMENT_VERSION,
                BUDGET_CONFIG_VERSION,
            ),
        )
        event_sequence = int(cursor.lastrowid)
        if event_sequence != predicted_event_sequence:
            raise IngressRejectedError("ingress event sequence prediction mismatch")
        _fault_ingress(protected_test_fault, "after_event")

        response_bytes = canonical_json_bytes(response)
        connection.execute(
            """
            INSERT INTO consultation_response (
                response_id, request_id, dispatch_id, organism_id,
                lineage_generation, status, event_sequence, envelope_json,
                canonical_size_bytes, package_digest
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                response_id,
                response["request_id"],
                response["dispatch_id"],
                organism_id,
                organism["lineage_generation"],
                response["status"],
                event_sequence,
                response_bytes.decode("utf-8"),
                len(response_bytes),
                package_digest,
            ),
        )
        _fault_ingress(protected_test_fault, "after_response")

        proposal_id: str | None = None
        if proposals:
            proposal = proposals[0]
            proposal_id = str(proposal["proposal_id"])
            proposal_identity = {
                key: deepcopy(value)
                for key, value in proposal.items()
                if key not in {"proposal_id", "response_id"}
            }
            content_digest = proposal_content_digest(
                proposal_identity,
                request_envelope=request,
                fixture_case_id=str(dispatch["fixture_case_id"]),
            )
            proposal_bytes = canonical_json_bytes(proposal)
            connection.execute(
                """
                INSERT INTO consultation_proposal (
                    proposal_id, request_id, dispatch_id, response_id, organism_id,
                    lineage_generation, proposal_ordinal, proposal_type,
                    expiry_lifecycle_number, content_digest, envelope_json,
                    canonical_size_bytes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proposal_id,
                    proposal["request_id"],
                    proposal["dispatch_id"],
                    proposal["response_id"],
                    organism_id,
                    organism["lineage_generation"],
                    proposal["proposal_ordinal"],
                    proposal["proposal_type"],
                    proposal["expiry_lifecycle_number"],
                    content_digest,
                    proposal_bytes.decode("utf-8"),
                    len(proposal_bytes),
                ),
            )
        _fault_ingress(protected_test_fault, "after_proposal")

        connection.execute(
            """
            INSERT INTO consultation_ingress_receipt (
                receipt_id, request_id, dispatch_id, response_id, event_sequence,
                package_digest, measured_package_bytes
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                receipt["receipt_id"],
                receipt["request_id"],
                receipt["dispatch_id"],
                receipt["response_id"],
                event_sequence,
                receipt["package_digest"],
                receipt["measured_package_bytes"],
            ),
        )
        _fault_ingress(protected_test_fault, "after_receipt")

        connection.execute(
            """
            INSERT INTO consultation_cost_completion (
                completion_id, dispatch_id, response_id, terminal_id,
                measured_package_bytes
            ) VALUES (?, ?, ?, NULL, ?)
            """,
            (
                completion["completion_id"],
                completion["dispatch_id"],
                completion["response_id"],
                completion["measured_package_bytes"],
            ),
        )
        _fault_ingress(protected_test_fault, "after_completion")

        ensure_active_database_within_limit(
            connection,
            context="consultation ingress post-write",
        )
        ensure_active_database_has_wake_reserve(
            connection,
            context="consultation ingress post-write",
        )
        ensure_checkpoint_store_within_limit(
            paths,
            context="consultation ingress post-write",
        )
        ensure_runtime_working_set_within_limit(
            paths,
            context="consultation ingress post-write",
        )
        _fault_ingress(protected_test_fault, "before_commit")
        connection.commit()

        return IngressResult(
            created=True,
            organism_id=organism_id,
            request_id=str(request["request_id"]),
            dispatch_id=dispatch_id,
            response_id=response_id,
            receipt_id=str(receipt["receipt_id"]),
            completion_id=str(completion["completion_id"]),
            event_sequence=event_sequence,
            package_digest=package_digest,
            measured_package_bytes=len(canonical_package),
            status=str(response["status"]),
            proposal_id=proposal_id,
        )
    except (IngressBusyError, _InjectedIngressFault):
        if connection.in_transaction:
            connection.rollback()
        raise
    except IngressRejectedError:
        if connection.in_transaction:
            connection.rollback()
        raise
    except (SchemaValidationError, sqlite3.Error, OSError, ValueError) as exc:
        if connection.in_transaction:
            connection.rollback()
        raise IngressRejectedError(str(exc)) from exc
    except Exception as exc:
        if connection.in_transaction:
            connection.rollback()
        raise IngressRejectedError(str(exc)) from exc
    finally:
        connection.close()


def _terminal_values(
    *,
    request: dict[str, object],
    dispatch: dict[str, object],
    organism_id: str,
    event_sequence: int,
    reason_code: str,
    raw_package_bytes: bytes | None,
    parents: list[int],
) -> tuple[dict[str, object], dict[str, object], bytes]:
    if reason_code not in _TERMINAL_REASONS:
        raise TerminalizationRejectedError("terminal reason code is not supported")
    current_dispatch_id = str(dispatch["dispatch_id"])
    if reason_code == "dispatch_interrupted":
        if raw_package_bytes is not None:
            raise TerminalizationRejectedError(
                "dispatch_interrupted does not accept package bytes"
            )
        rejected_digest = None
        rejected_size = None
        measured = 0
    else:
        if not isinstance(raw_package_bytes, bytes):
            raise TerminalizationRejectedError(
                f"{reason_code} requires attempted raw package bytes"
            )
        rejected_digest = rejected_package_digest(raw_package_bytes)
        rejected_size = len(raw_package_bytes)
        measured = len(raw_package_bytes)
    terminal = {
        "authority": {
            "source": TERMINAL_SOURCE,
            "writer_category": "administration",
        },
        "dispatch_id": current_dispatch_id,
        "event_sequence": event_sequence,
        "lineage_generation": request["lineage_generation"],
        "organism_id": organism_id,
        "parent_event_sequences": list(parents),
        "protocol_version": 1,
        "reason_code": reason_code,
        "rejected_package_digest": rejected_digest,
        "rejected_package_size_bytes": rejected_size,
        "request_id": request["request_id"],
        "terminal_id": terminal_id_from_dispatch_id(current_dispatch_id),
        "terminal_schema": TERMINAL_SCHEMA,
    }
    _terminal_envelope_bytes(terminal)
    completion = {
        "completion_id": completion_id_from_dispatch_id(current_dispatch_id),
        "dispatch_id": current_dispatch_id,
        "measured_package_bytes": measured,
        "terminal_id": terminal["terminal_id"],
    }
    canonical_json_bytes(completion)
    payload = {"completion": completion, "terminal": terminal}
    payload_bytes = _terminal_payload_bytes(payload)
    return terminal, completion, payload_bytes


def _existing_terminal_result(
    connection: sqlite3.Connection,
    *,
    organism_id: str,
    request: dict[str, object],
    dispatch: dict[str, object],
    reason_code: str,
    raw_package_bytes: bytes | None,
    parents: list[int],
) -> TerminalizationResult | None:
    row = connection.execute(
        "SELECT * FROM consultation_dispatch_terminal WHERE dispatch_id=?",
        (dispatch["dispatch_id"],),
    ).fetchone()
    if row is None:
        return None
    event_sequence = int(row["event_sequence"])
    terminal, completion, payload_bytes = _terminal_values(
        request=request,
        dispatch=dispatch,
        organism_id=organism_id,
        event_sequence=event_sequence,
        reason_code=reason_code,
        raw_package_bytes=raw_package_bytes,
        parents=parents,
    )
    if row["terminal_id"] != terminal["terminal_id"]:
        raise TerminalizationRejectedError("existing terminal ID mismatch")
    if row["reason_code"] != reason_code:
        raise TerminalizationRejectedError("conflicting terminal reason")
    if row["rejected_package_digest"] != terminal["rejected_package_digest"]:
        raise TerminalizationRejectedError("conflicting terminal package digest")
    stored_size = row["rejected_package_size_bytes"]
    if stored_size != terminal["rejected_package_size_bytes"]:
        raise TerminalizationRejectedError("conflicting terminal package size")
    completion_row = connection.execute(
        "SELECT * FROM consultation_cost_completion WHERE dispatch_id=?",
        (dispatch["dispatch_id"],),
    ).fetchone()
    if completion_row is None:
        raise TerminalizationRejectedError("existing terminal is missing completion")
    if completion_row["completion_id"] != completion["completion_id"]:
        raise TerminalizationRejectedError("existing terminal completion ID mismatch")
    if completion_row["terminal_id"] != terminal["terminal_id"]:
        raise TerminalizationRejectedError("existing terminal completion linkage mismatch")
    if completion_row["response_id"] is not None:
        raise TerminalizationRejectedError("existing terminal completion links a response")
    if int(completion_row["measured_package_bytes"]) != completion["measured_package_bytes"]:
        raise TerminalizationRejectedError("existing terminal completion bytes mismatch")
    event = connection.execute(
        "SELECT event_type, source, payload_json FROM event WHERE event_sequence=?",
        (event_sequence,),
    ).fetchone()
    if event is None or event["event_type"] != TERMINAL_EVENT_TYPE or event["source"] != TERMINAL_SOURCE:
        raise TerminalizationRejectedError("existing terminal event mismatch")
    if event["payload_json"].encode("utf-8") != payload_bytes:
        raise TerminalizationRejectedError("existing terminal event payload mismatch")
    return TerminalizationResult(
        created=False,
        organism_id=organism_id,
        request_id=str(request["request_id"]),
        dispatch_id=str(dispatch["dispatch_id"]),
        terminal_id=str(terminal["terminal_id"]),
        completion_id=str(completion["completion_id"]),
        event_sequence=event_sequence,
        reason_code=reason_code,
        rejected_package_digest=terminal["rejected_package_digest"],
        rejected_package_size_bytes=terminal["rejected_package_size_bytes"],
        measured_package_bytes=int(completion["measured_package_bytes"]),
    )


def terminalize_fixture_dispatch(
    runtime_root: Path | str,
    organism_id: str,
    *,
    dispatch_id: str,
    reason_code: str,
    raw_package_bytes: bytes | None,
    clock: Clock | None = None,
    protected_test_fault: str | None = None,
) -> TerminalizationResult:
    """Atomically record one exact terminal outcome for admitted fixture work."""

    if protected_test_fault is not None and protected_test_fault not in _TERMINAL_FAULT_POINTS:
        raise ValueError(f"unknown protected terminal fault: {protected_test_fault}")
    if reason_code not in _TERMINAL_REASONS:
        raise TerminalizationRejectedError("terminal reason code is not supported")
    try:
        _dispatch_digest(dispatch_id)
    except IngressRejectedError as exc:
        raise TerminalizationRejectedError(str(exc)) from exc
    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")
    connection = connect_database(paths.database)
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise TerminalizationBusyError(
                    "dispatch terminalization is busy; this attempt was not queued"
                ) from exc
            raise

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            "SELECT * FROM organism WHERE singleton_id=1"
        ).fetchone()
        if organism is None:
            raise TerminalizationRejectedError("terminal organism singleton is missing")
        try:
            _request_row, _dispatch_row, request, dispatch = _load_dispatch(
                connection,
                dispatch_id,
            )
            _require_common_state(
                connection,
                paths,
                organism=organism,
                request=request,
                dispatch=dispatch,
            )
            parents = _direct_parent_sequences(
                connection,
                request=request,
                dispatch=dispatch,
            )
        except IngressRejectedError as exc:
            raise TerminalizationRejectedError(str(exc)) from exc

        if connection.execute(
            "SELECT 1 FROM consultation_response WHERE dispatch_id=?",
            (dispatch_id,),
        ).fetchone() is not None:
            raise TerminalizationRejectedError("dispatch already has a successful response")

        existing = _existing_terminal_result(
            connection,
            organism_id=organism_id,
            request=request,
            dispatch=dispatch,
            reason_code=reason_code,
            raw_package_bytes=raw_package_bytes,
            parents=parents,
        )
        if existing is not None:
            connection.rollback()
            return existing

        expired = int(organism["lifecycle_number"]) > int(request["expiry_lifecycle_number"])
        if reason_code == "expired_before_ingress" and not expired:
            raise TerminalizationRejectedError(
                "expired_before_ingress requires lifecycle crossing"
            )
        if reason_code == "fixture_output_invalid" and expired:
            raise TerminalizationRejectedError(
                "expired dispatch must use expired_before_ingress"
            )

        reading = (clock or RealClock()).read()
        predicted_event_sequence = int(
            connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM event"
            ).fetchone()[0]
        )
        terminal, completion, payload_bytes = _terminal_values(
            request=request,
            dispatch=dispatch,
            organism_id=organism_id,
            event_sequence=predicted_event_sequence,
            reason_code=reason_code,
            raw_package_bytes=raw_package_bytes,
            parents=parents,
        )

        cursor = connection.execute(
            """
            INSERT INTO event (
                organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
                event_type, source, payload_json, schema_version,
                environment_version, budget_config_version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                organism_id,
                organism["lineage_generation"],
                organism["lifecycle_number"],
                reading.wall_time_utc_us,
                TERMINAL_EVENT_TYPE,
                TERMINAL_SOURCE,
                payload_bytes.decode("utf-8"),
                PHASE2_SCHEMA_VERSION,
                ENVIRONMENT_VERSION,
                BUDGET_CONFIG_VERSION,
            ),
        )
        event_sequence = int(cursor.lastrowid)
        if event_sequence != predicted_event_sequence:
            raise TerminalizationRejectedError("terminal event sequence prediction mismatch")
        _fault_terminal(protected_test_fault, "after_event")

        connection.execute(
            """
            INSERT INTO consultation_dispatch_terminal (
                terminal_id, request_id, dispatch_id, organism_id,
                lineage_generation, reason_code, rejected_package_digest,
                rejected_package_size_bytes, event_sequence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                terminal["terminal_id"],
                terminal["request_id"],
                terminal["dispatch_id"],
                terminal["organism_id"],
                terminal["lineage_generation"],
                terminal["reason_code"],
                terminal["rejected_package_digest"],
                terminal["rejected_package_size_bytes"],
                event_sequence,
            ),
        )
        _fault_terminal(protected_test_fault, "after_terminal")

        connection.execute(
            """
            INSERT INTO consultation_cost_completion (
                completion_id, dispatch_id, response_id, terminal_id,
                measured_package_bytes
            ) VALUES (?, ?, NULL, ?, ?)
            """,
            (
                completion["completion_id"],
                completion["dispatch_id"],
                completion["terminal_id"],
                completion["measured_package_bytes"],
            ),
        )
        _fault_terminal(protected_test_fault, "after_completion")

        ensure_active_database_within_limit(
            connection,
            context="dispatch terminalization post-write",
        )
        ensure_active_database_has_wake_reserve(
            connection,
            context="dispatch terminalization post-write",
        )
        ensure_checkpoint_store_within_limit(
            paths,
            context="dispatch terminalization post-write",
        )
        ensure_runtime_working_set_within_limit(
            paths,
            context="dispatch terminalization post-write",
        )
        _fault_terminal(protected_test_fault, "before_commit")
        connection.commit()

        return TerminalizationResult(
            created=True,
            organism_id=organism_id,
            request_id=str(request["request_id"]),
            dispatch_id=dispatch_id,
            terminal_id=str(terminal["terminal_id"]),
            completion_id=str(completion["completion_id"]),
            event_sequence=event_sequence,
            reason_code=reason_code,
            rejected_package_digest=terminal["rejected_package_digest"],
            rejected_package_size_bytes=terminal["rejected_package_size_bytes"],
            measured_package_bytes=int(completion["measured_package_bytes"]),
        )
    except (TerminalizationBusyError, _InjectedTerminalFault):
        if connection.in_transaction:
            connection.rollback()
        raise
    except TerminalizationRejectedError:
        if connection.in_transaction:
            connection.rollback()
        raise
    except (SchemaValidationError, sqlite3.Error, OSError, ValueError) as exc:
        if connection.in_transaction:
            connection.rollback()
        raise TerminalizationRejectedError(str(exc)) from exc
    except Exception as exc:
        if connection.in_transaction:
            connection.rollback()
        raise TerminalizationRejectedError(str(exc)) from exc
    finally:
        connection.close()


def reconcile_interrupted_dispatch(
    runtime_root: Path | str,
    organism_id: str,
    *,
    dispatch_id: str,
    clock: Clock | None = None,
    protected_test_fault: str | None = None,
) -> TerminalizationResult:
    """Record only `dispatch_interrupted`; never invoke or retry the fixture."""

    return terminalize_fixture_dispatch(
        runtime_root,
        organism_id,
        dispatch_id=dispatch_id,
        reason_code="dispatch_interrupted",
        raw_package_bytes=None,
        clock=clock,
        protected_test_fault=protected_test_fault,
    )


__all__ = [
    "IngressBusyError",
    "IngressError",
    "IngressRejectedError",
    "IngressResult",
    "TerminalizationBusyError",
    "TerminalizationError",
    "TerminalizationRejectedError",
    "TerminalizationResult",
    "completion_id_from_dispatch_id",
    "ingress_external_package",
    "receipt_id_from_package_digest",
    "reconcile_interrupted_dispatch",
    "rejected_package_digest",
    "terminal_id_from_dispatch_id",
    "terminalize_fixture_dispatch",
]
