"""Administrative dispatch admission, conservative precharge, and fixture handoff."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from typing import Final

from .checkpoints import validate_checkpoint_directory
from .clock import Clock, RealClock
from .constants import BUDGET_CONFIG_VERSION, ENVIRONMENT_VERSION
from .errors import (
    CheckpointError,
    OrganismNotFoundError,
    SchemaValidationError,
    SudachiError,
)
from .paths import OrganismPaths
from .phase2_dispatch import (
    DISPATCH_ADAPTER_VERSION,
    DISPATCH_CONFIGURATION_VERSION,
    DISPATCH_SCHEMA,
    DISPATCH_SOURCE,
    DISPATCH_WORK_CLASS,
    finalize_dispatch,
    validate_dispatch_envelope,
)
from .phase2_fixture import run_deterministic_fixture
from .phase2_ingress_runtime import terminalize_fixture_dispatch
from .phase2_protocol import canonical_json_bytes, validate_request_envelope
from .phase2_schema import PHASE2_SCHEMA_VERSION
from .runtime_storage import (
    ensure_active_database_has_wake_reserve,
    ensure_active_database_within_limit,
    ensure_checkpoint_store_within_limit,
    ensure_runtime_working_set_within_limit,
)
from .storage import connect_database, validate_canonical_state


DISPATCH_ADMISSION_EVENT_TYPE: Final = "consultation_dispatch_admitted"
CHARGE_ID_PREFIX: Final = "consultation-cost-charge:"

_DISPATCH_ID_RE: Final = re.compile(r"^consultation-dispatch:([0-9a-f]{64})$")
_CHARGE_FIELDS: Final = frozenset(
    {
        "attempt_count",
        "charge_id",
        "declared_latency_ms",
        "fixture_invocation_count",
        "human_minutes",
        "model_units",
        "money_microunits",
        "request_bytes",
        "work_units",
    }
)
_DISPATCH_ENVELOPE_FIELDS: Final = frozenset(
    {
        "adapter_version",
        "authority",
        "configuration_version",
        "dispatch_id",
        "dispatch_ordinal",
        "dispatch_schema",
        "event_sequence",
        "fixture_case_id",
        "lineage_generation",
        "organism_id",
        "protocol_version",
        "request_id",
        "work_class",
    }
)

_CHECKPOINT_MANIFEST_FIELDS: Final = frozenset(
    {
        "budget_config_version",
        "checkpoint_format_version",
        "checkpoint_id",
        "contract_version",
        "creation_wall_time_utc_us",
        "database_filename",
        "database_sha256",
        "database_size_bytes",
        "environment_version",
        "event_sequence",
        "implementation_version",
        "lifecycle_number",
        "lineage_generation",
        "organism_id",
        "provenance",
        "schema_version",
        "snapshot_method",
        "status",
    }
)

_FAULT_POINTS: Final = frozenset(
    {"after_event", "after_dispatch", "after_charge", "before_commit"}
)


class DispatchAdmissionError(SudachiError):
    """Base class for expected dispatch-admission failures."""


class DispatchAdmissionBusyError(DispatchAdmissionError):
    """Raised when fail-fast administrative ownership is unavailable."""


class DispatchAdmissionRejectedError(DispatchAdmissionError):
    """Raised when a request is not eligible for a new dispatch."""


class FixtureExecutionError(DispatchAdmissionError):
    """Raised after a committed charge when deterministic fixture work fails."""


class _InjectedDispatchAdmissionFault(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DispatchAdmissionResult:
    created: bool
    organism_id: str
    request_id: str
    dispatch_id: str
    charge_id: str
    event_sequence: int
    fixture_case_id: str
    request_envelope: dict[str, object]
    dispatch_envelope: dict[str, object]
    charge: dict[str, object]


@dataclass(frozen=True, slots=True)
class FixtureDispatchResult:
    admission: DispatchAdmissionResult
    fixture_invoked: bool
    fixture_output: bytes | None



def _is_busy(exc: sqlite3.OperationalError) -> bool:
    text = str(exc).lower()
    return "locked" in text or "busy" in text


def _integer(value: object, *, context: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise DispatchAdmissionRejectedError(
            f"{context} must be an integer greater than or equal to {minimum}"
        )
    return value


def _exact_fields(value: object, expected: frozenset[str], *, context: str) -> dict:
    if not isinstance(value, dict):
        raise DispatchAdmissionRejectedError(f"{context} must be an object")
    actual = frozenset(value)
    if actual != expected:
        raise DispatchAdmissionRejectedError(
            f"{context} field set mismatch: "
            f"missing={sorted(expected - actual)!r}, extra={sorted(actual - expected)!r}"
        )
    return value


def charge_id_from_dispatch_id(dispatch_id: object) -> str:
    """Return ADR 0011's typed alias of one exact dispatch digest."""

    if not isinstance(dispatch_id, str):
        raise DispatchAdmissionRejectedError("dispatch ID is not an exact digest identifier")
    match = _DISPATCH_ID_RE.fullmatch(dispatch_id)
    if match is None:
        raise DispatchAdmissionRejectedError("dispatch ID is not an exact digest identifier")
    return CHARGE_ID_PREFIX + match.group(1)


