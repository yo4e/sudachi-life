from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from threading import RLock

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
    PROPOSED_PILOT_ATTEMPTS,
    PROPOSED_PROPOSAL_PAYLOAD_RETENTION_DAYS,
    EthicsReviewStatus,
    HumanProposalDraft,
    validate_human_proposal_draft,
)

HUMAN_PILOT_LIVE_BRIDGE_VERSION = "sudachi.phase3.human_caregiver_live_bridge/v1"
SELF_HUMAN_PILOT_ID = "pilot:human-caregiver-v1-self"
LOCAL_STRUCTURED_HUMAN_TRANSPORT = "local_structured_manual"
SELF_HUMAN_AUTHORIZATION_RECORD = "github:yo4e/sudachi-life/issues/158"
SELF_HUMAN_CONSENT_NOTICE_VERSION = "sudachi.phase3.self_human_consent/v1"
SELF_HUMAN_ATTEMPT_ID = "attempt:self-human-pilot-v1-001"
SELF_HUMAN_CAREGIVER_ID = "caregiver:pseudo:0123456789abcdef0123456789abcdef"


@dataclass(frozen=True, slots=True)
class SelfHumanPilotAuthorization:
    protocol_version: str
    pilot_id: str
    attempt_id: str
    caregiver_id: str
    source_kind: CaregiverSourceKind
    transport: str
    authorization_record: str
    consent_notice_version: str
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
    attempt_id: str
    generation: int = 0
    consultations_used: int = 0
    clarifications_used: int = 0
    caregiver_active_ms_used: int = 0
    attempt_elapsed_ms: int = 0
    live_enabled: bool = True
    disabled_at_elapsed_ms: int | None = None
    accepted_request_ids: tuple[str, ...] = ()
    accepted_proposal_ids: tuple[str, ...] = ()


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


_SESSION_LOCK = RLock()
_AUTHORITATIVE_STATE: HumanPilotAttemptState | None = None


def _is_offset_timestamp(value: str) -> bool:
    if not value:
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def _validate_attempt_state(state: HumanPilotAttemptState) -> tuple[str, ...]:
    errors: list[str] = []
    if state.attempt_id != SELF_HUMAN_ATTEMPT_ID:
        errors.append("state.attempt_id")

    integer_fields = (
        ("generation", state.generation, None),
        ("consultations_used", state.consultations_used, PROPOSED_MAX_CONSULTATIONS_PER_ATTEMPT),
        ("clarifications_used", state.clarifications_used, PROPOSED_MAX_CLARIFICATIONS_PER_ATTEMPT),
        ("caregiver_active_ms_used", state.caregiver_active_ms_used, PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT),
        ("attempt_elapsed_ms", state.attempt_elapsed_ms, PROPOSED_MAX_ATTEMPT_WALL_MS),
    )
    for name, value, maximum in integer_fields:
        if type(value) is not int or value < 0 or (maximum is not None and value > maximum):
            errors.append(f"state.{name}")

    if type(state.live_enabled) is not bool:
        errors.append("state.live_enabled")
    if state.clarifications_used > state.consultations_used:
        errors.append("state.clarifications_exceed_consultations")
    if len(state.accepted_request_ids) != state.consultations_used:
        errors.append("state.request_count")
    if len(state.accepted_proposal_ids) != state.consultations_used:
        errors.append("state.proposal_count")
    if len(set(state.accepted_request_ids)) != len(state.accepted_request_ids):
        errors.append("state.request_ids_duplicate")
    if len(set(state.accepted_proposal_ids)) != len(state.accepted_proposal_ids):
        errors.append("state.proposal_ids_duplicate")
    if any(not value for value in state.accepted_request_ids):
        errors.append("state.request_id_empty")
    if any(not value.startswith("proposal:") for value in state.accepted_proposal_ids):
        errors.append("state.proposal_id_shape")

    if state.live_enabled:
        if state.disabled_at_elapsed_ms is not None:
            errors.append("state.enabled_with_disablement")
    else:
        if type(state.disabled_at_elapsed_ms) is not int:
            errors.append("state.disabled_without_timestamp")
        elif state.disabled_at_elapsed_ms != state.attempt_elapsed_ms:
            errors.append("state.disablement_timestamp")

    return tuple(errors)


