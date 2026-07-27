from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_disposition_runtime import perform_disposition_wake
from sudachi_life.phase2_dispatch_runtime import perform_fixture_dispatch
from sudachi_life.phase2_fixture import run_deterministic_fixture
from sudachi_life.phase2_ingress_runtime import (
    IngressRejectedError,
    ingress_external_package,
    validate_lineage_payload_projection,
)
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
)
from sudachi_life.runtime_storage import (
    ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
    active_database_allocated_bytes,
    checkpoint_store_bytes,
    runtime_working_set_bytes,
)
from sudachi_life.storage import connect_database, read_status


MAX_ORGANISM_ID = "o" * 64
PARENT_TYPES = [
    "wake_accepted",
    "input_claimed",
    "observation_created",
    "action_abstained",
    "evaluation_completed",
    "failure_streak_updated",
    "lifecycle_completed",
    "budget_ledger",
]
VALID_PACKAGE_CASES = (
    "valid-action-candidate",
    "valid-abstain",
    "valid-defer",
    "unavailable",
)


def _wake_clock(base: int) -> FakeClock:
    return FakeClock(
        [
            ClockReading(base, 10_000_000),
            ClockReading(base + 1, 15_000_000),
            ClockReading(base + 2, 20_000_000),
            ClockReading(base + 3, 30_000_000),
            ClockReading(base + 4, 40_000_000),
        ]
    )


def _disposition_clock(base: int) -> FakeClock:
    return FakeClock(
        [
            ClockReading(base, 50_000_000),
            ClockReading(base + 1, 60_000_000),
            ClockReading(base + 2, 70_000_000),
        ]
    )


def _init(tmp_path: Path) -> tuple[Path, OrganismPaths]:
    root = tmp_path / "runtime"
    initialize_organism(
        root,
        MAX_ORGANISM_ID,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_500_000_000_000_000,
            monotonic_ns=1_000_000,
        ),
        schema_version=PHASE2_SCHEMA_VERSION,
        consultation_configuration_version=FIXTURE_CONFIGURATION_VERSION,
    )
    return root, OrganismPaths.build(root, MAX_ORGANISM_ID)


def _set_no_action_state(paths: OrganismPaths) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE inventory SET water_units=0, harvested_fruit=0 WHERE singleton_id=1"
        )
        connection.execute("UPDATE garden_plot SET moisture=1, fruit=0")
        connection.execute(
            "UPDATE environment_state SET objective_complete=0 WHERE singleton_id=1"
        )
        connection.commit()
    finally:
        connection.close()


def _set_successful_water_state(paths: OrganismPaths) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE inventory SET water_units=1 WHERE singleton_id=1")
        connection.execute(
            "UPDATE garden_plot SET moisture=0, fruit=0 WHERE plot_id='bed-a'"
        )
        connection.execute(
            "UPDATE environment_state SET objective_complete=0 WHERE singleton_id=1"
        )
        connection.commit()
    finally:
        connection.close()


def _enqueue(paths: OrganismPaths, name: str, ordinal: int) -> None:
    enqueue_garden_tick(
        paths,
        name,
        clock=FakeClock(
            [ClockReading(2_510_000_000_000_000 + ordinal, 2_000_000 + ordinal)]
        ),
    )


def _load_request(paths: OrganismPaths, request_id: str) -> tuple[dict, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT * FROM consultation_request WHERE request_id=?",
            (request_id,),
        ).fetchone()
        assert row is not None
        return json.loads(row["envelope_json"]), row
    finally:
        connection.close()


def _independent_request_id(envelope: dict[str, object]) -> str:
    identity = {
        "allowed_action_ids": envelope["allowed_action_ids"],
        "budget_config_version": envelope["budget_config_version"],
        "configuration_version": envelope["configuration_version"],
        "expiry_lifecycle_number": envelope["expiry_lifecycle_number"],
        "lineage_generation": envelope["lineage_generation"],
        "lifecycle_number": envelope["lifecycle_number"],
        "objective_digest": envelope["objective_reference"]["digest"],
        "observation_digest": envelope["observation_reference"]["digest"],
        "organism_id": envelope["organism_id"],
        "permission_ids": envelope["permission_ids"],
        "policy_version": envelope["policy_version"],
        "protocol_version": envelope["protocol_version"],
        "reason_code": envelope["reason_code"],
        "request_ordinal": envelope["request_ordinal"],
        "request_schema": envelope["request_schema"],
        "requested_proposal_types": envelope["requested_proposal_types"],
    }
    encoded = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "consultation-request:" + hashlib.sha256(
        b"sudachi.consultation/v1\nrequest-id\n" + encoded
    ).hexdigest()


