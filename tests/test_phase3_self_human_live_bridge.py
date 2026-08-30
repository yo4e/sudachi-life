from __future__ import annotations

from dataclasses import replace

import pytest

from sudachi_life.phase3.caregiver import (
    ACTIVE_SOURCE_KINDS,
    AccountingStatus,
    CaregiverRequest,
    CaregiverSourceKind,
    ProposalAuthority,
    ProposalKind,
    validate_proposal,
)
from sudachi_life.phase3.human_live import (
    HUMAN_PILOT_LIVE_BRIDGE_VERSION,
    LOCAL_STRUCTURED_HUMAN_TRANSPORT,
    SELF_HUMAN_AUTHORIZATION_RECORD,
    SELF_HUMAN_CONSENT_NOTICE_VERSION,
    SELF_HUMAN_PILOT_ID,
    HumanConsultationMeasurement,
    HumanPilotAttemptState,
    accept_self_human_proposal,
    accepted_self_human_pilot_v1_authorization,
    disable_self_human_bridge,
    start_self_human_pilot_attempt,
    validate_self_human_pilot_authorization,
)
from sudachi_life.phase3.human_pilot import (
    PROPOSED_MAX_ATTEMPT_WALL_MS,
    PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT,
    PROPOSED_MAX_CLARIFICATIONS_PER_ATTEMPT,
    PROPOSED_MAX_CONSULTATIONS_PER_ATTEMPT,
    PROPOSED_MAX_RESPONSE_LATENCY_MS,
    CaregiverConfidence,
    EthicsReviewStatus,
    HumanProposalDraft,
)

_CAREGIVER_ID = "caregiver:pseudo:0123456789abcdef0123456789abcdef"
_ATTEMPT_ID = "attempt:self-human-pilot-v1-001"


def _authorization():
    return accepted_self_human_pilot_v1_authorization(
        attempt_id=_ATTEMPT_ID,
        caregiver_id=_CAREGIVER_ID,
    )


def _request(*, sequence_ordinal: int = 1) -> CaregiverRequest:
    return CaregiverRequest(
        request_id=f"request:self-human-{sequence_ordinal:03d}",
        study_id="study:self-human-pilot-v1",
        attempt_id=_ATTEMPT_ID,
        episode_id="episode:self-human-pilot-v1-001",
        organism_id="sudachi-self-human-v1",
        lineage_generation=0,
        sequence_ordinal=sequence_ordinal,
        allowed_kinds=(ProposalKind.EXPLANATION, ProposalKind.ABSTAIN),
    )


def _draft(*, sequence_ordinal: int = 1, **changes: object) -> HumanProposalDraft:
    values: dict[str, object] = {
        "draft_id": f"draft:self-human-{sequence_ordinal:03d}",
        "request_id": f"request:self-human-{sequence_ordinal:03d}",
        "caregiver_id": _CAREGIVER_ID,
        "sequence_ordinal": sequence_ordinal,
        "kind": ProposalKind.EXPLANATION,
        "text": "The visible marker supports inspecting before moving.",
        "confidence": CaregiverConfidence.MEDIUM,
        "observation_ids": ("observation:marker-visible",),
        "objective_ids": ("objective:reach-marker",),
        "action_ids": ("action:inspect", "action:move"),
    }
    values.update(changes)
    return HumanProposalDraft(**values)  # type: ignore[arg-type]


def _measurement(
    *,
    elapsed_ms: int = 30_000,
    latency_ms: int = 2_000,
    active_ms: int = 5_000,
    is_clarification: bool = False,
    timestamp: str = "2026-08-30T14:30:00+09:00",
) -> HumanConsultationMeasurement:
    return HumanConsultationMeasurement(
        latency_ms=latency_ms,
        caregiver_active_ms=active_ms,
        attempt_elapsed_ms=elapsed_ms,
        source_timestamp=timestamp,
        is_clarification=is_clarification,
    )