def accepted_self_human_pilot_v1_authorization() -> SelfHumanPilotAuthorization:
    """Return the one exact owner-approved self-only Pilot v1 authorization."""
    return SelfHumanPilotAuthorization(
        protocol_version=HUMAN_PILOT_LIVE_BRIDGE_VERSION,
        pilot_id=SELF_HUMAN_PILOT_ID,
        attempt_id=SELF_HUMAN_ATTEMPT_ID,
        caregiver_id=SELF_HUMAN_CAREGIVER_ID,
        source_kind=CaregiverSourceKind.HUMAN,
        transport=LOCAL_STRUCTURED_HUMAN_TRANSPORT,
        authorization_record=SELF_HUMAN_AUTHORIZATION_RECORD,
        consent_notice_version=SELF_HUMAN_CONSENT_NOTICE_VERSION,
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

    if PROPOSED_PILOT_ATTEMPTS != 1:
        errors.append("authorization.pilot_attempt_count")
    if authorization.protocol_version != HUMAN_PILOT_LIVE_BRIDGE_VERSION:
        errors.append("authorization.protocol_version")
    if authorization.pilot_id != SELF_HUMAN_PILOT_ID:
        errors.append("authorization.pilot_id")
    if authorization.attempt_id != SELF_HUMAN_ATTEMPT_ID:
        errors.append("authorization.attempt_id")
    if authorization.caregiver_id != SELF_HUMAN_CAREGIVER_ID:
        errors.append("authorization.caregiver_id")
    if authorization.source_kind is not CaregiverSourceKind.HUMAN:
        errors.append("authorization.source_kind")
    if authorization.transport != LOCAL_STRUCTURED_HUMAN_TRANSPORT:
        errors.append("authorization.transport")
    if authorization.authorization_record != SELF_HUMAN_AUTHORIZATION_RECORD:
        errors.append("authorization.record")
    if authorization.consent_notice_version != SELF_HUMAN_CONSENT_NOTICE_VERSION:
        errors.append("authorization.consent_notice_version")
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


def start_self_human_pilot_attempt(
    *, authorization: SelfHumanPilotAuthorization
) -> HumanPilotAttemptState:
    """Start the one process-authoritative Pilot v1 attempt exactly once."""
    authorization_errors = validate_self_human_pilot_authorization(authorization)
    if authorization_errors:
        raise ValueError(f"invalid authorization: {authorization_errors}")

    global _AUTHORITATIVE_STATE
    with _SESSION_LOCK:
        if _AUTHORITATIVE_STATE is not None:
            raise RuntimeError("self-human Pilot v1 attempt already started in this process")
        _AUTHORITATIVE_STATE = HumanPilotAttemptState(attempt_id=SELF_HUMAN_ATTEMPT_ID)
        return _AUTHORITATIVE_STATE


def _current_state_or(state: HumanPilotAttemptState) -> HumanPilotAttemptState:
    return _AUTHORITATIVE_STATE if _AUTHORITATIVE_STATE is not None else state


def disable_self_human_bridge(
    *,
    authorization: SelfHumanPilotAuthorization,
    state: HumanPilotAttemptState,
    attempt_elapsed_ms: int,
) -> HumanPilotAttemptState:
    authorization_errors = validate_self_human_pilot_authorization(authorization)
    if authorization_errors:
        raise ValueError(f"invalid authorization: {authorization_errors}")

    global _AUTHORITATIVE_STATE
    with _SESSION_LOCK:
        if _AUTHORITATIVE_STATE is None:
            raise RuntimeError("self-human Pilot v1 attempt has not started")
        if state != _AUTHORITATIVE_STATE:
            raise ValueError("stale or forked attempt state")
        state_errors = _validate_attempt_state(_AUTHORITATIVE_STATE)
        if state_errors:
            raise ValueError(f"invalid authoritative attempt state: {state_errors}")
        if not _AUTHORITATIVE_STATE.live_enabled:
            raise ValueError("bridge is already disabled")
        if type(attempt_elapsed_ms) is not int:
            raise TypeError("disablement elapsed time must be int")
        if attempt_elapsed_ms < _AUTHORITATIVE_STATE.attempt_elapsed_ms:
            raise ValueError("disablement elapsed time cannot move backwards")
        if attempt_elapsed_ms > PROPOSED_MAX_ATTEMPT_WALL_MS:
            raise ValueError("disablement exceeds attempt wall budget")

        _AUTHORITATIVE_STATE = replace(
            _AUTHORITATIVE_STATE,
            generation=_AUTHORITATIVE_STATE.generation + 1,
            attempt_elapsed_ms=attempt_elapsed_ms,
            live_enabled=False,
            disabled_at_elapsed_ms=attempt_elapsed_ms,
        )
        return _AUTHORITATIVE_STATE


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
    """Accept one local structured self-caregiver draft against authoritative state.

    The bridge performs no network, subprocess, browser, credential, filesystem,
    or external-service access. State progression is process-authoritative and
    atomic: stale, fresh-reset, or forked snapshots cannot advance the attempt.
    """
    global _AUTHORITATIVE_STATE
    with _SESSION_LOCK:
        errors = list(validate_self_human_pilot_authorization(authorization))
        if _AUTHORITATIVE_STATE is None:
            errors.append("bridge.attempt_not_started")
            authoritative = state
        else:
            authoritative = _AUTHORITATIVE_STATE
            if state != authoritative:
                errors.append("bridge.stale_or_forked_state")
            errors.extend(f"bridge.{error}" for error in _validate_attempt_state(authoritative))

        if not authoritative.live_enabled:
            errors.append("bridge.disabled")
        if request.attempt_id != authorization.attempt_id:
            errors.append("bridge.attempt_binding")
        if request.request_id in authoritative.accepted_request_ids:
            errors.append("bridge.request_replay")
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

        measurement_ints = (
            ("latency_ms", measurement.latency_ms),
            ("caregiver_active_ms", measurement.caregiver_active_ms),
            ("attempt_elapsed_ms", measurement.attempt_elapsed_ms),
        )
        for name, value in measurement_ints:
            if type(value) is not int:
                errors.append(f"bridge.{name}_type")
        if type(measurement.is_clarification) is not bool:
            errors.append("bridge.is_clarification_type")

        elapsed_delta: int | None = None
        if type(measurement.attempt_elapsed_ms) is int:
            if measurement.attempt_elapsed_ms < authoritative.attempt_elapsed_ms:
                errors.append("bridge.elapsed_time_regression")
            elif measurement.attempt_elapsed_ms > PROPOSED_MAX_ATTEMPT_WALL_MS:
                errors.append("bridge.attempt_wall_budget")
            else:
                elapsed_delta = measurement.attempt_elapsed_ms - authoritative.attempt_elapsed_ms

        if type(measurement.latency_ms) is int:
            if measurement.latency_ms < 0:
                errors.append("bridge.latency_negative")
            elif measurement.latency_ms > PROPOSED_MAX_RESPONSE_LATENCY_MS:
                errors.append("bridge.latency_budget")
            elif elapsed_delta is not None and measurement.latency_ms > elapsed_delta:
                errors.append("bridge.latency_exceeds_elapsed")
        if type(measurement.caregiver_active_ms) is int:
            if measurement.caregiver_active_ms < 0:
                errors.append("bridge.active_ms_negative")
            elif elapsed_delta is not None and measurement.caregiver_active_ms > elapsed_delta:
                errors.append("bridge.active_ms_exceeds_elapsed")
        if not _is_offset_timestamp(measurement.source_timestamp):
            errors.append("bridge.source_timestamp")

        is_linked_clarification = draft.clarification_of_proposal_id is not None
        if type(measurement.is_clarification) is bool and measurement.is_clarification != is_linked_clarification:
            errors.append("bridge.clarification_binding")
        if is_linked_clarification and draft.clarification_of_proposal_id not in authoritative.accepted_proposal_ids:
            errors.append("bridge.clarification_source")

        next_consultations = authoritative.consultations_used + 1
        next_clarifications = authoritative.clarifications_used + int(measurement.is_clarification is True)
        next_active_ms = (
            authoritative.caregiver_active_ms_used + measurement.caregiver_active_ms
            if type(measurement.caregiver_active_ms) is int
            else authoritative.caregiver_active_ms_used
        )

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
                state=_current_state_or(state),
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

        generic_validation = validate_proposal(request, proposal)
        unexpected_generic_errors = tuple(
            error
            for error in generic_validation.errors
            if error != "proposal.live_source_not_authorized"
        )
        if "proposal.live_source_not_authorized" not in generic_validation.errors:
            unexpected_generic_errors += ("proposal.expected_global_rejection_missing",)
        if proposal.proposal_id in authoritative.accepted_proposal_ids:
            unexpected_generic_errors += ("proposal.replay",)
        if unexpected_generic_errors:
            return HumanBridgeResult(
                accepted=False,
                errors=tuple(f"bridge.{error}" for error in unexpected_generic_errors),
                proposal=None,
                state=authoritative,
            )

        if proposal.authority is not ProposalAuthority.PROPOSAL_ONLY:
            return HumanBridgeResult(False, ("bridge.proposal_authority",), None, authoritative)
        if proposal.source_kind is not CaregiverSourceKind.HUMAN:
            return HumanBridgeResult(False, ("bridge.proposal_source_kind",), None, authoritative)
        if draft_validation.payload_sha256 != proposal.payload_sha256:
            return HumanBridgeResult(False, ("bridge.payload_digest",), None, authoritative)

        _AUTHORITATIVE_STATE = HumanPilotAttemptState(
            attempt_id=SELF_HUMAN_ATTEMPT_ID,
            generation=authoritative.generation + 1,
            consultations_used=next_consultations,
            clarifications_used=next_clarifications,
            caregiver_active_ms_used=next_active_ms,
            attempt_elapsed_ms=measurement.attempt_elapsed_ms,
            live_enabled=True,
            disabled_at_elapsed_ms=None,
            accepted_request_ids=authoritative.accepted_request_ids + (request.request_id,),
            accepted_proposal_ids=authoritative.accepted_proposal_ids + (proposal.proposal_id,),
        )
        return HumanBridgeResult(
            accepted=True,
            errors=(),
            proposal=proposal,
            state=_AUTHORITATIVE_STATE,
        )
