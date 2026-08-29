from __future__ import annotations

from .model import (
    ACCEPTED_PHASE3_REGISTRY_BYTES,
    ACCEPTED_PHASE3_REGISTRY_SHA256,
    CONTRACT_VERSION,
    REPORT_GROUPS,
    Availability,
    CapabilityStatus,
    EpisodeEvidence,
    EvaluationPointRecord,
    Point,
    WRITER_ADMINISTRATION,
    digest_record,
)
from ._validation_base import classify_availability, _substrate_errors, _validate_cost_vector

def _validate_points(evidence: EpisodeEvidence) -> tuple[list[str], dict[Point, EvaluationPointRecord]]:
    errors: list[str] = []
    if tuple(point.point for point in evidence.points) != (Point.E0, Point.E1, Point.E2):
        errors.append("points.order_or_set")
    by_point = {point.point: point for point in evidence.points}
    if len(by_point) != 3:
        errors.append("points.cardinality")
        return errors, by_point
    e0, e1, e2 = by_point[Point.E0], by_point[Point.E1], by_point[Point.E2]
    if not (e0.ordinal < e1.ordinal < e2.ordinal):
        errors.append("points.ordinal_order")
    if e0.ordinal >= min((r.ordinal for r in evidence.caregiving_records), default=evidence.schedule.e1_cutoff_ordinal):
        errors.append("points.e0_after_caregiving")
    if e1.ordinal <= evidence.schedule.e1_cutoff_ordinal:
        errors.append("points.e1_before_cutoff")
    if e1.checkpoint_id != evidence.schedule.e1_checkpoint_id:
        errors.append("points.e1_checkpoint")
    if e2.checkpoint_id != evidence.schedule.e2_checkpoint_id:
        errors.append("points.e2_checkpoint")
    if e2.ordinal <= evidence.availability_transition.ordinal:
        errors.append("points.e2_before_disablement")
    if e0.availability != evidence.schedule.before_availability or e1.availability != evidence.schedule.before_availability:
        errors.append("points.pre_disable_availability")
    if e2.availability != evidence.schedule.after_availability:
        errors.append("points.e2_availability")
    for point in evidence.points:
        if not (point.integrity_valid and point.infrastructure_valid and point.reachable and point.suite_complete):
            errors.append(f"points.{point.point}.integrity")
        if not point.evaluator_sequestered:
            errors.append(f"points.{point.point}.evaluator_sequestration")
        ids = [result.capability_id for result in point.capability_results]
        if len(ids) != len(set(ids)):
            errors.append(f"points.{point.point}.duplicate_capability")
        for result in point.capability_results:
            if result.point != point.point or result.checkpoint_id != point.checkpoint_id:
                errors.append(f"result.{point.point}.{result.capability_id}.binding")
            if result.evaluator_digest != evidence.binding.outcome_evaluator_digest:
                errors.append(f"result.{point.point}.{result.capability_id}.evaluator")
            if result.suite_digest != evidence.binding.capability_suite_digest:
                errors.append(f"result.{point.point}.{result.capability_id}.suite")
        substrate_ids = [entry.substrate_id for entry in point.substrates]
        if len(substrate_ids) != len(set(substrate_ids)):
            errors.append(f"points.{point.point}.duplicate_substrate")
        for entry in point.substrates:
            errors.extend(_substrate_errors(entry, evidence, point))
        errors.extend(_validate_cost_vector(point.cumulative_cost, complete=False, prefix=f"points.{point.point}"))
    capability_sets = [set(r.capability_id for r in point.capability_results) for point in evidence.points]
    if not (capability_sets[0] == capability_sets[1] == capability_sets[2]):
        errors.append("points.capability_set_drift")
    return errors, by_point


