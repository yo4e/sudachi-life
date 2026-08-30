# Review and Audit Policy

Status: **Active operational policy**

This file keeps its historical filename for continuity. The policy is tool-neutral.

## Purpose

SUDACHI should use the lightest review process that still protects the research boundary.

Normal design and implementation work uses ordinary repository review, relevant protected tests, CI, and Issue/PR tracking. Independent audits are high-cost phase-gate tools, not routine development steps.

The default development path is:

1. confirm scope when the change is material;
2. implement a bounded change;
3. add or update relevant tests;
4. run ordinary CI;
5. merge when the change is reviewable and green.

Do **not** require an independent audit for every slice, pull request, bug fix, documentation change, or repair commit.

## Review levels

### 1. Ordinary review

Use for normal development. Review the diff, governing requirements, relevant tests, and CI. Escalate only when the change reaches a protected boundary.

### 2. Audit mode

Audit mode is an optional concentrated read-only review. It may happen in the same working conversation.

When using audit mode:

- fix one exact candidate commit;
- do not modify that candidate during the review;
- treat repository state, governing documents, tests, and CI as evidence;
- do not use implementation-conversation claims as proof;
- record material findings before returning to implementation.

Audit mode is useful for adversarial checking, but it is **not** an independent audit merely because the reviewer changes mental roles.

### 3. Independent phase-gate audit

Reserve an independent read-only audit for a completed boundary that is actually being frozen or for another explicitly high-risk gate.

An independent audit is normally justified when:

- a phase or major accepted design package is ready to freeze;
- a change reopens frozen Phase 1 or Phase 2 behavior;
- canonical authority, writer categories, security boundaries, checkpoint/rollback semantics, destructive migration, or protected evidence are materially changed;
- a live external capability is introduced, including human/model caregiver access, network, subprocess, credentials, or external mutable writes;
- material autonomy, cost, or resource ceilings expand;
- the project owner explicitly requests an independent gate review.

A reviewer may be Codex, ChatGPT in a fresh context, another model/tool, or a human. For an independent audit, the reviewer must not materially implement the exact candidate being certified.

## Audit scope

Use a bounded, risk-scoped packet. Start with:

- exact base/head and diff;
- scope authorization;
- directly governing contracts, ADR sections, and matrix requirements;
- protected boundaries plausibly affected by the diff;
- relevant tests, CI, and adversarial cases;
- current Issue/PR state needed to identify the gate.

Do not require a full repository-history reread. Read older material only when a concrete ambiguity, conflict, provenance question, or cross-boundary risk requires it.

## Findings and repairs

For material findings, record severity, affected invariant, exact location, evidence/reasoning, reproduction when useful, test coverage, and the minimal correction.

Repairs return to ordinary development: implement, test, and run CI.

Avoid audit-repair-reaudit ping-pong. A full new independent audit is **not** automatically required after every repair. Before a phase is frozen, perform only the closure review needed to verify that accepted findings are resolved. Escalate to another independent pass when the repair itself materially changes the critical boundary being certified, the prior evidence was insufficient, or the project owner requests it.

## Historical audits

Historical Phase 1 and Phase 2 audit records remain valid evidence of the frozen baselines. Their use of Codex or fresh reviewer sessions does not create a requirement to repeat the same process for ordinary later pull requests.

The Phase 3 accepted design package still requires an independent implementation audit **before Phase 3 freeze**. This is a phase gate, not a per-foundation-PR merge gate.
