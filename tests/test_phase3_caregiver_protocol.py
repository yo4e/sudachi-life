from __future__ import annotations

from dataclasses import replace

import pytest

from sudachi_life.phase3.caregiver import (
    ACTIVE_SOURCE_KINDS,
    AccountingStatus,
    CaregiverAccounting,
    CaregiverRequest,
    CaregiverSourceKind,
    FixtureCaregiverAdapter,
    FixtureResponse,
    ProposalAuthority,
    ProposalKind,
    proposal_data_fields,
    proposal_from_text,
    validate_proposal,
)


def _request(*, allowed_kinds: tuple[ProposalKind, ...] | None = None) -> CaregiverRequest:
    return CaregiverRequest(
        request_id="request:fixture-001",
        study_id="study:fixture",
        attempt_id="attempt:fixture-001",
        episode_id="episode:fixture-001",
        organism_id="sudachi-fixture-001",
        lineage_generation=0,
        sequence_ordinal=7,
        allowed_kinds=allowed_kinds or tuple(ProposalKind),
    )


def _adapter(
    *,
    kind: ProposalKind = ProposalKind.EXPLANATION,
    text: str = "Use the marked path before the cutoff.",
) -> FixtureCaregiverAdapter:
    return FixtureCaregiverAdapter(
        source_id="fixture:caregiver-v1",
        responses=(
            FixtureResponse(
                request_id="request:fixture-001",
                kind=kind,
                text=text,
            ),
        ),
    )


def _fixture_accounting() -> CaregiverAccounting:
    return CaregiverAccounting(
        consultation_count=1,
        clarification_count=0,
        latency_ms=0,
        human_active_ms=None,
        model_calls=None,
        money_minor_units=None,
        live_cost_status=AccountingStatus.NOT_APPLICABLE,
        absence_reason="deterministic fixture source; no live caregiver cost",
    )


def test_fixture_adapter_produces_deterministic_valid_proposal_data() -> None:
    request = _request()
    adapter = _adapter(text="  Use the marked path before the cutoff.  ")

    first = adapter.propose(request)
    second = adapter.propose(request)
    result = validate_proposal(request, first)

    assert first == second
    assert result.valid is True
    assert result.errors == ()
    assert first.payload == "Use the marked path before the cutoff."
    assert first.source_kind is CaregiverSourceKind.FIXTURE
    assert first.authority is ProposalAuthority.PROPOSAL_ONLY
    assert first.source_timestamp is None
    assert first.accounting.live_cost_status is AccountingStatus.NOT_APPLICABLE
    assert first.proposal_id.startswith("proposal:")
    assert len(first.payload_sha256) == 64


def test_protocol_exposes_exact_typed_proposal_classes() -> None:
    assert {item.value for item in ProposalKind} == {
        "demonstration",
        "correction",
        "constraint",
        "explanation",
        "preference",
        "question",
        "defer",
        "abstain",
    }


def test_raw_string_enum_masquerading_fails_closed() -> None:
    request = _request()
    proposal = _adapter().propose(request)

    raw_kind = validate_proposal(request, replace(proposal, kind="explanation"))  # type: ignore[arg-type]
    raw_source = validate_proposal(request, replace(proposal, source_kind="fixture"))  # type: ignore[arg-type]
    raw_authority = validate_proposal(request, replace(proposal, authority="proposal_only"))  # type: ignore[arg-type]
    raw_allowed = validate_proposal(
        replace(request, allowed_kinds=("explanation",)),  # type: ignore[arg-type]
        proposal,
    )

    assert "proposal.kind" in raw_kind.errors
    assert "proposal.source_kind" in raw_source.errors
    assert "proposal.authority" in raw_authority.errors
    assert "request.allowed_kinds" in raw_allowed.errors


def test_request_episode_and_order_bindings_fail_closed() -> None:
    request = _request()
    proposal = _adapter().propose(request)

    wrong_episode = validate_proposal(request, replace(proposal, episode_id="episode:other"))
    wrong_order = validate_proposal(request, replace(proposal, sequence_ordinal=8))

    assert "proposal.binding.episode_id" in wrong_episode.errors
    assert "proposal.binding.sequence_ordinal" in wrong_order.errors


