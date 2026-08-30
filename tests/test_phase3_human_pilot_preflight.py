from __future__ import annotations

from dataclasses import replace

from sudachi_life.phase3.caregiver import (
    ACTIVE_SOURCE_KINDS,
    CaregiverRequest,
    CaregiverSourceKind,
    ProposalKind,
)
from sudachi_life.phase3.human_pilot import (
    EthicsReviewStatus,
    HumanCaregiverPilotPreflight,
    HumanProposalDraft,
    CaregiverConfidence,
    PROPOSED_MAX_PROPOSAL_BYTES,
    proposed_human_caregiver_pilot_v1,
    validate_human_pilot_preflight,
    validate_human_proposal_draft,
)


def _request(*, allowed_kinds: tuple[ProposalKind, ...] = (ProposalKind.EXPLANATION,)) -> CaregiverRequest:
    return CaregiverRequest(
        request_id="request:human-pilot-preflight-001",
        study_id="study:human-pilot-preflight",
        attempt_id="attempt:human-pilot-preflight-001",
        episode_id="episode:human-pilot-preflight-001",
        organism_id="sudachi-preflight-001",
        lineage_generation=0,
        sequence_ordinal=2,
        allowed_kinds=allowed_kinds,
    )


def _draft(**changes: object) -> HumanProposalDraft:
    values: dict[str, object] = {
        "draft_id": "draft:human-pilot-001",
        "request_id": "request:human-pilot-preflight-001",
        "caregiver_id": "caregiver:pseudonymous-001",
        "sequence_ordinal": 2,
        "kind": ProposalKind.EXPLANATION,
        "text": "The visible marker suggests using action:inspect before action:move.",
        "confidence": CaregiverConfidence.MEDIUM,
        "observation_ids": ("observation:marker-visible",),
        "objective_ids": ("objective:reach-marker",),
        "action_ids": ("action:inspect", "action:move"),
    }
    values.update(changes)
    return HumanProposalDraft(**values)  # type: ignore[arg-type]


def _validate(draft: HumanProposalDraft):
    return validate_human_proposal_draft(
        _request(),
        draft,
        allowed_observation_ids=frozenset({"observation:marker-visible"}),
        allowed_objective_ids=frozenset({"objective:reach-marker"}),
        allowed_action_ids=frozenset({"action:inspect", "action:move"}),
    )


def test_proposed_pilot_is_valid_review_packet_but_not_activation_ready() -> None:
    plan = proposed_human_caregiver_pilot_v1()
    result = validate_human_pilot_preflight(plan)

    assert result.design_valid is True
    assert result.review_packet_ready is True
    assert result.activation_ready is False
    assert result.errors == ()
    assert set(result.activation_blockers) == {
        "activation.project_owner_approval_required",
        "activation.ethics_context_must_be_resolved",
        "activation.consent_materials_not_ready",
        "activation.independent_live_candidate_audit_required",
        "activation.live_human_source_not_implemented",
        "activation.live_transport_not_implemented",
    }


def test_preflight_cannot_enable_human_source_or_transport() -> None:
    plan = proposed_human_caregiver_pilot_v1()

    enabled = validate_human_pilot_preflight(replace(plan, live_human_enabled=True))
    transported = validate_human_pilot_preflight(replace(plan, live_transport="local-form"))

    assert "pilot.live_human_must_remain_disabled" in enabled.errors
    assert "pilot.live_transport_forbidden" in transported.errors
    assert ACTIVE_SOURCE_KINDS == {CaregiverSourceKind.FIXTURE}
    assert CaregiverSourceKind.HUMAN not in ACTIVE_SOURCE_KINDS


def test_preflight_cannot_claim_scientific_developmental_result() -> None:
    plan = proposed_human_caregiver_pilot_v1()
    result = validate_human_pilot_preflight(replace(plan, scientific_claims_allowed=True))

    assert result.design_valid is False
    assert "pilot.scientific_claims_forbidden" in result.errors