def _validate_availability(evidence: EpisodeEvidence, by_point: dict[Point, EvaluationPointRecord]) -> list[str]:
    errors: list[str] = []
    schedule = evidence.schedule
    transition = evidence.availability_transition
    if schedule.writer != WRITER_ADMINISTRATION:
        errors.append("schedule.writer")
    if schedule.before_availability != Availability.W0:
        errors.append("schedule.before_availability")
    if schedule.after_availability not in {Availability.W1, Availability.W2}:
        errors.append("schedule.after_availability")
    if schedule.canonical_digest() != evidence.binding.schedule_digest:
        errors.append("schedule.digest")
    if transition.binding != evidence.binding:
        errors.append("availability_transition.binding")
    if transition.writer != WRITER_ADMINISTRATION or not transition.applied:
        errors.append("availability_transition.writer_or_status")
    if transition.before != schedule.before_availability or transition.after != schedule.after_availability:
        errors.append("availability_transition.values")
    if transition.source_checkpoint_id != schedule.e1_checkpoint_id or transition.destination_checkpoint_id != schedule.e2_checkpoint_id:
        errors.append("availability_transition.checkpoints")
    expected_transition_digest = digest_record(
        "sudachi.phase3.availability_transition/v1",
        {
            "before": transition.before.value,
            "after": transition.after.value,
            "source": transition.source_checkpoint_id,
            "destination": transition.destination_checkpoint_id,
            "writer": transition.writer,
            "ordinal": transition.ordinal,
        },
    )
    if transition.payload_digest != expected_transition_digest:
        errors.append("availability_transition.payload_digest")
    if Point.E1 in by_point and transition.ordinal <= by_point[Point.E1].ordinal:
        errors.append("availability_transition.before_e1_complete")

    proof = evidence.disablement
    if proof.schedule_digest != evidence.binding.schedule_digest or proof.transition_id != transition.transition_id:
        errors.append("disablement.binding")
    if proof.writer != WRITER_ADMINISTRATION:
        errors.append("disablement.writer")
    if proof.source_checkpoint_id != schedule.e1_checkpoint_id or proof.destination_checkpoint_id != schedule.e2_checkpoint_id:
        errors.append("disablement.checkpoints")
    zero_fields = (
        proof.live_adapter_handles,
        proof.post_cutoff_dispatches,
        proof.post_cutoff_human_bridges,
        proof.post_cutoff_model_calls,
        proof.post_cutoff_network_calls,
        proof.post_cutoff_subprocess_calls,
        proof.post_cutoff_human_interventions,
        proof.post_cutoff_caregiver_cost_units,
        proof.queued_or_cached_usable_outputs,
    )
    if any(value != 0 for value in zero_fields):
        errors.append("disablement.nonzero_route_or_cost")
    if not (
        proof.guarded_imports_passed
        and proof.source_inspection_passed
        and proof.alternate_path_probes_passed
        and proof.independently_reconstructed
    ):
        errors.append("disablement.proof_incomplete")

    e2 = by_point.get(Point.E2)
    if e2 is not None:
        observed = classify_availability(caregiver_routes_available=False, substrates=e2.substrates)
        if observed != e2.availability:
            errors.append("e2.availability_class_mismatch")
        for entry in e2.substrates:
            if entry.origin != "caregiver_derived" or not entry.runtime_visible:
                continue
            if e2.availability == Availability.W1 and not entry.w1_permitted:
                errors.append(f"e2.w1_permission.{entry.substrate_id}")
            if e2.availability == Availability.W2:
                if entry.externalized:
                    errors.append(f"e2.hidden_externalized_scaffold.{entry.substrate_id}")
                if not entry.w2_permitted:
                    errors.append(f"e2.w2_permission.{entry.substrate_id}")
    return errors


def _validate_information_flow(evidence: EpisodeEvidence) -> list[str]:
    info = evidence.information_flow
    errors: list[str] = []
    if not info.verifier_evaluator_distinct:
        errors.append("information_flow.aliasing")
    if not (info.stores_disjoint and info.paths_disjoint and info.caches_disjoint):
        errors.append("information_flow.shared_domain")
    if info.heldout_access_before_terminal != 0 or info.derivative_leaks != 0:
        errors.append("information_flow.leakage")
    if info.probe_budget_exceeded or info.retry_budget_exhausted or info.evaluator_targeted_artifact:
        errors.append("information_flow.invalid_development_feedback")
    if not info.invocations_reconciled:
        errors.append("information_flow.invocations")
    return errors


