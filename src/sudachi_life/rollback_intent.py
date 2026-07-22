"""Durable adoption of one verified pre-rollback archive."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import sqlite3
from typing import Any

from .clock import Clock, RealClock
from .errors import CheckpointError, OrganismNotFoundError, SchemaValidationError, SudachiError
from .paths import OrganismPaths
from .rollback import (
    RollbackArchiveError,
    RollbackPreparationRejectedError,
    _sha256_file,
    _validate_archive_directory,
    _validate_selected_checkpoint,
)
from .storage import connect_database, validate_canonical_state


_ROLLBACK_ARCHIVE_ID_RE = re.compile(
    r"^pre-rb-g[0-9]{6}-e[0-9]{12}-to-e[0-9]{12}-[0-9a-f]{8}$"
)


class RollbackBeginBusyError(SudachiError):
    """Rollback begin could not acquire fail-fast administrative ownership."""


class RollbackBeginRejectedError(SudachiError):
    """The archive or active organism is not eligible for durable rollback intent."""


class _InjectedRollbackBeginFailure(Exception):
    """Protected test-only failure after the rollback-start event is inserted."""


@dataclass(frozen=True, slots=True)
class RollbackBeginResult:
    organism_id: str
    archive_id: str
    archive_manifest_sha256: str
    selected_checkpoint_id: str
    selected_checkpoint_event_sequence: int
    lineage_generation: int
    lifecycle_number: int
    pre_rollback_status: str
    status: str
    pre_rollback_event_sequence: int
    rollback_started_event_sequence: int
    latest_stable_checkpoint_id: str
    latest_stable_event_sequence: int

    def as_dict(self) -> dict[str, object]:
        return {
            "organism_id": self.organism_id,
            "archive_id": self.archive_id,
            "archive_manifest_sha256": self.archive_manifest_sha256,
            "selected_checkpoint_id": self.selected_checkpoint_id,
            "selected_checkpoint_event_sequence": self.selected_checkpoint_event_sequence,
            "lineage_generation": self.lineage_generation,
            "lifecycle_number": self.lifecycle_number,
            "pre_rollback_status": self.pre_rollback_status,
            "status": self.status,
            "pre_rollback_event_sequence": self.pre_rollback_event_sequence,
            "rollback_started_event_sequence": self.rollback_started_event_sequence,
            "latest_stable_checkpoint_id": self.latest_stable_checkpoint_id,
            "latest_stable_event_sequence": self.latest_stable_event_sequence,
        }


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _canonical_sqlite_snapshot(connection: sqlite3.Connection) -> dict[str, object]:
    """Return exact protected schema, table rows, and AUTOINCREMENT state."""

    schema_rows = connection.execute(
        """SELECT type, name, tbl_name, sql
           FROM sqlite_master
           WHERE name NOT LIKE 'sqlite_%'
           ORDER BY type, name"""
    ).fetchall()
    schema = [tuple(row) for row in schema_rows]
    tables = [str(row[1]) for row in schema_rows if row[0] == "table"]
    table_rows: dict[str, list[tuple[object, ...]]] = {}
    for table in tables:
        quoted = _quote_identifier(table)
        columns = connection.execute(f"PRAGMA table_info({quoted})").fetchall()
        primary_key = sorted(
            (
                (int(column["pk"]), str(column["name"]))
                for column in columns
                if int(column["pk"]) > 0
            ),
            key=lambda item: item[0],
        )
        if primary_key:
            order_clause = ", ".join(
                _quote_identifier(column_name) for _, column_name in primary_key
            )
        else:
            order_clause = "rowid"
        rows = connection.execute(
            f"SELECT * FROM {quoted} ORDER BY {order_clause}"
        ).fetchall()
        table_rows[table] = [tuple(row) for row in rows]

    has_sequence = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'sqlite_sequence'"
    ).fetchone()
    sequence_rows: list[tuple[object, ...]] = []
    if has_sequence is not None:
        sequence_rows = [
            tuple(row)
            for row in connection.execute(
                "SELECT name, seq FROM sqlite_sequence ORDER BY name"
            ).fetchall()
        ]

    return {
        "user_version": int(connection.execute("PRAGMA user_version").fetchone()[0]),
        "schema": schema,
        "tables": table_rows,
        "sqlite_sequence": sequence_rows,
    }


def _load_archive(
    paths: OrganismPaths,
    archive_id: str,
) -> tuple[Path, dict[str, Any], str]:
    if not _ROLLBACK_ARCHIVE_ID_RE.fullmatch(archive_id):
        raise RollbackBeginRejectedError(
            "rollback archive identifier does not match the protected pre-rollback format"
        )
    archives_dir = paths.rollback_archives
    if not archives_dir.is_dir() or archives_dir.is_symlink():
        raise RollbackBeginRejectedError("rollback archive root is missing or unsafe")
    archive_dir = archives_dir / archive_id
    manifest = _validate_archive_directory(archive_dir)
    if manifest.get("archive_id") != archive_id:
        raise RollbackBeginRejectedError(
            "rollback archive identifier does not match manifest"
        )
    return archive_dir, manifest, _sha256_file(archive_dir / "manifest.json")


def _reject_repeated_begin(
    connection: sqlite3.Connection,
    organism: sqlite3.Row,
    archive_id: str,
) -> None:
    row = connection.execute(
        """SELECT payload_json
           FROM event
           WHERE event_type = 'rollback_started'
             AND lineage_generation = ?
           ORDER BY event_sequence DESC
           LIMIT 1""",
        (organism["lineage_generation"],),
    ).fetchone()
    if row is None:
        raise RollbackBeginRejectedError(
            "rollback_in_progress state has no rollback_started event"
        )
    try:
        payload = json.loads(row["payload_json"])
    except json.JSONDecodeError as exc:
        raise RollbackBeginRejectedError(
            "rollback_started event payload is not valid JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise RollbackBeginRejectedError(
            "rollback_started event payload is not a JSON object"
        )
    active_archive_id = payload.get("archive_id")
    if active_archive_id == archive_id:
        raise RollbackBeginRejectedError(
            f"rollback intent is already active for archive {archive_id}"
        )
    raise RollbackBeginRejectedError(
        "rollback is already in progress with a different archive: "
        f"active={active_archive_id!r}, requested={archive_id!r}"
    )


def _validate_latest_checkpoint(
    connection: sqlite3.Connection,
    organism: sqlite3.Row,
) -> None:
    checkpoint_id = organism["latest_stable_checkpoint_id"]
    if checkpoint_id is None:
        raise RollbackBeginRejectedError(
            "rollback begin requires a latest stable checkpoint"
        )
    row = connection.execute(
        """SELECT lineage_generation, event_sequence, protected
           FROM checkpoint_registry WHERE checkpoint_id = ?""",
        (checkpoint_id,),
    ).fetchone()
    if row is None or (
        int(row["lineage_generation"]) != int(organism["lineage_generation"])
        or int(row["event_sequence"])
        != int(organism["latest_stable_event_sequence"])
        or int(row["protected"]) != 1
    ):
        raise RollbackBeginRejectedError(
            "latest stable checkpoint does not match protected active state"
        )


def _validate_current_matches_archive(
    connection: sqlite3.Connection,
    archive_dir: Path,
    paths: OrganismPaths,
    organism: sqlite3.Row,
    manifest: dict[str, Any],
) -> tuple[sqlite3.Row, int]:
    active_event_sequence = int(
        connection.execute(
            "SELECT COALESCE(MAX(event_sequence), 0) FROM event"
        ).fetchone()[0]
    )
    expected = {
        "organism_id": str(organism["organism_id"]),
        "active_lineage_generation": int(organism["lineage_generation"]),
        "active_lifecycle_number": int(organism["lifecycle_number"]),
        "active_status": str(organism["status"]),
        "active_event_sequence": active_event_sequence,
        "latest_stable_checkpoint_id": organism["latest_stable_checkpoint_id"],
        "latest_stable_event_sequence": int(organism["latest_stable_event_sequence"]),
        "contract_version": str(organism["contract_version"]),
        "schema_version": int(organism["schema_version"]),
        "environment_version": str(organism["environment_version"]),
        "budget_config_version": str(organism["budget_config_version"]),
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise RollbackBeginRejectedError(
                f"active state drifted from rollback archive: {key}"
            )

    archived = connect_database(archive_dir / "organism.sqlite3", read_only=True)
    try:
        if _canonical_sqlite_snapshot(connection) != _canonical_sqlite_snapshot(archived):
            raise RollbackBeginRejectedError(
                "active canonical SQLite content drifted from rollback archive"
            )
    finally:
        archived.close()

    source_event_sequence = int(manifest.get("selected_checkpoint_event_sequence", -1))
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
        "selected_checkpoint_database_size_bytes": int(selected["database_size_bytes"]),
        "selected_checkpoint_provenance": str(selected_manifest["provenance"]),
    }
    for key, value in selected_expected.items():
        if manifest.get(key) != value:
            raise RollbackBeginRejectedError(
                f"selected rollback source drifted from archive: {key}"
            )
    return selected, active_event_sequence


def begin_rollback(
    runtime_root: Path | str,
    organism_id: str,
    archive_id: str,
    *,
    clock: Clock | None = None,
    protected_test_fail_after_event_insert: bool = False,
) -> RollbackBeginResult:
    """Atomically adopt one verified archive as a durable rollback intent."""

    paths = OrganismPaths.build(runtime_root, organism_id)
    if not paths.database.is_file() or paths.database.is_symlink():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")
    if not _ROLLBACK_ARCHIVE_ID_RE.fullmatch(archive_id):
        raise RollbackBeginRejectedError(
            "rollback archive identifier does not match the protected pre-rollback format"
        )

    connection = connect_database(paths.database)
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise RollbackBeginBusyError(
                    "rollback begin is busy; this attempt was not queued"
                ) from exc
            raise

        validate_canonical_state(connection)
        organism = connection.execute(
            """SELECT organism_id, contract_version, schema_version,
                      environment_version, budget_config_version,
                      lineage_generation, lifecycle_number, status,
                      checkpoint_pending, latest_stable_checkpoint_id,
                      latest_stable_event_sequence
               FROM organism WHERE singleton_id = 1"""
        ).fetchone()
        if organism is None:
            raise RollbackBeginRejectedError("canonical organism state is missing")
        if int(organism["checkpoint_pending"]) != 0:
            raise RollbackBeginRejectedError(
                "rollback begin requires no pending checkpoint"
            )
        if organism["status"] == "rollback_in_progress":
            _reject_repeated_begin(connection, organism, archive_id)
        if organism["status"] not in {"sleeping", "maintenance_required"}:
            raise RollbackBeginRejectedError(
                "rollback begin requires stable sleeping or maintenance state: "
                f"status={organism['status']}"
            )

        _validate_latest_checkpoint(connection, organism)
        archive_dir, manifest, manifest_sha256 = _load_archive(paths, archive_id)
        if manifest.get("organism_id") != organism["organism_id"]:
            raise RollbackBeginRejectedError(
                "rollback archive belongs to a different organism"
            )
        selected, active_event_sequence = _validate_current_matches_archive(
            connection,
            archive_dir,
            paths,
            organism,
            manifest,
        )

        reading = (clock or RealClock()).read()
        pre_status = str(organism["status"])
        cursor = connection.execute(
            """UPDATE organism
               SET status = 'rollback_in_progress'
               WHERE singleton_id = 1
                 AND status = ?
                 AND checkpoint_pending = 0
                 AND lineage_generation = ?
                 AND lifecycle_number = ?
                 AND latest_stable_checkpoint_id = ?
                 AND latest_stable_event_sequence = ?""",
            (
                pre_status,
                organism["lineage_generation"],
                organism["lifecycle_number"],
                organism["latest_stable_checkpoint_id"],
                organism["latest_stable_event_sequence"],
            ),
        )
        if cursor.rowcount != 1:
            raise RollbackBeginRejectedError(
                "active state changed before rollback intent adoption"
            )

        payload = {
            "archive_id": archive_id,
            "archive_manifest_sha256": manifest_sha256,
            "archive_database_sha256": str(manifest["database_sha256"]),
            "pre_rollback_status": pre_status,
            "pre_rollback_lineage_generation": int(organism["lineage_generation"]),
            "pre_rollback_lifecycle_number": int(organism["lifecycle_number"]),
            "pre_rollback_event_sequence": active_event_sequence,
            "latest_stable_checkpoint_id": str(organism["latest_stable_checkpoint_id"]),
            "latest_stable_event_sequence": int(
                organism["latest_stable_event_sequence"]
            ),
            "selected_checkpoint_id": str(selected["checkpoint_id"]),
            "selected_checkpoint_lineage_generation": int(
                selected["lineage_generation"]
            ),
            "selected_checkpoint_event_sequence": int(selected["event_sequence"]),
            "selected_checkpoint_manifest_sha256": str(
                selected["manifest_sha256"]
            ),
            "selected_checkpoint_database_sha256": str(
                selected["database_sha256"]
            ),
        }
        event_cursor = connection.execute(
            """INSERT INTO event (
                   organism_id, lineage_generation, lifecycle_number,
                   wall_time_utc_us, event_type, source, payload_json,
                   schema_version, environment_version, budget_config_version
               ) VALUES (?, ?, ?, ?, 'rollback_started',
                         'administration:rollback', ?, ?, ?, ?)""",
            (
                organism["organism_id"],
                organism["lineage_generation"],
                organism["lifecycle_number"],
                reading.wall_time_utc_us,
                json.dumps(payload, sort_keys=True, separators=(",", ":")),
                organism["schema_version"],
                organism["environment_version"],
                organism["budget_config_version"],
            ),
        )
        rollback_started_event_sequence = int(event_cursor.lastrowid)
        if rollback_started_event_sequence != active_event_sequence + 1:
            raise SchemaValidationError(
                "rollback_started event did not append at the exact next sequence"
            )

        if protected_test_fail_after_event_insert:
            raise _InjectedRollbackBeginFailure(
                "injected rollback begin failure after event insert"
            )

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        connection.commit()
        return RollbackBeginResult(
            organism_id=str(organism["organism_id"]),
            archive_id=archive_id,
            archive_manifest_sha256=manifest_sha256,
            selected_checkpoint_id=str(selected["checkpoint_id"]),
            selected_checkpoint_event_sequence=int(selected["event_sequence"]),
            lineage_generation=int(organism["lineage_generation"]),
            lifecycle_number=int(organism["lifecycle_number"]),
            pre_rollback_status=pre_status,
            status="rollback_in_progress",
            pre_rollback_event_sequence=active_event_sequence,
            rollback_started_event_sequence=rollback_started_event_sequence,
            latest_stable_checkpoint_id=str(
                organism["latest_stable_checkpoint_id"]
            ),
            latest_stable_event_sequence=int(
                organism["latest_stable_event_sequence"]
            ),
        )
    except _InjectedRollbackBeginFailure as exc:
        raise RollbackBeginRejectedError(str(exc)) from exc
    except (
        CheckpointError,
        RollbackArchiveError,
        RollbackPreparationRejectedError,
        SchemaValidationError,
        OSError,
    ) as exc:
        raise RollbackBeginRejectedError(str(exc)) from exc
    finally:
        if connection.in_transaction:
            connection.rollback()
        connection.close()
