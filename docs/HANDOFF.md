# SUDACHI Handoff

Updated: **2026-07-25**

This is the operational restart point after Phase 1 SUDACHI-0, Slices 1–35, and the independent completion-audit repairs. The next authorized work is review of the Phase 2.0 Consultation Boundary in Issue #59. There is no authorized Slice 36 or Phase 2 implementation.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, this handoff, Minimal Organism Contract v0.2, ADRs 0001–0007, the protected test matrix, and current open Issues before changing implementation.

## Project thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A language model is a possible future caregiver or organ, not the organism itself.

> As it becomes smarter, it should become smaller and quieter.

## Normative Phase 1 baseline

Use this precedence:

1. `docs/MINIMAL_ORGANISM_CONTRACT.md` v0.2
2. ADRs 0001–0007 in `docs/decisions/`
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage, explicit authority provenance, no organism-writable external workspace, and action-scoped SQL authority.

Phase 1 has no caregiver, model adapter, chat interface, network access, organism subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

The Phase 1 body and trusted kernel are frozen by default. Phase 2 must be an explicitly reviewed and versioned extension, not a silent reinterpretation of Contract v0.2 or its tests.

Repository and GitHub state outrank conversation memory. Do not introduce paid infrastructure, external services, or model/API calls without explicit owner approval.

## Current work streams

### Issue #13 — Phase 1 SUDACHI-0 metabolism

**Completed and closed.** PR #57 repaired the six cross-boundary regressions found by Issue #56 and was squash-merged into `main` as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

Reopen Issue #13 only for a demonstrated Phase 1 regression. Do not use it for Phase 2 scope or implementation.

### Issue #56 — independent completion audit

The first read-only audit at baseline commit `54b2be47107cd9fbad3301812d23ab90f7ea9c4e` confirmed the original 142-test baseline and found six cross-boundary failures.

The first Codex re-audit classified findings 1, 2, 3, and 6 as resolved. Findings 4 and 5 remained partial:

- enqueue could leave the active database exactly at 8 MiB with no room for the next wake
- interruption after retention-staging deletion could lose the completion audit event

PR #57 added the requested residual repairs:

- a 1 MiB implementation reserve inside the accepted 8 MiB active-database ceiling, protected before and after enqueue writes
- a durable pending retention-reconciliation audit before deletion and an idempotent linked completion audit after deletion
- two adversarial regression tests for the residual boundaries

The final read-only Codex re-audit is deferred because the available Codex usage allocation is exhausted. This is not a satisfactory audit conclusion.

The exact state is:

> **repairs implemented, CI verified, final independent re-audit pending**

Issue #56 remains open as the durable queue for that later audit. When Codex availability returns, it must reproduce findings 4 and 5 against the merged code, confirm findings 1, 2, 3, and 6 remain closed, and review the Phase 2 Consultation Boundary for any bypass of Phase 1 authority, transaction, evaluation, budget, provenance, or checkpoint controls.

### Issue #59 — Phase 2.0 Consultation Boundary

**Open for review. No implementation is authorized by opening it.**

Issue #59 proposes the source-neutral boundary for deterministic fixture consultation. It requires:

- the Phase 1 body and trusted kernel to remain frozen by default
- consultation dispatch and caregiver latency outside the wake transaction
- caregiver responses as typed proposals, never commands
- later-wake dispositions: `accepted`, `rejected`, `deferred`, or `clarification_requested`
- independent evaluation before a proposal may affect an action or persistent capability
- no caregiver database handle or direct canonical mutation authority
- versioned request, response, and proposal schemas
- exact authority, provenance, concrete budgets, expiry, and cost ledger
- frozen Phase 1 and Phase 2 zero-caregiver comparison conditions
- explicit initialization and migration policy
- a deterministic fixture before any live human or model caregiver

The unresolved questions in Issue #59 must be reviewed before an ADR or implementation issue is accepted.

### Issue #3 — prior work and provider review

Research continues independently. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized.

Fixture-caregiver plumbing and source-neutral schemas are not blocked by Issue #3. Live human experiments, live model integration, automated provider calls, retained provider output, and strong novelty claims remain blocked until the relevant research, privacy, consent, terms, retention, pricing, limit, and transformation questions are reviewed from current sources.

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

## Accepted ADR 0007 retention boundary

Phase 1 permits at most one completed rollback per organism. The complete pre-rollback archive and candidate evidence set remains immutable and retained. There is no rollback-artifact deletion or pruning in Phase 1.

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

No existing protected test was deleted, weakened, skipped, or redefined.

The final independent re-audit remains pending in Issue #56 and must not be described as completed.

## Exact next gate — review Phase 2.0, do not implement it

There is no authorized Slice 36.

The exact next action is to review Issue #59 and resolve its decision questions. In particular:

1. decide whether the first fixture slice stops at proposal disposition or permits one accepted registered-action candidate to enter ordinary action selection
2. fix exact request, response, proposal, disposition, authority, provenance, budget, expiry, and cost schemas
3. decide whether Phase 2 begins only with newly initialized schema-v2 organisms
4. define the Phase 1-relevant canonical projection for the Phase 2 zero-caregiver baseline
5. map every new invariant to protected tests
6. decide whether to preserve the accepted result as ADR 0008 before opening an implementation issue
7. keep the final independent review queued in Issue #56

Do not begin implementation until the reviewed decision explicitly authorizes it.

## Explicitly excluded for now

Do not add:

- a live API or live model caregiver
- a live human chat UI
- long-term memory
- skill generation or promotion
- model training, fine-tuning, imitation, distillation, or synthetic-data training
- arbitrary Python, shell, SQL, tools, paths, or executable payloads
- continuous or always-on execution
- autonomous internet use
- personality, emotion, affection, mood, or virtual-pet presentation
- caregiver-controlled budgets, permissions, evaluation, checkpoints, migrations, or rollback
- a generic agent framework

## Restart protocol

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff, Contract v0.2, ADRs 0001–0007, and the test matrix
4. verify Issue #13 is closed and PR #57 is merged at `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`
5. inspect open Issues #3, #56, and #59
6. preserve the exact statement that the final independent re-audit is pending
7. stop at Issue #59's review gate; do not create Slice 36 from conversation memory

No critical decision may remain only in chat history.