def _validate_charge(charge: object) -> dict[str, object]:
    value = _exact_fields(charge, _CHARGE_FIELDS, context="dispatch charge")
    if value["charge_id"] != charge_id_from_dispatch_id(
        "consultation-dispatch:" + str(value["charge_id"]).split(":", 1)[-1]
    ):
        raise DispatchAdmissionRejectedError("dispatch charge ID is not exact")
    for name in ("attempt_count", "fixture_invocation_count", "work_units"):
        if _integer(value[name], context=f"dispatch charge {name}", minimum=1) != 1:
            raise DispatchAdmissionRejectedError(f"dispatch charge {name} must equal 1")
    _integer(value["request_bytes"], context="dispatch charge request bytes")
    for name in (
        "human_minutes",
        "model_units",
        "money_microunits",
        "declared_latency_ms",
    ):
        if _integer(value[name], context=f"dispatch charge {name}") != 0:
            raise DispatchAdmissionRejectedError(f"dispatch charge {name} must equal 0")
    canonical_json_bytes(value)
    return deepcopy(value)


def build_dispatch_charge(
    *,
    dispatch_id: object,
    request_canonical_size_bytes: object,
    request_envelope: object,
) -> dict[str, object]:
    """Build and validate the exact ADR 0011 conservative charge ledger."""

    charge_id = charge_id_from_dispatch_id(dispatch_id)
    stored_size = _integer(
        request_canonical_size_bytes,
        context="dispatch request bytes",
    )
    measured_size = len(canonical_json_bytes(request_envelope))
    if stored_size != measured_size:
        raise DispatchAdmissionRejectedError(
            "dispatch request bytes do not match the canonical request envelope"
        )
    return _validate_charge(
        {
            "attempt_count": 1,
            "charge_id": charge_id,
            "declared_latency_ms": 0,
            "fixture_invocation_count": 1,
            "human_minutes": 0,
            "model_units": 0,
            "money_microunits": 0,
            "request_bytes": measured_size,
            "work_units": 1,
        }
    )


def build_dispatch_admission_payload(
    *,
    dispatch: object,
    charge: object,
) -> dict[str, object]:
    """Build the exact two-key ADR 0011 event payload."""

    if not isinstance(dispatch, dict):
        raise DispatchAdmissionRejectedError("dispatch envelope must be an object")
    actual = frozenset(dispatch)
    if not {"dispatch_id", "event_sequence"}.issubset(actual):
        raise DispatchAdmissionRejectedError("dispatch envelope field set is incomplete")
    extra = actual - _DISPATCH_ENVELOPE_FIELDS
    if extra:
        raise DispatchAdmissionRejectedError(
            f"dispatch envelope field set mismatch: extra={sorted(extra)!r}"
        )
    validated_charge = _validate_charge(charge)
    payload = {
        "charge": validated_charge,
        "dispatch": deepcopy(dispatch),
    }
    canonical_json_bytes(payload)
    return payload


