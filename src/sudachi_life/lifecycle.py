"""Complete bounded wakes for the deterministic seed garden."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .actions import (
    GardenAbstention,
    GardenActionDecision,
    GardenDecision,
    InjectedActionFailure,
    ProtectedActionFailure,
    execute_garden_action,
    select_garden_decision,
)
from .budgets import WakeBudgetLedger
from .checkpoints import CheckpointResult, create_and_register_lifecycle_checkpoint
from .clock import Clock, RealClock
from .constants import ACTIVE_DATABASE_MAX_BYTES, CONSECUTIVE_FAILURE_LIMIT
from .evaluation import (
    GardenEvaluation,
    evaluate_classified_action_failure,
    evaluate_garden_decision,
)
from .errors import SchemaValidationError
from .paths import OrganismPaths
from .storage import read_status, validate_canonical_state
from .wake import WakeTransaction


@dataclass(frozen=True, slots=True)
class WakeResult:
    organism_id: str
    lifecycle_number: int
    external_event_id: str
    seed: int
    decision: GardenDecision
    evaluation: GardenEvaluation
    budget_ledger: dict[str, Any]
    checkpoint: CheckpointResult
    status: str

    def as_dict(self) -> dict[str, Any]:
        return {
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
    import json

    cursor = connection.execute(
        """
        INSERT INTO event (
            organism_id, lineage_generation, lifecycle_number, wall_time_utc_us,
            event_type, source, payload_json, schema_version,
            environment_version, budget_config_version
        )
        SELECT ?, ?, ?, ?, ?, ?, ?, schema_version, environment_version, budget_config_version
        FROM organism WHERE singleton_id = 1
        """,
        (
            organism_id,
            lineage_generation,
            lifecycle_number,
            wall_time_utc_us,
            event_type,
            source,
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
        ),
    )
    return int(cursor.lastrowid)


def _event(
    wake: WakeTransaction,
    *,
    organism_id: str,
    lineage_generation: int,
    wall_time_utc_us: int,
    event_type: str,
    payload: dict[str, Any],
    ledger: WakeBudgetLedger,
) -> int:
    ledger.reserve_record()
    return _append_event_sql(
        wake.connection,
        organism_id=organism_id,
        lineage_generation=lineage_generation,
        lifecycle_number=wake.lifecycle_number,
        wall_time_utc_us=wall_time_utc_us,
        event_type=event_type,
        source="organism:phase1-fixed-policy",
        payload=payload,
    )


def _record_decision_and_evaluate(
    wake: WakeTransaction,
    *,
    organism_id: str,
    lineage_generation: int,
    wall_time_utc_us: int,
    decision: GardenDecision,
    observation,
    ledger: WakeBudgetLedger,
    protected_test_failure_after_plot_write: bool,
) -> tuple[GardenEvaluation, ProtectedActionFailure | None]:
    action_failure: ProtectedActionFailure | None = None
    if isinstance(decision, GardenActionDecision):
        _event(
            wake,
            organism_id=organism_id,
            lineage_generation=lineage_generation,
            wall_time_utc_us=wall_time_utc_us,
            event_type="action_proposed",
            payload=decision.as_dict(),
            ledger=ledger,
        )
        try:
            execute_garden_action(
                wake.connection,
                decision,
                ledger,
                protected_test_failure_after_plot_write=protected_test_failure_after_plot_write,
            )
        except InjectedActionFailure as exc:
            action_failure = exc.failure
            _event(
                wake,
                organism_id=organism_id,
                lineage_generation=lineage_generation,
                wall_time_utc_us=wall_time_utc_us,
                event_type="action_failed",
                payload=action_failure.as_dict(),
                ledger=ledger,
            )
            evaluation = evaluate_classified_action_failure(
                wake.connection, observation, decision, action_failure
            )
        else:
            _event(
                wake,
                organism_id=organism_id,
                lineage_generation=lineage_generation,
                wall_time_utc_us=wall_time_utc_us,
                event_type="action_completed",
                payload={**decision.as_dict(), "success": True},
                ledger=ledger,
            )
            evaluation = evaluate_garden_decision(wake.connection, observation, decision)
    else:
        if protected_test_failure_after_plot_write:
            raise SchemaValidationError(
                "protected action-failure injection requires a mutating action"
            )
        _event(
            wake,
            organism_id=organism_id,
            lineage_generation=lineage_generation,
            wall_time_utc_us=wall_time_utc_us,
            event_type="action_abstained",
            payload=decision.as_dict(),
            ledger=ledger,
        )
        evaluation = evaluate_garden_decision(wake.connection, observation, decision)

    _event(
        wake,
        organism_id=organism_id,
        lineage_generation=lineage_generation,
        wall_time_utc_us=wall_time_utc_us,
        event_type="evaluation_completed",
        payload=evaluation.as_dict(),
        ledger=ledger,
    )
    return evaluation, action_failure


def _completion_payload(
    decision: GardenDecision,
    action_failure: ProtectedActionFailure | None,
) -> dict[str, Any]:
    if action_failure is not None:
        return {
            "outcome": "action_failure",
            "action_id": action_failure.action_id,
            "plot_id": action_failure.plot_id,
            "reason": action_failure.reason,
            "input_consumed": True,
        }
    if isinstance(decision, GardenAbstention):
        return {
            "outcome": "abstention",
            "reason": decision.reason,
            "input_consumed": True,
        }
    return {
        "outcome": "action_success",
        "action_id": decision.action_id,
        "plot_id": decision.plot_id,
        "input_consumed": True,
    }


def _next_failure_streak(
    decision: GardenDecision,
    evaluation: GardenEvaluation,
    current: int,
) -> int:
    """Classify implemented success, abstention, and rolled-back action failure."""

    if current < 0:
        raise SchemaValidationError("canonical failure streak is negative")

    if isinstance(decision, GardenAbstention):
        if decision.reason == "objective_already_complete":
            if not evaluation.success:
                raise SchemaValidationError(
                    "justified objective-complete abstention evaluated as failure"
                )
            updated = 0
        elif decision.reason == "no_applicable_action":
            if evaluation.success:
                raise SchemaValidationError(
                    "no-applicable-action abstention evaluated as success"
                )
            updated = current + 1
        else:
            raise SchemaValidationError(
                f"failure-streak classification is not implemented for {decision.reason}"
            )
    else:
        if evaluation.success:
            updated = 0
        elif evaluation.progress == "action_failed_rolled_back":
            updated = current + 1
        else:
            raise SchemaValidationError(
                "mutating action failure has no protected classification"
            )

    if updated >= CONSECUTIVE_FAILURE_LIMIT:
        raise SchemaValidationError(
            "maintenance threshold entry is not implemented in Slice 8"
        )
    return updated


def perform_garden_wake(
    runtime_root: Path | str,
    organism_id: str,
    *,
    seed: int,
    clock: Clock | None = None,
    protected_test_failure_after_plot_write: bool = False,
) -> WakeResult:
    """Perform one fixed-policy wake and stabilize its checkpoint."""

    clock = clock or RealClock()
    paths = OrganismPaths.build(runtime_root, organism_id)
    wake = WakeTransaction.acquire(paths)
    committed = False
    try:
        started = clock.read()
        organism = wake.connection.execute(
            "SELECT organism_id, lineage_generation, consecutive_failures "
            "FROM organism WHERE singleton_id = 1"
        ).fetchone()
        if organism is None:
            raise SchemaValidationError("canonical organism state is missing")
        organism_id_value = str(organism["organism_id"])
        lineage_generation = int(organism["lineage_generation"])
        ledger = WakeBudgetLedger.load(wake.connection)
        _event(
            wake,
            organism_id=organism_id_value,
            lineage_generation=lineage_generation,
            wall_time_utc_us=started.wall_time_utc_us,
            event_type="wake_accepted",
            payload={"seed": seed},
            ledger=ledger,
        )

        claimed = wake.claim_oldest_garden_tick()
        ledger.consume("input_events")
        _event(
            wake,
            organism_id=organism_id_value,
            lineage_generation=lineage_generation,
            wall_time_utc_us=started.wall_time_utc_us,
            event_type="input_claimed",
            payload={
                "inbox_id": claimed.inbox_id,
                "external_event_id": claimed.external_event_id,
                "event_type": claimed.event_type,
            },
            ledger=ledger,
        )

        observation = wake.build_observation()
        ledger.consume("observations")
        _event(
            wake,
            organism_id=organism_id_value,
            lineage_generation=lineage_generation,
            wall_time_utc_us=started.wall_time_utc_us,
            event_type="observation_created",
            payload=observation.as_dict(),
            ledger=ledger,
        )

        decision = select_garden_decision(observation)
        evaluation, action_failure = _record_decision_and_evaluate(
            wake,
            organism_id=organism_id_value,
            lineage_generation=lineage_generation,
            wall_time_utc_us=started.wall_time_utc_us,
            decision=decision,
            observation=observation,
            ledger=ledger,
            protected_test_failure_after_plot_write=protected_test_failure_after_plot_write,
        )

        failure_streak_before = int(organism["consecutive_failures"])
        failure_streak_after = _next_failure_streak(
            decision, evaluation, failure_streak_before
        )
        if failure_streak_after != failure_streak_before:
            failure_reason = (
                decision.reason
                if isinstance(decision, GardenAbstention)
                else (
                    action_failure.reason
                    if action_failure is not None
                    else "successful_action"
                )
            )
            _event(
                wake,
                organism_id=organism_id_value,
                lineage_generation=lineage_generation,
                wall_time_utc_us=started.wall_time_utc_us,
                event_type="failure_streak_updated",
                payload={
                    "before": failure_streak_before,
                    "after": failure_streak_after,
                    "reason": failure_reason,
                    "maintenance_threshold": CONSECUTIVE_FAILURE_LIMIT,
                },
                ledger=ledger,
            )

        consumed = wake.connection.execute(
            "UPDATE inbox_event SET consumed = 1 "
            "WHERE inbox_id = ? AND claimed_lifecycle_number = ? AND consumed = 0",
            (claimed.inbox_id, wake.lifecycle_number),
        )
        if consumed.rowcount != 1:
            raise SchemaValidationError("claimed input consumption changed unexpectedly")

        _event(
            wake,
            organism_id=organism_id_value,
            lineage_generation=lineage_generation,
            wall_time_utc_us=started.wall_time_utc_us,
            event_type="lifecycle_completed",
            payload=_completion_payload(decision, action_failure),
            ledger=ledger,
        )

        finished = clock.read()
        ledger.finish(
            semantic_steps_used=12,
            elapsed_monotonic_ns=finished.monotonic_ns - started.monotonic_ns,
        )
        ledger.reserve_record(2)
        _append_event_sql(
            wake.connection,
            organism_id=organism_id_value,
            lineage_generation=lineage_generation,
            lifecycle_number=wake.lifecycle_number,
            wall_time_utc_us=finished.wall_time_utc_us,
            event_type="budget_ledger",
            source="organism:phase1-fixed-policy",
            payload=ledger.as_dict(),
        )
        boundary = _append_event_sql(
            wake.connection,
            organism_id=organism_id_value,
            lineage_generation=lineage_generation,
            lifecycle_number=wake.lifecycle_number,
            wall_time_utc_us=finished.wall_time_utc_us,
            event_type="checkpoint_pending",
            source="organism:phase1-fixed-policy",
            payload={"reason": "committed_wake", "lifecycle_number": wake.lifecycle_number},
        )
        wake.connection.execute(
            """
            UPDATE organism
            SET lifecycle_number = ?, status = 'checkpoint_pending', checkpoint_pending = 1,
                pending_checkpoint_generation = lineage_generation,
                pending_checkpoint_event_sequence = ?, consecutive_failures = ?,
                maintenance_reason = NULL, last_wake_wall_time_utc_us = ?
            WHERE singleton_id = 1
            """,
            (
                wake.lifecycle_number,
                boundary,
                failure_streak_after,
                started.wall_time_utc_us,
            ),
        )
        validate_canonical_state(wake.connection, expect_checkpoint_pending=True)
        page_count = wake.connection.execute("PRAGMA page_count").fetchone()[0]
        page_size = wake.connection.execute("PRAGMA page_size").fetchone()[0]
        if page_count * page_size > ACTIVE_DATABASE_MAX_BYTES:
            raise SchemaValidationError("active database would exceed protected Phase 1 limit")
        wake.connection.commit()
        wake.close_committed()
        committed = True
    except Exception:
        wake.rollback_and_close()
        raise

    if not committed:
        raise SchemaValidationError("wake did not commit")

    checkpoint = create_and_register_lifecycle_checkpoint(paths, clock=clock)
    status = read_status(paths)
    return WakeResult(
        organism_id=status.organism_id,
        lifecycle_number=status.lifecycle_number,
        external_event_id=claimed.external_event_id,
        seed=seed,
        decision=decision,
        evaluation=evaluation,
        budget_ledger=ledger.as_dict(),
        checkpoint=checkpoint,
        status=status.status,
    )


def perform_first_water_wake(
    runtime_root: Path | str,
    organism_id: str,
    *,
    seed: int,
    clock: Clock | None = None,
) -> WakeResult:
    """Compatibility entry point retained for the canonical first wake tests."""

    return perform_garden_wake(runtime_root, organism_id, seed=seed, clock=clock)
