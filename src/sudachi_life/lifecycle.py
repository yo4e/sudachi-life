"""Public garden wake API with the bounded schema-v2 request extension.

The frozen pre-extension wake remains byte-identical in ``lifecycle_impl``.
This module preserves the public/private surface and inserts only the accepted
fixture request savepoint between the Phase 1 budget ledger and checkpoint event.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import lifecycle_impl as _impl
from .phase2_request import ConsultationRequestResult, maybe_create_fixture_request


for _name, _value in vars(_impl).items():
    if not _name.startswith("__"):
        globals()[_name] = _value


@dataclass(frozen=True, slots=True)
class WakeResult:
    organism_id: str
    lifecycle_number: int
    external_event_id: str
    seed: int
    decision: GardenDecision
    evaluation: GardenEvaluation
    budget_exhaustion: ProtectedBudgetExhaustion | None
    budget_ledger: dict[str, Any]
    checkpoint: CheckpointResult
    status: str
    consultation_request: ConsultationRequestResult | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "organism_id": self.organism_id,
            "lifecycle_number": self.lifecycle_number,
            "external_event_id": self.external_event_id,
            "seed": self.seed,
            "decision": self.decision.as_dict(),
            "evaluation": self.evaluation.as_dict(),
            "budget_ledger": self.budget_ledger,
            "checkpoint_id": self.checkpoint.checkpoint_id,
            "checkpoint_event_sequence": self.checkpoint.event_sequence,
            "status": self.status,
        }
        if self.budget_exhaustion is not None:
            payload["budget_exhaustion"] = self.budget_exhaustion.as_dict()
        if self.consultation_request is not None:
            payload["consultation_request"] = self.consultation_request.as_dict()
        return payload


_State = dict[str, Any]
_request_state: ContextVar[_State | None] = ContextVar(
    "fixture_request_wake_state",
    default=None,
)
_original_append_event_sql = _impl._append_event_sql
_original_perform_garden_wake = _impl.perform_garden_wake


def _append_event_sql(
    connection,
    *,
    organism_id: str,
    lineage_generation: int,
    lifecycle_number: int,
    wall_time_utc_us: int,
    event_type: str,
    source: str,
    payload: dict[str, Any],
) -> int:
    state = _request_state.get()
    if state is not None and event_type == "budget_ledger":
        state["budget_snapshot"] = payload
    if state is not None and event_type == "checkpoint_pending":
        state["consultation_request"] = maybe_create_fixture_request(
            connection,
            runtime_root=state["runtime_root"],
            organism_id=organism_id,
            lineage_generation=lineage_generation,
            lifecycle_number=lifecycle_number,
            wall_time_utc_us=wall_time_utc_us,
            checkpoint_payload=payload,
            budget_snapshot=state.get("budget_snapshot"),
            append_event=_original_append_event_sql,
        )
    return _original_append_event_sql(
        connection,
        organism_id=organism_id,
        lineage_generation=lineage_generation,
        lifecycle_number=lifecycle_number,
        wall_time_utc_us=wall_time_utc_us,
        event_type=event_type,
        source=source,
        payload=payload,
    )


_impl._append_event_sql = _append_event_sql


def _convert_result(
    result: Any,
    consultation_request: ConsultationRequestResult | None,
) -> WakeResult:
    return WakeResult(
        organism_id=result.organism_id,
        lifecycle_number=result.lifecycle_number,
        external_event_id=result.external_event_id,
        seed=result.seed,
        decision=result.decision,
        evaluation=result.evaluation,
        budget_exhaustion=result.budget_exhaustion,
        budget_ledger=result.budget_ledger,
        checkpoint=result.checkpoint,
        status=result.status,
        consultation_request=consultation_request,
    )


def perform_garden_wake(
    runtime_root: Path | str,
    organism_id: str,
    *,
    seed: int,
    clock: Clock | None = None,
    protected_test_failure_after_plot_write: bool = False,
    protected_test_retention_failure_after_stage: bool = False,
) -> WakeResult:
    """Perform the frozen wake plus an eligible fixture request extension."""

    state: _State = {
        "runtime_root": Path(runtime_root),
        "budget_snapshot": None,
        "consultation_request": None,
    }
    token = _request_state.set(state)
    try:
        result = _original_perform_garden_wake(
            runtime_root,
            organism_id,
            seed=seed,
            clock=clock,
            protected_test_failure_after_plot_write=(
                protected_test_failure_after_plot_write
            ),
            protected_test_retention_failure_after_stage=(
                protected_test_retention_failure_after_stage
            ),
        )
    finally:
        _request_state.reset(token)
    return _convert_result(result, state["consultation_request"])


def perform_first_water_wake(
    runtime_root: Path | str,
    organism_id: str,
    *,
    seed: int,
    clock: Clock | None = None,
) -> WakeResult:
    """Compatibility entry point retained for the canonical first wake tests."""

    return perform_garden_wake(runtime_root, organism_id, seed=seed, clock=clock)


_impl.perform_garden_wake = perform_garden_wake
_impl.perform_first_water_wake = perform_first_water_wake
