# SUDACHI Handoff

Updated: **2026-07-26**

This is the operational restart point after Phase 1 SUDACHI-0, Slices 1–35, the independent completion-audit repairs, and the successful final read-only audit. Phase 1 is frozen. The current authorized work is Phase 2.0 Consultation Boundary design review in Issue #59 and draft PR #60. There is no authorized Slice 36 or Phase 2 implementation.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, this handoff, Minimal Organism Contract v0.2, accepted ADRs 0001–0007, the Phase 1 test matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, and current Issues/PRs before changing anything.

When reviewing Phase 2.0, also read proposed ADR 0008, `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` from draft PR #60.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A language model is a possible future caregiver or organ, not the organism itself.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1 baseline

Use this precedence:

1. `docs/MINIMAL_ORGANISM_CONTRACT.md` v0.2
2. accepted ADRs 0001–0007
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage, explicit authority provenance, no organism-writable external workspace, and action-scoped SQL authority.

Phase 1 has no caregiver, model adapter, chat interface, network access, organism subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

Phase 1 and its trusted kernel are frozen. A Phase 2 extension must be reviewed, versioned, and protected. Proposed ADR 0008 is not accepted merely because it exists in a draft PR.

Repository and GitHub state outrank conversation memory. Do not introduce paid infrastructure, external services, or model/API calls without explicit owner approval.

## Completed Phase 1 work

### Issue #13 — Phase 1 SUDACHI-0 metabolism

**Completed and closed.** PR #57 repaired the six cross-boundary regressions found by Issue #56 and was squash-merged into `main` as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

Reopen Issue #13 only for a demonstrated Phase 1 regression. Do not use it for Phase 2 scope or implementation.

### Issue #56 — independent completion audit

**Completed and closed.**

The initial audit at `54b2be47107cd9fbad3301812d23ab90f7ea9c4e` confirmed the original 142-test baseline and found six cross-boundary defects. PR #57 repaired all six and expanded the protected suite to 152 tests.

The final independent read-only audit checked current `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and reported:

- Findings 1–6: all `resolved`
- new blocker/high/medium Phase 1 defects: none
- local Python 3.12: `152 passed`
- the real 8 MiB storage boundary independently reproduced
- the retention-reconciliation interruption and retry independently reproduced
- tracked files and index unchanged during audit

Final conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

This satisfies the Phase 1 audit gate. Future independent audits follow `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md` rather than per-slice review.

## Implemented Phase 1 summary

### Slices 1–23

- canonical SQLite body, append-only events, injected clocks, and fail-fast write ownership
- deterministic garden water, harvest, abstention, classified failure, and recovery paths
- concrete budgets, lifecycle deadline, savepoint rollback, maintenance, checkpoint retention and repair
- deterministic non-canonical JSONL export
- complete bounded rollback path and one-completed-rollback evidence retention

### Slices 24–32

- backward wall time cannot reorder canonical events
- declared seed does not change fixed seed-garden behavior
- identical declared inputs produce exact canonical and checkpoint equivalence
- cleanup grace permits only terminalization and overrun rolls back atomically
- lexicographic action selection ignores physical insertion order
- consumed input replay cannot duplicate action
- real process exit rolls back uncommitted work and releases ownership
- nested wake and hidden writers fail fast
- pending checkpoint blocks the next wake until explicit repair

### Slices 33–35

- no organism-writable external workspace
- narrow action-scoped SQLite authority
- exact `organism:` and `administration:` provenance namespaces
- all current CLI reports carry protected authority provenance

### Independent completion-audit repairs

The merged repair adds:

1. protected schema, trigger, singleton, budget, seed-layout, and action-registry validation
2. genesis, ordinary, and maintenance-bound published-orphan checkpoint repair
3. one retention policy shared by normal and repaired registration
4. enqueue storage enforcement with one bounded-wake reserve
5. explicit maintenance and crash-retryable post-commit retention reconciliation
6. common working-set accounting for SQLite sidecars, checkpoints and staging, rollback archives, and restore candidates

Ten adversarial tests protect these intersections. See `docs/phase1/PHASE1_INDEPENDENT_AUDIT_REPAIRS.md`.

## Current Phase 2.0 design stream

### Issue #59 — Consultation Boundary

Issue #59 is open as the design decision record.

### Draft PR #60 — proposed ADR 0008 and protocol

Draft PR #60 contains documentation only:

- `docs/decisions/0008-caregiver-consultation-boundary.md`
- `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
- `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
- continuity updates in `AGENTS.md` and this handoff

The current proposal fixes the following decisions:

1. Phase 2 begins with newly initialized schema-v2 organisms only; no Phase 1 migration.
2. One request wake commits and checkpoints before any fixture execution.
3. Deterministic fixture execution occurs outside every wake transaction and without a held SQLite write lock.
4. Response ingress is a separate administrative transaction that records immutable untrusted data only.
5. A later wake records one `accepted`, `rejected`, `deferred`, or `clarification_requested` disposition.
6. The first fixture slice stops at disposition. An accepted proposal cannot influence the existing action selector or execute an action.
7. Initial proposal types are `action_candidate`, `abstain`, and `defer`.
8. Canonical writer categories remain exactly `organism` and `administration`; caregiver identity is provenance, not authority.
9. Request, response, proposal, disposition, cost, provenance, payload, expiry, and lifetime limits are concrete.
10. The Phase 1 152-test suite remains unchanged, and a protected Phase 2 zero-caregiver projection is required.

The proposed first budget permits at most four requests and four fixture invocations over one organism lifetime, one outstanding request, one response and proposal per request, one proposal considered per wake, zero clarification rounds, 16 KiB request/response envelopes, 64 KiB total consultation payload, and zero human/model/money cost.

Request expiry is lifecycle-based: a request created in lifecycle `N` is eligible through lifecycle `N+2` and expired at `N+3`.

## Review required before implementation

Draft PR #60 must remain documentation-only until the following are complete:

1. review the exact schemas, enums, identifiers, authority sources, budgets, expiry, and zero-caregiver projection
2. inspect the proposed matrix for missing transaction, crash, checkpoint, rollback, storage, and provenance interactions
3. decide whether the disposition-only first slice is sufficiently informative
4. run one independent read-only Codex Phase 2.0 design audit under `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
5. post that audit to Issue #59
6. resolve accepted audit findings through the normal review process
7. change ADR 0008 from Proposed to Accepted only after satisfactory review
8. merge the design PR
9. create a separate test-first implementation issue and only then define Slice 36

