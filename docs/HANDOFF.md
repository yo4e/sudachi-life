# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36a through Slice 36b2a5 are merged. Slice 36b2a6 independent absolute physical limits is implemented on PR #73; final documentation CI, review, and merge are the current gate.

No live caregiver integration is authorized.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, Minimal Organism Contract v0.2, accepted ADRs 0001–0009, the Phase 1 matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, this handoff, Consultation Protocol v1, the accepted Phase 2 matrix, implemented Phase 2 notes, and current Issues/PRs.

## Thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

Repository is auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

The final Phase 1 audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and found all six findings resolved, no new blocker/high/medium defect, and 152 tests passing. Those 152 tests remain unchanged and form the schema-v1 control.

Do not alter Phase 1 garden actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, authority categories, or protected tests for Phase 2 convenience.

PR #73 reopened shared Phase 1 code only for explicit, real-file absolute-limit defects. Pre-repair bodies remain in `*_impl.py` modules. After PR #73 merges, these narrow boundaries are re-frozen; do not treat the wrappers as general redesign permission.

## Accepted Phase 2 design

ADRs 0008 and 0009, Consultation Protocol v1, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` form one accepted design package.

Original Phase 1 budget locations stay exactly `phase1-v1`; Phase 2 policy lives in immutable `consultation_configuration`; checkpoint, repair, retention, rollback, export, and physical evidence use the exact closed rules in ADR 0009.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are provenance only.

## Implemented Slice 36 evidence

### Slice 36a — merged

PR #65 merged as `75077220ecb52256857f2b234283d36e3c0f51d2`.

It delivers schema-v2 genesis, exact protected zero/fixture configuration, unchanged Phase 1 tables and budget locations, immutable consultation objects, stable schema-v2 checkpoint validation, zero-caregiver absence, and the genesis active-database overhead bound.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

It delivers the active-database and genesis-checkpoint core of `phase1-projection-v2`, including exact side roles, fixed-order original Phase 1 rows, strict zero-caregiver absence, independent checkpoint integrity, raw checkpoint linkage before `CP(g,e)`, and exact nested/unlisted/wrong-location behavior.

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — merged

PR #67 merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

It validates exact pending-checkpoint repair identity, digest, size, previous-boundary, and checkpoint-store evidence before projection.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

### Slice 36b2a2 — merged

PR #69 merged as `64ea9eb094a687c056a571d362c1914aaf7911f2`.

It validates normal prune, restored pre-commit failure, committed cleanup failure, `STAGE(CP(g,e))`, pending reconciliation, interruption after deletion, retry, and completion. Deleted identity and bytes come only from prior immutable evidence.

Durable note: `docs/phase2/SLICE36B2A2_RETENTION_PROJECTION.md`.

### Slice 36b2a3 — merged

PR #70 merged as `054382a1ea57fa3e3c87d70d725b5a4a5415334b`.

Final head `4a0f82432e780245b3258983735c4f224a2f89fc` passed run 461 with `191 passed in 19.74s`. It validates exact `CP`, `RA`, `RC`, and `TC` artifact/event linkage, cross-lineage checkpoint references, abandoned-future preservation, and lineage-aware event-sequence reuse.

Durable note: `docs/phase2/SLICE36B2A3_ROLLBACK_PROJECTION.md`.

### Slice 36b2a4 — merged

PR #71 merged as `d7ce1703eaaf9aca1a33f72add4a9dfa707e7abe`.

Final head `31736c45ff1879002991a6249c86ffa86c0f07b8` passed run 468 with `196 passed in 19.01s`; installation, compilation, and schema-v1 genesis CLI smoke succeeded.

It independently validates raw canonical JSONL, exact manifest/event schemas, event range/count/order, active source-checkpoint linkage, reconstructed bytes, raw size, and raw SHA before semantic event projection.

Durable note: `docs/phase2/SLICE36B2A4_EVENT_EXPORT_PROJECTION.md`.

### Slice 36b2a5 — merged

PR #72 merged as `3cd46b5929d6bc5dea8b0cbede417b40e792ce72`.

Final run 475 passed with `200 passed in 20.09s`. Real paired schema-v1/schema-v2-zero scenarios enforce:

- active database overhead at most 256 KiB
- each `CP`, `RA`, `RC`, and `TC` database overhead at most 256 KiB
- aggregate additional non-database artifact bytes at most 1 MiB

Durable note: `docs/phase2/SLICE36B2A5_PHYSICAL_OVERHEAD.md`.

### Slice 36b2a6 — implemented on PR #73

Branch: `slice36b2-absolute-physical-limits`.

Base: merged PR #72 at `3cd46b5929d6bc5dea8b0cbede417b40e792ce72`.

Code head `409b82962cee00f59e573b6bf5c90d0d9d426cb6` passed run 502 with `222 passed in 32.16s`. Installation, compilation, and schema-v1 genesis CLI smoke succeeded. The unchanged 152 Phase 1 tests remain included. Codex was not used.

Protected real-file evidence closes P2-O18, P2-O19, P2-O21, and P2-O22:

- valid schema-v2-zero active database near 8 MiB
- exact 1 MiB next-wake reserve and subsequent real wake
- checkpoint database exact 8 MiB acceptance and one-page-over rejection
- checkpoint store exact 40 MiB acceptance and one-byte-over cleanup
- runtime working set exact 64 MiB acceptance and one-byte-over rejection for checkpoint registration, pending repair, retention, rollback archive, source candidate, and transformed candidate
- idempotent RA/RC/TC reentry obeys the same full working-set admission
- no retained new artifact, deleted existing artifact, or rejected canonical registration
- raw immutable zero-caregiver configuration and empty operational consultation state inside active, `CP`, `RA`, `RC`, and `TC` SQLite bodies

Test-first work found and closed:

- Issue #74: source/transformed candidate manifest bytes omitted from admission
- Issue #75: shared checkpoint validator omitted the independent 8 MiB artifact ceiling
- Issue #76: rollback archive remained published after post-publication rejection
- Issue #77: pending repair omitted the independent active-database ceiling
- Issue #78: idempotent rollback and retention no-op bypassed full working-set admission
- one same-turn checkpoint/repair post-write registration-growth defect

Each shared repair was explicitly owner-authorized and limited to physical admission, cleanup, or transaction rollback. No accepted limit, authority, idempotence, retention choice, or semantic rule changed.

Durable notes:

- `docs/phase2/SLICE36B2A6_ABSOLUTE_PHYSICAL_LIMITS.md`
- `docs/phase2/SLICE36B2A6_ACTIVE_REPAIR_ADDENDUM.md`

PR #73 final documentation head is the current gate. Run final CI, review the complete diff, mark ready, and merge only if green.

## Accepted boundaries and budgets

- schema-v2 new organisms only; no migration/downgrade
- request envelope ≤16 KiB
- complete external package ≤16 KiB
- provenance ≤8 KiB inside package limit
- four requests/four charged fixture calls per current lineage
- one outstanding current-lineage request
- 64 KiB exact logical payload per lineage
- zero human/model/money/declared fixture latency
- active database/artifact 8 MiB
- checkpoint store 40 MiB
- working set 64 MiB
- next-wake reserve 1 MiB

## Audit cadence

The next Codex use is the single Phase 2 implementation-completion audit, after every accepted matrix requirement has protected evidence and one exact CI-green candidate is ready to freeze. Do not use Codex per slice or for ordinary editing.

## Explicit exclusions

No live model/API/human caregiver, memory or skill generation, source/test generation, training, arbitrary code/SQL/shell/tools/paths/URLs/credentials, organism network/subprocess, continuous execution, personality/emotion state, caregiver-controlled authority, or generic agent framework.

## Exact restart

1. inspect Issue #61, PR #73, this handoff, and `docs/phase2/SLICE36B2A6_ABSOLUTE_PHYSICAL_LIMITS.md`
2. verify the final PR #73 documentation head and CI
3. review and merge PR #73; close Issues #74–#78 and re-freeze the narrow shared boundaries
4. confirm the unchanged 152 Phase 1 tests remain included and passing
5. create Slice 37 from updated `main`
6. implement the request-envelope and storage-safe request-extension boundary test-first
7. keep Codex deferred until the complete Phase 2 implementation candidate is ready for the single completion audit
