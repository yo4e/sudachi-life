from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.constants import (
    ACTIVE_DATABASE_MAX_BYTES,
    CHECKPOINT_ARTIFACT_MAX_BYTES,
    CHECKPOINT_STORE_MAX_BYTES,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.phase2_schema import (
    CONSULTATION_PROTOCOL_VERSION,
    OPERATIONAL_CONSULTATION_TABLES,
    ZERO_CAREGIVER_CONFIGURATION_VERSION,
    consultation_configuration_json,
)
from sudachi_life.rollback import prepare_rollback_archive
from sudachi_life.rollback_candidate import build_restore_candidate
from sudachi_life.rollback_intent import begin_rollback
from sudachi_life.rollback_transform import transform_restore_candidate
from sudachi_life.runtime_storage import (
    ACTIVE_DATABASE_WAKE_RESERVE_BYTES,
    checkpoint_store_bytes,
)
from sudachi_life.storage import connect_database, read_status

from phase1_audit_helpers import _wake_clock
from test_phase2_absolute_active_and_repair_limits import _initialize_v2
from test_phase2_projection_rollback import _prepared_pair, _rollback_clock


def _sparse_file(path: Path, size: int) -> None:
    assert size >= 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        handle.truncate(size)


def _complete_store_wake(tmp_path: Path):
    runtime_root, paths = _initialize_v2(tmp_path, "absolute-store-v2")
    enqueue_garden_tick(
        paths,
        "absolute-store-source",
        clock=_rollback_clock(1_760_000_000_000_000, 60_000_000),
    )
    result = perform_garden_wake(
        runtime_root,
        paths.organism_id,
        seed=2,
        clock=_wake_clock(1_761_000_000_000_000),
    )
    assert result.status == "sleeping"
    return runtime_root, paths, result


def _prepared_store_wake(tmp_path: Path):
    runtime_root, paths = _initialize_v2(tmp_path, "absolute-store-v2")
    enqueue_garden_tick(
        paths,
        "absolute-store-source",
        clock=_rollback_clock(1_760_000_000_000_000, 60_000_000),
    )
    return runtime_root, paths


def test_absolute_physical_limit_constants_are_exact() -> None:
    assert ACTIVE_DATABASE_MAX_BYTES == 8 * 1024 * 1024
    assert CHECKPOINT_ARTIFACT_MAX_BYTES == 8 * 1024 * 1024
    assert CHECKPOINT_STORE_MAX_BYTES == 40 * 1024 * 1024
    assert RUNTIME_WORKING_SET_MAX_BYTES == 64 * 1024 * 1024
    assert ACTIVE_DATABASE_WAKE_RESERVE_BYTES == 1 * 1024 * 1024


def test_checkpoint_creation_accepts_exact_absolute_store_limit(tmp_path: Path) -> None:
    _control_root, control_paths, _control_result = _complete_store_wake(
        tmp_path / "control"
    )
    control_final_store = checkpoint_store_bytes(control_paths)
    assert control_final_store < CHECKPOINT_STORE_MAX_BYTES

    runtime_root, paths = _prepared_store_wake(tmp_path / "probe")
    padding = CHECKPOINT_STORE_MAX_BYTES - control_final_store
    _sparse_file(paths.checkpoints / ".absolute-store-padding", padding)

    result = perform_garden_wake(
        runtime_root,
        paths.organism_id,
        seed=2,
        clock=_wake_clock(1_761_000_000_000_000),
    )
    assert result.status == "sleeping"
    assert checkpoint_store_bytes(paths) == CHECKPOINT_STORE_MAX_BYTES


def test_checkpoint_creation_rejects_one_byte_over_store_without_temp_artifact(
    tmp_path: Path,
) -> None:
    _control_root, control_paths, _control_result = _complete_store_wake(
        tmp_path / "control"
    )
    control_final_store = checkpoint_store_bytes(control_paths)

    runtime_root, paths = _prepared_store_wake(tmp_path / "probe")
    padding = CHECKPOINT_STORE_MAX_BYTES - control_final_store + 1
    _sparse_file(paths.checkpoints / ".absolute-store-padding", padding)
    before_store = checkpoint_store_bytes(paths)
    before_visible = sorted(
        entry.name
        for entry in paths.checkpoints.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    )

    with pytest.raises(CheckpointError, match="checkpoint store"):
        perform_garden_wake(
            runtime_root,
            paths.organism_id,
            seed=2,
            clock=_wake_clock(1_761_000_000_000_000),
        )

    assert checkpoint_store_bytes(paths) == before_store
    assert not any(
        entry.name.startswith(".tmp-checkpoint-")
        for entry in paths.checkpoints.iterdir()
    )
    assert sorted(
        entry.name
        for entry in paths.checkpoints.iterdir()
        if entry.is_dir() and not entry.name.startswith(".")
    ) == before_visible
    status = read_status(paths)
    assert status.status == "checkpoint_pending"
    assert status.checkpoint_pending is True


def _assert_raw_zero_consultation_database(database: Path) -> None:
    connection = connect_database(database, read_only=True)
    try:
        row = connection.execute(
            "SELECT singleton_id, protocol_version, configuration_version, "
            "configuration_json FROM consultation_configuration"
        ).fetchone()
        assert row is not None
        assert int(row["singleton_id"]) == 1
        assert int(row["protocol_version"]) == CONSULTATION_PROTOCOL_VERSION
        assert row["configuration_version"] == ZERO_CAREGIVER_CONFIGURATION_VERSION
        assert row["configuration_json"] == consultation_configuration_json(
            ZERO_CAREGIVER_CONFIGURATION_VERSION
        )
        for table in OPERATIONAL_CONSULTATION_TABLES:
            assert int(
                connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            ) == 0
        sequence_names = {
            str(row[0])
            for row in connection.execute(
                "SELECT name FROM sqlite_sequence WHERE name LIKE 'consultation_%'"
            ).fetchall()
        }
        assert sequence_names == set()
    finally:
        connection.close()


def test_zero_consultation_raw_state_survives_active_cp_ra_rc_tc(tmp_path: Path) -> None:
    _v1_root, _v1, v2_root, v2, _left, _right = _prepared_pair(tmp_path)
    _assert_raw_zero_consultation_database(v2.database)

    active = connect_database(v2.database, read_only=True)
    try:
        latest_checkpoint_id = str(
            active.execute(
                "SELECT latest_stable_checkpoint_id FROM organism WHERE singleton_id=1"
            ).fetchone()[0]
        )
    finally:
        active.close()
    _assert_raw_zero_consultation_database(
        v2.checkpoints / latest_checkpoint_id / "organism.sqlite3"
    )

    archive = prepare_rollback_archive(v2_root, "paired", 2)
    _assert_raw_zero_consultation_database(
        archive.archive_dir / "organism.sqlite3"
    )
    begin_rollback(
        v2_root,
        "paired",
        archive.archive_id,
        clock=_rollback_clock(1_710_000_000_000_000, 11_000_000),
    )
    source = build_restore_candidate(v2_root, "paired")
    _assert_raw_zero_consultation_database(
        source.candidate_dir / "organism.sqlite3"
    )
    transformed = transform_restore_candidate(
        v2_root,
        "paired",
        source.candidate_id,
        "raw zero consultation preservation",
        clock=_rollback_clock(1_720_000_000_000_000, 12_000_000),
    )
    _assert_raw_zero_consultation_database(
        transformed.transformed_candidate_dir / "organism.sqlite3"
    )