def _capability_semantics(
    evidence: EpisodeEvidence, by_point: dict[Point, EvaluationPointRecord], *, conformance_clean: bool
) -> tuple[list[str], tuple[str, ...], tuple[str, ...]]:
    errors: list[str] = []
    if any(point not in by_point for point in Point):
        return errors, (), ()
    maps = {
        point: {result.capability_id: result for result in by_point[point].capability_results}
        for point in Point
    }
    acquired: list[str] = []
    retained: list[str] = []
    transition_chain_complete = len(evidence.transitions) == 4
    for capability_id in sorted(maps[Point.E0]):
        e0 = maps[Point.E0][capability_id]
        e1 = maps[Point.E1][capability_id]
        e2 = maps[Point.E2][capability_id]
        acquisition_baseline = e0.status == CapabilityStatus.FAILED or (
            e0.status == CapabilityStatus.ABSTAINED and e0.acquisition_eligible_abstention
        )
        if acquisition_baseline and e1.status == CapabilityStatus.PASSED and transition_chain_complete:
            acquired.append(capability_id)
        if e0.protected_at_e0 and e0.status == CapabilityStatus.PASSED:
            if e1.status != CapabilityStatus.PASSED or e2.status != CapabilityStatus.PASSED:
                errors.append(f"capability.{capability_id}.protected_regression")
        if capability_id in acquired and e2.status == CapabilityStatus.PASSED and conformance_clean:
            retained.append(capability_id)
    return errors, tuple(acquired), tuple(retained)


def _validate_report_finalization(evidence: EpisodeEvidence) -> list[str]:
    errors: list[str] = []
    draft = evidence.reviewed_draft
    groups = draft.as_mapping()
    if tuple(key for key, _ in draft.groups) != REPORT_GROUPS or set(groups) != set(REPORT_GROUPS):
        errors.append("report.exact_14_groups")
    if len(draft.groups) != len(groups):
        errors.append("report.duplicate_group")
    if not draft.reviewed:
        errors.append("report.not_reviewed")
    provenance = groups.get("version_provenance")
    if not isinstance(provenance, dict):
        errors.append("report.version_provenance")
    else:
        if provenance.get("accepted_phase3_registry_sha256") != ACCEPTED_PHASE3_REGISTRY_SHA256:
            errors.append("report.registry_sha256")
        if provenance.get("accepted_phase3_registry_bytes") != ACCEPTED_PHASE3_REGISTRY_BYTES:
            errors.append("report.registry_bytes")
        if provenance.get("contract_version") != CONTRACT_VERSION:
            errors.append("report.contract_version")
        if provenance.get("repository_commit") != evidence.repository_commit:
            errors.append("report.repository_commit")

    closure = evidence.cost_closure
    if closure.draft_digest != draft.canonical_digest():
        errors.append("closure.draft_digest")
    if closure.cost_vector_digest != evidence.final_cost.canonical_digest():
        errors.append("closure.cost_vector_digest")
    if closure.closed_after_ordinal <= draft.prepared_ordinal:
        errors.append("closure.order")
    if not closure.vector_reconciled or not closure.all_in_scope_work_complete:
        errors.append("closure.reconciliation")
    if closure.late_in_scope_cost_count or closure.unmatched_event_count or closure.visible_unmeasured_labor_count:
        errors.append("closure.late_or_unmatched_work")

    seal = evidence.publication_seal
    if seal.draft_digest != closure.draft_digest or seal.closure_digest != closure.canonical_digest():
        errors.append("seal.binding")
    if seal.operations_used != 1 or seal.operations_used > seal.operations_limit:
        errors.append("seal.operations")
    if seal.bytes_used < 0 or seal.bytes_used > seal.bytes_limit:
        errors.append("seal.bytes")
    if seal.retries != 0 or seal.semantic_edits != 0:
        errors.append("seal.retry_or_edit")
    return errors
