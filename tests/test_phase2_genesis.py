from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

import pytest

from sudachi_life.checkpoints import validate_checkpoint_directory
from sudachi_life.cli import build_parser, main
from sudachi_life.clock import FakeClock
from sudachi_life.constants import BUDGET_CONFIG_VERSION, PHASE1_BUDGETS
from sudachi_life.errors import CheckpointError, SchemaValidationError
from sudachi_life.organism import get_status, initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import (
    ACCEPTED_CONSULTATION_CONFIGURATION_VERSIONS,
    CONSULTATION_PROTOCOL_VERSION,
    FIXTURE_CONFIGURATION_VERSION,
    OPERATIONAL_CONSULTATION_TABLES,
    PHASE2_SCHEMA_VERSION,
    ZERO_CAREGIVER_CONFIGURATION_VERSION,
    consultation_configuration_json,
)
from sudachi_life.storage import connect_database, read_status

ORIGINAL_TABLES = (
    "organism", "budget_config", "environment_state", "garden_plot",
    "inventory", "action_definition", "inbox_event", "event",
    "checkpoint_registry",
)


def _clock() -> FakeClock:
    return FakeClock.fixed(
        wall_time_utc_us=1_700_000_000_000_000,
        monotonic_ns=10_000_000,
    )


def _init_v2(
    tmp_path: Path,
    config: str = ZERO_CAREGIVER_CONFIGURATION_VERSION,
    organism_id: str = "sudachi-v2",
):
    root = tmp_path / f"runtime-{config}"
    status, checkpoint = initialize_organism(
        root,
        organism_id,
        clock=_clock(),
        schema_version=PHASE2_SCHEMA_VERSION,
        consultation_configuration_version=config,
    )
    return root, status, checkpoint


def _columns(connection: sqlite3.Connection, table: str):
    return tuple(tuple(row) for row in connection.execute(f"PRAGMA table_info({table})"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _replace_config_json(database: Path, value: dict[str, object]) -> None:
    connection = connect_database(database)
    try:
        trigger_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='trigger' "
            "AND name='consultation_configuration_no_update'"
        ).fetchone()[0]
        connection.execute("DROP TRIGGER consultation_configuration_no_update")
        connection.execute(
            "UPDATE consultation_configuration SET configuration_json=?",
            (json.dumps(value, sort_keys=True, separators=(",", ":")),),
        )
        connection.execute(trigger_sql)
    finally:
        connection.close()


def test_phase1_default_surface_and_schema_remain_exact(initialized) -> None:
    root, status, _ = initialized
    assert status.schema_version == 1
    assert status.budget_config_version == BUDGET_CONFIG_VERSION
    assert status.consultation_configuration_version is None
    assert "consultation_configuration_version" not in status.as_dict()
    connection = connect_database(
        OrganismPaths.build(root, status.organism_id).database,
        read_only=True,
    )
    try:
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "consultation_configuration" not in names
        assert not names.intersection(OPERATIONAL_CONSULTATION_TABLES)
    finally:
        connection.close()


@pytest.mark.parametrize(
    "config", ACCEPTED_CONSULTATION_CONFIGURATION_VERSIONS
)
def test_schema_v2_genesis_configuration_and_empty_objects_are_exact(
    tmp_path: Path,
    config: str,
) -> None:
    root, status, checkpoint = _init_v2(
        tmp_path,
        config,
        f"organism-{config}",
    )
    assert status.schema_version == PHASE2_SCHEMA_VERSION
    assert status.budget_config_version == BUDGET_CONFIG_VERSION
    assert status.consultation_configuration_version == config
    assert status.status == "sleeping"
    assert status.latest_stable_checkpoint_id == checkpoint.checkpoint_id
    assert status.latest_stable_event_sequence == 2
    assert status.event_count == 3

    paths = OrganismPaths.build(root, status.organism_id)
    manifest = validate_checkpoint_directory(checkpoint.checkpoint_dir)
    assert manifest["schema_version"] == PHASE2_SCHEMA_VERSION
    assert manifest["budget_config_version"] == BUDGET_CONFIG_VERSION
    assert get_status(root, status.organism_id) == status

    connection = connect_database(paths.database)
    try:
        row = connection.execute(
            "SELECT * FROM consultation_configuration"
        ).fetchone()
        assert dict(row) == {
            "singleton_id": 1,
            "protocol_version": CONSULTATION_PROTOCOL_VERSION,
            "configuration_version": config,
            "configuration_json": consultation_configuration_json(config),
        }
        assert row["configuration_json"] == json.dumps(
            json.loads(row["configuration_json"]),
            sort_keys=True,
            separators=(",", ":"),
        )
        for table in OPERATIONAL_CONSULTATION_TABLES:
            assert connection.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0] == 0
        sequence_names = {
            item[0] for item in connection.execute("SELECT name FROM sqlite_sequence")
        }
        assert not sequence_names.intersection(OPERATIONAL_CONSULTATION_TABLES)
        trigger_names = {
            item[0]
            for item in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='trigger'"
            )
        }
        for table in ("consultation_configuration", *OPERATIONAL_CONSULTATION_TABLES):
            assert {f"{table}_no_update", f"{table}_no_delete"} <= trigger_names
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE consultation_configuration SET protocol_version=2"
            )
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute("DELETE FROM consultation_configuration")
    finally:
        connection.close()


