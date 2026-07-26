# SUDACHI Handoff

Updated: **2026-07-26**

This is the operational restart point after Phase 1 SUDACHI-0, Slices 1–35, the completion-audit repairs, and the successful final read-only audit. Phase 1 is frozen.

The current authorized work is Phase 2.0 Consultation Boundary design review in Issue #59 and draft PR #60. There is no authorized Slice 36 or Phase 2 implementation.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, this handoff, Minimal Organism Contract v0.2, accepted ADRs 0001–0007, the Phase 1 matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, and current Issues/PRs before changing anything.

For Phase 2.0 also read proposed ADR 0008, `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` from draft PR #60.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A language model is a possible future caregiver or organ, not the organism itself.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1 baseline

Normative precedence:

1. `docs/MINIMAL_ORGANISM_CONTRACT.md` v0.2
2. accepted ADRs 0001–0007
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage, explicit authority provenance, no organism-writable external workspace, and action-scoped SQL authority.

Phase 1 has no caregiver, model adapter, chat interface, network access, organism subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

The Phase 1 body and trusted kernel are frozen. Proposed ADR 0008 is not accepted merely because it exists in a draft PR.

Repository and GitHub state outrank conversation memory. Do not introduce paid infrastructure, external services, or model/API calls without explicit owner approval.

## Completed Phase 1 work

### Issue #13 — implementation

**Completed and closed.** PR #57 repaired the six cross-boundary regressions found by Issue #56 and was squash-merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

Reopen Issue #13 only for a demonstrated Phase 1 regression.

### Issue #56 — independent completion audit

**Completed and closed.** The final read-only audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and reported:

- Findings 1–6: all `resolved`
- no new blocker/high/medium Phase 1 defect
- local Python 3.12: `152 passed`
- real 8 MiB boundary independently reproduced
- retention-reconciliation interruption and retry independently reproduced
- tracked files and index unchanged during audit

Final conclusion:

> Phase 1 is ready to freeze and Phase 2 design may begin.

Future independent audits follow `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md` rather than per-slice review.

## Implemented Phase 1 summary

- Slices 1–23: canonical metabolism, budgets, maintenance, checkpoints, export, and rollback
- Slices 24–32: ordering, seed independence, repeated-run equivalence, cleanup, tie breaking, replay, process crash, nested writers, and pending-checkpoint exclusion
- Slices 33–35: no external workspace, narrow SQL authority, and exact provenance
- audit repairs: exact schema validation, orphan repair, shared retention, enqueue reserve, crash-retryable retention reconciliation, and full working-set accounting

See `docs/PHASE1_TEST_MATRIX.md` and `docs/phase1/` for exact evidence.

## Current Phase 2.0 design stream

### Issue #59

Issue #59 is open as the design decision record.

### Draft PR #60

Draft PR #60 is documentation-only and contains:

- proposed `docs/decisions/0008-caregiver-consultation-boundary.md`
- `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
- `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
- synchronized `AGENTS.md` and this handoff

No Phase 2 code or tests exist.

## Refined Phase 2.0 decisions

### 1. New initialization only

The first experiment uses newly initialized schema-v2 organisms. There is no Phase 1 migration, downgrade, or cross-version rollback decision.

The base contract remains `0.2`. Schema-v2 uses protocol v1 and one of:

- `phase2-zero-caregiver-v1`
- `phase2-fixture-v1`

### 2. Garden request wake preserves Phase 1 truth

A request can be created only after the unchanged Phase 1 policy selects `no_applicable_action` for an incomplete objective.

The garden lifecycle remains the same classified abstention:

- same consumed tick and Phase 1 core outcome
- same action/mutation accounting
- `consecutive_failures` increments exactly once
- request creation does not reset failure
- no request is created on the wake that enters maintenance

### 3. Dispatch is admitted and charged before external work

After the request checkpoint is stable, administration records one immutable dispatch and conservatively charges one attempt/work unit in a short fail-fast transaction.

The charge is never refunded after process interruption. A repeated admission cannot authorize another fixture call.

### 4. Fixture execution holds no SQLite write lock

The deterministic fixture runs outside every write transaction. It receives only:

- the canonical request envelope
- a protected declared fixture case ID

It receives no database/path/workspace/executor/evaluator/checkpoint/rollback/network/subprocess capability.

### 5. Response ingress and writer authority are separate

External response/proposal packages contain no canonical writer category/source and no authoritative cost ledger.

A separate administrative ingress receipt and event record writer authority, measured bytes, and package digest. Caregiver identity and adapter information remain untrusted provenance.

### 6. Invalid or interrupted dispatches terminalize without retry

A dispatch that cannot produce a valid ingressed response records exactly one terminal outcome:

- `dispatch_interrupted`
- `fixture_output_invalid`
- `expired_before_ingress`

A process crash after dispatch admission requires an explicit bounded reconciliation operation. Reconciliation never invokes the fixture again.

### 7. Identifier construction is acyclic

Derivation order is fixed:

