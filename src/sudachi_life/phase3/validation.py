from __future__ import annotations

from typing import Any

from .model import (
    AttemptState,
    ConformanceResult,
    EpisodeEvidence,
    Point,
    TERMINAL_ATTEMPT_STATES,
)
from ._validation_base import (
    _binding_errors,
    _expected_identity,
    _validate_caregiving,
    _validate_cost_monotonic,
    _validate_cost_vector,
    _validate_study,
    _validate_transitions,
    classify_availability,
)
from ._validation_episode import (
    _capability_semantics,
    _validate_availability,
    _validate_information_flow,
    _validate_points,
    _validate_report_finalization,
)


def validate_episode(evidence: EpisodeEvidence) -> ConformanceResult:
    """Validate a fixture-only Phase 3 episode and return fail-closed W3 conformance.

    The function has no I/O, performs no caregiver call, and never writes the
    organism body. Any integrity error prevents W3 certification.
    """
    errors = _binding_errors(evidence.binding)
    errors.extend(_validate_study(evidence))

    points_errors, by_point = _validate_points(evidence)
    errors.extend(points_errors)
    e0_ordinal = by_point.get(Point.E0).ordinal if Point.E0 in by_point else -1
    errors.extend(_validate_caregiving(evidence, e0_ordinal))
    errors.extend(_validate_transitions(evidence))
    errors.extend(_validate_availability(evidence, by_point))
    errors.extend(_validate_information_flow(evidence))

    for index, point in enumerate(evidence.points):
        expected_identity = _expected_identity(evidence, point=point.point, checkpoint_id=point.checkpoint_id)
        errors.extend(
            _validate_cost_vector(
                point.cumulative_cost,
                complete=False,
                prefix=f"point_cost.{index}",
                expected_identity=expected_identity,
            )
        )
    final_identity = _expected_identity(evidence, point=Point.E2, checkpoint_id=evidence.schedule.e2_checkpoint_id)
    errors.extend(
        _validate_cost_vector(
            evidence.final_cost,
            complete=True,
            prefix="final_cost",
            expected_identity=final_identity,
        )
    )
    errors.extend(_validate_cost_monotonic([p.cumulative_cost for p in evidence.points] + [evidence.final_cost]))
    errors.extend(_validate_report_finalization(evidence))

    if any(record.source != "deterministic_fixture" for record in evidence.caregiving_records):
        errors.append("fixture_only.live_caregiver_forbidden")

    capability_errors, acquired, _ = _capability_semantics(evidence, by_point, conformance_clean=False)
    errors.extend(capability_errors)
    clean = not errors
    _, acquired, retained = _capability_semantics(evidence, by_point, conformance_clean=clean)
    if clean and not retained:
        errors.append("capability.no_retained_acquisition")
        clean = False

    availability = by_point.get(Point.E2).availability if Point.E2 in by_point else None
    report = evidence.reviewed_draft.as_mapping() if clean else {}
    return ConformanceResult(
        valid=clean,
        availability_subtype=availability if clean else None,
        acquired_capabilities=acquired if clean else (),
        retained_capabilities=retained if clean else (),
        errors=tuple(sorted(set(errors))),
        report=report,
    )


class ReplayConflict(ValueError):
    """Raised when the same immutable evidence identity is replayed with different content."""


def reconcile_immutable_replay(existing: Any, incoming: Any, *, identity_attr: str) -> Any:
    existing_id = getattr(existing, identity_attr)
    incoming_id = getattr(incoming, identity_attr)
    if existing_id != incoming_id:
        raise ReplayConflict("replay identity mismatch")
    if existing == incoming:
        return existing
    raise ReplayConflict("same identity with different immutable content")


def advance_attempt_history(
    history: tuple[AttemptState, ...], next_state: AttemptState
) -> tuple[AttemptState, ...]:
    if not history:
        if next_state != AttemptState.SCHEDULED:
            raise ReplayConflict("attempt must begin scheduled")
        return (AttemptState.SCHEDULED,)
    current = history[-1]
    if current in TERMINAL_ATTEMPT_STATES:
        if next_state == current:
            return history
        raise ReplayConflict("terminal attempt outcome is immutable")
    if current == AttemptState.SCHEDULED:
        if next_state != AttemptState.STARTED:
            raise ReplayConflict("scheduled attempt must start before terminalization")
        return history + (AttemptState.STARTED,)
    if current == AttemptState.STARTED:
        if next_state not in TERMINAL_ATTEMPT_STATES:
            raise ReplayConflict("started attempt requires exactly one terminal outcome")
        return history + (next_state,)
    raise ReplayConflict("unknown attempt state")
