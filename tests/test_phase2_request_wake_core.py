from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import BUDGET_CONFIG_VERSION
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import (
    CONSULTATION_PROTOCOL_VERSION,
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
    ZERO_CAREGIVER_CONFIGURATION_VERSION,
)
from sudachi_life.storage import connect_database, read_status

from phase1_audit_helpers import _wake_clock

REQUEST_SCHEMA = "sudachi.consultation.request/v1"
REQUEST_SOURCE = "organism:consultation.request"
REQUEST_POLICY_VERSION = "phase1-fixed-policy-v1"
REQUESTED_PROPOSAL_TYPES = ("abstain", "action_candidate", "defer")
ALLOWED_ACTION_IDS = ("harvest_plot", "water_plot")
PERMISSION_IDS = (
    "garden.action.execute:harvest_plot",
    "garden.action.execute:water_plot",
)
OBJECTIVE_ID = "seed-garden.harvest-fruit/v1"


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256_canonical(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _request_id(identity: dict[str, object]) -> str:
    digest = hashlib.sha256(
        b"sudachi.consultation/v1\nrequest-id\n" + _canonical_bytes(identity)
    ).hexdigest()
    return f"consultation-request:{digest}"


def _init(
    tmp_path: Path,
    *,
    configuration: str,
    organism_id: str,
) -> tuple[Path, OrganismPaths]:
    root = tmp_path / configuration
    initialize_organism(
        root,
        organism_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=1_900_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
        schema_version=PHASE2_SCHEMA_VERSION,
        consultation_configuration_version=configuration,
    )
    return root, OrganismPaths.build(root, organism_id)


def _set_no_applicable_action(paths: OrganismPaths) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE inventory SET water_units=0 WHERE singleton_id=1")
        connection.execute("UPDATE garden_plot SET moisture=1, fruit=0")
        connection.execute(
            "UPDATE environment_state SET objective_complete=0 WHERE singleton_id=1"
        )
        connection.commit()
    finally:
        connection.close()


def _set_objective_complete(paths: OrganismPaths) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE inventory SET harvested_fruit=1 WHERE singleton_id=1"
        )
        connection.execute("UPDATE garden_plot SET moisture=1, fruit=0")
        connection.execute(
            "UPDATE environment_state SET objective_complete=1 WHERE singleton_id=1"
        )
        connection.commit()
    finally:
        connection.close()


def _set_failure_streak(paths: OrganismPaths, value: int) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE organism SET consecutive_failures=? WHERE singleton_id=1",
            (value,),
        )
        connection.commit()
    finally:
        connection.close()


def _wake(root: Path, paths: OrganismPaths, external_id: str, *, seed: int = 1):
    enqueue_garden_tick(
        paths,
        external_id,
        clock=FakeClock([ClockReading(1_901_000_000_000_000, 20_000_000)]),
    )
    return perform_garden_wake(
        root,
        paths.organism_id,
        seed=seed,
        clock=_wake_clock(1_902_000_000_000_000 + seed * 100),
    )


def _operational_counts(paths: OrganismPaths) -> tuple[int, int]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return (
            int(connection.execute("SELECT COUNT(*) FROM consultation_request").fetchone()[0]),
            int(
                connection.execute(
                    "SELECT COUNT(*) FROM event "
                    "WHERE event_type='consultation_request_created'"
                ).fetchone()[0]
            ),
        )
    finally:
        connection.close()


