from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sqlite3

import pytest

from sudachi_life.checkpoint_repair import (
    PendingCheckpointRepairBusyError,
    PendingCheckpointRepairRejectedError,
    repair_pending_checkpoint_registration,
)
from sudachi_life.cli import main
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import CheckpointError
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_garden_wake
from sudachi_life.organism import initialize_organism
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def _checkpoint_store_bytes(paths: OrganismPaths) -> int:
    return sum(
        path.stat().st_size
        for path in paths.checkpoints.rglob("*")
        if path.is_file() and not path.is_symlink()
    )


def _orphan_dirs(paths: OrganismPaths) -> list[Path]:
    connection = connect_database(paths.database, read_only=True)
    try:
        registered = {
            str(row[0])
            for row in connection.execute(
                "SELECT checkpoint_id FROM checkpoint_registry"
            ).fetchall()
        }
    finally:
        connection.close()
    return sorted(
        [
            path
            for path in paths.checkpoints.iterdir()
            if path.is_dir() and not path.name.startswith(".")
            and path.name not in registered
        ],
        key=lambda path: path.name,
    )


def _prepare_pending_orphan(
    runtime_root: Path,
    organism_id: str,
    *,
    tick_id: str,
) -> Path:
    paths = OrganismPaths.build(runtime_root, organism_id)
    enqueue_garden_tick(
        paths,
        tick_id,
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    timeout_clock = FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 5_030_000_001),
        ]
    )
    with pytest.raises(CheckpointError, match="deadline"):
        perform_garden_wake(
            runtime_root,
            organism_id,
            seed=1,
            clock=timeout_clock,
        )
    assert timeout_clock.read_count == 5

    status = read_status(paths)
    assert status.status == "checkpoint_pending"
    assert status.checkpoint_pending is True
    assert status.lifecycle_number == 1
    assert status.environment_step == 1
    assert status.water_units == 0
    assert status.latest_stable_event_sequence == 2
    assert status.event_count == 13
    orphans = _orphan_dirs(paths)
    assert len(orphans) == 1
    return orphans[0]


def _canonical_rows(paths: OrganismPaths) -> dict[str, object]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return {
            "organism": tuple(
                connection.execute(
                    "SELECT organism_id, lineage_generation, lifecycle_number, status, "
                    "checkpoint_pending, pending_checkpoint_generation, "
                    "pending_checkpoint_event_sequence, latest_stable_checkpoint_id, "
                    "latest_stable_event_sequence, consecutive_failures, maintenance_reason, "
                    "last_wake_wall_time_utc_us, last_sleep_wall_time_utc_us "
                    "FROM organism WHERE singleton_id = 1"
                ).fetchone()
            ),
            "environment": tuple(
                connection.execute(
                    "SELECT environment_step, objective_complete FROM environment_state"
                ).fetchone()
            ),
            "plots": [
                tuple(row)
                for row in connection.execute(
                    "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id"
                ).fetchall()
            ],
            "inventory": tuple(
                connection.execute(
                    "SELECT water_units, harvested_fruit FROM inventory"
                ).fetchone()
            ),
            "inbox": [
                tuple(row)
                for row in connection.execute(
                    "SELECT inbox_id, external_event_id, event_type, source, "
                    "claimed_lifecycle_number, consumed FROM inbox_event ORDER BY inbox_id"
                ).fetchall()
            ],
            "events": [
                tuple(row)
                for row in connection.execute(
                    "SELECT event_sequence, event_type, source, payload_json "
                    "FROM event ORDER BY event_sequence"
                ).fetchall()
            ],
            "registry": [
                tuple(row)
                for row in connection.execute(
                    "SELECT checkpoint_id, lineage_generation, event_sequence, "
                    "manifest_sha256, database_sha256, database_size_bytes, protected "
                    "FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"
                ).fetchall()
            ],
        }
    finally:
        connection.close()


def _wake_clock() -> FakeClock:
    return FakeClock(
        [
            ClockReading(500, 10_000_000),
            ClockReading(500, 15_000_000),
            ClockReading(501, 20_000_000),
            ClockReading(502, 30_000_000),
            ClockReading(503, 40_000_000),
        ]
    )


