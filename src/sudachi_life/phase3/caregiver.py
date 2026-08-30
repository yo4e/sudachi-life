from __future__ import annotations

from dataclasses import dataclass, fields
from enum import StrEnum
import hashlib
import json
from typing import Protocol

CAREGIVER_PROTOCOL_VERSION = "sudachi.phase3.caregiver_proposal/v1"


class ProposalKind(StrEnum):
    DEMONSTRATION = "demonstration"
    CORRECTION = "correction"
    CONSTRAINT = "constraint"
    EXPLANATION = "explanation"
    PREFERENCE = "preference"
    QUESTION = "question"
    DEFER = "defer"
    ABSTAIN = "abstain"


class CaregiverSourceKind(StrEnum):
    FIXTURE = "fixture"
    HUMAN = "human"
    MODEL = "model"
    OTHER = "other"


class ProposalAuthority(StrEnum):
    PROPOSAL_ONLY = "proposal_only"


class AccountingStatus(StrEnum):
    MEASURED = "measured"
    NOT_APPLICABLE = "not_applicable"
    UNMEASURED = "unmeasured"


ACTIVE_SOURCE_KINDS = frozenset({CaregiverSourceKind.FIXTURE})
ALL_PROPOSAL_KINDS = tuple(ProposalKind)


@dataclass(frozen=True, slots=True)
class CaregiverRequest:
    request_id: str
    study_id: str
    attempt_id: str
    episode_id: str
    organism_id: str
    lineage_generation: int
    sequence_ordinal: int
    allowed_kinds: tuple[ProposalKind, ...] = ALL_PROPOSAL_KINDS


@dataclass(frozen=True, slots=True)
class CaregiverAccounting:
    consultation_count: int
    clarification_count: int
    latency_ms: int | None
    human_active_ms: int | None
    model_calls: int | None
    money_minor_units: int | None
    live_cost_status: AccountingStatus
    absence_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CaregiverProposal:
    protocol_version: str
    proposal_id: str
    request_id: str
    source_id: str
    source_kind: CaregiverSourceKind
    authority: ProposalAuthority
    study_id: str
    attempt_id: str
    episode_id: str
    organism_id: str
    lineage_generation: int
    sequence_ordinal: int
    source_timestamp: str | None
    kind: ProposalKind
    payload: str
    payload_sha256: str
    accounting: CaregiverAccounting


@dataclass(frozen=True, slots=True)
class ProposalValidation:
    valid: bool
    errors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FixtureResponse:
    request_id: str
    kind: ProposalKind
    text: str


class CaregiverSource(Protocol):
    source_id: str

    def propose(self, request: CaregiverRequest) -> CaregiverProposal: ...


