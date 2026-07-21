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
