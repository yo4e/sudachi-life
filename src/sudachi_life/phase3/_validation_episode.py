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
from ._fixture_helpers import _closure_payload_bytes, _report_groups, _seal_payload_bytes
from ._validation_base import (
    _expected_identity,
    _is_commit_sha,
    _is_sha256,
    _substrate_errors,
    _validate_cost_vector,
    classify_availability,
)


def _validate_points(evidence: EpisodeEvidence) -> tuple[list[str], dict[Point, EvaluationPointRecord]]:
    errors: list[str] = []
    if any(not isinstance(point.point, Point) for point in evidence.points):
        errors.append("points.point_type")
    if tuple(point.point for point in evidence.points) != (Point.E0, Point.E1, Point.E2):
        errors.append("points.order_or_set")
    by_point = {point.point: point for point in evidence.points if isinstance(point.point, Point)}
    if len(by_point) != 3:
        errors.append("points.cardinality")
        return errors, by_point
    e0, e1, e2 = by_point[Point.E0], by_point[Point.E1], by_point[Point.E2]
    if not (e0.ordinal < e1.ordinal < e2.ordinal):
        errors.append("points.ordinal_order")
    if e0.ordinal >= min((r.ordinal for r in evidence.caregiving_records), default=evidence.schedule.e1_cutoff_ordinal):
        errors.append("points.e0_after_caregiving")
    if e0.checkpoint_id != evidence.binding.baseline_checkpoint_id:
        errors.append("points.e0_checkpoint")
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
        expected_identity = _expected_identity(evidence, point=point.point, checkpoint_id=point.checkpoint_id)
        if point.identity != expected_identity:
            errors.append(f"points.{point.point}.identity")
        if not isinstance(point.availability, Availability):
            errors.append(f"points.{point.point}.availability_type")
        if not (point.integrity_valid and point.infrastructure_valid and point.reachable and point.suite_complete):
            errors.append(f"points.{point.point}.integrity")
        if not point.evaluator_sequestered:
            errors.append(f"points.{point.point}.evaluator_sequestration")
        ids = [result.capability_id for result in point.capability_results]
        if len(ids) != len(set(ids)):
            errors.append(f"points.{point.point}.duplicate_capability")
        for result in point.capability_results:
            if result.identity != expected_identity:
                errors.append(f"result.{point.point}.{result.capability_id}.identity")
            if not isinstance(result.status, CapabilityStatus):
                errors.append(f"result.{point.point}.{result.capability_id}.status_type")
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
        errors.extend(
            _validate_cost_vector(
                point.cumulative_cost,
                complete=False,
                prefix=f"points.{point.point}",
                expected_identity=expected_identity,
            )
        )
    capability_sets = [set(r.capability_id for r in point.capability_results) for point in evidence.points]
    if not (capability_sets[0] == capability_sets[1] == capability_sets[2]):
        errors.append("points.capability_set_drift")
    return errors, by_point


