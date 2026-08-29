from __future__ import annotations

from dataclasses import asdict
from typing import Any, Iterable

from .model import (
    ACCEPTED_PHASE3_REGISTRY_BYTES,
    ACCEPTED_PHASE3_REGISTRY_SHA256,
    ALLOWED_CUSTODIANS,
    ALLOWED_ORIGINS,
    ALLOWED_SUBSTRATE_CLASSES,
    CONTRACT_VERSION,
    MANDATORY_COST_FIELDS,
    REPORT_GROUPS,
    TERMINAL_ATTEMPT_STATES,
    Availability,
    AttemptState,
    CapabilityStatus,
    ConformanceResult,
    CostStatus,
    CostVector,
    EpisodeBinding,
    EpisodeEvidence,
    EvaluationPointRecord,
    Point,
    SubstrateEntry,
    TransitionKind,
    TransitionRecord,
    WRITER_ADMINISTRATION,
    WRITER_ORGANISM,
    digest_record,
)


_ALLOWED_ASSISTANCE_CLASSES = frozenset(
    {"demonstration", "correction", "constraint", "explanation", "preference", "question", "defer", "abstain"}
)
_ALLOWED_CAREGIVER_OUTCOMES = frozenset(
    {
        "accepted",
        "rejected",
        "deferred",
        "clarification_requested",
        "misleading_detected",
        "inconsistent_detected",
        "unrepresentable",
        "expired",
        "invalid",
    }
)


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def _binding_errors(binding: EpisodeBinding) -> list[str]:
    errors: list[str] = []
    if binding.contract_version != CONTRACT_VERSION:
        errors.append("binding.contract_version")
    for name, value in asdict(binding).items():
        if name.endswith("_digest") and not _is_sha256(str(value)):
            errors.append(f"binding.{name}")
    if binding.attempt_ordinal < 1:
        errors.append("binding.attempt_ordinal")
    if binding.lineage_generation < 0:
        errors.append("binding.lineage_generation")
    if binding.database_schema_version < 1:
        errors.append("binding.database_schema_version")
    required_text = (
        "study_id",
        "attempt_id",
        "episode_id",
        "organism_id",
        "base_contract_version",
        "environment_version",
        "capability_suite_version",
        "outcome_evaluator_version",
        "conversion_verifier_version",
        "information_flow_policy_version",
        "schedule_version",
        "protected_budget_version",
        "protected_configuration_version",
        "baseline_checkpoint_id",
        "caregiver_condition_id",
        "substrate_baseline_condition_id",
        "fixture_case_id",
    )
    for name in required_text:
        if not getattr(binding, name):
            errors.append(f"binding.{name}")
    return errors


def classify_availability(*, caregiver_routes_available: bool, substrates: Iterable[SubstrateEntry]) -> Availability:
    """Classify the point-local W0/W1/W2 axis from technical availability.

    W3 is deliberately absent because it is episode-level conformance, not a
    fourth availability class.
    """
    if caregiver_routes_available:
        return Availability.W0
    externalized = any(
        item.origin == "caregiver_derived" and item.externalized and item.runtime_visible
        for item in substrates
    )
    return Availability.W1 if externalized else Availability.W2


def _validate_cost_vector(vector: CostVector, *, complete: bool, prefix: str) -> list[str]:
    errors: list[str] = []
    mapping = vector.as_mapping()
    expected = set(MANDATORY_COST_FIELDS)
    actual = set(mapping)
    if actual != expected:
        errors.append(f"{prefix}.cost_field_set")
    if len(vector.fields) != len(mapping):
        errors.append(f"{prefix}.duplicate_cost_field")
    for key in sorted(expected & actual):
        field = mapping[key]
        if not field.unit:
            errors.append(f"{prefix}.{key}.unit")
        if field.status == CostStatus.MEASURED:
            if not isinstance(field.value, int) or isinstance(field.value, bool) or field.value < 0:
                errors.append(f"{prefix}.{key}.measured_value")
            if field.reason is not None:
                errors.append(f"{prefix}.{key}.measured_reason")
        elif field.status == CostStatus.NOT_APPLICABLE:
            if field.value is not None or not field.reason:
                errors.append(f"{prefix}.{key}.not_applicable")
        elif field.status == CostStatus.UNMEASURED:
            if field.value is not None or not field.reason:
                errors.append(f"{prefix}.{key}.unmeasured")
            if complete:
                errors.append(f"{prefix}.{key}.incomplete")
        else:
            errors.append(f"{prefix}.{key}.status")
    return errors


