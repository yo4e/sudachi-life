from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.event_export import export_stable_events
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_disposition_runtime import (
    DispositionNoEligibleProposalError,
    perform_disposition_wake,
)
from sudachi_life.phase2_dispatch_runtime import perform_fixture_dispatch
from sudachi_life.phase2_ingress_runtime import (
    IngressRejectedError,
    ingress_external_package,
    validate_lineage_payload_projection,
)
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
)
from sudachi_life.rollback import (
    RollbackPreparationRejectedError,
    prepare_rollback_archive,
)
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_complete import complete_rollback
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_replace import replace_active_with_candidate
from sudachi_life.rollback_transform import transform_restore_candidate
from sudachi_life.runtime_storage import (
    ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
    active_database_allocated_bytes,
    checkpoint_store_bytes,
    runtime_working_set_bytes,
)
from sudachi_life.storage import connect_database, read_status


ORGANISM_ID = "r" * 64
CONSULTATION_TABLES = (
    "consultation_configuration",
    "consultation_request",
    "consultation_dispatch",
    "consultation_cost_charge",
    "consultation_response",
    "consultation_proposal",
    "consultation_ingress_receipt",
    "consultation_cost_completion",
    "consultation_disposition",
    "consultation_dispatch_terminal",
)


class _ClockPlan:
    def __init__(self) -> None:
        self.wall_time_utc_us = 2_700_000_000_000_000
        self.monotonic_ns = 10_000_000

    def fixed(self) -> FakeClock:
        reading = ClockReading(self.wall_time_utc_us, self.monotonic_ns)
        self.wall_time_utc_us += 1_000
        self.monotonic_ns += 1_000_000
        return FakeClock([reading])

    def wake(self) -> FakeClock:
        base_wall = self.wall_time_utc_us
        base_mono = self.monotonic_ns
        self.wall_time_utc_us += 10_000
        self.monotonic_ns += 50_000_000
        return FakeClock(
            [
                ClockReading(base_wall, base_mono),
                ClockReading(base_wall + 1, base_mono + 5_000_000),
                ClockReading(base_wall + 2, base_mono + 10_000_000),
                ClockReading(base_wall + 3, base_mono + 20_000_000),
                ClockReading(base_wall + 4, base_mono + 30_000_000),
            ]
        )

    def disposition(self) -> FakeClock:
        base_wall = self.wall_time_utc_us
        base_mono = self.monotonic_ns
        self.wall_time_utc_us += 10_000
        self.monotonic_ns += 30_000_000
        return FakeClock(
            [
                ClockReading(base_wall, base_mono),
                ClockReading(base_wall + 1, base_mono + 10_000_000),
                ClockReading(base_wall + 2, base_mono + 20_000_000),
            ]
        )


def _init(tmp_path: Path) -> tuple[Path, OrganismPaths, _ClockPlan]:
    root = tmp_path / "runtime"
    plan = _ClockPlan()
    initialize_organism(
        root,
        ORGANISM_ID,
        clock=plan.fixed(),
        schema_version=PHASE2_SCHEMA_VERSION,
        consultation_configuration_version=FIXTURE_CONFIGURATION_VERSION,
    )
    return root, OrganismPaths.build(root, ORGANISM_ID), plan


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


def _enqueue(paths: OrganismPaths, plan: _ClockPlan, name: str) -> None:
    enqueue_garden_tick(paths, name, clock=plan.fixed())


def _load_request(paths: OrganismPaths, request_id: str) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT envelope_json FROM consultation_request WHERE request_id=?",
            (request_id,),
        ).fetchone()
        assert row is not None
        value = json.loads(row["envelope_json"])
        assert isinstance(value, dict)
        return value
    finally:
        connection.close()


def _create_request(
    root: Path,
    paths: OrganismPaths,
    plan: _ClockPlan,
    *,
    expected_ordinal: int,
    name: str,
):
    _set_no_action_state(paths)
    _enqueue(paths, plan, name)
    wake = perform_garden_wake(
        root,
        paths.organism_id,
        seed=expected_ordinal,
        clock=plan.wake(),
    )
    assert wake.consultation_request is not None
    assert wake.consultation_request.created is True
    assert wake.consultation_request.request_id is not None
    request = _load_request(paths, wake.consultation_request.request_id)
    assert request["request_ordinal"] == expected_ordinal
    return wake, request


def _dispatch(
    root: Path,
    paths: OrganismPaths,
    plan: _ClockPlan,
    request_id: str,
):
    result = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=request_id,
        fixture_case_id="valid-abstain",
        clock=plan.fixed(),
    )
    assert result.fixture_invoked is True
    assert result.fixture_output is not None
    return result