def test_fixture_no_applicable_action_creates_exact_atomic_request_and_checkpoint(
    tmp_path: Path,
) -> None:
    root, paths = _init(
        tmp_path,
        configuration=FIXTURE_CONFIGURATION_VERSION,
        organism_id="fixture-request-core",
    )
    _set_no_applicable_action(paths)

    result = _wake(root, paths, "fixture-request-core-tick")
    request = result.consultation_request
    assert request is not None
    assert request.created is True
    assert request.reason is None
    assert result.decision.as_dict() == {
        "decision_type": "abstention",
        "reason": "no_applicable_action",
    }
    assert result.evaluation.success is False
    assert read_status(paths).consecutive_failures == 1
    assert _operational_counts(paths) == (1, 1)

    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute("SELECT * FROM consultation_request").fetchone()
        assert row is not None
        event = connection.execute(
            "SELECT event_sequence, lifecycle_number, source, payload_json, "
            "schema_version, budget_config_version FROM event "
            "WHERE event_type='consultation_request_created'"
        ).fetchone()
        assert event is not None
        observation_event = connection.execute(
            "SELECT event_sequence, payload_json FROM event "
            "WHERE lifecycle_number=? AND event_type='observation_created'",
            (result.lifecycle_number,),
        ).fetchone()
        assert observation_event is not None
        parent_sequences = tuple(
            int(item[0])
            for item in connection.execute(
                "SELECT event_sequence FROM event WHERE lifecycle_number=? "
                "AND event_sequence < ? ORDER BY event_sequence",
                (result.lifecycle_number, event["event_sequence"]),
            ).fetchall()
        )
    finally:
        connection.close()

    observation = json.loads(observation_event["payload_json"])
    objective_identity = {
        "environment_version": observation["environment_version"],
        "harvested_fruit": observation["inventory"]["harvested_fruit"],
        "objective_complete": observation["objective_complete"],
        "objective_id": OBJECTIVE_ID,
    }
    identity = {
        "allowed_action_ids": list(ALLOWED_ACTION_IDS),
        "budget_config_version": BUDGET_CONFIG_VERSION,
        "configuration_version": FIXTURE_CONFIGURATION_VERSION,
        "expiry_lifecycle_number": result.lifecycle_number + 2,
        "lineage_generation": 0,
        "lifecycle_number": result.lifecycle_number,
        "objective_digest": _sha256_canonical(objective_identity),
        "observation_digest": _sha256_canonical(observation),
        "organism_id": paths.organism_id,
        "permission_ids": list(PERMISSION_IDS),
        "policy_version": REQUEST_POLICY_VERSION,
        "protocol_version": CONSULTATION_PROTOCOL_VERSION,
        "reason_code": "no_applicable_action",
        "request_ordinal": 1,
        "request_schema": REQUEST_SCHEMA,
        "requested_proposal_types": list(REQUESTED_PROPOSAL_TYPES),
    }
    expected_request_id = _request_id(identity)
    expected_envelope = {
        "allowed_action_ids": list(ALLOWED_ACTION_IDS),
        "authority": {
            "source": REQUEST_SOURCE,
            "writer_category": "organism",
        },
        "budget_config_version": BUDGET_CONFIG_VERSION,
        "budget_snapshot": result.budget_ledger,
        "configuration_version": FIXTURE_CONFIGURATION_VERSION,
        "event_sequence": int(event["event_sequence"]),
        "expiry_lifecycle_number": result.lifecycle_number + 2,
        "lineage_generation": 0,
        "lifecycle_number": result.lifecycle_number,
        "objective_reference": {
            "digest": identity["objective_digest"],
            "objective_id": OBJECTIVE_ID,
        },
        "observation_reference": {
            "digest": identity["observation_digest"],
            "event_sequence": int(observation_event["event_sequence"]),
        },
        "organism_id": paths.organism_id,
        "parent_event_sequences": list(parent_sequences),
        "permission_ids": list(PERMISSION_IDS),
        "policy_version": REQUEST_POLICY_VERSION,
        "protocol_version": CONSULTATION_PROTOCOL_VERSION,
        "reason_code": "no_applicable_action",
        "request_id": expected_request_id,
        "request_ordinal": 1,
        "request_schema": REQUEST_SCHEMA,
        "requested_proposal_types": list(REQUESTED_PROPOSAL_TYPES),
    }
    expected_bytes = _canonical_bytes(expected_envelope)
    assert len(expected_bytes) <= 16 * 1024
    assert request.request_id == expected_request_id
    assert request.event_sequence == int(event["event_sequence"])
    assert request.canonical_size_bytes == len(expected_bytes)
    assert row["request_id"] == expected_request_id
    assert row["organism_id"] == paths.organism_id
    assert int(row["lineage_generation"]) == 0
    assert int(row["request_ordinal"]) == 1
    assert int(row["lifecycle_number"]) == result.lifecycle_number
    assert int(row["event_sequence"]) == int(event["event_sequence"])
    assert int(row["expiry_lifecycle_number"]) == result.lifecycle_number + 2
    assert row["configuration_version"] == FIXTURE_CONFIGURATION_VERSION
    assert row["envelope_json"].encode("utf-8") == expected_bytes
    assert int(row["canonical_size_bytes"]) == len(expected_bytes)
    assert event["source"] == REQUEST_SOURCE
    assert int(event["schema_version"]) == PHASE2_SCHEMA_VERSION
    assert event["budget_config_version"] == BUDGET_CONFIG_VERSION
    assert json.loads(event["payload_json"]) == {
        "canonical_size_bytes": len(expected_bytes),
        "request": expected_envelope,
    }

    manifest = validate_checkpoint_directory(result.checkpoint.checkpoint_dir)
    checkpoint = connect_database(
        result.checkpoint.checkpoint_dir / "organism.sqlite3",
        read_only=True,
    )
    try:
        checkpoint_row = checkpoint.execute(
            "SELECT request_id, envelope_json, canonical_size_bytes "
            "FROM consultation_request"
        ).fetchone()
        assert checkpoint_row is not None
        assert checkpoint_row["request_id"] == expected_request_id
        assert checkpoint_row["envelope_json"].encode("utf-8") == expected_bytes
        assert int(checkpoint_row["canonical_size_bytes"]) == len(expected_bytes)
    finally:
        checkpoint.close()
    assert manifest["event_sequence"] == result.checkpoint.event_sequence


