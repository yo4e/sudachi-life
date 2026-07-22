"""Independent protected evaluation for seed-garden transitions."""

from __future__ import annotations

from dataclasses import dataclass
import json
import sqlite3
from typing import Any

from .actions import (
    GardenAbstention,
    GardenActionDecision,
    GardenDecision,
    ProtectedActionFailure,
)
from .budgets import ProtectedBudgetExhaustion
from .constants import BUDGET_CONFIG_VERSION, PHASE1_BUDGETS
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


def evaluate_classified_action_failure(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenActionDecision,
    failure: ProtectedActionFailure,
) -> GardenEvaluation:
    """Prove that a classified failed action left no partial environment change."""

    if failure.reason != "protected_test_injected_action_failure":
        raise SchemaValidationError("unsupported classified action-failure reason")
    if failure.injection_point != "after_plot_write":
        raise SchemaValidationError("unsupported classified action-failure injection point")
    if (
        failure.action_id != decision.action_id
        or failure.action_version != decision.action_version
        or failure.plot_id != decision.plot_id
    ):
        raise SchemaValidationError("classified action failure does not match its decision")

    observed = next(
        (action for action in before.actions if action["action_id"] == decision.action_id),
        None,
    )
    if observed is None or decision.plot_id not in tuple(observed["applicable_targets"]):
        raise SchemaValidationError("classified action failure was not an executable proposal")

    after_environment, after_inventory, after_plots = _read_after_state(connection)
    before_plots = {str(plot["plot_id"]): dict(plot) for plot in before.plots}
    if after_plots != before_plots:
        raise SchemaValidationError("classified action failure left a partial plot mutation")
    if after_inventory["water_units"] != before.water_units:
        raise SchemaValidationError("classified action failure changed water inventory")
    if after_inventory["harvested_fruit"] != before.harvested_fruit:
        raise SchemaValidationError("classified action failure changed harvested inventory")
    if after_environment["environment_step"] != before.environment_step:
        raise SchemaValidationError("classified action failure changed environment step")
    objective_after = recompute_objective(connection)
    if (
        bool(after_environment["objective_complete"]) != before.objective_complete
        or objective_after != before.objective_complete
    ):
        raise SchemaValidationError("classified action failure changed objective state")

    unresolved_before = _unresolved_needs_before(before)
    unresolved_after = _unresolved_needs(connection)
    if unresolved_after != unresolved_before:
        raise SchemaValidationError("classified action failure changed unresolved needs")

    return GardenEvaluation(
        success=False,
        objective_complete_before=before.objective_complete,
        objective_complete_after=objective_after,
        unresolved_needs_before=unresolved_before,
        unresolved_needs_after=unresolved_after,
        progress="action_failed_rolled_back",
        environment_step_before=before.environment_step,
        environment_step_after=int(after_environment["environment_step"]),
    )


