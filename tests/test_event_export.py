from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from sudachi_life.cli import main
from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import CheckpointError
from sudachi_life.event_export import (
    EVENT_EXPORT_FORMAT,
    EVENT_EXPORT_FORMAT_VERSION,
    EventExportRejectedError,
    EventExportWriteError,
    export_stable_events,
)
from sudachi_life.inbox import enqueue_garden_tick
from sudachi_life.lifecycle import perform_first_water_wake
from sudachi_life.paths import OrganismPaths
from sudachi_life.storage import connect_database, read_status


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_snapshot(paths: OrganismPaths) -> dict[str, object]:
    checkpoint_files = {
        str(path.relative_to(paths.checkpoints)): (path.stat().st_size, _sha256(path))
        for path in sorted(paths.checkpoints.rglob("*"))
        if path.is_file()
    }
    connection = connect_database(paths.database, read_only=True)
    try:
        inbox_rows = [
            tuple(row)
            for row in connection.execute(
                "SELECT inbox_id, external_event_id, event_type, source, "
                "source_wall_time_utc_us, received_wall_time_utc_us, "
                "claimed_lifecycle_number, consumed FROM inbox_event ORDER BY inbox_id"
            ).fetchall()
        ]
        checkpoint_rows = [
            tuple(row)
            for row in connection.execute(
                "SELECT checkpoint_id, lineage_generation, event_sequence, "
                "manifest_sha256, database_sha256, database_size_bytes, "
                "created_wall_time_utc_us, registered_wall_time_utc_us, protected "
                "FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"
            ).fetchall()
        ]
        event_rows = [
            tuple(row)
            for row in connection.execute(
                "SELECT event_sequence, organism_id, lineage_generation, "
                "lifecycle_number, wall_time_utc_us, event_type, source, payload_json, "
                "schema_version, environment_version, budget_config_version "
                "FROM event ORDER BY event_sequence"
            ).fetchall()
        ]
    finally:
        connection.close()
    return {
        "database_size": paths.database.stat().st_size,
        "database_sha256": _sha256(paths.database),
        "status": read_status(paths),
        "checkpoint_files": checkpoint_files,
        "inbox_rows": inbox_rows,
        "checkpoint_rows": checkpoint_rows,
        "event_rows": event_rows,
    }


def _normal_water_clock() -> FakeClock:
    return FakeClock(
        [
            ClockReading(300, 10_000_000),
            ClockReading(300, 15_000_000),
            ClockReading(301, 20_000_000),
            ClockReading(302, 30_000_000),
            ClockReading(303, 40_000_000),
        ]
    )


def test_stable_boundary_export_is_canonical_and_byte_identical(initialized) -> None:
    runtime_root, initial, checkpoint = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    before = _canonical_snapshot(paths)

    first = export_stable_events(runtime_root, initial.organism_id, checkpoint.event_sequence)
    first_bytes = first.export_path.read_bytes()
    records = [json.loads(line) for line in first_bytes.splitlines()]

    assert records[0] == {
        "record_type": "manifest",
        "organism_id": initial.organism_id,
        "lineage_generation": 0,
        "source_checkpoint_id": checkpoint.checkpoint_id,
        "first_event_sequence": 1,
        "last_event_sequence": 2,
        "event_count": 2,
        "export_format": EVENT_EXPORT_FORMAT,
        "export_format_version": EVENT_EXPORT_FORMAT_VERSION,
        "contract_version": initial.contract_version,
        "schema_version": initial.schema_version,
        "environment_version": initial.environment_version,
        "budget_config_version": initial.budget_config_version,
    }
    assert [record["event_sequence"] for record in records[1:]] == [1, 2]
    assert [record["event_type"] for record in records[1:]] == [
        "organism_initialized",
        "checkpoint_pending",
    ]
    assert all(record["record_type"] == "event" for record in records[1:])
    assert first.as_dict() == {
        "organism_id": initial.organism_id,
        "lineage_generation": 0,
        "source_checkpoint_id": checkpoint.checkpoint_id,
        "first_event_sequence": 1,
        "last_event_sequence": 2,
        "event_count": 2,
        "export_format": EVENT_EXPORT_FORMAT,
        "export_format_version": EVENT_EXPORT_FORMAT_VERSION,
        "export_path": str(first.export_path),
        "export_size_bytes": len(first_bytes),
        "export_sha256": hashlib.sha256(first_bytes).hexdigest(),
    }

    second = export_stable_events(runtime_root, initial.organism_id, checkpoint.event_sequence)
    assert second.export_path == first.export_path
    assert second.export_path.read_bytes() == first_bytes
    assert second.export_sha256 == first.export_sha256
    assert _canonical_snapshot(paths) == before
    assert not list(paths.exports.glob(".*.tmp"))


