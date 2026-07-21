from __future__ import annotations

import json
from pathlib import Path

from sudachi_life.cli import main


def test_cli_init_and_status_json(tmp_path: Path, capsys) -> None:
    runtime = tmp_path / "runtime"

    assert main(["--runtime-dir", str(runtime), "init", "alpha", "--json"]) == 0
    init_payload = json.loads(capsys.readouterr().out)
    assert init_payload["organism_id"] == "alpha"
    assert init_payload["status"] == "sleeping"
    assert init_payload["genesis_checkpoint_id"].startswith("cp-g000000-e000000000002-")

    assert main(["--runtime-dir", str(runtime), "status", "alpha", "--json"]) == 0
    status_payload = json.loads(capsys.readouterr().out)
    assert status_payload["organism_id"] == "alpha"
    assert status_payload["status"] == "sleeping"
    assert status_payload["event_count"] == 3


def test_cli_reports_missing_organism(tmp_path: Path, capsys) -> None:
    result = main(
        ["--runtime-dir", str(tmp_path / "runtime"), "status", "missing", "--json"]
    )
    captured = capsys.readouterr()
    assert result == 1
    assert "organism database not found" in captured.err


def test_cli_runs_canonical_three_wake_sequence(tmp_path: Path, capsys) -> None:
    runtime = tmp_path / "runtime"
    assert main(["--runtime-dir", str(runtime), "init", "alpha", "--json"]) == 0
    capsys.readouterr()

    for event_id, seed in (("tick-1", "1"), ("tick-2", "2"), ("tick-3", "3")):
        assert main([
            "--runtime-dir", str(runtime), "enqueue", "alpha",
            "synthetic:garden_tick", "--id", event_id, "--json",
        ]) == 0
        capsys.readouterr()
        assert main([
            "--runtime-dir", str(runtime), "wake", "alpha",
            "--seed", seed, "--json",
        ]) == 0
        wake_payload = json.loads(capsys.readouterr().out)

    assert wake_payload["decision"] == {
        "decision_type": "abstention",
        "reason": "objective_already_complete",
    }
    assert wake_payload["evaluation"]["objective_complete_after"] is True
    assert wake_payload["budget_ledger"]["consumed"]["action_attempts"] == 0
    assert wake_payload["budget_ledger"]["consumed"]["environment_mutations"] == 0

    assert main(["--runtime-dir", str(runtime), "status", "alpha", "--json"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["lifecycle_number"] == 3
    assert status["objective_complete"] is True
    assert status["harvested_fruit"] == 1
    assert status["event_count"] == 35
