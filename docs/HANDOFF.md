# SUDACHI Handoff

Updated: **2026-07-26**

This is the operational restart point after Phase 1 SUDACHI-0, Slices 1–35, completion-audit repairs, and successful final independent audit. Phase 1 is frozen.

Current authorized work is Phase 2.0 Consultation Boundary design review in Issue #59 and draft PR #60. There is no authorized Slice 36 or implementation.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, this handoff, Contract v0.2, accepted ADRs 0001–0007, Phase 1 matrix, audit policy, and current Issues/PRs. For Phase 2.0 also read proposed ADR 0008, protocol v1, and Phase 2 matrix from PR #60.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

Repository is auditable body, developmental history, skill base, and lineage record. A model may later be caregiver/organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

Precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0007
3. protected tests and Phase 1 matrix

Phase 1 provides canonical SQLite, append-only sequence events, injected clocks, fail-fast ownership, deterministic garden, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable retention, rollback lineage, exact authority, no external workspace, and narrow SQL action authority.

It has no caregiver, model adapter, chat UI, organism network/subprocess, arbitrary code, learning, memory, skill, continuous loop, or generic agent framework.

The body/trusted kernel are frozen. Proposed ADR 0008 is non-normative until accepted/merged.

## Completed Phase 1 work

### Issue #13

Completed/closed. PR #57 repaired six Issue #56 defects and merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

### Issue #56

