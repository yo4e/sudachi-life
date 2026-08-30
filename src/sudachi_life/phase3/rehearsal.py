from __future__ import annotations

from dataclasses import dataclass

from .caregiver import (
    CaregiverProposal,
    CaregiverRequest,
    CaregiverSourceKind,
    FixtureCaregiverAdapter,
    FixtureResponse,
    ProposalKind,
    validate_proposal,
)
from .fixtures import build_valid_fixture_episode
from .model import Availability, ConformanceResult, EpisodeEvidence, Point, TransitionKind
from .validation import validate_episode

_REHEARSAL_REQUEST_ID = "request:fixture-caregiver-retention-001"
_REHEARSAL_SOURCE_ID = "fixture:caregiver:retention-rehearsal-v1"
_REHEARSAL_TEXT = "fixture demonstration: map marker-alpha to capability success"


@dataclass(frozen=True, slots=True)
class IntegratedCaregiverRehearsal:
    """Fixture-only bridge from a typed caregiver proposal to Phase 3 evidence."""

    request: CaregiverRequest
    proposal: CaregiverProposal
    evidence: EpisodeEvidence


@dataclass(frozen=True, slots=True)
class IntegratedRehearsalValidation:
    valid: bool
    errors: tuple[str, ...]
    conformance: ConformanceResult


def build_integrated_caregiver_rehearsal(
    *, repository_commit: str = "0" * 40
) -> IntegratedCaregiverRehearsal:
    """Build the canonical deterministic proposal-to-retention mechanics rehearsal.

    This binds the already-authorized fixture caregiver proposal surface to the
    already-authorized withheld-caregiver evidence fixture. It does not claim a
    scientific developmental gain and does not activate any live caregiver.
    """
    evidence = build_valid_fixture_episode(repository_commit=repository_commit)
    caregiving = evidence.caregiving_records[0]
    binding = evidence.binding

    request = CaregiverRequest(
        request_id=_REHEARSAL_REQUEST_ID,
        study_id=binding.study_id,
        attempt_id=binding.attempt_id,
        episode_id=binding.episode_id,
        organism_id=binding.organism_id,
        lineage_generation=binding.lineage_generation,
        sequence_ordinal=caregiving.ordinal,
        allowed_kinds=(ProposalKind.DEMONSTRATION,),
    )
    adapter = FixtureCaregiverAdapter(
        source_id=_REHEARSAL_SOURCE_ID,
        responses=(
            FixtureResponse(
                request_id=request.request_id,
                kind=ProposalKind.DEMONSTRATION,
                text=_REHEARSAL_TEXT,
            ),
        ),
    )
    proposal = adapter.propose(request)
    return IntegratedCaregiverRehearsal(
        request=request,
        proposal=proposal,
        evidence=evidence,
    )


