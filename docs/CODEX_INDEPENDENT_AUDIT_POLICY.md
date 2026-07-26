# Codex Independent Audit Policy

## Purpose

Codex independent audits are high-cost phase-completion reviews. They are not routine per-slice, per-pull-request, or design-draft reviews.

Use ordinary repository review, protected tests, CI, and issue tracking while designing and implementing a phase. Reserve Codex for one bounded independent pass when the implemented phase is complete and is a candidate for freezing.

## Default cadence

Plan approximately one independent Codex audit for each completed implementation phase.

Do not request a Codex audit for every:

- design gate or ADR draft
- implementation slice
- pull request
- ordinary bug fix
- documentation update
- intermediate repair commit

The normal sequence is:

1. complete and accept the phase design through ordinary review
2. implement the phase through bounded test-first slices
3. assemble the accepted ADRs, implementation, protected tests, test matrix, and CI evidence
4. request one read-only independent audit of the complete implemented phase
5. record findings in GitHub
6. repair accepted findings through the normal development process
7. protect repairs with tests and CI
8. freeze the phase only after a satisfactory completion conclusion

Avoid audit-repair-reaudit ping-pong. An immediate repeat audit is justified only when the previous conclusion directly blocks phase completion, evidence was insufficient, or a repair changes the same authority, persistence, checkpoint, rollback, or other critical boundary being certified.

## Required audit behavior

Each independent audit must:

- be read-only unless a separate implementation task is explicitly authorized
- identify the exact audited commit
- reconstruct the project from repository state rather than conversation memory
- read the applicable contract, accepted ADRs, protected-test matrix, implementation notes, handoff, and current Issues and pull requests
- run the protected suite and available non-mutating checks
- distinguish verified evidence from assumptions
- inspect cross-boundary interactions, not only expected paths
- report important areas inspected where no issue was found
- use exact file and symbol references for findings
- avoid weakening tests, redefining the contract, or introducing the next phase to make a finding disappear

Every finding should include:

- severity
- affected invariant or requirement
- exact file and symbol
- evidence and reasoning
- minimal reproduction when possible
- whether an existing test should have caught it
- recommended disposition

## Phase 1 closure audit

Issue #56 was the one final Phase 1 completion audit. It is complete and closed.

The final audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`, reported all original Findings 1–6 resolved, found no new blocker/high/medium Phase 1 defect, and confirmed the protected 152-test baseline.

Final conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

## Phase 2 completion audit

Do not run a separate Codex audit for Phase 2.0 design acceptance.

Issue #59, ADR 0008, protocol schemas, authority and provenance rules, budgets and expiry, initialization policy, zero-caregiver comparison, and the protected test matrix are reviewed through the normal repository process.

Run one independent read-only Phase 2 audit only after:

- ADR 0008 is accepted and merged
- the authorized Phase 2 implementation slices are complete
- the complete Phase 1 suite remains unchanged and passing
- all accepted Phase 2 matrix requirements have protected evidence
- CI is green at one exact candidate head
- the implemented Phase 2 baseline is ready to be judged for freezing

That audit reviews the accepted design and its implementation together. It must decide whether the complete Phase 2 baseline is ready to freeze or requires specified repairs.

Additional Codex audits require a specific phase-completion reason. Codex availability alone is not a reason to audit incomplete work.