def _load_request(
    connection: sqlite3.Connection,
    request_id: str,
) -> tuple[sqlite3.Row, dict[str, object]]:
    row = connection.execute(
        "SELECT * FROM consultation_request WHERE request_id=?",
        (request_id,),
    ).fetchone()
    if row is None:
        raise DispatchAdmissionRejectedError("dispatch request does not exist")
    try:
        decoded = json.loads(str(row["envelope_json"]))
    except (TypeError, json.JSONDecodeError) as exc:
        raise DispatchAdmissionRejectedError("dispatch request envelope is not valid JSON") from exc
    envelope = validate_request_envelope(decoded)
    encoded = canonical_json_bytes(envelope)
    if encoded.decode("utf-8") != row["envelope_json"]:
        raise DispatchAdmissionRejectedError("dispatch request envelope is not canonical")
    if int(row["canonical_size_bytes"]) != len(encoded):
        raise DispatchAdmissionRejectedError("dispatch request bytes do not match stored size")
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
            raise DispatchAdmissionRejectedError(
                f"dispatch request row/envelope mismatch at {column}"
            )
    return row, envelope


def _dispatch_identity(
    *,
    request_envelope: dict[str, object],
    fixture_case_id: str,
) -> dict[str, object]:
    return {
        "adapter_version": DISPATCH_ADAPTER_VERSION,
        "configuration_version": DISPATCH_CONFIGURATION_VERSION,
        "dispatch_ordinal": 1,
        "dispatch_schema": DISPATCH_SCHEMA,
        "fixture_case_id": fixture_case_id,
        "lineage_generation": request_envelope["lineage_generation"],
        "organism_id": request_envelope["organism_id"],
        "protocol_version": 1,
        "request_id": request_envelope["request_id"],
        "work_class": DISPATCH_WORK_CLASS,
    }


def _result_from_existing(
    connection: sqlite3.Connection,
    *,
    organism_id: str,
    request_row: sqlite3.Row,
    request_envelope: dict[str, object],
    fixture_case_id: str,
) -> DispatchAdmissionResult | None:
    dispatch_row = connection.execute(
        "SELECT * FROM consultation_dispatch WHERE request_id=?",
        (request_envelope["request_id"],),
    ).fetchone()
    if dispatch_row is None:
        return None
    try:
        dispatch_decoded = json.loads(str(dispatch_row["envelope_json"]))
    except (TypeError, json.JSONDecodeError) as exc:
        raise DispatchAdmissionRejectedError("existing dispatch envelope is invalid") from exc
    dispatch = validate_dispatch_envelope(
        dispatch_decoded,
        request_envelope=request_envelope,
    )
    if dispatch["fixture_case_id"] != fixture_case_id:
        raise DispatchAdmissionRejectedError("conflicting fixture case for existing dispatch")
    if dispatch_row["dispatch_id"] != dispatch["dispatch_id"]:
        raise DispatchAdmissionRejectedError("existing dispatch row/envelope mismatch")
    if int(dispatch_row["event_sequence"]) != dispatch["event_sequence"]:
        raise DispatchAdmissionRejectedError("existing dispatch event linkage mismatch")
    if int(dispatch_row["canonical_size_bytes"]) != len(canonical_json_bytes(dispatch)):
        raise DispatchAdmissionRejectedError("existing dispatch size mismatch")

    charge_row = connection.execute(
        "SELECT * FROM consultation_cost_charge WHERE dispatch_id=?",
        (dispatch["dispatch_id"],),
    ).fetchone()
    if charge_row is None:
        raise DispatchAdmissionRejectedError("existing dispatch is missing its charge")
    charge = build_dispatch_charge(
        dispatch_id=dispatch["dispatch_id"],
        request_canonical_size_bytes=request_row["canonical_size_bytes"],
        request_envelope=request_envelope,
    )
    if charge_row["charge_id"] != charge["charge_id"]:
        raise DispatchAdmissionRejectedError("existing charge ID mismatch")
    if int(charge_row["event_sequence"]) != dispatch["event_sequence"]:
        raise DispatchAdmissionRejectedError("existing charge event linkage mismatch")
    for key in _CHARGE_FIELDS - {"charge_id"}:
        if int(charge_row[key]) != charge[key]:
            raise DispatchAdmissionRejectedError(f"existing charge mismatch at {key}")

    event = connection.execute(
        "SELECT event_type, source, payload_json FROM event WHERE event_sequence=?",
        (dispatch["event_sequence"],),
    ).fetchone()
    if event is None:
        raise DispatchAdmissionRejectedError("existing dispatch event is missing")
    if event["event_type"] != DISPATCH_ADMISSION_EVENT_TYPE:
        raise DispatchAdmissionRejectedError("existing dispatch event type mismatch")
    if event["source"] != DISPATCH_SOURCE:
        raise DispatchAdmissionRejectedError("existing dispatch event source mismatch")
    expected_payload = build_dispatch_admission_payload(
        dispatch=dispatch,
        charge=charge,
    )
    if json.loads(str(event["payload_json"])) != expected_payload:
        raise DispatchAdmissionRejectedError("existing dispatch event payload mismatch")

    return DispatchAdmissionResult(
        created=False,
        organism_id=organism_id,
        request_id=str(request_envelope["request_id"]),
        dispatch_id=str(dispatch["dispatch_id"]),
        charge_id=str(charge["charge_id"]),
        event_sequence=int(dispatch["event_sequence"]),
        fixture_case_id=fixture_case_id,
        request_envelope=deepcopy(request_envelope),
        dispatch_envelope=deepcopy(dispatch),
        charge=deepcopy(charge),
    )