def _validate_cost_monotonic(vectors: list[CostVector]) -> list[str]:
    errors: list[str] = []
    for key in MANDATORY_COST_FIELDS:
        previous: int | None = None
        previous_status = None
        for index, vector in enumerate(vectors):
            field = vector.as_mapping().get(key)
            if field is None:
                continue
            if field.status == CostStatus.MEASURED:
                if previous_status == CostStatus.NOT_APPLICABLE:
                    errors.append(f"cost_monotonic.{key}.status_changed")
                if previous is not None and field.value is not None and field.value < previous:
                    errors.append(f"cost_monotonic.{key}.decreased_at_{index}")
                previous = field.value
            elif field.status == CostStatus.NOT_APPLICABLE and previous_status == CostStatus.MEASURED:
                errors.append(f"cost_monotonic.{key}.status_changed")
            previous_status = field.status
    return errors


def _validate_study(evidence: EpisodeEvidence) -> list[str]:
    study = evidence.study
    binding = evidence.binding
    errors: list[str] = []
    if study.study_id != binding.study_id:
        errors.append("study.binding")
    if study.exact_attempt_count != len(study.planned_attempt_ordinals):
        errors.append("study.exact_attempt_count")
    if len(set(study.planned_attempt_ordinals)) != len(study.planned_attempt_ordinals):
        errors.append("study.duplicate_ordinal")
    if len(study.attempt_records) != study.exact_attempt_count:
        errors.append("study.population_size")
    by_ordinal = {record.ordinal: record for record in study.attempt_records}
    if set(by_ordinal) != set(study.planned_attempt_ordinals):
        errors.append("study.population_ordinals")
    if len(by_ordinal) != len(study.attempt_records):
        errors.append("study.population_duplicate")
    for ordinal, record in by_ordinal.items():
        expected_history = (AttemptState.SCHEDULED, AttemptState.STARTED, record.state)
        if record.state not in TERMINAL_ATTEMPT_STATES:
            errors.append(f"study.attempt.{ordinal}.nonterminal")
        if record.state_history != expected_history:
            errors.append(f"study.attempt.{ordinal}.state_graph")
        if record.attempt_id == binding.attempt_id:
            if record.episode_id != binding.episode_id:
                errors.append("study.current_attempt.episode")
            if record.organism_id != binding.organism_id or record.lineage_generation != binding.lineage_generation:
                errors.append("study.current_attempt.identity")
            if record.state != evidence.terminal_attempt_state:
                errors.append("study.current_attempt.terminal_state")
    current = [r for r in study.attempt_records if r.attempt_id == binding.attempt_id]
    if len(current) != 1:
        errors.append("study.current_attempt.cardinality")
    if study.suite_digest != binding.capability_suite_digest:
        errors.append("study.suite_digest")
    if study.evaluator_digest != binding.outcome_evaluator_digest:
        errors.append("study.evaluator_digest")
    if study.verifier_digest != binding.conversion_verifier_digest:
        errors.append("study.verifier_digest")
    if study.information_flow_policy_digest != binding.information_flow_policy_digest:
        errors.append("study.information_flow_policy_digest")
    if study.schedule_digest != binding.schedule_digest:
        errors.append("study.schedule_digest")
    if study.claim_tier != "deterministic_conformance":
        errors.append("study.claim_tier")
    return errors


def _validate_caregiving(evidence: EpisodeEvidence, e0_ordinal: int) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for record in evidence.caregiving_records:
        if record.record_id in seen:
            errors.append("caregiving.duplicate_id")
        seen.add(record.record_id)
        if record.binding != evidence.binding:
            errors.append(f"caregiving.{record.record_id}.binding")
        if record.source != "deterministic_fixture":
            errors.append(f"caregiving.{record.record_id}.live_source_forbidden")
        if record.assistance_class not in _ALLOWED_ASSISTANCE_CLASSES:
            errors.append(f"caregiving.{record.record_id}.assistance_class")
        if record.terminal_outcome not in _ALLOWED_CAREGIVER_OUTCOMES:
            errors.append(f"caregiving.{record.record_id}.outcome")
        if not record.terminal:
            errors.append(f"caregiving.{record.record_id}.nonterminal")
        if record.ordinal <= e0_ordinal or record.ordinal >= evidence.schedule.e1_cutoff_ordinal:
            errors.append(f"caregiving.{record.record_id}.ordering")
        if not _is_sha256(record.content_digest) or record.content_size_bytes < 0:
            errors.append(f"caregiving.{record.record_id}.content")
    if not evidence.caregiving_records:
        errors.append("caregiving.empty")
    return errors


