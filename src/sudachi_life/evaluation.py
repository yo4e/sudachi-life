"""Independent protected evaluation for seed-garden transitions."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Any

from .actions import GardenAbstention, GardenActionDecision, GardenDecision
from .errors import SchemaValidationError
from .garden import GardenObservation


@dataclass(frozen=True, slots=True)
class GardenEvaluation:
    success: bool
    objective_complete_before: bool
    objective_complete_after: bool
    unresolved_needs_before: int
    unresolved_needs_after: int
    progress: str
    environment_step_before: int
    environment_step_after: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "objective_complete_before": self.objective_complete_before,
            "objective_complete_after": self.objective_complete_after,
            "unresolved_needs_before": self.unresolved_needs_before,
            "unresolved_needs_after": self.unresolved_needs_after,
            "progress": self.progress,
            "environment_step_before": self.environment_step_before,
            "environment_step_after": self.environment_step_after,
        }


def _unresolved_needs(connection: sqlite3.Connection) -> int:
    dry_living = connection.execute(
        "SELECT COUNT(*) FROM garden_plot "
        "WHERE stage IN ('sprout', 'mature') AND moisture = 0"
    ).fetchone()[0]
    harvestable = connection.execute(
        "SELECT COUNT(*) FROM garden_plot WHERE fruit > 0"
    ).fetchone()[0]
    harvested = connection.execute(
        "SELECT harvested_fruit FROM inventory WHERE singleton_id = 1"
    ).fetchone()[0]
    missing_harvest = 1 if harvested < 1 and harvestable == 0 else 0
    return int(dry_living) + int(harvestable) + missing_harvest


def _unresolved_needs_before(observation: GardenObservation) -> int:
    dry_living = sum(
        1
        for plot in observation.plots
        if plot["stage"] in {"sprout", "mature"} and plot["moisture"] == 0
    )
    harvestable = sum(1 for plot in observation.plots if plot["fruit"] > 0)
    missing_harvest = (
        1 if observation.harvested_fruit < 1 and harvestable == 0 else 0
    )
    return dry_living + harvestable + missing_harvest


def recompute_objective(connection: sqlite3.Connection) -> bool:
    dry_living = connection.execute(
        "SELECT COUNT(*) FROM garden_plot "
        "WHERE stage IN ('sprout', 'mature') AND moisture = 0"
    ).fetchone()[0]
    harvestable = connection.execute(
        "SELECT COUNT(*) FROM garden_plot WHERE fruit > 0"
    ).fetchone()[0]
    harvested = connection.execute(
        "SELECT harvested_fruit FROM inventory WHERE singleton_id = 1"
    ).fetchone()[0]
    return dry_living == 0 and harvestable == 0 and harvested >= 1


def _read_after_state(connection: sqlite3.Connection):
    environment = connection.execute(
        "SELECT environment_step, objective_complete "
        "FROM environment_state WHERE singleton_id = 1"
    ).fetchone()
    inventory = connection.execute(
        "SELECT water_units, harvested_fruit FROM inventory WHERE singleton_id = 1"
    ).fetchone()
    plots = {
        row["plot_id"]: dict(row)
        for row in connection.execute(
            "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id"
        ).fetchall()
    }
    if environment is None or inventory is None:
        raise SchemaValidationError("garden evaluation cannot read canonical state")
    return environment, inventory, plots


def _finish_action_evaluation(
    connection: sqlite3.Connection,
    before: GardenObservation,
    *,
    environment_step_after: int,
) -> GardenEvaluation:
    objective_after = recompute_objective(connection)
    connection.execute(
        "UPDATE environment_state SET objective_complete = ? WHERE singleton_id = 1",
        (int(objective_after),),
    )
    unresolved_before = _unresolved_needs_before(before)
    unresolved_after = _unresolved_needs(connection)
    if unresolved_after >= unresolved_before:
        raise SchemaValidationError(
            "successful garden action did not reduce unresolved needs"
        )
    return GardenEvaluation(
        success=True,
        objective_complete_before=before.objective_complete,
        objective_complete_after=objective_after,
        unresolved_needs_before=unresolved_before,
        unresolved_needs_after=unresolved_after,
        progress="positive",
        environment_step_before=before.environment_step,
        environment_step_after=environment_step_after,
    )


def evaluate_water_transition(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenActionDecision,
) -> GardenEvaluation:
    """Re-read canonical state and independently prove the exact water transition."""

    after_environment, after_inventory, after_plots = _read_after_state(connection)
    before_plots = {str(plot["plot_id"]): dict(plot) for plot in before.plots}
    if set(after_plots) != set(before_plots):
        raise SchemaValidationError("water_plot changed the protected plot set")

    for plot_id, prior in before_plots.items():
        expected = dict(prior)
        if plot_id == decision.plot_id:
            expected["moisture"] = 1
        if after_plots[plot_id] != expected:
            raise SchemaValidationError(
                f"water_plot produced an invalid transition for {plot_id}"
            )

    if after_inventory["water_units"] != before.water_units - 1:
        raise SchemaValidationError("water_plot did not consume exactly one water unit")
    if after_inventory["harvested_fruit"] != before.harvested_fruit:
        raise SchemaValidationError("water_plot changed harvested fruit")
    if after_environment["environment_step"] != before.environment_step + 1:
        raise SchemaValidationError("water_plot did not advance exactly one environment step")

    return _finish_action_evaluation(
        connection,
        before,
        environment_step_after=int(after_environment["environment_step"]),
    )


def evaluate_harvest_transition(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenActionDecision,
) -> GardenEvaluation:
    """Re-read canonical state and independently prove the exact harvest transition."""

    after_environment, after_inventory, after_plots = _read_after_state(connection)
    before_plots = {str(plot["plot_id"]): dict(plot) for plot in before.plots}
    if set(after_plots) != set(before_plots):
        raise SchemaValidationError("harvest_plot changed the protected plot set")

    for plot_id, prior in before_plots.items():
        expected = dict(prior)
        if plot_id == decision.plot_id:
            if prior["stage"] != "mature" or prior["fruit"] < 1:
                raise SchemaValidationError(
                    "harvest_plot evaluation received an invalid prior target"
                )
            expected["fruit"] = prior["fruit"] - 1
        if after_plots[plot_id] != expected:
            raise SchemaValidationError(
                f"harvest_plot produced an invalid transition for {plot_id}"
            )

    if after_inventory["water_units"] != before.water_units:
        raise SchemaValidationError("harvest_plot changed water inventory")
    if after_inventory["harvested_fruit"] != before.harvested_fruit + 1:
        raise SchemaValidationError(
            "harvest_plot did not add exactly one harvested fruit"
        )
    if after_environment["environment_step"] != before.environment_step + 1:
        raise SchemaValidationError(
            "harvest_plot did not advance exactly one environment step"
        )

    return _finish_action_evaluation(
        connection,
        before,
        environment_step_after=int(after_environment["environment_step"]),
    )


def evaluate_objective_complete_abstention(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenAbstention,
) -> GardenEvaluation:
    """Prove that justified completion abstention leaves canonical environment unchanged."""

    if decision.reason != "objective_already_complete":
        raise SchemaValidationError("unsupported protected abstention reason")
    if not before.objective_complete:
        raise SchemaValidationError(
            "objective_already_complete abstention requires a complete observation"
        )

    after_environment, after_inventory, after_plots = _read_after_state(connection)
    before_plots = {str(plot["plot_id"]): dict(plot) for plot in before.plots}
    if after_plots != before_plots:
        raise SchemaValidationError("objective-complete abstention changed garden plots")
    if after_inventory["water_units"] != before.water_units:
        raise SchemaValidationError("objective-complete abstention changed water inventory")
    if after_inventory["harvested_fruit"] != before.harvested_fruit:
        raise SchemaValidationError("objective-complete abstention changed harvested fruit")
    if after_environment["environment_step"] != before.environment_step:
        raise SchemaValidationError("objective-complete abstention changed environment step")
    if after_environment["objective_complete"] != 1 or not recompute_objective(connection):
        raise SchemaValidationError(
            "objective-complete abstention could not independently verify completion"
        )

    unresolved_before = _unresolved_needs_before(before)
    unresolved_after = _unresolved_needs(connection)
    if unresolved_before != 0 or unresolved_after != 0:
        raise SchemaValidationError(
            "objective-complete abstention observed unresolved garden needs"
        )

    return GardenEvaluation(
        success=True,
        objective_complete_before=True,
        objective_complete_after=True,
        unresolved_needs_before=0,
        unresolved_needs_after=0,
        progress="objective_complete_unchanged",
        environment_step_before=before.environment_step,
        environment_step_after=int(after_environment["environment_step"]),
    )


def evaluate_garden_decision(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenDecision,
) -> GardenEvaluation:
    """Dispatch the protected evaluator independently of executor claims."""

    if isinstance(decision, GardenAbstention):
        return evaluate_objective_complete_abstention(connection, before, decision)
    if decision.action_id == "water_plot":
        return evaluate_water_transition(connection, before, decision)
    if decision.action_id == "harvest_plot":
        return evaluate_harvest_transition(connection, before, decision)
    raise SchemaValidationError(f"no protected evaluator for {decision.action_id}")


def evaluate_garden_transition(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenActionDecision,
) -> GardenEvaluation:
    """Compatibility entry point for mutating-action evaluation."""

    return evaluate_garden_decision(connection, before, decision)