def _require_exact_request_created_event(
    event: sqlite3.Row,
    *,
    context: str,
    active_organism_id: str,
    request_row: sqlite3.Row,
    request_envelope: dict[str, object],
) -> None:
    expected = {
        "event_sequence": int(request_row["event_sequence"]),
        "organism_id": active_organism_id,
        "lineage_generation": int(request_row["lineage_generation"]),
        "lifecycle_number": int(request_row["lifecycle_number"]),
        "event_type": "consultation_request_created",
        "source": "organism:consultation.request",
        "payload_json": canonical_json_bytes(
            {
                "canonical_size_bytes": int(request_row["canonical_size_bytes"]),
                "request": request_envelope,
            }
        ).decode("utf-8"),
        "schema_version": PHASE2_SCHEMA_VERSION,
        "environment_version": ENVIRONMENT_VERSION,
        "budget_config_version": BUDGET_CONFIG_VERSION,
    }
    actual = {
        "event_sequence": int(event["event_sequence"]),
        "organism_id": event["organism_id"],
        "lineage_generation": int(event["lineage_generation"]),
        "lifecycle_number": int(event["lifecycle_number"]),
        "event_type": event["event_type"],
        "source": event["source"],
        "payload_json": event["payload_json"],
        "schema_version": int(event["schema_version"]),
        "environment_version": event["environment_version"],
        "budget_config_version": event["budget_config_version"],
    }
    if actual != expected:
        mismatches = sorted(
            field for field in expected if actual[field] != expected[field]
        )
        raise DispatchAdmissionRejectedError(
            f"{context} request event semantics mismatch: {mismatches!r}"
        )


