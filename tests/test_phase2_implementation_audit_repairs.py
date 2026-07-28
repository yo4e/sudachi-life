from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
import shutil

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.constants import MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT
from sudachi_life.phase2_dispatch_runtime import (
    DispatchAdmissionRejectedError,
    FixtureExecutionError,
    admit_fixture_dispatch,
    perform_fixture_dispatch,
)
from sudachi_life.phase2_ingress_runtime import (
    ingress_external_package,
    terminalize_fixture_dispatch,
)
from sudachi_life.storage import connect_database, read_status, validate_canonical_state

from test_phase2_dispatch_admission_fixture import _init_request


AUDITED_DISPATCH_SHA256 = "ed573180a7017b9ec8b1002ec59f2376e90653ee8a4013f8b24775a80a0f80ac"


def _consultation_counts(paths) -> tuple[int, int, int, int, int]:
    connection = connect_database(paths.database, read_only=True)
    try:
        return tuple(
            int(value)
            for value in connection.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM consultation_dispatch), "
                "(SELECT COUNT(*) FROM consultation_cost_charge), "
                "(SELECT COUNT(*) FROM consultation_dispatch_terminal), "
                "(SELECT COUNT(*) FROM consultation_cost_completion), "
                "(SELECT COUNT(*) FROM event WHERE event_type="
                "'consultation_dispatch_terminalized')"
            ).fetchone()
        )
    finally:
        connection.close()


def _enter_failure_maintenance(paths) -> None:
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute(
            "UPDATE organism SET status='maintenance_required', "
            "maintenance_reason=?, consecutive_failures=3 WHERE singleton_id=1",
            (MAINTENANCE_REASON_CONSECUTIVE_FAILURE_LIMIT,),
        )
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
    finally:
        connection.close()


def test_audited_dispatch_body_is_retained_byte_identically() -> None:
    retained = (
        Path(__file__).resolve().parents[1]
        / "docs/phase2/retained/phase2_dispatch_runtime_impl.py"
    )
    assert hashlib.sha256(retained.read_bytes()).hexdigest() == AUDITED_DISPATCH_SHA256


def test_public_dispatch_has_no_caller_callable_execution_seam() -> None:
    parameters = inspect.signature(perform_fixture_dispatch).parameters
    assert "fixture_runner" not in parameters
    module = inspect.getmodule(perform_fixture_dispatch)
    assert module is not None
    assert "fixture_runner" not in inspect.getsource(module)
    with pytest.raises(TypeError, match="fixture_runner"):
        perform_fixture_dispatch(
            Path("unused"),
            "unused",
            request_id="unused",
            fixture_case_id="unused",
            fixture_runner=lambda *_: b"unsafe",
        )


def test_caught_fixture_failure_terminalizes_once_without_retry(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="audit-fixture-failure")
    clock = FakeClock(
        [
            ClockReading(2_300_000_000_000_000, 100_000_000),
            ClockReading(2_301_000_000_000_000, 110_000_000),
        ]
    )
    with pytest.raises(FixtureExecutionError, match="protected deterministic fixture failure"):
        perform_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="fixture-exception",
            clock=clock,
            protected_test_fault="fixture_exception",
        )
    assert _consultation_counts(paths) == (1, 1, 1, 1, 1)

    second = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="fixture-exception",
        clock=FakeClock([]),
    )
    assert second.admission.created is False
    assert second.fixture_invoked is False
    assert _consultation_counts(paths) == (1, 1, 1, 1, 1)


def test_success_ingress_preserves_failure_maintenance(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="audit-maintenance-ingress")
    dispatched = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-defer",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_310_000_000_000_000,
            monotonic_ns=120_000_000,
        ),
    )
    _enter_failure_maintenance(paths)
    before = read_status(paths)
    result = ingress_external_package(
        root,
        paths.organism_id,
        dispatch_id=dispatched.admission.dispatch_id,
        raw_package_bytes=dispatched.fixture_output,
        clock=FakeClock.fixed(
            wall_time_utc_us=2_311_000_000_000_000,
            monotonic_ns=130_000_000,
        ),
    )
    assert result.created is True
    after = read_status(paths)
    assert after.status == before.status == "maintenance_required"
    assert after.maintenance_reason == before.maintenance_reason
    assert after.consecutive_failures == before.consecutive_failures == 3
    assert after.lifecycle_number == before.lifecycle_number


