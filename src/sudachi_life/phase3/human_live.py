from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from .caregiver import (
    AccountingStatus,
    CaregiverAccounting,
    CaregiverProposal,
    CaregiverRequest,
    CaregiverSourceKind,
    ProposalAuthority,
    proposal_from_text,
    validate_proposal,
)
from .human_pilot import (
    PROPOSED_MAX_ATTEMPT_WALL_MS,
    PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT,
    PROPOSED_MAX_CLARIFICATIONS_PER_ATTEMPT,
    PROPOSED_MAX_CONSULTATIONS_PER_ATTEMPT,
    PROPOSED_MAX_RESPONSE_LATENCY_MS,
    PROPOSED_PROPOSAL_PAYLOAD_RETENTION_DAYS,
    EthicsReviewStatus,
    HumanProposalDraft,
    validate_human_proposal_draft,
)

HUMAN_PILOT_LIVE_BRIDGE_VERSION = "sudachi.phase3.human_caregiver_live_bridge/v1"
SELF_HUMAN_PILOT_ID = "pilot:human-caregiver-v1-self"
LOCAL_STRUCTURED_HUMAN_TRANSPORT = "local_structured_manual"


@dataclass(frozen=True, slots=True)
class SelfHumanPilotAuthorization:
    protocol_version: str
    pilot_id: str
    attempt_id: str
    caregiver_id: str
    source_kind: CaregiverSourceKind
    transport: str
    project_owner_is_caregiver: bool
    self_only: bool
    ethics_review_status: EthicsReviewStatus
    consent_attested: bool
    consent_revocable: bool
    raw_chat_transcript_retained: bool
    public_raw_payload_default: bool
    proposal_payload_retention_days: int
    third_party_participants: int


@dataclass(frozen=True, slots=True)
class HumanPilotAttemptState:
    consultations_used: int = 0
    clarifications_used: int = 0
    caregiver_active_ms_used: int = 0
    attempt_elapsed_ms: int = 0
    live_enabled: bool = True
    disabled_at_elapsed_ms: int | None = None


@dataclass(frozen=True, slots=True)
class HumanConsultationMeasurement:
    latency_ms: int
    caregiver_active_ms: int
    attempt_elapsed_ms: int
    source_timestamp: str
    is_clarification: bool = False


@dataclass(frozen=True, slots=True)
class HumanBridgeResult:
    accepted: bool
    errors: tuple[str, ...]
    proposal: CaregiverProposal | None
    state: HumanPilotAttemptState


def _is_pseudonymous_caregiver_id(value: str) -> bool:
    prefix = "caregiver:pseudo:"
    if not value.startswith(prefix):
        return False
    token = value[len(prefix) :]
    return len(token) == 32 and all(ch in "0123456789abcdef" for ch in token)


def _is_offset_timestamp(value: str) -> bool:
    if not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def accepted_self_human_pilot_v1_authorization(
    *,
    attempt_id: str,
    caregiver_id: str,
) -> SelfHumanPilotAuthorization:
    """Return the owner-approved self-only Pilot v1 live authorization record.

    This function does not perform I/O or contact any external service. The only
    live source it authorizes is the project owner supplying a structured draft
    locally for the single bound attempt.
    """
    return SelfHumanPilotAuthorization(
        protocol_version=HUMAN_PILOT_LIVE_BRIDGE_VERSION,
        pilot_id=SELF_HUMAN_PILOT_ID,
        attempt_id=attempt_id,
        caregiver_id=caregiver_id,
        source_kind=CaregiverSourceKind.HUMAN,
        transport=LOCAL_STRUCTURED_HUMAN_TRANSPORT,
        project_owner_is_caregiver=True,
        self_only=True,
        ethics_review_status=EthicsReviewStatus.NOT_REQUIRED_DECLARED,
        consent_attested=True,
        consent_revocable=True,
        raw_chat_transcript_retained=False,
        public_raw_payload_default=False,
        proposal_payload_retention_days=PROPOSED_PROPOSAL_PAYLOAD_RETENTION_DAYS,
        third_party_participants=0,
    )


