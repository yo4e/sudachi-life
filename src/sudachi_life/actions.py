"""Protected deterministic policy and registered seed-garden actions."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3

from .budgets import WakeBudgetLedger
from .errors import SchemaValidationError, SudachiError
from .garden import GardenObservation


class ActionRejectedError(SudachiError):
    """A registered action proposal failed validation before mutation."""


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
        inventory_update = connection.execute(
            "UPDATE inventory SET water_units = water_units - 1 "
            "WHERE singleton_id = 1 AND water_units > 0"
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
) -> None:
    """Dispatch one protected registered mutating garden action."""

    if decision.action_id == "water_plot":
        execute_water_plot(connection, decision, ledger)
        return
    if decision.action_id == "harvest_plot":
        execute_harvest_plot(connection, decision, ledger)
        return
    raise ActionRejectedError(f"unregistered Phase 1 action: {decision.action_id}")