def test_terminalization_preserves_failure_maintenance(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="audit-maintenance-terminal")
    admission = admit_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-defer",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_320_000_000_000_000,
            monotonic_ns=140_000_000,
        ),
    )
    _enter_failure_maintenance(paths)
    before = read_status(paths)
    result = terminalize_fixture_dispatch(
        root,
        paths.organism_id,
        dispatch_id=admission.dispatch_id,
        reason_code="fixture_output_invalid",
        raw_package_bytes=b"{",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_321_000_000_000_000,
            monotonic_ns=150_000_000,
        ),
    )
    assert result.created is True
    after = read_status(paths)
    assert after.status == before.status == "maintenance_required"
    assert after.maintenance_reason == before.maintenance_reason
    assert after.consecutive_failures == before.consecutive_failures == 3
    assert after.lifecycle_number == before.lifecycle_number


@pytest.mark.parametrize(
    "corruption",
    [
        "database-append",
        "manifest-whitespace",
        "manifest-database-sha",
        "manifest-database-size",
        "manifest-lineage",
        "manifest-boundary",
        "manifest-id",
    ],
)
def test_dispatch_validates_exact_stable_checkpoint_before_any_effect(
    tmp_path: Path,
    corruption: str,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id=f"audit-checkpoint-{corruption}",
    )
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id
    database_path = checkpoint_dir / "organism.sqlite3"
    manifest_path = checkpoint_dir / "manifest.json"
    if corruption == "database-append":
        with database_path.open("ab") as handle:
            handle.write(b"x")
    elif corruption == "manifest-whitespace":
        manifest_path.write_bytes(manifest_path.read_bytes() + b"\n")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if corruption == "manifest-database-sha":
            manifest["database_sha256"] = "0" * 64
        elif corruption == "manifest-database-size":
            manifest["database_size_bytes"] = int(manifest["database_size_bytes"]) + 1
        elif corruption == "manifest-lineage":
            manifest["lineage_generation"] = int(manifest["lineage_generation"]) + 1
        elif corruption == "manifest-boundary":
            manifest["event_sequence"] = int(manifest["event_sequence"]) + 1
        elif corruption == "manifest-id":
            manifest["checkpoint_id"] = str(manifest["checkpoint_id"]) + "-wrong"
        else:
            raise AssertionError(corruption)
        manifest_path.write_text(
            json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )

    no_clock = FakeClock([])
    with pytest.raises(DispatchAdmissionRejectedError):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="valid-defer",
            clock=no_clock,
        )
    assert no_clock.read_count == 0
    assert _consultation_counts(paths) == (0, 0, 0, 0, 0)


def _drop_table_triggers(connection, table_names: tuple[str, ...]) -> list[str]:
    placeholders = ",".join("?" for _ in table_names)
    rows = connection.execute(
        f"SELECT name, sql FROM sqlite_master WHERE type='trigger' "
        f"AND tbl_name IN ({placeholders}) ORDER BY name",
        table_names,
    ).fetchall()
    statements: list[str] = []
    for row in rows:
        if row["sql"] is None:
            raise AssertionError(f"trigger {row['name']} has no SQL")
        statements.append(str(row["sql"]))
        quoted = str(row["name"]).replace('"', '""')
        connection.execute(f'DROP TRIGGER "{quoted}"')
    return statements


def _restore_triggers(connection, statements: list[str]) -> None:
    for statement in statements:
        connection.execute(statement)


def _write_manifest(checkpoint_dir: Path, manifest: dict[str, object]) -> None:
    (checkpoint_dir / "manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _relink_checkpoint_registry(paths, checkpoint_id: str, checkpoint_dir: Path) -> None:
    database_path = checkpoint_dir / "organism.sqlite3"
    manifest_path = checkpoint_dir / "manifest.json"
    connection = connect_database(paths.database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        trigger_sql = _drop_table_triggers(connection, ("checkpoint_registry",))
        connection.execute(
            "UPDATE checkpoint_registry SET manifest_sha256=?, database_sha256=?, "
            "database_size_bytes=? WHERE checkpoint_id=?",
            (
                hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                hashlib.sha256(database_path.read_bytes()).hexdigest(),
                database_path.stat().st_size,
                checkpoint_id,
            ),
        )
        _restore_triggers(connection, trigger_sql)
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
    finally:
        connection.close()


def _rewrite_snapshot(checkpoint_dir: Path, operation) -> None:
    connection = connect_database(checkpoint_dir / "organism.sqlite3")
    try:
        connection.execute("BEGIN IMMEDIATE")
        trigger_sql = _drop_table_triggers(
            connection,
            ("consultation_request", "event"),
        )
        operation(connection)
        _restore_triggers(connection, trigger_sql)
        connection.commit()
    finally:
        connection.close()


def _refresh_checkpoint_manifest_and_registry(paths, checkpoint_id: str) -> Path:
    checkpoint_dir = paths.checkpoints / checkpoint_id
    database_path = checkpoint_dir / "organism.sqlite3"
    manifest = json.loads(
        (checkpoint_dir / "manifest.json").read_text(encoding="utf-8")
    )
    manifest["database_sha256"] = hashlib.sha256(database_path.read_bytes()).hexdigest()
    manifest["database_size_bytes"] = database_path.stat().st_size
    _write_manifest(checkpoint_dir, manifest)
    _relink_checkpoint_registry(paths, checkpoint_id, checkpoint_dir)
    return checkpoint_dir


def _assert_dispatch_snapshot_rejection(root, paths, request_id: str, match: str) -> None:
    no_clock = FakeClock([])
    with pytest.raises(DispatchAdmissionRejectedError, match=match):
        admit_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=request_id,
            fixture_case_id="valid-defer",
            clock=no_clock,
        )
    assert no_clock.read_count == 0
    assert _consultation_counts(paths) == (0, 0, 0, 0, 0)
    connection = connect_database(paths.database, read_only=True)
    try:
        assert int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type="
                "'consultation_dispatch_admitted'"
            ).fetchone()[0]
        ) == 0
    finally:
        connection.close()