def _ingress(
    root: Path,
    paths: OrganismPaths,
    plan: _ClockPlan,
    dispatch_result,
):
    result = ingress_external_package(
        root,
        paths.organism_id,
        dispatch_id=dispatch_result.admission.dispatch_id,
        raw_package_bytes=dispatch_result.fixture_output,
        clock=plan.fixed(),
    )
    assert result.proposal_id is not None
    return result


def _successful_checkpoint(
    root: Path,
    paths: OrganismPaths,
    plan: _ClockPlan,
    *,
    name: str,
):
    _set_successful_water_state(paths)
    _enqueue(paths, plan, name)
    wake = perform_garden_wake(
        root,
        paths.organism_id,
        seed=101,
        clock=plan.wake(),
    )
    assert wake.evaluation.success is True
    assert wake.consultation_request is None
    assert wake.checkpoint is not None
    return wake.checkpoint


def _complete_cycle(
    root: Path,
    paths: OrganismPaths,
    plan: _ClockPlan,
    *,
    expected_ordinal: int,
    prefix: str,
):
    wake, request = _create_request(
        root,
        paths,
        plan,
        expected_ordinal=expected_ordinal,
        name=f"{prefix}-request-{expected_ordinal}",
    )
    assert wake.consultation_request is not None
    assert wake.consultation_request.request_id is not None
    dispatched = _dispatch(
        root,
        paths,
        plan,
        wake.consultation_request.request_id,
    )
    ingress = _ingress(root, paths, plan, dispatched)
    disposition = perform_disposition_wake(
        root,
        paths.organism_id,
        clock=plan.disposition(),
    )
    assert disposition.proposal_id == ingress.proposal_id
    assert disposition.disposition == "accepted"
    assert disposition.reason_code == "no_supported_action_confirmed"
    checkpoint = _successful_checkpoint(
        root,
        paths,
        plan,
        name=f"{prefix}-reset-{expected_ordinal}",
    )
    return {
        "request": request,
        "dispatch": dispatched,
        "ingress": ingress,
        "disposition": disposition,
        "checkpoint": checkpoint,
    }


def _rollback_to(
    root: Path,
    paths: OrganismPaths,
    plan: _ClockPlan,
    *,
    selected_event_sequence: int,
    reason: str,
):
    archive = prepare_rollback_archive(
        root,
        paths.organism_id,
        selected_event_sequence,
    )
    begin = begin_rollback(
        root,
        paths.organism_id,
        archive.archive_id,
        clock=plan.fixed(),
    )
    source = build_restore_candidate(root, paths.organism_id)
    transformed = transform_restore_candidate(
        root,
        paths.organism_id,
        source.candidate_id,
        reason,
        clock=plan.fixed(),
    )
    replacement = replace_active_with_candidate(
        root,
        paths.organism_id,
        transformed.transformed_candidate_id,
    )
    completion = complete_rollback(
        root,
        paths.organism_id,
        transformed.transformed_candidate_id,
        clock=plan.fixed(),
    )
    assert completion.abandoned_lineage_generation == 0
    assert completion.new_lineage_generation == 1
    assert completion.status == "sleeping"
    return {
        "archive": archive,
        "begin": begin,
        "source": source,
        "transformed": transformed,
        "replacement": replacement,
        "completion": completion,
    }


def _consultation_snapshot(database: Path) -> dict[str, object]:
    connection = connect_database(database, read_only=True)
    try:
        tables = {
            table: [
                tuple(row)
                for row in connection.execute(
                    f'SELECT * FROM "{table}" ORDER BY rowid'
                ).fetchall()
            ]
            for table in CONSULTATION_TABLES
        }
        sequences = [
            tuple(row)
            for row in connection.execute(
                "SELECT name, seq FROM sqlite_sequence "
                "WHERE name LIKE 'consultation_%' ORDER BY name"
            ).fetchall()
        ]
        return {"tables": tables, "sqlite_sequence": sequences}
    finally:
        connection.close()