def test_request_id_excludes_later_request_event_sequence(tmp_path: Path) -> None:
    root, paths = _init(
        tmp_path,
        configuration=FIXTURE_CONFIGURATION_VERSION,
        organism_id="fixture-request-id",
    )
    _set_no_applicable_action(paths)
    result = _wake(root, paths, "fixture-request-id-tick")
    request = result.consultation_request
    assert request is not None

    connection = connect_database(paths.database, read_only=True)
    try:
        envelope = json.loads(
            connection.execute(
                "SELECT envelope_json FROM consultation_request"
            ).fetchone()[0]
        )
    finally:
        connection.close()
    changed = dict(envelope)
    changed["event_sequence"] = int(envelope["event_sequence"]) + 1000
    identity = {
        "allowed_action_ids": changed["allowed_action_ids"],
        "budget_config_version": changed["budget_config_version"],
        "configuration_version": changed["configuration_version"],
        "expiry_lifecycle_number": changed["expiry_lifecycle_number"],
        "lineage_generation": changed["lineage_generation"],
        "lifecycle_number": changed["lifecycle_number"],
        "objective_digest": changed["objective_reference"]["digest"],
        "observation_digest": changed["observation_reference"]["digest"],
        "organism_id": changed["organism_id"],
        "permission_ids": changed["permission_ids"],
        "policy_version": changed["policy_version"],
        "protocol_version": changed["protocol_version"],
        "reason_code": changed["reason_code"],
        "request_ordinal": changed["request_ordinal"],
        "request_schema": changed["request_schema"],
        "requested_proposal_types": changed["requested_proposal_types"],
    }
    assert _request_id(identity) == request.request_id


def test_zero_caregiver_no_applicable_action_creates_no_consultation_state(
    tmp_path: Path,
) -> None:
    root, paths = _init(
        tmp_path,
        configuration=ZERO_CAREGIVER_CONFIGURATION_VERSION,
        organism_id="zero-request-control",
    )
    _set_no_applicable_action(paths)
    result = _wake(root, paths, "zero-request-control-tick")
    assert result.consultation_request is None
    assert _operational_counts(paths) == (0, 0)
    assert read_status(paths).consecutive_failures == 1


def test_fixture_action_and_objective_complete_paths_create_no_request(
    tmp_path: Path,
) -> None:
    action_root, action_paths = _init(
        tmp_path / "action",
        configuration=FIXTURE_CONFIGURATION_VERSION,
        organism_id="fixture-action-control",
    )
    action_result = _wake(action_root, action_paths, "fixture-action-control-tick")
    assert action_result.consultation_request is None
    assert _operational_counts(action_paths) == (0, 0)

    complete_root, complete_paths = _init(
        tmp_path / "complete",
        configuration=FIXTURE_CONFIGURATION_VERSION,
        organism_id="fixture-complete-control",
    )
    _set_objective_complete(complete_paths)
    complete_result = _wake(
        complete_root,
        complete_paths,
        "fixture-complete-control-tick",
    )
    assert complete_result.consultation_request is None
    assert complete_result.decision.as_dict()["reason"] == "objective_already_complete"
    assert _operational_counts(complete_paths) == (0, 0)


def test_maintenance_entering_wake_creates_no_request(tmp_path: Path) -> None:
    root, paths = _init(
        tmp_path,
        configuration=FIXTURE_CONFIGURATION_VERSION,
        organism_id="fixture-maintenance-control",
    )
    _set_no_applicable_action(paths)
    _set_failure_streak(paths, 2)
    result = _wake(root, paths, "fixture-maintenance-control-tick")
    assert result.status == "maintenance_required"
    assert result.consultation_request is None
    assert _operational_counts(paths) == (0, 0)
    assert read_status(paths).consecutive_failures == 3


def test_outstanding_request_does_not_block_later_garden_wake_or_duplicate(
    tmp_path: Path,
) -> None:
    root, paths = _init(
        tmp_path,
        configuration=FIXTURE_CONFIGURATION_VERSION,
        organism_id="fixture-outstanding-control",
    )
    _set_no_applicable_action(paths)
    first = _wake(root, paths, "fixture-outstanding-one", seed=1)
    assert first.consultation_request is not None

    second = _wake(root, paths, "fixture-outstanding-two", seed=2)
    assert second.status == "sleeping"
    assert second.consultation_request is None
    assert _operational_counts(paths) == (1, 1)
    assert read_status(paths).consecutive_failures == 2