def validate_integrated_caregiver_rehearsal(
    rehearsal: IntegratedCaregiverRehearsal,
) -> IntegratedRehearsalValidation:
    """Validate exact proposal provenance through withdrawal and retained W1 evidence."""
    errors: list[str] = []
    request = rehearsal.request
    proposal = rehearsal.proposal
    evidence = rehearsal.evidence
    binding = evidence.binding

    try:
        proposal_validation = validate_proposal(request, proposal)
    except (AttributeError, TypeError, ValueError):
        proposal_validation = None
        errors.append("proposal_bridge.validation_exception")
    if proposal_validation is not None:
        errors.extend(f"proposal_bridge.{error}" for error in proposal_validation.errors)

    request_bindings = (
        ("study_id", binding.study_id),
        ("attempt_id", binding.attempt_id),
        ("episode_id", binding.episode_id),
        ("organism_id", binding.organism_id),
        ("lineage_generation", binding.lineage_generation),
    )
    for name, expected in request_bindings:
        if getattr(request, name) != expected:
            errors.append(f"rehearsal.request_binding.{name}")

    if proposal.source_kind is not CaregiverSourceKind.FIXTURE:
        errors.append("rehearsal.live_source_forbidden")

    if len(evidence.caregiving_records) != 1:
        errors.append("rehearsal.caregiving_cardinality")
        caregiving = None
    else:
        caregiving = evidence.caregiving_records[0]

    if caregiving is not None:
        if request.sequence_ordinal != caregiving.ordinal:
            errors.append("rehearsal.request_sequence")
        if proposal.sequence_ordinal != caregiving.ordinal:
            errors.append("rehearsal.proposal_sequence")
        if type(proposal.kind) is not ProposalKind:
            errors.append("rehearsal.proposal_kind_type")
        elif proposal.kind.value != caregiving.assistance_class:
            errors.append("rehearsal.assistance_class")
        if proposal.payload_sha256 != caregiving.content_digest:
            errors.append("rehearsal.payload_digest")
        if not isinstance(proposal.payload, str):
            errors.append("rehearsal.payload_type")
        elif len(proposal.payload.encode("utf-8")) != caregiving.content_size_bytes:
            errors.append("rehearsal.payload_size")
        if caregiving.source != "deterministic_fixture":
            errors.append("rehearsal.caregiving_source")
        if not caregiving.terminal or caregiving.terminal_outcome != "accepted":
            errors.append("rehearsal.caregiving_terminal")

    conversions = tuple(
        record
        for record in evidence.transitions
        if record.kind is TransitionKind.CONVERSION
    )
    if len(conversions) != 1:
        errors.append("rehearsal.conversion_cardinality")
        conversion = None
    else:
        conversion = conversions[0]

    if caregiving is not None and conversion is not None:
        if conversion.input_id != caregiving.record_id:
            errors.append("rehearsal.conversion_source")

    candidate_id = conversion.output_id if conversion is not None else None
    capability_id: str | None = None
    points = {record.point: record for record in evidence.points}

    for point in (Point.E1, Point.E2):
        point_record = points.get(point)
        if point_record is None:
            errors.append(f"rehearsal.{point.value.lower()}_missing")
            continue
        if candidate_id is None:
            continue
        candidates = tuple(
            substrate
            for substrate in point_record.substrates
            if substrate.substrate_id == candidate_id
        )
        if len(candidates) != 1:
            errors.append(f"rehearsal.{point.value.lower()}_candidate_cardinality")
            continue
        candidate = candidates[0]
        if caregiving is not None and caregiving.record_id not in candidate.source_caregiving_event_ids:
            errors.append(f"rehearsal.{point.value.lower()}_caregiver_provenance")
        if conversion is not None and candidate.conversion_id != conversion.transition_id:
            errors.append(f"rehearsal.{point.value.lower()}_conversion_provenance")
        if candidate.origin != "caregiver_derived":
            errors.append(f"rehearsal.{point.value.lower()}_origin")
        if not candidate.w1_permitted:
            errors.append(f"rehearsal.{point.value.lower()}_w1_permission")
        if not candidate.capability_dependency:
            errors.append(f"rehearsal.{point.value.lower()}_capability_dependency")
        elif capability_id is None:
            capability_id = candidate.capability_dependency
        elif candidate.capability_dependency != capability_id:
            errors.append("rehearsal.capability_dependency_changed")

    e2 = points.get(Point.E2)
    if e2 is not None and e2.availability is not Availability.W1:
        errors.append("rehearsal.withdrawal_availability")

    disablement = evidence.disablement
    post_cutoff_counts = (
        disablement.live_adapter_handles,
        disablement.post_cutoff_dispatches,
        disablement.post_cutoff_human_bridges,
        disablement.post_cutoff_model_calls,
        disablement.post_cutoff_network_calls,
        disablement.post_cutoff_subprocess_calls,
        disablement.post_cutoff_human_interventions,
        disablement.post_cutoff_caregiver_cost_units,
        disablement.queued_or_cached_usable_outputs,
    )
    if any(value != 0 for value in post_cutoff_counts):
        errors.append("rehearsal.withdrawal_not_closed")

    conformance = validate_episode(evidence)
    if not conformance.valid:
        errors.append("rehearsal.episode_invalid")
    if conformance.availability_subtype is not Availability.W1:
        errors.append("rehearsal.conformance_not_w1")

    if capability_id is None:
        errors.append("rehearsal.capability_unresolved")
    else:
        if capability_id not in conformance.acquired_capabilities:
            errors.append("rehearsal.capability_not_acquired")
        if capability_id not in conformance.retained_capabilities:
            errors.append("rehearsal.capability_not_retained")

    limitations = conformance.report.get("limitations", {}) if conformance.report else {}
    if limitations.get("developmental_gain_claimed") is not False:
        errors.append("rehearsal.developmental_claim_forbidden")

    return IntegratedRehearsalValidation(
        valid=not errors,
        errors=tuple(errors),
        conformance=conformance,
    )