def _accept(
    *,
    authorization=None,
    state: HumanPilotAttemptState | None = None,
    request: CaregiverRequest | None = None,
    draft: HumanProposalDraft | None = None,
    measurement: HumanConsultationMeasurement | None = None,
):
    return accept_self_human_proposal(
        authorization=authorization or _authorization(),
        state=state or start_self_human_pilot_attempt(),
        request=request or _request(),
        draft=draft or _draft(),
        measurement=measurement or _measurement(),
        allowed_observation_ids=frozenset({"observation:marker-visible"}),
        allowed_objective_ids=frozenset({"objective:reach-marker"}),
        allowed_action_ids=frozenset({"action:inspect", "action:move"}),
    )


def _valid_used_state(*, consultations: int, clarifications: int = 0) -> HumanPilotAttemptState:
    request_ids = tuple(f"request:used:{index}" for index in range(consultations))
    proposal_ids = tuple(f"proposal:{index:064x}" for index in range(consultations))
    return HumanPilotAttemptState(
        consultations_used=consultations,
        clarifications_used=clarifications,
        caregiver_active_ms_used=10_000,
        attempt_elapsed_ms=20_000,
        accepted_request_ids=request_ids,
        accepted_proposal_ids=proposal_ids,
    )


def test_authorization_is_exact_self_only_owner_approved_scope() -> None:
    authorization = _authorization()

    assert authorization.protocol_version == HUMAN_PILOT_LIVE_BRIDGE_VERSION
    assert authorization.pilot_id == SELF_HUMAN_PILOT_ID
    assert authorization.transport == LOCAL_STRUCTURED_HUMAN_TRANSPORT
    assert authorization.authorization_record == SELF_HUMAN_AUTHORIZATION_RECORD
    assert authorization.consent_notice_version == SELF_HUMAN_CONSENT_NOTICE_VERSION
    assert authorization.project_owner_is_caregiver is True
    assert authorization.self_only is True
    assert authorization.ethics_review_status is EthicsReviewStatus.NOT_REQUIRED_DECLARED
    assert authorization.consent_attested is True
    assert authorization.consent_revocable is True
    assert authorization.third_party_participants == 0
    assert validate_self_human_pilot_authorization(authorization) == ()


def test_live_bridge_accepts_structured_self_human_proposal_only() -> None:
    result = _accept()

    assert result.accepted is True
    assert result.errors == ()
    assert result.proposal is not None
    proposal = result.proposal
    assert proposal.source_kind is CaregiverSourceKind.HUMAN
    assert proposal.source_id == _CAREGIVER_ID
    assert proposal.authority is ProposalAuthority.PROPOSAL_ONLY
    assert proposal.accounting.live_cost_status is AccountingStatus.MEASURED
    assert proposal.accounting.human_active_ms == 5_000
    assert proposal.accounting.latency_ms == 2_000
    assert proposal.accounting.model_calls is None
    assert proposal.accounting.money_minor_units is None
    assert result.state.consultations_used == 1
    assert result.state.caregiver_active_ms_used == 5_000
    assert result.state.accepted_request_ids == (_request().request_id,)
    assert result.state.accepted_proposal_ids == (proposal.proposal_id,)


def test_generic_validator_remains_fixture_only_and_rejects_live_human() -> None:
    result = _accept()
    assert result.proposal is not None

    generic = validate_proposal(_request(), result.proposal)

    assert generic.valid is False
    assert generic.errors == ("proposal.live_source_not_authorized",)
    assert ACTIVE_SOURCE_KINDS == frozenset({CaregiverSourceKind.FIXTURE})
    assert CaregiverSourceKind.HUMAN not in ACTIVE_SOURCE_KINDS


def test_wrong_attempt_or_caregiver_binding_fails_closed() -> None:
    wrong_request = replace(_request(), attempt_id="attempt:other")
    wrong_draft = _draft(caregiver_id="caregiver:pseudo:ffffffffffffffffffffffffffffffff")

    attempt_result = _accept(request=wrong_request)
    caregiver_result = _accept(draft=wrong_draft)

    assert "bridge.attempt_binding" in attempt_result.errors
    assert "bridge.caregiver_binding" in caregiver_result.errors
    assert attempt_result.proposal is None
    assert caregiver_result.proposal is None


