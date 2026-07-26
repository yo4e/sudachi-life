"""Protected schema-v2 consultation configuration and empty canonical objects."""

from __future__ import annotations

import json
from types import MappingProxyType
from typing import Final, Mapping

PHASE2_SCHEMA_VERSION: Final = 2
CONSULTATION_PROTOCOL_VERSION: Final = 1
ZERO_CAREGIVER_CONFIGURATION_VERSION: Final = "phase2-zero-caregiver-v1"
FIXTURE_CONFIGURATION_VERSION: Final = "phase2-fixture-v1"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


_LIMIT_NAMES: Final[tuple[str, ...]] = (
    "request_per_garden_wake",
    "outstanding_request_per_lineage",
    "requests_per_lineage",
    "dispatch_per_request",
    "charged_fixture_invocations_per_lineage",
    "successful_response_per_request",
    "proposal_per_successful_response",
    "proposal_considered_per_disposition_wake",
    "disposition_per_proposal",
    "clarification_rounds",
    "request_envelope_bytes",
    "external_package_bytes",
    "external_provenance_bytes",
    "logical_payload_bytes_per_lineage",
    "human_minutes",
    "model_units",
    "money_microunits",
    "declared_latency_ms",
    "additional_request_records",
    "disposition_semantic_steps",
    "disposition_records",
    "dispatch_records",
    "ingress_records",
    "terminalization_records",
)

_ZERO_LIMITS: Final[dict[str, int]] = {name: 0 for name in _LIMIT_NAMES}
_FIXTURE_LIMITS: Final[dict[str, int]] = {
    "request_per_garden_wake": 1,
    "outstanding_request_per_lineage": 1,
    "requests_per_lineage": 4,
    "dispatch_per_request": 1,
    "charged_fixture_invocations_per_lineage": 4,
    "successful_response_per_request": 1,
    "proposal_per_successful_response": 1,
    "proposal_considered_per_disposition_wake": 1,
    "disposition_per_proposal": 1,
    "clarification_rounds": 0,
    "request_envelope_bytes": 16 * 1024,
    "external_package_bytes": 16 * 1024,
    "external_provenance_bytes": 8 * 1024,
    "logical_payload_bytes_per_lineage": 64 * 1024,
    "human_minutes": 0,
    "model_units": 0,
    "money_microunits": 0,
    "declared_latency_ms": 0,
    "additional_request_records": 2,
    "disposition_semantic_steps": 10,
    "disposition_records": 12,
    "dispatch_records": 3,
    "ingress_records": 5,
    "terminalization_records": 3,
}


def _configuration(version: str, limits: Mapping[str, int]) -> dict[str, object]:
    return {
        "configuration_version": version,
        "limits": dict(limits),
        "protocol_version": CONSULTATION_PROTOCOL_VERSION,
    }


_CONSULTATION_CONFIGURATIONS_MUTABLE: Final[dict[str, dict[str, object]]] = {
    ZERO_CAREGIVER_CONFIGURATION_VERSION: _configuration(
        ZERO_CAREGIVER_CONFIGURATION_VERSION,
        _ZERO_LIMITS,
    ),
    FIXTURE_CONFIGURATION_VERSION: _configuration(
        FIXTURE_CONFIGURATION_VERSION,
        _FIXTURE_LIMITS,
    ),
}

CONSULTATION_CONFIGURATIONS: Final[Mapping[str, Mapping[str, object]]] = MappingProxyType(
    {
        key: MappingProxyType(value)
        for key, value in _CONSULTATION_CONFIGURATIONS_MUTABLE.items()
    }
)

ACCEPTED_CONSULTATION_CONFIGURATION_VERSIONS: Final[tuple[str, str]] = (
    ZERO_CAREGIVER_CONFIGURATION_VERSION,
    FIXTURE_CONFIGURATION_VERSION,
)

OPERATIONAL_CONSULTATION_TABLES: Final[tuple[str, ...]] = (
    "consultation_request",
    "consultation_dispatch",
    "consultation_cost_charge",
    "consultation_cost_completion",
    "consultation_response",
    "consultation_proposal",
    "consultation_ingress_receipt",
    "consultation_disposition",
    "consultation_dispatch_terminal",
)


def consultation_configuration_json(configuration_version: str) -> str:
    """Return exact protected canonical JSON for one accepted configuration."""

    try:
        value = _CONSULTATION_CONFIGURATIONS_MUTABLE[configuration_version]
    except KeyError as exc:
        raise ValueError(
            f"unsupported consultation configuration: {configuration_version!r}"
        ) from exc
    return _canonical_json(value)


