# Codex Independent Audit Policy

## Purpose

Codex independent audits are high-cost phase-gate reviews. They are not routine per-slice or per-pull-request code review.

Use ordinary repository review, protected tests, CI, and issue tracking for normal implementation work. Reserve Codex for a bounded independent pass when a phase, architecture boundary, or frozen baseline is ready to be judged as a whole.

## Default cadence

Plan approximately one independent Codex audit for each completed phase or completed design gate.

Do not request a Codex audit for every:

- implementation slice
- pull request
- ordinary bug fix
- documentation update
- intermediate repair commit

The normal sequence is:

1. complete the phase or design gate
2. assemble the normative documents, implementation, protected tests, and CI evidence
3. request one read-only independent audit with a fixed scope and output format
4. record findings in GitHub
5. repair accepted findings through the normal development process
6. protect repairs with tests and CI
7. wait until the next planned phase gate for the next independent audit

Avoid audit-repair-reaudit ping-pong. An immediate repeat audit is justified only when the previous conclusion directly blocks the next phase, the evidence was insufficient, or a repair changes the same authority, persistence, checkpoint, rollback, or other critical boundary that the gate is meant to certify.

## Required audit behavior

Each independent audit must:

- be read-only unless a separate implementation task is explicitly authorized
- identify the exact audited commit
- reconstruct the project from repository state rather than conversation memory
- read the applicable contract, accepted ADRs, protected-test matrix, implementation notes, handoff, and current Issues and pull requests
- run the existing protected suite and available non-mutating checks
- distinguish verified evidence from assumptions
- inspect important cross-boundary interactions, not only expected paths
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

Issue #56 is the one planned final Phase 1 closure audit after the Issue #56 repairs were merged in PR #57.

Audit current `main` and determine:

- whether original Findings 1 through 6 are resolved
- with particular attention to the final repairs for Findings 4 and 5
- whether Findings 1, 2, 3, and 6 remain closed without regression
- whether the repair work weakened tests or changed the Phase 1 contract
- whether the unchanged 152-test protected suite and added adversarial coverage protect the repaired boundaries
- whether any new blocker, high, or medium Phase 1 regression exists
- whether Phase 1 is a stable frozen foundation on which a separate Phase 2 consultation layer may later be designed

Do not review an unfinished Phase 2 design in this pass. Do not implement Phase 2. The Phase 2.0 Consultation Boundary receives its own single independent design audit only after Issue #59 is resolved and the proposed ADR, schemas, budgets, provenance rules, migration decision, and test matrix are complete.

For each original finding, report exactly one status:

- `resolved`
- `partially resolved`
- `unresolved`
- `regressed`

Finish the Phase 1 closure audit with exactly one conclusion:

- `Phase 1 is ready to freeze and Phase 2 design may begin.`
- `Phase 1 is ready after specified test additions.`
- `Phase 1 requires specified repairs before Phase 2.`
- `The available evidence is insufficient to conclude.`

Post the report to Issue #56. Do not modify tracked files during the audit.

## Later planned audits

After Phase 1 closure:

- perform one Phase 2.0 design audit only after the Consultation Boundary decision is complete, normally including ADR 0008, versioned schemas, authority and provenance rules, concrete budgets and expiry, initialization or migration policy, zero-caregiver comparison, and the protected test matrix
- perform one Phase 2 implementation audit before freezing the implemented Phase 2 baseline

Additional audits require a specific gate-level reason. Codex availability alone is not a reason to audit incomplete work repeatedly.
