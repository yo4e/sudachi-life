from __future__ import annotations

import ast
import json
from pathlib import Path

from sudachi_life.cli import build_parser
from sudachi_life.clock import FakeClock
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_schema import FIXTURE_CONFIGURATION_VERSION
from sudachi_life.storage import connect_database, read_status
import sudachi_life


_FORBIDDEN_IMPORT_ROOTS = {
    "aiohttp",
    "anthropic",
    "httpx",
    "openai",
    "requests",
    "socket",
    "subprocess",
    "urllib",
    "websockets",
}
_FORBIDDEN_SURFACE_TERMS = {
    "caregiver-chat",
    "chat-server",
    "daemon",
    "generate-source",
    "generate-tests",
    "memory",
    "model-api",
    "personality",
    "serve",
    "skill",
    "train",
    "watch",
}
_FORBIDDEN_STATE_TERMS = {
    "affection",
    "emotion",
    "mood",
    "personality",
    "virtual_pet",
}
_EXTERNAL_CONSUMER_MODULES = {
    "phase2_ingress_runtime.py",
    "phase2_ingress_runtime_impl.py",
    "phase2_disposition_runtime.py",
    "phase2_disposition_runtime_impl.py",
}


def _package_root() -> Path:
    package_file = sudachi_life.__file__
    assert package_file is not None
    return Path(package_file).resolve().parent


def _python_sources() -> list[Path]:
    return sorted(_package_root().glob("*.py"))


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)
    return imported


def _all_json_keys(value: object) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(str(key))
            keys.update(_all_json_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_all_json_keys(item))
    return keys


def test_package_import_graph_has_no_live_api_network_or_subprocess_route() -> None:
    violations: dict[str, list[str]] = {}
    for path in _python_sources():
        forbidden = sorted(
            imported
            for imported in _imports(path)
            if imported.split(".", 1)[0] in _FORBIDDEN_IMPORT_ROOTS
        )
        if forbidden:
            violations[path.name] = forbidden
    assert violations == {}


def test_cli_and_phase2_runtime_have_no_continuous_or_generation_surface() -> None:
    help_text = build_parser().format_help().lower()
    assert not {
        term for term in _FORBIDDEN_SURFACE_TERMS if term in help_text
    }

    loop_modules: list[str] = []
    for path in _python_sources():
        if not path.name.startswith("phase2_"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if any(isinstance(node, ast.While) for node in ast.walk(tree)):
            loop_modules.append(path.name)
    assert loop_modules == []


def test_schema_status_and_configuration_have_no_adaptive_or_personality_state(
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "runtime"
    status, _checkpoint = initialize_organism(
        runtime_root,
        "absence-profile",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_800_000_000_000_000,
            monotonic_ns=10_000_000,
        ),
        schema_version=2,
        consultation_configuration_version=FIXTURE_CONFIGURATION_VERSION,
    )
    paths = OrganismPaths.build(runtime_root, status.organism_id)
    connection = connect_database(paths.database, read_only=True)
    try:
        objects = connection.execute(
            "SELECT type, name, tbl_name, sql FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        ).fetchall()
        schema_text = "\n".join(
            " ".join(str(value) for value in tuple(row) if value is not None)
            for row in objects
        ).lower()
        configuration = json.loads(
            connection.execute(
                "SELECT configuration_json FROM consultation_configuration"
            ).fetchone()[0]
        )
    finally:
        connection.close()

    exposed_keys = {
        *read_status(paths).as_dict().keys(),
        *_all_json_keys(configuration),
    }
    exposed_text = "\n".join(sorted(str(key).lower() for key in exposed_keys))
    for term in _FORBIDDEN_STATE_TERMS | {"memory", "skill", "training"}:
        assert term not in schema_text
        assert term not in exposed_text


def test_external_package_consumers_do_not_import_phase1_selector_or_executor() -> None:
    consumer_paths = {
        path.name: path for path in _python_sources() if path.name in _EXTERNAL_CONSUMER_MODULES
    }
    assert set(consumer_paths) == _EXTERNAL_CONSUMER_MODULES

    forbidden: dict[str, list[str]] = {}
    for name, path in consumer_paths.items():
        matches = sorted(
            imported
            for imported in _imports(path)
            if imported.rsplit(".", 1)[-1] in {"selector", "executor"}
        )
        if matches:
            forbidden[name] = matches
    assert forbidden == {}
