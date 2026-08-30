from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
import hashlib
import json
from typing import Any, Mapping

CONTRACT_VERSION = "sudachi.withheld_caregiver_evaluation/v1"
AVAILABILITY_VERSION = "sudachi.assistance_availability/v1"
W3_VERSION = "sudachi.w3_conformance/v1"
IMPLEMENTATION_VERSION = "sudachi.phase3.fixture_foundation/v1"
ACCEPTED_PHASE3_REGISTRY_SHA256 = "12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1"
ACCEPTED_PHASE3_REGISTRY_BYTES = 43179

WRITER_ORGANISM = "organism"
WRITER_ADMINISTRATION = "administration"
WRITER_CATEGORIES = frozenset({WRITER_ORGANISM, WRITER_ADMINISTRATION})

FIXTURE_MANIFEST_VERSION = "sudachi.phase3.fixture_study_manifest/v1"
FIXTURE_STUDY_PURPOSE = "deterministic fixture-only W3 conformance mechanics"
FIXTURE_RUN_GENERATION_RULE = "planned ordinal deterministically selects the closed fixture case"
FIXTURE_ATTEMPT_ASSIGNMENT_RULE = "each planned ordinal is assigned exactly once before E0"
FIXTURE_STOPPING_RULE = "stop only after the exact planned attempt population is terminal"
FIXTURE_POPULATION_RECONCILIATION_RULE = "planned ordinals equal terminal attempt-record ordinals exactly"
FIXTURE_COST_POLICY_ID = "phase3-fixture-cost-policy-v1"
FIXTURE_PROTECTED_CONFIGURATION_VERSION = "phase3-fixture-v1"
FIXTURE_PUBLICATION_POLICY_VERSION = "sudachi.phase3.fixture_publication_policy/v1"
FIXTURE_CLOSURE_OPERATIONS_LIMIT = 1
FIXTURE_CLOSURE_BYTES_LIMIT = 4096
FIXTURE_SEAL_OPERATIONS_LIMIT = 1
FIXTURE_SEAL_BYTES_LIMIT = 4096

MANDATORY_FAILURE_CONTROLS = (
    "misleading_assistance",
    "inconsistent_assistance",
    "correct_but_unrepresentable_advice",
    "ambiguous_advice",
    "premature_withdrawal",
    "delayed_withdrawal_dependency_persistence",
    "hidden_scaffold_injection",
    "stale_episode_or_lineage_reuse",
    "evaluator_targeting_or_leakage",
    "opaque_model_update",
    "cost_displacement",
    "caregiver_outage_or_abstention",
    "organism_abstention",
    "transition_replay_or_conflict",
    "rollback_after_harmful_activation",
)


class Availability(StrEnum):
    W0 = "W0"
    W1 = "W1"
    W2 = "W2"


class Point(StrEnum):
    E0 = "E0"
    E1 = "E1"
    E2 = "E2"


class AttemptState(StrEnum):
    SCHEDULED = "scheduled"
    STARTED = "started"
    E0_INVALID = "e0_invalid"
    DEVELOPMENT_FAILED = "development_failed"
    ROLLED_BACK = "rolled_back"
    E2_INVALID = "e2_invalid"
    COMPLETED_UNSUCCESSFUL = "completed_unsuccessful"
    COMPLETED_SUCCESSFUL = "completed_successful"


TERMINAL_ATTEMPT_STATES = frozenset(
    {
        AttemptState.E0_INVALID,
        AttemptState.DEVELOPMENT_FAILED,
        AttemptState.ROLLED_BACK,
        AttemptState.E2_INVALID,
        AttemptState.COMPLETED_UNSUCCESSFUL,
        AttemptState.COMPLETED_SUCCESSFUL,
    }
)


class CapabilityStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    ABSTAINED = "abstained"
    NOT_REACHED = "not_reached"
    INVALID = "invalid"


class CostStatus(StrEnum):
    MEASURED = "measured"
    NOT_APPLICABLE = "not_applicable"
    UNMEASURED = "unmeasured"


class TransitionKind(StrEnum):
    CONVERSION = "conversion"
    VERIFICATION = "verification"
    ADOPTION = "adoption"
    ACTIVATION = "activation"


EXTERNALIZED_SUBSTRATE_CLASSES = frozenset(
    {
        "prompt_example",
        "retrieved_memory",
        "skill_bank",
        "deterministic_code",
        "rule",
        "test",
        "action_trace",
        "demonstration",
        "recovery_suffix",
        "router",
        "external_tool",
        "fixture",
        "cache",
        "other_declared",
    }
)

