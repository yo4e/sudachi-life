"""Audited transformed-candidate publication and retention reconciliation.

The pre-repair implementation remains byte-identical in
``rollback_transform_impl``. This public module preserves that surface, adds
exact working-set guards, and removes only checkpoint registry rows that the
verified pre-rollback archive proves were later pruned.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any, Callable

from . import rollback_transform_impl as _impl
from .constants import CHECKPOINT_RETENTION_LIMIT
from .paths import OrganismPaths
from .rollback_intent import _load_archive
from .runtime_storage import ensure_runtime_working_set_within_limit

_Replace = Callable[[Path | str, Path | str], None]
_ReplaceGuard = Callable[[_Replace, Path | str, Path | str], None]
_replace_guard: ContextVar[_ReplaceGuard | None] = ContextVar(
    "transformed_candidate_replace_guard", default=None
)


class _GuardedOs:
    def __init__(self, base: object) -> None:
        self._base = base

    def __getattr__(self, name: str) -> object:
        return getattr(self._base, name)

    def replace(self, source: Path | str, destination: Path | str) -> None:
        guard = _replace_guard.get()
        if guard is None:
            self._base.replace(source, destination)
            return
        guard(self._base.replace, source, destination)


if not isinstance(_impl.os, _GuardedOs):
    _impl.os = _GuardedOs(_impl.os)

for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value
del _name, _value

_original_connect_database = _impl.connect_database
_original_validate_candidate = _impl._validate_transformed_candidate_directory
_PRUNE_FIELDS = {
    "latest_stable_checkpoint_id",
    "latest_stable_event_sequence",
    "pruned_artifact_size_bytes",
    "pruned_checkpoint_id",
    "pruned_database_size_bytes",
    "pruned_event_sequence",
    "pruned_lineage_generation",
    "pruned_provenance",
    "reason",
    "retained_checkpoint_count",
    "retained_checkpoint_store_bytes",
    "retention_limit",
}


@dataclass(frozen=True, slots=True)
class _Proof:
    checkpoint_id: str
    registry_row: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class _Plan:
    source_database: Path
    proofs: tuple[_Proof, ...]

    @property
    def ids(self) -> frozenset[str]:
        return frozenset(proof.checkpoint_id for proof in self.proofs)


@dataclass(slots=True)
class _TransformScope:
    paths: OrganismPaths
    source_candidate_dir: Path
    plan: _Plan | None = None


_transform_scope: ContextVar[_TransformScope | None] = ContextVar(
    "rollback_transform_scope", default=None
)
_validation_plan: ContextVar[_Plan | None] = ContextVar(
    "rollback_transform_validation_plan", default=None
)


def _resolved(path: Path | str) -> Path:
    return Path(path).resolve(strict=False)


def _manifest(path: Path, *, context: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise CandidateTransformError(f"{context} is missing or unsafe")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CandidateTransformError(f"{context} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise CandidateTransformError(f"{context} is not a JSON object")
    return value


def _exact_int(value: object, *, context: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise CandidateTransformError(f"{context} is not a protected integer")
    return value


def _rows(connection: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    rows = connection.execute(
        "SELECT * FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"
    ).fetchall()
    result = {str(row["checkpoint_id"]): row for row in rows}
    if len(result) != len(rows):
        raise CandidateTransformError("checkpoint registry identifiers are not unique")
    return result


def _derive_plan(
    paths: OrganismPaths,
    source_candidate_dir: Path,
    *,
    expected_archive_id: str | None = None,
    expected_source_event_sequence: int | None = None,
) -> _Plan:
    hint = _manifest(
        source_candidate_dir / "manifest.json",
        context="source restore candidate manifest",
    )
    selected_id = hint.get("selected_checkpoint_id")
    if not isinstance(selected_id, str) or not selected_id:
        raise CandidateTransformError("source candidate selected checkpoint is invalid")
    try:
        source_manifest = _impl._validate_candidate_directory(
            source_candidate_dir,
            source_checkpoint_dir=paths.checkpoints / selected_id,
        )
    except Exception as exc:
        raise CandidateTransformError(str(exc)) from exc

    archive_id = source_manifest.get("archive_id")
    source_boundary = source_manifest.get("source_event_sequence")
    if not isinstance(archive_id, str) or not archive_id:
        raise CandidateTransformError("source candidate archive identifier is invalid")
    source_boundary = _exact_int(
        source_boundary, context="source candidate event sequence", minimum=1
    )
    if expected_archive_id is not None and archive_id != expected_archive_id:
        raise CandidateTransformError("source candidate archive linkage changed")
    if (
        expected_source_event_sequence is not None
        and source_boundary != expected_source_event_sequence
    ):
        raise CandidateTransformError("source candidate event boundary changed")

    archive_dir, archive_manifest, archive_manifest_sha = _load_archive(
        paths, archive_id
    )
    expected_source = {
        "archive_manifest_sha256": archive_manifest_sha,
        "archive_database_sha256": archive_manifest["database_sha256"],
        "selected_checkpoint_id": archive_manifest["selected_checkpoint_id"],
        "source_lineage_generation": archive_manifest[
            "selected_checkpoint_lineage_generation"
        ],
        "source_event_sequence": archive_manifest[
            "selected_checkpoint_event_sequence"
        ],
        "source_checkpoint_manifest_sha256": archive_manifest[
            "selected_checkpoint_manifest_sha256"
        ],
        "source_checkpoint_database_sha256": archive_manifest[
            "selected_checkpoint_database_sha256"
        ],
        "source_checkpoint_database_size_bytes": archive_manifest[
            "selected_checkpoint_database_size_bytes"
        ],
        "source_checkpoint_provenance": archive_manifest[
            "selected_checkpoint_provenance"
        ],
    }
    for key, value in expected_source.items():
        if source_manifest.get(key) != value:
            raise CandidateTransformError(
                f"source candidate does not match rollback archive: {key}"
            )

    source_database = source_candidate_dir / "organism.sqlite3"
    source = _original_connect_database(source_database, read_only=True)
    archive = _original_connect_database(
        archive_dir / "organism.sqlite3", read_only=True
    )
    try:
        source_rows = _rows(source)
        archive_rows = _rows(archive)
        for checkpoint_id in source_rows.keys() & archive_rows.keys():
            if tuple(source_rows[checkpoint_id]) != tuple(archive_rows[checkpoint_id]):
                raise CandidateTransformError(
                    f"retained checkpoint registry row changed: {checkpoint_id}"
                )

        evidence: dict[str, tuple[sqlite3.Row, dict[str, Any]]] = {}
        events = archive.execute(
            "SELECT event_sequence, organism_id, lineage_generation, source, "
            "payload_json FROM event WHERE event_type='checkpoint_pruned' "
            "ORDER BY event_sequence"
        ).fetchall()
        for event in events:
            try:
                payload = json.loads(str(event["payload_json"]))
            except json.JSONDecodeError as exc:
                raise CandidateTransformError(
                    "checkpoint_pruned evidence is not valid JSON"
                ) from exc
            if not isinstance(payload, dict) or set(payload) != _PRUNE_FIELDS:
                raise CandidateTransformError(
                    "checkpoint_pruned evidence field set is invalid"
                )
            checkpoint_id = payload["pruned_checkpoint_id"]
            if not isinstance(checkpoint_id, str) or not checkpoint_id:
                raise CandidateTransformError(
                    "checkpoint_pruned evidence identifier is invalid"
                )
            if checkpoint_id in evidence:
                raise CandidateTransformError(
                    "checkpoint_pruned evidence repeats an identifier"
                )
            evidence[checkpoint_id] = (event, payload)

        proofs: list[_Proof] = []
        missing_ids = sorted(
            source_rows.keys() - archive_rows.keys(),
            key=lambda value: (int(source_rows[value]["event_sequence"]), value),
        )
        for checkpoint_id in missing_ids:
            row = source_rows[checkpoint_id]
            found = evidence.get(checkpoint_id)
            if found is None:
                raise CandidateTransformError(
                    "missing registry row has no checkpoint_pruned evidence"
                )
            event, payload = found
            pruned_event_sequence = _exact_int(
                payload["pruned_event_sequence"],
                context="pruned checkpoint event sequence",
                minimum=1,
            )
            pruned_lineage = _exact_int(
                payload["pruned_lineage_generation"],
                context="pruned checkpoint lineage",
            )
            pruned_database_bytes = _exact_int(
                payload["pruned_database_size_bytes"],
                context="pruned checkpoint database bytes",
                minimum=1,
            )
            retention_limit = _exact_int(
                payload["retention_limit"],
                context="checkpoint retention limit",
                minimum=1,
            )
            provenance = payload["pruned_provenance"]
            if not isinstance(provenance, str) or not provenance:
                raise CandidateTransformError(
                    "checkpoint_pruned provenance is invalid"
                )
            checks = {
                "authority": event["source"]
                == "administration:checkpoint-retention",
                "organism": event["organism_id"] == archive_manifest["organism_id"],
                "event lineage": int(event["lineage_generation"])
                == int(row["lineage_generation"]),
                "event order": int(event["event_sequence"]) > source_boundary,
                "row order": int(row["event_sequence"]) < source_boundary,
                "protected row": int(row["protected"]) == 1,
                "reason": payload["reason"] == "checkpoint_retention_limit",
                "retention limit": retention_limit == CHECKPOINT_RETENTION_LIMIT,
                "checkpoint sequence": pruned_event_sequence
                == int(row["event_sequence"]),
                "checkpoint lineage": pruned_lineage
                == int(row["lineage_generation"]),
                "database bytes": pruned_database_bytes
                == int(row["database_size_bytes"]),
            }
            failed = next((name for name, passed in checks.items() if not passed), None)
            if failed is not None:
                raise CandidateTransformError(
                    f"checkpoint_pruned evidence mismatch: {failed}"
                )
            if (
                _exact_int(
                    payload["pruned_artifact_size_bytes"],
                    context="pruned artifact bytes",
                    minimum=1,
                )
                <= int(row["database_size_bytes"])
            ):
                raise CandidateTransformError(
                    "checkpoint_pruned artifact accounting is invalid"
                )
            if _exact_int(
                payload["retained_checkpoint_count"],
                context="retained checkpoint count",
            ) < CHECKPOINT_RETENTION_LIMIT:
                raise CandidateTransformError(
                    "checkpoint_pruned retained checkpoint count is invalid"
                )
            _exact_int(
                payload["retained_checkpoint_store_bytes"],
                context="retained checkpoint store bytes",
            )
            _exact_int(
                payload["latest_stable_event_sequence"],
                context="checkpoint_pruned latest stable sequence",
                minimum=1,
            )
            if provenance == "genesis":
                raise CandidateTransformError(
                    "checkpoint_pruned evidence may not remove genesis"
                )
            if Path(checkpoint_id).name != checkpoint_id:
                raise CandidateTransformError("checkpoint identifier is unsafe")
            if (paths.checkpoints / checkpoint_id).exists():
                raise CandidateTransformError(
                    "checkpoint_pruned registry row still has a retained artifact"
                )
            if (paths.checkpoints / f".pruning-{checkpoint_id}").exists():
                raise CandidateTransformError(
                    "checkpoint_pruned registry row still has a staged artifact"
                )
            proofs.append(_Proof(checkpoint_id, tuple(row)))

        return _Plan(_resolved(source_database), tuple(proofs))
    finally:
        archive.close()
        source.close()


class _FilteredCursor:
    def __init__(self, cursor: sqlite3.Cursor, rows: list[sqlite3.Row]) -> None:
        self._cursor = cursor
        self._rows = rows

    def __getattr__(self, name: str) -> object:
        return getattr(self._cursor, name)

    def fetchall(self) -> list[sqlite3.Row]:
        rows, self._rows = self._rows, []
        return rows


class _FilteredSourceConnection:
    def __init__(self, connection: sqlite3.Connection, ids: frozenset[str]) -> None:
        self._connection = connection
        self._ids = ids

    def __getattr__(self, name: str) -> object:
        return getattr(self._connection, name)

    def execute(self, sql: str, parameters: tuple[object, ...] = ()):
        cursor = self._connection.execute(sql, parameters)
        normalized = " ".join(sql.replace('"', "").lower().split())
        if (
            normalized.startswith("select * from checkpoint_registry")
            and " where " not in normalized
        ):
            return _FilteredCursor(
                cursor,
                [
                    row
                    for row in cursor.fetchall()
                    if str(row["checkpoint_id"]) not in self._ids
                ],
            )
        return cursor


class _ReconciledConnection:
    def __init__(self, connection: sqlite3.Connection, plan: _Plan) -> None:
        self._connection = connection
        self._plan = plan
        self._applied = False

    def __getattr__(self, name: str) -> object:
        return getattr(self._connection, name)

    def execute(self, sql: str, parameters: tuple[object, ...] = ()):
        cursor = self._connection.execute(sql, parameters)
        if not self._applied and " ".join(sql.lower().split()) == "begin immediate":
            for proof in self._plan.proofs:
                row = self._connection.execute(
                    "SELECT * FROM checkpoint_registry WHERE checkpoint_id=?",
                    (proof.checkpoint_id,),
                ).fetchone()
                if row is None or tuple(row) != proof.registry_row:
                    raise CandidateTransformError(
                        "checkpoint registry changed before reconciliation"
                    )
                deleted = self._connection.execute(
                    "DELETE FROM checkpoint_registry WHERE checkpoint_id=?",
                    (proof.checkpoint_id,),
                )
                if deleted.rowcount != 1:
                    raise CandidateTransformError(
                        "checkpoint reconciliation did not delete exactly one row"
                    )
            self._applied = True
        return cursor


def _scoped_connect_database(path: Path, *, read_only: bool = False):
    connection = _original_connect_database(path, read_only=read_only)
    plan = _validation_plan.get()
    if (
        plan is not None
        and plan.proofs
        and read_only
        and _resolved(path) == plan.source_database
    ):
        return _FilteredSourceConnection(connection, plan.ids)

    scope = _transform_scope.get()
    path = Path(path)
    is_transform_temp = (
        scope is not None
        and not read_only
        and path.name == "organism.sqlite3"
        and path.parent.name.startswith(".tmp-transformed-candidate-")
        and _resolved(path.parent.parent) == _resolved(scope.paths.restore_candidates)
    )
    if is_transform_temp:
        assert scope is not None
        try:
            current = _derive_plan(scope.paths, scope.source_candidate_dir)
        except Exception:
            connection.close()
            raise
        if scope.plan is not None and scope.plan != current:
            connection.close()
            raise CandidateTransformError(
                "checkpoint reconciliation plan changed during transformation"
            )
        scope.plan = current
        if current.proofs:
            return _ReconciledConnection(connection, current)
    return connection


def _validate_transformed_candidate_directory(
    candidate_dir: Path,
    *,
    source_candidate_dir: Path,
    selected_registry: sqlite3.Row,
    expected_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = expected_manifest or _manifest(
        candidate_dir / "manifest.json", context="transformed candidate manifest"
    )
    organism_id = manifest.get("organism_id")
    if not isinstance(organism_id, str) or not organism_id:
        raise CandidateTransformError("transformed candidate organism is invalid")
    paths = OrganismPaths.build(candidate_dir.parent.parent.parent, organism_id)
    if _resolved(candidate_dir.parent) != _resolved(paths.restore_candidates):
        raise CandidateTransformError("transformed candidate root is invalid")
    source_id = manifest.get("source_restore_candidate_id")
    if (
        not isinstance(source_id, str)
        or _resolved(source_candidate_dir)
        != _resolved(paths.restore_candidates / source_id)
    ):
        raise CandidateTransformError("transformed candidate source linkage is invalid")
    if selected_registry["checkpoint_id"] != manifest.get("selected_checkpoint_id"):
        raise CandidateTransformError("transformed candidate checkpoint linkage is invalid")
    archive_id = manifest.get("archive_id")
    source_boundary = _exact_int(
        manifest.get("source_event_sequence"),
        context="transformed candidate source boundary",
        minimum=1,
    )
    if not isinstance(archive_id, str):
        raise CandidateTransformError("transformed candidate archive linkage is invalid")
    plan = _derive_plan(
        paths,
        source_candidate_dir,
        expected_archive_id=archive_id,
        expected_source_event_sequence=source_boundary,
    )
    scope = _transform_scope.get()
    if scope is not None and scope.plan is not None and scope.plan != plan:
        raise CandidateTransformError(
            "checkpoint reconciliation plan changed before validation"
        )
    token = _validation_plan.set(plan)
    try:
        return _original_validate_candidate(
            candidate_dir,
            source_candidate_dir=source_candidate_dir,
            selected_registry=selected_registry,
            expected_manifest=expected_manifest,
        )
    finally:
        _validation_plan.reset(token)


_impl.connect_database = _scoped_connect_database
_impl._validate_transformed_candidate_directory = _validate_transformed_candidate_directory


def _working_set_error(paths: OrganismPaths, *, context: str) -> None:
    try:
        ensure_runtime_working_set_within_limit(paths, context=context)
    except SchemaValidationError as exc:
        raise CandidateTransformError(str(exc)) from exc


def _remove_failed_candidate(path: Path, *, context: str) -> None:
    try:
        if path.exists():
            shutil.rmtree(path)
        _fsync_dir(path.parent)
    except OSError as exc:
        raise CandidateTransformError(f"{context}: candidate cleanup failed") from exc


def _guarded_candidate_replace(paths: OrganismPaths) -> _ReplaceGuard:
    def guarded_replace(
        replace: _Replace,
        source: Path | str,
        destination: Path | str,
    ) -> None:
        try:
            _working_set_error(paths, context="transformed candidate pre-publication")
        except CandidateTransformError:
            _remove_failed_candidate(
                Path(source), context="transformed candidate pre-publication"
            )
            raise
        replace(source, destination)
        try:
            _working_set_error(paths, context="transformed candidate publication")
        except CandidateTransformError:
            _remove_failed_candidate(
                Path(destination), context="transformed candidate publication"
            )
            raise

    return guarded_replace


def transform_restore_candidate(
    runtime_root: Path | str,
    organism_id: str,
    source_candidate_id: str,
    administrative_reason: str,
    *,
    clock: Clock | None = None,
    protected_test_fail_after_event_insert: bool = False,
    protected_test_fail_before_publish: bool = False,
) -> CandidateTransformResult:
    """Transform or reuse a candidate within physical and retention bounds."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    _working_set_error(paths, context="transformed candidate admission")
    scope = _TransformScope(
        paths=paths,
        source_candidate_dir=paths.restore_candidates / source_candidate_id,
    )
    replace_token = _replace_guard.set(_guarded_candidate_replace(paths))
    transform_token = _transform_scope.set(scope)
    try:
        return _impl.transform_restore_candidate(
            runtime_root,
            organism_id,
            source_candidate_id,
            administrative_reason,
            clock=clock,
            protected_test_fail_after_event_insert=protected_test_fail_after_event_insert,
            protected_test_fail_before_publish=protected_test_fail_before_publish,
        )
    finally:
        _transform_scope.reset(transform_token)
        _replace_guard.reset(replace_token)
