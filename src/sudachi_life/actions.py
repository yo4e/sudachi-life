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
class GardenDecision:
    action_id: str
    action_version: int
    plot_id: str
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "action_version": self.action_version,
            "parameters": {"plot_id": self.plot_id},
            "reason": self.reason,
        }


def select_first_water_decision(observation: GardenObservation) -> GardenDecision:
    """Apply the fixed policy, restricted to Slice 3's canonical first action."""

    if observation.objective_complete:
        raise ActionRejectedError("Slice 3 does not implement objective-complete abstention")
    water = next(
        (action for action in observation.actions if action["action_id"] == "water_plot"),
        None,
    )
    if water is None:
        raise ActionRejectedError("protected water_plot observation metadata is missing")
    targets = tuple(water["applicable_targets"])
    if not targets:
        raise ActionRejectedError("Slice 3 requires the canonical executable water action")
    return GardenDecision(
        action_id="water_plot",
        action_version=int(water["version"]),
        plot_id=str(targets[0]),
        reason="fixed_policy_first_executable_dry_plot",
    )


def execute_water_plot(
    connection: sqlite3.Connection,
    decision: GardenDecision,
    ledger: WakeBudgetLedger,
) -> None:
    """Validate, reserve, and execute one water transition inside a savepoint."""

    ledger.consume("action_attempts")
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
        raise ActionRejectedError("water_plot is not a valid protected action definition")

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