ALLOWED_SUBSTRATE_CLASSES = frozenset(
    {
        "model_weights",
        "prompt_example",
        "retrieved_memory",
        "skill_bank",
        "deterministic_code",
        "rule",
        "test",
        "action_trace",
        "demonstration",
        "recovery_suffix",
        "router",
        "external_tool",
        "fixture",
        "environment_state",
        "protected_evaluator",
        "conversion_verifier",
        "protected_runtime",
        "cache",
        "other_declared",
    }
)

ALLOWED_CUSTODIANS = frozenset(
    {"organism", "administration", "protected_experiment_infrastructure", "environment"}
)
ALLOWED_ORIGINS = frozenset(
    {"genesis", "caregiver_derived", "organism_derived", "administration_protected", "environment"}
)

MANDATORY_COST_FIELDS = (
    "human.active_caregiver_ms",
    "human.monitoring_ms",
    "human.intervention_ms",
    "human.artifact_review_ms",
    "human.maintenance_ms",
    "human.experimenter_development_ms",
    "human.evaluator_operation_ms",
    "human.integrity_investigation_ms",
    "human.report_preparation_ms",
    "human.report_review_ms",
    "model.calls",
    "model.input_tokens",
    "model.output_tokens",
    "model.measured_latency_ms",
    "model.retries",
    "model.failures",
    "model.money_minor_units",
    "experiment.interactions",
    "experiment.resets",
    "experiment.failed_attempts",
    "experiment.evaluator_calls",
    "experiment.verifier_calls",
    "experiment.fixture_calls",
    "experiment.administrative_operations",
    "experiment.research_wall_duration_ms",
    "compute.training_cpu_ms",
    "compute.inference_cpu_ms",
    "compute.accelerator_ms",
    "storage.peak_working_set_bytes",
    "storage.active_state_bytes",
    "storage.checkpoint_store_bytes",
    "storage.caregiver_derived_runtime_substrate_bytes",
    "storage.total_runtime_substrate_bytes",
    "storage.retained_artifact_log_evidence_bytes",
    "storage.report_package_bytes",
)

P3_REQUIREMENT_GROUP_COUNTS = (("A", 10), ("B", 10), ("C", 10), ("D", 12), ("E", 14), ("F", 12), ("G", 10), ("H", 12), ("I", 10), ("J", 12), ("K", 14), ("L", 14))


def accepted_phase3_requirement_ids() -> tuple[str, ...]:
    return tuple(
        f"P3-{group}{index:02d}"
        for group, count in P3_REQUIREMENT_GROUP_COUNTS
        for index in range(1, count + 1)
    )


REPORT_GROUPS = (
    "study_population",
    "identity",
    "e0_baseline",
    "caregiving_events",
    "lifecycle_transitions",
    "capability_outcomes",
    "substrate_declarations",
    "caregiver_disablement",
    "integrity",
    "cost_vectors",
    "protected_outcomes",
    "negative_history",
    "limitations",
    "version_provenance",
)


def _normalize(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return _normalize(asdict(value))
    if isinstance(value, Mapping):
        return {str(k): _normalize(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_normalize(v) for v in value]
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, set | frozenset):
        return sorted(_normalize(v) for v in value)
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        _normalize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def digest_record(domain: str, value: Any) -> str:
    if not domain or "\n" in domain:
        raise ValueError("digest domain must be a nonempty single line")
    payload = f"{domain}\n{canonical_json(value)}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class EpisodeBinding:
    study_id: str
    attempt_id: str
    attempt_ordinal: int
    episode_id: str
    organism_id: str
    lineage_generation: int
    database_schema_version: int
    base_contract_version: str
    environment_version: str
    capability_suite_version: str
    capability_suite_digest: str
    outcome_evaluator_version: str
    outcome_evaluator_digest: str
    conversion_verifier_version: str
    conversion_verifier_digest: str
    information_flow_policy_version: str
    information_flow_policy_digest: str
    schedule_version: str
    schedule_digest: str
    protected_budget_version: str
    protected_configuration_version: str
    baseline_checkpoint_id: str
    caregiver_condition_id: str
    substrate_baseline_condition_id: str
    fixture_case_id: str
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True, slots=True)
class EvidenceIdentity:
    study_id: str
    attempt_id: str
    episode_id: str
    organism_id: str
    lineage_generation: int
    point: Point
    cutoff_ordinal: int
    checkpoint_id: str

    @classmethod
    def from_binding(
        cls,
        binding: EpisodeBinding,
        *,
        point: Point,
        cutoff_ordinal: int,
        checkpoint_id: str,
    ) -> "EvidenceIdentity":
        return cls(
            study_id=binding.study_id,
            attempt_id=binding.attempt_id,
            episode_id=binding.episode_id,
            organism_id=binding.organism_id,
            lineage_generation=binding.lineage_generation,
            point=point,
            cutoff_ordinal=cutoff_ordinal,
            checkpoint_id=checkpoint_id,
        )