def test_event_export_cli_is_narrow_and_reports_published_artifact(
    initialized,
    capsys,
) -> None:
    runtime_root, initial, checkpoint = initialized

    assert main(
        [
            "--runtime-dir",
            str(runtime_root),
            "export",
            "events",
            initial.organism_id,
            "--event-sequence",
            str(checkpoint.event_sequence),
            "--json",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    export_path = Path(payload["export_path"])
    assert payload["export_format"] == EVENT_EXPORT_FORMAT
    assert payload["last_event_sequence"] == checkpoint.event_sequence
    assert payload["event_count"] == 2
    assert export_path.parent == OrganismPaths.build(
        runtime_root, initial.organism_id
    ).exports
    assert export_path.is_file()


def test_export_create_modify_delete_cannot_change_canonical_state_or_wakeability(
    initialized,
) -> None:
    runtime_root, initial, checkpoint = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    enqueue_garden_tick(
        paths,
        "export-preservation-tick-1",
        clock=FakeClock([ClockReading(200, 2_000_000)]),
    )
    before = _canonical_snapshot(paths)

    result = export_stable_events(runtime_root, initial.organism_id, checkpoint.event_sequence)
    assert _canonical_snapshot(paths) == before

    result.export_path.write_bytes(b'{"tampered":true}\n')
    assert _canonical_snapshot(paths) == before

    result.export_path.unlink()
    assert _canonical_snapshot(paths) == before

    wake = perform_first_water_wake(
        runtime_root,
        initial.organism_id,
        seed=1,
        clock=_normal_water_clock(),
    )
    assert wake.decision.as_dict()["parameters"] == {"plot_id": "bed-a"}
    status = read_status(paths)
    assert status.status == "sleeping"
    assert status.lifecycle_number == 1
    assert status.environment_step == 1
    assert status.latest_stable_event_sequence == 13


def test_partial_temporary_write_failure_preserves_previous_export_and_canonical_state(
    initialized,
) -> None:
    runtime_root, initial, checkpoint = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    successful = export_stable_events(
        runtime_root, initial.organism_id, checkpoint.event_sequence
    )
    previous_bytes = successful.export_path.read_bytes()
    before = _canonical_snapshot(paths)

    with pytest.raises(EventExportWriteError, match="injected event export failure"):
        export_stable_events(
            runtime_root,
            initial.organism_id,
            checkpoint.event_sequence,
            protected_test_fail_after_bytes=17,
        )

    assert successful.export_path.read_bytes() == previous_bytes
    assert _canonical_snapshot(paths) == before
    assert not list(paths.exports.glob(".*.tmp"))


def test_export_rejects_unregistered_and_pending_boundaries_without_state_change(
    initialized,
) -> None:
    runtime_root, initial, checkpoint = initialized
    paths = OrganismPaths.build(runtime_root, initial.organism_id)
    stable_before = _canonical_snapshot(paths)

    with pytest.raises(
        EventExportRejectedError,
        match="exactly one registered stable checkpoint at boundary 3; found 0",
    ):
        export_stable_events(runtime_root, initial.organism_id, 3)
    assert _canonical_snapshot(paths) == stable_before

    enqueue_garden_tick(
        paths,
        "pending-export-rejection-tick-1",
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
        perform_first_water_wake(
            runtime_root,
            initial.organism_id,
            seed=1,
            clock=timeout_clock,
        )
    pending_before = _canonical_snapshot(paths)

    with pytest.raises(
        EventExportRejectedError,
        match="checkpoint_pending mismatch: expected False, found True",
    ):
        export_stable_events(runtime_root, initial.organism_id, checkpoint.event_sequence)
    assert _canonical_snapshot(paths) == pending_before
