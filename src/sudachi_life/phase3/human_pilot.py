from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib

from .caregiver import (
    ACTIVE_SOURCE_KINDS,
    CaregiverRequest,
    CaregiverSourceKind,
    ProposalKind,
)

HUMAN_PILOT_PREFLIGHT_VERSION = "sudachi.phase3.human_caregiver_pilot_preflight/v1"

# Proposed operational-pilot limits. They are review defaults only and do not
# authorize a live human source.
PROPOSED_PILOT_ATTEMPTS = 1
PROPOSED_MAX_CONSULTATIONS_PER_ATTEMPT = 3
PROPOSED_MAX_CLARIFICATIONS_PER_ATTEMPT = 2
PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT = 600_000
PROPOSED_MAX_RESPONSE_LATENCY_MS = 300_000
PROPOSED_MAX_ATTEMPT_WALL_MS = 1_800_000
PROPOSED_MAX_PROPOSAL_BYTES = 2_048
PROPOSED_PROPOSAL_PAYLOAD_RETENTION_DAYS = 365


class CaregiverConfidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EthicsReviewStatus(StrEnum):
    UNRESOLVED = "unresolved"
    NOT_REQUIRED_DECLARED = "not_required_declared"
    APPROVED = "approved"


@dataclass(frozen=True, slots=True)
class HumanPilotBudget:
    planned_attempts: int
    max_consultations_per_attempt: int
    max_clarifications_per_attempt: int
    max_caregiver_active_ms_per_attempt: int
    max_response_latency_ms: int
    max_attempt_wall_ms: int
    max_proposal_bytes: int


@dataclass(frozen=True, slots=True)
class HumanPilotDataPolicy:
    purpose: str
    raw_chat_transcript_retained: bool
    proposal_payload_retention_days: int
    retain_digest_and_typed_metadata: bool
    public_raw_payload_default: bool
    pseudonymous_caregiver_id_required: bool
    personal_data_prohibited: bool
    secrets_prohibited: bool
    third_party_confidential_data_prohibited: bool
    consent_record_required: bool
    retention_extension_requires_owner_decision: bool


@dataclass(frozen=True, slots=True)
class HiddenLaborPolicy:
    off_channel_semantic_interventions_limit: int
    manual_code_edits_during_attempt_limit: int
    unlogged_semantic_assistance_invalidates_attempt: bool
    administrative_actions_must_be_logged: bool


@dataclass(frozen=True, slots=True)
class HumanCaregiverPilotPreflight:
    protocol_version: str
    pilot_id: str
    purpose: str
    scientific_claims_allowed: bool
    live_human_enabled: bool
    live_transport: str
    capture_mode: str
    budget: HumanPilotBudget
    data_policy: HumanPilotDataPolicy
    hidden_labor_policy: HiddenLaborPolicy
    ethics_review_status: EthicsReviewStatus
    project_owner_live_approval: bool
    independent_live_candidate_audit_complete: bool
    consent_materials_ready: bool


@dataclass(frozen=True, slots=True)
class HumanPilotPreflightResult:
    design_valid: bool
    review_packet_ready: bool
    activation_ready: bool
    errors: tuple[str, ...]
    activation_blockers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class HumanProposalDraft:
    """Human-authored structured draft; deliberately not a live CaregiverProposal.

    There is intentionally no function in this module that turns this object into
    an active human CaregiverProposal. Crossing that bridge is a separately
    authorized live-capability change.
    """

    draft_id: str
    request_id: str
    caregiver_id: str
    sequence_ordinal: int
    kind: ProposalKind
    text: str
    confidence: CaregiverConfidence
    observation_ids: tuple[str, ...] = ()
    objective_ids: tuple[str, ...] = ()
    action_ids: tuple[str, ...] = ()
    clarification_of_proposal_id: str | None = None
    contains_personal_data: bool = False
    contains_secret: bool = False
    contains_third_party_confidential_data: bool = False


@dataclass(frozen=True, slots=True)
class HumanProposalDraftValidation:
    valid: bool
    errors: tuple[str, ...]
    payload_sha256: str | None


def _is_pseudonymous_caregiver_id(value: str) -> bool:
    prefix = "caregiver:pseudo:"
    if not value.startswith(prefix):
        return False
    token = value[len(prefix) :]
    return len(token) == 32 and all(ch in "0123456789abcdef" for ch in token)