def _validate_availability(evidence: EpisodeEvidence, by_point: dict[Point, EvaluationPointRecord]) -> list[str]:
    errors: list[str] = []
    schedule = evidence.schedule
    transition = evidence.availability_transition
    schedule_types_valid = isinstance(schedule.before_availability, Availability) and isinstance(schedule.after_availability, Availability)
    transition_types_valid = isinstance(transition.before, Availability) and isinstance(transition.after, Availability)
    if not schedule_types_valid:
        errors.append("schedule.availability_type")
    if not transition_types_valid:
        errors.append("availability_transition.value_type")
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
    if transition_types_valid:
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
    expected_e2_identity = _expected_identity(evidence, point=Point.E2, checkpoint_id=schedule.e2_checkpoint_id)
    if proof.identity != expected_e2_identity:
        errors.append("disablement.identity")
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
    policy = evidence.information_flow_policy
    info = evidence.information_flow
    errors: list[str] = []

    if policy.version != evidence.binding.information_flow_policy_version:
        errors.append("information_flow.policy_version")
    policy_digest = policy.canonical_digest()
    if policy_digest != evidence.binding.information_flow_policy_digest or policy_digest != evidence.study.information_flow_policy_digest:
        errors.append("information_flow.policy_digest")
    if policy.verifier_digest != evidence.binding.conversion_verifier_digest:
        errors.append("information_flow.verifier_identity")
    if policy.evaluator_digest != evidence.binding.outcome_evaluator_digest:
        errors.append("information_flow.evaluator_identity")
    if policy.verifier_digest == policy.evaluator_digest:
        errors.append("information_flow.aliasing")

    verifier_domain = {
        policy.verifier_input_store_id,
        policy.verifier_output_store_id,
        policy.verifier_path_id,
        policy.verifier_cache_id,
    }
    evaluator_domain = {
        policy.evaluator_input_store_id,
        policy.evaluator_output_store_id,
        policy.evaluator_path_id,
        policy.evaluator_cache_id,
    }
    if "" in verifier_domain | evaluator_domain or verifier_domain & evaluator_domain:
        errors.append("information_flow.shared_domain")
    if policy.verifier_probe_budget < 0 or policy.verifier_retry_budget < 0 or policy.permitted_feedback_cardinality < 0:
        errors.append("information_flow.policy_budget")
    if not policy.permitted_feedback_timing:
        errors.append("information_flow.policy_timing")

    expected_e2_identity = _expected_identity(evidence, point=Point.E2, checkpoint_id=evidence.schedule.e2_checkpoint_id)
    if info.identity != expected_e2_identity:
        errors.append("information_flow.identity")

    invocation_ids = [record.invocation_id for record in info.invocations]
    if len(invocation_ids) != len(set(invocation_ids)):
        errors.append("information_flow.duplicate_invocation")

    computed_heldout_access = 0
    computed_derivative_leaks = 0
    computed_probe_exceeded = False
    computed_retry_exhausted = False
    computed_targeted = False
    disclosed_count = 0
    verifier_calls = 0
    evaluator_calls = 0

    point_checkpoints = {
        Point.E0: evidence.binding.baseline_checkpoint_id,
        Point.E1: evidence.schedule.e1_checkpoint_id,
        Point.E2: evidence.schedule.e2_checkpoint_id,
    }
    for record in info.invocations:
        if record.role not in {"verifier", "evaluator"}:
            errors.append(f"information_flow.{record.invocation_id}.role")
            continue
        if record.identity.point not in point_checkpoints:
            errors.append(f"information_flow.{record.invocation_id}.point")
        else:
            expected_identity = _expected_identity(
                evidence,
                point=record.identity.point,
                checkpoint_id=point_checkpoints[record.identity.point],
            )
            if record.identity != expected_identity:
                errors.append(f"information_flow.{record.invocation_id}.identity")
        if record.ordinal < 1:
            errors.append(f"information_flow.{record.invocation_id}.ordinal")
        if not _is_sha256(record.input_digest) or not _is_sha256(record.output_digest):
            errors.append(f"information_flow.{record.invocation_id}.digest")
        if record.probe_ordinal < 0 or record.retry_ordinal < 0:
            errors.append(f"information_flow.{record.invocation_id}.probe_or_retry")

        computed_targeted = computed_targeted or record.evaluator_targeted_artifact
        if record.derivative_of_heldout and any(recipient != "protected_evidence_store" for recipient in record.recipients):
            computed_derivative_leaks += 1

        if record.role == "verifier":
            verifier_calls += 1
            if record.contains_heldout_material or record.derivative_of_heldout:
                computed_heldout_access += 1
            if record.probe_ordinal > policy.verifier_probe_budget:
                computed_probe_exceeded = True
            if record.retry_ordinal > policy.verifier_retry_budget:
                computed_retry_exhausted = True
            if not set(record.disclosed_fields) <= set(policy.permitted_feedback_fields):
                errors.append(f"information_flow.{record.invocation_id}.disclosed_fields")
            if not set(record.recipients) <= set(policy.permitted_feedback_recipients):
                errors.append(f"information_flow.{record.invocation_id}.recipients")
            if record.disclosure_timing != policy.permitted_feedback_timing:
                errors.append(f"information_flow.{record.invocation_id}.timing")
            if record.disclosed_fields or record.recipients:
                disclosed_count += 1
        else:
            evaluator_calls += 1
            if record.recipients != ("protected_evidence_store",):
                computed_heldout_access += 1
                errors.append(f"information_flow.{record.invocation_id}.evaluator_recipient")
            if record.disclosed_fields:
                computed_heldout_access += 1
                errors.append(f"information_flow.{record.invocation_id}.evaluator_disclosure")
            if record.disclosure_timing != "protected_only":
                computed_heldout_access += 1
                errors.append(f"information_flow.{record.invocation_id}.evaluator_timing")
            if not record.contains_heldout_material:
                errors.append(f"information_flow.{record.invocation_id}.evaluator_scope")

    if disclosed_count > policy.permitted_feedback_cardinality:
        errors.append("information_flow.feedback_cardinality")

    final_cost = evidence.final_cost.as_mapping()
    expected_verifier_calls = final_cost.get("experiment.verifier_calls")
    expected_evaluator_calls = final_cost.get("experiment.evaluator_calls")
    if expected_verifier_calls is None or expected_verifier_calls.value != verifier_calls:
        errors.append("information_flow.verifier_call_reconciliation")
    if expected_evaluator_calls is None or expected_evaluator_calls.value != evaluator_calls:
        errors.append("information_flow.evaluator_call_reconciliation")

    if info.heldout_access_before_terminal != computed_heldout_access or computed_heldout_access != 0:
        errors.append("information_flow.leakage")
    if info.derivative_leaks != computed_derivative_leaks or computed_derivative_leaks != 0:
        errors.append("information_flow.derivative_leakage")
    if info.probe_budget_exceeded != computed_probe_exceeded or computed_probe_exceeded:
        errors.append("information_flow.probe_budget")
    if info.retry_budget_exhausted != computed_retry_exhausted or computed_retry_exhausted:
        errors.append("information_flow.retry_budget")
    if info.evaluator_targeted_artifact != computed_targeted or computed_targeted:
        errors.append("information_flow.evaluator_targeting")
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
    expected_final_identity = _expected_identity(evidence, point=Point.E2, checkpoint_id=evidence.schedule.e2_checkpoint_id)
    if draft.identity != expected_final_identity:
        errors.append("report.identity")
    if tuple(key for key, _ in draft.groups) != REPORT_GROUPS or set(groups) != set(REPORT_GROUPS):
        errors.append("report.exact_14_groups")
    if len(draft.groups) != len(groups):
        errors.append("report.duplicate_group")
    if not draft.reviewed:
        errors.append("report.not_reviewed")
    if not _is_commit_sha(evidence.repository_commit):
        errors.append("report.repository_commit_format")
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
        if provenance.get("study_manifest_digest") != evidence.study.canonical_digest():
            errors.append("report.study_manifest_digest")
        if provenance.get("information_flow_policy_digest") != evidence.information_flow_policy.canonical_digest():
            errors.append("report.information_flow_policy_digest")
        if provenance.get("publication_policy_digest") != evidence.study.publication_policy.canonical_digest():
            errors.append("report.publication_policy_digest")

    try:
        expected_groups = dict(
            _report_groups(
                binding=evidence.binding,
                study=evidence.study,
                caregiving_records=evidence.caregiving_records,
                transitions=evidence.transitions,
                points=evidence.points,
                disablement=evidence.disablement,
                information_flow_policy=evidence.information_flow_policy,
                information_flow=evidence.information_flow,
                final_cost=evidence.final_cost,
                terminal_state=evidence.terminal_attempt_state,
                repository_commit=evidence.repository_commit,
            )
        )
    except (AttributeError, KeyError, StopIteration, TypeError, ValueError):
        errors.append("report.semantic_projection_invalid")
    else:
        if groups != expected_groups:
            errors.append("report.semantic_binding")

    policy = evidence.study.publication_policy
    closure = evidence.cost_closure
    if closure.identity != expected_final_identity:
        errors.append("closure.identity")
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
    expected_closure_bytes = _closure_payload_bytes(draft_digest=closure.draft_digest, cost_vector_digest=closure.cost_vector_digest)
    if closure.operations_used != 1 or closure.operations_used > policy.closure_operations_limit:
        errors.append("closure.operations")
    if closure.bytes_used != expected_closure_bytes or closure.bytes_used > policy.closure_bytes_limit:
        errors.append("closure.bytes")

    seal = evidence.publication_seal
    if seal.identity != expected_final_identity:
        errors.append("seal.identity")
    if seal.draft_digest != closure.draft_digest or seal.closure_digest != closure.canonical_digest():
        errors.append("seal.binding")
    expected_seal_bytes = _seal_payload_bytes(draft_digest=seal.draft_digest, closure_digest=seal.closure_digest)
    if seal.operations_used != 1 or seal.operations_used > policy.seal_operations_limit:
        errors.append("seal.operations")
    if seal.bytes_used != expected_seal_bytes or seal.bytes_used > policy.seal_bytes_limit:
        errors.append("seal.bytes")
    if seal.retries != 0 or seal.semantic_edits != 0:
        errors.append("seal.retry_or_edit")
    return errors
