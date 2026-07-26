# Codex Independent Audit Policy

## Purpose

Codex independent audits are high-cost phase-gate reviews. They are not routine per-slice or per-pull-request code review.

Use ordinary repository review, protected tests, CI, and issue tracking for normal design and implementation work. Reserve Codex for bounded independent passes when a completed design boundary or implemented phase is ready to be judged as a whole.

## Default cadence

Plan at most two independent Codex audits for Phase 2:

1. one read-only design audit after the complete Consultation Boundary design package is internally coherent
2. one read-only implementation audit after the complete Phase 2 implementation and protected evidence are ready to freeze

Do not request a Codex audit for every:

- implementation slice
- pull request
- ordinary bug fix
- documentation update
- intermediate repair commit
- design edit between the two planned gates

The normal Phase 2 sequence is:

1. complete the design package through ordinary review
2. assemble proposed ADR 0008, protocol v1, authority and provenance rules, budgets, expiry, initialization policy, zero-caregiver comparison, and the protected test matrix
3. request one read-only independent design audit against one exact PR head
4. record findings in Issue #59 and repair accepted findings through ordinary design work
5. accept and merge the design
6. implement Phase 2 through bounded test-first slices
7. assemble the accepted ADR, implementation, protected tests, completed matrix, and CI evidence
8. request one read-only independent implementation audit against one exact candidate head
9. repair accepted findings and freeze Phase 2 only after a satisfactory completion conclusion

Avoid audit-repair-reaudit ping-pong. An immediate repeat audit is justified only when the previous conclusion directly blocks the gate, the evidence was insufficient, or a repair changes the same authority, persistence, checkpoint, rollback, or other critical boundary being certified.

## Required audit behavior

Each independent audit must:

- be read-only unless a separate implementation task is explicitly authorized
- identify the exact audited commit
- reconstruct the project from repository state rather than conversation memory
- read the applicable contract, accepted or proposed ADRs as appropriate, protected-test matrix, implementation notes, handoff, and current Issues and pull requests
- run the existing protected suite and available non-mutating checks when code exists
- distinguish verified evidence from assumptions
- inspect important cross-boundary interactions, not only expected paths
- report important areas inspected where no issue was found
- use exact file and symbol references for findings
- avoid weakening tests, redefining the contract, or introducing the next phase to make a finding disappear

Every finding should include:

- severity
- affected invariant or requirement
- exact file and symbol or document section
- evidence and reasoning
- minimal reproduction when possible
- whether the protected test matrix would catch it
- recommended disposition

## Phase 1 closure audit

Issue #56 was the one final Phase 1 completion audit. It is complete and closed.

The final audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`, reported all original Findings 1–6 resolved, found no new blocker/high/medium Phase 1 defect, and confirmed the protected 152-test baseline.

Final conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

## Phase 2 design audit

Run one independent read-only design audit only after Issue #59 and draft PR #60 contain an internally coherent package including:

- proposed ADR 0008
- versioned request, dispatch, response, proposal, ingress, disposition, terminal, and cost semantics
- exact authority and provenance rules
- concrete budgets and lifecycle expiry
- initialization and no-migration decision
- rollback-lineage and consultation-budget-epoch behavior
- zero-caregiver comparison
- protected Phase 2 test matrix
- synchronized continuity documents

The design audit determines whether the Consultation Boundary is implementable, internally consistent, compatible with the frozen Phase 1 baseline, and ready to accept. It must not implement Phase 2, change ADR status, merge PR #60, or create Slice 36.

## Phase 2 implementation audit

Run one separate independent read-only implementation audit only after:

- ADR 0008 is accepted and merged
- authorized Phase 2 implementation slices are complete
- the complete Phase 1 suite remains unchanged and passing
- all accepted Phase 2 matrix requirements have protected evidence
- CI is green at one exact candidate head
- the implemented Phase 2 baseline is ready to be judged for freezing

That audit reviews the accepted design and its implementation together. It must decide whether the complete Phase 2 baseline is ready to freeze or requires specified repairs.

Additional Codex audits require a specific gate-level reason. Codex availability alone is not a reason to audit incomplete work repeatedly.