def test_relaxed_or_non_self_authorization_fails_closed() -> None:
    authorization = _authorization()
    relaxed = replace(
        authorization,
        authorization_record="chat-only",
        consent_notice_version="unknown",
        self_only=False,
        project_owner_is_caregiver=False,
        consent_attested=False,
        ethics_review_status=EthicsReviewStatus.UNRESOLVED,
        raw_chat_transcript_retained=True,
        public_raw_payload_default=True,
        third_party_participants=1,
    )

    errors = validate_self_human_pilot_authorization(relaxed)
    result = _accept(authorization=relaxed)

    assert "authorization.record" in errors
    assert "authorization.consent_notice_version" in errors
    assert "authorization.self_only" in errors
    assert "authorization.owner_is_caregiver" in errors
    assert "authorization.consent_attested" in errors
    assert "authorization.ethics_review_status" in errors
    assert "authorization.raw_chat_transcript" in errors
    assert "authorization.public_raw_payload" in errors
    assert "authorization.third_party_participants" in errors
    assert result.accepted is False
    assert result.proposal is None


def test_privacy_and_visible_reference_violations_are_rejected() -> None:
    draft = _draft(
        contains_personal_data=True,
        contains_secret=True,
        contains_third_party_confidential_data=True,
        observation_ids=("observation:hidden",),
    )
    result = _accept(draft=draft)

    assert result.accepted is False
    assert "bridge.draft.personal_data_forbidden" in result.errors
    assert "bridge.draft.secret_forbidden" in result.errors
    assert "bridge.draft.third_party_confidential_data_forbidden" in result.errors
    assert "bridge.draft.observation_ids.not_allowed" in result.errors


def test_latency_active_time_and_wall_budgets_fail_closed() -> None:
    latency = _accept(
        measurement=_measurement(
            elapsed_ms=PROPOSED_MAX_RESPONSE_LATENCY_MS + 2,
            latency_ms=PROPOSED_MAX_RESPONSE_LATENCY_MS + 1,
        )
    )
    active = _accept(
        measurement=_measurement(
            elapsed_ms=PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT + 2,
            active_ms=PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT + 1,
        )
    )
    wall = _accept(
        measurement=_measurement(elapsed_ms=PROPOSED_MAX_ATTEMPT_WALL_MS + 1)
    )

    assert "bridge.latency_budget" in latency.errors
    assert "bridge.active_time_budget" in active.errors
    assert "bridge.attempt_wall_budget" in wall.errors


def test_measured_time_must_fit_inside_elapsed_attempt_interval() -> None:
    latency = _accept(measurement=_measurement(elapsed_ms=1_000, latency_ms=1_001, active_ms=500))
    active = _accept(measurement=_measurement(elapsed_ms=1_000, latency_ms=500, active_ms=1_001))

    assert "bridge.latency_exceeds_elapsed" in latency.errors
    assert "bridge.active_ms_exceeds_elapsed" in active.errors


def test_consultation_budget_is_aggregate_and_fixed() -> None:
    state = _valid_used_state(consultations=PROPOSED_MAX_CONSULTATIONS_PER_ATTEMPT)
    result = _accept(state=state, measurement=_measurement(elapsed_ms=25_000))

    assert result.accepted is False
    assert "bridge.consultation_budget" in result.errors
    assert result.state is state


def test_clarification_must_link_to_prior_accepted_proposal_and_budget() -> None:
    unlinked = _accept(measurement=_measurement(is_clarification=True))
    first = _accept()
    assert first.accepted is True
    assert first.proposal is not None

    linked_draft = _draft(
        sequence_ordinal=2,
        clarification_of_proposal_id=first.proposal.proposal_id,
    )
    linked = _accept(
        state=first.state,
        request=_request(sequence_ordinal=2),
        draft=linked_draft,
        measurement=_measurement(elapsed_ms=40_000, is_clarification=True),
    )

    exhausted_state = _valid_used_state(
        consultations=2,
        clarifications=PROPOSED_MAX_CLARIFICATIONS_PER_ATTEMPT,
    )
    exhausted_draft = _draft(
        sequence_ordinal=3,
        clarification_of_proposal_id=exhausted_state.accepted_proposal_ids[0],
    )
    exhausted = _accept(
        state=exhausted_state,
        request=_request(sequence_ordinal=3),
        draft=exhausted_draft,
        measurement=_measurement(elapsed_ms=40_000, is_clarification=True),
    )

    assert "bridge.clarification_binding" in unlinked.errors
    assert linked.accepted is True
    assert linked.state.clarifications_used == 1
    assert "bridge.clarification_budget" in exhausted.errors


