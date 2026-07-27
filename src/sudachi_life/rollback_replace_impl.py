"""Protected active-database replacement with a verified rollback candidate."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from typing import Any

from .checkpoints import validate_checkpoint_directory
from .constants import RUNTIME_WORKING_SET_MAX_BYTES
from .errors import CheckpointError, OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .rollback import (
    RollbackArchiveError,
    RollbackPreparationRejectedError,
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
from .rollback_intent import RollbackBeginRejectedError, _canonical_sqlite_snapshot, _load_archive
from .rollback_transform import (
    CandidateTransformError,
    CandidateTransformRejectedError,
    _validate_source_candidate,
    _validate_transformed_candidate_directory,
)
from .storage import connect_database, validate_canonical_state

_TRANSFORMED_CANDIDATE_ID_RE = re.compile(
    r"^rtc-g[0-9]{6}-rb-e[0-9]{12}-from-e[0-9]{12}-[0-9a-f]{8}$"
)


class ActiveReplacementBusyError(SudachiError):
    """Active replacement could not acquire fail-fast administrative ownership."""


class ActiveReplacementRejectedError(SudachiError):
    """The active rollback state or transformed candidate is not replaceable."""


class ActiveReplacementError(SudachiError):
    """The active database could not be replaced before authority transfer."""


class ActiveReplacementIncompleteError(SudachiError):
    """Authority transferred, but post-replacement validation did not complete."""


@dataclass(frozen=True, slots=True)
class ActiveReplacementResult:
    organism_id: str
    transformed_candidate_id: str
    active_database: Path
    archive_id: str
    selected_checkpoint_id: str
    abandoned_lineage_generation: int
    new_lineage_generation: int
    source_lifecycle_number: int
    source_event_sequence: int
    restoration_event_sequence: int
    active_database_size_bytes: int
    active_database_sha256: str
    transformed_candidate_database_sha256: str
    transformed_candidate_manifest_sha256: str
    recovered_existing_replacement: bool
    status: str

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "transformed_candidate_id": self.transformed_candidate_id,
            "active_database": str(self.active_database),
            "archive_id": self.archive_id,
            "selected_checkpoint_id": self.selected_checkpoint_id,
            "abandoned_lineage_generation": self.abandoned_lineage_generation,
            "new_lineage_generation": self.new_lineage_generation,
            "source_lifecycle_number": self.source_lifecycle_number,
            "source_event_sequence": self.source_event_sequence,
            "restoration_event_sequence": self.restoration_event_sequence,
            "active_database_size_bytes": self.active_database_size_bytes,
            "active_database_sha256": self.active_database_sha256,
            "transformed_candidate_database_sha256": self.transformed_candidate_database_sha256,
            "transformed_candidate_manifest_sha256": self.transformed_candidate_manifest_sha256,
            "recovered_existing_replacement": self.recovered_existing_replacement,
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class _ReplacementContext:
    candidate_dir: Path
    manifest: dict[str, Any]
    manifest_sha256: str
    database_sha256: str
    source_candidate_dir: Path
    selected_registry: sqlite3.Row


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def _read_manifest(
    paths: OrganismPaths,
    transformed_candidate_id: str,
) -> tuple[Path, dict[str, Any]]:
    if not _TRANSFORMED_CANDIDATE_ID_RE.fullmatch(transformed_candidate_id):
        raise ActiveReplacementRejectedError(
            "transformed candidate identifier does not match the protected format"
        )
    root = paths.restore_candidates
    if not root.is_dir() or root.is_symlink():
        raise ActiveReplacementRejectedError("restore candidate root is missing or unsafe")
    if any(entry.is_symlink() for entry in root.iterdir()):
        raise ActiveReplacementRejectedError(
            "restore candidate root contains an unsafe symlink"
        )
    candidate_dir = root / transformed_candidate_id
    if not candidate_dir.is_dir() or candidate_dir.is_symlink():
        raise ActiveReplacementRejectedError(
            "transformed candidate directory is missing or unsafe"
        )
    if {entry.name for entry in candidate_dir.iterdir()} != {
        "organism.sqlite3",
        "manifest.json",
    }:
        raise ActiveReplacementRejectedError(
            "transformed candidate contains unexpected entries"
        )
    manifest_path = candidate_dir / "manifest.json"
    if not manifest_path.is_file() or manifest_path.is_symlink():
        raise ActiveReplacementRejectedError(
            "transformed candidate manifest is missing or unsafe"
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ActiveReplacementRejectedError(
            "transformed candidate manifest is not valid JSON"
        ) from exc
    if not isinstance(manifest, dict):
        raise ActiveReplacementRejectedError(
            "transformed candidate manifest is not a JSON object"
        )
    if manifest.get("transformed_candidate_id") != transformed_candidate_id:
        raise ActiveReplacementRejectedError(
            "transformed candidate identifier does not match manifest"
        )
    return candidate_dir, manifest


def _validate_manifest_relations(manifest: dict[str, Any]) -> None:
    required_text = (
        "transformed_candidate_id",
        "organism_id",
        "source_restore_candidate_id",
        "archive_id",
        "selected_checkpoint_id",
        "administrative_reason",
        "contract_version",
        "environment_version",
        "budget_config_version",
    )
    if any(not isinstance(manifest.get(key), str) or not manifest[key] for key in required_text):
        raise ActiveReplacementRejectedError(
            "transformed candidate manifest has missing protected text metadata"
        )
    required_int = (
        "rollback_started_event_sequence",
        "abandoned_lineage_generation",
        "abandoned_lifecycle_number",
        "abandoned_event_sequence",
        "selected_checkpoint_lineage_generation",
        "selected_checkpoint_event_sequence",
        "source_lineage_generation",
        "source_lifecycle_number",
        "source_event_sequence",
        "new_lineage_generation",
        "restoration_event_sequence",
        "restoration_wall_time_utc_us",
        "schema_version",
    )
    if any(
        not isinstance(manifest.get(key), int) or int(manifest[key]) < 0
        for key in required_int
    ):
        raise ActiveReplacementRejectedError(
            "transformed candidate manifest has invalid protected integer metadata"
        )
    exact = {
        "candidate_state": "lineage_transformed_replacement_ready",
        "status": "published",
        "provenance": "rollback_transformed_candidate",
    }
    for key, value in exact.items():
        if manifest.get(key) != value:
            raise ActiveReplacementRejectedError(
                f"transformed candidate {key} is invalid"
            )
    if manifest["new_lineage_generation"] != manifest["abandoned_lineage_generation"] + 1:
        raise ActiveReplacementRejectedError(
            "transformed candidate new lineage is not abandoned generation plus one"
        )
    if manifest["restoration_event_sequence"] != manifest["source_event_sequence"] + 1:
        raise ActiveReplacementRejectedError(
            "transformed candidate restoration event is not source boundary plus one"
        )
    if manifest["source_event_sequence"] != manifest["selected_checkpoint_event_sequence"]:
        raise ActiveReplacementRejectedError(
            "transformed candidate source and selected boundaries differ"
        )
    if manifest["source_lineage_generation"] != manifest[
        "selected_checkpoint_lineage_generation"
    ]:
        raise ActiveReplacementRejectedError(
            "transformed candidate source and selected lineages differ"
        )
    if manifest["rollback_started_event_sequence"] != manifest["abandoned_event_sequence"] + 1:
        raise ActiveReplacementRejectedError(
            "transformed candidate rollback-start boundary is invalid"
        )


def _selected_registry(
    connection: sqlite3.Connection,
    manifest: dict[str, Any],
) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM checkpoint_registry WHERE checkpoint_id = ?",
        (manifest.get("selected_checkpoint_id"),),
    ).fetchone()
    if row is None:
        raise ActiveReplacementRejectedError(
            "selected checkpoint registry row is missing"
        )
    expected = {
        "checkpoint_id": manifest.get("selected_checkpoint_id"),
        "lineage_generation": manifest.get("selected_checkpoint_lineage_generation"),
        "event_sequence": manifest.get("selected_checkpoint_event_sequence"),
        "manifest_sha256": manifest.get("selected_checkpoint_manifest_sha256"),
        "database_sha256": manifest.get("selected_checkpoint_database_sha256"),
        "database_size_bytes": manifest.get("selected_checkpoint_database_size_bytes"),
        "protected": 1,
    }
    for key, value in expected.items():
        if row[key] != value:
            raise ActiveReplacementRejectedError(
                f"selected checkpoint registry row does not match transformed candidate: {key}"
            )
    return row


def _validate_artifact_chain(
    paths: OrganismPaths,
    connection: sqlite3.Connection,
    candidate_dir: Path,
    manifest: dict[str, Any],
) -> _ReplacementContext:
    _validate_manifest_relations(manifest)
    selected_registry = _selected_registry(connection, manifest)
    checkpoint_dir = paths.checkpoints / str(manifest["selected_checkpoint_id"])
    checkpoint_manifest = validate_checkpoint_directory(checkpoint_dir)
    checkpoint_expected = {
        "checkpoint_id": manifest["selected_checkpoint_id"],
        "lineage_generation": manifest["selected_checkpoint_lineage_generation"],
        "event_sequence": manifest["selected_checkpoint_event_sequence"],
        "database_sha256": manifest["selected_checkpoint_database_sha256"],
        "database_size_bytes": manifest["selected_checkpoint_database_size_bytes"],
        "provenance": manifest["selected_checkpoint_provenance"],
        "organism_id": manifest["organism_id"],
        "lifecycle_number": manifest["source_lifecycle_number"],
        "contract_version": manifest["contract_version"],
        "schema_version": manifest["schema_version"],
        "environment_version": manifest["environment_version"],
        "budget_config_version": manifest["budget_config_version"],
    }
    for key, value in checkpoint_expected.items():
        if checkpoint_manifest.get(key) != value:
            raise ActiveReplacementRejectedError(
                f"selected checkpoint does not match transformed candidate: {key}"
            )
    if _sha256_file(checkpoint_dir / "manifest.json") != manifest[
        "selected_checkpoint_manifest_sha256"
    ]:
        raise ActiveReplacementRejectedError(
            "selected checkpoint manifest digest does not match transformed candidate"
        )

    source_candidate_dir = paths.restore_candidates / str(
        manifest["source_restore_candidate_id"]
    )
    source_manifest = _validate_candidate_directory(
        source_candidate_dir,
        source_checkpoint_dir=checkpoint_dir,
    )
    source_expected = {
        "candidate_id": manifest["source_restore_candidate_id"],
        "organism_id": manifest["organism_id"],
        "archive_id": manifest["archive_id"],
        "archive_manifest_sha256": manifest["archive_manifest_sha256"],
        "archive_database_sha256": manifest["archive_database_sha256"],
        "selected_checkpoint_id": manifest["selected_checkpoint_id"],
        "source_lineage_generation": manifest["source_lineage_generation"],
        "source_lifecycle_number": manifest["source_lifecycle_number"],
        "source_event_sequence": manifest["source_event_sequence"],
        "source_checkpoint_manifest_sha256": manifest[
            "selected_checkpoint_manifest_sha256"
        ],
        "source_checkpoint_database_sha256": manifest[
            "selected_checkpoint_database_sha256"
        ],
        "source_checkpoint_database_size_bytes": manifest[
            "selected_checkpoint_database_size_bytes"
        ],
        "source_checkpoint_provenance": manifest["selected_checkpoint_provenance"],
        "candidate_state": "source_restored_untransformed",
        "status": "published",
        "provenance": "restore_candidate",
    }
    for key, value in source_expected.items():
        if source_manifest.get(key) != value:
            raise ActiveReplacementRejectedError(
                f"source restore candidate does not match transformed candidate: {key}"
            )
    if _sha256_file(source_candidate_dir / "manifest.json") != manifest[
        "source_restore_candidate_manifest_sha256"
    ]:
        raise ActiveReplacementRejectedError(
            "source restore candidate manifest digest mismatch"
        )
    if _sha256_file(source_candidate_dir / "organism.sqlite3") != manifest[
        "source_restore_candidate_database_sha256"
    ]:
        raise ActiveReplacementRejectedError(
            "source restore candidate database digest mismatch"
        )

    _, archive_manifest, archive_manifest_sha256 = _load_archive(
        paths, str(manifest["archive_id"])
    )
    if archive_manifest_sha256 != manifest["archive_manifest_sha256"]:
        raise ActiveReplacementRejectedError(
            "rollback archive manifest digest does not match transformed candidate"
        )
    archive_expected = {
        "database_sha256": manifest["archive_database_sha256"],
        "organism_id": manifest["organism_id"],
        "active_lineage_generation": manifest["abandoned_lineage_generation"],
        "active_lifecycle_number": manifest["abandoned_lifecycle_number"],
        "active_event_sequence": manifest["abandoned_event_sequence"],
        "selected_checkpoint_id": manifest["selected_checkpoint_id"],
        "selected_checkpoint_lineage_generation": manifest[
            "selected_checkpoint_lineage_generation"
        ],
        "selected_checkpoint_event_sequence": manifest[
            "selected_checkpoint_event_sequence"
        ],
        "selected_checkpoint_manifest_sha256": manifest[
            "selected_checkpoint_manifest_sha256"
        ],
        "selected_checkpoint_database_sha256": manifest[
            "selected_checkpoint_database_sha256"
        ],
        "selected_checkpoint_database_size_bytes": manifest[
            "selected_checkpoint_database_size_bytes"
        ],
        "selected_checkpoint_provenance": manifest["selected_checkpoint_provenance"],
    }
    for key, value in archive_expected.items():
        if archive_manifest.get(key) != value:
            raise ActiveReplacementRejectedError(
                f"rollback archive does not match transformed candidate: {key}"
            )

    validated_manifest = _validate_transformed_candidate_directory(
        candidate_dir,
        source_candidate_dir=source_candidate_dir,
        selected_registry=selected_registry,
    )
    if validated_manifest != manifest:
        raise ActiveReplacementRejectedError(
            "transformed candidate manifest changed during validation"
        )
    return _ReplacementContext(
        candidate_dir=candidate_dir,
        manifest=manifest,
        manifest_sha256=_sha256_file(candidate_dir / "manifest.json"),
        database_sha256=_sha256_file(candidate_dir / "organism.sqlite3"),
        source_candidate_dir=source_candidate_dir,
        selected_registry=selected_registry,
    )


def _validate_pre_replacement(
    active: sqlite3.Connection,
    paths: OrganismPaths,
    transformed_candidate_id: str,
) -> _ReplacementContext:
    (
        organism,
        rollback_started,
        payload,
        _,
        _,
        selected,
        selected_manifest,
    ) = _validate_durable_intent(active, paths)
    candidate_dir, manifest = _read_manifest(paths, transformed_candidate_id)
    _validate_manifest_relations(manifest)
    selected_registry = active.execute(
        "SELECT * FROM checkpoint_registry WHERE checkpoint_id = ?",
        (selected["checkpoint_id"],),
    ).fetchone()
    if selected_registry is None:
        raise ActiveReplacementRejectedError(
            "selected checkpoint registry row disappeared after intent validation"
        )
    source_dir, source_manifest, source_manifest_sha, source_database_sha = (
        _validate_source_candidate(
            paths,
            str(manifest["source_restore_candidate_id"]),
            organism=organism,
            rollback_started=rollback_started,
            payload=payload,
            selected=selected,
            selected_manifest=selected_manifest,
        )
    )
    validated = _validate_transformed_candidate_directory(
        candidate_dir,
        source_candidate_dir=source_dir,
        selected_registry=selected_registry,
    )
    expected = {
        "transformed_candidate_id": transformed_candidate_id,
        "organism_id": organism["organism_id"],
        "source_restore_candidate_id": source_manifest["candidate_id"],
        "source_restore_candidate_manifest_sha256": source_manifest_sha,
        "source_restore_candidate_database_sha256": source_database_sha,
        "archive_id": payload["archive_id"],
        "archive_manifest_sha256": payload["archive_manifest_sha256"],
        "archive_database_sha256": payload["archive_database_sha256"],
        "rollback_started_event_sequence": int(rollback_started["event_sequence"]),
        "abandoned_lineage_generation": int(payload["pre_rollback_lineage_generation"]),
        "abandoned_lifecycle_number": int(payload["pre_rollback_lifecycle_number"]),
        "abandoned_event_sequence": int(payload["pre_rollback_event_sequence"]),
        "selected_checkpoint_id": selected["checkpoint_id"],
        "selected_checkpoint_lineage_generation": int(selected["lineage_generation"]),
        "selected_checkpoint_event_sequence": int(selected["event_sequence"]),
        "selected_checkpoint_manifest_sha256": selected["manifest_sha256"],
        "selected_checkpoint_database_sha256": selected["database_sha256"],
        "selected_checkpoint_database_size_bytes": int(selected["database_size_bytes"]),
        "selected_checkpoint_provenance": selected_manifest["provenance"],
        "source_lineage_generation": int(selected["lineage_generation"]),
        "source_lifecycle_number": int(selected_manifest["lifecycle_number"]),
        "source_event_sequence": int(selected["event_sequence"]),
        "new_lineage_generation": int(organism["lineage_generation"]) + 1,
        "restoration_event_sequence": int(selected["event_sequence"]) + 1,
    }
    for key, value in expected.items():
        if validated.get(key) != value:
            raise ActiveReplacementRejectedError(
                f"transformed candidate does not match active rollback intent: {key}"
            )
    return _ReplacementContext(
        candidate_dir=candidate_dir,
        manifest=validated,
        manifest_sha256=_sha256_file(candidate_dir / "manifest.json"),
        database_sha256=_sha256_file(candidate_dir / "organism.sqlite3"),
        source_candidate_dir=source_dir,
        selected_registry=selected_registry,
    )


def _validate_replaced(
    active: sqlite3.Connection,
    paths: OrganismPaths,
    transformed_candidate_id: str,
) -> _ReplacementContext:
    candidate_dir, manifest = _read_manifest(paths, transformed_candidate_id)
    context = _validate_artifact_chain(paths, active, candidate_dir, manifest)
    organism = active.execute(
        "SELECT * FROM organism WHERE singleton_id = 1"
    ).fetchone()
    tip = active.execute(
        "SELECT * FROM event ORDER BY event_sequence DESC LIMIT 1"
    ).fetchone()
    if organism is None or tip is None:
        raise ActiveReplacementRejectedError(
            "replaced active database is missing protected state"
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
    }
    for key, value in expected_organism.items():
        if organism[key] != value:
            raise ActiveReplacementRejectedError(
                f"replaced active organism does not match transformed candidate: {key}"
            )
    expected_tip = {
        "event_sequence": manifest["restoration_event_sequence"],
        "organism_id": manifest["organism_id"],
        "lineage_generation": manifest["new_lineage_generation"],
        "lifecycle_number": manifest["source_lifecycle_number"],
        "event_type": "rollback_lineage_prepared",
        "source": "administration:rollback-candidate",
    }
    for key, value in expected_tip.items():
        if tip[key] != value:
            raise ActiveReplacementRejectedError(
                f"replaced active event tip does not match transformed candidate: {key}"
            )
    candidate = connect_database(candidate_dir / "organism.sqlite3", read_only=True)
    try:
        if _canonical_sqlite_snapshot(active) != _canonical_sqlite_snapshot(candidate):
            raise ActiveReplacementRejectedError(
                "replaced active SQLite content does not exactly match transformed candidate"
            )
    finally:
        candidate.close()
    return context


def _validate_stage(stage_path: Path, context: _ReplacementContext) -> None:
    staged = connect_database(stage_path, read_only=True)
    candidate = connect_database(context.candidate_dir / "organism.sqlite3", read_only=True)
    try:
        integrity = staged.execute("PRAGMA integrity_check").fetchall()
        if len(integrity) != 1 or integrity[0][0] != "ok":
            raise ActiveReplacementError(
                f"staged active database integrity check failed: {integrity!r}"
            )
        foreign_keys = staged.execute("PRAGMA foreign_key_check").fetchall()
        if foreign_keys:
            raise ActiveReplacementError(
                f"staged active database foreign-key check failed: {foreign_keys!r}"
            )
        validate_canonical_state(staged, expect_checkpoint_pending=False)
        if _canonical_sqlite_snapshot(staged) != _canonical_sqlite_snapshot(candidate):
            raise ActiveReplacementError(
                "staged active database does not exactly match transformed candidate"
            )
    except SchemaValidationError as exc:
        raise ActiveReplacementError(str(exc)) from exc
    finally:
        candidate.close()
        staged.close()


def _result(
    paths: OrganismPaths,
    transformed_candidate_id: str,
    context: _ReplacementContext,
    *,
    recovered: bool,
) -> ActiveReplacementResult:
    manifest = context.manifest
    return ActiveReplacementResult(
        organism_id=str(manifest["organism_id"]),
        transformed_candidate_id=transformed_candidate_id,
        active_database=paths.database,
        archive_id=str(manifest["archive_id"]),
        selected_checkpoint_id=str(manifest["selected_checkpoint_id"]),
        abandoned_lineage_generation=int(manifest["abandoned_lineage_generation"]),
        new_lineage_generation=int(manifest["new_lineage_generation"]),
        source_lifecycle_number=int(manifest["source_lifecycle_number"]),
        source_event_sequence=int(manifest["source_event_sequence"]),
        restoration_event_sequence=int(manifest["restoration_event_sequence"]),
        active_database_size_bytes=paths.database.stat().st_size,
        active_database_sha256=_sha256_file(paths.database),
        transformed_candidate_database_sha256=context.database_sha256,
        transformed_candidate_manifest_sha256=context.manifest_sha256,
        recovered_existing_replacement=recovered,
        status="rollback_in_progress",
    )


def replace_active_with_candidate(
    runtime_root: Path | str,
    organism_id: str,
    transformed_candidate_id: str,
    *,
    protected_test_fail_before_replace: bool = False,
    protected_test_fail_after_replace: bool = False,
) -> ActiveReplacementResult:
    """Atomically replace the blocked active database and validate the new body."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file() or paths.database.is_symlink():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")
    if not _TRANSFORMED_CANDIDATE_ID_RE.fullmatch(transformed_candidate_id):
        raise ActiveReplacementRejectedError(
            "transformed candidate identifier does not match the protected format"
        )

    active: sqlite3.Connection | None = connect_database(paths.database)
    stage_path: Path | None = None
    replaced = False
    try:
        try:
            active.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise ActiveReplacementBusyError(
                    "active replacement is busy; this attempt was not queued"
                ) from exc
            raise
        validate_canonical_state(active, expect_checkpoint_pending=False)
        organism = active.execute(
            "SELECT * FROM organism WHERE singleton_id = 1"
        ).fetchone()
        tip = active.execute(
            "SELECT * FROM event ORDER BY event_sequence DESC LIMIT 1"
        ).fetchone()
        if organism is None or tip is None:
            raise ActiveReplacementRejectedError(
                "active database is missing protected rollback state"
            )

        is_replaced = (
            organism["status"] == "rollback_in_progress"
            and tip["event_type"] == "rollback_lineage_prepared"
            and tip["source"] == "administration:rollback-candidate"
            and tip["lineage_generation"] == organism["lineage_generation"]
        )
        if is_replaced:
            context = _validate_replaced(active, paths, transformed_candidate_id)
            active.rollback()
            active.close()
            active = None
            return _result(paths, transformed_candidate_id, context, recovered=True)

        is_prepared = (
            organism["status"] == "rollback_in_progress"
            and tip["event_type"] == "rollback_started"
            and tip["source"] == "administration:rollback"
            and tip["lineage_generation"] == organism["lineage_generation"]
        )
        if not is_prepared:
            raise ActiveReplacementRejectedError(
                "active database is neither the protected pre-replacement intent nor the exact replaced candidate"
            )

        context = _validate_pre_replacement(active, paths, transformed_candidate_id)
        predicted_size = _tree_size(paths.organism_dir) + int(
            context.manifest["database_size_bytes"]
        )
        if predicted_size > RUNTIME_WORKING_SET_MAX_BYTES:
            raise ActiveReplacementError(
                "active replacement staging would exceed the protected runtime working-set limit"
            )

        descriptor, stage_name = tempfile.mkstemp(
            prefix=".tmp-active-replacement-",
            suffix=".sqlite3",
            dir=paths.organism_dir,
        )
        os.close(descriptor)
        stage_path = Path(stage_name)
        source = connect_database(context.candidate_dir / "organism.sqlite3", read_only=True)
        destination = sqlite3.connect(stage_path, isolation_level=None)
        try:
            source.backup(destination, pages=64, sleep=0.0)
        finally:
            destination.close()
            source.close()
        _validate_stage(stage_path, context)
        _fsync_file(stage_path)

        active_size = paths.database.stat().st_size
        active_sha = _sha256_file(paths.database)
        candidate_manifest_sha = _sha256_file(context.candidate_dir / "manifest.json")
        candidate_database_sha = _sha256_file(context.candidate_dir / "organism.sqlite3")
        if candidate_manifest_sha != context.manifest_sha256:
            raise ActiveReplacementRejectedError(
                "transformed candidate manifest changed before replacement"
            )
        if candidate_database_sha != context.database_sha256:
            raise ActiveReplacementRejectedError(
                "transformed candidate database changed before replacement"
            )

        active.rollback()
        active.close()
        active = None
        if (
            not paths.database.is_file()
            or paths.database.is_symlink()
            or paths.database.stat().st_size != active_size
            or _sha256_file(paths.database) != active_sha
        ):
            raise ActiveReplacementRejectedError(
                "active database changed after validation and before replacement"
            )
        if (
            _sha256_file(context.candidate_dir / "manifest.json")
            != candidate_manifest_sha
            or _sha256_file(context.candidate_dir / "organism.sqlite3")
            != candidate_database_sha
        ):
            raise ActiveReplacementRejectedError(
                "transformed candidate changed after validation and before replacement"
            )
        if protected_test_fail_before_replace:
            raise ActiveReplacementError(
                "injected active replacement failure before authority transfer"
            )

        os.replace(stage_path, paths.database)
        stage_path = None
        replaced = True
        _fsync_dir(paths.organism_dir)
        if protected_test_fail_after_replace:
            raise ActiveReplacementIncompleteError(
                "active database was replaced but post-replacement validation was interrupted"
            )

        post = connect_database(paths.database)
        try:
            try:
                post.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError as exc:
                if _is_busy(exc):
                    raise ActiveReplacementIncompleteError(
                        "active database was replaced but post-replacement validation is busy"
                    ) from exc
                raise
            validate_canonical_state(post, expect_checkpoint_pending=False)
            validated = _validate_replaced(post, paths, transformed_candidate_id)
            post.rollback()
        finally:
            if post.in_transaction:
                post.rollback()
            post.close()
        return _result(paths, transformed_candidate_id, validated, recovered=False)
    except ActiveReplacementIncompleteError:
        raise
    except (
        CheckpointError,
        RollbackArchiveError,
        RollbackBeginRejectedError,
        RollbackPreparationRejectedError,
        RestoreCandidateError,
        RestoreCandidateRejectedError,
        CandidateTransformError,
        CandidateTransformRejectedError,
        SchemaValidationError,
    ) as exc:
        if replaced:
            raise ActiveReplacementIncompleteError(
                "active database was replaced but post-replacement validation failed: "
                f"{exc}"
            ) from exc
        raise ActiveReplacementRejectedError(str(exc)) from exc
    except (OSError, sqlite3.Error) as exc:
        if replaced:
            raise ActiveReplacementIncompleteError(
                "active database was replaced but post-replacement validation failed: "
                f"{exc}"
            ) from exc
        raise ActiveReplacementError(str(exc)) from exc
    finally:
        if active is not None:
            if active.in_transaction:
                active.rollback()
            active.close()
        if stage_path is not None and stage_path.exists():
            stage_path.unlink(missing_ok=True)
            _fsync_dir(paths.organism_dir)
