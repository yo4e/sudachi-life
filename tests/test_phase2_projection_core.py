from __future__ import annotations

import json
from pathlib import Path

import pytest

from sudachi_life.clock import FakeClock
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.phase2_projection import (
    ZeroCaregiverProjectionError,
    assert_zero_caregiver_equivalent,
    project_zero_caregiver_state,
)
from sudachi_life.phase2_schema import (
    FIXTURE_CONFIGURATION_VERSION,
    ZERO_CAREGIVER_CONFIGURATION_VERSION,
)
from sudachi_life.storage import connect_database


def _clock() -> FakeClock:
    return FakeClock.fixed(
        wall_time_utc_us=1_700_000_000_000_000,
        monotonic_ns=10_000_000,
    )


def _paired_genesis(tmp_path: Path) -> tuple[OrganismPaths, OrganismPaths]:
    v1_root = tmp_path / "v1"
    v2_root = tmp_path / "v2"
    initialize_organism(v1_root, "paired", clock=_clock())
    initialize_organism(
        v2_root,
        "paired",
        clock=_clock(),
        schema_version=2,
        consultation_configuration_version=ZERO_CAREGIVER_CONFIGURATION_VERSION,
    )
    return (
        OrganismPaths.build(v1_root, "paired"),
        OrganismPaths.build(v2_root, "paired"),
    )


def _replace_event_payload(database: Path, event_sequence: int, payload: dict[str, object]) -> None:
    connection = connect_database(database)
    try:
        trigger_rows = connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='trigger' "
            "AND name IN ('event_no_update','event_no_delete') ORDER BY name"
        ).fetchall()
        for row in trigger_rows:
            connection.execute(f"DROP TRIGGER {row['name']}")
        connection.execute(
            "UPDATE event SET payload_json=? WHERE event_sequence=?",
            (json.dumps(payload, sort_keys=True, separators=(",", ":")), event_sequence),
        )
        for row in trigger_rows:
            connection.execute(row["sql"])
    finally:
        connection.close()


def test_paired_genesis_projects_to_exact_semantic_equality(tmp_path: Path) -> None:
    v1, v2 = _paired_genesis(tmp_path)

    v1_projection = project_zero_caregiver_state(v1)
    v2_projection = project_zero_caregiver_state(v2)

    assert v1.database.read_bytes() != v2.database.read_bytes()
    assert (
        v1_projection["checkpoint_artifacts"][0]["manifest"]["checkpoint_id"]
        == "CP(0,2)"
    )
    assert v1_projection == v2_projection
    assert_zero_caregiver_equivalent(v1, v2)


def test_fixture_configuration_is_not_a_zero_caregiver_control(
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "fixture"
    initialize_organism(
        runtime_root,
        "fixture",
        clock=_clock(),
        schema_version=2,
        consultation_configuration_version=FIXTURE_CONFIGURATION_VERSION,
    )
    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="requires phase2-zero-caregiver-v1",
    ):
        project_zero_caregiver_state(
            OrganismPaths.build(runtime_root, "fixture")
        )


def test_unlisted_event_payload_key_is_not_hidden(tmp_path: Path) -> None:
    v1, v2 = _paired_genesis(tmp_path)
    connection = connect_database(v2.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT payload_json FROM event WHERE event_sequence=2"
        ).fetchone()
        payload = json.loads(row["payload_json"])
    finally:
        connection.close()
    payload["checkpoint_id"] = "checkpoint:unlisted-location"
    _replace_event_payload(v2.database, 2, payload)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="projected canonical state differs",
    ):
        assert_zero_caregiver_equivalent(v1, v2)


def test_nested_schema_version_is_not_normalized(tmp_path: Path) -> None:
    v1, v2 = _paired_genesis(tmp_path)
    connection = connect_database(v2.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT payload_json FROM event WHERE event_sequence=1"
        ).fetchone()
        payload = json.loads(row["payload_json"])
    finally:
        connection.close()
    payload["nested"] = {"schema_version": 1}
    _replace_event_payload(v2.database, 1, payload)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="projected canonical state differs",
    ):
        assert_zero_caregiver_equivalent(v1, v2)


