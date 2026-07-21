"""Protected per-wake budget accounting for Contract v0.2."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import sqlite3
from typing import Any

from .constants import BUDGET_CONFIG_VERSION, PHASE1_BUDGETS
from .errors import SchemaValidationError, SudachiError


class BudgetExhaustedError(SudachiError):
    """A protected per-wake budget would be exceeded."""


_DECISION_BUDGETS = (
    "input_events",
    "observations",
    "action_attempts",
    "environment_mutations",
    "caregiver_consultations",
    "network_calls",
    "subprocess_calls",
    "external_mutable_writes",
)


@dataclass(slots=True)
class WakeBudgetLedger:
    """One non-rechargeable budget vector for an accepted wake."""

    config_version: str
    limits: dict[str, int]
    consumed: dict[str, int] = field(default_factory=dict)
    semantic_steps_used: int = 0
    canonical_records_used: int = 0
    elapsed_monotonic_ns: int = 0

    @classmethod
    def load(cls, connection: sqlite3.Connection) -> "WakeBudgetLedger":
        row = connection.execute(
            "SELECT config_version, config_json FROM budget_config WHERE singleton_id = 1"
        ).fetchone()
        if row is None or row["config_version"] != BUDGET_CONFIG_VERSION:
            raise SchemaValidationError("protected budget configuration is missing")
        try:
            limits = json.loads(row["config_json"])
        except json.JSONDecodeError as exc:
            raise SchemaValidationError("protected budget configuration is invalid JSON") from exc
        if limits != PHASE1_BUDGETS.as_dict():
            raise SchemaValidationError("protected budget configuration does not match Contract v0.2")
        return cls(
            config_version=row["config_version"],
            limits=limits,
            consumed={name: 0 for name in _DECISION_BUDGETS},
        )

    def consume(self, name: str, amount: int = 1) -> None:
        if name not in self.consumed:
            raise SchemaValidationError(f"unknown per-wake budget: {name}")
        if amount < 0:
            raise SchemaValidationError("budget consumption may not be negative")
        used = self.consumed[name]
        limit = int(self.limits[name])
        if used + amount > limit:
            raise BudgetExhaustedError(
                f"budget exhausted: {name} would become {used + amount} / {limit}"
            )
        self.consumed[name] = used + amount

    def release(self, name: str, amount: int = 1) -> None:
        if name not in self.consumed:
            raise SchemaValidationError(f"unknown per-wake budget: {name}")
        if amount < 0 or self.consumed[name] < amount:
            raise SchemaValidationError("budget release would create an invalid counter")
        self.consumed[name] -= amount

    def reserve_record(self, amount: int = 1) -> None:
        if amount < 0:
            raise SchemaValidationError("canonical record reservation may not be negative")
        limit = int(self.limits["canonical_records"])
        if self.canonical_records_used + amount > limit:
            raise BudgetExhaustedError("canonical record budget exhausted")
        self.canonical_records_used += amount

    def finish(self, *, semantic_steps_used: int, elapsed_monotonic_ns: int) -> None:
        if semantic_steps_used < 0 or semantic_steps_used > int(self.limits["lifecycle_steps"]):
            raise BudgetExhaustedError("semantic lifecycle step budget exhausted")
        if elapsed_monotonic_ns < 0:
            raise SchemaValidationError("monotonic elapsed time may not be negative")
        deadline_ns = int(self.limits["lifecycle_wall_time_ms"]) * 1_000_000
        if elapsed_monotonic_ns > deadline_ns:
            raise BudgetExhaustedError("lifecycle monotonic deadline exhausted")
        self.semantic_steps_used = semantic_steps_used
        self.elapsed_monotonic_ns = elapsed_monotonic_ns

    def as_dict(self) -> dict[str, Any]:
        remaining = {
            name: int(self.limits[name]) - used for name, used in self.consumed.items()
        }
        if any(value < 0 for value in remaining.values()):
            raise SchemaValidationError("canonical budget counter became negative")
        return {
            "config_version": self.config_version,
            "limits": {name: int(self.limits[name]) for name in _DECISION_BUDGETS},
            "consumed": dict(self.consumed),
            "remaining": remaining,
            "semantic_steps_used": self.semantic_steps_used,
            "semantic_steps_limit": int(self.limits["lifecycle_steps"]),
            "canonical_records_used": self.canonical_records_used,
            "canonical_records_limit": int(self.limits["canonical_records"]),
            "elapsed_monotonic_ns": self.elapsed_monotonic_ns,
            "lifecycle_wall_time_limit_ns": int(self.limits["lifecycle_wall_time_ms"])
            * 1_000_000,
        }
