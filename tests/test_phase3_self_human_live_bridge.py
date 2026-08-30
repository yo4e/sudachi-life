from __future__ import annotations

from dataclasses import replace

import pytest

import sudachi_life.phase3.human_live as live_module
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
    SELF_HUMAN_ATTEMPT_ID,
    SELF_HUMAN_AUTHORIZATION_RECORD,
    SELF_HUMAN_CAREGIVER_ID,
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


@pytest.fixture(autouse=True)
def _reset_process_authoritative_state():
    with live_module._SESSION_LOCK:
        live_module._AUTHORITATIVE_STATE = None
    yield
    with live_module._SESSION_LOCK:
        live_module._AUTHORITATIVE_STATE = None


def _authorization():
    return accepted_self_human_pilot_v1_authorization()


def _request(*, sequence_ordinal: int = 1) -> CaregiverRequest:
    return CaregiverRequest(
        request_id=f"request:self-human-{sequence_ordinal:03d}",
        study_id="study:self-human-pilot-v1",
        attempt_id=SELF_HUMAN_ATTEMPT_ID,
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
        "caregiver_id": SELF_HUMAN_CAREGIVER_ID,
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


def _start():
    return start_self_human_pilot_attempt(authorization=_authorization())


def _accept(
    *,
    authorization=None,
    state: HumanPilotAttemptState | None = None,
    request: CaregiverRequest | None = None,
    draft: HumanProposalDraft | None = None,
    measurement: HumanConsultationMeasurement | None = None,
):
    actual_state = state if state is not None else _start()
    return accept_self_human_proposal(
        authorization=authorization or _authorization(),
        state=actual_state,
        request=request or _request(),
        draft=draft or _draft(),
        measurement=measurement or _measurement(),
        allowed_observation_ids=frozenset({"observation:marker-visible"}),
        allowed_objective_ids=frozenset({"objective:reach-marker"}),
        allowed_action_ids=frozenset({"action:inspect", "action:move"}),
    )


def test_authorization_is_one_exact_attempt_and_caregiver() -> None:
    authorization = _authorization()

    assert authorization.protocol_version == HUMAN_PILOT_LIVE_BRIDGE_VERSION
    assert authorization.pilot_id == SELF_HUMAN_PILOT_ID
    assert authorization.attempt_id == SELF_HUMAN_ATTEMPT_ID
    assert authorization.caregiver_id == SELF_HUMAN_CAREGIVER_ID
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


def test_second_attempt_or_caregiver_cannot_mint_equivalent_authorization() -> None:
    authorization = _authorization()

    wrong_attempt = replace(authorization, attempt_id="attempt:self-human-pilot-v1-002")
    wrong_caregiver = replace(
        authorization,
        caregiver_id="caregiver:pseudo:ffffffffffffffffffffffffffffffff",
    )

    assert "authorization.attempt_id" in validate_self_human_pilot_authorization(wrong_attempt)
    assert "authorization.caregiver_id" in validate_self_human_pilot_authorization(wrong_caregiver)


def test_attempt_start_is_process_authoritative_and_one_shot() -> None:
    authorization = _authorization()
    first = start_self_human_pilot_attempt(authorization=authorization)

    assert first.attempt_id == SELF_HUMAN_ATTEMPT_ID
    assert first.generation == 0
    with pytest.raises(RuntimeError):
        start_self_human_pilot_attempt(authorization=authorization)


def test_live_bridge_accepts_structured_self_human_proposal_only() -> None:
    state = _start()
    result = _accept(state=state)

    assert result.accepted is True
    assert result.errors == ()
    assert result.proposal is not None
    proposal = result.proposal
    assert proposal.source_kind is CaregiverSourceKind.HUMAN
    assert proposal.source_id == SELF_HUMAN_CAREGIVER_ID
    assert proposal.authority is ProposalAuthority.PROPOSAL_ONLY
    assert proposal.accounting.live_cost_status is AccountingStatus.MEASURED
    assert proposal.accounting.human_active_ms == 5_000
    assert proposal.accounting.latency_ms == 2_000
    assert proposal.accounting.model_calls is None
    assert proposal.accounting.money_minor_units is None
    assert result.state.generation == 1
    assert result.state.consultations_used == 1
    assert result.state.accepted_request_ids == (_request().request_id,)
    assert result.state.accepted_proposal_ids == (proposal.proposal_id,)


def test_generic_validator_remains_fixture_only() -> None:
    state = _start()
    result = _accept(state=state)
    assert result.proposal is not None

    generic = validate_proposal(_request(), result.proposal)

    assert generic.valid is False
    assert generic.errors == ("proposal.live_source_not_authorized",)
    assert ACTIVE_SOURCE_KINDS == frozenset({CaregiverSourceKind.FIXTURE})
    assert CaregiverSourceKind.HUMAN not in ACTIVE_SOURCE_KINDS


def test_fresh_state_reset_is_rejected_after_progress() -> None:
    state0 = _start()
    first = _accept(state=state0)
    assert first.accepted is True

    forged_fresh = HumanPilotAttemptState(attempt_id=SELF_HUMAN_ATTEMPT_ID)
    replay = _accept(
        state=forged_fresh,
        request=_request(sequence_ordinal=2),
        draft=_draft(sequence_ordinal=2),
        measurement=_measurement(elapsed_ms=40_000),
    )

    assert replay.accepted is False
    assert "bridge.stale_or_forked_state" in replay.errors
    assert replay.state == first.state


def test_parallel_fork_from_same_prior_state_is_rejected() -> None:
    state0 = _start()
    first = _accept(state=state0)
    assert first.accepted is True

    fork = _accept(
        state=state0,
        request=_request(sequence_ordinal=2),
        draft=_draft(sequence_ordinal=2),
        measurement=_measurement(elapsed_ms=40_000),
    )

    assert fork.accepted is False
    assert "bridge.stale_or_forked_state" in fork.errors
    assert fork.state == first.state


def test_stale_enabled_state_cannot_bypass_disablement() -> None:
    state0 = _start()
    first = _accept(state=state0)
    disabled = disable_self_human_bridge(
        authorization=_authorization(),
        state=first.state,
        attempt_elapsed_ms=40_000,
    )

    stale_after_disable = _accept(
        state=first.state,
        request=_request(sequence_ordinal=2),
        draft=_draft(sequence_ordinal=2),
        measurement=_measurement(elapsed_ms=50_000),
    )

    assert disabled.live_enabled is False
    assert stale_after_disable.accepted is False
    assert "bridge.stale_or_forked_state" in stale_after_disable.errors
    assert "bridge.disabled" in stale_after_disable.errors
    assert stale_after_disable.state == disabled


def test_current_disabled_state_rejects_post_cutoff_submission() -> None:
    state0 = _start()
    disabled = disable_self_human_bridge(
        authorization=_authorization(),
        state=state0,
        attempt_elapsed_ms=10_000,
    )
    result = _accept(
        state=disabled,
        measurement=_measurement(elapsed_ms=20_000),
    )

    assert result.accepted is False
    assert "bridge.disabled" in result.errors
    assert result.state == disabled


def test_clarification_parent_must_be_actually_accepted() -> None:
    state0 = _start()
    first = _accept(state=state0)
    assert first.proposal is not None

    unknown = _draft(
        sequence_ordinal=2,
        clarification_of_proposal_id="proposal:" + "f" * 64,
    )
    rejected = _accept(
        state=first.state,
        request=_request(sequence_ordinal=2),
        draft=unknown,
        measurement=_measurement(elapsed_ms=40_000, is_clarification=True),
    )
    assert "bridge.clarification_source" in rejected.errors

    linked = _draft(
        sequence_ordinal=2,
        clarification_of_proposal_id=first.proposal.proposal_id,
    )
    accepted = _accept(
        state=first.state,
        request=_request(sequence_ordinal=2),
        draft=linked,
        measurement=_measurement(elapsed_ms=40_000, is_clarification=True),
    )
    assert accepted.accepted is True
    assert accepted.state.clarifications_used == 1


def test_forged_well_shaped_history_is_not_authoritative() -> None:
    state0 = _start()
    first = _accept(state=state0)
    forged = HumanPilotAttemptState(
        attempt_id=SELF_HUMAN_ATTEMPT_ID,
        generation=1,
        consultations_used=1,
        caregiver_active_ms_used=5_000,
        attempt_elapsed_ms=30_000,
        accepted_request_ids=("request:forged",),
        accepted_proposal_ids=("proposal:" + "a" * 64,),
    )

    result = _accept(
        state=forged,
        request=_request(sequence_ordinal=2),
        draft=_draft(
            sequence_ordinal=2,
            clarification_of_proposal_id="proposal:" + "a" * 64,
        ),
        measurement=_measurement(elapsed_ms=40_000, is_clarification=True),
    )

    assert result.accepted is False
    assert "bridge.stale_or_forked_state" in result.errors
    assert result.state == first.state


def test_rejected_submission_does_not_advance_authoritative_state() -> None:
    state0 = _start()
    rejected = _accept(state=state0, draft=_draft(contains_secret=True))

    assert rejected.accepted is False
    assert rejected.state == state0

    valid = _accept(state=state0)
    assert valid.accepted is True
    assert valid.state.generation == 1


def test_request_replay_is_rejected_on_current_state() -> None:
    state0 = _start()
    first = _accept(state=state0)
    replay = _accept(
        state=first.state,
        measurement=_measurement(elapsed_ms=40_000),
    )

    assert replay.accepted is False
    assert "bridge.request_replay" in replay.errors


def test_budget_and_elapsed_time_controls_fail_closed() -> None:
    state0 = _start()

    latency = _accept(
        state=state0,
        measurement=_measurement(
            elapsed_ms=PROPOSED_MAX_RESPONSE_LATENCY_MS + 2,
            latency_ms=PROPOSED_MAX_RESPONSE_LATENCY_MS + 1,
        ),
    )
    active = _accept(
        state=state0,
        measurement=_measurement(
            elapsed_ms=PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT + 2,
            active_ms=PROPOSED_MAX_CAREGIVER_ACTIVE_MS_PER_ATTEMPT + 1,
        ),
    )
    wall = _accept(
        state=state0,
        measurement=_measurement(elapsed_ms=PROPOSED_MAX_ATTEMPT_WALL_MS + 1),
    )

    assert "bridge.latency_budget" in latency.errors
    assert "bridge.active_time_budget" in active.errors
    assert "bridge.attempt_wall_budget" in wall.errors


def test_measured_time_must_fit_elapsed_delta() -> None:
    state0 = _start()
    latency = _accept(
        state=state0,
        measurement=_measurement(elapsed_ms=1_000, latency_ms=1_001, active_ms=500),
    )
    active = _accept(
        state=state0,
        measurement=_measurement(elapsed_ms=1_000, latency_ms=500, active_ms=1_001),
    )

    assert "bridge.latency_exceeds_elapsed" in latency.errors
    assert "bridge.active_ms_exceeds_elapsed" in active.errors


def test_privacy_visible_reference_and_caregiver_identity_violations_reject() -> None:
    state0 = _start()
    draft = _draft(
        caregiver_id="caregiver:pseudo:ffffffffffffffffffffffffffffffff",
        contains_personal_data=True,
        contains_secret=True,
        contains_third_party_confidential_data=True,
        observation_ids=("observation:hidden",),
    )
    result = _accept(state=state0, draft=draft)

    assert "bridge.caregiver_binding" in result.errors
    assert "bridge.draft.personal_data_forbidden" in result.errors
    assert "bridge.draft.secret_forbidden" in result.errors
    assert "bridge.draft.third_party_confidential_data_forbidden" in result.errors
    assert "bridge.draft.observation_ids.not_allowed" in result.errors


def test_wrong_attempt_and_relaxed_authorization_reject() -> None:
    state0 = _start()
    wrong_request = replace(_request(), attempt_id="attempt:other")
    wrong_auth = replace(
        _authorization(),
        self_only=False,
        project_owner_is_caregiver=False,
        ethics_review_status=EthicsReviewStatus.UNRESOLVED,
        third_party_participants=1,
    )

    request_result = _accept(state=state0, request=wrong_request)
    authorization_result = _accept(state=state0, authorization=wrong_auth)

    assert "bridge.attempt_binding" in request_result.errors
    assert "authorization.self_only" in authorization_result.errors
    assert "authorization.owner_is_caregiver" in authorization_result.errors
    assert "authorization.ethics_review_status" in authorization_result.errors
    assert "authorization.third_party_participants" in authorization_result.errors


def test_timestamp_and_integer_types_fail_closed() -> None:
    state0 = _start()
    naive = _accept(
        state=state0,
        measurement=_measurement(timestamp="2026-08-30T14:30:00"),
    )
    bool_latency = _accept(
        state=state0,
        measurement=HumanConsultationMeasurement(
            latency_ms=True,  # type: ignore[arg-type]
            caregiver_active_ms=1,
            attempt_elapsed_ms=10,
            source_timestamp="2026-08-30T14:30:00+09:00",
        ),
    )

    assert "bridge.source_timestamp" in naive.errors
    assert "bridge.latency_ms_type" in bool_latency.errors


def test_disablement_is_one_way_and_time_bounded() -> None:
    state0 = _start()
    state1 = _accept(state=state0).state

    with pytest.raises(ValueError):
        disable_self_human_bridge(
            authorization=_authorization(),
            state=state0,
            attempt_elapsed_ms=40_000,
        )
    with pytest.raises(ValueError):
        disable_self_human_bridge(
            authorization=_authorization(),
            state=state1,
            attempt_elapsed_ms=state1.attempt_elapsed_ms - 1,
        )

    disabled = disable_self_human_bridge(
        authorization=_authorization(),
        state=state1,
        attempt_elapsed_ms=40_000,
    )
    with pytest.raises(ValueError):
        disable_self_human_bridge(
            authorization=_authorization(),
            state=disabled,
            attempt_elapsed_ms=50_000,
        )


def test_public_surface_contains_no_direct_execution_authority() -> None:
    authorization = _authorization()
    state = _start()

    for obj in (authorization, state):
        assert not hasattr(obj, "action")
        assert not hasattr(obj, "writer")
        assert not hasattr(obj, "execute")
        assert not hasattr(obj, "command")
