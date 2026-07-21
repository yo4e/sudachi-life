"""Deterministic full observation of seed-garden-v1."""

from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Any

from .constants import ENVIRONMENT_VERSION
from .errors import SchemaValidationError


@dataclass(frozen=True, slots=True)
class GardenObservation:
    environment_version: str
    environment_step: int
    objective_complete: bool
    water_units: int
    harvested_fruit: int
    plots: tuple[dict[str, Any], ...]
    actions: tuple[dict[str, Any], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "environment_version": self.environment_version,
            "environment_step": self.environment_step,
            "objective_complete": self.objective_complete,
            "inventory": {
                "water_units": self.water_units,
                "harvested_fruit": self.harvested_fruit,
            },
            "plots": [dict(plot) for plot in self.plots],
            "actions": [
                {
                    "action_id": action["action_id"],
                    "version": action["version"],
                    "preconditions": list(action["preconditions"]),
                    "applicable_targets": list(action["applicable_targets"]),
                }
                for action in self.actions
            ],
        }


def build_garden_observation(connection: sqlite3.Connection) -> GardenObservation:
    environment = connection.execute(
        "SELECT environment_version, environment_step, objective_complete "
        "FROM environment_state WHERE singleton_id = 1"
    ).fetchone()
    if environment is None or environment["environment_version"] != ENVIRONMENT_VERSION:
        raise SchemaValidationError("seed-garden-v1 environment state is missing or invalid")

    inventory = connection.execute(
        "SELECT water_units, harvested_fruit FROM inventory WHERE singleton_id = 1"
    ).fetchone()
    if inventory is None:
        raise SchemaValidationError("seed-garden-v1 inventory is missing")

    plots = tuple(
        dict(row)
        for row in connection.execute(
            "SELECT plot_id, stage, moisture, fruit FROM garden_plot ORDER BY plot_id"
        ).fetchall()
    )
    if not plots:
        raise SchemaValidationError("seed-garden-v1 has no plots")

    water_targets = tuple(
        plot["plot_id"]
        for plot in plots
        if plot["stage"] in {"sprout", "mature"}
        and plot["moisture"] == 0
        and inventory["water_units"] > 0
    )
    harvest_targets = tuple(
        plot["plot_id"]
        for plot in plots
        if plot["stage"] == "mature" and plot["fruit"] > 0
    )

    actions = (
        {
            "action_id": "water_plot",
            "version": 1,
            "preconditions": (
                "plot_exists",
                "living_stage",
                "moisture_is_zero",
                "water_unit_available",
                "action_and_mutation_budget_available",
            ),
            "applicable_targets": water_targets,
        },
        {
            "action_id": "harvest_plot",
            "version": 1,
            "preconditions": (
                "plot_exists",
                "stage_is_mature",
                "fruit_is_positive",
                "action_and_mutation_budget_available",
            ),
            "applicable_targets": harvest_targets,
        },
    )
    return GardenObservation(
        environment_version=environment["environment_version"],
        environment_step=environment["environment_step"],
        objective_complete=bool(environment["objective_complete"]),
        water_units=inventory["water_units"],
        harvested_fruit=inventory["harvested_fruit"],
        plots=plots,
        actions=actions,
    )
