from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3
from typing import Callable

import pytest

import sudachi_life.actions as actions_module
from sudachi_life.actions import execute_garden_action, select_garden_decision
from sudachi_life.budgets import WakeBudgetLedger
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import SudachiError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status
from sudachi_life.wake import WakeTransaction


_TABLE_ORDER = {
    "organism": "singleton_id",
    "budget_config": "singleton_id",
    "environment_state": "singleton_id",
    "garden_plot": "plot_id",
    "inventory": "singleton_id",
    "action_definition": "action_id",
    "inbox_event": "inbox_id",
    "event": "event_sequence",
    "checkpoint_registry": "event_sequence, checkpoint_id",
    "sqlite_sequence": "name",
}

_PROTECTED_DATABASE_KEYS = (
    "user_version",
    "sqlite_schema",
    "organism",
    "budget_config",
    "action_definition",
    "inbox_event",
    "event",
    "checkpoint_registry",
    "sqlite_sequence",
)

_PROHIBITED_SQL = (
    (
        "organism-identity",
        "UPDATE organism SET contract_version = 'tampered' WHERE singleton_id = 1",
    ),
    (
        "budget-configuration",
        "UPDATE budget_config SET config_json = '{}' WHERE singleton_id = 1",
    ),
    (
        "action-definition",
        "UPDATE action_definition SET version = version + 1 WHERE action_id = 'water_plot'",
    ),
    (
        "protected-garden-column",
        "UPDATE garden_plot SET stage = 'mature' WHERE plot_id = 'bed-a'",
    ),
    (
        "input-queue",
        "UPDATE inbox_event SET consumed = 1 WHERE external_event_id = 'slice-34-authority-probe'",
    ),
    (
        "forged-event",
        """
        INSERT INTO event (
            organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
            event_type, source, payload_json, schema_version,
            environment_version, budget_config_version
        )
        SELECT organism_id, lineage_generation, lifecycle_number, 0,
               'forged_action_event', 'organism:forged', '{}', schema_version,
               environment_version, budget_config_version
        FROM organism WHERE singleton_id = 1
        """,
    ),
    (
        "checkpoint-registry",
        """
        INSERT INTO checkpoint_registry (
            checkpoint_id, lineage_generation, event_sequence,
            manifest_sha256, database_sha256, database_size_bytes,
            created_wall_time_utc_us, registered_wall_time_utc_us, protected
        ) VALUES ('forged-checkpoint', 0, 0, 'x', 'y', 0, 0, 0, 0)
        """,
    ),
    ("schema-version", "PRAGMA user_version = 999"),
    ("append-only-trigger", "DROP TRIGGER event_no_update"),
    ("schema-object", "CREATE TABLE organism_action_rogue (id INTEGER)"),
)


def _wake_clock() -> FakeClock:
    return FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 40_000_000),
        ]
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _database_snapshot(connection: sqlite3.Connection) -> dict[str, object]:
    snapshot: dict[str, object] = {
        "user_version": connection.execute("PRAGMA user_version").fetchone()[0],
        "sqlite_schema": [
            tuple(row)
            for row in connection.execute(
                "SELECT type, name, tbl_name, rootpage, sql "
                "FROM sqlite_schema ORDER BY type, name"
            ).fetchall()
        ],
    }
    for table, ordering in _TABLE_ORDER.items():
        snapshot[table] = [
            tuple(row)
            for row in connection.execute(
                f'SELECT * FROM "{table}" ORDER BY {ordering}'
            ).fetchall()
        ]
    return snapshot


def _protected_repository_snapshot() -> dict[str, tuple[int, str]]:
    repository_root = Path(__file__).resolve().parents[1]
    candidates = [
        repository_root / "pyproject.toml",
        repository_root / "AGENTS.md",
        repository_root / "docs" / "MINIMAL_ORGANISM_CONTRACT.md",
        *sorted((repository_root / "docs" / "decisions").glob("*.md")),
        *sorted((repository_root / "src" / "sudachi_life").glob("*.py")),
        *sorted((repository_root / "tests").glob("*.py")),
    ]
    return {
        str(path.relative_to(repository_root)): (path.stat().st_size, _sha256(path))
        for path in candidates
    }


def _administrative_artifact_snapshot(
    paths: OrganismPaths,
) -> tuple[tuple[str, str, int, str | None], ...]:
    entries: list[tuple[str, str, int, str | None]] = []
    for root in (
        paths.checkpoints,
        paths.exports,
        paths.diagnostics,
        paths.rollback_archives,
        paths.restore_candidates,
    ):
        if not root.exists():
            entries.append((str(root.relative_to(paths.organism_dir)), "absent", 0, None))
            continue
        entries.append((str(root.relative_to(paths.organism_dir)), "directory", 0, None))
        for path in sorted(root.rglob("*")):
            relative = str(path.relative_to(paths.organism_dir))
            if path.is_symlink():
                entries.append((relative, "symlink", 0, None))
            elif path.is_dir():
                entries.append((relative, "directory", 0, None))
            elif path.is_file():
                entries.append((relative, "file", path.stat().st_size, _sha256(path)))
            else:
                entries.append((relative, "other", 0, None))
    return tuple(entries)


