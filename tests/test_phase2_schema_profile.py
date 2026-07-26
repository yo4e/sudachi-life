from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sudachi_life.clock import FakeClock
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    ZERO_CAREGIVER_CONFIGURATION_VERSION,
    consultation_configuration_json,
)
from sudachi_life.storage import connect_database


_SCHEMA_V2_FINGERPRINT = "41ee900df99b3c1b44700e2de628d3151e907c8d0069f87098eb9fd72a3f6fec"

_LIMIT_NAMES = {
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
}

_FIXTURE_LIMITS = {
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


def test_consultation_configuration_objects_are_independent_golden_values() -> None:
    zero = json.loads(
        consultation_configuration_json(ZERO_CAREGIVER_CONFIGURATION_VERSION)
    )
    assert zero == {
        "configuration_version": ZERO_CAREGIVER_CONFIGURATION_VERSION,
        "limits": {name: 0 for name in sorted(_LIMIT_NAMES)},
        "protocol_version": 1,
    }

    fixture = json.loads(
        consultation_configuration_json(FIXTURE_CONFIGURATION_VERSION)
    )
    assert fixture == {
        "configuration_version": FIXTURE_CONFIGURATION_VERSION,
        "limits": _FIXTURE_LIMITS,
        "protocol_version": 1,
    }
    assert set(fixture["limits"]) == _LIMIT_NAMES


def test_schema_v2_sqlite_object_fingerprint_is_fixed(tmp_path: Path) -> None:
    runtime_root = tmp_path / "runtime"
    initialize_organism(
        runtime_root,
        "fingerprint",
        clock=FakeClock.fixed(
            wall_time_utc_us=1_700_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
        schema_version=2,
        consultation_configuration_version=ZERO_CAREGIVER_CONFIGURATION_VERSION,
    )
    connection = connect_database(
        OrganismPaths.build(runtime_root, "fingerprint").database,
        read_only=True,
    )
    try:
        rows = [
            tuple(row)
            for row in connection.execute(
                "SELECT type, name, tbl_name, sql FROM sqlite_master "
                "WHERE name NOT LIKE 'sqlite_%' AND sql IS NOT NULL "
                "ORDER BY type, name, tbl_name"
            )
        ]
    finally:
        connection.close()
    normalized = [
        (object_type, name, table, " ".join(sql.split()))
        for object_type, name, table, sql in rows
    ]
    encoded = json.dumps(normalized, separators=(",", ":")).encode("utf-8")
    assert len(normalized) == 46
    assert hashlib.sha256(encoded).hexdigest() == _SCHEMA_V2_FINGERPRINT