def test_valid_published_orphan_is_registered_and_later_wake_proceeds(
    initialized,
) -> None:
    runtime_root, initial, genesis = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    orphan = _prepare_pending_orphan(
        runtime_root,
        initial.organism_id,
        tick_id="pending-repair-tick-1",
    )
    before_files = _file_hashes(paths.checkpoints)
    before_store_bytes = _checkpoint_store_bytes(paths)
    before = _canonical_rows(paths)
    assert len(before["registry"]) == 1
    assert before["registry"][0][0] == genesis.checkpoint_id

    repair_clock = FakeClock([ClockReading(400, 6_000_000_000)])
    result = repair_pending_checkpoint_registration(
        runtime_root,
        initial.organism_id,
        clock=repair_clock,
    )
    assert repair_clock.read_count == 1
    assert result.as_dict() == {
        "organism_id": initial.organism_id,
        "status_before": "checkpoint_pending",
        "status": "sleeping",
        "checkpoint_id": orphan.name,
        "lineage_generation": 0,
        "event_sequence": 13,
        "previous_latest_stable_checkpoint_id": genesis.checkpoint_id,
        "previous_latest_stable_event_sequence": 2,
        "registered_checkpoint_count": 2,
        "checkpoint_store_bytes": before_store_bytes,
        "audit_event_sequence": 14,
    }

    status = read_status(paths)
    assert status.status == "sleeping"
    assert status.checkpoint_pending is False
    assert status.lifecycle_number == 1
    assert status.environment_step == 1
    assert status.water_units == 0
    assert status.latest_stable_checkpoint_id == orphan.name
    assert status.latest_stable_event_sequence == 13
    assert status.event_count == 14
    assert _file_hashes(paths.checkpoints) == before_files
    assert _checkpoint_store_bytes(paths) == before_store_bytes

    after = _canonical_rows(paths)
    assert after["environment"] == before["environment"]
    assert after["plots"] == before["plots"]
    assert after["inventory"] == before["inventory"]
    assert after["inbox"] == before["inbox"]
    assert len(after["registry"]) == 2
    assert [row[2] for row in after["registry"]] == [2, 13]
    assert len(after["events"]) == 14

    connection = connect_database(paths.database, read_only=True)
    try:
        audit = connection.execute(
            "SELECT event_type, source, payload_json FROM event WHERE event_sequence = 14"
        ).fetchone()
        assert tuple(audit[:2]) == (
            "checkpoint_registration_repaired",
            "administration:checkpoint-repair",
        )
        payload = json.loads(audit["payload_json"])
        assert payload == {
            "checkpoint_id": orphan.name,
            "checkpoint_store_bytes": before_store_bytes,
            "database_sha256": payload["database_sha256"],
            "database_size_bytes": payload["database_size_bytes"],
            "event_sequence": 13,
            "lineage_generation": 0,
            "manifest_sha256": payload["manifest_sha256"],
            "previous_latest_stable_checkpoint_id": genesis.checkpoint_id,
            "previous_latest_stable_event_sequence": 2,
            "reason": "published_checkpoint_registration_missing",
            "status_after": "sleeping",
            "status_before": "checkpoint_pending",
        }
        assert len(payload["database_sha256"]) == 64
        assert len(payload["manifest_sha256"]) == 64
        assert payload["database_size_bytes"] > 0
    finally:
        connection.close()

    enqueue_garden_tick(
        paths,
        "pending-repair-tick-2",
        clock=FakeClock([ClockReading(450, 7_000_000_000)]),
    )
    wake = perform_garden_wake(
        runtime_root,
        initial.organism_id,
        seed=2,
        clock=_wake_clock(),
    )
    assert wake.decision.as_dict() == {
        "decision_type": "action",
        "action_id": "harvest_plot",
        "action_version": 1,
        "parameters": {"plot_id": "bed-b"},
        "reason": "fixed_policy_first_executable_harvest",
    }
    assert wake.checkpoint.event_sequence == 24
    final = read_status(paths)
    assert final.status == "sleeping"
    assert final.lifecycle_number == 2
    assert final.environment_step == 2
    assert final.harvested_fruit == 1
    assert final.objective_complete is True
    assert final.latest_stable_event_sequence == 24
    assert final.event_count == 25


