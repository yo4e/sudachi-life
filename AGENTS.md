# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI.

Do not rely on conversation memory, prior model context, an issue title, or one code fragment. Reconstruct the project from repository state before proposing or changing anything.

## Before doing any work

Read these files in order:

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/AI_COLLABORATION_OPERATIONS.md`
4. `docs/ORIGIN.md`
5. `docs/MINIMAL_ORGANISM_CONTRACT.md`
6. accepted files in `docs/decisions/`, in numeric order
7. `docs/ARCHITECTURE.md`
8. `docs/ROADMAP.md`
9. `docs/IMPLEMENTATION_DISCIPLINE.md`
10. `docs/PHASE1_TEST_MATRIX.md`
11. implemented notes in `docs/phase1/`, in slice order
12. `docs/RESEARCH_QUESTIONS.md`
13. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
14. preliminary notes in `docs/research/`
15. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
16. `docs/HANDOFF.md`
17. current open GitHub issues and pull requests
18. when reviewing Phase 2.0, proposed ADR 0008, `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`

Repository state and current GitHub state outrank conversation history.

## Core project question

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and retain capability while requiring less justified caregiver assistance.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A model may later be a caregiver or organ; it is not the whole organism.

> As it becomes smarter, it should become smaller and quieter.

Do not flatten SUDACHI into a generic autonomous agent, chatbot, virtual pet, or self-modifying loop.

## Normative authority

For the frozen Phase 1 baseline, use this precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0007
3. protected tests and `docs/PHASE1_TEST_MATRIX.md`
4. explicit current repository decisions

Phase 1 passed its final independent read-only audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: all six prior findings were resolved, no new blocker/high/medium defect was found, and 152 tests passed. Issue #56 is closed as completed.

The Phase 1 body and trusted kernel are frozen. A Phase 2 extension must be explicitly reviewed, versioned, and protected. Proposed ADR 0008 and its protocol/test matrix are not normative until accepted and merged.

If implementation reveals a contradiction, stop and resolve the contract or ADR through review before proceeding.

## AI collaboration safety and continuity

SUDACHI's organism, metabolism, body, lineage, growth, and caregiver vocabulary describes deterministic local software. Phase 1 uses Python, SQLite, immutable artifacts, and a synthetic garden only. It has no wet-lab biology, pathogens, genetic engineering, medical intervention, weapons work, offensive cybersecurity, third-party system access, network activity, or organism subprocess execution.

Do not evade product safeguards. State the concrete benign software context when sensitive vocabulary could be misread. Follow `docs/AI_COLLABORATION_OPERATIONS.md` for safety context, cost awareness, and conversation rollover.

Continue through multiple bounded slices only while repository, branch, pull-request, Issue, and CI state remain directly reconstructable. Do not create an automatic next slice merely to continue activity.

## Current repository state

### Issue #13 — Phase 1 implementation

**Completed and closed.** Repository state contains Slices 1–35 and the independent completion-audit repairs:

1. package, schema, initialization, status, genesis checkpoint
2. inbox, fail-fast wake acquisition, deterministic observation
3. first canonical water wake
4. canonical harvest wake
5. objective-complete abstention
6. classified no-applicable-action abstention
7. resource-aware harvest recovery
8. classified action failure with savepoint rollback
9. classified lifecycle budget exhaustion
10. maintenance-threshold entry
11. read-only maintenance inspection
12. explicit administrative maintenance clear
13. successful bounded checkpoint retention
14. classified checkpoint-retention failure
15. pending checkpoint registration repair
16. deterministic non-canonical JSONL event export
17. retained rollback-source validation and verified pre-rollback archive
18. durable rollback intent with atomic `rollback_started`
19. verified source-restored candidate construction
20. isolated candidate lineage transformation with `rollback_lineage_prepared`
21. atomic active-database replacement with immediate validation and recoverable interruption
22. atomic `rollback_completed`, restored wakeability, and first new-lineage stable checkpoint
23. single-completed-rollback admission enforcement at preparation
24. complete first-wake event ordering under backward wall time
25. complete first-wake behavior independence from different declared seeds
26. exact repeated-run canonical and artifact equivalence for identical declared inputs
27. protected cleanup-grace terminalization boundary and overrun rollback
28. complete lexicographic action tie breaking under reversed physical row insertion order
29. complete consumed-input replay rejection without duplicate action
30. real process-exit rollback of an uncommitted wake with released write ownership
31. nested wake and hidden writer fail-fast rejection with restored normal wakeability
32. explicit second-wake rejection behind a committed pending checkpoint and resumed progress after repair
33. guarded proof that registered organism actions have no external workspace or effect route
34. action-scoped SQLite authority restricted to exact registered garden transition columns
35. protected organism and administration provenance across canonical sources and public reports

All 41 fixed Contract v0.2 evaluations have complete protected coverage. The merged Phase 1 suite contains 152 tests.

PR #57 repaired the six Issue #56 cross-boundary defects and was squash-merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`. Reopen Issue #13 only for a demonstrated Phase 1 regression. Do not use it for Phase 2 features.

### Issue #56 — independent completion audit

**Completed and closed.**

The initial audit found six cross-boundary defects. PR #57 repaired them and added adversarial coverage. The final independent read-only audit checked current `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and reported:

- Findings 1–6: all `resolved`
- new blocker/high/medium Phase 1 defects: none
- local Python 3.12 protected suite: `152 passed`
- real 8 MiB storage boundary and retention-reconciliation interruption/retry independently reproduced
- no tracked-file or index modification during audit