def _prepared_action_probe(initialized, external_event_id: str):
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(
        paths,
        external_event_id,
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    pre_probe_status = read_status(paths)
    wake = WakeTransaction.acquire(paths)
    claimed = wake.claim_oldest_garden_tick()
    observation = wake.build_observation()
    decision = select_garden_decision(observation)
    assert claimed.external_event_id == external_event_id
    assert decision.as_dict() == {
        "decision_type": "action",
        "action_id": "water_plot",
        "action_version": 1,
        "parameters": {"plot_id": "bed-a"},
        "reason": "fixed_policy_first_executable_dry_plot",
    }
    return runtime_root, initial, genesis, paths, pre_probe_status, wake, decision


def test_valid_action_changes_only_declared_mutable_garden_rows(initialized) -> None:
    (
        runtime_root,
        initial,
        genesis,
        paths,
        pre_probe_status,
        wake,
        decision,
    ) = _prepared_action_probe(initialized, "slice-34-valid-authority-probe")

    before_database = _database_snapshot(wake.connection)
    before_repository = _protected_repository_snapshot()
    before_artifacts = _administrative_artifact_snapshot(paths)
    ledger = WakeBudgetLedger.load(wake.connection)

    try:
        execute_garden_action(wake.connection, decision, ledger)
        after_database = _database_snapshot(wake.connection)

        for key in _PROTECTED_DATABASE_KEYS:
            assert after_database[key] == before_database[key]

        assert before_database["environment_state"] == [
            (1, "seed-garden-v1", 0, 0)
        ]
        assert after_database["environment_state"] == [
            (1, "seed-garden-v1", 1, 0)
        ]
        assert before_database["garden_plot"] == [
            ("bed-a", "sprout", 0, 0),
            ("bed-b", "mature", 1, 1),
        ]
        assert after_database["garden_plot"] == [
            ("bed-a", "sprout", 1, 0),
            ("bed-b", "mature", 1, 1),
        ]
        assert before_database["inventory"] == [(1, 1, 0)]
        assert after_database["inventory"] == [(1, 0, 0)]
        assert ledger.consumed["action_attempts"] == 1
        assert ledger.consumed["environment_mutations"] == 1
        assert _protected_repository_snapshot() == before_repository
        assert _administrative_artifact_snapshot(paths) == before_artifacts
    finally:
        wake.rollback_and_close()

    assert read_status(paths).as_dict() == pre_probe_status.as_dict()
    assert read_status(paths).latest_stable_checkpoint_id == genesis.checkpoint_id

    normal_clock = _wake_clock()
    result = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=34,
        clock=normal_clock,
    )
    assert normal_clock.read_count == 5
    assert result.decision.as_dict() == decision.as_dict()
    assert result.evaluation.success is True
    assert result.status == "sleeping"


@pytest.mark.parametrize(("probe_name", "statement"), _PROHIBITED_SQL)
def test_action_authority_rejects_protected_table_and_schema_mutation(
    initialized,
    monkeypatch: pytest.MonkeyPatch,
    probe_name: str,
    statement: str,
) -> None:
    (
        _,
        _,
        _,
        paths,
        pre_probe_status,
        wake,
        decision,
    ) = _prepared_action_probe(initialized, "slice-34-authority-probe")

    before_database = _database_snapshot(wake.connection)
    before_repository = _protected_repository_snapshot()
    before_artifacts = _administrative_artifact_snapshot(paths)
    ledger = WakeBudgetLedger.load(wake.connection)

    def prohibited_executor(
        connection: sqlite3.Connection,
        action_decision,
        action_ledger: WakeBudgetLedger,
        *,
        protected_test_failure_after_plot_write: bool = False,
    ) -> None:
        assert action_decision == decision
        assert action_ledger is ledger
        assert protected_test_failure_after_plot_write is False
        connection.execute(statement)

    monkeypatch.setattr(actions_module, "execute_water_plot", prohibited_executor)
    try:
        with pytest.raises(
            SudachiError,
            match="protected action SQL authority denied",
        ):
            execute_garden_action(wake.connection, decision, ledger)
        assert _database_snapshot(wake.connection) == before_database, probe_name
        assert _protected_repository_snapshot() == before_repository, probe_name
        assert _administrative_artifact_snapshot(paths) == before_artifacts, probe_name
        assert ledger.consumed["action_attempts"] == 0
        assert ledger.consumed["environment_mutations"] == 0
    finally:
        wake.rollback_and_close()

    assert read_status(paths).as_dict() == pre_probe_status.as_dict()
