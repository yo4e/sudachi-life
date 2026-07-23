"""Offline rollback-source validation and verified pre-rollback archives."""

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

from .checkpoints import validate_checkpoint_directory
from .constants import (
    CHECKPOINT_ARTIFACT_MAX_BYTES,
    RUNTIME_WORKING_SET_MAX_BYTES,
)
from .errors import CheckpointError, OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state

ROLLBACK_ARCHIVE_FORMAT_VERSION = 1


class RollbackPreparationBusyError(SudachiError):
    """Rollback preparation could not acquire fail-fast administrative ownership."""


class RollbackPreparationRejectedError(SudachiError):
    """The active organism or selected checkpoint is not eligible for rollback preparation."""


class RollbackArchiveError(SudachiError):
    """A verified pre-rollback archive could not be created or validated."""


class _InjectedRollbackArchiveFailure(Exception):
    """Protected test-only failure after the temporary snapshot is complete."""


@dataclass(frozen=True, slots=True)
class RollbackPreparationResult:
    organism_id: str
    active_lineage_generation: int
    active_lifecycle_number: int
    active_status: str
    active_event_sequence: int
    latest_stable_checkpoint_id: str
    latest_stable_event_sequence: int
    selected_checkpoint_id: str
    selected_checkpoint_event_sequence: int
    archive_id: str
    archive_dir: Path
    database_size_bytes: int
    database_sha256: str
    manifest_sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "active_lineage_generation": self.active_lineage_generation,
            "active_lifecycle_number": self.active_lifecycle_number,
            "active_status": self.active_status,
            "active_event_sequence": self.active_event_sequence,
            "latest_stable_checkpoint_id": self.latest_stable_checkpoint_id,
            "latest_stable_event_sequence": self.latest_stable_event_sequence,
            "selected_checkpoint_id": self.selected_checkpoint_id,
            "selected_checkpoint_event_sequence": self.selected_checkpoint_event_sequence,
            "archive_id": self.archive_id,
            "archive_dir": str(self.archive_dir),
            "database_size_bytes": self.database_size_bytes,
            "database_sha256": self.database_sha256,
            "manifest_sha256": self.manifest_sha256,
        }


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _fsync_file(path: Path) -> None:
    with path.open("rb") as handle:
        os.fsync(handle.fileno())