def _lineage_counts(paths: OrganismPaths, lineage_generation: int) -> dict[str, int]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "requests": int(
                connection.execute(
                    "SELECT COUNT(*) FROM consultation_request "
                    "WHERE lineage_generation=?",
                    (lineage_generation,),
                ).fetchone()[0]
            ),
            "dispatches": int(
                connection.execute(
                    "SELECT COUNT(*) FROM consultation_dispatch "
                    "WHERE lineage_generation=?",
                    (lineage_generation,),
                ).fetchone()[0]
            ),
            "charges": int(
                connection.execute(
                    "SELECT COUNT(*) FROM consultation_cost_charge c "
                    "JOIN consultation_dispatch d ON d.dispatch_id=c.dispatch_id "
                    "WHERE d.lineage_generation=?",
                    (lineage_generation,),
                ).fetchone()[0]
            ),
            "receipts": int(
                connection.execute(
                    "SELECT COUNT(*) FROM consultation_ingress_receipt r "
                    "JOIN consultation_request q ON q.request_id=r.request_id "
                    "WHERE q.lineage_generation=?",
                    (lineage_generation,),
                ).fetchone()[0]
            ),
            "proposals": int(
                connection.execute(
                    "SELECT COUNT(*) FROM consultation_proposal "
                    "WHERE lineage_generation=?",
                    (lineage_generation,),
                ).fetchone()[0]
            ),
            "dispositions": int(
                connection.execute(
                    "SELECT COUNT(*) FROM consultation_disposition "
                    "WHERE lineage_generation=?",
                    (lineage_generation,),
                ).fetchone()[0]
            ),
        }
    finally:
        connection.close()


def _logical_payload_bytes(paths: OrganismPaths, lineage_generation: int) -> int:
    connection = connect_database(paths.database, read_only=True)
    try:
        request_bytes = int(
            connection.execute(
                "SELECT COALESCE(SUM(canonical_size_bytes),0) "
                "FROM consultation_request WHERE lineage_generation=?",
                (lineage_generation,),
            ).fetchone()[0]
        )
        package_bytes = int(
            connection.execute(
                "SELECT COALESCE(SUM(r.measured_package_bytes),0) "
                "FROM consultation_ingress_receipt r "
                "JOIN consultation_request q ON q.request_id=r.request_id "
                "WHERE q.lineage_generation=?",
                (lineage_generation,),
            ).fetchone()[0]
        )
        return validate_lineage_payload_projection(request_bytes, package_bytes, 0)
    finally:
        connection.close()


def _attempt_fifth_request(
    root: Path,
    paths: OrganismPaths,
    plan: _ClockPlan,
    *,
    name: str,
):
    _set_no_action_state(paths)
    _enqueue(paths, plan, name)
    return perform_garden_wake(
        root,
        paths.organism_id,
        seed=999,
        clock=plan.wake(),
    )


def _assert_physical_limits(paths: OrganismPaths) -> None:
    connection = connect_database(paths.database, read_only=True)
    try:
        assert (
            active_database_allocated_bytes(connection)
            + ACTIVE_DATABASE_WAKE_RESERVE_BYTES
            <= 8 * 1024 * 1024
        )
    finally:
        connection.close()
    assert checkpoint_store_bytes(paths) <= 40 * 1024 * 1024
    assert runtime_working_set_bytes(paths) <= 64 * 1024 * 1024
    artifact_roots = (
        paths.checkpoints,
        paths.rollback_archives,
        paths.restore_candidates,
    )
    databases = [
        database
        for root in artifact_roots
        if root.exists()
        for database in root.rglob("*.sqlite3")
    ]
    assert databases
    assert all(database.stat().st_size <= 8 * 1024 * 1024 for database in databases)