@dataclass(frozen=True, slots=True)
class ProtectedSchedule:
    version: str
    e1_cutoff_ordinal: int
    e1_checkpoint_id: str
    e2_checkpoint_id: str
    before_availability: Availability
    after_availability: Availability
    writer: str = WRITER_ADMINISTRATION

    def canonical_digest(self) -> str:
        return digest_record("sudachi.phase3.protected_schedule/v1", self)


@dataclass(frozen=True, slots=True)
class PublicationPolicy:
    version: str
    closure_operations_limit: int
    closure_bytes_limit: int
    seal_operations_limit: int
    seal_bytes_limit: int

    def canonical_digest(self) -> str:
        return digest_record("sudachi.phase3.publication_policy/v1", self)


@dataclass(frozen=True, slots=True)
class InformationFlowPolicy:
    version: str
    verifier_digest: str
    evaluator_digest: str
    verifier_input_store_id: str
    verifier_output_store_id: str
    evaluator_input_store_id: str
    evaluator_output_store_id: str
    verifier_path_id: str
    evaluator_path_id: str
    verifier_cache_id: str
    evaluator_cache_id: str
    verifier_probe_budget: int
    verifier_retry_budget: int
    permitted_feedback_fields: tuple[str, ...]
    permitted_feedback_recipients: tuple[str, ...]
    permitted_feedback_timing: str
    permitted_feedback_cardinality: int

    def canonical_digest(self) -> str:
        return digest_record("sudachi.phase3.information_flow_policy/v1", self)


@dataclass(frozen=True, slots=True)
class AttemptRecord:
    attempt_id: str
    ordinal: int
    state: AttemptState
    state_history: tuple[AttemptState, ...]
    episode_id: str | None
    organism_id: str
    lineage_generation: int


@dataclass(frozen=True, slots=True)
class StudyManifest:
    study_id: str
    manifest_version: str
    study_purpose: str
    claim_tier: str
    deterministic_run_generation_rule: str
    planned_attempt_ordinals: tuple[int, ...]
    exact_attempt_count: int
    stopping_rule: str
    attempt_assignment_rule: str
    required_failure_controls: tuple[str, ...]
    comparison_family_conditions: tuple[str, ...]
    population_reconciliation_rule: str
    attempt_records: tuple[AttemptRecord, ...]
    suite_digest: str
    evaluator_digest: str
    verifier_digest: str
    information_flow_policy_digest: str
    schedule_digest: str
    cost_policy_id: str
    publication_policy: PublicationPolicy

    def canonical_digest(self) -> str:
        return digest_record("sudachi.phase3.study_manifest/v1", self)


@dataclass(frozen=True, slots=True)
class CaregivingRecord:
    record_id: str
    binding: EpisodeBinding
    assistance_class: str
    content_digest: str
    content_size_bytes: int
    terminal_outcome: str
    terminal: bool
    ordinal: int
    source: str = "deterministic_fixture"


@dataclass(frozen=True, slots=True)
class TransitionRecord:
    transition_id: str
    kind: TransitionKind
    binding: EpisodeBinding
    writer: str
    status: str
    ordinal: int
    input_id: str
    output_id: str
    payload_digest: str
    source_checkpoint_id: str | None = None
    destination_checkpoint_id: str | None = None
    cost_entry_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AvailabilityTransition:
    transition_id: str
    binding: EpisodeBinding
    writer: str
    before: Availability
    after: Availability
    source_checkpoint_id: str
    destination_checkpoint_id: str
    applied: bool
    ordinal: int
    payload_digest: str


@dataclass(frozen=True, slots=True)
class SubstrateEntry:
    substrate_id: str
    substrate_class: str
    version: str
    canonical_digest: str
    canonical_size_bytes: int
    measured_size_bytes: int
    active: bool
    executable: bool
    readable: bool
    callable: bool
    custodian: str
    origin: str
    source_caregiving_event_ids: tuple[str, ...]
    conversion_id: str | None
    verification_id: str | None
    adoption_id: str | None
    activation_id: str | None
    study_id: str
    attempt_id: str
    episode_id: str
    organism_id: str
    lineage_generation: int
    point: Point
    cutoff_ordinal: int
    checkpoint_id: str
    w1_permitted: bool
    w2_permitted: bool
    capability_dependency: str | None

    @property
    def runtime_visible(self) -> bool:
        return self.active or self.executable or self.readable or self.callable

    @property
    def externalized(self) -> bool:
        return self.substrate_class in EXTERNALIZED_SUBSTRATE_CLASSES


@dataclass(frozen=True, slots=True)
class CapabilityResult:
    identity: EvidenceIdentity
    capability_id: str
    point: Point
    status: CapabilityStatus
    evaluator_digest: str
    suite_digest: str
    checkpoint_id: str
    scenario_id: str
    evidence: tuple[str, ...]
    resource_counters: tuple[tuple[str, int], ...]
    protected_at_e0: bool = False
    acquisition_eligible_abstention: bool = False