def _largest_case(request: dict[str, object]) -> tuple[str, dict[str, int]]:
    sizes = {
        case: len(run_deterministic_fixture(request, case))
        for case in VALID_PACKAGE_CASES
    }
    largest = max(sizes, key=lambda case: (sizes[case], case))
    assert largest == "valid-abstain"
    return largest, sizes


def _request_cycle(
    root: Path,
    paths: OrganismPaths,
    *,
    ordinal: int,
) -> tuple[dict[str, object], int, int]:
    _set_no_action_state(paths)
    _enqueue(paths, f"request-{ordinal}", ordinal * 10)
    wake = perform_garden_wake(
        root,
        paths.organism_id,
        seed=ordinal,
        clock=_wake_clock(2_520_000_000_000_000 + ordinal * 100),
    )
    assert wake.consultation_request is not None
    assert wake.consultation_request.created is True
    assert wake.consultation_request.request_id is not None
    request, request_row = _load_request(
        paths,
        wake.consultation_request.request_id,
    )
    assert request["request_ordinal"] == ordinal
    case_id, _sizes = _largest_case(request)
    dispatched = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id=case_id,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_530_000_000_000_000 + ordinal,
            monotonic_ns=80_000_000 + ordinal,
        ),
    )
    assert dispatched.fixture_output is not None
    ingress = ingress_external_package(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        raw_package_bytes=dispatched.fixture_output,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_540_000_000_000_000 + ordinal,
            monotonic_ns=90_000_000 + ordinal,
        ),
    )
    assert ingress.proposal_id is not None
    disposition = perform_disposition_wake(
        root,
        paths.organism_id,
        clock=_disposition_clock(2_550_000_000_000_000 + ordinal * 100),
    )
    assert disposition.proposal_id == ingress.proposal_id
    assert disposition.disposition == "accepted"
    assert disposition.reason_code == "no_supported_action_confirmed"
    return request, int(request_row["canonical_size_bytes"]), len(dispatched.fixture_output)


def _successful_reset(root: Path, paths: OrganismPaths, ordinal: int) -> None:
    _set_successful_water_state(paths)
    _enqueue(paths, f"reset-{ordinal}", ordinal * 10 + 1)
    wake = perform_garden_wake(
        root,
        paths.organism_id,
        seed=100 + ordinal,
        clock=_wake_clock(2_560_000_000_000_000 + ordinal * 100),
    )
    assert wake.evaluation.success is True
    assert wake.consultation_request is None
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(
            connection.execute(
                "SELECT consecutive_failures FROM organism WHERE singleton_id=1"
            ).fetchone()[0]
        ) == 0
    finally:
        connection.close()


def test_pure_lineage_payload_projection_boundary_and_type_corpus() -> None:
    assert validate_lineage_payload_projection(10, 20, 65506) == 65536
    with pytest.raises(IngressRejectedError, match="64 KiB"):
        validate_lineage_payload_projection(10, 20, 65507)
    for values in (
        (True, 0, 0),
        (0, False, 0),
        (0, 0, True),
        (-1, 0, 0),
        (0, -1, 0),
        (0, 0, -1),
        (1.0, 0, 0),
        (0, "1", 0),
        (0, 0, None),
    ):
        with pytest.raises(IngressRejectedError, match="byte count"):
            validate_lineage_payload_projection(*values)


