"""Deterministic non-canonical JSONL export from one stable event boundary."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from .checkpoints import validate_checkpoint_directory
from .constants import RUNTIME_WORKING_SET_MAX_BYTES
from .errors import CheckpointError, OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state


EVENT_EXPORT_FORMAT = "sudachi-event-jsonl"
EVENT_EXPORT_FORMAT_VERSION = 1


class EventExportRejectedError(SudachiError):
    """The requested source boundary is not eligible for export."""


class EventExportWriteError(SudachiError):
    """A validated export could not be published atomically."""


class _InjectedEventExportWriteFailure(Exception):
    """Protected test-only partial temporary-file write failure."""


@dataclass(frozen=True, slots=True)
class EventExportResult:
    organism_id: str
    lineage_generation: int
    source_checkpoint_id: str
    first_event_sequence: int
    last_event_sequence: int
    event_count: int
    export_format: str
    export_format_version: int
    export_path: Path
    export_size_bytes: int
    export_sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "lineage_generation": self.lineage_generation,
            "source_checkpoint_id": self.source_checkpoint_id,
            "first_event_sequence": self.first_event_sequence,
            "last_event_sequence": self.last_event_sequence,
            "event_count": self.event_count,
            "export_format": self.export_format,
            "export_format_version": self.export_format_version,
            "export_path": str(self.export_path),
            "export_size_bytes": self.export_size_bytes,
            "export_sha256": self.export_sha256,
        }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_line(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def _fsync_directory(path: Path) -> None:
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


def _read_export_bytes(
    paths: OrganismPaths,
    event_sequence: int,
) -> tuple[bytes, dict[str, object]]:
    if event_sequence <= 0:
        raise EventExportRejectedError("event export boundary must be a positive integer")
    if not paths.database.is_file() or paths.database.is_symlink():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database, read_only=True)
    try:
        connection.execute("BEGIN")
        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            """SELECT organism_id, contract_version, schema_version,
                      environment_version, budget_config_version,
                      lineage_generation, status, checkpoint_pending
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise EventExportRejectedError("canonical organism state is missing")
        if organism["status"] not in {"sleeping", "maintenance_required"}:
            raise EventExportRejectedError(
                "event export requires stable sleeping or maintenance state: "
                f"status={organism['status']}"
            )
        if int(organism["checkpoint_pending"]) != 0:
            raise EventExportRejectedError(
                "event export requires a stable boundary with no pending checkpoint"
            )

        checkpoint_rows = connection.execute(
            """SELECT checkpoint_id, lineage_generation, event_sequence,
                      manifest_sha256, database_sha256, database_size_bytes, protected
               FROM checkpoint_registry WHERE event_sequence = ?
               ORDER BY checkpoint_id""",
            (event_sequence,),
        ).fetchall()
        if len(checkpoint_rows) != 1:
            raise EventExportRejectedError(
                "event export requires exactly one registered stable checkpoint at "
                f"boundary {event_sequence}; found {len(checkpoint_rows)}"
            )
        checkpoint = checkpoint_rows[0]
        if int(checkpoint["protected"]) != 1:
            raise EventExportRejectedError("source checkpoint is not protected")
        lineage_generation = int(checkpoint["lineage_generation"])
        if lineage_generation != int(organism["lineage_generation"]):
            raise EventExportRejectedError(
                "source checkpoint lineage does not match the active lineage"
            )

        checkpoint_dir = paths.checkpoints / str(checkpoint["checkpoint_id"])
        manifest = validate_checkpoint_directory(checkpoint_dir)
        if (
            manifest.get("organism_id") != organism["organism_id"]
            or int(manifest.get("lineage_generation", -1)) != lineage_generation
            or int(manifest.get("event_sequence", -1)) != event_sequence
            or manifest.get("contract_version") != organism["contract_version"]
            or int(manifest.get("schema_version", -1)) != int(organism["schema_version"])
            or manifest.get("environment_version") != organism["environment_version"]
            or manifest.get("budget_config_version")
            != organism["budget_config_version"]
            or manifest.get("database_sha256") != checkpoint["database_sha256"]
            or int(manifest.get("database_size_bytes", -1))
            != int(checkpoint["database_size_bytes"])
            or _sha256_file(checkpoint_dir / "manifest.json")
            != checkpoint["manifest_sha256"]
        ):
            raise EventExportRejectedError(
                "source checkpoint artifact does not match the canonical registry"
            )

        event_rows = connection.execute(
            """SELECT event_sequence, organism_id, lineage_generation,
                      lifecycle_number, wall_time_utc_us, event_type, source,
                      payload_json, schema_version, environment_version,
                      budget_config_version
               FROM event WHERE event_sequence <= ? ORDER BY event_sequence""",
            (event_sequence,),
        ).fetchall()
        sequences = [int(row["event_sequence"]) for row in event_rows]
        if not sequences or sequences != list(range(1, event_sequence + 1)):
            raise EventExportRejectedError(
                "canonical event history is not complete through the declared boundary"
            )
        if int(event_rows[-1]["lineage_generation"]) != lineage_generation:
            raise EventExportRejectedError(
                "declared boundary event does not belong to the checkpoint lineage"
            )

        event_records: list[dict[str, Any]] = []
        for row in event_rows:
            if row["organism_id"] != organism["organism_id"]:
                raise EventExportRejectedError(
                    "canonical event history contains a foreign organism identifier"
                )
            try:
                payload = json.loads(row["payload_json"])
            except json.JSONDecodeError as exc:
                raise EventExportRejectedError(
                    f"event {row['event_sequence']} payload is not valid JSON"
                ) from exc
            if not isinstance(payload, dict):
                raise EventExportRejectedError(
                    f"event {row['event_sequence']} payload is not a JSON object"
                )
            event_records.append(
                {
                    "record_type": "event",
                    "event_sequence": int(row["event_sequence"]),
                    "organism_id": str(row["organism_id"]),
                    "lineage_generation": int(row["lineage_generation"]),
                    "lifecycle_number": int(row["lifecycle_number"]),
                    "wall_time_utc_us": int(row["wall_time_utc_us"]),
                    "event_type": str(row["event_type"]),
                    "source": str(row["source"]),
                    "payload": payload,
                    "schema_version": int(row["schema_version"]),
                    "environment_version": str(row["environment_version"]),
                    "budget_config_version": str(row["budget_config_version"]),
                }
            )

        metadata: dict[str, object] = {
            "organism_id": str(organism["organism_id"]),
            "lineage_generation": lineage_generation,
            "source_checkpoint_id": str(checkpoint["checkpoint_id"]),
            "first_event_sequence": sequences[0],
            "last_event_sequence": sequences[-1],
            "event_count": len(sequences),
            "export_format": EVENT_EXPORT_FORMAT,
            "export_format_version": EVENT_EXPORT_FORMAT_VERSION,
        }
        manifest_record = {
            "record_type": "manifest",
            **metadata,
            "contract_version": str(organism["contract_version"]),
            "schema_version": int(organism["schema_version"]),
            "environment_version": str(organism["environment_version"]),
            "budget_config_version": str(organism["budget_config_version"]),
        }
        export_bytes = _canonical_json_line(manifest_record) + b"".join(
            _canonical_json_line(record) for record in event_records
        )
        if len(export_bytes) > RUNTIME_WORKING_SET_MAX_BYTES:
            raise EventExportRejectedError(
                "event export exceeds the protected runtime working-set limit"
            )
        return export_bytes, metadata
    except (CheckpointError, SchemaValidationError) as exc:
        raise EventExportRejectedError(str(exc)) from exc
    finally:
        if connection.in_transaction:
            connection.rollback()
        connection.close()


