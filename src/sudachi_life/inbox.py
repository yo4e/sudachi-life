"""Idempotent administrative input enqueueing."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import sqlite3

from .clock import Clock, RealClock
from .errors import SudachiError, OrganismNotFoundError
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state

GARDEN_TICK_EVENT_TYPE = "synthetic:garden_tick"
_EXTERNAL_EVENT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


class InboxBusyError(SudachiError):
    """The administrative inbox write could not acquire SQLite ownership."""


class InvalidExternalEventIdError(SudachiError):
    """The caller-supplied external event identifier is invalid."""


class InputRejectedError(SudachiError):
    """Canonical state is not eligible to accept normal input."""


@dataclass(frozen=True, slots=True)
class EnqueueResult:
    external_event_id: str
    event_type: str
    inbox_id: int
    inserted: bool
    received_wall_time_utc_us: int

    def as_dict(self) -> dict[str, object]:
        return {
            "external_event_id": self.external_event_id,
            "event_type": self.event_type,
            "inbox_id": self.inbox_id,
            "inserted": self.inserted,
            "received_wall_time_utc_us": self.received_wall_time_utc_us,
        }


def validate_external_event_id(external_event_id: str) -> str:
    if not _EXTERNAL_EVENT_ID_RE.fullmatch(external_event_id):
        raise InvalidExternalEventIdError(
            "external event id must be 1-128 ASCII letters, digits, dots, underscores, "
            "colons, or hyphens and must start with a letter or digit"
        )
    return external_event_id


def _is_busy(exc: sqlite3.OperationalError) -> bool:
    code = getattr(exc, "sqlite_errorcode", None)
    return code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower()


def _append_enqueue_event(
    connection: sqlite3.Connection,
    *,
    organism: sqlite3.Row,
    wall_time_utc_us: int,
    source: str,
    external_event_id: str,
    inbox_id: int,
) -> None:
    connection.execute(
        """
        INSERT INTO event (
            organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
            event_type, source, payload_json, schema_version,
            environment_version, budget_config_version
        ) VALUES (?, ?, ?, ?, 'input_enqueued', ?, ?, ?, ?, ?)
        """,
        (
            organism["organism_id"],
            organism["lineage_generation"],
            organism["lifecycle_number"],
            wall_time_utc_us,
            source,
            json.dumps(
                {
                    "external_event_id": external_event_id,
                    "event_type": GARDEN_TICK_EVENT_TYPE,
                    "inbox_id": inbox_id,
                },
                sort_keys=True,
                separators=(",", ":"),
            ),
            organism["schema_version"],
            organism["environment_version"],
            organism["budget_config_version"],
        ),
    )


def enqueue_garden_tick(
    paths: OrganismPaths,
    external_event_id: str,
    *,
    clock: Clock | None = None,
    source: str = "administration:cli",
) -> EnqueueResult:
    """Insert one unique tick or return the existing row without another clock read."""

    external_event_id = validate_external_event_id(external_event_id)
    if not paths.database.is_file():
        raise OrganismNotFoundError(f"organism database not found: {paths.database}")

    connection = connect_database(paths.database)
    try:
        try:
            connection.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            if _is_busy(exc):
                raise InboxBusyError("organism database is busy; input was not queued") from exc
            raise

        validate_canonical_state(connection, expect_checkpoint_pending=False)
        organism = connection.execute(
            "SELECT organism_id, lineage_generation, lifecycle_number, status, "
            "schema_version, environment_version, budget_config_version "
            "FROM organism WHERE singleton_id = 1"
        ).fetchone()
        if organism["status"] != "sleeping":
            raise InputRejectedError(
                f"organism status does not accept normal input: {organism['status']}"
            )

        existing = connection.execute(
            "SELECT inbox_id, event_type, received_wall_time_utc_us "
            "FROM inbox_event WHERE external_event_id = ?",
            (external_event_id,),
        ).fetchone()
        if existing is not None:
            if existing["event_type"] != GARDEN_TICK_EVENT_TYPE:
                raise InputRejectedError(
                    "external event id already belongs to another event type"
                )
            connection.rollback()
            return EnqueueResult(
                external_event_id=external_event_id,
                event_type=existing["event_type"],
                inbox_id=existing["inbox_id"],
                inserted=False,
                received_wall_time_utc_us=existing["received_wall_time_utc_us"],
            )

        reading = (clock or RealClock()).read()
        cursor = connection.execute(
            """
            INSERT INTO inbox_event (
                external_event_id, event_type, source,
                source_wall_time_utc_us, received_wall_time_utc_us,
                claimed_lifecycle_number, consumed
            ) VALUES (?, ?, ?, NULL, ?, NULL, 0)
            """,
            (
                external_event_id,
                GARDEN_TICK_EVENT_TYPE,
                source,
                reading.wall_time_utc_us,
            ),
        )
        inbox_id = int(cursor.lastrowid)
        _append_enqueue_event(
            connection,
            organism=organism,
            wall_time_utc_us=reading.wall_time_utc_us,
            source=source,
            external_event_id=external_event_id,
            inbox_id=inbox_id,
        )
        connection.commit()
        return EnqueueResult(
            external_event_id=external_event_id,
            event_type=GARDEN_TICK_EVENT_TYPE,
            inbox_id=inbox_id,
            inserted=True,
            received_wall_time_utc_us=reading.wall_time_utc_us,
        )
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise
    finally:
        connection.close()