def test_projected_registry_digest_is_recomputed_before_omission(
    tmp_path: Path,
) -> None:
    _v1, v2 = _paired_genesis(tmp_path)
    connection = connect_database(v2.database)
    try:
        connection.execute(
            "UPDATE checkpoint_registry SET database_sha256=?",
            ("0" * 64,),
        )
    finally:
        connection.close()

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="registry database digest does not match artifact",
    ):
        project_zero_caregiver_state(v2)


def test_checkpoint_directory_identity_must_be_bijective(tmp_path: Path) -> None:
    _v1, v2 = _paired_genesis(tmp_path)
    checkpoint_dir = next(v2.checkpoints.iterdir())
    duplicate = v2.checkpoints / "checkpoint:duplicate"
    duplicate.mkdir()
    for source in checkpoint_dir.iterdir():
        (duplicate / source.name).write_bytes(source.read_bytes())

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="checkpoint directory name does not match manifest",
    ):
        project_zero_caregiver_state(v2)


def _sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rewrite_checkpoint_database_semantics(paths: OrganismPaths) -> None:
    checkpoint_dir = next(paths.checkpoints.iterdir())
    database_path = checkpoint_dir / "organism.sqlite3"
    manifest_path = checkpoint_dir / "manifest.json"

    connection = connect_database(database_path)
    try:
        connection.execute(
            "UPDATE inventory SET water_units=water_units+1 WHERE singleton_id=1"
        )
    finally:
        connection.close()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["database_sha256"] = _sha256(database_path)
    manifest["database_size_bytes"] = database_path.stat().st_size
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )

    connection = connect_database(paths.database)
    try:
        connection.execute(
            """UPDATE checkpoint_registry
               SET database_sha256=?, manifest_sha256=?, database_size_bytes=?""",
            (
                _sha256(database_path),
                _sha256(manifest_path),
                database_path.stat().st_size,
            ),
        )
    finally:
        connection.close()


def test_equivalence_requires_schema_v1_then_schema_v2_zero(tmp_path: Path) -> None:
    v1, v2 = _paired_genesis(tmp_path)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="schema-v2-zero control has schema version 1",
    ):
        assert_zero_caregiver_equivalent(v1, v1)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="schema-v1 control has schema version 2",
    ):
        assert_zero_caregiver_equivalent(v2, v1)


def test_organism_checkpoint_identity_is_validated_before_projection(
    tmp_path: Path,
) -> None:
    _v1, v2 = _paired_genesis(tmp_path)
    connection = connect_database(v2.database)
    try:
        connection.execute(
            "UPDATE organism SET latest_stable_checkpoint_id=? WHERE singleton_id=1",
            ("checkpoint:wrong",),
        )
    finally:
        connection.close()

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="organism latest checkpoint identity does not match artifact",
    ):
        project_zero_caregiver_state(v2)


def test_checkpoint_stabilized_identity_is_validated_before_projection(
    tmp_path: Path,
) -> None:
    _v1, v2 = _paired_genesis(tmp_path)
    connection = connect_database(v2.database, read_only=True)
    try:
        row = connection.execute(
            "SELECT event_sequence, payload_json FROM event "
            "WHERE event_type='checkpoint_stabilized'"
        ).fetchone()
    finally:
        connection.close()
    payload = json.loads(row["payload_json"])
    payload["checkpoint_id"] = "checkpoint:wrong"
    _replace_event_payload(v2.database, int(row["event_sequence"]), payload)

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="checkpoint_stabilized identity does not match artifact",
    ):
        project_zero_caregiver_state(v2)


def test_checkpoint_database_semantics_are_not_hidden_by_digest_projection(
    tmp_path: Path,
) -> None:
    v1, v2 = _paired_genesis(tmp_path)
    _rewrite_checkpoint_database_semantics(v2)

    projection = project_zero_caregiver_state(v2)
    assert projection["checkpoint_artifacts"][0]["database_state"]["tables"][
        "inventory"
    ][0]["water_units"] == 2

    with pytest.raises(
        ZeroCaregiverProjectionError,
        match="projected canonical state differs",
    ):
        assert_zero_caregiver_equivalent(v1, v2)
