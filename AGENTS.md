# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI.

Do not rely on conversation memory, prior model context, an issue title, or one code fragment. Reconstruct the project from repository and GitHub state before proposing or changing anything.

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

Repository and current GitHub state outrank conversation history.

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

Phase 1 passed its final independent read-only audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: Findings 1–6 were resolved, no new blocker/high/medium defect was found, and 152 tests passed. Issue #56 is closed as completed.

The Phase 1 body and trusted kernel are frozen. Proposed ADR 0008 and its protocol/matrix are not normative until reviewed, accepted, and merged.

If implementation reveals a contradiction, stop and resolve the contract or ADR through review before proceeding.

## AI collaboration safety and continuity

SUDACHI's organism, metabolism, body, lineage, growth, and caregiver vocabulary describes deterministic local software. Phase 1 uses Python, SQLite, immutable artifacts, and a synthetic garden only. It has no wet-lab biology, pathogens, genetic engineering, medical intervention, weapons work, offensive cybersecurity, third-party system access, network activity, or organism subprocess execution.

Do not evade product safeguards. State the concrete benign software context when sensitive vocabulary could be misread. Follow `docs/AI_COLLABORATION_OPERATIONS.md` for safety context, cost awareness, and conversation rollover.

Continue through multiple bounded slices only while repository, branch, pull-request, Issue, and CI state remain directly reconstructable. Do not create an automatic next slice merely to continue activity.

## Completed Phase 1

### Issue #13 — Phase 1 implementation

**Completed and closed.** Slices 1–35 implement the complete Minimal Organism Contract v0.2 seed baseline:

- canonical SQLite state and append-only events
- injected clocks and deterministic garden behavior
- fail-fast `BEGIN IMMEDIATE` wake ownership
- bounded actions, abstention, failure, maintenance, and budgets
- stable checkpoints, repair, retention, and deterministic export
- protected rollback lineage and one complete retained rollback evidence set
- ordering, seed independence, exact repeated-run equivalence, cleanup grace, replay rejection, process-crash rollback, nested-writer rejection, and pending-checkpoint exclusion
- no organism-writable external workspace
- narrow action-scoped SQL authority
- exact organism/administration provenance

PR #57 repaired the six Issue #56 cross-boundary defects and was squash-merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`. Reopen Issue #13 only for a demonstrated Phase 1 regression.

### Issue #56 — independent completion audit

**Completed and closed.** The final read-only audit reported:

- Findings 1–6: all `resolved`
- no new blocker/high/medium Phase 1 defect
- Python 3.12 protected suite: `152 passed`
- real 8 MiB enqueue boundary independently reproduced
- retention-reconciliation interruption and retry independently reproduced
- no tracked-file or index mutation during audit

Final conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

## Current Phase 2.0 design gate

### Issue #59 and draft PR #60

Issue #59 is the current design decision record. Draft PR #60 is documentation-only and proposes ADR 0008, protocol v1, the protected test matrix, and continuity updates.

The refined proposal fixes these boundaries:

1. **New initialization only.** Schema-v2 organisms are newly initialized; no Phase 1 migration or downgrade exists.
2. **Two budget controls.** `phase2-zero-caregiver-v1` produces no consultation state or event; `phase2-fixture-v1` has exact small limits.
3. **Garden request wake.** Request creation is an additional bounded effect after unchanged `no_applicable_action`; the Phase 1 failure increment remains exact and no request is created on maintenance entry.
4. **Dispatch admission.** Administration durably records and conservatively charges one dispatch before external work.
5. **Fixture execution.** The deterministic fixture runs outside every SQLite write transaction and receives only the request envelope and declared case ID.
6. **Ingress or terminalization.** A valid response is ingressed as immutable untrusted data. Invalid, expired, or interrupted dispatches are terminalized without retry.
7. **Authority separation.** External response/proposal packages contain no canonical writer authority or authoritative cost; administrative ingress receipts carry writer provenance.
8. **Non-circular identifiers.** Request, dispatch, proposal, response, package, and disposition identities have a fixed acyclic derivation order.
9. **Explicit disposition wake.** Garden and proposal work are separate caller-selected wake classes. Disposition claims no garden input and has no action effect.
10. **Maintenance honesty.** Disposition cannot bypass maintenance. Already-admitted evidence may be recorded administratively without clearing maintenance.
11. **Finite storage and work.** Logical limits supplement existing 8 MiB/40 MiB/64 MiB physical limits and preserve the 1 MiB next-wake reserve.
12. **Disposition-only first slice.** Accepted proposals do not enter the existing action selector.
13. **Frozen zero-caregiver projection.** Original Phase 1 rows, columns, payloads, and sequences remain exact except schema/budget configuration values and empty added objects.
14. **No hidden retry.** A process crash after dispatch admission requires explicit reconciliation and consumes the conservative charge.

