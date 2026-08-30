from __future__ import annotations

from dataclasses import replace

from sudachi_life.phase3.caregiver import CaregiverSourceKind
from sudachi_life.phase3.model import Availability, Point, TransitionKind
from sudachi_life.phase3.rehearsal import (
    build_integrated_caregiver_rehearsal,
    validate_integrated_caregiver_rehearsal,
)


def _valid_rehearsal():
    return build_integrated_caregiver_rehearsal(repository_commit="1" * 40)


def test_integrated_rehearsal_traces_fixture_proposal_through_w1_retention() -> None:
    rehearsal = _valid_rehearsal()
    result = validate_integrated_caregiver_rehearsal(rehearsal)

    assert result.valid is True
    assert result.errors == ()
    assert result.conformance.valid is True
    assert result.conformance.availability_subtype is Availability.W1
    assert result.conformance.acquired_capabilities == ("capability:fixture-transform",)
    assert result.conformance.retained_capabilities == ("capability:fixture-transform",)
    assert result.conformance.report["limitations"]["developmental_gain_claimed"] is False


def test_integrated_rehearsal_builder_is_deterministic() -> None:
    assert _valid_rehearsal() == _valid_rehearsal()


def test_foreign_request_episode_fails_closed() -> None:
    rehearsal = _valid_rehearsal()
    bad_request = replace(rehearsal.request, episode_id="episode:foreign")
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, request=bad_request))

    assert result.valid is False
    assert "rehearsal.request_binding.episode_id" in result.errors


def test_tampered_proposal_payload_fails_bridge() -> None:
    rehearsal = _valid_rehearsal()
    bad_proposal = replace(rehearsal.proposal, payload="tampered caregiver text")
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, proposal=bad_proposal))

    assert result.valid is False
    assert "proposal_bridge.proposal.payload_digest" in result.errors
    assert "rehearsal.payload_size" in result.errors


def test_live_source_proposal_is_not_accepted_by_rehearsal() -> None:
    rehearsal = _valid_rehearsal()
    bad_proposal = replace(rehearsal.proposal, source_kind=CaregiverSourceKind.HUMAN)
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, proposal=bad_proposal))

    assert result.valid is False
    assert "proposal_bridge.proposal.live_source_not_authorized" in result.errors
    assert "rehearsal.live_source_forbidden" in result.errors


def test_wrong_proposal_sequence_fails_caregiving_binding() -> None:
    rehearsal = _valid_rehearsal()
    bad_proposal = replace(
        rehearsal.proposal,
        sequence_ordinal=rehearsal.proposal.sequence_ordinal + 1,
    )
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, proposal=bad_proposal))

    assert result.valid is False
    assert "rehearsal.proposal_sequence" in result.errors


def test_wrong_assistance_class_fails_proposal_to_record_binding() -> None:
    rehearsal = _valid_rehearsal()
    caregiving = rehearsal.evidence.caregiving_records[0]
    bad_record = replace(caregiving, assistance_class="correction")
    bad_evidence = replace(rehearsal.evidence, caregiving_records=(bad_record,))
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, evidence=bad_evidence))

    assert result.valid is False
    assert "rehearsal.assistance_class" in result.errors


def test_broken_conversion_source_fails_downstream_trace() -> None:
    rehearsal = _valid_rehearsal()
    transitions = tuple(
        replace(record, input_id="caregiving:foreign")
        if record.kind is TransitionKind.CONVERSION
        else record
        for record in rehearsal.evidence.transitions
    )
    bad_evidence = replace(rehearsal.evidence, transitions=transitions)
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, evidence=bad_evidence))

    assert result.valid is False
    assert "rehearsal.conversion_source" in result.errors
    assert "rehearsal.episode_invalid" in result.errors


def test_broken_e1_caregiver_provenance_fails_trace() -> None:
    rehearsal = _valid_rehearsal()
    conversion = next(
        record
        for record in rehearsal.evidence.transitions
        if record.kind is TransitionKind.CONVERSION
    )
    points = []
    for point_record in rehearsal.evidence.points:
        if point_record.point is Point.E1:
            substrates = tuple(
                replace(substrate, source_caregiving_event_ids=())
                if substrate.substrate_id == conversion.output_id
                else substrate
                for substrate in point_record.substrates
            )
            point_record = replace(point_record, substrates=substrates)
        points.append(point_record)
    bad_evidence = replace(rehearsal.evidence, points=tuple(points))
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, evidence=bad_evidence))

    assert result.valid is False
    assert "rehearsal.e1_caregiver_provenance" in result.errors
    assert "rehearsal.episode_invalid" in result.errors


def test_broken_e2_conversion_provenance_fails_trace() -> None:
    rehearsal = _valid_rehearsal()
    conversion = next(
        record
        for record in rehearsal.evidence.transitions
        if record.kind is TransitionKind.CONVERSION
    )
    points = []
    for point_record in rehearsal.evidence.points:
        if point_record.point is Point.E2:
            substrates = tuple(
                replace(substrate, conversion_id="conversion:foreign")
                if substrate.substrate_id == conversion.output_id
                else substrate
                for substrate in point_record.substrates
            )
            point_record = replace(point_record, substrates=substrates)
        points.append(point_record)
    bad_evidence = replace(rehearsal.evidence, points=tuple(points))
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, evidence=bad_evidence))

    assert result.valid is False
    assert "rehearsal.e2_conversion_provenance" in result.errors
    assert "rehearsal.episode_invalid" in result.errors


def test_post_cutoff_caregiver_route_fails_withdrawal_rehearsal() -> None:
    rehearsal = _valid_rehearsal()
    bad_disablement = replace(rehearsal.evidence.disablement, post_cutoff_model_calls=1)
    bad_evidence = replace(rehearsal.evidence, disablement=bad_disablement)
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, evidence=bad_evidence))

    assert result.valid is False
    assert "rehearsal.withdrawal_not_closed" in result.errors
    assert "rehearsal.episode_invalid" in result.errors


def test_raw_string_proposal_kind_fails_closed_without_becoming_authority() -> None:
    rehearsal = _valid_rehearsal()
    bad_proposal = replace(rehearsal.proposal, kind="demonstration")
    result = validate_integrated_caregiver_rehearsal(replace(rehearsal, proposal=bad_proposal))

    assert result.valid is False
    assert "proposal_bridge.proposal.kind" in result.errors
    assert "rehearsal.proposal_kind_type" in result.errors