def test_four_legal_cycles_largest_request_fifth_refusal_and_payload_maximum(
    tmp_path: Path,
) -> None:
    root, paths = _init(tmp_path)
    requests: list[dict[str, object]] = []
    request_sizes: list[int] = []
    package_sizes: list[int] = []

    for ordinal in range(1, 5):
        request, request_size, package_size = _request_cycle(
            root,
            paths,
            ordinal=ordinal,
        )
        requests.append(request)
        request_sizes.append(request_size)
        package_sizes.append(package_size)
        _successful_reset(root, paths, ordinal)

    fourth = requests[-1]
    assert len(fourth["organism_id"]) == 64
    assert fourth["request_ordinal"] == 4
    assert fourth["allowed_action_ids"] == ["harvest_plot", "water_plot"]
    assert fourth["permission_ids"] == [
        "garden.action.execute:harvest_plot",
        "garden.action.execute:water_plot",
    ]
    assert fourth["requested_proposal_types"] == [
        "abstain",
        "action_candidate",
        "defer",
    ]
    assert len(fourth["parent_event_sequences"]) == 8
    assert fourth["parent_event_sequences"] == sorted(
        set(fourth["parent_event_sequences"])
    )
    assert fourth["request_id"] == _independent_request_id(fourth)
    fourth_bytes = json.dumps(
        fourth,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert len(fourth_bytes) == request_sizes[-1]
    assert len(fourth_bytes) < 16 * 1024

    connection = connect_database(paths.database, read_only=True)
    try:
        parent_rows = connection.execute(
            "SELECT event_sequence, event_type, lineage_generation, lifecycle_number "
            "FROM event WHERE event_sequence IN ("
            + ",".join("?" for _ in fourth["parent_event_sequences"])
            + ") ORDER BY event_sequence",
            tuple(fourth["parent_event_sequences"]),
        ).fetchall()
        assert [row["event_type"] for row in parent_rows] == PARENT_TYPES
        assert all(int(row["lineage_generation"]) == 0 for row in parent_rows)
        assert all(
            int(row["lifecycle_number"]) == fourth["lifecycle_number"]
            for row in parent_rows
        )
        request_event = connection.execute(
            "SELECT event_sequence, event_type FROM event WHERE event_sequence=?",
            (fourth["event_sequence"],),
        ).fetchone()
        assert request_event["event_type"] == "consultation_request_created"
        assert int(request_event["event_sequence"]) > max(
            fourth["parent_event_sequences"]
        )
        assert int(
            connection.execute("SELECT COUNT(*) FROM consultation_request").fetchone()[0]
        ) == 4
        assert int(
            connection.execute("SELECT COUNT(*) FROM consultation_cost_charge").fetchone()[0]
        ) == 4
        assert int(
            connection.execute("SELECT COUNT(*) FROM consultation_ingress_receipt").fetchone()[0]
        ) == 4
        assert int(
            connection.execute("SELECT COUNT(*) FROM consultation_disposition").fetchone()[0]
        ) == 4
        sql_request_bytes = int(
            connection.execute(
                "SELECT SUM(canonical_size_bytes) FROM consultation_request "
                "WHERE lineage_generation=0"
            ).fetchone()[0]
        )
        sql_package_bytes = int(
            connection.execute(
                "SELECT SUM(r.measured_package_bytes) "
                "FROM consultation_ingress_receipt r "
                "JOIN consultation_request q ON q.request_id=r.request_id "
                "WHERE q.lineage_generation=0"
            ).fetchone()[0]
        )
        metadata_bytes = int(
            connection.execute(
                "SELECT COALESCE(SUM(canonical_size_bytes),0) FROM consultation_response"
            ).fetchone()[0]
        ) + int(
            connection.execute(
                "SELECT COALESCE(SUM(canonical_size_bytes),0) FROM consultation_proposal"
            ).fetchone()[0]
        )
    finally:
        connection.close()

    legal_payload = sum(request_sizes) + sum(package_sizes)
    assert legal_payload == sql_request_bytes + sql_package_bytes
    assert legal_payload == validate_lineage_payload_projection(
        sql_request_bytes,
        sql_package_bytes,
        0,
    )
    assert legal_payload < 64 * 1024
    assert legal_payload + metadata_bytes > legal_payload

    before_status = read_status(paths)
    before_counts = (4, 4, 4, 4)
    _set_no_action_state(paths)
    _enqueue(paths, "fifth-request", 999)
    fifth = perform_garden_wake(
        root,
        paths.organism_id,
        seed=999,
        clock=_wake_clock(2_570_000_000_000_000),
    )
    assert fifth.consultation_request is not None
    assert fifth.consultation_request.as_dict() == {
        "canonical_size_bytes": None,
        "created": False,
        "event_sequence": None,
        "reason": "consultation_request_not_created_lineage_request_limit",
        "request_id": None,
    }
    assert fifth.lifecycle_number == before_status.lifecycle_number + 1
    assert fifth.checkpoint is not None

    connection = connect_database(paths.database, read_only=True)
    try:
        after_counts = (
            int(connection.execute("SELECT COUNT(*) FROM consultation_request").fetchone()[0]),
            int(connection.execute("SELECT COUNT(*) FROM consultation_cost_charge").fetchone()[0]),
            int(connection.execute("SELECT COUNT(*) FROM consultation_ingress_receipt").fetchone()[0]),
            int(connection.execute("SELECT COUNT(*) FROM consultation_disposition").fetchone()[0]),
        )
        assert after_counts == before_counts
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type='consultation_request_created'"
            ).fetchone()[0]
        ) == 4
        allocated = active_database_allocated_bytes(connection)
        assert allocated + ACTIVE_DATABASE_WAKE_RESERVE_BYTES <= 8 * 1024 * 1024
    finally:
        connection.close()

    assert checkpoint_store_bytes(paths) <= 40 * 1024 * 1024
    assert runtime_working_set_bytes(paths) <= 64 * 1024 * 1024
    status = read_status(paths)
    assert status.latest_stable_checkpoint_id is not None
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id
    databases = list(checkpoint_dir.rglob("*.sqlite3"))
    assert databases
    assert all(path.stat().st_size <= 8 * 1024 * 1024 for path in databases)