def _publish_export(
    exports_dir: Path,
    final_path: Path,
    export_bytes: bytes,
    *,
    protected_test_fail_after_bytes: int | None,
) -> None:
    if not exports_dir.is_dir() or exports_dir.is_symlink():
        raise EventExportWriteError("organism export directory is missing or unsafe")
    if final_path.exists() and (final_path.is_symlink() or not final_path.is_file()):
        raise EventExportWriteError("event export destination is unsafe")
    if protected_test_fail_after_bytes is not None and not (
        0 <= protected_test_fail_after_bytes < len(export_bytes)
    ):
        raise EventExportWriteError("protected test failure byte count is out of range")

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{final_path.name}.",
        suffix=".tmp",
        dir=exports_dir,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            if protected_test_fail_after_bytes is None:
                handle.write(export_bytes)
            else:
                handle.write(export_bytes[:protected_test_fail_after_bytes])
                handle.flush()
                os.fsync(handle.fileno())
                raise _InjectedEventExportWriteFailure(
                    "injected event export failure after partial temporary write"
                )
            handle.flush()
            os.fsync(handle.fileno())
        if temporary_path.stat().st_size != len(export_bytes):
            raise EventExportWriteError("temporary event export size changed before publication")
        if temporary_path.read_bytes() != export_bytes:
            raise EventExportWriteError("temporary event export bytes changed before publication")
        os.replace(temporary_path, final_path)
        _fsync_directory(exports_dir)
    except EventExportWriteError:
        raise
    except (OSError, _InjectedEventExportWriteFailure) as exc:
        raise EventExportWriteError(str(exc)) from exc
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def export_stable_events(
    runtime_root: Path | str,
    organism_id: str,
    event_sequence: int,
    *,
    protected_test_fail_after_bytes: int | None = None,
) -> EventExportResult:
    """Export canonical events through one declared registered stable boundary."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    export_bytes, metadata = _read_export_bytes(paths, event_sequence)
    filename = (
        f"events-g{int(metadata['lineage_generation']):06d}-"
        f"e{event_sequence:012d}.jsonl"
    )
    export_path = paths.exports / filename
    _publish_export(
        paths.exports,
        export_path,
        export_bytes,
        protected_test_fail_after_bytes=protected_test_fail_after_bytes,
    )
    return EventExportResult(
        organism_id=str(metadata["organism_id"]),
        lineage_generation=int(metadata["lineage_generation"]),
        source_checkpoint_id=str(metadata["source_checkpoint_id"]),
        first_event_sequence=int(metadata["first_event_sequence"]),
        last_event_sequence=int(metadata["last_event_sequence"]),
        event_count=int(metadata["event_count"]),
        export_format=str(metadata["export_format"]),
        export_format_version=int(metadata["export_format_version"]),
        export_path=export_path,
        export_size_bytes=len(export_bytes),
        export_sha256=hashlib.sha256(export_bytes).hexdigest(),
    )