def _require_request_checkpoint_snapshot(
    active_connection: sqlite3.Connection,
    checkpoint_dir: Path,
    *,
    active_organism_id: str,
    request_row: sqlite3.Row,
    request_envelope: dict[str, object],
) -> None:
    request_id = str(request_envelope["request_id"])
    request_event_sequence = int(request_row["event_sequence"])
    snapshot = connect_database(checkpoint_dir / "organism.sqlite3", read_only=True)
    try:
        try:
            snapshot_row, snapshot_envelope = _load_request(snapshot, request_id)
        except DispatchAdmissionRejectedError as exc:
            raise DispatchAdmissionRejectedError(
                f"dispatch checkpoint request is invalid: {exc}"
            ) from exc
        if snapshot_envelope != request_envelope or dict(snapshot_row) != dict(request_row):
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request row does not match active request"
            )

        active_event = active_connection.execute(
            "SELECT * FROM event WHERE event_sequence=?",
            (request_event_sequence,),
        ).fetchone()
        if active_event is None:
            raise DispatchAdmissionRejectedError(
                "dispatch active request event is missing"
            )
        _require_exact_request_created_event(
            active_event,
            context="dispatch active",
            active_organism_id=active_organism_id,
            request_row=request_row,
            request_envelope=request_envelope,
        )

        snapshot_event = snapshot.execute(
            "SELECT * FROM event WHERE event_sequence=?",
            (request_event_sequence,),
        ).fetchone()
        if snapshot_event is None:
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request event is missing"
            )
        _require_exact_request_created_event(
            snapshot_event,
            context="dispatch checkpoint",
            active_organism_id=active_organism_id,
            request_row=request_row,
            request_envelope=request_envelope,
        )
        if dict(snapshot_event) != dict(active_event):
            raise DispatchAdmissionRejectedError(
                "dispatch checkpoint request event does not match active event"
            )
    finally:
        snapshot.close()


def _require_admission_state(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
    *,
    organism: sqlite3.Row,
    request_row: sqlite3.Row,
    request_envelope: dict[str, object],
) -> None:
    if int(organism["schema_version"]) != PHASE2_SCHEMA_VERSION:
        raise DispatchAdmissionRejectedError("dispatch requires schema-v2")
    if organism["status"] != "sleeping" or bool(organism["checkpoint_pending"]):
        raise DispatchAdmissionRejectedError(
            "dispatch requires sleeping status with no pending checkpoint"
        )
    if organism["maintenance_reason"] is not None:
        raise DispatchAdmissionRejectedError("dispatch cannot bypass maintenance")
    if request_envelope["configuration_version"] != DISPATCH_CONFIGURATION_VERSION:
        raise DispatchAdmissionRejectedError("dispatch requires fixture configuration")
    if int(request_envelope["lineage_generation"]) != int(
        organism["lineage_generation"]
    ):
        raise DispatchAdmissionRejectedError("dispatch request is not in the current lineage")
    if int(organism["lifecycle_number"]) > int(
        request_envelope["expiry_lifecycle_number"]
    ):
        raise DispatchAdmissionRejectedError("dispatch request has expired")

    latest_checkpoint_id = organism["latest_stable_checkpoint_id"]
    latest_boundary = int(organism["latest_stable_event_sequence"])
    if latest_checkpoint_id is None or latest_boundary < int(request_row["event_sequence"]):
        raise DispatchAdmissionRejectedError("dispatch request is not checkpoint-stable")
    registry = connection.execute(
        "SELECT lineage_generation, event_sequence, manifest_sha256, "
        "database_sha256, database_size_bytes FROM checkpoint_registry "
        "WHERE checkpoint_id=?",
        (latest_checkpoint_id,),
    ).fetchone()
    if registry is None:
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint is not registered")
    if int(registry["lineage_generation"]) != int(organism["lineage_generation"]):
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint lineage mismatch")
    if int(registry["event_sequence"]) != latest_boundary:
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint boundary mismatch")

    checkpoint_dir = paths.checkpoints / str(latest_checkpoint_id)
    if not checkpoint_dir.is_dir():
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint artifact is missing")
    try:
        manifest = validate_checkpoint_directory(checkpoint_dir)
        manifest_sha = hashlib.sha256(
            (checkpoint_dir / "manifest.json").read_bytes()
        ).hexdigest()
    except (CheckpointError, OSError) as exc:
        raise DispatchAdmissionRejectedError(str(exc)) from exc
    manifest = _exact_fields(
        manifest,
        _CHECKPOINT_MANIFEST_FIELDS,
        context="dispatch checkpoint manifest",
    )
    active_organism_id = str(organism["organism_id"])
    if request_envelope["organism_id"] != active_organism_id:
        raise DispatchAdmissionRejectedError("dispatch request organism mismatch")
    if manifest["organism_id"] != active_organism_id:
        raise DispatchAdmissionRejectedError("dispatch checkpoint organism mismatch")
    if manifest["checkpoint_id"] != latest_checkpoint_id:
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest ID mismatch")
    if int(manifest["lineage_generation"]) != int(registry["lineage_generation"]):
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest lineage mismatch")
    if int(manifest["event_sequence"]) != int(registry["event_sequence"]):
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest boundary mismatch")
    if manifest["database_sha256"] != registry["database_sha256"]:
        raise DispatchAdmissionRejectedError("dispatch checkpoint database digest mismatch")
    if int(manifest["database_size_bytes"]) != int(registry["database_size_bytes"]):
        raise DispatchAdmissionRejectedError("dispatch checkpoint database size mismatch")
    if manifest_sha != registry["manifest_sha256"]:
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest digest mismatch")
    _require_request_checkpoint_snapshot(
        connection,
        checkpoint_dir,
        active_organism_id=active_organism_id,
        request_row=request_row,
        request_envelope=request_envelope,
    )

    if connection.execute(
        "SELECT 1 FROM consultation_response WHERE request_id=?",
        (request_envelope["request_id"],),
    ).fetchone() is not None:
        raise DispatchAdmissionRejectedError("dispatch request already has a response")
    if connection.execute(
        "SELECT 1 FROM consultation_dispatch_terminal WHERE request_id=?",
        (request_envelope["request_id"],),
    ).fetchone() is not None:
        raise DispatchAdmissionRejectedError("dispatch request is already terminal")

    charged_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM consultation_cost_charge c "
            "JOIN consultation_dispatch d ON d.dispatch_id=c.dispatch_id "
            "WHERE d.organism_id=? AND d.lineage_generation=?",
            (organism["organism_id"], organism["lineage_generation"]),
        ).fetchone()[0]
    )
    if charged_count >= 4:
        raise DispatchAdmissionRejectedError(
            "current lineage has exhausted charged fixture invocations"
        )

    ensure_active_database_within_limit(
        connection,
        context="dispatch admission preflight",
    )
    ensure_active_database_has_wake_reserve(
        connection,
        context="dispatch admission preflight",
    )
    ensure_checkpoint_store_within_limit(
        paths,
        context="dispatch admission preflight",
    )
    ensure_runtime_working_set_within_limit(
        paths,
        context="dispatch admission preflight",
    )


