"""Deterministic, fixture-only Phase 3 evaluation foundation.

This package is intentionally additive and does not write the Phase 1/2 organism body.
"""

from .fixtures import build_valid_fixture_episode
from .model import (
    ACCEPTED_PHASE3_REGISTRY_BYTES,
    ACCEPTED_PHASE3_REGISTRY_SHA256,
    CONTRACT_VERSION,
    IMPLEMENTATION_VERSION,
    Availability,
    AttemptState,
    CapabilityStatus,
    ConformanceResult,
    CostField,
    CostStatus,
    EpisodeEvidence,
    Point,
    accepted_phase3_requirement_ids,
)
from .validation import (
    ReplayConflict,
    advance_attempt_history,
    classify_availability,
    reconcile_immutable_replay,
    validate_episode,
)

__all__ = [
    "ACCEPTED_PHASE3_REGISTRY_BYTES",
    "ACCEPTED_PHASE3_REGISTRY_SHA256",
    "CONTRACT_VERSION",
    "IMPLEMENTATION_VERSION",
    "Availability",
    "AttemptState",
    "CapabilityStatus",
    "ConformanceResult",
    "CostField",
    "CostStatus",
    "EpisodeEvidence",
    "Point",
    "accepted_phase3_requirement_ids",
    "ReplayConflict",
    "advance_attempt_history",
    "build_valid_fixture_episode",
    "classify_availability",
    "reconcile_immutable_replay",
    "validate_episode",
]