IMMUTABLE_CONSULTATION_TABLES: Final[tuple[str, ...]] = (
    "consultation_configuration",
    *OPERATIONAL_CONSULTATION_TABLES,
)


def _immutable_triggers(table: str) -> str:
    return f"""
CREATE TRIGGER {table}_no_update BEFORE UPDATE ON {table}
BEGIN SELECT RAISE(ABORT, 'protected consultation rows are immutable'); END;
CREATE TRIGGER {table}_no_delete BEFORE DELETE ON {table}
BEGIN SELECT RAISE(ABORT, 'protected consultation rows are immutable'); END;
"""


PHASE2_SQL_EXTENSION: Final = """
CREATE TABLE consultation_configuration (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    protocol_version INTEGER NOT NULL CHECK (protocol_version = 1),
    configuration_version TEXT NOT NULL UNIQUE,
    configuration_json TEXT NOT NULL
);

CREATE TABLE consultation_request (
    request_id TEXT PRIMARY KEY,
    organism_id TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    request_ordinal INTEGER NOT NULL CHECK (request_ordinal BETWEEN 1 AND 4),
    lifecycle_number INTEGER NOT NULL CHECK (lifecycle_number >= 0),
    event_sequence INTEGER NOT NULL UNIQUE,
    expiry_lifecycle_number INTEGER NOT NULL,
    configuration_version TEXT NOT NULL,
    envelope_json TEXT NOT NULL,
    canonical_size_bytes INTEGER NOT NULL CHECK (canonical_size_bytes BETWEEN 0 AND 16384),
    UNIQUE (organism_id, lineage_generation, request_ordinal),
    CHECK (expiry_lifecycle_number = lifecycle_number + 2),
    FOREIGN KEY (event_sequence) REFERENCES event(event_sequence),
    FOREIGN KEY (configuration_version)
        REFERENCES consultation_configuration(configuration_version)
);

CREATE TABLE consultation_dispatch (
    dispatch_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    organism_id TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    dispatch_ordinal INTEGER NOT NULL CHECK (dispatch_ordinal = 1),
    event_sequence INTEGER NOT NULL UNIQUE,
    configuration_version TEXT NOT NULL,
    envelope_json TEXT NOT NULL,
    canonical_size_bytes INTEGER NOT NULL CHECK (canonical_size_bytes >= 0),
    FOREIGN KEY (request_id) REFERENCES consultation_request(request_id),
    FOREIGN KEY (event_sequence) REFERENCES event(event_sequence),
    FOREIGN KEY (configuration_version)
        REFERENCES consultation_configuration(configuration_version)
);

CREATE TABLE consultation_cost_charge (
    charge_id TEXT PRIMARY KEY,
    dispatch_id TEXT NOT NULL UNIQUE,
    event_sequence INTEGER NOT NULL UNIQUE,
    attempt_count INTEGER NOT NULL CHECK (attempt_count = 1),
    fixture_invocation_count INTEGER NOT NULL CHECK (fixture_invocation_count = 1),
    work_units INTEGER NOT NULL CHECK (work_units = 1),
    request_bytes INTEGER NOT NULL CHECK (request_bytes >= 0),
    human_minutes INTEGER NOT NULL CHECK (human_minutes = 0),
    model_units INTEGER NOT NULL CHECK (model_units = 0),
    money_microunits INTEGER NOT NULL CHECK (money_microunits = 0),
    declared_latency_ms INTEGER NOT NULL CHECK (declared_latency_ms = 0),
    FOREIGN KEY (dispatch_id) REFERENCES consultation_dispatch(dispatch_id),
    FOREIGN KEY (event_sequence) REFERENCES event(event_sequence)
);

CREATE TABLE consultation_cost_completion (
    completion_id TEXT PRIMARY KEY,
    dispatch_id TEXT NOT NULL UNIQUE,
    response_id TEXT,
    terminal_id TEXT,
    measured_package_bytes INTEGER NOT NULL CHECK (measured_package_bytes >= 0),
    CHECK ((response_id IS NULL) != (terminal_id IS NULL)),
    FOREIGN KEY (dispatch_id) REFERENCES consultation_dispatch(dispatch_id)
);

CREATE TABLE consultation_response (
    response_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    dispatch_id TEXT NOT NULL UNIQUE,
    organism_id TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    status TEXT NOT NULL CHECK (status IN ('proposals_returned', 'unavailable')),
    event_sequence INTEGER NOT NULL UNIQUE,
    envelope_json TEXT NOT NULL,
    canonical_size_bytes INTEGER NOT NULL CHECK (canonical_size_bytes BETWEEN 0 AND 16384),
    package_digest TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES consultation_request(request_id),
    FOREIGN KEY (dispatch_id) REFERENCES consultation_dispatch(dispatch_id),
    FOREIGN KEY (event_sequence) REFERENCES event(event_sequence)
);

CREATE TABLE consultation_proposal (
    proposal_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    dispatch_id TEXT NOT NULL UNIQUE,
    response_id TEXT NOT NULL UNIQUE,
    organism_id TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    proposal_ordinal INTEGER NOT NULL CHECK (proposal_ordinal = 1),
    proposal_type TEXT NOT NULL CHECK (proposal_type IN ('action_candidate', 'abstain', 'defer')),
    expiry_lifecycle_number INTEGER NOT NULL CHECK (expiry_lifecycle_number >= 0),
    content_digest TEXT NOT NULL,
    envelope_json TEXT NOT NULL,
    canonical_size_bytes INTEGER NOT NULL CHECK (canonical_size_bytes >= 0),
    FOREIGN KEY (request_id) REFERENCES consultation_request(request_id),
    FOREIGN KEY (dispatch_id) REFERENCES consultation_dispatch(dispatch_id),
    FOREIGN KEY (response_id) REFERENCES consultation_response(response_id)
);

CREATE TABLE consultation_ingress_receipt (
    receipt_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    dispatch_id TEXT NOT NULL UNIQUE,
    response_id TEXT NOT NULL UNIQUE,
    event_sequence INTEGER NOT NULL UNIQUE,
    package_digest TEXT NOT NULL,
    measured_package_bytes INTEGER NOT NULL CHECK (measured_package_bytes BETWEEN 0 AND 16384),
    FOREIGN KEY (request_id) REFERENCES consultation_request(request_id),
    FOREIGN KEY (dispatch_id) REFERENCES consultation_dispatch(dispatch_id),
    FOREIGN KEY (response_id) REFERENCES consultation_response(response_id),
    FOREIGN KEY (event_sequence) REFERENCES event(event_sequence)
);

CREATE TABLE consultation_disposition (
    disposition_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    dispatch_id TEXT NOT NULL UNIQUE,
    response_id TEXT NOT NULL UNIQUE,
    proposal_id TEXT NOT NULL UNIQUE,
    organism_id TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    lifecycle_number INTEGER NOT NULL CHECK (lifecycle_number >= 0),
    disposition TEXT NOT NULL CHECK (disposition IN ('accepted', 'rejected', 'deferred', 'clarification_requested')),
    reason_code TEXT NOT NULL,
    event_sequence INTEGER NOT NULL UNIQUE,
    envelope_json TEXT NOT NULL,
    FOREIGN KEY (request_id) REFERENCES consultation_request(request_id),
    FOREIGN KEY (dispatch_id) REFERENCES consultation_dispatch(dispatch_id),
    FOREIGN KEY (response_id) REFERENCES consultation_response(response_id),
    FOREIGN KEY (proposal_id) REFERENCES consultation_proposal(proposal_id),
    FOREIGN KEY (event_sequence) REFERENCES event(event_sequence)
);

CREATE TABLE consultation_dispatch_terminal (
    terminal_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL UNIQUE,
    dispatch_id TEXT NOT NULL UNIQUE,
    organism_id TEXT NOT NULL,
    lineage_generation INTEGER NOT NULL CHECK (lineage_generation >= 0),
    reason_code TEXT NOT NULL CHECK (reason_code IN ('dispatch_interrupted', 'fixture_output_invalid', 'expired_before_ingress')),
    rejected_package_digest TEXT,
    rejected_package_size_bytes INTEGER CHECK (rejected_package_size_bytes >= 0),
    event_sequence INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (request_id) REFERENCES consultation_request(request_id),
    FOREIGN KEY (dispatch_id) REFERENCES consultation_dispatch(dispatch_id),
    FOREIGN KEY (event_sequence) REFERENCES event(event_sequence)
);
""" + "".join(_immutable_triggers(table) for table in IMMUTABLE_CONSULTATION_TABLES)