def test_schema_v2_preserves_original_columns_budget_and_event_shape(
    tmp_path: Path,
) -> None:
    v1_root = tmp_path / "v1"
    v1_status, _ = initialize_organism(v1_root, "paired", clock=_clock())
    v2_root, v2_status, _ = _init_v2(tmp_path, organism_id="paired")
    v1 = connect_database(
        OrganismPaths.build(v1_root, v1_status.organism_id).database,
        read_only=True,
    )
    v2 = connect_database(
        OrganismPaths.build(v2_root, v2_status.organism_id).database,
        read_only=True,
    )
    try:
        for table in ORIGINAL_TABLES:
            assert _columns(v2, table) == _columns(v1, table)
        budget = v2.execute("SELECT * FROM budget_config").fetchone()
        assert dict(budget) == {
            "singleton_id": 1,
            "config_version": BUDGET_CONFIG_VERSION,
            "config_json": json.dumps(
                PHASE1_BUDGETS.as_dict(),
                sort_keys=True,
                separators=(",", ":"),
            ),
        }
        events = v2.execute("SELECT * FROM event ORDER BY event_sequence").fetchall()
        assert {row["budget_config_version"] for row in events} == {
            BUDGET_CONFIG_VERSION
        }
        assert json.loads(events[0]["payload_json"]) == {
            "budget_config_version": BUDGET_CONFIG_VERSION,
            "contract_version": "0.2",
            "environment_version": "seed-garden-v1",
            "schema_version": PHASE2_SCHEMA_VERSION,
        }
        assert all("consultation" not in row["event_type"] for row in events)
        assert all("consultation" not in row["source"] for row in events)
    finally:
        v1.close()
        v2.close()