def _fsync_dir(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _tree_size(root: Path) -> int:
    total = 0
    if not root.exists():
        return total
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            total += path.stat().st_size
    return total


def _validate_archive_directory(
    archive_dir: Path,
    *,
    expected_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not archive_dir.is_dir() or archive_dir.is_symlink():
        raise RollbackArchiveError("rollback archive directory is missing or unsafe")
    entries = {entry.name for entry in archive_dir.iterdir()}
    if entries != {"organism.sqlite3", "manifest.json"}:
        raise RollbackArchiveError("rollback archive contains unexpected entries")

    database_path = archive_dir / "organism.sqlite3"
    manifest_path = archive_dir / "manifest.json"
    if not database_path.is_file() or database_path.is_symlink():
        raise RollbackArchiveError("rollback archive database is missing or unsafe")
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise RollbackArchiveError("rollback archive manifest is missing or unsafe")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RollbackArchiveError("rollback archive manifest is not valid JSON") from exc
    if expected_manifest is not None and manifest != expected_manifest:
        raise RollbackArchiveError("rollback archive manifest changed before publication")
    if manifest.get("rollback_archive_format_version") != ROLLBACK_ARCHIVE_FORMAT_VERSION:
        raise RollbackArchiveError("unsupported rollback archive format")
    if manifest.get("status") != "published" or manifest.get("provenance") != "pre_rollback":
        raise RollbackArchiveError("rollback archive publication metadata is invalid")
    if manifest.get("database_filename") != "organism.sqlite3":
        raise RollbackArchiveError("rollback archive database filename mismatch")
    if manifest.get("snapshot_method") != "python-sqlite3-connection-backup":
        raise RollbackArchiveError("rollback archive snapshot method mismatch")
    if expected_manifest is None and archive_dir.name != manifest.get("archive_id"):
        raise RollbackArchiveError("rollback archive directory name does not match manifest")
    size = database_path.stat().st_size
    if size != manifest.get("database_size_bytes"):
        raise RollbackArchiveError("rollback archive database size mismatch")
    if _sha256_file(database_path) != manifest.get("database_sha256"):
        raise RollbackArchiveError("rollback archive database digest mismatch")

    connection = connect_database(database_path, read_only=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchall()
        if len(integrity) != 1 or integrity[0][0] != "ok":
            raise RollbackArchiveError(f"rollback archive integrity check failed: {integrity!r}")
        foreign_keys = connection.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_keys:
            raise RollbackArchiveError(
                f"rollback archive foreign-key check failed: {foreign_keys!r}"
            )
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        max_event = int(
            connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) FROM event"
            ).fetchone()[0]
        )
        if organism is None:
            raise RollbackArchiveError("rollback archive organism state is missing")
        expected = {
            "organism_id": organism["organism_id"],
            "active_lineage_generation": int(organism["lineage_generation"]),
            "active_lifecycle_number": int(organism["lifecycle_number"]),
            "active_status": str(organism["status"]),
            "active_event_sequence": max_event,
            "latest_stable_checkpoint_id": organism["latest_stable_checkpoint_id"],
            "latest_stable_event_sequence": int(organism["latest_stable_event_sequence"]),
            "contract_version": organism["contract_version"],
            "schema_version": int(organism["schema_version"]),
            "environment_version": organism["environment_version"],
            "budget_config_version": organism["budget_config_version"],
        }
        for key, value in expected.items():
            if manifest.get(key) != value:
                raise RollbackArchiveError(
                    f"rollback archive {key} does not match snapshot contents"
                )
        selected = connection.execute(
            """SELECT checkpoint_id, lineage_generation, event_sequence,
                      manifest_sha256, database_sha256, database_size_bytes, protected
               FROM checkpoint_registry WHERE checkpoint_id = ?""",
            (manifest.get("selected_checkpoint_id"),),
        ).fetchone()
        if selected is None:
            raise RollbackArchiveError("selected rollback source is missing from archive snapshot")
        if (
            int(selected["lineage_generation"]) != manifest.get("selected_checkpoint_lineage_generation")
            or int(selected["event_sequence"]) != manifest.get("selected_checkpoint_event_sequence")
            or selected["manifest_sha256"] != manifest.get("selected_checkpoint_manifest_sha256")
            or selected["database_sha256"] != manifest.get("selected_checkpoint_database_sha256")
            or int(selected["database_size_bytes"])
            != manifest.get("selected_checkpoint_database_size_bytes")
            or int(selected["protected"]) != 1
        ):
            raise RollbackArchiveError(
                "selected rollback source metadata does not match archive snapshot"
            )
    except SchemaValidationError as exc:
        raise RollbackArchiveError(str(exc)) from exc
    finally:
        connection.close()
    return manifest


def _validate_selected_checkpoint(
    connection: sqlite3.Connection,
    paths: OrganismPaths,
    organism: sqlite3.Row,
    source_event_sequence: int,
) -> tuple[sqlite3.Row, dict[str, Any]]:
    if source_event_sequence <= 0:
        raise RollbackPreparationRejectedError(
            "rollback source event sequence must be a positive integer"
        )
    rows = connection.execute(
        """SELECT checkpoint_id, lineage_generation, event_sequence,
                  manifest_sha256, database_sha256, database_size_bytes, protected
           FROM checkpoint_registry WHERE event_sequence = ? ORDER BY checkpoint_id""",
        (source_event_sequence,),
    ).fetchall()
    if len(rows) != 1:
        raise RollbackPreparationRejectedError(
            "rollback preparation requires exactly one retained stable checkpoint at "
            f"boundary {source_event_sequence}; found {len(rows)}"
        )
    checkpoint = rows[0]
    if int(checkpoint["protected"]) != 1:
        raise RollbackPreparationRejectedError("selected rollback source is not protected")
    if int(checkpoint["lineage_generation"]) != int(organism["lineage_generation"]):
        raise RollbackPreparationRejectedError(
            "selected rollback source does not belong to the active lineage"
        )
    if source_event_sequence > int(organism["latest_stable_event_sequence"]):
        raise RollbackPreparationRejectedError(
            "selected rollback source is newer than the latest stable boundary"
        )

    checkpoint_dir = paths.checkpoints / str(checkpoint["checkpoint_id"])
    if not checkpoint_dir.is_dir() or checkpoint_dir.is_symlink():
        raise RollbackPreparationRejectedError(
            "selected rollback source artifact is missing or unsafe"
        )
    entries = {entry.name for entry in checkpoint_dir.iterdir()}
    if entries != {"organism.sqlite3", "manifest.json"}:
        raise RollbackPreparationRejectedError(
            "selected rollback source contains unexpected entries"
        )
    manifest = validate_checkpoint_directory(checkpoint_dir)
    if (
        manifest.get("checkpoint_id") != checkpoint["checkpoint_id"]
        or manifest.get("organism_id") != organism["organism_id"]
        or int(manifest.get("lineage_generation", -1))
        != int(checkpoint["lineage_generation"])
        or int(manifest.get("event_sequence", -1)) != source_event_sequence
        or manifest.get("contract_version") != organism["contract_version"]
        or int(manifest.get("schema_version", -1)) != int(organism["schema_version"])
        or manifest.get("environment_version") != organism["environment_version"]
        or manifest.get("budget_config_version") != organism["budget_config_version"]
        or manifest.get("database_sha256") != checkpoint["database_sha256"]
        or int(manifest.get("database_size_bytes", -1))
        != int(checkpoint["database_size_bytes"])
        or _sha256_file(checkpoint_dir / "manifest.json")
        != checkpoint["manifest_sha256"]
    ):
        raise RollbackPreparationRejectedError(
            "selected rollback source artifact does not match the canonical registry"
        )
    return checkpoint, manifest


def prepare_rollback_archive(
    runtime_root: Path | str,
    organism_id: str,
    source_event_sequence: int,
    *,
    protected_test_fail_after_snapshot: bool = False,
) -> RollbackPreparationResult:
    """Validate a retained rollback source and publish the current active-state archive."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file() or paths.database.is_symlink():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database)
    temp_dir: Path | None = None
    final_dir: Path | None = None
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise RollbackPreparationBusyError(
                    "rollback preparation is busy; this attempt was not queued"
                ) from exc
            raise

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            """SELECT organism_id, contract_version, schema_version,
                      environment_version, budget_config_version,
                      lineage_generation, lifecycle_number, status,
                      checkpoint_pending, latest_stable_checkpoint_id,
                      latest_stable_event_sequence
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise RollbackPreparationRejectedError("canonical organism state is missing")
        if organism["status"] not in {"sleeping", "maintenance_required"}:
            raise RollbackPreparationRejectedError(
                "rollback preparation requires stable sleeping or maintenance state: "
                f"status={organism['status']}"
            )
        if int(organism["checkpoint_pending"]) != 0:
            raise RollbackPreparationRejectedError(
                "rollback preparation requires no pending checkpoint"
            )

        completed_rollbacks = int(
            connection.execute(
                "SELECT COUNT(*) FROM event WHERE event_type = 'rollback_completed'"
            ).fetchone()[0]
        )
        if completed_rollbacks != 0:
            raise RollbackPreparationRejectedError(
                "rollback preparation requires no completed rollback history; "
                f"found {completed_rollbacks} rollback_completed event(s)"
            )

        latest_checkpoint_id = organism["latest_stable_checkpoint_id"]
        if latest_checkpoint_id is None:
            raise RollbackPreparationRejectedError(
                "rollback preparation requires a latest stable checkpoint"
            )
        latest = connection.execute(
            """SELECT checkpoint_id, lineage_generation, event_sequence, protected
               FROM checkpoint_registry WHERE checkpoint_id = ?""",
            (latest_checkpoint_id,),
        ).fetchone()
        if latest is None or (
            int(latest["lineage_generation"]) != int(organism["lineage_generation"])
            or int(latest["event_sequence"])
            != int(organism["latest_stable_event_sequence"])
            or int(latest["protected"]) != 1
        ):
            raise RollbackPreparationRejectedError(
                "latest stable checkpoint does not match protected organism state"
            )

        selected, selected_manifest = _validate_selected_checkpoint(
            connection, paths, organism, source_event_sequence
        )
        active_event_sequence = int(
            connection.execute(
                "SELECT COALESCE(MAX(event_sequence), 0) FROM event"
            ).fetchone()[0]
        )
        if active_event_sequence < int(organism["latest_stable_event_sequence"]):
            raise RollbackPreparationRejectedError(
                "active event history ends before the latest stable boundary"
            )

        archives_dir = paths.rollback_archives
        archives_dir.mkdir(mode=0o700, exist_ok=True)
        if not archives_dir.is_dir() or archives_dir.is_symlink():
            raise RollbackArchiveError("rollback archive root is missing or unsafe")
        if any(entry.is_symlink() for entry in archives_dir.iterdir()):
            raise RollbackArchiveError("rollback archive root contains an unsafe symlink")

        predicted_size = (
            paths.database.stat().st_size
            + _tree_size(paths.checkpoints)
            + _tree_size(archives_dir)
            + paths.database.stat().st_size
        )
        if predicted_size > RUNTIME_WORKING_SET_MAX_BYTES:
            raise RollbackArchiveError(
                "pre-rollback archive would exceed the protected runtime working-set limit"
            )

        temp_dir = Path(
            tempfile.mkdtemp(prefix=".tmp-pre-rollback-", dir=archives_dir)
        )
        destination_path = temp_dir / "organism.sqlite3"
        manifest_path = temp_dir / "manifest.json"
        snapshot_source = connect_database(paths.database, read_only=True)
        destination = sqlite3.connect(destination_path, isolation_level=None)
        try:
            snapshot_source.backup(destination, pages=64, sleep=0.0)
        finally:
            destination.close()
            snapshot_source.close()

        size = destination_path.stat().st_size
        if size > CHECKPOINT_ARTIFACT_MAX_BYTES:
            raise RollbackArchiveError(
                f"pre-rollback archive database exceeds {CHECKPOINT_ARTIFACT_MAX_BYTES} bytes"
            )
        database_sha = _sha256_file(destination_path)
        archive_id = (
            f"pre-rb-g{int(organism['lineage_generation']):06d}-"
            f"e{active_event_sequence:012d}-to-e{source_event_sequence:012d}-"
            f"{database_sha[:8]}"
        )
        final_dir = archives_dir / archive_id
        if final_dir.exists():
            existing = _validate_archive_directory(final_dir)
            if (
                existing.get("database_sha256") != database_sha
                or existing.get("selected_checkpoint_id") != selected["checkpoint_id"]
                or existing.get("active_event_sequence") != active_event_sequence
            ):
                raise RollbackArchiveError(
                    "deterministic rollback archive path already contains different content"
                )
            shutil.rmtree(temp_dir)
            temp_dir = None
            return RollbackPreparationResult(
                organism_id=str(existing["organism_id"]),
                active_lineage_generation=int(existing["active_lineage_generation"]),
                active_lifecycle_number=int(existing["active_lifecycle_number"]),
                active_status=str(existing["active_status"]),
                active_event_sequence=int(existing["active_event_sequence"]),
                latest_stable_checkpoint_id=str(existing["latest_stable_checkpoint_id"]),
                latest_stable_event_sequence=int(existing["latest_stable_event_sequence"]),
                selected_checkpoint_id=str(existing["selected_checkpoint_id"]),
                selected_checkpoint_event_sequence=int(
                    existing["selected_checkpoint_event_sequence"]
                ),
                archive_id=str(existing["archive_id"]),
                archive_dir=final_dir,
                database_size_bytes=int(existing["database_size_bytes"]),
                database_sha256=str(existing["database_sha256"]),
                manifest_sha256=_sha256_file(final_dir / "manifest.json"),
            )

        manifest: dict[str, Any] = {
            "rollback_archive_format_version": ROLLBACK_ARCHIVE_FORMAT_VERSION,
            "archive_id": archive_id,
            "organism_id": str(organism["organism_id"]),
            "active_lineage_generation": int(organism["lineage_generation"]),
            "active_lifecycle_number": int(organism["lifecycle_number"]),
            "active_status": str(organism["status"]),
            "active_event_sequence": active_event_sequence,
            "latest_stable_checkpoint_id": str(latest_checkpoint_id),
            "latest_stable_event_sequence": int(
                organism["latest_stable_event_sequence"]
            ),
            "selected_checkpoint_id": str(selected["checkpoint_id"]),
            "selected_checkpoint_lineage_generation": int(
                selected["lineage_generation"]
            ),
            "selected_checkpoint_event_sequence": source_event_sequence,
            "selected_checkpoint_manifest_sha256": str(
                selected["manifest_sha256"]
            ),
            "selected_checkpoint_database_sha256": str(
                selected["database_sha256"]
            ),
            "selected_checkpoint_database_size_bytes": int(
                selected["database_size_bytes"]
            ),
            "selected_checkpoint_provenance": str(selected_manifest["provenance"]),
            "contract_version": str(organism["contract_version"]),
            "schema_version": int(organism["schema_version"]),
            "environment_version": str(organism["environment_version"]),
            "budget_config_version": str(organism["budget_config_version"]),
            "database_filename": "organism.sqlite3",
            "database_size_bytes": size,
            "database_sha256": database_sha,
            "snapshot_method": "python-sqlite3-connection-backup",
            "implementation_version": "0.1.0",
            "status": "published",
            "provenance": "pre_rollback",
        }
        manifest_bytes = _canonical_json_bytes(manifest)
        manifest_path.write_bytes(manifest_bytes)
        manifest_sha = hashlib.sha256(manifest_bytes).hexdigest()
        _validate_archive_directory(temp_dir, expected_manifest=manifest)
        _fsync_file(destination_path)
        _fsync_file(manifest_path)
        _fsync_dir(temp_dir)

        if protected_test_fail_after_snapshot:
            raise _InjectedRollbackArchiveFailure(
                "injected pre-rollback archive failure before publication"
            )

        os.replace(temp_dir, final_dir)
        temp_dir = None
        _fsync_dir(archives_dir)
        if (
            paths.database.stat().st_size
            + _tree_size(paths.checkpoints)
            + _tree_size(archives_dir)
            > RUNTIME_WORKING_SET_MAX_BYTES
        ):
            raise RollbackArchiveError(
                "runtime working set exceeds the protected limit after archive publication"
            )
        _validate_archive_directory(final_dir, expected_manifest=manifest)
        return RollbackPreparationResult(
            organism_id=str(organism["organism_id"]),
            active_lineage_generation=int(organism["lineage_generation"]),
            active_lifecycle_number=int(organism["lifecycle_number"]),
            active_status=str(organism["status"]),
            active_event_sequence=active_event_sequence,
            latest_stable_checkpoint_id=str(latest_checkpoint_id),
            latest_stable_event_sequence=int(organism["latest_stable_event_sequence"]),
            selected_checkpoint_id=str(selected["checkpoint_id"]),
            selected_checkpoint_event_sequence=source_event_sequence,
            archive_id=archive_id,
            archive_dir=final_dir,
            database_size_bytes=size,
            database_sha256=database_sha,
            manifest_sha256=manifest_sha,
        )
    except (CheckpointError, SchemaValidationError) as exc:
        raise RollbackPreparationRejectedError(str(exc)) from exc
    except _InjectedRollbackArchiveFailure as exc:
        raise RollbackArchiveError(str(exc)) from exc
    finally:
        if temp_dir is not None and temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        if connection.in_transaction:
            connection.rollback()
        connection.close()
