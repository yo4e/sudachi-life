# SUDACHI Handoff

Updated: **2026-07-25**

This is the operational restart point for Phase 1 SUDACHI-0, accepted ADRs 0001–0007, and the independent completion-audit repair stream in draft PR #57. Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, this handoff, the Minimal Organism Contract, the ADRs, and current open Issues/PRs before changing implementation.

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

Phase 1 has one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, deterministic `seed-garden-v1`, concrete budgets, protected evaluation, exact checkpoint boundaries, immutable checkpoints, bounded retention, rollback lineage rules, explicit authority provenance, no organism-writable external workspace, and action-scoped SQL authority.

Phase 1 has no caregiver, model adapter, chat interface, network access, organism subprocess access, arbitrary generated code, learning, memory, skills, continuous execution, or generic autonomous loop.

Repository and GitHub state outrank conversation memory. Do not introduce paid infrastructure, external services, or model/API calls without explicit owner approval.

## Current work streams

### Issue #13 — Phase 1 regression repair only

Issue #13 was reopened only because the independent completion audit in Issue #56 demonstrated Phase 1 regressions. PR #57 is the bounded repair stream. Do not use the reopened issue to add Phase 2 behavior.

### Issue #56 — independent completion audit

The first read-only audit at baseline commit `54b2be47107cd9fbad3301812d23ab90f7ea9c4e` confirmed the original 142-test baseline and found six cross-boundary failures.

Codex re-audited PR #57 head `2ec29f896059ca5e476c20b6f1b05309f7d194ba`:

- findings 1, 2, 3, and 6 were resolved
- finding 4 remained partial because enqueue could leave the active database exactly at 8 MiB with no room for the next wake
- finding 5 remained partial because interruption after staging deletion could lose the completion audit event
- final conclusion remained: Phase 1 requires specified repairs before Phase 2

PR #57 now contains two additional bounded repairs:

- enqueue preserves a 1 MiB implementation reserve inside the accepted 8 MiB active-database ceiling for one complete bounded wake
- retention cleanup reconciliation uses a durable pending audit before deletion and an idempotent completion audit after deletion; retry after interruption requires no new clock read

Two new adversarial tests protect these boundaries. GitHub Actions run 340 passed **152 tests in 10.32 seconds**, source/test compilation, and genesis CLI smoke at head `b8ce12843d9692e50e770735d00f4b5379425eca`.

A second read-only Codex re-audit of the final documentation-synchronized PR head is required before merge.

### Issue #3 — prior work and provider review

Research continues independently. Preliminary evidence and provider-neutral strategy exist, but no strong novelty claim and no live caregiver selection are authorized.

Do not connect a human or model caregiver merely because Phase 1 is complete. Provider permissions, retention, pricing, limits, and transformation classes must be reverified from current first-party sources before any live integration.

## Implemented Phase 1 summary

### Slices 1–23

- canonical SQLite body, append-only events, injected clocks, and fail-fast write ownership
- deterministic garden water, harvest, abstention, classified failure, and recovery paths
- concrete budgets, lifecycle deadline, savepoint rollback, maintenance, checkpoint retention/repair
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

See the corresponding files in `docs/phase1/`.

## Independent completion-audit repairs — PR #57

PR #57 repairs the six Issue #56 findings without changing Contract v0.2 or adding Phase 2 capability:

1. protected schema, append-only triggers, singleton cardinality, budget configuration, seed layout, and action registry are validated before active/checkpoint acceptance
2. published pending-checkpoint repair supports genesis, ordinary lifecycle, and maintenance-bound boundaries
3. normal and repaired registration share one retention policy
4. enqueue checks storage before and after writes and preserves one bounded-wake reserve
5. post-commit cleanup failure records maintenance; reconciliation is auditable and crash-retryable
6. common working-set accounting includes SQLite sidecars, checkpoints/staging, rollback archives, and restore candidates

Ten adversarial tests now protect these intersections. See `docs/phase1/PHASE1_INDEPENDENT_AUDIT_REPAIRS.md`.

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
- first Codex re-audit: findings 1/2/3/6 resolved; findings 4/5 partial
- run 340: **152 tests in 10.32 seconds**, compilation and genesis smoke passed

No existing protected test was deleted, weakened, skipped, or redefined.

## Exact next gate — second re-audit before Phase 2

There is no authorized Slice 36 and no authorized Phase 2 implementation.

1. synchronize PR #57 documentation and obtain a green final-head CI run
2. ask Codex to re-audit only the two residual Issue #56 findings against that exact head
3. require exact reproduction attempts, finding-by-finding evidence, and a final conclusion in Issue #56
4. repair any newly verified Phase 1 defect without changing the contract or adding Phase 2 behavior
5. merge PR #57 only after a satisfactory re-audit
6. verify merged `main` CI, close Issue #13, and re-freeze the protected Phase 1 baseline
7. only then review Issue #3 and make an explicit reviewed Phase 2 scope decision
8. keep the Phase 1 caregiver budget at zero and preserve the no-caregiver baseline

Do not begin human/model caregiver integration, live APIs, learning, memory, skill adoption, or a generic agent framework without the reviewed Phase 2 scope decision.

## Restart protocol

1. read `AGENTS.md`
2. read `docs/AI_COLLABORATION_OPERATIONS.md`
3. read this handoff and normative documents
4. inspect Issues #13 and #56 and PR #57
5. verify the latest PR head and CI rather than relying on chat history
6. stop at the second independent re-audit gate
7. after merge, verify final `main` and CI before closing Issue #13
8. stop at the Phase 2 decision gate unless a newer reviewed repository decision authorizes implementation

No critical decision may remain only in chat history.