def proposed_human_caregiver_pilot_v1() -> HumanCaregiverPilotPreflight:
    """Return the proposed pre-live Pilot v1 review packet.

    The returned object is intentionally not activation-ready. In particular,
    human source activation, a live transport, project-owner approval, resolved
    ethics context, consent readiness, and an independent audit of the eventual
    live candidate are absent.
    """
    return HumanCaregiverPilotPreflight(
        protocol_version=HUMAN_PILOT_PREFLIGHT_VERSION,
        pilot_id="pilot:human-caregiver-v1-preflight",
        purpose="single-caregiver operational protocol pilot; no developmental-gain claim",
        scientific_claims_allowed=False,
        live_human_enabled=False,
        live_transport="none",
        capture_mode="human_attested_structured_form",
        budget=HumanPilotBudget(
            planned_attempts=PROPOSED_PILOT_ATTEMPTS,
            max_consultations_per_attempt=PROPOSED_MAX_CONSULTATIONS_PER_ATTEMPT,
            max_clarifications_per_attempt=PROPOSED_MAX_CLARIFICATIONS_PER_ATTEMPT,
            max_caregiver_active_ms_per_attempt=PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT,
            max_response_latency_ms=PROPOSED_MAX_RESPONSE_LATENCY_MS,
            max_attempt_wall_ms=PROPOSED_MAX_ATTEMPT_WALL_MS,
            max_proposal_bytes=PROPOSED_MAX_PROPOSAL_BYTES,
        ),
        data_policy=HumanPilotDataPolicy(
            purpose="evaluate the bounded human-caregiver protocol and accounting mechanics",
            raw_chat_transcript_retained=False,
            proposal_payload_retention_days=PROPOSED_PROPOSAL_PAYLOAD_RETENTION_DAYS,
            retain_digest_and_typed_metadata=True,
            public_raw_payload_default=False,
            pseudonymous_caregiver_id_required=True,
            personal_data_prohibited=True,
            secrets_prohibited=True,
            third_party_confidential_data_prohibited=True,
            consent_record_required=True,
            retention_extension_requires_owner_decision=True,
        ),
        hidden_labor_policy=HiddenLaborPolicy(
            off_channel_semantic_interventions_limit=0,
            manual_code_edits_during_attempt_limit=0,
            unlogged_semantic_assistance_invalidates_attempt=True,
            administrative_actions_must_be_logged=True,
        ),
        ethics_review_status=EthicsReviewStatus.UNRESOLVED,
        project_owner_live_approval=False,
        independent_live_candidate_audit_complete=False,
        consent_materials_ready=False,
    )


def validate_human_pilot_preflight(
    plan: HumanCaregiverPilotPreflight,
) -> HumanPilotPreflightResult:
    errors: list[str] = []
    blockers: list[str] = []

    if plan.protocol_version != HUMAN_PILOT_PREFLIGHT_VERSION:
        errors.append("pilot.protocol_version")
    if not plan.pilot_id:
        errors.append("pilot.pilot_id")
    if plan.scientific_claims_allowed:
        errors.append("pilot.scientific_claims_forbidden")
    if plan.live_human_enabled:
        errors.append("pilot.live_human_must_remain_disabled")
    if plan.live_transport != "none":
        errors.append("pilot.live_transport_forbidden")
    if plan.capture_mode != "human_attested_structured_form":
        errors.append("pilot.capture_mode")
    if CaregiverSourceKind.HUMAN in ACTIVE_SOURCE_KINDS:
        errors.append("pilot.human_source_already_active")

    budget = plan.budget
    if budget.planned_attempts != PROPOSED_PILOT_ATTEMPTS:
        errors.append("pilot.budget.planned_attempts")
    if budget.max_consultations_per_attempt != PROPOSED_MAX_CONSULTATIONS_PER_ATTEMPT:
        errors.append("pilot.budget.consultations")
    if budget.max_clarifications_per_attempt != PROPOSED_MAX_CLARIFICATIONS_PER_ATTEMPT:
        errors.append("pilot.budget.clarifications")
    if budget.max_caregiver_active_ms_per_attempt != PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT:
        errors.append("pilot.budget.active_ms")
    if budget.max_response_latency_ms != PROPOSED_MAX_RESPONSE_LATENCY_MS:
        errors.append("pilot.budget.response_latency_ms")
    if budget.max_attempt_wall_ms != PROPOSED_MAX_ATTEMPT_WALL_MS:
        errors.append("pilot.budget.attempt_wall_ms")
    if budget.max_proposal_bytes != PROPOSED_MAX_PROPOSAL_BYTES:
        errors.append("pilot.budget.proposal_bytes")

    data = plan.data_policy
    if not data.purpose:
        errors.append("pilot.data.purpose")
    if data.raw_chat_transcript_retained:
        errors.append("pilot.data.raw_chat_transcript")
    if data.proposal_payload_retention_days != PROPOSED_PROPOSAL_PAYLOAD_RETENTION_DAYS:
        errors.append("pilot.data.retention_days")
    if not data.retain_digest_and_typed_metadata:
        errors.append("pilot.data.digest_metadata")
    if data.public_raw_payload_default:
        errors.append("pilot.data.public_raw_payload")
    if not data.pseudonymous_caregiver_id_required:
        errors.append("pilot.data.pseudonymous_id")
    if not data.personal_data_prohibited:
        errors.append("pilot.data.personal_data")
    if not data.secrets_prohibited:
        errors.append("pilot.data.secrets")
    if not data.third_party_confidential_data_prohibited:
        errors.append("pilot.data.third_party_confidential")
    if not data.consent_record_required:
        errors.append("pilot.data.consent_record")
    if not data.retention_extension_requires_owner_decision:
        errors.append("pilot.data.retention_extension")

    labor = plan.hidden_labor_policy
    if labor.off_channel_semantic_interventions_limit != 0:
        errors.append("pilot.hidden_labor.off_channel")
    if labor.manual_code_edits_during_attempt_limit != 0:
        errors.append("pilot.hidden_labor.manual_code_edits")
    if not labor.unlogged_semantic_assistance_invalidates_attempt:
        errors.append("pilot.hidden_labor.unlogged_assistance")
    if not labor.administrative_actions_must_be_logged:
        errors.append("pilot.hidden_labor.administrative_logging")

    if not plan.project_owner_live_approval:
        blockers.append("activation.project_owner_approval_required")
    if plan.ethics_review_status is EthicsReviewStatus.UNRESOLVED:
        blockers.append("activation.ethics_context_must_be_resolved")
    elif type(plan.ethics_review_status) is not EthicsReviewStatus:
        errors.append("pilot.ethics_review_status")
    if not plan.consent_materials_ready:
        blockers.append("activation.consent_materials_not_ready")
    if not plan.independent_live_candidate_audit_complete:
        blockers.append("activation.independent_live_candidate_audit_required")
    if not plan.live_human_enabled:
        blockers.append("activation.live_human_source_not_implemented")
    if plan.live_transport == "none":
        blockers.append("activation.live_transport_not_implemented")

    design_valid = not errors
    review_packet_ready = design_valid
    activation_ready = design_valid and not blockers
    return HumanPilotPreflightResult(
        design_valid=design_valid,
        review_packet_ready=review_packet_ready,
        activation_ready=activation_ready,
        errors=tuple(errors),
        activation_blockers=tuple(blockers),
    )


