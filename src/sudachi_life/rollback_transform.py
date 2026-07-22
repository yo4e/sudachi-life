"""Verified lineage transformation of one source-restored rollback candidate."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
from typing import Any

from .clock import Clock, RealClock
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
)
from .rollback_candidate import (
    RestoreCandidateError,
    RestoreCandidateRejectedError,
    _validate_candidate_directory,
    _validate_durable_intent,
)
from .rollback_intent import RollbackBeginRejectedError, _canonical_sqlite_snapshot
from .storage import connect_database, validate_canonical_state

TRANSFORMED_CANDIDATE_FORMAT_VERSION = 1
_SOURCE_CANDIDATE_ID_RE = re.compile(
    r"^rc-g[0-9]{6}-rb-e[0-9]{12}-from-e[0-9]{12}-[0-9a-f]{8}$"
)


class CandidateTransformBusyError(SudachiError):
    """Candidate transformation could not acquire administrative ownership."""


class CandidateTransformRejectedError(SudachiError):
    """The active rollback intent or source candidate is not eligible."""


class CandidateTransformError(SudachiError):
    """A transformed rollback candidate could not be published or validated."""


class _InjectedCandidateTransformFailure(Exception):
    """Protected test-only failure after transformed candidate validation."""


@dataclass(frozen=True, slots=True)
class CandidateTransformResult:
    organism_id: str
    source_candidate_id: str
    transformed_candidate_id: str
    transformed_candidate_dir: Path
    archive_id: str
    selected_checkpoint_id: str
    abandoned_lineage_generation: int
    new_lineage_generation: int
    source_lifecycle_number: int
    source_event_sequence: int
    restoration_event_sequence: int
    administrative_reason: str
    database_size_bytes: int
    database_sha256: str
    manifest_sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "source_candidate_id": self.source_candidate_id,
            "transformed_candidate_id": self.transformed_candidate_id,
            "transformed_candidate_dir": str(self.transformed_candidate_dir),
            "archive_id": self.archive_id,
            "selected_checkpoint_id": self.selected_checkpoint_id,
            "abandoned_lineage_generation": self.abandoned_lineage_generation,
            "new_lineage_generation": self.new_lineage_generation,
            "source_lifecycle_number": self.source_lifecycle_number,
            "source_event_sequence": self.source_event_sequence,
            "restoration_event_sequence": self.restoration_event_sequence,
            "administrative_reason": self.administrative_reason,
            "database_size_bytes": self.database_size_bytes,
            "database_sha256": self.database_sha256,
            "manifest_sha256": self.manifest_sha256,
        }


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def _validate_reason(reason: str) -> str:
    if not isinstance(reason, str):
        raise CandidateTransformRejectedError("administrative reason must be text")
    if not reason or reason != reason.strip():
        raise CandidateTransformRejectedError(
            "administrative reason must be non-empty with no surrounding whitespace"
        )
    if len(reason) > 256:
        raise CandidateTransformRejectedError(
            "administrative reason exceeds the protected 256-character limit"
        )
    if any(ord(character) < 32 or ord(character) == 127 for character in reason):
        raise CandidateTransformRejectedError(
            "administrative reason may not contain control characters"
        )
    return reason


def _expected_source_candidate_context(
    *,
    source_candidate_id: str,
    organism: sqlite3.Row,
    rollback_started: sqlite3.Row,
    payload: dict[str, Any],
    selected: sqlite3.Row,
    selected_manifest: dict[str, Any],
) -> dict[str, object]:
    return {
        "candidate_id": source_candidate_id,
        "organism_id": str(organism["organism_id"]),
        "active_lineage_generation": int(organism["lineage_generation"]),
        "rollback_started_event_sequence": int(rollback_started["event_sequence"]),
        "archive_id": str(payload["archive_id"]),
        "archive_manifest_sha256": str(payload["archive_manifest_sha256"]),
        "archive_database_sha256": str(payload["archive_database_sha256"]),
        "selected_checkpoint_id": str(selected["checkpoint_id"]),
        "source_lineage_generation": int(selected["lineage_generation"]),
        "source_lifecycle_number": int(selected_manifest["lifecycle_number"]),
        "source_event_sequence": int(selected["event_sequence"]),
        "source_checkpoint_manifest_sha256": str(selected["manifest_sha256"]),
        "source_checkpoint_database_sha256": str(selected["database_sha256"]),
        "source_checkpoint_database_size_bytes": int(selected["database_size_bytes"]),
        "source_checkpoint_provenance": str(selected_manifest["provenance"]),
        "contract_version": str(organism["contract_version"]),
        "schema_version": int(organism["schema_version"]),
        "environment_version": str(organism["environment_version"]),
        "budget_config_version": str(organism["budget_config_version"]),
        "candidate_state": "source_restored_untransformed",
        "status": "published",
        "provenance": "restore_candidate",
    }


def _validate_source_candidate(
    paths: OrganismPaths,
    source_candidate_id: str,
    *,
    organism: sqlite3.Row,
    rollback_started: sqlite3.Row,
    payload: dict[str, Any],
    selected: sqlite3.Row,
    selected_manifest: dict[str, Any],
) -> tuple[Path, dict[str, Any], str, str]:
    if not _SOURCE_CANDIDATE_ID_RE.fullmatch(source_candidate_id):
        raise CandidateTransformRejectedError(
            "source restore-candidate identifier does not match the protected format"
        )
    root = paths.restore_candidates
    if not root.is_dir() or root.is_symlink():
        raise CandidateTransformRejectedError(
            "restore candidate root is missing or unsafe"
        )
    if any(entry.is_symlink() for entry in root.iterdir()):
        raise CandidateTransformRejectedError(
            "restore candidate root contains an unsafe symlink"
        )
    source_dir = root / source_candidate_id
    source_manifest = _validate_candidate_directory(
        source_dir,
        source_checkpoint_dir=paths.checkpoints / str(selected["checkpoint_id"]),
    )
    expected = _expected_source_candidate_context(
        source_candidate_id=source_candidate_id,
        organism=organism,
        rollback_started=rollback_started,
        payload=payload,
        selected=selected,
        selected_manifest=selected_manifest,
    )
    for key, value in expected.items():
        if source_manifest.get(key) != value:
            raise CandidateTransformRejectedError(
                f"source restore candidate does not match durable intent: {key}"
            )
    source_manifest_sha256 = _sha256_file(source_dir / "manifest.json")
    source_database_sha256 = _sha256_file(source_dir / "organism.sqlite3")
    if source_database_sha256 != source_manifest["database_sha256"]:
        raise CandidateTransformRejectedError(
            "source restore candidate database digest changed after validation"
        )
    return source_dir, source_manifest, source_manifest_sha256, source_database_sha256


def _restoration_payload(manifest: dict[str, Any]) -> dict[str, object]:
    return {
        "administrative_reason": manifest["administrative_reason"],
        "archive_database_sha256": manifest["archive_database_sha256"],
        "archive_id": manifest["archive_id"],
        "archive_manifest_sha256": manifest["archive_manifest_sha256"],
        "abandoned_event_sequence": manifest["abandoned_event_sequence"],
        "abandoned_lifecycle_number": manifest["abandoned_lifecycle_number"],
        "abandoned_lineage_generation": manifest["abandoned_lineage_generation"],
        "new_lineage_generation": manifest["new_lineage_generation"],
        "rollback_started_event_sequence": manifest["rollback_started_event_sequence"],
        "selected_checkpoint_database_sha256": manifest[
            "selected_checkpoint_database_sha256"
        ],
        "selected_checkpoint_event_sequence": manifest[
            "selected_checkpoint_event_sequence"
        ],
        "selected_checkpoint_id": manifest["selected_checkpoint_id"],
        "selected_checkpoint_lineage_generation": manifest[
            "selected_checkpoint_lineage_generation"
        ],
        "selected_checkpoint_manifest_sha256": manifest[
            "selected_checkpoint_manifest_sha256"
        ],
        "source_restore_candidate_database_sha256": manifest[
            "source_restore_candidate_database_sha256"
        ],
        "source_restore_candidate_id": manifest["source_restore_candidate_id"],
        "source_restore_candidate_manifest_sha256": manifest[
            "source_restore_candidate_manifest_sha256"
        ],
        "status_after": "rollback_in_progress",
    }


def _validate_transformed_candidate_directory(
    candidate_dir: Path,
    *,
    source_candidate_dir: Path,
    selected_registry: sqlite3.Row,
    expected_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not candidate_dir.is_dir() or candidate_dir.is_symlink():
        raise CandidateTransformError(
            "transformed candidate directory is missing or unsafe"
        )
    if {entry.name for entry in candidate_dir.iterdir()} != {
        "organism.sqlite3",
        "manifest.json",
    }:
        raise CandidateTransformError(
            "transformed candidate contains unexpected entries"
        )
    database_path = candidate_dir / "organism.sqlite3"
    manifest_path = candidate_dir / "manifest.json"
    if not database_path.is_file() or database_path.is_symlink():
        raise CandidateTransformError(
            "transformed candidate database is missing or unsafe"
        )
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise CandidateTransformError(
            "transformed candidate manifest is missing or unsafe"
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CandidateTransformError(
            "transformed candidate manifest is not valid JSON"
        ) from exc
    if expected_manifest is not None and manifest != expected_manifest:
        raise CandidateTransformError(
            "transformed candidate manifest changed before publication"
        )
    if (
        manifest.get("transformed_candidate_format_version")
        != TRANSFORMED_CANDIDATE_FORMAT_VERSION
    ):
        raise CandidateTransformError("unsupported transformed candidate format")
    if manifest.get("status") != "published":
        raise CandidateTransformError(
            "transformed candidate publication status is invalid"
        )
    if manifest.get("provenance") != "rollback_transformed_candidate":
        raise CandidateTransformError(
            "transformed candidate provenance is invalid"
        )
    if manifest.get("candidate_state") != "lineage_transformed_replacement_ready":
        raise CandidateTransformError("transformed candidate state is invalid")
    if manifest.get("database_filename") != "organism.sqlite3":
        raise CandidateTransformError(
            "transformed candidate database filename mismatch"
        )
    if manifest.get("snapshot_method") != "python-sqlite3-connection-backup":
        raise CandidateTransformError(
            "transformed candidate snapshot method mismatch"
        )
    if manifest.get("transformation_method") != "bounded-sqlite-administrative-transaction":
        raise CandidateTransformError(
            "transformed candidate transformation method mismatch"
        )
    if (
        expected_manifest is None
        and candidate_dir.name != manifest.get("transformed_candidate_id")
    ):
        raise CandidateTransformError(
            "transformed candidate directory name does not match manifest"
        )
    size = database_path.stat().st_size
    if size != manifest.get("database_size_bytes"):
        raise CandidateTransformError(
            "transformed candidate database size mismatch"
        )
    if _sha256_file(database_path) != manifest.get("database_sha256"):
        raise CandidateTransformError(
            "transformed candidate database digest mismatch"
        )

    transformed = connect_database(database_path, read_only=True)
    source = connect_database(source_candidate_dir / "organism.sqlite3", read_only=True)
    try:
        integrity = transformed.execute("PRAGMA integrity_check").fetchall()
        if len(integrity) != 1 or integrity[0][0] != "ok":
            raise CandidateTransformError(
                f"transformed candidate integrity check failed: {integrity!r}"
            )
        foreign_keys = transformed.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_keys:
            raise CandidateTransformError(
                f"transformed candidate foreign-key check failed: {foreign_keys!r}"
            )
        validate_canonical_state(transformed, expect_checkpoint_pending=False)
        validate_canonical_state(source, expect_checkpoint_pending=True)

        transformed_snapshot = _canonical_sqlite_snapshot(transformed)
        source_snapshot = _canonical_sqlite_snapshot(source)
        if transformed_snapshot["user_version"] != source_snapshot["user_version"]:
            raise CandidateTransformError(
                "transformed candidate user_version changed from source"
            )
        if transformed_snapshot["schema"] != source_snapshot["schema"]:
            raise CandidateTransformError(
                "transformed candidate schema changed from source"
            )
        transformed_tables = transformed_snapshot["tables"]
        source_tables = source_snapshot["tables"]
        if set(transformed_tables) != set(source_tables):
            raise CandidateTransformError(
                "transformed candidate canonical table set changed from source"
            )
        for table_name in sorted(transformed_tables):
            if table_name in {"organism", "event", "checkpoint_registry"}:
                continue
            if transformed_tables[table_name] != source_tables[table_name]:
                raise CandidateTransformError(
                    f"transformed candidate table changed from source: {table_name}"
                )

        transformed_organism = transformed.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        source_organism = source.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        if transformed_organism is None or source_organism is None:
            raise CandidateTransformError(
                "transformed or source candidate organism state is missing"
            )
        transformed_organism_dict = dict(transformed_organism)
        source_organism_dict = dict(source_organism)
        changed_columns = {
            "lineage_generation",
            "status",
            "checkpoint_pending",
            "pending_checkpoint_generation",
            "pending_checkpoint_event_sequence",
            "latest_stable_checkpoint_id",
            "latest_stable_event_sequence",
        }
        for column, source_value in source_organism_dict.items():
            if column not in changed_columns and transformed_organism_dict[column] != source_value:
                raise CandidateTransformError(
                    f"transformed candidate organism column changed unexpectedly: {column}"
                )

        expected_organism = {
            "organism_id": manifest["organism_id"],
            "lineage_generation": manifest["new_lineage_generation"],
            "lifecycle_number": manifest["source_lifecycle_number"],
            "status": "rollback_in_progress",
            "checkpoint_pending": 0,
            "pending_checkpoint_generation": None,
            "pending_checkpoint_event_sequence": None,
            "latest_stable_checkpoint_id": manifest["selected_checkpoint_id"],
            "latest_stable_event_sequence": manifest["source_event_sequence"],
            "contract_version": manifest["contract_version"],
            "schema_version": manifest["schema_version"],
            "environment_version": manifest["environment_version"],
            "budget_config_version": manifest["budget_config_version"],
        }
        for key, value in expected_organism.items():
            if transformed_organism_dict[key] != value:
                raise CandidateTransformError(
                    f"transformed candidate organism {key} mismatch"
                )

        source_events = source.execute(
            "SELECT * FROM event ORDER BY event_sequence"
        ).fetchall()
        transformed_events = transformed.execute(
            "SELECT * FROM event ORDER BY event_sequence"
        ).fetchall()
        if [tuple(row) for row in transformed_events[:-1]] != [
            tuple(row) for row in source_events
        ]:
            raise CandidateTransformError(
                "transformed candidate did not preserve source event history"
            )
        if len(transformed_events) != len(source_events) + 1:
            raise CandidateTransformError(
                "transformed candidate has an unexpected event count"
            )
        restoration_event = transformed_events[-1]
        expected_event_sequence = int(manifest["source_event_sequence"]) + 1
        if int(restoration_event["event_sequence"]) != expected_event_sequence:
            raise CandidateTransformError(
                "candidate restoration event is not the exact next sequence"
            )
        event_expected = {
            "organism_id": manifest["organism_id"],
            "lineage_generation": manifest["new_lineage_generation"],
            "lifecycle_number": manifest["source_lifecycle_number"],
            "wall_time_utc_us": manifest["restoration_wall_time_utc_us"],
            "event_type": "rollback_lineage_prepared",
            "source": "administration:rollback-candidate",
            "schema_version": manifest["schema_version"],
            "environment_version": manifest["environment_version"],
            "budget_config_version": manifest["budget_config_version"],
        }
        for key, value in event_expected.items():
            if restoration_event[key] != value:
                raise CandidateTransformError(
                    f"candidate restoration event {key} mismatch"
                )
        try:
            event_payload = json.loads(restoration_event["payload_json"])
        except json.JSONDecodeError as exc:
            raise CandidateTransformError(
                "candidate restoration event payload is invalid JSON"
            ) from exc
        if event_payload != _restoration_payload(manifest):
            raise CandidateTransformError(
                "candidate restoration event payload does not match manifest"
            )

        source_registry = [
            tuple(row)
            for row in source.execute(
                "SELECT * FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"
            ).fetchall()
        ]
        transformed_registry = [
            tuple(row)
            for row in transformed.execute(
                "SELECT * FROM checkpoint_registry ORDER BY event_sequence, checkpoint_id"
            ).fetchall()
        ]
        selected_tuple = tuple(selected_registry)
        expected_registry = sorted(
            [*source_registry, selected_tuple],
            key=lambda row: (int(row[2]), str(row[0])),
        )
        if transformed_registry != expected_registry:
            raise CandidateTransformError(
                "transformed candidate checkpoint registry is invalid"
            )

        transformed_sequence = dict(transformed_snapshot["sqlite_sequence"])
        source_sequence = dict(source_snapshot["sqlite_sequence"])
        if set(transformed_sequence) != set(source_sequence):
            raise CandidateTransformError(
                "transformed candidate AUTOINCREMENT table set changed"
            )
        for name, source_value in source_sequence.items():
            expected_value = int(source_value) + 1 if name == "event" else int(source_value)
            if int(transformed_sequence[name]) != expected_value:
                raise CandidateTransformError(
                    f"transformed candidate AUTOINCREMENT state mismatch: {name}"
                )

        manifest_expected = {
            "organism_id": transformed_organism["organism_id"],
            "new_lineage_generation": int(transformed_organism["lineage_generation"]),
            "source_lifecycle_number": int(transformed_organism["lifecycle_number"]),
            "source_event_sequence": int(manifest["source_event_sequence"]),
            "restoration_event_sequence": int(restoration_event["event_sequence"]),
            "contract_version": transformed_organism["contract_version"],
            "schema_version": int(transformed_organism["schema_version"]),
            "environment_version": transformed_organism["environment_version"],
            "budget_config_version": transformed_organism["budget_config_version"],
        }
        for key, value in manifest_expected.items():
            if manifest.get(key) != value:
                raise CandidateTransformError(
                    f"transformed candidate {key} does not match database contents"
                )
    except SchemaValidationError as exc:
        raise CandidateTransformError(str(exc)) from exc
    finally:
        source.close()
        transformed.close()
    return manifest


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
    """Transform one verified source-restored candidate into a new-lineage candidate."""

    reason = _validate_reason(administrative_reason)
    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file() or paths.database.is_symlink():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    active = connect_database(paths.database)
    temp_dir: Path | None = None
    final_dir: Path | None = None
    published_new = False
    completed = False
    try:
        try:
            active.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise CandidateTransformBusyError(
                    "candidate transformation is busy; this attempt was not queued"
                ) from exc
            raise

        validate_canonical_state(active, expect_checkpoint_pending=False)
        (
            organism,
            rollback_started,
            payload,
            _archive_dir,
            _archive_manifest,
            selected,
            selected_manifest,
        ) = _validate_durable_intent(active, paths)
        selected_registry = active.execute(
            "SELECT * FROM checkpoint_registry WHERE checkpoint_id = ?",
            (selected["checkpoint_id"],),
        ).fetchone()
        if selected_registry is None:
            raise CandidateTransformRejectedError(
                "selected checkpoint registry row disappeared after intent validation"
            )
        selected_registry_expected = {
            "checkpoint_id": selected["checkpoint_id"],
            "lineage_generation": selected["lineage_generation"],
            "event_sequence": selected["event_sequence"],
            "manifest_sha256": selected["manifest_sha256"],
            "database_sha256": selected["database_sha256"],
            "database_size_bytes": selected["database_size_bytes"],
            "protected": selected["protected"],
        }
        for key, value in selected_registry_expected.items():
            if selected_registry[key] != value:
                raise CandidateTransformRejectedError(
                    f"selected checkpoint registry row changed after validation: {key}"
                )

        (
            source_candidate_dir,
            source_manifest,
            source_manifest_sha256,
            source_database_sha256,
        ) = _validate_source_candidate(
            paths,
            source_candidate_id,
            organism=organism,
            rollback_started=rollback_started,
            payload=payload,
            selected=selected,
            selected_manifest=selected_manifest,
        )

        abandoned_generation = int(payload["pre_rollback_lineage_generation"])
        new_generation = abandoned_generation + 1
        rollback_started_event_sequence = int(rollback_started["event_sequence"])
        source_event_sequence = int(selected["event_sequence"])
        source_lifecycle_number = int(selected_manifest["lifecycle_number"])
        restoration_event_sequence = source_event_sequence + 1
        transformed_candidate_id = (
            f"rtc-g{new_generation:06d}-"
            f"rb-e{rollback_started_event_sequence:012d}-"
            f"from-e{source_event_sequence:012d}-"
            f"{source_manifest_sha256[:8]}"
        )
        candidates_dir = paths.restore_candidates
        final_dir = candidates_dir / transformed_candidate_id

        context_expected: dict[str, object] = {
            "transformed_candidate_id": transformed_candidate_id,
            "organism_id": str(organism["organism_id"]),
            "source_restore_candidate_id": source_candidate_id,
            "source_restore_candidate_manifest_sha256": source_manifest_sha256,
            "source_restore_candidate_database_sha256": source_database_sha256,
            "source_restore_candidate_database_size_bytes": int(
                source_manifest["database_size_bytes"]
            ),
            "archive_id": str(payload["archive_id"]),
            "archive_manifest_sha256": str(payload["archive_manifest_sha256"]),
            "archive_database_sha256": str(payload["archive_database_sha256"]),
            "rollback_started_event_sequence": rollback_started_event_sequence,
            "abandoned_lineage_generation": abandoned_generation,
            "abandoned_lifecycle_number": int(
                payload["pre_rollback_lifecycle_number"]
            ),
            "abandoned_event_sequence": int(payload["pre_rollback_event_sequence"]),
            "selected_checkpoint_id": str(selected["checkpoint_id"]),
            "selected_checkpoint_lineage_generation": int(
                selected["lineage_generation"]
            ),
            "selected_checkpoint_event_sequence": source_event_sequence,
            "selected_checkpoint_manifest_sha256": str(selected["manifest_sha256"]),
            "selected_checkpoint_database_sha256": str(selected["database_sha256"]),
            "selected_checkpoint_database_size_bytes": int(
                selected["database_size_bytes"]
            ),
            "selected_checkpoint_provenance": str(selected_manifest["provenance"]),
            "source_lineage_generation": int(selected["lineage_generation"]),
            "source_lifecycle_number": source_lifecycle_number,
            "source_event_sequence": source_event_sequence,
            "new_lineage_generation": new_generation,
            "restoration_event_sequence": restoration_event_sequence,
            "administrative_reason": reason,
            "contract_version": str(organism["contract_version"]),
            "schema_version": int(organism["schema_version"]),
            "environment_version": str(organism["environment_version"]),
            "budget_config_version": str(organism["budget_config_version"]),
            "database_filename": "organism.sqlite3",
            "snapshot_method": "python-sqlite3-connection-backup",
            "transformation_method": "bounded-sqlite-administrative-transaction",
            "implementation_version": "0.1.0",
            "candidate_state": "lineage_transformed_replacement_ready",
            "status": "published",
            "provenance": "rollback_transformed_candidate",
        }

        if final_dir.exists():
            existing = _validate_transformed_candidate_directory(
                final_dir,
                source_candidate_dir=source_candidate_dir,
                selected_registry=selected_registry,
            )
            for key, value in context_expected.items():
                if existing.get(key) != value:
                    raise CandidateTransformError(
                        f"existing transformed candidate does not match request: {key}"
                    )
            completed = True
            return CandidateTransformResult(
                organism_id=str(existing["organism_id"]),
                source_candidate_id=str(existing["source_restore_candidate_id"]),
                transformed_candidate_id=str(existing["transformed_candidate_id"]),
                transformed_candidate_dir=final_dir,
                archive_id=str(existing["archive_id"]),
                selected_checkpoint_id=str(existing["selected_checkpoint_id"]),
                abandoned_lineage_generation=int(
                    existing["abandoned_lineage_generation"]
                ),
                new_lineage_generation=int(existing["new_lineage_generation"]),
                source_lifecycle_number=int(existing["source_lifecycle_number"]),
                source_event_sequence=int(existing["source_event_sequence"]),
                restoration_event_sequence=int(existing["restoration_event_sequence"]),
                administrative_reason=str(existing["administrative_reason"]),
                database_size_bytes=int(existing["database_size_bytes"]),
                database_sha256=str(existing["database_sha256"]),
                manifest_sha256=_sha256_file(final_dir / "manifest.json"),
            )

        predicted_size = (
            paths.database.stat().st_size
            + _tree_size(paths.checkpoints)
            + _tree_size(paths.rollback_archives)
            + _tree_size(candidates_dir)
            + int(source_manifest["database_size_bytes"])
        )
        if predicted_size > RUNTIME_WORKING_SET_MAX_BYTES:
            raise CandidateTransformError(
                "transformed candidate would exceed the protected runtime working-set limit"
            )

        reading = (clock or RealClock()).read()
        temp_dir = Path(
            tempfile.mkdtemp(prefix=".tmp-transformed-candidate-", dir=candidates_dir)
        )
        destination_path = temp_dir / "organism.sqlite3"
        manifest_path = temp_dir / "manifest.json"
        source = connect_database(
            source_candidate_dir / "organism.sqlite3", read_only=True
        )
        destination = sqlite3.connect(destination_path, isolation_level=None)
        try:
            source.backup(destination, pages=64, sleep=0.0)
        finally:
            destination.close()
            source.close()

        working = connect_database(destination_path)
        try:
            working.execute("BEGIN IMMEDIATE")
            source_checkpoint_present = working.execute(
                "SELECT 1 FROM checkpoint_registry WHERE checkpoint_id = ?",
                (selected["checkpoint_id"],),
            ).fetchone()
            if source_checkpoint_present is not None:
                raise CandidateTransformRejectedError(
                    "source candidate already contains the selected checkpoint registry row"
                )
            updated = working.execute(
                """UPDATE organism
                   SET lineage_generation = ?,
                       status = 'rollback_in_progress',
                       checkpoint_pending = 0,
                       pending_checkpoint_generation = NULL,
                       pending_checkpoint_event_sequence = NULL,
                       latest_stable_checkpoint_id = ?,
                       latest_stable_event_sequence = ?
                   WHERE singleton_id = 1
                     AND organism_id = ?
                     AND lineage_generation = ?
                     AND lifecycle_number = ?
                     AND status = 'checkpoint_pending'
                     AND checkpoint_pending = 1
                     AND pending_checkpoint_generation = ?
                     AND pending_checkpoint_event_sequence = ?""",
                (
                    new_generation,
                    selected["checkpoint_id"],
                    source_event_sequence,
                    organism["organism_id"],
                    selected["lineage_generation"],
                    source_lifecycle_number,
                    selected["lineage_generation"],
                    source_event_sequence,
                ),
            )
            if updated.rowcount != 1:
                raise CandidateTransformRejectedError(
                    "source candidate changed before lineage transformation"
                )
            working.execute(
                """INSERT INTO checkpoint_registry (
                       checkpoint_id, lineage_generation, event_sequence,
                       manifest_sha256, database_sha256, database_size_bytes,
                       created_wall_time_utc_us, registered_wall_time_utc_us, protected
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                tuple(selected_registry),
            )
            manifest_stub: dict[str, Any] = {
                **context_expected,
                "restoration_wall_time_utc_us": reading.wall_time_utc_us,
            }
            cursor = working.execute(
                """INSERT INTO event (
                       organism_id, lineage_generation, lifecycle_number,
                       wall_time_utc_us, event_type, source, payload_json,
                       schema_version, environment_version, budget_config_version
                   ) VALUES (?, ?, ?, ?, 'rollback_lineage_prepared',
                             'administration:rollback-candidate', ?, ?, ?, ?)""",
                (
                    organism["organism_id"],
                    new_generation,
                    source_lifecycle_number,
                    reading.wall_time_utc_us,
                    json.dumps(
                        _restoration_payload(manifest_stub),
                        sort_keys=True,
                        separators=(",", ":"),
                    ),
                    organism["schema_version"],
                    organism["environment_version"],
                    organism["budget_config_version"],
                ),
            )
            if int(cursor.lastrowid) != restoration_event_sequence:
                raise CandidateTransformRejectedError(
                    "candidate restoration event did not append at the exact next sequence"
                )
            if protected_test_fail_after_event_insert:
                raise _InjectedCandidateTransformFailure(
                    "injected candidate transformation failure after event insert"
                )
            validate_canonical_state(working, expect_checkpoint_pending=False)
            working.commit()
        except Exception:
            if working.in_transaction:
                working.rollback()
            raise
        finally:
            working.close()

        size = destination_path.stat().st_size
        if size > CHECKPOINT_ARTIFACT_MAX_BYTES:
            raise CandidateTransformError(
                f"transformed candidate database exceeds {CHECKPOINT_ARTIFACT_MAX_BYTES} bytes"
            )
        database_sha256 = _sha256_file(destination_path)
        manifest: dict[str, Any] = {
            "transformed_candidate_format_version": TRANSFORMED_CANDIDATE_FORMAT_VERSION,
            **context_expected,
            "restoration_wall_time_utc_us": reading.wall_time_utc_us,
            "database_size_bytes": size,
            "database_sha256": database_sha256,
        }
        manifest_bytes = _canonical_json_bytes(manifest)
        manifest_path.write_bytes(manifest_bytes)
        manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
        _validate_transformed_candidate_directory(
            temp_dir,
            source_candidate_dir=source_candidate_dir,
            selected_registry=selected_registry,
            expected_manifest=manifest,
        )
        _fsync_file(destination_path)
        _fsync_file(manifest_path)
        _fsync_dir(temp_dir)

        if protected_test_fail_before_publish:
            raise _InjectedCandidateTransformFailure(
                "injected candidate transformation failure before publication"
            )

        os.replace(temp_dir, final_dir)
        temp_dir = None
        published_new = True
        _fsync_dir(candidates_dir)
        _validate_transformed_candidate_directory(
            final_dir,
            source_candidate_dir=source_candidate_dir,
            selected_registry=selected_registry,
            expected_manifest=manifest,
        )
        completed = True
        return CandidateTransformResult(
            organism_id=str(organism["organism_id"]),
            source_candidate_id=source_candidate_id,
            transformed_candidate_id=transformed_candidate_id,
            transformed_candidate_dir=final_dir,
            archive_id=str(payload["archive_id"]),
            selected_checkpoint_id=str(selected["checkpoint_id"]),
            abandoned_lineage_generation=abandoned_generation,
            new_lineage_generation=new_generation,
            source_lifecycle_number=source_lifecycle_number,
            source_event_sequence=source_event_sequence,
            restoration_event_sequence=restoration_event_sequence,
            administrative_reason=reason,
            database_size_bytes=size,
            database_sha256=database_sha256,
            manifest_sha256=manifest_sha256,
        )
    except _InjectedCandidateTransformFailure as exc:
        raise CandidateTransformError(str(exc)) from exc
    except (OSError, sqlite3.Error) as exc:
        raise CandidateTransformError(str(exc)) from exc
    except (
        CheckpointError,
        RollbackArchiveError,
        RollbackBeginRejectedError,
        RollbackPreparationRejectedError,
        RestoreCandidateError,
        RestoreCandidateRejectedError,
        SchemaValidationError,
    ) as exc:
        raise CandidateTransformRejectedError(str(exc)) from exc
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
        if active.in_transaction:
            active.rollback()
        active.close()