def test_schema_and_configuration_admission_fail_before_partial_creation(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime"
    cases = (
        ({"schema_version": 2}, "requires one accepted"),
        (
            {
                "schema_version": 2,
                "consultation_configuration_version": "phase2-unknown-v1",
            },
            "requires one accepted",
        ),
        (
            {
                "consultation_configuration_version": (
                    ZERO_CAREGIVER_CONFIGURATION_VERSION
                )
            },
            "schema-v1 initialization does not accept",
        ),
        ({"schema_version": 3}, "unsupported database schema"),
    )
    for index, (kwargs, message) in enumerate(cases):
        organism_id = f"rejected-{index}"
        with pytest.raises(SchemaValidationError, match=message):
            initialize_organism(root, organism_id, clock=_clock(), **kwargs)
        assert not (root / organism_id).exists()


def test_active_and_checkpoint_validation_reject_config_and_schema_corruption(
    tmp_path: Path,
) -> None:
    root, status, checkpoint = _init_v2(tmp_path)
    paths = OrganismPaths.build(root, status.organism_id)
    mixed = json.loads(
        consultation_configuration_json(ZERO_CAREGIVER_CONFIGURATION_VERSION)
    )
    mixed["configuration_version"] = FIXTURE_CONFIGURATION_VERSION
    _replace_config_json(paths.database, mixed)
    with pytest.raises(SchemaValidationError, match="noncanonical or changed"):
        read_status(paths)

    validate_checkpoint_directory(checkpoint.checkpoint_dir)

    corrupted = tmp_path / "corrupted-checkpoint"
    shutil.copytree(checkpoint.checkpoint_dir, corrupted)
    database = corrupted / "organism.sqlite3"
    manifest_path = corrupted / "manifest.json"
    changed = json.loads(
        consultation_configuration_json(ZERO_CAREGIVER_CONFIGURATION_VERSION)
    )
    changed["limits"]["requests_per_lineage"] = 1
    _replace_config_json(database, changed)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["database_size_bytes"] = database.stat().st_size
    manifest["database_sha256"] = _sha256(database)
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(CheckpointError, match="consultation configuration"):
        validate_checkpoint_directory(corrupted, expected_manifest=manifest)


def test_schema_v2_rejects_unreviewed_objects_exactly(tmp_path: Path) -> None:
    root, status, _ = _init_v2(tmp_path)
    paths = OrganismPaths.build(root, status.organism_id)
    connection = connect_database(paths.database)
    try:
        connection.execute("CREATE TABLE unreviewed_phase2_object (value TEXT)")
    finally:
        connection.close()
    with pytest.raises(SchemaValidationError, match="unexpected mutable object"):
        read_status(paths)


def test_zero_caregiver_genesis_imports_no_fixture_runtime(tmp_path: Path) -> None:
    before = set(sys.modules)
    _init_v2(tmp_path)
    imported = set(sys.modules) - before
    assert not {
        name
        for name in imported
        if "caregiver" in name
        or "fixture_adapter" in name
        or "consultation_fixture" in name
    }


def test_schema_v2_genesis_overhead_is_within_accepted_cap(tmp_path: Path) -> None:
    v1_root = tmp_path / "overhead-v1"
    v1_status, _ = initialize_organism(v1_root, "paired-overhead", clock=_clock())
    v2_root, v2_status, _ = _init_v2(tmp_path, organism_id="paired-overhead")
    v1_size = OrganismPaths.build(v1_root, v1_status.organism_id).database.stat().st_size
    v2_size = OrganismPaths.build(v2_root, v2_status.organism_id).database.stat().st_size
    assert 0 <= v2_size - v1_size <= 256 * 1024


def test_cli_explicit_schema_v2_and_no_migration_surface(
    tmp_path: Path,
    capsys,
) -> None:
    runtime = tmp_path / "runtime"
    assert main(
        [
            "--runtime-dir", str(runtime), "init", "cli-v2",
            "--schema-version", "2",
            "--consultation-config", ZERO_CAREGIVER_CONFIGURATION_VERSION,
            "--json",
        ]
    ) == 0
    initialized = json.loads(capsys.readouterr().out)
    assert initialized["schema_version"] == PHASE2_SCHEMA_VERSION
    assert initialized["budget_config_version"] == BUDGET_CONFIG_VERSION
    assert initialized["consultation_configuration_version"] == (
        ZERO_CAREGIVER_CONFIGURATION_VERSION
    )
    assert main(
        ["--runtime-dir", str(runtime), "status", "cli-v2", "--json"]
    ) == 0
    assert json.loads(capsys.readouterr().out)[
        "consultation_configuration_version"
    ] == ZERO_CAREGIVER_CONFIGURATION_VERSION

    parser = build_parser()
    help_text = parser.format_help()
    assert "migrate" not in help_text
    assert "downgrade" not in help_text

    assert main(
        [
            "--runtime-dir", str(runtime), "init", "missing-config",
            "--schema-version", "2", "--json",
        ]
    ) == 1
    assert "requires one accepted" in capsys.readouterr().err
    assert not (runtime / "missing-config").exists()
