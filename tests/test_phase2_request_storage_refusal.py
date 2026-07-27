from __future__ import annotations

from pathlib import Path
import shutil

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import (
    _original_perform_garden_wake,
    perform_garden_wake,
)
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    PHASE2_SCHEMA_VERSION,
    OPERATIONAL_CONSULTATION_TABLES,
)
from sudachi_life.runtime_storage import active_database_allocated_bytes
from sudachi_life.storage import connect_database, read_status

from phase1_audit_helpers import _wake_clock

_ORIGINAL_TABLES = (
    "organism",
    "budget_config",
    "environment_state",
    "garden_plot",
    "inventory",
    "action_definition",
    "inbox_event",
    "event",
    "checkpoint_registry",
)


def _initialize(tmp_path: Path) -> tuple[Path, OrganismPaths]:
    root = tmp_path / "runtime"
    initialize_organism(
        root,
        "request-storage",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_000_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
        schema_version=PHASE2_SCHEMA_VERSION,
        consultation_configuration_version=FIXTURE_CONFIGURATION_VERSION,
    )
    paths = OrganismPaths.build(root, "request-storage")
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
    return root, paths


def _clone_runtime(source_root: Path, destination_root: Path) -> OrganismPaths:
    shutil.copytree(source_root, destination_root)
    return OrganismPaths.build(destination_root, "request-storage")


def _enqueue(paths: OrganismPaths) -> None:
    enqueue_garden_tick(
        paths,
        "request-storage-tick",
        clock=FakeClock([ClockReading(2_001_000_000_000_000, 20_000_000)]),
    )


def _snapshot(paths: OrganismPaths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        tables = {
            table: tuple(
                tuple(row)
                for row in connection.execute(
                    f"SELECT * FROM {table} ORDER BY rowid"
                ).fetchall()
            )
            for table in (*_ORIGINAL_TABLES, *OPERATIONAL_CONSULTATION_TABLES)
        }
        sequences = tuple(
            tuple(row)
            for row in connection.execute(
                "SELECT name, seq FROM sqlite_sequence ORDER BY name"
            ).fetchall()
        )
        allocated = active_database_allocated_bytes(connection)
    finally:
        connection.close()
    checkpoint_files = tuple(
        (path.relative_to(paths.checkpoints).as_posix(), path.read_bytes())
        for path in sorted(paths.checkpoints.rglob("*"))
        if path.is_file()
    )
    return {
        "tables": tables,
        "sequences": sequences,
        "allocated": allocated,
        "checkpoint_files": checkpoint_files,
        "status": read_status(paths),
    }


def _run_control(root: Path, paths: OrganismPaths):
    _enqueue(paths)
    return _original_perform_garden_wake(
        root,
        paths.organism_id,
        seed=7,
        clock=_wake_clock(2_002_000_000_000_000),
    )


def _run_refusal(
    root: Path,
    paths: OrganismPaths,
    *,
    reject_after_write: bool,
):
    _enqueue(paths)
    return perform_garden_wake(
        root,
        paths.organism_id,
        seed=7,
        clock=_wake_clock(2_002_000_000_000_000),
        protected_test_request_storage_reject_before_write=not reject_after_write,
        protected_test_request_storage_reject_after_write=reject_after_write,
    )


@pytest.mark.parametrize("reject_after_write", [False, True])
def test_request_storage_refusal_commits_exact_core_and_checkpoint(
    tmp_path: Path,
    reject_after_write: bool,
) -> None:
    base_root, _base_paths = _initialize(tmp_path / "base")
    control_root = tmp_path / "control"
    refusal_root = tmp_path / "refusal"
    control_paths = _clone_runtime(base_root, control_root)
    refusal_paths = _clone_runtime(base_root, refusal_root)

    control = _run_control(control_root, control_paths)
    refusal = _run_refusal(
        refusal_root,
        refusal_paths,
        reject_after_write=reject_after_write,
    )

    assert refusal.consultation_request is not None
    assert refusal.consultation_request.created is False
    assert (
        refusal.consultation_request.reason
        == "consultation_request_not_created_storage_budget"
    )
    assert refusal.consultation_request.request_id is None
    assert refusal.consultation_request.event_sequence is None
    assert refusal.consultation_request.canonical_size_bytes is None

    assert refusal.decision == control.decision
    assert refusal.evaluation == control.evaluation
    assert refusal.budget_exhaustion == control.budget_exhaustion
    assert refusal.budget_ledger == control.budget_ledger
    assert refusal.status == control.status == "sleeping"
    assert refusal.checkpoint.checkpoint_id == control.checkpoint.checkpoint_id
    assert _snapshot(refusal_paths) == _snapshot(control_paths)