def test_payload_and_proposal_identity_are_integrity_bound() -> None:
    request = _request()
    proposal = _adapter().propose(request)

    changed_payload = validate_proposal(request, replace(proposal, payload="different text"))
    changed_identity = validate_proposal(request, replace(proposal, proposal_id="proposal:tampered"))

    assert "proposal.payload_digest" in changed_payload.errors
    assert "proposal.identity_digest" in changed_identity.errors


def test_unpermitted_proposal_class_is_rejected() -> None:
    request = _request(allowed_kinds=(ProposalKind.CORRECTION,))
    proposal = proposal_from_text(
        request=request,
        source_id="fixture:caregiver-v1",
        source_kind=CaregiverSourceKind.FIXTURE,
        kind=ProposalKind.EXPLANATION,
        text="This class is not permitted for the request.",
        accounting=_fixture_accounting(),
    )

    result = validate_proposal(request, proposal)

    assert result.valid is False
    assert "proposal.kind_not_allowed" in result.errors


def test_live_source_records_are_not_authorized_in_this_slice() -> None:
    request = _request()
    proposal = proposal_from_text(
        request=request,
        source_id="human:placeholder",
        source_kind=CaregiverSourceKind.HUMAN,
        kind=ProposalKind.EXPLANATION,
        text="Representable data only; no human route exists.",
        accounting=CaregiverAccounting(
            consultation_count=1,
            clarification_count=0,
            latency_ms=None,
            human_active_ms=None,
            model_calls=None,
            money_minor_units=None,
            live_cost_status=AccountingStatus.UNMEASURED,
            absence_reason="no live source is connected",
        ),
    )

    result = validate_proposal(request, proposal)

    assert ACTIVE_SOURCE_KINDS == {CaregiverSourceKind.FIXTURE}
    assert result.valid is False
    assert "proposal.live_source_not_authorized" in result.errors


def test_fixture_live_cost_and_timestamp_fields_must_remain_explicitly_absent() -> None:
    request = _request()
    proposal = _adapter().propose(request)

    cost_value = replace(proposal.accounting, human_active_ms=1)
    measured_status = replace(proposal.accounting, live_cost_status=AccountingStatus.MEASURED)

    with_cost = validate_proposal(request, replace(proposal, accounting=cost_value))
    with_status = validate_proposal(request, replace(proposal, accounting=measured_status))
    with_timestamp = validate_proposal(request, replace(proposal, source_timestamp="2026-08-30T00:00:00Z"))

    assert "proposal.fixture_live_cost_value" in with_cost.errors
    assert "proposal.fixture_live_cost_status" in with_status.errors
    assert "proposal.fixture_timestamp" in with_timestamp.errors


def test_fixture_adapter_requires_exactly_one_closed_response() -> None:
    request = _request()
    missing = FixtureCaregiverAdapter(source_id="fixture:caregiver-v1", responses=())
    duplicate = FixtureCaregiverAdapter(
        source_id="fixture:caregiver-v1",
        responses=(
            FixtureResponse(request.request_id, ProposalKind.EXPLANATION, "one"),
            FixtureResponse(request.request_id, ProposalKind.CORRECTION, "two"),
        ),
    )

    with pytest.raises(LookupError):
        missing.propose(request)
    with pytest.raises(LookupError):
        duplicate.propose(request)


def test_text_transformation_rejects_empty_input() -> None:
    with pytest.raises(ValueError):
        proposal_from_text(
            request=_request(),
            source_id="fixture:caregiver-v1",
            source_kind=CaregiverSourceKind.FIXTURE,
            kind=ProposalKind.ABSTAIN,
            text="   ",
            accounting=_fixture_accounting(),
        )


def test_proposal_surface_is_data_only_and_has_no_action_or_execution_handle() -> None:
    fields = set(proposal_data_fields())

    assert {
        "action",
        "command",
        "callable",
        "code",
        "executable",
        "tool",
        "writer",
    }.isdisjoint(fields)
    assert "payload" in fields
    assert "authority" in fields