def validate_self_human_pilot_authorization(
    authorization: SelfHumanPilotAuthorization,
) -> tuple[str, ...]:
    errors: list[str] = []

    if authorization.protocol_version != HUMAN_PILOT_LIVE_BRIDGE_VERSION:
        errors.append("authorization.protocol_version")
    if authorization.pilot_id != SELF_HUMAN_PILOT_ID:
        errors.append("authorization.pilot_id")
    if not authorization.attempt_id:
        errors.append("authorization.attempt_id")
    if not _is_pseudonymous_caregiver_id(authorization.caregiver_id):
        errors.append("authorization.caregiver_id")
    if authorization.source_kind is not CaregiverSourceKind.HUMAN:
        errors.append("authorization.source_kind")
    if authorization.transport != LOCAL_STRUCTURED_HUMAN_TRANSPORT:
        errors.append("authorization.transport")
    if not authorization.project_owner_is_caregiver:
        errors.append("authorization.owner_is_caregiver")
    if not authorization.self_only:
        errors.append("authorization.self_only")
    if authorization.ethics_review_status is not EthicsReviewStatus.NOT_REQUIRED_DECLARED:
        errors.append("authorization.ethics_review_status")
    if not authorization.consent_attested:
        errors.append("authorization.consent_attested")
    if not authorization.consent_revocable:
        errors.append("authorization.consent_revocable")
    if authorization.raw_chat_transcript_retained:
        errors.append("authorization.raw_chat_transcript")
    if authorization.public_raw_payload_default:
        errors.append("authorization.public_raw_payload")
    if authorization.proposal_payload_retention_days != PROPOSED_PROPOSAL_PAYLOAD_RETENTION_DAYS:
        errors.append("authorization.retention_days")
    if authorization.third_party_participants != 0:
        errors.append("authorization.third_party_participants")

    return tuple(errors)


def start_self_human_pilot_attempt() -> HumanPilotAttemptState:
    return HumanPilotAttemptState()


def disable_self_human_bridge(
    state: HumanPilotAttemptState,
    *,
    attempt_elapsed_ms: int,
) -> HumanPilotAttemptState:
    if attempt_elapsed_ms < state.attempt_elapsed_ms:
        raise ValueError("disablement elapsed time cannot move backwards")
    if attempt_elapsed_ms > PROPOSED_MAX_ATTEMPT_WALL_MS:
        raise ValueError("disablement exceeds attempt wall budget")
    return replace(
        state,
        attempt_elapsed_ms=attempt_elapsed_ms,
        live_enabled=False,
        disabled_at_elapsed_ms=attempt_elapsed_ms,
    )


