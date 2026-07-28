from __future__ import annotations

import hashlib
from pathlib import Path
import re


AUDITED_DISPATCH_SHA256 = "dfda290b508dba16c802f084f564f1d8a8c68d0e"
ROOT = Path(__file__).resolve().parents[1]


def replace_exact(text: str, old: str, new: str, *, context: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{context}: expected one exact match, found {count}")
    return text.replace(old, new, 1)


def replace_function(text: str, name: str, next_name: str, replacement: str) -> str:
    pattern = re.compile(
        rf"^def {re.escape(name)}\(.*?(?=^def {re.escape(next_name)}\()",
        re.MULTILINE | re.DOTALL,
    )
    updated, count = pattern.subn(replacement.rstrip() + "\n\n\n", text, count=1)
    if count != 1:
        raise RuntimeError(f"unable to replace {name}")
    return updated


def repair_dispatch_runtime() -> None:
    path = ROOT / "src/sudachi_life/phase2_dispatch_runtime.py"
    original = path.read_bytes()
    actual_sha = hashlib.sha256(original).hexdigest()
    if actual_sha != AUDITED_DISPATCH_SHA256:
        raise RuntimeError(
            f"unexpected dispatch candidate {actual_sha}; expected {AUDITED_DISPATCH_SHA256}"
        )

    retained = ROOT / "docs/phase2/retained/phase2_dispatch_runtime_impl.py"
    retained.parent.mkdir(parents=True, exist_ok=True)
    retained.write_bytes(original)

    text = original.decode("utf-8")
    text = replace_exact(
        text,
        "from dataclasses import dataclass\nimport json",
        "from dataclasses import dataclass\nimport hashlib\nimport json",
        context="hashlib import",
    )
    text = replace_exact(
        text,
        "from typing import Callable, Final",
        "from typing import Final",
        context="callable import removal",
    )
    text = replace_exact(
        text,
        "from .clock import Clock, RealClock",
        "from .checkpoints import validate_checkpoint_directory\n"
        "from .clock import Clock, RealClock",
        context="checkpoint validator import",
    )
    text = replace_exact(
        text,
        "from .errors import OrganismNotFoundError, SchemaValidationError, SudachiError",
        "from .errors import (\n"
        "    CheckpointError,\n"
        "    OrganismNotFoundError,\n"
        "    SchemaValidationError,\n"
        "    SudachiError,\n"
        ")",
        context="checkpoint error import",
    )
    text = replace_exact(
        text,
        "from .phase2_fixture import run_deterministic_fixture",
        "from .phase2_fixture import run_deterministic_fixture\n"
        "from .phase2_ingress_runtime import terminalize_fixture_dispatch",
        context="terminalization import",
    )
    text = replace_exact(
        text,
        "\n\nFixtureRunner = Callable[[dict[str, object], str], bytes]\n",
        "\n",
        context="fixture runner alias removal",
    )

    old_checkpoint = '''    registry = connection.execute(
        "SELECT lineage_generation, event_sequence FROM checkpoint_registry "
        "WHERE checkpoint_id=?",
        (latest_checkpoint_id,),
    ).fetchone()
    if registry is None:
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint is not registered")
    if int(registry["lineage_generation"]) != int(organism["lineage_generation"]):
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint lineage mismatch")
    if int(registry["event_sequence"]) != latest_boundary:
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint boundary mismatch")
    if not (paths.checkpoints / str(latest_checkpoint_id)).is_dir():
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint artifact is missing")
'''
    new_checkpoint = '''    registry = connection.execute(
        "SELECT lineage_generation, event_sequence, manifest_sha256, "
        "database_sha256, database_size_bytes FROM checkpoint_registry "
        "WHERE checkpoint_id=?",
        (latest_checkpoint_id,),
    ).fetchone()
    if registry is None:
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint is not registered")
    if int(registry["lineage_generation"]) != int(organism["lineage_generation"]):
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint lineage mismatch")
    if int(registry["event_sequence"]) != latest_boundary:
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint boundary mismatch")

    checkpoint_dir = paths.checkpoints / str(latest_checkpoint_id)
    if not checkpoint_dir.is_dir():
        raise DispatchAdmissionRejectedError("dispatch stable checkpoint artifact is missing")
    try:
        manifest = validate_checkpoint_directory(checkpoint_dir)
        manifest_sha = hashlib.sha256(
            (checkpoint_dir / "manifest.json").read_bytes()
        ).hexdigest()
    except (CheckpointError, OSError) as exc:
        raise DispatchAdmissionRejectedError(str(exc)) from exc
    if manifest.get("checkpoint_id") != latest_checkpoint_id:
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest ID mismatch")
    if int(manifest.get("lineage_generation", -1)) != int(
        registry["lineage_generation"]
    ):
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest lineage mismatch")
    if int(manifest.get("event_sequence", -1)) != int(registry["event_sequence"]):
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest boundary mismatch")
    if manifest.get("database_sha256") != registry["database_sha256"]:
        raise DispatchAdmissionRejectedError("dispatch checkpoint database digest mismatch")
    if int(manifest.get("database_size_bytes", -1)) != int(
        registry["database_size_bytes"]
    ):
        raise DispatchAdmissionRejectedError("dispatch checkpoint database size mismatch")
    if manifest_sha != registry["manifest_sha256"]:
        raise DispatchAdmissionRejectedError("dispatch checkpoint manifest digest mismatch")
'''
    text = replace_exact(
        text,
        old_checkpoint,
        new_checkpoint,
        context="stable checkpoint validation",
    )

    start = text.index("def perform_fixture_dispatch(\n")
    end = text.index("\n\n__all__ = [", start)
    safe_dispatch = '''_PROTECTED_FIXTURE_FAULTS: Final = frozenset(
    {"fixture_exception", "probe_lock_released"}
)


def _protected_test_probe_lock_released(
    runtime_root: Path | str,
    organism_id: str,
) -> None:
    paths = OrganismPaths.build(runtime_root, organism_id)
    probe = connect_database(paths.database)
    try:
        probe.execute("BEGIN IMMEDIATE")
        counts = probe.execute(
            "SELECT (SELECT COUNT(*) FROM consultation_dispatch), "
            "(SELECT COUNT(*) FROM consultation_cost_charge), "
            "(SELECT COUNT(*) FROM event WHERE event_type=?)",
            (DISPATCH_ADMISSION_EVENT_TYPE,),
        ).fetchone()
        if tuple(counts) != (1, 1, 1):
            raise FixtureExecutionError(
                "protected fixture lock probe did not observe committed admission"
            )
        probe.rollback()
    finally:
        if probe.in_transaction:
            probe.rollback()
        probe.close()


def _terminalize_fixture_failure(
    runtime_root: Path | str,
    organism_id: str,
    *,
    admission: DispatchAdmissionResult,
    raw_package_bytes: bytes,
    clock: Clock | None,
) -> None:
    try:
        terminalize_fixture_dispatch(
            runtime_root,
            organism_id,
            dispatch_id=admission.dispatch_id,
            reason_code="fixture_output_invalid",
            raw_package_bytes=raw_package_bytes,
            clock=clock,
        )
    except Exception as exc:
        raise FixtureExecutionError(
            f"deterministic fixture failure terminalization failed: {exc}"
        ) from exc


def perform_fixture_dispatch(
    runtime_root: Path | str,
    organism_id: str,
    *,
    request_id: str,
    fixture_case_id: str,
    clock: Clock | None = None,
    protected_test_fault: str | None = None,
) -> FixtureDispatchResult:
    """Commit admission, then invoke only the exact deterministic fixture."""

    fixture_fault = (
        protected_test_fault
        if protected_test_fault in _PROTECTED_FIXTURE_FAULTS
        else None
    )
    admission_fault = None if fixture_fault is not None else protected_test_fault
    admission = admit_fixture_dispatch(
        runtime_root,
        organism_id,
        request_id=request_id,
        fixture_case_id=fixture_case_id,
        clock=clock,
        protected_test_fault=admission_fault,
    )
    if not admission.created:
        return FixtureDispatchResult(
            admission=admission,
            fixture_invoked=False,
            fixture_output=None,
        )
    try:
        if fixture_fault == "probe_lock_released":
            _protected_test_probe_lock_released(runtime_root, organism_id)
        if fixture_fault == "fixture_exception":
            raise RuntimeError("protected deterministic fixture failure")
        output = run_deterministic_fixture(
            deepcopy(admission.request_envelope),
            fixture_case_id,
        )
    except Exception as exc:
        _terminalize_fixture_failure(
            runtime_root,
            organism_id,
            admission=admission,
            raw_package_bytes=b"",
            clock=clock,
        )
        raise FixtureExecutionError(str(exc)) from exc
    if not isinstance(output, bytes):
        _terminalize_fixture_failure(
            runtime_root,
            organism_id,
            admission=admission,
            raw_package_bytes=b"",
            clock=clock,
        )
        raise FixtureExecutionError("deterministic fixture output must be bytes")
    if len(output) > 16 * 1024:
        _terminalize_fixture_failure(
            runtime_root,
            organism_id,
            admission=admission,
            raw_package_bytes=bytes(output),
            clock=clock,
        )
        raise FixtureExecutionError("deterministic fixture output exceeds 16 KiB")
    return FixtureDispatchResult(
        admission=admission,
        fixture_invoked=True,
        fixture_output=bytes(output),
    )
'''
    text = text[:start] + safe_dispatch + text[end:]
    path.write_text(text, encoding="utf-8")


def repair_existing_dispatch_tests() -> None:
    fixture_path = ROOT / "tests/test_phase2_dispatch_admission_fixture.py"
    text = fixture_path.read_text(encoding="utf-8")

    lock_test = '''def test_fixture_runs_only_after_commit_and_without_sqlite_ownership(
    tmp_path: Path,
) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-lock-release")
    result = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-action-candidate",
        clock=FakeClock.fixed(
            wall_time_utc_us=2_106_000_000_000_000,
            monotonic_ns=70_000_000,
        ),
        protected_test_fault="probe_lock_released",
    )
    assert result.admission.created is True
    assert result.fixture_invoked is True
    assert result.fixture_output == run_deterministic_fixture(
        result.admission.request_envelope,
        "valid-action-candidate",
    )

    second = perform_fixture_dispatch(
        root,
        paths.organism_id,
        request_id=wake.consultation_request.request_id,
        fixture_case_id="valid-action-candidate",
        clock=FakeClock([]),
    )
    assert second.admission.created is False
    assert second.fixture_invoked is False
    assert second.fixture_output is None
'''
    text = replace_function(
        text,
        "test_fixture_runs_only_after_commit_and_without_sqlite_ownership",
        "test_fixture_exception_preserves_single_conservative_charge",
        lock_test,
    )

    exception_test = '''def test_fixture_exception_preserves_single_conservative_charge(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-fixture-error")
    clock = FakeClock(
        [
            ClockReading(2_107_000_000_000_000, 80_000_000),
            ClockReading(2_108_000_000_000_000, 90_000_000),
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
    rows = _rows(paths)
    assert len(rows["dispatch"]) == len(rows["charge"]) == len(rows["event"]) == 1
    connection = connect_database(paths.database, read_only=True)
    try:
        terminal = connection.execute(
            "SELECT reason_code FROM consultation_dispatch_terminal"
        ).fetchone()
        completion = connection.execute(
            "SELECT terminal_id FROM consultation_cost_completion"
        ).fetchone()
        terminal_events = int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type="
                "'consultation_dispatch_terminalized'"
            ).fetchone()[0]
        )
        assert terminal is not None
        assert terminal["reason_code"] == "fixture_output_invalid"
        assert completion is not None and completion["terminal_id"] is not None
        assert terminal_events == 1
    finally:
        connection.close()
'''
    text = replace_function(
        text,
        "test_fixture_exception_preserves_single_conservative_charge",
        "test_default_fixture_is_two_argument_deterministic_and_noncanonical",
        exception_test,
    )
    if "fixture_runner" in text:
        raise RuntimeError("fixture_runner remains in dispatch fixture tests")
    fixture_path.write_text(text, encoding="utf-8")

    matrix_path = ROOT / "tests/test_phase2_dispatch_admission_matrix.py"
    matrix = matrix_path.read_text(encoding="utf-8")
    precommit_test = '''def test_forced_precommit_failure_never_calls_fixture(tmp_path: Path) -> None:
    root, paths, wake = _init_request(tmp_path, organism_id="dispatch-no-early-call")
    with pytest.raises(RuntimeError, match="protected dispatch admission fault"):
        perform_fixture_dispatch(
            root,
            paths.organism_id,
            request_id=wake.consultation_request.request_id,
            fixture_case_id="valid-action-candidate",
            clock=FakeClock.fixed(
                wall_time_utc_us=2_210_000_000_000_000,
                monotonic_ns=110_000_000,
            ),
            protected_test_fault="before_commit",
        )
    rows = _rows(paths)
    assert rows["dispatch"] == []
    assert rows["charge"] == []
    assert rows["event"] == []
'''
    matrix = replace_function(
        matrix,
        "test_forced_precommit_failure_never_calls_fixture",
        "test_real_active_database_reserve_refusal_is_nonmutating",
        precommit_test,
    )
    if "fixture_runner" in matrix:
        raise RuntimeError("fixture_runner remains in dispatch matrix tests")
    matrix_path.write_text(matrix, encoding="utf-8")


def write_repair_regressions() -> None:
    path = ROOT / "tests/test_phase2_implementation_audit_repairs.py"
    path.write_text(
        '''from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

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


AUDITED_DISPATCH_SHA256 = "dfda290b508dba16c802f084f564f1d8a8c68d0e"


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
''',
        encoding="utf-8",
    )


def main() -> None:
    repair_dispatch_runtime()
    repair_existing_dispatch_tests()
    write_repair_regressions()


if __name__ == "__main__":
    main()