No implementation issue currently exists.

## Issue #3 — prior work and provider review

Research continues independently. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized.

Deterministic fixture plumbing and source-neutral schemas are not blocked by Issue #3. Live human experiments, live model integration, automated provider calls, retained provider output, and strong novelty claims remain blocked until research, privacy, consent, terms, retention, pricing, limits, and transformation questions are reviewed from current sources.

## Validation state

Original completion evidence:

- PR #54 squash-merged as `1f46ea5817414dbaa11b5ac65039477bcaf10a42`
- run 317: **142 tests in 7.25 seconds**
- run 323: **142 tests in 7.95 seconds**

Audit repair evidence:

- run 335: **150 tests in 8.74 seconds**
- run 336: **150 tests in 10.16 seconds**
- first Codex re-audit: findings 1, 2, 3, and 6 resolved; findings 4 and 5 partial
- run 340: **152 tests in 10.32 seconds**
- final PR head `1fd1e252ea45885f0c966abcc52cdb59c4f4ff0a`, run 343: clean installation, source/test compilation, genesis CLI smoke, and **152 tests in 10.12 seconds**
- PR #57 squash-merged into `main` as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`
- final independent read-only audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: **152 passed**, all six findings resolved, no new blocker/high/medium defect

No existing protected test was deleted, weakened, skipped, or redefined.

Draft PR #60 changes documentation only. No Phase 2 code or tests have been run because no implementation exists.

## Explicitly excluded for now

Do not add:

- a live API or live model caregiver
- a live human chat UI
- long-term memory
- skill generation or promotion
- model training, fine-tuning, imitation, distillation, or synthetic-data training
- arbitrary Python, shell, SQL, tools, paths, URLs, or executable payloads
- continuous or always-on execution
- autonomous internet use
- personality, emotion, affection, mood, or virtual-pet presentation
- caregiver-controlled budgets, permissions, evaluation, checkpoints, migrations, or rollback
- a generic agent framework

## Exact next gate

The exact next action is to review draft PR #60 and complete one Phase 2.0 design audit. Do not write implementation code or create Slice 36 yet.

## Restart protocol

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff, Contract v0.2, ADRs 0001–0007, and the Phase 1 test matrix
4. verify Issues #13 and #56 are closed and PR #57 is merged
5. inspect open Issues #3 and #59 and draft PR #60
6. read proposed ADR 0008, protocol v1, and the Phase 2 matrix
7. stop at the Phase 2.0 design audit gate
8. do not create Slice 36 until the design is accepted, merged, and followed by a separate implementation issue

No critical decision may remain only in chat history.