Final conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

Do not reopen Issue #56 for ordinary Phase 2 review. Use the phase-gate audit policy for later completed design and implementation baselines.

### Issue #59 and draft PR #60 — Phase 2.0 Consultation Boundary

Issue #59 is the current design gate. Draft PR #60 proposes:

- ADR 0008: caregiver consultation remains outside organism authority
- `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
- `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
- newly initialized schema-v2 organisms only; no initial migration
- request wake, external fixture, administrative response ingress, and later disposition wake as distinct boundaries
- first fixture slice stopping at disposition, with no influence on the existing action selector
- initial proposal types `action_candidate`, `abstain`, and `defer`
- exact lifetime, per-wake, payload, provenance, cost, expiry, and physical-storage controls
- canonical writer categories remaining exactly `organism` and `administration`
- a protected Phase 2 zero-caregiver projection alongside the unchanged Phase 1 suite

PR #60 is documentation-only and intentionally draft. It does not authorize Slice 36 or Phase 2 implementation.

Before implementation:

1. review and resolve Issue #59's questions against the proposed documents
2. run one independent read-only Codex Phase 2.0 design audit
3. record the result in Issue #59
4. accept and merge ADR 0008 only after satisfactory review
5. open a separate test-first implementation issue

### Issue #3 — prior work and provider review

Research stream. Preliminary review is active, but no strong novelty claim and no live caregiver selection are authorized.

Do not connect a human or model caregiver automatically. Do not treat ChatGPT and an API as the same product. Provider permissions, retention, pricing, limits, and transformation classes must be reverified from current first-party sources before any live integration.

## Independent Codex audit cadence

Codex independent audits are high-cost phase-gate reviews, not routine per-slice or per-pull-request review. Follow `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`.

The Phase 1 closure audit is complete. The next planned audit is one read-only Phase 2.0 design audit after Issue #59, proposed ADR 0008, protocol schemas, authority/provenance rules, concrete budgets/expiry, initialization decision, zero-caregiver comparison, and test matrix are complete.

Do not create audit-repair-reaudit ping-pong. A later single implementation audit occurs before freezing the implemented Phase 2 baseline.

## Frozen Phase 1 invariants

Phase 1 is deterministic, local, network-free, organism-subprocess-free, caregiver-free, bounded, auditable, SQLite-canonical, checkpointed after every committed wake, and explicit about organism versus administrative authority.

The Phase 1 organism runtime must not:

- dual-write canonical SQLite and JSONL
- write authoritative mutable files outside SQLite
- consult a caregiver
- execute arbitrary generated code
- run continuously
- add unrestricted retries or backtracking
- weaken protected tests or budgets
- modify protected actions, evaluators, schema, contract, or environment
- claim administrative authority

Administration is distinct from organism autonomy. Canonical and report sources use protected `organism:` and `administration:` namespaces. Administrative operations and protected test harnesses retain narrow typed boundaries.

## Complete protected rollback path

Rollback archive preparation validates one retained source, snapshots the complete active future through SQLite Online Backup, and publishes immutable evidence without canonical mutation.

Rollback begin records durable intent. Candidate construction restores the selected checkpoint. Candidate transformation creates a distinct lineage and records `rollback_lineage_prepared`. Active replacement transfers authority atomically and remains blocked. Completion records `rollback_completed`, restores wakeability, and preserves the abandoned future.

ADR 0007 permits at most one completed rollback per organism and retains the complete archive and candidate evidence set without pruning.

## Fixed-evaluation and audit closures

- Slices 24–26 protect ordering, seed independence, and repeated-run equivalence.
- Slices 27–32 close cleanup, tie-breaking, replay, process-exit, nested-write, and pending-checkpoint boundaries.
- Slices 33–35 protect external-workspace absence, action SQL authority, and provenance.
- Issue #56 repairs protect schema integrity, published-orphan recovery, shared retention, enqueue headroom, crash-retryable retention reconciliation, and complete working-set accounting.
- The final audit independently closed all six findings and found no new blocker/high/medium Phase 1 defect.

Read the corresponding durable notes in `docs/phase1/` and `docs/PHASE1_TEST_MATRIX.md` for exact boundaries and CI evidence.

## Exact restart point — Phase 2.0 design gate

There is no authorized Slice 36 and no authorized Phase 2 implementation.

After reconstructing current repository and GitHub state:

1. verify Issues #13 and #56 are closed and PR #57 is merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`
2. verify the final audit conclusion and unchanged 152-test Phase 1 baseline
3. read Issue #3 and current research documents
4. review Issue #59 and draft PR #60
5. inspect proposed ADR 0008, protocol v1, and the Phase 2 test matrix rather than inventing scope in code
6. preserve the first-slice disposition-only boundary and zero-caregiver controls unless review explicitly changes them
7. conduct one independent Phase 2.0 design audit after the documents are complete
8. do not create an implementation issue until the design is accepted and merged

Do not begin a live human or model caregiver, API integration, long-term memory, skill generation, training, arbitrary Python, continuous execution, personality, emotion, or a generic agent framework.

## End-of-work protocol

Before ending substantial work:

- update `docs/HANDOFF.md` with the true state and one exact next gate
- update protected-test mapping and durable notes
- update relevant Issue and PR status
- report tests, CI, failures, and skipped checks honestly
- ensure no critical decision exists only in chat or model memory
- preserve the repository language policy

Repository prose, code, issues, ADRs, and tests are written in English. The intentional Japanese lines in `README.md` remain the only standing exception.
