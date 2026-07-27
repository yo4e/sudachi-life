"""Verified restore-candidate construction from one durable rollback intent."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
from typing import Any

from .constants import CHECKPOINT_ARTIFACT_MAX_BYTES, RUNTIME_WORKING_SET_MAX_BYTES
from .errors import CheckpointError, OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .rollback import (
    RollbackArchiveError,
    RollbackPreparationRejectedError,
    _canonical_json_bytes,
    _fsync_dir,
    _fsync_file,
    _sha256_file,
    _tree_size,
    _validate_selected_checkpoint,
)
from .rollback_intent import (
    RollbackBeginRejectedError,
    _canonical_sqlite_snapshot,
    _load_archive,
)
from .storage import connect_database, validate_canonical_state

RESTORE_CANDIDATE_FORMAT_VERSION = 1


class RestoreCandidateBusyError(SudachiError):
    """Restore-candidate construction could not acquire administrative ownership."""


class RestoreCandidateRejectedError(SudachiError):
    """The durable rollback intent is not eligible for candidate construction."""


class RestoreCandidateError(SudachiError):
    """A verified restore candidate could not be created or validated."""


class _InjectedRestoreCandidateFailure(Exception):
    """Protected test-only failure after temporary candidate validation."""


@dataclass(frozen=True, slots=True)
class RestoreCandidateResult:
    organism_id: str
    candidate_id: str
    candidate_dir: Path
    rollback_started_event_sequence: int
    archive_id: str
    selected_checkpoint_id: str
    source_lineage_generation: int
    source_lifecycle_number: int
    source_event_sequence: int
    database_size_bytes: int
    database_sha256: str
    manifest_sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "candidate_id": self.candidate_id,
            "candidate_dir": str(self.candidate_dir),
            "rollback_started_event_sequence": self.rollback_started_event_sequence,
            "archive_id": self.archive_id,
            "selected_checkpoint_id": self.selected_checkpoint_id,
            "source_lineage_generation": self.source_lineage_generation,
            "source_lifecycle_number": self.source_lifecycle_number,
            "source_event_sequence": self.source_event_sequence,
            "database_size_bytes": self.database_size_bytes,
            "database_sha256": self.database_sha256,
            "manifest_sha256": self.manifest_sha256,
        }


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def _parse_rollback_started_payload(row: sqlite3.Row) -> dict[str, Any]:
    try:
        payload = json.loads(row["payload_json"])
    except json.JSONDecodeError as exc:
        raise RestoreCandidateRejectedError(
            "rollback_started event payload is not valid JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise RestoreCandidateRejectedError(
            "rollback_started event payload is not a JSON object"
        )
    required_keys = {
        "archive_database_sha256",
        "archive_id",
        "archive_manifest_sha256",
        "latest_stable_checkpoint_id",
        "latest_stable_event_sequence",
        "pre_rollback_event_sequence",
        "pre_rollback_lifecycle_number",
        "pre_rollback_lineage_generation",
        "pre_rollback_status",
        "selected_checkpoint_database_sha256",
        "selected_checkpoint_event_sequence",
        "selected_checkpoint_id",
        "selected_checkpoint_lineage_generation",
        "selected_checkpoint_manifest_sha256",
    }
    if set(payload) != required_keys:
        raise RestoreCandidateRejectedError(
            "rollback_started event payload keys do not match the protected format"
        )
    return payload


def _validate_active_abandoned_future(
    active: sqlite3.Connection,
    archived: sqlite3.Connection,
    *,
    active_organism: sqlite3.Row,
    payload: dict[str, Any],
    rollback_started: sqlite3.Row,
) -> None:
    active_snapshot = _canonical_sqlite_snapshot(active)
    archived_snapshot = _canonical_sqlite_snapshot(archived)
    if active_snapshot["user_version"] != archived_snapshot["user_version"]:
        raise RestoreCandidateRejectedError(
            "active schema version drifted after rollback begin"
        )
    if active_snapshot["schema"] != archived_snapshot["schema"]:
        raise RestoreCandidateRejectedError("active schema drifted after rollback begin")

    active_tables = active_snapshot["tables"]
    archived_tables = archived_snapshot["tables"]
    if set(active_tables) != set(archived_tables):
        raise RestoreCandidateRejectedError(
            "active canonical table set drifted after rollback begin"
        )
    for table_name in sorted(active_tables):
        if table_name in {"organism", "event"}:
            continue
        if active_tables[table_name] != archived_tables[table_name]:
            raise RestoreCandidateRejectedError(
                f"active canonical table drifted after rollback begin: {table_name}"
            )

    archived_organism = archived.execute(
        "SELECT * FROM organism WHERE singleton_id = 1"
    ).fetchone()
    if archived_organism is None:
        raise RestoreCandidateRejectedError(
            "pre-rollback archive is missing the organism singleton"
        )
    active_organism_dict = dict(active_organism)
    archived_organism_dict = dict(archived_organism)
    if archived_organism_dict.get("status") != payload["pre_rollback_status"]:
        raise RestoreCandidateRejectedError(
            "archive pre-rollback status does not match durable intent"
        )
    active_organism_dict["status"] = payload["pre_rollback_status"]
    if active_organism_dict != archived_organism_dict:
        raise RestoreCandidateRejectedError(
            "active organism state drifted after rollback begin"
        )

    active_events = active_tables["event"]
    archived_events = archived_tables["event"]
    if active_events[:-1] != archived_events or active_events[-1:] != [tuple(rollback_started)]:
        raise RestoreCandidateRejectedError(
            "active event history drifted after rollback begin"
        )

    active_sequence = dict(active_snapshot["sqlite_sequence"])
    archived_sequence = dict(archived_snapshot["sqlite_sequence"])
    if set(active_sequence) != set(archived_sequence):
        raise RestoreCandidateRejectedError(
            "active AUTOINCREMENT state drifted after rollback begin"
        )
    for name, archived_value in archived_sequence.items():
        expected = int(archived_value) + 1 if name == "event" else int(archived_value)
        if int(active_sequence[name]) != expected:
            raise RestoreCandidateRejectedError(
                f"active AUTOINCREMENT state drifted after rollback begin: {name}"
            )


def _validate_durable_intent(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
) -> tuple[
    sqlite3.Row,
    sqlite3.Row,
    dict[str, Any],
    Path,
    dict[str, Any],
    sqlite3.Row,
    dict[str, Any],
]:
    organism = connection.execute(
        "SELECT * FROM organism WHERE singleton_id = 1"
    ).fetchone()
    if organism is None:
        raise RestoreCandidateRejectedError("canonical organism state is missing")
    if organism["status"] != "rollback_in_progress":
        raise RestoreCandidateRejectedError(
            "restore-candidate construction requires rollback_in_progress: "
            f"status={organism['status']}"
        )
    if int(organism["checkpoint_pending"]) != 0:
        raise RestoreCandidateRejectedError(
            "restore-candidate construction requires no pending checkpoint"
        )

    rollback_started = connection.execute(
        "SELECT * FROM event ORDER BY event_sequence DESC LIMIT 1"
    ).fetchone()
    if rollback_started is None:
        raise RestoreCandidateRejectedError(
            "rollback_in_progress has no canonical event history"
        )
    if (
        rollback_started["event_type"] != "rollback_started"
        or rollback_started["source"] != "administration:rollback"
        or int(rollback_started["lineage_generation"])
        != int(organism["lineage_generation"])
        or int(rollback_started["lifecycle_number"])
        != int(organism["lifecycle_number"])
        or int(rollback_started["schema_version"]) != int(organism["schema_version"])
        or rollback_started["environment_version"] != organism["environment_version"]
        or rollback_started["budget_config_version"] != organism["budget_config_version"]
    ):
        raise RestoreCandidateRejectedError(
            "active event tip is not the protected rollback_started intent"
        )

    payload = _parse_rollback_started_payload(rollback_started)
    if payload["pre_rollback_status"] not in {"sleeping", "maintenance_required"}:
        raise RestoreCandidateRejectedError(
            "rollback_started pre-rollback status is invalid"
        )
    if int(rollback_started["event_sequence"]) != int(
        payload["pre_rollback_event_sequence"]
    ) + 1:
        raise RestoreCandidateRejectedError(
            "rollback_started event is not the exact successor of the abandoned future"
        )
    active_expected = {
        "organism_id": organism["organism_id"],
        "lineage_generation": int(organism["lineage_generation"]),
        "lifecycle_number": int(organism["lifecycle_number"]),
        "latest_stable_checkpoint_id": organism["latest_stable_checkpoint_id"],
        "latest_stable_event_sequence": int(organism["latest_stable_event_sequence"]),
    }
    payload_expected = {
        "organism_id": rollback_started["organism_id"],
        "lineage_generation": int(payload["pre_rollback_lineage_generation"]),
        "lifecycle_number": int(payload["pre_rollback_lifecycle_number"]),
        "latest_stable_checkpoint_id": payload["latest_stable_checkpoint_id"],
        "latest_stable_event_sequence": int(payload["latest_stable_event_sequence"]),
    }
    if active_expected != payload_expected:
        raise RestoreCandidateRejectedError(
            "active protected metadata does not match rollback_started intent"
        )

    archive_dir, archive_manifest, archive_manifest_sha256 = _load_archive(
        paths, str(payload["archive_id"])
    )
    if archive_manifest_sha256 != payload["archive_manifest_sha256"]:
        raise RestoreCandidateRejectedError(
            "rollback archive manifest digest does not match durable intent"
        )
    if archive_manifest.get("database_sha256") != payload["archive_database_sha256"]:
        raise RestoreCandidateRejectedError(
            "rollback archive database digest does not match durable intent"
        )
    archive_expected = {
        "organism_id": organism["organism_id"],
        "active_lineage_generation": int(payload["pre_rollback_lineage_generation"]),
        "active_lifecycle_number": int(payload["pre_rollback_lifecycle_number"]),
        "active_status": payload["pre_rollback_status"],
        "active_event_sequence": int(payload["pre_rollback_event_sequence"]),
        "latest_stable_checkpoint_id": payload["latest_stable_checkpoint_id"],
        "latest_stable_event_sequence": int(payload["latest_stable_event_sequence"]),
        "selected_checkpoint_id": payload["selected_checkpoint_id"],
        "selected_checkpoint_lineage_generation": int(
            payload["selected_checkpoint_lineage_generation"]
        ),
        "selected_checkpoint_event_sequence": int(
            payload["selected_checkpoint_event_sequence"]
        ),
        "selected_checkpoint_manifest_sha256": payload[
            "selected_checkpoint_manifest_sha256"
        ],
        "selected_checkpoint_database_sha256": payload[
            "selected_checkpoint_database_sha256"
        ],
    }
    for key, value in archive_expected.items():
        if archive_manifest.get(key) != value:
            raise RestoreCandidateRejectedError(
                f"rollback archive does not match durable intent: {key}"
            )

    archived = connect_database(archive_dir / "organism.sqlite3", read_only=True)
    try:
        _validate_active_abandoned_future(
            connection,
            archived,
            active_organism=organism,
            payload=payload,
            rollback_started=rollback_started,
        )
    finally:
        archived.close()

    source_event_sequence = int(payload["selected_checkpoint_event_sequence"])
    selected, selected_manifest = _validate_selected_checkpoint(
        connection,
        paths,
        organism,
        source_event_sequence,
    )
    selected_expected = {
        "selected_checkpoint_id": str(selected["checkpoint_id"]),
        "selected_checkpoint_lineage_generation": int(selected["lineage_generation"]),
        "selected_checkpoint_event_sequence": int(selected["event_sequence"]),
        "selected_checkpoint_manifest_sha256": str(selected["manifest_sha256"]),
        "selected_checkpoint_database_sha256": str(selected["database_sha256"]),
    }
    for key, value in selected_expected.items():
        if payload[key] != value:
            raise RestoreCandidateRejectedError(
                f"selected rollback source does not match durable intent: {key}"
            )
    selected_archive_expected = {
        **selected_expected,
        "selected_checkpoint_database_size_bytes": int(selected["database_size_bytes"]),
        "selected_checkpoint_provenance": str(selected_manifest["provenance"]),
    }
    for key, value in selected_archive_expected.items():
        if archive_manifest.get(key) != value:
            raise RestoreCandidateRejectedError(
                f"selected rollback source does not match archive: {key}"
            )
    return (
        organism,
        rollback_started,
        payload,
        archive_dir,
        archive_manifest,
        selected,
        selected_manifest,
    )


def _validate_candidate_directory(
    candidate_dir: Path,
    *,
    source_checkpoint_dir: Path,
    expected_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not candidate_dir.is_dir() or candidate_dir.is_symlink():
        raise RestoreCandidateError("restore candidate directory is missing or unsafe")
    if {entry.name for entry in candidate_dir.iterdir()} != {
        "organism.sqlite3",
        "manifest.json",
    }:
        raise RestoreCandidateError("restore candidate contains unexpected entries")

    database_path = candidate_dir / "organism.sqlite3"
    manifest_path = candidate_dir / "manifest.json"
    if not database_path.is_file() or database_path.is_symlink():
        raise RestoreCandidateError("restore candidate database is missing or unsafe")
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise RestoreCandidateError("restore candidate manifest is missing or unsafe")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RestoreCandidateError(
            "restore candidate manifest is not valid JSON"
        ) from exc
    if expected_manifest is not None and manifest != expected_manifest:
        raise RestoreCandidateError(
            "restore candidate manifest changed before publication"
        )
    if manifest.get("restore_candidate_format_version") != RESTORE_CANDIDATE_FORMAT_VERSION:
        raise RestoreCandidateError("unsupported restore candidate format")
    if manifest.get("status") != "published":
        raise RestoreCandidateError("restore candidate publication status is invalid")
    if manifest.get("provenance") != "restore_candidate":
        raise RestoreCandidateError("restore candidate provenance is invalid")
    if manifest.get("candidate_state") != "source_restored_untransformed":
        raise RestoreCandidateError("restore candidate state is invalid")
    if manifest.get("database_filename") != "organism.sqlite3":
        raise RestoreCandidateError("restore candidate database filename mismatch")
    if manifest.get("snapshot_method") != "python-sqlite3-connection-backup":
        raise RestoreCandidateError("restore candidate snapshot method mismatch")
    if expected_manifest is None and candidate_dir.name != manifest.get("candidate_id"):
        raise RestoreCandidateError(
            "restore candidate directory name does not match manifest"
        )
    size = database_path.stat().st_size
    if size != manifest.get("database_size_bytes"):
        raise RestoreCandidateError("restore candidate database size mismatch")
    if _sha256_file(database_path) != manifest.get("database_sha256"):
        raise RestoreCandidateError("restore candidate database digest mismatch")

    candidate = connect_database(database_path, read_only=True)
    source = connect_database(source_checkpoint_dir / "organism.sqlite3", read_only=True)
    try:
        integrity = candidate.execute("PRAGMA integrity_check").fetchall()
        if len(integrity) != 1 or integrity[0][0] != "ok":
            raise RestoreCandidateError(
                f"restore candidate integrity check failed: {integrity!r}"
            )
        foreign_keys = candidate.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_keys:
            raise RestoreCandidateError(
                f"restore candidate foreign-key check failed: {foreign_keys!r}"
            )
        validate_canonical_state(candidate, expect_checkpoint_pending=True)
        if _canonical_sqlite_snapshot(candidate) != _canonical_sqlite_snapshot(source):
            raise RestoreCandidateError(
                "restore candidate does not exactly match the selected checkpoint"
            )
        organism = candidate.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        max_event = int(
            candidate.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) FROM event"
            ).fetchone()[0]
        )
        if organism is None:
            raise RestoreCandidateError("restore candidate organism state is missing")
        expected = {
            "organism_id": organism["organism_id"],
            "source_lineage_generation": int(organism["lineage_generation"]),
            "source_lifecycle_number": int(organism["lifecycle_number"]),
            "source_event_sequence": max_event,
            "contract_version": organism["contract_version"],
            "schema_version": int(organism["schema_version"]),
            "environment_version": organism["environment_version"],
            "budget_config_version": organism["budget_config_version"],
        }
        for key, value in expected.items():
            if manifest.get(key) != value:
                raise RestoreCandidateError(
                    f"restore candidate {key} does not match database contents"
                )
        if (
            int(organism["checkpoint_pending"]) != 1
            or int(organism["pending_checkpoint_generation"])
            != manifest["source_lineage_generation"]
            or int(organism["pending_checkpoint_event_sequence"])
            != manifest["source_event_sequence"]
        ):
            raise RestoreCandidateError(
                "restore candidate pending checkpoint boundary is invalid"
            )
    except SchemaValidationError as exc:
        raise RestoreCandidateError(str(exc)) from exc
    finally:
        source.close()
        candidate.close()
    return manifest


def build_restore_candidate(
    runtime_root: Path | str,
    organism_id: str,
    *,
    protected_test_fail_before_publish: bool = False,
) -> RestoreCandidateResult:
    """Construct and atomically publish one source-restored rollback candidate."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file() or paths.database.is_symlink():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database)
    temp_dir: Path | None = None
    final_dir: Path | None = None
    published_new = False
    completed = False
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise RestoreCandidateBusyError(
                    "restore-candidate construction is busy; this attempt was not queued"
                ) from exc
            raise

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        (
            organism,
            rollback_started,
            payload,
            _archive_dir,
            _archive_manifest,
            selected,
            selected_manifest,
        ) = _validate_durable_intent(connection, paths)

        candidates_dir = paths.restore_candidates
        candidates_dir.mkdir(mode=0o700, exist_ok=True)
        if not candidates_dir.is_dir() or candidates_dir.is_symlink():
            raise RestoreCandidateError("restore candidate root is missing or unsafe")
        if any(entry.is_symlink() for entry in candidates_dir.iterdir()):
            raise RestoreCandidateError(
                "restore candidate root contains an unsafe symlink"
            )

        source_checkpoint_dir = paths.checkpoints / str(selected["checkpoint_id"])
        source_database_size = int(selected["database_size_bytes"])
        rollback_started_event_sequence = int(rollback_started["event_sequence"])
        source_event_sequence = int(selected["event_sequence"])
        candidate_id = (
            f"rc-g{int(organism['lineage_generation']):06d}-"
            f"rb-e{rollback_started_event_sequence:012d}-"
            f"from-e{source_event_sequence:012d}-"
            f"{str(selected['database_sha256'])[:8]}"
        )
        final_dir = candidates_dir / candidate_id
        context_expected = {
            "candidate_id": candidate_id,
            "organism_id": str(organism["organism_id"]),
            "active_lineage_generation": int(organism["lineage_generation"]),
            "rollback_started_event_sequence": rollback_started_event_sequence,
            "archive_id": str(payload["archive_id"]),
            "archive_manifest_sha256": str(payload["archive_manifest_sha256"]),
            "archive_database_sha256": str(payload["archive_database_sha256"]),
            "selected_checkpoint_id": str(selected["checkpoint_id"]),
            "source_lineage_generation": int(selected["lineage_generation"]),
            "source_lifecycle_number": int(selected_manifest["lifecycle_number"]),
            "source_event_sequence": source_event_sequence,
            "source_checkpoint_manifest_sha256": str(selected["manifest_sha256"]),
            "source_checkpoint_database_sha256": str(selected["database_sha256"]),
            "source_checkpoint_database_size_bytes": source_database_size,
            "source_checkpoint_provenance": str(selected_manifest["provenance"]),
            "contract_version": str(organism["contract_version"]),
            "schema_version": int(organism["schema_version"]),
            "environment_version": str(organism["environment_version"]),
            "budget_config_version": str(organism["budget_config_version"]),
            "database_filename": "organism.sqlite3",
            "snapshot_method": "python-sqlite3-connection-backup",
            "implementation_version": "0.1.0",
            "candidate_state": "source_restored_untransformed",
            "status": "published",
            "provenance": "restore_candidate",
        }
        if final_dir.exists():
            existing = _validate_candidate_directory(
                final_dir,
                source_checkpoint_dir=source_checkpoint_dir,
            )
            for key, value in context_expected.items():
                if existing.get(key) != value:
                    raise RestoreCandidateError(
                        f"existing restore candidate does not match durable intent: {key}"
                    )
            completed = True
            return RestoreCandidateResult(
                organism_id=str(existing["organism_id"]),
                candidate_id=str(existing["candidate_id"]),
                candidate_dir=final_dir,
                rollback_started_event_sequence=int(
                    existing["rollback_started_event_sequence"]
                ),
                archive_id=str(existing["archive_id"]),
                selected_checkpoint_id=str(existing["selected_checkpoint_id"]),
                source_lineage_generation=int(existing["source_lineage_generation"]),
                source_lifecycle_number=int(existing["source_lifecycle_number"]),
                source_event_sequence=int(existing["source_event_sequence"]),
                database_size_bytes=int(existing["database_size_bytes"]),
                database_sha256=str(existing["database_sha256"]),
                manifest_sha256=_sha256_file(final_dir / "manifest.json"),
            )

        predicted_size = (
            paths.database.stat().st_size
            + _tree_size(paths.checkpoints)
            + _tree_size(paths.rollback_archives)
            + _tree_size(candidates_dir)
            + source_database_size
        )
        if predicted_size > RUNTIME_WORKING_SET_MAX_BYTES:
            raise RestoreCandidateError(
                "restore candidate would exceed the protected runtime working-set limit"
            )

        temp_dir = Path(
            tempfile.mkdtemp(prefix=".tmp-restore-candidate-", dir=candidates_dir)
        )
        destination_path = temp_dir / "organism.sqlite3"
        manifest_path = temp_dir / "manifest.json"
        source = connect_database(
            source_checkpoint_dir / "organism.sqlite3", read_only=True
        )
        destination = sqlite3.connect(destination_path, isolation_level=None)
        try:
            source.backup(destination, pages=64, sleep=0.0)
        finally:
            destination.close()
            source.close()

        size = destination_path.stat().st_size
        if size > CHECKPOINT_ARTIFACT_MAX_BYTES:
            raise RestoreCandidateError(
                f"restore candidate database exceeds {CHECKPOINT_ARTIFACT_MAX_BYTES} bytes"
            )
        database_sha256 = _sha256_file(destination_path)
        manifest: dict[str, Any] = {
            "restore_candidate_format_version": RESTORE_CANDIDATE_FORMAT_VERSION,
            **context_expected,
            "database_size_bytes": size,
            "database_sha256": database_sha256,
        }
        manifest_bytes = _canonical_json_bytes(manifest)
        manifest_path.write_bytes(manifest_bytes)
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
        _validate_candidate_directory(
            temp_dir,
            source_checkpoint_dir=source_checkpoint_dir,
            expected_manifest=manifest,
        )
        _fsync_file(destination_path)
        _fsync_file(manifest_path)
        _fsync_dir(temp_dir)

        if protected_test_fail_before_publish:
            raise _InjectedRestoreCandidateFailure(
                "injected restore candidate failure before publication"
            )

        os.replace(temp_dir, final_dir)
        temp_dir = None
        published_new = True
        _fsync_dir(candidates_dir)
        _validate_candidate_directory(
            final_dir,
            source_checkpoint_dir=source_checkpoint_dir,
            expected_manifest=manifest,
        )
        completed = True
        return RestoreCandidateResult(
            organism_id=str(organism["organism_id"]),
            candidate_id=candidate_id,
            candidate_dir=final_dir,
            rollback_started_event_sequence=rollback_started_event_sequence,
            archive_id=str(payload["archive_id"]),
            selected_checkpoint_id=str(selected["checkpoint_id"]),
            source_lineage_generation=int(selected["lineage_generation"]),
            source_lifecycle_number=int(selected_manifest["lifecycle_number"]),
            source_event_sequence=source_event_sequence,
            database_size_bytes=size,
            database_sha256=database_sha256,
            manifest_sha256=manifest_sha256,
        )
    except _InjectedRestoreCandidateFailure as exc:
        raise RestoreCandidateError(str(exc)) from exc
    except (OSError, sqlite3.Error) as exc:
        raise RestoreCandidateError(str(exc)) from exc
    except (
        CheckpointError,
        RollbackArchiveError,
        RollbackBeginRejectedError,
        RollbackPreparationRejectedError,
        SchemaValidationError,
    ) as exc:
        raise RestoreCandidateRejectedError(str(exc)) from exc
    finally:
        if temp_dir is not None and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        if (
            published_new
            and not completed
            and final_dir is not None
            and final_dir.exists()
        ):
            shutil.rmtree(final_dir, ignore_errors=True)
            if final_dir.parent.exists():
                _fsync_dir(final_dir.parent)
        if connection.in_transaction:
            connection.rollback()
        connection.close()
