"""Protected deterministic policy and registered seed-garden actions."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
import sqlite3
from typing import Iterator

from .budgets import WakeBudgetLedger
from .errors import SchemaValidationError, SudachiError
from .garden import GardenObservation


class ActionRejectedError(SudachiError):
    """A registered action proposal failed validation before mutation."""


class ProtectedAuthorityViolationError(SudachiError):
    """Organism action SQL attempted to exceed its protected authority."""


@dataclass(frozen=True, slots=True)
class ProtectedActionFailure:
    action_id: str
    action_version: int
    plot_id: str
    reason: str
    injection_point: str

    def as_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "action_version": self.action_version,
            "parameters": {"plot_id": self.plot_id},
            "reason": self.reason,
            "injection_point": self.injection_point,
            "success": False,
        }


class InjectedActionFailure(SudachiError):
    """A protected administrative fixture injected one classified action failure."""

    def __init__(self, failure: ProtectedActionFailure) -> None:
        super().__init__(failure.reason)
        self.failure = failure


@dataclass(frozen=True, slots=True)
class GardenActionDecision:
    action_id: str
    action_version: int
    plot_id: str
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "decision_type": "action",
            "action_id": self.action_id,
            "action_version": self.action_version,
            "parameters": {"plot_id": self.plot_id},
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class GardenAbstention:
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "decision_type": "abstention",
            "reason": self.reason,
        }


GardenDecision = GardenActionDecision | GardenAbstention


_ACTION_READ_TABLES = frozenset(
    {
        "action_definition",
        "garden_plot",
        "inventory",
        "environment_state",
    }
)

_ACTION_UPDATE_COLUMNS = {
    "water_plot": frozenset(
        {
            ("garden_plot", "moisture"),
            ("inventory", "water_units"),
            ("environment_state", "environment_step"),
        }
    ),
    "harvest_plot": frozenset(
        {
            ("garden_plot", "fruit"),
            ("inventory", "harvested_fruit"),
            ("environment_state", "environment_step"),
        }
    ),
}

_AUTHORIZER_ACTION_NAMES = {
    sqlite3.SQLITE_CREATE_INDEX: "CREATE_INDEX",
    sqlite3.SQLITE_CREATE_TABLE: "CREATE_TABLE",
    sqlite3.SQLITE_CREATE_TEMP_INDEX: "CREATE_TEMP_INDEX",
    sqlite3.SQLITE_CREATE_TEMP_TABLE: "CREATE_TEMP_TABLE",
    sqlite3.SQLITE_CREATE_TEMP_TRIGGER: "CREATE_TEMP_TRIGGER",
    sqlite3.SQLITE_CREATE_TEMP_VIEW: "CREATE_TEMP_VIEW",
    sqlite3.SQLITE_CREATE_TRIGGER: "CREATE_TRIGGER",
    sqlite3.SQLITE_CREATE_VIEW: "CREATE_VIEW",
    sqlite3.SQLITE_DELETE: "DELETE",
    sqlite3.SQLITE_DROP_INDEX: "DROP_INDEX",
    sqlite3.SQLITE_DROP_TABLE: "DROP_TABLE",
    sqlite3.SQLITE_DROP_TEMP_INDEX: "DROP_TEMP_INDEX",
    sqlite3.SQLITE_DROP_TEMP_TABLE: "DROP_TEMP_TABLE",
    sqlite3.SQLITE_DROP_TEMP_TRIGGER: "DROP_TEMP_TRIGGER",
    sqlite3.SQLITE_DROP_TEMP_VIEW: "DROP_TEMP_VIEW",
    sqlite3.SQLITE_DROP_TRIGGER: "DROP_TRIGGER",
    sqlite3.SQLITE_DROP_VIEW: "DROP_VIEW",
    sqlite3.SQLITE_INSERT: "INSERT",
    sqlite3.SQLITE_PRAGMA: "PRAGMA",
    sqlite3.SQLITE_READ: "READ",
    sqlite3.SQLITE_SELECT: "SELECT",
    sqlite3.SQLITE_TRANSACTION: "TRANSACTION",
    sqlite3.SQLITE_UPDATE: "UPDATE",
    sqlite3.SQLITE_ATTACH: "ATTACH",
    sqlite3.SQLITE_DETACH: "DETACH",
    sqlite3.SQLITE_ALTER_TABLE: "ALTER_TABLE",
    sqlite3.SQLITE_REINDEX: "REINDEX",
    sqlite3.SQLITE_ANALYZE: "ANALYZE",
    sqlite3.SQLITE_CREATE_VTABLE: "CREATE_VTABLE",
    sqlite3.SQLITE_DROP_VTABLE: "DROP_VTABLE",
    sqlite3.SQLITE_FUNCTION: "FUNCTION",
    sqlite3.SQLITE_SAVEPOINT: "SAVEPOINT",
    sqlite3.SQLITE_RECURSIVE: "RECURSIVE",
}


@dataclass(slots=True)
class _ActionSqlAuthority:
    decision: GardenActionDecision
    violation: tuple[int, str | None, str | None, str | None, str | None] | None = None

    def authorize(
        self,
        action_code: int,
        first_argument: str | None,
        second_argument: str | None,
        database_name: str | None,
        trigger_name: str | None,
    ) -> int:
        if action_code == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK

        if action_code == sqlite3.SQLITE_READ:
            if database_name == "main" and first_argument in _ACTION_READ_TABLES:
                return sqlite3.SQLITE_OK

        elif action_code == sqlite3.SQLITE_UPDATE:
            allowed_updates = _ACTION_UPDATE_COLUMNS.get(
                self.decision.action_id, frozenset()
            )
            if (
                database_name == "main"
                and (first_argument, second_argument) in allowed_updates
            ):
                return sqlite3.SQLITE_OK

        elif action_code == sqlite3.SQLITE_SAVEPOINT:
            if (
                first_argument in {"BEGIN", "RELEASE", "ROLLBACK"}
                and second_argument == "garden_action"
            ):
                return sqlite3.SQLITE_OK

        if self.violation is None:
            self.violation = (
                action_code,
                first_argument,
                second_argument,
                database_name,
                trigger_name,
            )
        return sqlite3.SQLITE_DENY

    def violation_message(self) -> str:
        if self.violation is None:
            return "protected action SQL authority denied an unknown operation"
        action_code, first, second, database, trigger = self.violation
        operation = _AUTHORIZER_ACTION_NAMES.get(action_code, f"CODE_{action_code}")
        target_parts = [part for part in (database, first, second) if part]
        target = ".".join(target_parts) if target_parts else "<unspecified>"
        suffix = f" through trigger {trigger}" if trigger else ""
        return (
            f"protected action SQL authority denied {operation} on {target}{suffix}"
        )


@contextmanager
def _protected_action_sql_authority(
    connection: sqlite3.Connection,
    decision: GardenActionDecision,
) -> Iterator[None]:
    authority = _ActionSqlAuthority(decision)
    connection.set_authorizer(authority.authorize)
    try:
        try:
            yield
        except sqlite3.DatabaseError as exc:
            if authority.violation is not None:
                raise ProtectedAuthorityViolationError(
                    authority.violation_message()
                ) from exc
            raise
        if authority.violation is not None:
            raise ProtectedAuthorityViolationError(authority.violation_message())
    finally:
        connection.set_authorizer(None)


def _observed_action(observation: GardenObservation, action_id: str) -> dict[str, object]:
    action = next(
        (candidate for candidate in observation.actions if candidate["action_id"] == action_id),
        None,
    )
    if action is None:
        raise ActionRejectedError(f"protected {action_id} observation metadata is missing")
    return action


def select_garden_decision(observation: GardenObservation) -> GardenDecision:
    """Apply the fixed Phase 1 policy for water, harvest, then abstention."""

    if observation.objective_complete:
        return GardenAbstention(reason="objective_already_complete")

    water = _observed_action(observation, "water_plot")
    water_targets = tuple(water["applicable_targets"])
    if water_targets:
        return GardenActionDecision(
            action_id="water_plot",
            action_version=int(water["version"]),
            plot_id=str(water_targets[0]),
            reason="fixed_policy_first_executable_dry_plot",
        )

    harvest = _observed_action(observation, "harvest_plot")
    harvest_targets = tuple(harvest["applicable_targets"])
    if harvest_targets:
        return GardenActionDecision(
            action_id="harvest_plot",
            action_version=int(harvest["version"]),
            plot_id=str(harvest_targets[0]),
            reason="fixed_policy_first_executable_harvest",
        )

    return GardenAbstention(reason="no_applicable_action")


def select_first_water_decision(observation: GardenObservation) -> GardenActionDecision:
    """Compatibility name for the Slice 3 first-state policy assertion."""

    decision = select_garden_decision(observation)
    if not isinstance(decision, GardenActionDecision) or decision.action_id != "water_plot":
        raise ActionRejectedError("canonical first wake did not select water_plot")
    return decision


def _validate_definition(
    connection: sqlite3.Connection,
    decision: GardenActionDecision,
) -> None:
    definition = connection.execute(
        "SELECT version, deterministic, protected FROM action_definition WHERE action_id = ?",
        (decision.action_id,),
    ).fetchone()
    if (
        definition is None
        or definition["version"] != decision.action_version
        or definition["deterministic"] != 1
        or definition["protected"] != 1
    ):
        raise ActionRejectedError(
            f"{decision.action_id} is not a valid protected action definition"
        )


def execute_water_plot(
    connection: sqlite3.Connection,
    decision: GardenActionDecision,
    ledger: WakeBudgetLedger,
    *,
    protected_test_failure_after_plot_write: bool = False,
) -> None:
    """Validate, reserve, and execute one water transition inside a savepoint."""

    ledger.consume("action_attempts")
    _validate_definition(connection, decision)
    if decision.action_id != "water_plot":
        raise ActionRejectedError("water executor received a different action")

    plot = connection.execute(
        "SELECT stage, moisture FROM garden_plot WHERE plot_id = ?",
        (decision.plot_id,),
    ).fetchone()
    inventory = connection.execute(
        "SELECT water_units FROM inventory WHERE singleton_id = 1"
    ).fetchone()
    if plot is None:
        raise ActionRejectedError("water_plot target does not exist")
    if plot["stage"] not in {"sprout", "mature"}:
        raise ActionRejectedError("water_plot target is not living")
    if plot["moisture"] != 0:
        raise ActionRejectedError("water_plot target is not dry")
    if inventory is None or inventory["water_units"] < 1:
        raise ActionRejectedError("water_plot has insufficient water")

    ledger.consume("environment_mutations")
    connection.execute("SAVEPOINT garden_action")
    try:
        plot_update = connection.execute(
            "UPDATE garden_plot SET moisture = 1 WHERE plot_id = ? AND moisture = 0",
            (decision.plot_id,),
        )
        if plot_update.rowcount != 1:
            raise SchemaValidationError(
                "water_plot partial transition changed an unexpected row count"
            )
        if protected_test_failure_after_plot_write:
            raise InjectedActionFailure(
                ProtectedActionFailure(
                    action_id=decision.action_id,
                    action_version=decision.action_version,
                    plot_id=decision.plot_id,
                    reason="protected_test_injected_action_failure",
                    injection_point="after_plot_write",
                )
            )
        inventory_update = connection.execute(
            "UPDATE inventory SET water_units = water_units - 1 "
            "WHERE singleton_id = 1 AND water_units > 0"
        )
        environment_update = connection.execute(
            "UPDATE environment_state SET environment_step = environment_step + 1 "
            "WHERE singleton_id = 1"
        )
        if inventory_update.rowcount != 1 or environment_update.rowcount != 1:
            raise SchemaValidationError("water_plot transition changed an unexpected row count")
        connection.execute("RELEASE SAVEPOINT garden_action")
    except Exception:
        connection.execute("ROLLBACK TO SAVEPOINT garden_action")
        connection.execute("RELEASE SAVEPOINT garden_action")
        ledger.release("environment_mutations")
        raise


def execute_harvest_plot(
    connection: sqlite3.Connection,
    decision: GardenActionDecision,
    ledger: WakeBudgetLedger,
) -> None:
    """Validate, reserve, and execute one harvest transition inside a savepoint."""

    ledger.consume("action_attempts")
    _validate_definition(connection, decision)
    if decision.action_id != "harvest_plot":
        raise ActionRejectedError("harvest executor received a different action")

    plot = connection.execute(
        "SELECT stage, fruit FROM garden_plot WHERE plot_id = ?",
        (decision.plot_id,),
    ).fetchone()
    if plot is None:
        raise ActionRejectedError("harvest_plot target does not exist")
    if plot["stage"] != "mature":
        raise ActionRejectedError("harvest_plot target is not mature")
    if plot["fruit"] < 1:
        raise ActionRejectedError("harvest_plot target has no fruit")

    ledger.consume("environment_mutations")
    connection.execute("SAVEPOINT garden_action")
    try:
        plot_update = connection.execute(
            "UPDATE garden_plot SET fruit = fruit - 1 "
            "WHERE plot_id = ? AND stage = 'mature' AND fruit > 0",
            (decision.plot_id,),
        )
        inventory_update = connection.execute(
            "UPDATE inventory SET harvested_fruit = harvested_fruit + 1 "
            "WHERE singleton_id = 1"
        )
        environment_update = connection.execute(
            "UPDATE environment_state SET environment_step = environment_step + 1 "
            "WHERE singleton_id = 1"
        )
        if (
            plot_update.rowcount != 1
            or inventory_update.rowcount != 1
            or environment_update.rowcount != 1
        ):
            raise SchemaValidationError(
                "harvest_plot transition changed an unexpected row count"
            )
        connection.execute("RELEASE SAVEPOINT garden_action")
    except Exception:
        connection.execute("ROLLBACK TO SAVEPOINT garden_action")
        connection.execute("RELEASE SAVEPOINT garden_action")
        ledger.release("environment_mutations")
        raise


def execute_garden_action(
    connection: sqlite3.Connection,
    decision: GardenActionDecision,
    ledger: WakeBudgetLedger,
    *,
    protected_test_failure_after_plot_write: bool = False,
) -> None:
    """Dispatch one protected registered mutating garden action."""

    if protected_test_failure_after_plot_write and decision.action_id != "water_plot":
        raise SchemaValidationError(
            "protected action-failure injection requires water_plot"
        )
    if decision.action_id not in _ACTION_UPDATE_COLUMNS:
        raise ActionRejectedError(f"unregistered Phase 1 action: {decision.action_id}")

    with _protected_action_sql_authority(connection, decision):
        if decision.action_id == "water_plot":
            execute_water_plot(
                connection,
                decision,
                ledger,
                protected_test_failure_after_plot_write=protected_test_failure_after_plot_write,
            )
            return
        if decision.action_id == "harvest_plot":
            execute_harvest_plot(connection, decision, ledger)
            return

    raise ActionRejectedError(f"unregistered Phase 1 action: {decision.action_id}")