Completed/closed. Final audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` reported:

- Findings 1–6 resolved
- no new blocker/high/medium defect
- Python 3.12: 152 passed
- real 8 MiB boundary reproduced
- retention reconciliation interruption/retry reproduced
- no tracked/index modification

Conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

Codex audits now follow phase-gate policy, not per-slice review.

## Current Phase 2.0 stream

### Issue #59

Open design decision record.

### Draft PR #60

Documentation only:

- proposed ADR 0008
- Consultation Protocol v1
- Phase 2 Consultation Test Matrix
- synchronized AGENTS/HANDOFF

No Phase 2 code/tests exist.

## Refined proposed design

### New initialization only

Schema-v2 organisms are newly initialized. No Phase1 migration, downgrade, or cross-version rollback decision.

Base contract remains 0.2. Budget config is:

- `phase2-zero-caregiver-v1`
- `phase2-fixture-v1`

### Five explicit boundaries

1. **Garden request wake**
   - only after unchanged no-applicable action with incomplete objective
   - same tick/outcome/action/mutation accounting
   - failure streak increments once
   - request never resets failure
   - no request on maintenance-entry wake
   - commits/checkpoints before dispatch

2. **Administrative dispatch admission**
   - fresh fail-fast transaction
   - stable current-lineage request required
   - immutable dispatch + event + conservative cost charge
   - commit/release lock before fixture
   - repeated admission never authorizes another call

3. **External deterministic fixture**
   - receives only request envelope + declared fixture case
   - no DB/path/workspace/executor/evaluator/checkpoint/rollback/network/subprocess/randomness capability
   - returns package to explicit caller/harness
   - package remains noncanonical before ingress

4. **Administrative ingress or terminalization**
   - external package has no writer authority or authoritative cost
   - receipt/event separately records administration source, digest, measured bytes
   - busy/pending rejection can be explicitly resubmitted with identical already-produced bytes; no fixture recall
   - invalid/expired/interrupted dispatch records one terminal outcome and no retry

5. **Explicit disposition wake**
   - caller selects this work class separately from garden wake
   - fail-fast wake ownership
   - no garden claim
   - oldest ingress sequence then proposal ID
   - one proposal max
   - lifecycle increments, garden failure streak preserved
   - no action/garden effect
   - ordinary checkpoint
   - requires sleeping and cannot bypass maintenance

### Proposal boundary

Types:

- action_candidate
- abstain
- defer

Final dispositions:

- accepted
- rejected
- deferred
- clarification_requested

First slice stops at disposition. Accepted proposal does not enter selector/execute action. Clarification budget is zero.

### Authority boundary

Only canonical writer categories:

- organism
- administration

Caregiver/adapter are provenance only. External package cannot declare writer authority/cost. Protected admin receipt/event does.

### Acyclic IDs

Order:

1. request
2. dispatch
3. proposal content/ID
4. response ID
5. final package digest
6. disposition

Proposal ID excludes response ID. Pre-insert IDs exclude later event sequences.

### Lineage budget epoch

Budget epoch is current `lineage_generation`.

- four requests/charged invocations per lineage
- one current-lineage outstanding request
- 64 KiB logical payload per lineage
- old-lineage rows are immutable historical evidence and inactive
- rollback starts a new four-call epoch
- ADR 0007 permits one completed rollback, so total physical-organism maximum is eight charged fixture invocations

A global cross-lineage four-call counter is rejected because enforcing it would alter frozen rollback transformation or introduce another authority.

### Finite limits

- request <=16 KiB
- response+proposal <=16 KiB
- provenance <=8 KiB
- zero human/model/money/declared latency
- exact record/step caps in ADR/protocol
- inherited 8 MiB active DB, 40 MiB checkpoint store, 64 MiB working set
- admin writes preserve 1 MiB next-wake reserve predicted and post-write

### Expiry/state

Request created lifecycle N eligible through N+2.

Current-lineage state derived from immutable rows:

- no dispatch + expired: terminal for admission, no longer outstanding
- admitted dispatch: outstanding until response/terminal even after expiry
- unavailable: terminal
- success response: outstanding until disposition
- terminal dispatch: terminal
- disposition: terminal
- old-lineage rows: historical/inactive

No caregiver-writable status flag.

### Maintenance/checkpoint/rollback

- request does not block later garden wakes; current state may diverge
- dispatch requires sleeping and stable request checkpoint
- ingress/terminal may record already-admitted evidence in sleeping/maintenance with no pending checkpoint
- disposition requires sleeping; cannot clear/bypass maintenance
- garden/disposition wakes checkpoint
- admin dispatch/ingress/terminal do not checkpoint
- rollback increments lineage and makes old consultation rows inactive
- abandoned-lineage package/proposal cannot ingress/dispose
- ADR0007 limit/evidence unchanged

### Strict zero-caregiver control

Zero config creates no consultation row/event/source/import/cost/effect.

Projection normalizes only existing schema/budget config values, compares every original Phase1 row/column/event payload/sequence exactly, and requires operational consultation tables/sequences empty.

## Required review before implementation

1. finish internal consistency review of PR #60
2. run one read-only Codex Phase2.0 design audit against exact head
3. post report to Issue #59
4. resolve accepted findings through normal design work
5. change ADR0008 Proposed -> Accepted only after satisfactory review
6. merge PR #60
7. create separate test-first implementation Issue
8. only then define Slice36

No repeated per-edit audits.

## Issue #3 research

Research continues independently. Deterministic fixture plumbing is not blocked.

Live human/model experiments, provider automation, retained provider output, or strong novelty claims remain blocked pending current first-party review of privacy, consent, terms, retention, pricing, limits, and transformation.

## Validation state

Phase 1 evidence includes PR54, runs 317/323, repair runs 335/336/340/343, PR57 merge, and final independent 152-pass audit.

PR #60 changes documentation only. No Phase2 executable test is claimed.

## Explicit exclusions

No:

- live API/model caregiver
- live human chat/unattended automation
- memory/skill generation
- caregiver source/test generation
- model training/fine-tuning/imitation/distillation/synthetic training
- arbitrary Python/shell/SQL/tools/paths/URLs/credentials/executable payload
- organism network/subprocess
- continuous loop/autonomous internet
- personality/emotion/pet presentation
- caregiver-controlled budgets/permissions/evaluation/checkpoints/migration/rollback
- generic agent framework

## Exact next gate

Complete internal review, then one Phase2.0 independent design audit. Do not write code or create Slice36.

## Restart

1. read AGENTS and collaboration operations
2. read this handoff, Contract, ADRs1-7, Phase1 matrix
3. verify Issues13/56 closed and PR57 merged
4. inspect Issues3/59 and draft PR60
5. read proposed ADR8/protocol/matrix
6. verify failure honesty, dispatch precharge, same-byte ingress retry, authority separation, acyclic IDs, explicit disposition, lineage epoch, reserve, checkpoint, rollback
7. stop at design audit gate
8. no Slice36 before accepted merged design and separate implementation Issue

No critical decision may remain only in chat.