def test_pending_checkpoint_repair_cli_uses_narrow_administrative_boundary(
    initialized,
    capsys,
) -> None:
    runtime_root, initial, _ = initialized
    orphan = _prepare_pending_orphan(
        runtime_root,
        initial.organism_id,
        tick_id="pending-repair-cli-tick-1",
    )

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "checkpoint",
            "repair-pending",
            initial.organism_id,
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status_before"] == "checkpoint_pending"
    assert payload["status"] == "sleeping"
    assert payload["checkpoint_id"] == orphan.name
    assert payload["event_sequence"] == 13
    assert payload["audit_event_sequence"] == 14

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "checkpoint",
            "repair-pending",
            initial.organism_id,
            "--json",
        ]
    ) == 1
    assert "checkpoint_pending" in capsys.readouterr().err


def _replace_with_foreign_orphan(
    runtime_root: Path,
    target_paths: OrganismPaths,
    target_orphan: Path,
) -> None:
    _, foreign_initial_checkpoint = initialize_organism(
        runtime_root,
        "foreign-organism",
        clock=FakeClock.fixed(wall_time_utc_us=50, monotonic_ns=500_000),
    )
    assert foreign_initial_checkpoint.event_sequence == 2
    foreign_orphan = _prepare_pending_orphan(
        runtime_root,
        "foreign-organism",
        tick_id="foreign-pending-repair-tick-1",
    )
    shutil.rmtree(target_orphan)
    shutil.copytree(foreign_orphan, target_paths.checkpoints / foreign_orphan.name)


@pytest.mark.parametrize("case", ["missing", "ambiguous", "mismatched", "invalid"])
def test_missing_ambiguous_mismatched_or_invalid_orphan_keeps_pending_state(
    initialized,
    case: str,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    orphan = _prepare_pending_orphan(
        runtime_root,
        initial.organism_id,
        tick_id=f"pending-repair-reject-{case}",
    )

    if case == "missing":
        shutil.rmtree(orphan)
    elif case == "ambiguous":
        shutil.copytree(orphan, paths.checkpoints / "ambiguous-visible-orphan")
    elif case == "mismatched":
        _replace_with_foreign_orphan(runtime_root, paths, orphan)
    elif case == "invalid":
        (orphan / "manifest.json").write_text("{not-json\n", encoding="utf-8")
    else:  # pragma: no cover - protected parameter list is closed
        raise AssertionError(case)

    before_rows = _canonical_rows(paths)
    before_files = _file_hashes(paths.checkpoints)
    before_database_sha = _sha256(paths.database)
    clock = FakeClock([])
    with pytest.raises(PendingCheckpointRepairRejectedError):
        repair_pending_checkpoint_registration(
            runtime_root,
            initial.organism_id,
            clock=clock,
        )
    assert clock.read_count == 0
    assert _canonical_rows(paths) == before_rows
    assert _file_hashes(paths.checkpoints) == before_files
    assert _sha256(paths.database) == before_database_sha
    status = read_status(paths)
    assert status.status == "checkpoint_pending"
    assert status.checkpoint_pending is True
    assert status.latest_stable_event_sequence == 2
    assert status.event_count == 13


def test_pending_checkpoint_repair_is_fail_fast_when_database_is_busy(
    initialized,
) -> None:
    runtime_root, initial, _ = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    _prepare_pending_orphan(
        runtime_root,
        initial.organism_id,
        tick_id="pending-repair-busy-tick-1",
    )
    before = _canonical_rows(paths)

    competing = sqlite3.connect(paths.database, timeout=0.0, isolation_level=None)
    try:
        competing.execute("BEGIN IMMEDIATE")
        clock = FakeClock([])
        with pytest.raises(PendingCheckpointRepairBusyError):
            repair_pending_checkpoint_registration(
                runtime_root,
                initial.organism_id,
                clock=clock,
            )
        assert clock.read_count == 0
    finally:
        competing.rollback()
        competing.close()

    assert _canonical_rows(paths) == before