def _payload_digest(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _proposal_id(
    *,
    request: CaregiverRequest,
    source_id: str,
    source_kind: CaregiverSourceKind,
    kind: ProposalKind,
    payload_sha256: str,
) -> str:
    canonical = json.dumps(
        {
            "request_id": request.request_id,
            "study_id": request.study_id,
            "attempt_id": request.attempt_id,
            "episode_id": request.episode_id,
            "organism_id": request.organism_id,
            "lineage_generation": request.lineage_generation,
            "sequence_ordinal": request.sequence_ordinal,
            "source_id": source_id,
            "source_kind": source_kind.value,
            "kind": kind.value,
            "payload_sha256": payload_sha256,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return f"proposal:{hashlib.sha256(canonical).hexdigest()}"


def proposal_from_text(
    *,
    request: CaregiverRequest,
    source_id: str,
    source_kind: CaregiverSourceKind,
    kind: ProposalKind,
    text: str,
    accounting: CaregiverAccounting,
    source_timestamp: str | None = None,
) -> CaregiverProposal:
    if type(source_kind) is not CaregiverSourceKind:
        raise TypeError("source_kind must be CaregiverSourceKind")
    if type(kind) is not ProposalKind:
        raise TypeError("kind must be ProposalKind")
    payload = text.strip()
    if not payload:
        raise ValueError("proposal text must be nonempty")
    digest = _payload_digest(payload)
    return CaregiverProposal(
        protocol_version=CAREGIVER_PROTOCOL_VERSION,
        proposal_id=_proposal_id(
            request=request,
            source_id=source_id,
            source_kind=source_kind,
            kind=kind,
            payload_sha256=digest,
        ),
        request_id=request.request_id,
        source_id=source_id,
        source_kind=source_kind,
        authority=ProposalAuthority.PROPOSAL_ONLY,
        study_id=request.study_id,
        attempt_id=request.attempt_id,
        episode_id=request.episode_id,
        organism_id=request.organism_id,
        lineage_generation=request.lineage_generation,
        sequence_ordinal=request.sequence_ordinal,
        source_timestamp=source_timestamp,
        kind=kind,
        payload=payload,
        payload_sha256=digest,
        accounting=accounting,
    )


def validate_proposal(request: CaregiverRequest, proposal: CaregiverProposal) -> ProposalValidation:
    errors: list[str] = []

    if proposal.protocol_version != CAREGIVER_PROTOCOL_VERSION:
        errors.append("proposal.protocol_version")
    if type(proposal.source_kind) is not CaregiverSourceKind:
        errors.append("proposal.source_kind")
    elif proposal.source_kind not in ACTIVE_SOURCE_KINDS:
        errors.append("proposal.live_source_not_authorized")

    allowed_kinds_valid = bool(request.allowed_kinds) and all(
        type(item) is ProposalKind for item in request.allowed_kinds
    )
    if not allowed_kinds_valid or len(set(request.allowed_kinds)) != len(request.allowed_kinds):
        errors.append("request.allowed_kinds")
    if type(proposal.kind) is not ProposalKind:
        errors.append("proposal.kind")
    elif allowed_kinds_valid and proposal.kind not in request.allowed_kinds:
        errors.append("proposal.kind_not_allowed")
    if type(proposal.authority) is not ProposalAuthority or proposal.authority is not ProposalAuthority.PROPOSAL_ONLY:
        errors.append("proposal.authority")

    request_bindings = (
        ("request_id", request.request_id),
        ("study_id", request.study_id),
        ("attempt_id", request.attempt_id),
        ("episode_id", request.episode_id),
        ("organism_id", request.organism_id),
        ("lineage_generation", request.lineage_generation),
        ("sequence_ordinal", request.sequence_ordinal),
    )
    for name, expected in request_bindings:
        if getattr(proposal, name) != expected:
            errors.append(f"proposal.binding.{name}")

    if request.sequence_ordinal < 0:
        errors.append("request.sequence_ordinal")
    if not request.request_id or not proposal.proposal_id or not proposal.source_id:
        errors.append("proposal.identity_empty")
    if not proposal.payload:
        errors.append("proposal.payload_empty")
    if proposal.payload_sha256 != _payload_digest(proposal.payload):
        errors.append("proposal.payload_digest")

    if type(proposal.source_kind) is CaregiverSourceKind and type(proposal.kind) is ProposalKind:
        expected_id = _proposal_id(
            request=request,
            source_id=proposal.source_id,
            source_kind=proposal.source_kind,
            kind=proposal.kind,
            payload_sha256=proposal.payload_sha256,
        )
        if proposal.proposal_id != expected_id:
            errors.append("proposal.identity_digest")

    accounting = proposal.accounting
    if accounting.consultation_count != 1:
        errors.append("proposal.accounting.consultation_count")
    if accounting.clarification_count < 0:
        errors.append("proposal.accounting.clarification_count")
    if accounting.latency_ms is not None and accounting.latency_ms < 0:
        errors.append("proposal.accounting.latency_ms")
    if type(accounting.live_cost_status) is not AccountingStatus:
        errors.append("proposal.accounting.status")

    if proposal.source_kind is CaregiverSourceKind.FIXTURE:
        if proposal.source_timestamp is not None:
            errors.append("proposal.fixture_timestamp")
        if accounting.live_cost_status is not AccountingStatus.NOT_APPLICABLE:
            errors.append("proposal.fixture_live_cost_status")
        if any(
            value is not None
            for value in (accounting.human_active_ms, accounting.model_calls, accounting.money_minor_units)
        ):
            errors.append("proposal.fixture_live_cost_value")
        if not accounting.absence_reason:
            errors.append("proposal.fixture_absence_reason")

    return ProposalValidation(valid=not errors, errors=tuple(errors))


@dataclass(frozen=True, slots=True)
class FixtureCaregiverAdapter:
    source_id: str
    responses: tuple[FixtureResponse, ...]

    def propose(self, request: CaregiverRequest) -> CaregiverProposal:
        matches = tuple(response for response in self.responses if response.request_id == request.request_id)
        if len(matches) != 1:
            raise LookupError("fixture request must resolve to exactly one response")
        response = matches[0]
        accounting = CaregiverAccounting(
            consultation_count=1,
            clarification_count=0,
            latency_ms=0,
            human_active_ms=None,
            model_calls=None,
            money_minor_units=None,
            live_cost_status=AccountingStatus.NOT_APPLICABLE,
            absence_reason="deterministic fixture source; no live caregiver cost",
        )
        proposal = proposal_from_text(
            request=request,
            source_id=self.source_id,
            source_kind=CaregiverSourceKind.FIXTURE,
            kind=response.kind,
            text=response.text,
            accounting=accounting,
        )
        result = validate_proposal(request, proposal)
        if not result.valid:
            raise ValueError(f"invalid fixture proposal: {result.errors}")
        return proposal


def proposal_data_fields() -> tuple[str, ...]:
    """Return the immutable data surface; useful for protected absence checks."""
    return tuple(item.name for item in fields(CaregiverProposal))
