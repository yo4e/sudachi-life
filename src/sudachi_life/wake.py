"""Fail-fast wake acquisition, input claim, and deterministic observation."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from .errors import OrganismNotFoundError, SudachiError
from .garden import GardenObservation, build_garden_observation
from .inbox import GARDEN_TICK_EVENT_TYPE
from .paths import OrganismPaths
from .storage import connect_database, validate_canonical_state


class WakeBusyError(SudachiError):
    """A normal wake could not acquire the fail-fast write transaction."""


class WakeRejectedError(SudachiError):
    """Canonical state is not eligible for a normal wake operation."""


class NoInputEventError(SudachiError):
    """No eligible garden tick is available to claim."""


@dataclass(frozen=True, slots=True)
class ClaimedInput:
    inbox_id: int
    external_event_id: str
    event_type: str
    source: str
    received_wall_time_utc_us: int
    lifecycle_number: int


class WakeTransaction:
    """An acquired outer wake transaction.

    Slice 2 deliberately provides rollback-only ownership. A later slice will add
    validated lifecycle commit and checkpoint stabilization.
    """

    def __init__(self, connection: sqlite3.Connection, lifecycle_number: int) -> None:
        self.connection = connection
        self.lifecycle_number = lifecycle_number
        self._closed = False
        self._claimed: ClaimedInput | None = None

    @classmethod
    def acquire(cls, paths: OrganismPaths) -> "WakeTransaction":
        if not paths.database.is_file():
            raise OrganismNotFoundError(f"organism database not found: {paths.database}")

        connection = connect_database(paths.database)
        try:
            try:
                connection.execute("BEGIN IMMEDIATE")
            except sqlite3.OperationalError as exc:
                code = getattr(exc, "sqlite_errorcode", None)
                if code in {sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED} or "locked" in str(exc).lower():
                    raise WakeBusyError(
                        "organism wake is busy; this attempt was not queued"
                    ) from exc
                raise

            validate_canonical_state(connection, expect_checkpoint_pending=False)
            organism = connection.execute(
                "SELECT lifecycle_number, status, checkpoint_pending FROM organism "
                "WHERE singleton_id = 1"
            ).fetchone()
            if organism is None:
                raise WakeRejectedError("canonical organism state is missing")
            if organism["status"] != "sleeping" or organism["checkpoint_pending"] != 0:
                raise WakeRejectedError(
                    f"organism is not wakeable: status={organism['status']} "
                    f"checkpoint_pending={organism['checkpoint_pending']}"
                )
            return cls(connection, int(organism["lifecycle_number"]) + 1)
        except Exception:
            if connection.in_transaction:
                connection.rollback()
            connection.close()
            raise

    def claim_oldest_garden_tick(self) -> ClaimedInput:
        if self._closed:
            raise WakeRejectedError("wake transaction is closed")
        if self._claimed is not None:
            raise WakeRejectedError("wake transaction already claimed an input")

        row = self.connection.execute(
            """
            SELECT inbox_id, external_event_id, event_type, source, received_wall_time_utc_us
            FROM inbox_event
            WHERE consumed = 0
              AND claimed_lifecycle_number IS NULL
              AND event_type = ?
            ORDER BY inbox_id
            LIMIT 1
            """,
            (GARDEN_TICK_EVENT_TYPE,),
        ).fetchone()
        if row is None:
            raise NoInputEventError("no unclaimed synthetic:garden_tick is available")

        cursor = self.connection.execute(
            """
            UPDATE inbox_event
            SET claimed_lifecycle_number = ?
            WHERE inbox_id = ?
              AND consumed = 0
              AND claimed_lifecycle_number IS NULL
            """,
            (self.lifecycle_number, row["inbox_id"]),
        )
        if cursor.rowcount != 1:
            raise WakeRejectedError("garden tick claim changed unexpectedly")

        self._claimed = ClaimedInput(
            inbox_id=row["inbox_id"],
            external_event_id=row["external_event_id"],
            event_type=row["event_type"],
            source=row["source"],
            received_wall_time_utc_us=row["received_wall_time_utc_us"],
            lifecycle_number=self.lifecycle_number,
        )
        return self._claimed

    def build_observation(self) -> GardenObservation:
        if self._claimed is None:
            raise WakeRejectedError("an input must be claimed before observation")
        return build_garden_observation(self.connection)

    def rollback_and_close(self) -> None:
        if self._closed:
            return
        if self.connection.in_transaction:
            self.connection.rollback()
        self.connection.close()
        self._closed = True

    def __enter__(self) -> "WakeTransaction":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.rollback_and_close()