def test_rollback_starts_fresh_epoch_preserves_history_and_bounds_two_lineages(
    tmp_path: Path,
) -> None:
    root, paths, plan = _init(tmp_path)

    selected_checkpoint = None
    for ordinal in range(1, 5):
        cycle = _complete_cycle(
            root,
            paths,
            plan,
            expected_ordinal=ordinal,
            prefix="old",
        )
        selected_checkpoint = cycle["checkpoint"]
    assert selected_checkpoint is not None

    selected_database = (
        paths.checkpoints / selected_checkpoint.checkpoint_id / "organism.sqlite3"
    )
    selected_consultation = _consultation_snapshot(selected_database)
    assert _lineage_counts(paths, 0) == {
        "requests": 4,
        "dispatches": 4,
        "charges": 4,
        "receipts": 4,
        "proposals": 4,
        "dispositions": 4,
    }
    old_payload_bytes = _logical_payload_bytes(paths, 0)
    assert old_payload_bytes > 0

    rollback = _rollback_to(
        root,
        paths,
        plan,
        selected_event_sequence=selected_checkpoint.event_sequence,
        reason="phase2 rollback lineage boundary",
    )

    artifact_databases = (
        rollback["archive"].archive_dir / "organism.sqlite3",
        paths.restore_candidates / rollback["source"].candidate_id / "organism.sqlite3",
        rollback["transformed"].transformed_candidate_dir / "organism.sqlite3",
        paths.database,
    )
    for database in artifact_databases:
        assert _consultation_snapshot(database) == selected_consultation

    assert read_status(paths).lineage_generation == 1
    assert _lineage_counts(paths, 0) == {
        "requests": 4,
        "dispatches": 4,
        "charges": 4,
        "receipts": 4,
        "proposals": 4,
        "dispositions": 4,
    }
    assert _lineage_counts(paths, 1) == {
        "requests": 0,
        "dispatches": 0,
        "charges": 0,
        "receipts": 0,
        "proposals": 0,
        "dispositions": 0,
    }
    assert _logical_payload_bytes(paths, 0) == old_payload_bytes
    assert _logical_payload_bytes(paths, 1) == 0

    for ordinal in range(1, 5):
        _complete_cycle(
            root,
            paths,
            plan,
            expected_ordinal=ordinal,
            prefix="new",
        )

    assert _lineage_counts(paths, 0)["charges"] == 4
    assert _lineage_counts(paths, 1) == {
        "requests": 4,
        "dispatches": 4,
        "charges": 4,
        "receipts": 4,
        "proposals": 4,
        "dispositions": 4,
    }
    assert _logical_payload_bytes(paths, 1) > 0

    fifth = _attempt_fifth_request(
        root,
        paths,
        plan,
        name="new-fifth-request",
    )
    assert fifth.consultation_request is not None
    assert fifth.consultation_request.as_dict() == {
        "canonical_size_bytes": None,
        "created": False,
        "event_sequence": None,
        "reason": "consultation_request_not_created_lineage_request_limit",
        "request_id": None,
    }

    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(
            connection.execute("SELECT COUNT(*) FROM consultation_cost_charge").fetchone()[0]
        ) == 8
        rollback_events = connection.execute(
            "SELECT event_type, source, lineage_generation, payload_json "
            "FROM event WHERE event_type IN "
            "('rollback_lineage_prepared','rollback_completed') "
            "ORDER BY event_sequence"
        ).fetchall()
        assert [row["event_type"] for row in rollback_events] == [
            "rollback_lineage_prepared",
            "rollback_completed",
        ]
        assert [row["source"] for row in rollback_events] == [
            "administration:rollback-candidate",
            "administration:rollback",
        ]
        assert all(int(row["lineage_generation"]) == 1 for row in rollback_events)
        prepared_payload = json.loads(rollback_events[0]["payload_json"])
        completed_payload = json.loads(rollback_events[1]["payload_json"])
        assert prepared_payload["archive_id"] == rollback["archive"].archive_id
        assert prepared_payload["source_restore_candidate_id"] == rollback["source"].candidate_id
        assert completed_payload["transformed_candidate_id"] == rollback[
            "transformed"
        ].transformed_candidate_id
        assert completed_payload["abandoned_lineage_generation"] == 0
        assert completed_payload["new_lineage_generation"] == 1
    finally:
        connection.close()

    status = read_status(paths)
    export = export_stable_events(
        root,
        paths.organism_id,
        status.latest_stable_event_sequence,
    )
    records = [json.loads(line) for line in export.export_path.read_text().splitlines()]
    assert records[0]["record_type"] == "manifest"
    assert records[0]["lineage_generation"] == 1
    events = records[1:]
    assert [event["event_sequence"] for event in events] == list(
        range(1, status.latest_stable_event_sequence + 1)
    )
    assert {event["lineage_generation"] for event in events} == {0, 1}
    assert sum(
        event["event_type"] == "consultation_request_created" for event in events
    ) == 8
    assert sum(
        event["event_type"] == "consultation_dispatch_admitted" for event in events
    ) == 8
    assert any(event["event_type"] == "rollback_completed" for event in events)

    archives_before = sorted(path.name for path in paths.rollback_archives.iterdir())
    with pytest.raises(
        RollbackPreparationRejectedError,
        match="requires no completed rollback history",
    ):
        prepare_rollback_archive(
            root,
            paths.organism_id,
            status.latest_stable_event_sequence,
        )
    assert sorted(path.name for path in paths.rollback_archives.iterdir()) == archives_before
    _assert_physical_limits(paths)