def validate_human_proposal_draft(
    request: CaregiverRequest,
    draft: HumanProposalDraft,
    *,
    allowed_observation_ids: frozenset[str] = frozenset(),
    allowed_objective_ids: frozenset[str] = frozenset(),
    allowed_action_ids: frozenset[str] = frozenset(),
) -> HumanProposalDraftValidation:
    """Validate a human-authored draft without creating a live proposal.

    Only explicitly supplied development-visible identifiers may be referenced.
    Protected evaluator contents are therefore not part of this validation input.
    The Pilot v1 proposal-size limit is fixed and cannot be overridden by callers.
    """
    errors: list[str] = []

    if not request.request_id:
        errors.append("request.request_id")
    if request.sequence_ordinal < 0:
        errors.append("request.sequence_ordinal")
    allowed_kinds_valid = bool(request.allowed_kinds) and all(
        type(item) is ProposalKind for item in request.allowed_kinds
    )
    if not allowed_kinds_valid or len(set(request.allowed_kinds)) != len(request.allowed_kinds):
        errors.append("request.allowed_kinds")

    if not draft.draft_id:
        errors.append("draft.draft_id")
    if not _is_pseudonymous_caregiver_id(draft.caregiver_id):
        errors.append("draft.caregiver_id")
    if draft.request_id != request.request_id:
        errors.append("draft.request_id")
    if draft.sequence_ordinal != request.sequence_ordinal:
        errors.append("draft.sequence_ordinal")
    if type(draft.kind) is not ProposalKind:
        errors.append("draft.kind")
    elif allowed_kinds_valid and draft.kind not in request.allowed_kinds:
        errors.append("draft.kind_not_allowed")
    if type(draft.confidence) is not CaregiverConfidence:
        errors.append("draft.confidence")

    payload = draft.text.strip()
    payload_bytes = payload.encode("utf-8")
    if not payload:
        errors.append("draft.payload_empty")
    if len(payload_bytes) > PROPOSED_MAX_PROPOSAL_BYTES:
        errors.append("draft.payload_too_large")

    for name, values, allowed in (
        ("observation_ids", draft.observation_ids, allowed_observation_ids),
        ("objective_ids", draft.objective_ids, allowed_objective_ids),
        ("action_ids", draft.action_ids, allowed_action_ids),
    ):
        if len(values) != len(set(values)):
            errors.append(f"draft.{name}.duplicate")
        if any(not value for value in values):
            errors.append(f"draft.{name}.empty")
        if not set(values).issubset(allowed):
            errors.append(f"draft.{name}.not_allowed")

    if draft.clarification_of_proposal_id is not None and not draft.clarification_of_proposal_id.startswith("proposal:"):
        errors.append("draft.clarification_of_proposal_id")
    if draft.contains_personal_data:
        errors.append("draft.personal_data_forbidden")
    if draft.contains_secret:
        errors.append("draft.secret_forbidden")
    if draft.contains_third_party_confidential_data:
        errors.append("draft.third_party_confidential_data_forbidden")

    digest = hashlib.sha256(payload_bytes).hexdigest() if payload else None
    return HumanProposalDraftValidation(
        valid=not errors,
        errors=tuple(errors),
        payload_sha256=digest,
    )