def test_dispatch_rejects_coherently_linked_wrong_organism_checkpoint(
    tmp_path: Path,
) -> None:
    root_a, paths_a, wake_a = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-owner-a",
    )
    _, paths_b, _ = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-owner-b",
    )
    status_a = read_status(paths_a)
    status_b = read_status(paths_b)
    checkpoint_a = paths_a.checkpoints / status_a.latest_stable_checkpoint_id
    checkpoint_b = paths_b.checkpoints / status_b.latest_stable_checkpoint_id

    shutil.copy2(
        checkpoint_b / "organism.sqlite3",
        checkpoint_a / "organism.sqlite3",
    )
    manifest = json.loads(
        (checkpoint_b / "manifest.json").read_text(encoding="utf-8")
    )
    manifest["checkpoint_id"] = status_a.latest_stable_checkpoint_id
    _write_manifest(checkpoint_a, manifest)
    _relink_checkpoint_registry(
        paths_a,
        status_a.latest_stable_checkpoint_id,
        checkpoint_a,
    )

    _assert_dispatch_snapshot_rejection(
        root_a,
        paths_a,
        wake_a.consultation_request.request_id,
        "checkpoint organism mismatch",
    )


def test_dispatch_rejects_coherently_linked_extra_manifest_field(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-extra-field",
    )
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id
    manifest = json.loads(
        (checkpoint_dir / "manifest.json").read_text(encoding="utf-8")
    )
    manifest["undeclared_field"] = "not-part-of-checkpoint-v1"
    _write_manifest(checkpoint_dir, manifest)
    _relink_checkpoint_registry(
        paths,
        status.latest_stable_checkpoint_id,
        checkpoint_dir,
    )

    _assert_dispatch_snapshot_rejection(
        root,
        paths,
        wake.consultation_request.request_id,
        "manifest field set mismatch",
    )


def test_dispatch_rejects_checkpoint_missing_exact_request_row(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-request-row",
    )
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id
    request_id = wake.consultation_request.request_id
    _rewrite_snapshot(
        checkpoint_dir,
        lambda connection: connection.execute(
            "DELETE FROM consultation_request WHERE request_id=?",
            (request_id,),
        ),
    )
    _refresh_checkpoint_manifest_and_registry(
        paths,
        status.latest_stable_checkpoint_id,
    )

    _assert_dispatch_snapshot_rejection(
        root,
        paths,
        request_id,
        "checkpoint.*request",
    )


def test_dispatch_rejects_checkpoint_request_event_mismatch(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(
        tmp_path,
        organism_id="audit-checkpoint-request-event",
    )
    status = read_status(paths)
    checkpoint_dir = paths.checkpoints / status.latest_stable_checkpoint_id
    request_id = wake.consultation_request.request_id
    _rewrite_snapshot(
        checkpoint_dir,
        lambda connection: connection.execute(
            "UPDATE event SET payload_json='{}' WHERE event_sequence=("
            "SELECT event_sequence FROM consultation_request WHERE request_id=?"
            ")",
            (request_id,),
        ),
    )
    _refresh_checkpoint_manifest_and_registry(
        paths,
        status.latest_stable_checkpoint_id,
    )

    _assert_dispatch_snapshot_rejection(
        root,
        paths,
        request_id,
        "request event does not match",
    )