def test_old_lineage_unresolved_dispatch_does_not_block_and_late_package_fails(
    tmp_path: Path,
) -> None:
    root, paths, plan = _init(tmp_path)
    wake, _request = _create_request(
        root,
        paths,
        plan,
        expected_ordinal=1,
        name="old-dispatch-request",
    )
    assert wake.consultation_request is not None
    assert wake.consultation_request.request_id is not None
    old_dispatch = _dispatch(
        root,
        paths,
        plan,
        wake.consultation_request.request_id,
    )
    selected_checkpoint = _successful_checkpoint(
        root,
        paths,
        plan,
        name="checkpoint-old-dispatch",
    )

    _rollback_to(
        root,
        paths,
        plan,
        selected_event_sequence=selected_checkpoint.event_sequence,
        reason="preserve unresolved old dispatch",
    )
    assert _lineage_counts(paths, 0)["charges"] == 1
    assert _lineage_counts(paths, 1)["requests"] == 0

    before = _consultation_snapshot(paths.database)
    connection = connect_database(paths.database, read_only=True)
    try:
        event_count_before = int(connection.execute("SELECT COUNT(*) FROM event").fetchone()[0])
    finally:
        connection.close()
    rejected_clock = FakeClock([])
    with pytest.raises(IngressRejectedError, match="not in the current lineage"):
        ingress_external_package(
            root,
            paths.organism_id,
            dispatch_id=old_dispatch.admission.dispatch_id,
            raw_package_bytes=old_dispatch.fixture_output,
            clock=rejected_clock,
        )
    assert rejected_clock.read_count == 0
    assert _consultation_snapshot(paths.database) == before
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(connection.execute("SELECT COUNT(*) FROM event").fetchone()[0]) == event_count_before
    finally:
        connection.close()

    current_wake, current_request = _create_request(
        root,
        paths,
        plan,
        expected_ordinal=1,
        name="new-request-after-old-dispatch",
    )
    assert current_request["lineage_generation"] == 1
    assert current_wake.consultation_request is not None
    assert current_wake.consultation_request.request_id is not None
    _dispatch(
        root,
        paths,
        plan,
        current_wake.consultation_request.request_id,
    )
    assert _lineage_counts(paths, 0)["charges"] == 1
    assert _lineage_counts(paths, 1)["charges"] == 1


def test_old_lineage_proposal_is_inactive_and_current_proposal_is_selected(
    tmp_path: Path,
) -> None:
    root, paths, plan = _init(tmp_path)
    wake, _request = _create_request(
        root,
        paths,
        plan,
        expected_ordinal=1,
        name="old-proposal-request",
    )
    assert wake.consultation_request is not None
    assert wake.consultation_request.request_id is not None
    old_dispatch = _dispatch(
        root,
        paths,
        plan,
        wake.consultation_request.request_id,
    )
    old_ingress = _ingress(root, paths, plan, old_dispatch)
    assert old_ingress.proposal_id is not None
    selected_checkpoint = _successful_checkpoint(
        root,
        paths,
        plan,
        name="checkpoint-old-proposal",
    )

    _rollback_to(
        root,
        paths,
        plan,
        selected_event_sequence=selected_checkpoint.event_sequence,
        reason="preserve inactive old proposal",
    )
    assert _lineage_counts(paths, 0)["proposals"] == 1
    assert _lineage_counts(paths, 0)["dispositions"] == 0

    before = _consultation_snapshot(paths.database)
    no_proposal_clock = FakeClock([])
    with pytest.raises(
        DispositionNoEligibleProposalError,
        match="no eligible current-lineage proposal",
    ):
        perform_disposition_wake(
            root,
            paths.organism_id,
            clock=no_proposal_clock,
        )
    assert no_proposal_clock.read_count == 0
    assert _consultation_snapshot(paths.database) == before

    current_wake, current_request = _create_request(
        root,
        paths,
        plan,
        expected_ordinal=1,
        name="new-request-after-old-proposal",
    )
    assert current_request["lineage_generation"] == 1
    assert current_wake.consultation_request is not None
    assert current_wake.consultation_request.request_id is not None
    current_dispatch = _dispatch(
        root,
        paths,
        plan,
        current_wake.consultation_request.request_id,
    )
    current_ingress = _ingress(root, paths, plan, current_dispatch)
    current_disposition = perform_disposition_wake(
        root,
        paths.organism_id,
        clock=plan.disposition(),
    )
    assert current_disposition.proposal_id == current_ingress.proposal_id
    assert current_disposition.proposal_id != old_ingress.proposal_id

    connection = connect_database(paths.database, read_only=True)
    try:
        assert connection.execute(
            "SELECT 1 FROM consultation_disposition WHERE proposal_id=?",
            (old_ingress.proposal_id,),
        ).fetchone() is None
        current_row = connection.execute(
            "SELECT lineage_generation FROM consultation_disposition WHERE proposal_id=?",
            (current_ingress.proposal_id,),
        ).fetchone()
        assert current_row is not None
        assert int(current_row["lineage_generation"]) == 1
    finally:
        connection.close()