def _fault(protected_test_fault: str | None, point: str) -> None:
    if protected_test_fault == point:
        raise _InjectedDispatchAdmissionFault(
            f"protected dispatch admission fault: {point}"
        )


def admit_fixture_dispatch(
    runtime_root: Path | str,
    organism_id: str,
    *,
    request_id: str,
    fixture_case_id: str,
    clock: Clock | None = None,
    protected_test_fault: str | None = None,
) -> DispatchAdmissionResult:
    """Atomically admit and conservatively charge one deterministic fixture dispatch."""

    if protected_test_fault is not None and protected_test_fault not in _FAULT_POINTS:
        raise ValueError(f"unknown protected dispatch admission fault: {protected_test_fault}")
    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database)
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise DispatchAdmissionBusyError(
                    "dispatch admission is busy; this attempt was not queued"
                ) from exc
            raise

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            "SELECT * FROM organism WHERE singleton_id=1"
        ).fetchone()
        if organism is None:
            raise DispatchAdmissionRejectedError("dispatch organism singleton is missing")
        request_row, request_envelope = _load_request(connection, request_id)

        existing = _result_from_existing(
            connection,
            organism_id=organism_id,
            request_row=request_row,
            request_envelope=request_envelope,
            fixture_case_id=fixture_case_id,
        )
        if existing is not None:
            connection.rollback()
            return existing

        _require_admission_state(
            connection,
            paths,
            organism=organism,
            request_row=request_row,
            request_envelope=request_envelope,
        )

        reading = (clock or RealClock()).read()
        predicted_event_sequence = int(
            connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) + 1 FROM event"
            ).fetchone()[0]
        )
        dispatch = finalize_dispatch(
            _dispatch_identity(
                request_envelope=request_envelope,
                fixture_case_id=fixture_case_id,
            ),
            event_sequence=predicted_event_sequence,
            request_envelope=request_envelope,
        )
        charge = build_dispatch_charge(
            dispatch_id=dispatch["dispatch_id"],
            request_canonical_size_bytes=request_row["canonical_size_bytes"],
            request_envelope=request_envelope,
        )
        payload = build_dispatch_admission_payload(
            dispatch=dispatch,
            charge=charge,
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
                DISPATCH_ADMISSION_EVENT_TYPE,
                DISPATCH_SOURCE,
                canonical_json_bytes(payload).decode("utf-8"),
                PHASE2_SCHEMA_VERSION,
                ENVIRONMENT_VERSION,
                BUDGET_CONFIG_VERSION,
            ),
        )
        event_sequence = int(cursor.lastrowid)
        if event_sequence != predicted_event_sequence:
            raise DispatchAdmissionRejectedError(
                "dispatch admission event sequence prediction mismatch"
            )
        _fault(protected_test_fault, "after_event")

        dispatch_bytes = canonical_json_bytes(dispatch)
        connection.execute(
            """
            INSERT INTO consultation_dispatch (
                dispatch_id, request_id, organism_id, lineage_generation,
                dispatch_ordinal, event_sequence, configuration_version,
                envelope_json, canonical_size_bytes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dispatch["dispatch_id"],
                dispatch["request_id"],
                dispatch["organism_id"],
                dispatch["lineage_generation"],
                dispatch["dispatch_ordinal"],
                event_sequence,
                dispatch["configuration_version"],
                dispatch_bytes.decode("utf-8"),
                len(dispatch_bytes),
            ),
        )
        _fault(protected_test_fault, "after_dispatch")

        connection.execute(
            """
            INSERT INTO consultation_cost_charge (
                charge_id, dispatch_id, event_sequence, attempt_count,
                fixture_invocation_count, work_units, request_bytes,
                human_minutes, model_units, money_microunits, declared_latency_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                charge["charge_id"],
                dispatch["dispatch_id"],
                event_sequence,
                charge["attempt_count"],
                charge["fixture_invocation_count"],
                charge["work_units"],
                charge["request_bytes"],
                charge["human_minutes"],
                charge["model_units"],
                charge["money_microunits"],
                charge["declared_latency_ms"],
            ),
        )
        _fault(protected_test_fault, "after_charge")

        ensure_active_database_within_limit(
            connection,
            context="dispatch admission post-write",
        )
        ensure_active_database_has_wake_reserve(
            connection,
            context="dispatch admission post-write",
        )
        ensure_checkpoint_store_within_limit(
            paths,
            context="dispatch admission post-write",
        )
        ensure_runtime_working_set_within_limit(
            paths,
            context="dispatch admission post-write",
        )
        _fault(protected_test_fault, "before_commit")
        connection.commit()

        return DispatchAdmissionResult(
            created=True,
            organism_id=organism_id,
            request_id=request_id,
            dispatch_id=str(dispatch["dispatch_id"]),
            charge_id=str(charge["charge_id"]),
            event_sequence=event_sequence,
            fixture_case_id=fixture_case_id,
            request_envelope=deepcopy(request_envelope),
            dispatch_envelope=deepcopy(dispatch),
            charge=deepcopy(charge),
        )
    except (DispatchAdmissionBusyError, _InjectedDispatchAdmissionFault):
        if connection.in_transaction:
            connection.rollback()
        raise
    except DispatchAdmissionRejectedError:
        if connection.in_transaction:
            connection.rollback()
        raise
    except (SchemaValidationError, sqlite3.Error, OSError, ValueError) as exc:
        if connection.in_transaction:
            connection.rollback()
        raise DispatchAdmissionRejectedError(str(exc)) from exc
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()


