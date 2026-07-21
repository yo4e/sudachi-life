"""Independent protected evaluation for seed-garden transitions."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Any

from .actions import GardenDecision
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


def evaluate_water_transition(
    connection: sqlite3.Connection,
    before: GardenObservation,
    decision: GardenDecision,
) -> GardenEvaluation:
    """Re-read canonical state and independently prove the exact water transition."""

    after_environment = connection.execute(
        "SELECT environment_step FROM environment_state WHERE singleton_id = 1"
    ).fetchone()
    after_inventory = connection.execute(
        "SELECT water_units, harvested_fruit FROM inventory WHERE singleton_id = 1"
    ).fetchone()
    after_plots = {
        row["plot_id"]: dict(row)
        for row in connection.execute(
            "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id"
        ).fetchall()
    }
    before_plots = {str(plot["plot_id"]): dict(plot) for plot in before.plots}
    if after_environment is None or after_inventory is None:
        raise SchemaValidationError("garden evaluation cannot read canonical state")
    if set(after_plots) != set(before_plots):
        raise SchemaValidationError("water_plot changed the protected plot set")

    for plot_id, prior in before_plots.items():
        current = after_plots[plot_id]
        expected = dict(prior)
        if plot_id == decision.plot_id:
            expected["moisture"] = 1
        if current != expected:
            raise SchemaValidationError(
                f"water_plot produced an invalid transition for {plot_id}"
            )

    if after_inventory["water_units"] != before.water_units - 1:
        raise SchemaValidationError("water_plot did not consume exactly one water unit")
    if after_inventory["harvested_fruit"] != before.harvested_fruit:
        raise SchemaValidationError("water_plot changed harvested fruit")
    if after_environment["environment_step"] != before.environment_step + 1:
        raise SchemaValidationError("water_plot did not advance exactly one environment step")

    objective_after = recompute_objective(connection)
    connection.execute(
        "UPDATE environment_state SET objective_complete = ? WHERE singleton_id = 1",
        (int(objective_after),),
    )
    before_harvestable = sum(1 for plot in before.plots if plot["fruit"] > 0)
    unresolved_before = sum(
        1
        for plot in before.plots
        if plot["stage"] in {"sprout", "mature"} and plot["moisture"] == 0
    ) + before_harvestable + (
        1 if before.harvested_fruit < 1 and before_harvestable == 0 else 0
    )
    unresolved_after = _unresolved_needs(connection)
    if unresolved_after >= unresolved_before:
        raise SchemaValidationError("successful water_plot did not reduce unresolved needs")

    return GardenEvaluation(
        success=True,
        objective_complete_before=before.objective_complete,
        objective_complete_after=objective_after,
        unresolved_needs_before=unresolved_before,
        unresolved_needs_after=unresolved_after,
        progress="positive",
        environment_step_before=before.environment_step,
        environment_step_after=int(after_environment["environment_step"]),
    )