Initial proposal types are `action_candidate`, `abstain`, and `defer`. Initial dispositions are `accepted`, `rejected`, `deferred`, and `clarification_requested`; all are final in protocol v1.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver identity is provenance only.

### Current authorization

There is no authorized Slice 36 and no authorized Phase 2 implementation.

Before implementation:

1. complete internal consistency review of PR #60
2. run one independent read-only Codex Phase 2.0 design audit against the exact PR head
3. post the report to Issue #59
4. address accepted design findings without audit ping-pong
5. change ADR 0008 from Proposed to Accepted only after satisfactory review
6. merge PR #60
7. open a separate test-first implementation issue

## Issue #3 — prior work and provider review

Research continues independently. No strong novelty claim and no live caregiver selection are authorized.

Deterministic fixture plumbing is not blocked by Issue #3. Live human/model integration, automated provider calls, retained provider output, or strong novelty claims remain blocked until research, privacy, consent, terms, retention, pricing, limits, and transformation questions are reviewed from current first-party sources.

Do not connect a human or model caregiver automatically. ChatGPT and an API are not the same product.

## Independent Codex audit cadence

Codex independent audits are high-cost phase-gate reviews, not routine per-slice or per-PR review. Follow `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`.

The Phase 1 closure audit is complete. The next planned audit is one Phase 2.0 design audit after PR #60 is internally coherent. A later single implementation audit occurs before freezing the implemented Phase 2 baseline.

Do not create audit-repair-reaudit ping-pong unless a gate conclusion directly blocks the next phase or evidence is insufficient.

## Frozen Phase 1 invariants

Phase 1 is deterministic, local, network-free, organism-subprocess-free, caregiver-free, bounded, auditable, SQLite-canonical, checkpointed after every committed wake, and explicit about organism versus administrative authority.

The Phase 1 runtime must not:

- dual-write canonical SQLite and JSONL
- write authoritative mutable files outside SQLite
- consult a caregiver
- execute arbitrary generated code
- run continuously
- add unrestricted retries or backtracking
- weaken protected tests or budgets
- modify protected actions, evaluators, schema, contract, or environment
- claim administrative authority

Administration remains distinct from organism autonomy. Canonical and report sources use protected `organism:` and `administration:` namespaces.

## Complete protected rollback path

Rollback archive preparation preserves the abandoned future. Source and transformed candidates prove exact restoration and isolated lineage transformation. Active replacement transfers canonical authority atomically. Completion records `rollback_completed`, restores wakeability, and preserves evidence.

ADR 0007 permits at most one completed rollback per organism and retains the complete archive/candidate evidence set without pruning.

## Exact restart point

1. verify Issues #13 and #56 are closed and PR #57 is merged
2. verify the final Phase 1 audit and unchanged 152-test baseline
3. inspect open Issues #3 and #59 and draft PR #60
4. read proposed ADR 0008, protocol v1, and the Phase 2 matrix
5. verify the five operational boundaries and non-circular identity rules
6. conduct one independent Phase 2.0 design audit after the documents are complete
7. do not create implementation code or Slice 36 until the design is accepted and merged

Do not begin a live caregiver/API, human chat UI, memory, skill generation, training, arbitrary Python/shell/SQL, continuous execution, personality/emotion feature, or generic agent framework.

## End-of-work protocol

Before ending substantial work:

- update `docs/HANDOFF.md` with the true state and one exact next gate
- update protected-test mapping and durable notes
- update relevant Issue and PR state
- report tests, CI, failures, and skipped checks honestly
- ensure no critical decision exists only in chat or model memory
- preserve the repository language policy

Repository prose, code, Issues, ADRs, and tests are written in English. The intentional Japanese lines in `README.md` remain the only standing exception.