@dataclass(frozen=True, slots=True)
class CostField:
    status: CostStatus
    value: int | None
    unit: str
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class CostVector:
    identity: EvidenceIdentity
    fields: tuple[tuple[str, CostField], ...]
    service_metadata: tuple[tuple[str, str], ...] = ()

    def as_mapping(self) -> dict[str, CostField]:
        return dict(self.fields)

    def canonical_digest(self) -> str:
        return digest_record("sudachi.phase3.cost_vector/v1", self)


@dataclass(frozen=True, slots=True)
class EvaluationPointRecord:
    identity: EvidenceIdentity
    point: Point
    ordinal: int
    availability: Availability
    checkpoint_id: str
    integrity_valid: bool
    infrastructure_valid: bool
    reachable: bool
    suite_complete: bool
    evaluator_sequestered: bool
    capability_results: tuple[CapabilityResult, ...]
    substrates: tuple[SubstrateEntry, ...]
    cumulative_cost: CostVector


@dataclass(frozen=True, slots=True)
class DisablementProof:
    identity: EvidenceIdentity
    schedule_digest: str
    transition_id: str
    writer: str
    source_checkpoint_id: str
    destination_checkpoint_id: str
    live_adapter_handles: int
    post_cutoff_dispatches: int
    post_cutoff_human_bridges: int
    post_cutoff_model_calls: int
    post_cutoff_network_calls: int
    post_cutoff_subprocess_calls: int
    post_cutoff_human_interventions: int
    post_cutoff_caregiver_cost_units: int
    queued_or_cached_usable_outputs: int
    guarded_imports_passed: bool
    source_inspection_passed: bool
    alternate_path_probes_passed: bool
    independently_reconstructed: bool


@dataclass(frozen=True, slots=True)
class InformationFlowInvocation:
    invocation_id: str
    identity: EvidenceIdentity
    role: str
    ordinal: int
    input_digest: str
    output_digest: str
    probe_ordinal: int
    retry_ordinal: int
    disclosed_fields: tuple[str, ...]
    recipients: tuple[str, ...]
    disclosure_timing: str
    contains_heldout_material: bool
    derivative_of_heldout: bool
    evaluator_targeted_artifact: bool


@dataclass(frozen=True, slots=True)
class InformationFlowEvidence:
    identity: EvidenceIdentity
    invocations: tuple[InformationFlowInvocation, ...]
    heldout_access_before_terminal: int
    derivative_leaks: int
    probe_budget_exceeded: bool
    retry_budget_exhausted: bool
    evaluator_targeted_artifact: bool


@dataclass(frozen=True, slots=True)
class ReviewedDraft:
    identity: EvidenceIdentity
    groups: tuple[tuple[str, Any], ...]
    prepared_ordinal: int
    reviewed: bool

    def as_mapping(self) -> dict[str, Any]:
        return dict(self.groups)

    def canonical_digest(self) -> str:
        return digest_record("sudachi.phase3.reviewed_draft/v1", self)


@dataclass(frozen=True, slots=True)
class CostClosure:
    identity: EvidenceIdentity
    closure_id: str
    draft_digest: str
    cost_vector_digest: str
    closed_after_ordinal: int
    vector_reconciled: bool
    all_in_scope_work_complete: bool
    late_in_scope_cost_count: int
    unmatched_event_count: int
    visible_unmeasured_labor_count: int
    operations_used: int
    bytes_used: int
    version: int = 1

    def canonical_digest(self) -> str:
        return digest_record("sudachi.phase3.cost_closure/v1", self)


@dataclass(frozen=True, slots=True)
class PublicationSeal:
    identity: EvidenceIdentity
    seal_id: str
    draft_digest: str
    closure_digest: str
    operations_used: int
    bytes_used: int
    retries: int
    semantic_edits: int


@dataclass(frozen=True, slots=True)
class EpisodeEvidence:
    binding: EpisodeBinding
    schedule: ProtectedSchedule
    study: StudyManifest
    caregiving_records: tuple[CaregivingRecord, ...]
    transitions: tuple[TransitionRecord, ...]
    availability_transition: AvailabilityTransition
    points: tuple[EvaluationPointRecord, ...]
    disablement: DisablementProof
    information_flow_policy: InformationFlowPolicy
    information_flow: InformationFlowEvidence
    final_cost: CostVector
    reviewed_draft: ReviewedDraft
    cost_closure: CostClosure
    publication_seal: PublicationSeal
    terminal_attempt_state: AttemptState
    repository_commit: str
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ConformanceResult:
    valid: bool
    availability_subtype: Availability | None
    acquired_capabilities: tuple[str, ...] = ()
    retained_capabilities: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    report: Mapping[str, Any] = field(default_factory=dict)
