from __future__ import annotations

import builtins
import inspect
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
from typing import Any, Callable

import pytest

from sudachi_life.actions import (
    ActionRejectedError,
    GardenActionDecision,
    execute_garden_action,
    select_garden_decision,
)
from sudachi_life.budgets import WakeBudgetLedger
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status
from sudachi_life.wake import WakeTransaction


_HARD_ZERO_CAPABILITIES = (
    "caregiver_consultations",
    "network_calls",
    "subprocess_calls",
    "external_mutable_writes",
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


def _relative_directories(root: Path) -> tuple[str, ...]:
    return tuple(
        str(path.relative_to(root))
        for path in sorted(root.rglob("*"))
        if path.is_dir() and not path.is_symlink()
    )


def _administrative_workspace_entries(paths: OrganismPaths) -> tuple[str, ...]:
    entries: list[str] = []
    for root in (
        paths.exports,
        paths.diagnostics,
        paths.rollback_archives,
        paths.restore_candidates,
    ):
        if not root.exists():
            continue
        entries.append(str(root.relative_to(paths.organism_dir)) + "/")
        entries.extend(
            str(path.relative_to(paths.organism_dir)) + ("/" if path.is_dir() else "")
            for path in sorted(root.rglob("*"))
        )
    return tuple(entries)


def _install_external_effect_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> list[str]:
    attempted: list[str] = []

    def deny(name: str) -> Callable[..., Any]:
        def guarded(*args: Any, **kwargs: Any) -> Any:
            attempted.append(name)
            raise AssertionError(
                f"organism action attempted guarded external interface: {name}"
            )

        return guarded

    monkeypatch.setattr(builtins, "open", deny("builtins.open"))
    monkeypatch.setattr(os, "open", deny("os.open"))
    monkeypatch.setattr(Path, "open", deny("Path.open"))

    for module, names in (
        (
            os,
            (
                "chmod",
                "chown",
                "lchmod",
                "lchown",
                "link",
                "makedirs",
                "mkdir",
                "mkfifo",
                "mknod",
                "remove",
                "removedirs",
                "rename",
                "renames",
                "replace",
                "rmdir",
                "symlink",
                "truncate",
                "unlink",
                "utime",
            ),
        ),
        (
            Path,
            (
                "chmod",
                "hardlink_to",
                "lchmod",
                "mkdir",
                "rename",
                "replace",
                "rmdir",
                "symlink_to",
                "touch",
                "unlink",
                "write_bytes",
                "write_text",
            ),
        ),
        (
            shutil,
            (
                "chown",
                "copy",
                "copy2",
                "copyfile",
                "copymode",
                "copystat",
                "copytree",
                "make_archive",
                "move",
                "rmtree",
                "unpack_archive",
            ),
        ),
        (
            tempfile,
            (
                "NamedTemporaryFile",
                "SpooledTemporaryFile",
                "TemporaryDirectory",
                "TemporaryFile",
                "mkdtemp",
                "mkstemp",
            ),
        ),
    ):
        for name in names:
            if hasattr(module, name):
                monkeypatch.setattr(module, name, deny(f"{module.__name__}.{name}"))

    monkeypatch.setattr(socket, "socket", deny("socket.socket"))
    monkeypatch.setattr(socket, "create_connection", deny("socket.create_connection"))

    for name in (
        "Popen",
        "call",
        "check_call",
        "check_output",
        "getoutput",
        "getstatusoutput",
        "run",
    ):
        monkeypatch.setattr(subprocess, name, deny(f"subprocess.{name}"))

    for name in (
        "execv",
        "execve",
        "execvp",
        "execvpe",
        "fork",
        "forkpty",
        "popen",
        "posix_spawn",
        "posix_spawnp",
        "spawnl",
        "spawnle",
        "spawnlp",
        "spawnlpe",
        "spawnv",
        "spawnve",
        "spawnvp",
        "spawnvpe",
        "system",
    ):
        if hasattr(os, name):
            monkeypatch.setattr(os, name, deny(f"os.{name}"))

    return attempted


def test_action_execution_has_no_external_workspace_or_effect_surface(
    initialized,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(
        paths,
        "slice-33-external-workspace-probe",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    pre_probe_status = read_status(paths)

    signature = inspect.signature(execute_garden_action)
    assert tuple(signature.parameters) == (
        "connection",
        "decision",
        "ledger",
        "protected_test_failure_after_plot_write",
    )
    assert tuple(
        parameter.kind for parameter in signature.parameters.values()
    ) == (
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    )
    assert signature.parameters[
        "protected_test_failure_after_plot_write"
    ].default is False

    path_like_target = tmp_path / "outside-organism" / "created-by-action.txt"
    assert not path_like_target.parent.exists()

    wake = WakeTransaction.acquire(paths)
    try:
        claimed = wake.claim_oldest_garden_tick()
        observation = wake.build_observation()
        decision = select_garden_decision(observation)
        assert claimed.external_event_id == "slice-33-external-workspace-probe"
        assert decision.as_dict() == {
            "decision_type": "action",
            "action_id": "water_plot",
            "action_version": 1,
            "parameters": {"plot_id": "bed-a"},
            "reason": "fixed_policy_first_executable_dry_plot",
        }

        directories_before = _relative_directories(paths.organism_dir)
        administrative_workspace_before = _administrative_workspace_entries(paths)

        valid_ledger = WakeBudgetLedger.load(wake.connection)
        rejected_ledger = WakeBudgetLedger.load(wake.connection)
        rejected_decision = GardenActionDecision(
            action_id="water_plot",
            action_version=1,
            plot_id=str(path_like_target),
            reason="protected_test_path_like_nonexistent_plot",
        )

        with monkeypatch.context() as guarded:
            attempted = _install_external_effect_guards(guarded)
            execute_garden_action(wake.connection, decision, valid_ledger)
            with pytest.raises(
                ActionRejectedError,
                match="water_plot target does not exist",
            ):
                execute_garden_action(
                    wake.connection,
                    rejected_decision,
                    rejected_ledger,
                )
            assert attempted == []

        assert tuple(
            wake.connection.execute(
                "SELECT moisture FROM garden_plot WHERE plot_id = 'bed-a'"
            ).fetchone()
        ) == (1,)
        assert valid_ledger.consumed["action_attempts"] == 1
        assert valid_ledger.consumed["environment_mutations"] == 1
        assert rejected_ledger.consumed["action_attempts"] == 1
        assert rejected_ledger.consumed["environment_mutations"] == 0
        for ledger in (valid_ledger, rejected_ledger):
            for capability in _HARD_ZERO_CAPABILITIES:
                assert ledger.limits[capability] == 0
                assert ledger.consumed[capability] == 0

        assert not path_like_target.exists()
        assert not path_like_target.parent.exists()
        assert _relative_directories(paths.organism_dir) == directories_before
        assert _administrative_workspace_entries(paths) == administrative_workspace_before
    finally:
        wake.rollback_and_close()

    rolled_back = read_status(paths)
    assert rolled_back.as_dict() == pre_probe_status.as_dict()
    assert rolled_back.latest_stable_checkpoint_id == genesis.checkpoint_id

    connection = connect_database(paths.database, read_only=True)
    try:
        assert tuple(
            connection.execute(
                "SELECT claimed_lifecycle_number, consumed FROM inbox_event "
                "WHERE external_event_id = ?",
                ("slice-33-external-workspace-probe",),
            ).fetchone()
        ) == (None, 0)
    finally:
        connection.close()

    normal_clock = _wake_clock()
    result = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=33,
        clock=normal_clock,
    )
    assert normal_clock.read_count == 5
    assert result.decision.as_dict() == decision.as_dict()
    assert result.evaluation.success is True
    assert result.status == "sleeping"
    for capability in _HARD_ZERO_CAPABILITIES:
        assert result.budget_ledger["limits"][capability] == 0
        assert result.budget_ledger["consumed"][capability] == 0
        assert result.budget_ledger["remaining"][capability] == 0