def test_unknown_clarification_source_fails_closed() -> None:
    first = _accept()
    unknown = _draft(
        sequence_ordinal=2,
        clarification_of_proposal_id="proposal:" + "f" * 64,
    )
    result = _accept(
        state=first.state,
        request=_request(sequence_ordinal=2),
        draft=unknown,
        measurement=_measurement(elapsed_ms=40_000, is_clarification=True),
    )

    assert result.accepted is False
    assert "bridge.clarification_source" in result.errors


def test_request_replay_is_rejected() -> None:
    first = _accept()
    replay = _accept(
        state=first.state,
        measurement=_measurement(elapsed_ms=40_000),
    )

    assert replay.accepted is False
    assert "bridge.request_replay" in replay.errors


def test_tampered_aggregate_state_fails_closed() -> None:
    negative = HumanPilotAttemptState(consultations_used=-1)
    count_mismatch = HumanPilotAttemptState(
        consultations_used=1,
        accepted_request_ids=(),
        accepted_proposal_ids=(),
    )

    negative_result = _accept(state=negative)
    mismatch_result = _accept(state=count_mismatch)

    assert "bridge.state.consultations_used" in negative_result.errors
    assert "bridge.state.request_count" in mismatch_result.errors
    assert "bridge.state.proposal_count" in mismatch_result.errors


def test_measurement_bool_masquerading_as_integer_fails_closed() -> None:
    measurement = HumanConsultationMeasurement(
        latency_ms=True,  # type: ignore[arg-type]
        caregiver_active_ms=1,
        attempt_elapsed_ms=10,
        source_timestamp="2026-08-30T14:30:00+09:00",
    )
    result = _accept(measurement=measurement)

    assert result.accepted is False
    assert "bridge.latency_ms_type" in result.errors


def test_offset_timestamp_is_required_for_live_provenance() -> None:
    naive = _accept(measurement=_measurement(timestamp="2026-08-30T14:30:00"))
    malformed = _accept(measurement=_measurement(timestamp="not-a-time"))

    assert "bridge.source_timestamp" in naive.errors
    assert "bridge.source_timestamp" in malformed.errors


def test_disablement_technically_prevents_post_cutoff_proposals() -> None:
    accepted = _accept()
    disabled = disable_self_human_bridge(accepted.state, attempt_elapsed_ms=40_000)
    after_cutoff = _accept(
        state=disabled,
        request=_request(sequence_ordinal=2),
        draft=_draft(sequence_ordinal=2),
        measurement=_measurement(elapsed_ms=50_000),
    )

    assert disabled.live_enabled is False
    assert disabled.disabled_at_elapsed_ms == 40_000
    assert after_cutoff.accepted is False
    assert "bridge.disabled" in after_cutoff.errors
    assert after_cutoff.proposal is None


def test_disablement_time_cannot_regress_or_exceed_wall_budget() -> None:
    state = replace(start_self_human_pilot_attempt(), attempt_elapsed_ms=20_000)

    with pytest.raises(ValueError):
        disable_self_human_bridge(state, attempt_elapsed_ms=19_999)
    with pytest.raises(ValueError):
        disable_self_human_bridge(
            state,
            attempt_elapsed_ms=PROPOSED_MAX_ATTEMPT_WALL_MS + 1,
        )


def test_elapsed_time_cannot_move_backwards_between_consultations() -> None:
    state = replace(start_self_human_pilot_attempt(), attempt_elapsed_ms=30_000)
    result = _accept(state=state, measurement=_measurement(elapsed_ms=29_999))

    assert result.accepted is False
    assert "bridge.elapsed_time_regression" in result.errors


def test_live_bridge_exposes_no_direct_execution_or_model_authority() -> None:
    result = _accept()
    assert result.proposal is not None

    proposal = result.proposal
    assert not hasattr(proposal, "execute")
    assert not hasattr(proposal, "command")
    assert not hasattr(proposal, "writer")
    assert proposal.accounting.model_calls is None
    assert proposal.accounting.money_minor_units is None