def _validate_transitions(evidence: EpisodeEvidence) -> list[str]:
    errors: list[str] = []
    records = evidence.transitions
    by_kind: dict[TransitionKind, TransitionRecord] = {}
    for record in records:
        if record.kind in by_kind:
            errors.append(f"transitions.{record.kind}.duplicate")
        by_kind[record.kind] = record
        if record.binding != evidence.binding:
            errors.append(f"transitions.{record.kind}.binding")
        if record.ordinal >= evidence.schedule.e1_cutoff_ordinal:
            errors.append(f"transitions.{record.kind}.after_cutoff")
        if not _is_sha256(record.payload_digest):
            errors.append(f"transitions.{record.kind}.payload_digest")
    if set(by_kind) != set(TransitionKind):
        errors.append("transitions.kind_set")
        return errors

    conversion = by_kind[TransitionKind.CONVERSION]
    verification = by_kind[TransitionKind.VERIFICATION]
    adoption = by_kind[TransitionKind.ADOPTION]
    activation = by_kind[TransitionKind.ACTIVATION]
    if not (conversion.ordinal < verification.ordinal < adoption.ordinal < activation.ordinal):
        errors.append("transitions.order")
    if conversion.writer != WRITER_ORGANISM or conversion.status != "produced":
        errors.append("transitions.conversion.semantics")
    if conversion.input_id not in {r.record_id for r in evidence.caregiving_records}:
        errors.append("transitions.conversion.source")
    if verification.writer != WRITER_ADMINISTRATION or verification.status != "passed":
        errors.append("transitions.verification.semantics")
    if verification.input_id != conversion.transition_id:
        errors.append("transitions.verification.source")
    if adoption.writer != WRITER_ADMINISTRATION or adoption.status != "accepted":
        errors.append("transitions.adoption.semantics")
    if adoption.input_id != verification.transition_id:
        errors.append("transitions.adoption.source")
    if activation.writer != WRITER_ADMINISTRATION or activation.status != "activated":
        errors.append("transitions.activation.semantics")
    if activation.input_id != adoption.transition_id:
        errors.append("transitions.activation.source")
    if activation.source_checkpoint_id != evidence.binding.baseline_checkpoint_id:
        errors.append("transitions.activation.source_checkpoint")
    if activation.destination_checkpoint_id != evidence.schedule.e1_checkpoint_id:
        errors.append("transitions.activation.destination_checkpoint")
    if activation.output_id != conversion.output_id:
        errors.append("transitions.activation.candidate_identity")
    return errors


def _substrate_errors(entry: SubstrateEntry, evidence: EpisodeEvidence, point: EvaluationPointRecord) -> list[str]:
    errors: list[str] = []
    prefix = f"substrate.{point.point}.{entry.substrate_id}"
    if entry.substrate_class not in ALLOWED_SUBSTRATE_CLASSES:
        errors.append(f"{prefix}.class")
    if entry.custodian not in ALLOWED_CUSTODIANS:
        errors.append(f"{prefix}.custodian")
    if entry.origin not in ALLOWED_ORIGINS:
        errors.append(f"{prefix}.origin")
    if not _is_sha256(entry.canonical_digest):
        errors.append(f"{prefix}.digest")
    if entry.canonical_size_bytes < 0 or entry.measured_size_bytes < 0:
        errors.append(f"{prefix}.size_negative")
    if entry.canonical_size_bytes != entry.measured_size_bytes:
        errors.append(f"{prefix}.size_mismatch")
    if (
        entry.study_id != evidence.binding.study_id
        or entry.attempt_id != evidence.binding.attempt_id
        or entry.episode_id != evidence.binding.episode_id
        or entry.organism_id != evidence.binding.organism_id
        or entry.lineage_generation != evidence.binding.lineage_generation
        or entry.point != point.point
        or entry.cutoff_ordinal != evidence.schedule.e1_cutoff_ordinal
        or entry.checkpoint_id != point.checkpoint_id
    ):
        errors.append(f"{prefix}.binding")
    if entry.capability_dependency and not entry.runtime_visible:
        errors.append(f"{prefix}.dependency_declared_unavailable")
    if entry.origin == "caregiver_derived":
        known = {r.record_id for r in evidence.caregiving_records}
        if not entry.source_caregiving_event_ids or not set(entry.source_caregiving_event_ids) <= known:
            errors.append(f"{prefix}.caregiver_provenance")
        required = (entry.conversion_id, entry.verification_id, entry.adoption_id, entry.activation_id)
        if any(value is None for value in required):
            errors.append(f"{prefix}.transition_provenance")
        else:
            transitions_by_kind = {record.kind: record for record in evidence.transitions}
            if set(transitions_by_kind) == set(TransitionKind):
                expected = tuple(
                    transitions_by_kind[kind].transition_id
                    for kind in (
                        TransitionKind.CONVERSION,
                        TransitionKind.VERIFICATION,
                        TransitionKind.ADOPTION,
                        TransitionKind.ACTIVATION,
                    )
                )
                if required != expected:
                    errors.append(f"{prefix}.transition_provenance_mismatch")
                if transitions_by_kind[TransitionKind.ACTIVATION].output_id != entry.substrate_id:
                    errors.append(f"{prefix}.activation_output_mismatch")
        if entry.substrate_class in {"protected_evaluator", "conversion_verifier", "environment_state"}:
            errors.append(f"{prefix}.protected_target_modified")
    return errors