_PROTECTED_FIXTURE_FAULTS: Final = frozenset(
    {"exit_after_admission", "fixture_exception", "probe_lock_released"}
)


def _protected_test_probe_lock_released(
    runtime_root: Path | str,
    organism_id: str,
) -> None:
    paths = OrganismPaths.build(runtime_root, organism_id)
    probe = connect_database(paths.database)
    try:
        probe.execute("BEGIN IMMEDIATE")
        counts = probe.execute(
            "SELECT (SELECT COUNT(*) FROM consultation_dispatch), "
            "(SELECT COUNT(*) FROM consultation_cost_charge), "
            "(SELECT COUNT(*) FROM event WHERE event_type=?)",
            (DISPATCH_ADMISSION_EVENT_TYPE,),
        ).fetchone()
        if tuple(counts) != (1, 1, 1):
            raise FixtureExecutionError(
                "protected fixture lock probe did not observe committed admission"
            )
        probe.rollback()
    finally:
        if probe.in_transaction:
            probe.rollback()
        probe.close()


def _terminalize_fixture_failure(
    runtime_root: Path | str,
    organism_id: str,
    *,
    admission: DispatchAdmissionResult,
    raw_package_bytes: bytes,
    clock: Clock | None,
) -> None:
    try:
        terminalize_fixture_dispatch(
            runtime_root,
            organism_id,
            dispatch_id=admission.dispatch_id,
            reason_code="fixture_output_invalid",
            raw_package_bytes=raw_package_bytes,
            clock=clock,
        )
    except Exception as exc:
        raise FixtureExecutionError(
            f"deterministic fixture failure terminalization failed: {exc}"
        ) from exc