def test_proposed_limits_are_fixed_inside_preflight_packet() -> None:
    plan = proposed_human_caregiver_pilot_v1()

    changed = replace(
        plan,
        budget=replace(plan.budget, max_consultations_per_attempt=4),
    )
    result = validate_human_pilot_preflight(changed)

    assert "pilot.budget.consultations" in result.errors


def test_privacy_defaults_fail_closed_if_relaxed() -> None:
    plan = proposed_human_caregiver_pilot_v1()
    relaxed = replace(
        plan.data_policy,
        raw_chat_transcript_retained=True,
        public_raw_payload_default=True,
        personal_data_prohibited=False,
        secrets_prohibited=False,
    )
    result = validate_human_pilot_preflight(replace(plan, data_policy=relaxed))

    assert "pilot.data.raw_chat_transcript" in result.errors
    assert "pilot.data.public_raw_payload" in result.errors
    assert "pilot.data.personal_data" in result.errors
    assert "pilot.data.secrets" in result.errors


def test_hidden_semantic_labor_must_remain_zero_and_logged() -> None:
    plan = proposed_human_caregiver_pilot_v1()
    hidden = replace(
        plan.hidden_labor_policy,
        off_channel_semantic_interventions_limit=1,
        administrative_actions_must_be_logged=False,
    )
    result = validate_human_pilot_preflight(replace(plan, hidden_labor_policy=hidden))

    assert "pilot.hidden_labor.off_channel" in result.errors
    assert "pilot.hidden_labor.administrative_logging" in result.errors


def test_owner_approval_and_ethics_resolution_alone_cannot_activate_preflight() -> None:
    plan = proposed_human_caregiver_pilot_v1()
    reviewed = replace(
        plan,
        project_owner_live_approval=True,
        ethics_review_status=EthicsReviewStatus.NOT_REQUIRED_DECLARED,
        consent_materials_ready=True,
        independent_live_candidate_audit_complete=True,
    )
    result = validate_human_pilot_preflight(reviewed)

    assert result.design_valid is True
    assert result.activation_ready is False
    assert "activation.live_human_source_not_implemented" in result.activation_blockers
    assert "activation.live_transport_not_implemented" in result.activation_blockers


def test_structured_human_draft_accepts_only_explicitly_allowed_visible_ids() -> None:
    result = _validate(_draft())

    assert result.valid is True
    assert result.errors == ()
    assert result.payload_sha256 is not None
    assert len(result.payload_sha256) == 64


def test_human_draft_rejects_unregistered_references_and_duplicate_ids() -> None:
    draft = _draft(
        observation_ids=("observation:heldout",),
        action_ids=("action:move", "action:move"),
    )
    result = _validate(draft)

    assert "draft.observation_ids.not_allowed" in result.errors
    assert "draft.action_ids.duplicate" in result.errors


def test_human_draft_rejects_personal_secret_and_confidential_data_flags() -> None:
    result = _validate(
        _draft(
            contains_personal_data=True,
            contains_secret=True,
            contains_third_party_confidential_data=True,
        )
    )

    assert "draft.personal_data_forbidden" in result.errors
    assert "draft.secret_forbidden" in result.errors
    assert "draft.third_party_confidential_data_forbidden" in result.errors


def test_human_draft_payload_is_bounded_by_utf8_bytes() -> None:
    exact = "a" * PROPOSED_MAX_PROPOSAL_BYTES
    too_large = "a" * (PROPOSED_MAX_PROPOSAL_BYTES + 1)

    assert _validate(_draft(text=exact)).valid is True
    result = _validate(_draft(text=too_large))
    assert "draft.payload_too_large" in result.errors


def test_human_draft_is_not_a_live_caregiver_proposal() -> None:
    draft = _draft()

    assert not hasattr(draft, "authority")
    assert not hasattr(draft, "source_kind")
    assert not hasattr(draft, "proposal_id")
    assert not hasattr(draft, "execute")
    assert not hasattr(draft, "command")