def evaluate_classified_budget_exhaustion(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenDecision,
    exhaustion: ProtectedBudgetExhaustion,
) -> GardenEvaluation:
    """Prove a typed lifecycle deadline exhaustion preceded all mutation."""

    if exhaustion.budget_name != "lifecycle_wall_time_ms":
        raise SchemaValidationError("unsupported classified budget-exhaustion name")
    if exhaustion.reason != "lifecycle_wall_time_exhausted_before_action":
        raise SchemaValidationError("unsupported classified budget-exhaustion reason")
    if exhaustion.attempted_forbidden_operation != "execute_garden_action":
        raise SchemaValidationError("unsupported forbidden operation for budget exhaustion")
    if exhaustion.state_mutation_occurred:
        raise SchemaValidationError("budget exhaustion claims an environment mutation occurred")
    if exhaustion.environment_step != before.environment_step:
        raise SchemaValidationError("budget exhaustion references the wrong environment boundary")
    if exhaustion.configured_initial_value <= 0:
        raise SchemaValidationError("budget exhaustion has an invalid configured limit")
    if exhaustion.unit != "ms":
        raise SchemaValidationError("budget exhaustion uses an unsupported unit")
    if exhaustion.consumed_amount <= exhaustion.configured_initial_value:
        raise SchemaValidationError("budget exhaustion did not exceed its configured limit")
    if exhaustion.remaining_amount != 0:
        raise SchemaValidationError("budget exhaustion has invalid remaining capacity")
    if exhaustion.observed_elapsed_monotonic_ns <= (
        exhaustion.configured_initial_value * 1_000_000
    ):
        raise SchemaValidationError("budget exhaustion elapsed time did not exceed the limit")

    budget_row = connection.execute(
        "SELECT config_version, config_json FROM budget_config WHERE singleton_id = 1"
    ).fetchone()
    if budget_row is None or budget_row["config_version"] != BUDGET_CONFIG_VERSION:
        raise SchemaValidationError("budget exhaustion cannot verify protected configuration")
    try:
        protected_config = json.loads(budget_row["config_json"])
    except json.JSONDecodeError as exc:
        raise SchemaValidationError(
            "budget exhaustion found invalid protected configuration JSON"
        ) from exc
    if protected_config != PHASE1_BUDGETS.as_dict():
        raise SchemaValidationError(
            "budget exhaustion observed a changed protected configuration"
        )
    if exhaustion.configured_initial_value != int(
        protected_config["lifecycle_wall_time_ms"]
    ):
        raise SchemaValidationError(
            "budget exhaustion limit does not match protected configuration"
        )

    if not isinstance(decision, GardenActionDecision):
        raise SchemaValidationError("Slice 9 budget exhaustion requires a mutating decision")
    observed = next(
        (action for action in before.actions if action["action_id"] == decision.action_id),
        None,
    )
    if observed is None or decision.plot_id not in tuple(observed["applicable_targets"]):
        raise SchemaValidationError("budget exhaustion did not block an executable proposal")

    after_environment, after_inventory, after_plots = _read_after_state(connection)
    before_plots = {str(plot["plot_id"]): dict(plot) for plot in before.plots}
    if after_plots != before_plots:
        raise SchemaValidationError("budget exhaustion changed garden plots")
    if after_inventory["water_units"] != before.water_units:
        raise SchemaValidationError("budget exhaustion changed water inventory")
    if after_inventory["harvested_fruit"] != before.harvested_fruit:
        raise SchemaValidationError("budget exhaustion changed harvested inventory")
    if after_environment["environment_step"] != before.environment_step:
        raise SchemaValidationError("budget exhaustion changed environment step")
    objective_after = recompute_objective(connection)
    if (
        bool(after_environment["objective_complete"]) != before.objective_complete
        or objective_after != before.objective_complete
    ):
        raise SchemaValidationError("budget exhaustion changed objective state")

    unresolved_before = _unresolved_needs_before(before)
    unresolved_after = _unresolved_needs(connection)
    if unresolved_after != unresolved_before:
        raise SchemaValidationError("budget exhaustion changed unresolved needs")

    return GardenEvaluation(
        success=False,
        objective_complete_before=before.objective_complete,
        objective_complete_after=objective_after,
        unresolved_needs_before=unresolved_before,
        unresolved_needs_after=unresolved_after,
        progress="budget_exhausted_before_action",
        environment_step_before=before.environment_step,
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


def evaluate_no_applicable_action_abstention(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenAbstention,
) -> GardenEvaluation:
    """Prove an incomplete garden has no executable mutation and remains unchanged."""

    if decision.reason != "no_applicable_action":
        raise SchemaValidationError("unsupported protected abstention reason")
    if before.objective_complete:
        raise SchemaValidationError(
            "no_applicable_action abstention requires an incomplete observation"
        )

    after_environment, after_inventory, after_plots = _read_after_state(connection)
    before_plots = {str(plot["plot_id"]): dict(plot) for plot in before.plots}
    if after_plots != before_plots:
        raise SchemaValidationError("no-applicable-action abstention changed garden plots")
    if after_inventory["water_units"] != before.water_units:
        raise SchemaValidationError("no-applicable-action abstention changed water inventory")
    if after_inventory["harvested_fruit"] != before.harvested_fruit:
        raise SchemaValidationError("no-applicable-action abstention changed harvested fruit")
    if after_environment["environment_step"] != before.environment_step:
        raise SchemaValidationError("no-applicable-action abstention changed environment step")
    if after_environment["objective_complete"] != 0 or recompute_objective(connection):
        raise SchemaValidationError(
            "no-applicable-action abstention did not preserve an incomplete objective"
        )

    executable_water = any(
        plot["stage"] in {"sprout", "mature"}
        and plot["moisture"] == 0
        and after_inventory["water_units"] > 0
        for plot in after_plots.values()
    )
    executable_harvest = any(
        plot["stage"] == "mature" and plot["fruit"] > 0
        for plot in after_plots.values()
    )
    if executable_water or executable_harvest:
        raise SchemaValidationError(
            "no-applicable-action abstention ignored an executable protected action"
        )

    unresolved_before = _unresolved_needs_before(before)
    unresolved_after = _unresolved_needs(connection)
    if unresolved_before <= 0 or unresolved_after != unresolved_before:
        raise SchemaValidationError(
            "no-applicable-action abstention did not preserve the blocked need state"
        )

    return GardenEvaluation(
        success=False,
        objective_complete_before=False,
        objective_complete_after=False,
        unresolved_needs_before=unresolved_before,
        unresolved_needs_after=unresolved_after,
        progress="blocked_no_applicable_action",
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
        if decision.reason == "objective_already_complete":
            return evaluate_objective_complete_abstention(connection, before, decision)
        if decision.reason == "no_applicable_action":
            return evaluate_no_applicable_action_abstention(connection, before, decision)
        raise SchemaValidationError(
            f"no protected evaluator for abstention reason {decision.reason}"
        )
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