def perform_fixture_dispatch(
    runtime_root: Path | str,
    organism_id: str,
    *,
    request_id: str,
    fixture_case_id: str,
    clock: Clock | None = None,
    protected_test_fault: str | None = None,
) -> FixtureDispatchResult:
    """Commit admission, then invoke only the exact deterministic fixture."""

    fixture_fault = (
        protected_test_fault
        if protected_test_fault in _PROTECTED_FIXTURE_FAULTS
        else None
    )
    admission_fault = None if fixture_fault is not None else protected_test_fault
    admission = admit_fixture_dispatch(
        runtime_root,
        organism_id,
        request_id=request_id,
        fixture_case_id=fixture_case_id,
        clock=clock,
        protected_test_fault=admission_fault,
    )
    if not admission.created:
        return FixtureDispatchResult(
            admission=admission,
            fixture_invoked=False,
            fixture_output=None,
        )
    try:
        if fixture_fault == "probe_lock_released":
            _protected_test_probe_lock_released(runtime_root, organism_id)
        if fixture_fault == "exit_after_admission":
            raise SystemExit(23)
        if fixture_fault == "fixture_exception":
            raise RuntimeError("protected deterministic fixture failure")
        output = run_deterministic_fixture(
            deepcopy(admission.request_envelope),
            fixture_case_id,
        )
    except Exception as exc:
        _terminalize_fixture_failure(
            runtime_root,
            organism_id,
            admission=admission,
            raw_package_bytes=b"",
            clock=clock,
        )
        raise FixtureExecutionError(str(exc)) from exc
    if not isinstance(output, bytes):
        _terminalize_fixture_failure(
            runtime_root,
            organism_id,
            admission=admission,
            raw_package_bytes=b"",
            clock=clock,
        )
        raise FixtureExecutionError("deterministic fixture output must be bytes")
    if len(output) > 16 * 1024:
        _terminalize_fixture_failure(
            runtime_root,
            organism_id,
            admission=admission,
            raw_package_bytes=bytes(output),
            clock=clock,
        )
        raise FixtureExecutionError("deterministic fixture output exceeds 16 KiB")
    return FixtureDispatchResult(
        admission=admission,
        fixture_invoked=True,
        fixture_output=bytes(output),
    )


__all__ = [
    "DispatchAdmissionBusyError",
    "DispatchAdmissionError",
    "DispatchAdmissionRejectedError",
    "DispatchAdmissionResult",
    "FixtureDispatchResult",
    "FixtureExecutionError",
    "admit_fixture_dispatch",
    "build_dispatch_admission_payload",
    "build_dispatch_charge",
    "charge_id_from_dispatch_id",
    "perform_fixture_dispatch",
]