1. request
2. dispatch
3. proposal content and proposal ID
4. response ID
5. final response/proposal package digest
6. disposition

Proposal ID excludes response ID; response ID uses proposal IDs/content digests. Event sequence fields are excluded from IDs derived before insertion and remain explicit final linkage.

### 8. Disposition is an explicit separate wake class

Garden wake and consultation disposition wake are caller-selected operations. There is no hidden priority or unified automatic scheduler.

Disposition wake:

- uses the same fail-fast SQLite wake ownership
- claims no garden tick
- selects oldest ingress event then proposal ID
- considers at most one proposal
- increments lifecycle number
- preserves Phase 1 garden failure streak
- changes no garden/action/mutation state
- creates an ordinary checkpoint

It requires sleeping and cannot bypass maintenance.

### 9. First slice stops at disposition

Initial proposal types:

- `action_candidate`
- `abstain`
- `defer`

Initial final dispositions:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

An accepted proposal does not enter the existing action selector or execute an action. Clarification budget is zero, so clarification creates no follow-up request.

### 10. Budgets and storage are concrete

Fixture config permits at most:

- one request per eligible garden wake
- one outstanding request
- four lifetime requests
- one dispatch per request
- four conservatively charged fixture invocations
- one response and proposal per request
- one proposal considered per disposition wake
- zero clarification rounds
- 16 KiB request package
- 16 KiB response-plus-proposal package
- 8 KiB provenance subset
- 64 KiB lifetime logical payload
- zero human/model/money/declared-latency cost

Request wake, disposition wake, dispatch, ingress, and terminalization also have exact semantic/canonical-record caps in the ADR and protocol.

All Phase 2 writes remain under the inherited 8 MiB active DB, 40 MiB checkpoint store, and 64 MiB working-set ceilings. Administrative writes preserve the existing 1 MiB next-wake reserve before and after mutation.

### 11. Expiry and state are derived

A request created in lifecycle `N` is eligible through `N+2`.

- pre-dispatch expiry no longer counts outstanding
- admitted dispatch remains outstanding until response or terminal reconciliation
- unavailable response is terminal
- successful response remains outstanding until disposition
- disposition is final

No caregiver-writable mutable status flag is authoritative.

### 12. Zero-caregiver comparison is strict

Schema-v2 zero-caregiver config produces no consultation row, event, source, cost, fixture import, or effect.

The protected projection normalizes only existing schema and budget configuration values, then compares every original Phase 1 row, column, payload, and sequence exactly. Added operational consultation tables and sequences must be empty.

## Required review before implementation

1. internally inspect the exact ADR/protocol/matrix for contradictions
2. run one independent read-only Codex Phase 2.0 design audit against the exact PR #60 head
3. post the report to Issue #59
4. address accepted findings through normal design review
5. change ADR 0008 from Proposed to Accepted only after satisfactory review
6. merge PR #60
7. create a separate test-first implementation issue
8. only then define Slice 36

Do not perform repeated per-edit Codex audits.

## Issue #3 — research

Research continues independently. Deterministic fixture plumbing is not blocked by Issue #3.

Live human/model experiments, automated provider calls, retained provider output, or strong novelty claims remain blocked until research, privacy, consent, terms, retention, pricing, limits, and transformation questions are reviewed from current first-party sources.

## Validation state

Phase 1 evidence:

- PR #54 merge `1f46ea5817414dbaa11b5ac65039477bcaf10a42`
- run 317: 142 tests
- run 323: 142 tests
- audit repair runs 335/336/340/343
- final PR #57 head: 152 tests
- final independent audit at `62c9e0c...`: 152 passed, all findings resolved

Draft PR #60 changes documentation only. No Phase 2 code or executable test exists, so no Phase 2 test run is claimed.

## Explicit exclusions

Do not add:

- live API/model caregiver
- live human chat UI or unattended chat automation
- long-term memory
- skill generation/promotion
- source/test generation by caregiver
- model training, fine-tuning, imitation, distillation, or synthetic-data training
- arbitrary Python, shell, SQL, tools, paths, URLs, credentials, or executable payloads
- network or subprocess access inside organism execution
- continuous or always-on execution
- autonomous internet use
- personality, emotion, affection, mood, or virtual-pet presentation
- caregiver-controlled budgets, permissions, evaluation, checkpoints, migrations, or rollback
- generic agent framework

## Exact next gate

Complete internal review of draft PR #60, then run the one Phase 2.0 independent design audit. Do not write implementation code or create Slice 36.

## Restart protocol

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff, Contract v0.2, ADRs 0001–0007, and the Phase 1 matrix
4. verify Issues #13/#56 closed and PR #57 merged
5. inspect Issues #3/#59 and draft PR #60
6. read proposed ADR 0008, protocol v1, and Phase 2 matrix
7. verify dispatch pre-charge, authority separation, acyclic IDs, explicit disposition wake, maintenance behavior, reserve, and rollback lineage
8. stop at the design audit gate
9. do not create Slice 36 until accepted design is merged and a separate implementation issue exists

No critical decision may remain only in chat history.