def accept_self_human_proposal(
    *,
    authorization: SelfHumanPilotAuthorization,
    state: HumanPilotAttemptState,
    request: CaregiverRequest,
    draft: HumanProposalDraft,
    measurement: HumanConsultationMeasurement,
    allowed_observation_ids: frozenset[str] = frozenset(),
    allowed_objective_ids: frozenset[str] = frozenset(),
    allowed_action_ids: frozenset[str] = frozenset(),
) -> HumanBridgeResult:
    """Convert one validated self-caregiver draft into a proposal-only live proposal.

    The bridge performs no network, subprocess, browser, credential, filesystem,
    or external-service access. A caller supplies the already human-attested
    structured draft and measured timing values locally.
    """
    errors = list(validate_self_human_pilot_authorization(authorization))

    if not state.live_enabled:
        errors.append("bridge.disabled")
    if state.disabled_at_elapsed_ms is not None:
        errors.append("bridge.disablement_state")
    if request.attempt_id != authorization.attempt_id:
        errors.append("bridge.attempt_binding")
    if draft.caregiver_id != authorization.caregiver_id:
        errors.append("bridge.caregiver_binding")

    draft_validation = validate_human_proposal_draft(
        request,
        draft,
        allowed_observation_ids=allowed_observation_ids,
        allowed_objective_ids=allowed_objective_ids,
        allowed_action_ids=allowed_action_ids,
    )
    errors.extend(f"bridge.{error}" for error in draft_validation.errors)

    if measurement.latency_ms < 0:
        errors.append("bridge.latency_negative")
    elif measurement.latency_ms > PROPOSED_MAX_RESPONSE_LATENCY_MS:
        errors.append("bridge.latency_budget")
    if measurement.caregiver_active_ms < 0:
        errors.append("bridge.active_ms_negative")
    if measurement.attempt_elapsed_ms < state.attempt_elapsed_ms:
        errors.append("bridge.elapsed_time_regression")
    elif measurement.attempt_elapsed_ms > PROPOSED_MAX_ATTEMPT_WALL_MS:
        errors.append("bridge.attempt_wall_budget")
    if not _is_offset_timestamp(measurement.source_timestamp):
        errors.append("bridge.source_timestamp")

    is_linked_clarification = draft.clarification_of_proposal_id is not None
    if measurement.is_clarification != is_linked_clarification:
        errors.append("bridge.clarification_binding")

    next_consultations = state.consultations_used + 1
    next_clarifications = state.clarifications_used + int(measurement.is_clarification)
    next_active_ms = state.caregiver_active_ms_used + measurement.caregiver_active_ms

    if next_consultations > PROPOSED_MAX_CONSULTATIONS_PER_ATTEMPT:
        errors.append("bridge.consultation_budget")
    if next_clarifications > PROPOSED_MAX_CLARIFICATIONS_PER_ATTEMPT:
        errors.append("bridge.clarification_budget")
    if next_active_ms > PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT:
        errors.append("bridge.active_time_budget")

    if errors:
        return HumanBridgeResult(
            accepted=False,
            errors=tuple(errors),
            proposal=None,
            state=state,
        )

    accounting = CaregiverAccounting(
        consultation_count=1,
        clarification_count=int(measurement.is_clarification),
        latency_ms=measurement.latency_ms,
        human_active_ms=measurement.caregiver_active_ms,
        model_calls=None,
        money_minor_units=None,
        live_cost_status=AccountingStatus.MEASURED,
        absence_reason=None,
    )
    proposal = proposal_from_text(
        request=request,
        source_id=authorization.caregiver_id,
        source_kind=CaregiverSourceKind.HUMAN,
        kind=draft.kind,
        text=draft.text,
        accounting=accounting,
        source_timestamp=measurement.source_timestamp,
    )

    # The generic source-neutral validator deliberately remains fixture-only.
    # A human proposal is acceptable here only if its sole generic-validation
    # failure is exactly the expected live-source authorization error and every
    # self-pilot gate above has passed.
    generic_validation = validate_proposal(request, proposal)
    unexpected_generic_errors = tuple(
        error
        for error in generic_validation.errors
        if error != "proposal.live_source_not_authorized"
    )
    if "proposal.live_source_not_authorized" not in generic_validation.errors:
        unexpected_generic_errors += ("proposal.expected_global_rejection_missing",)
    if unexpected_generic_errors:
        return HumanBridgeResult(
            accepted=False,
            errors=tuple(f"bridge.{error}" for error in unexpected_generic_errors),
            proposal=None,
            state=state,
        )

    if proposal.authority is not ProposalAuthority.PROPOSAL_ONLY:
        return HumanBridgeResult(
            accepted=False,
            errors=("bridge.proposal_authority",),
            proposal=None,
            state=state,
        )
    if proposal.source_kind is not CaregiverSourceKind.HUMAN:
        return HumanBridgeResult(
            accepted=False,
            errors=("bridge.proposal_source_kind",),
            proposal=None,
            state=state,
        )
    if draft_validation.payload_sha256 != proposal.payload_sha256:
        return HumanBridgeResult(
            accepted=False,
            errors=("bridge.payload_digest",),
            proposal=None,
            state=state,
        )

    next_state = HumanPilotAttemptState(
        consultations_used=next_consultations,
        clarifications_used=next_clarifications,
        caregiver_active_ms_used=next_active_ms,
        attempt_elapsed_ms=measurement.attempt_elapsed_ms,
        live_enabled=True,
        disabled_at_elapsed_ms=None,
    )
    return HumanBridgeResult(
        accepted=True,
        errors=(),
        proposal=proposal,
        state=next_state,
    )
