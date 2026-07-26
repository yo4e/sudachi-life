# Phase 2 Audit Cadence Amendment

Status: **Active for Issue #59 and draft PR #60**

This document records the project owner's final operational decision for Phase 2 Codex review cadence.

It supersedes only audit-cadence statements in the current proposed versions of:

- `docs/decisions/0008-caregiver-consultation-boundary.md`, section 15
- `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, section 18
- `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`, final acceptance and audit rule

It does not change their authority, transaction, identifier, budget, expiry, lineage, checkpoint, rollback, zero-caregiver, or test-design content.

## Decision

Phase 2 has exactly two planned independent read-only Codex audits:

1. **Phase 2.0 design audit**
   - occurs after Issue #59 and draft PR #60 are internally coherent
   - reviews one exact PR head using `docs/phase2/CODEX_PHASE2_DESIGN_AUDIT.md`
   - determines whether proposed ADR 0008 and the Consultation Boundary are ready to accept
   - does not implement code, change ADR status, merge the PR, or create Slice 36
2. **Phase 2 implementation audit**
   - occurs after accepted ADR 0008 is implemented
   - requires the unchanged Phase 1 suite, completed Phase 2 matrix evidence, and green CI at one exact candidate head
   - determines whether the implemented Phase 2 baseline is ready to freeze

There is no Codex audit for each slice, pull request, document edit, ordinary bug fix, or intermediate repair.

Avoid audit-repair-reaudit ping-pong. A repeated audit at the same gate requires a specific reason: insufficient evidence, a blocking conclusion, or a repair that changes the same critical authority, persistence, checkpoint, rollback, or storage boundary being certified.

## Precedence for the current design audit

For audit procedure only, use this order:

1. Issue #59 current body
2. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
3. this amendment
4. `docs/phase2/CODEX_PHASE2_DESIGN_AUDIT.md`
5. PR #60 current body

The proposed ADR, protocol, and test matrix remain the source of truth for the design being audited.
