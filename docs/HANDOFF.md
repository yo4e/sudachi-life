# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36a, Slice 36b1, Slice 36b2a1, Slice 36b2a2, and Slice 36b2a3 are merged. Slice 36b2a4 semantic event-export projection is implemented test-first on PR #71. The exact next implementation boundary after PR #71 merges is physical projection closure.

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

## Accepted Phase 2 design

ADRs 0008 and 0009, Consultation Protocol v1, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` form one accepted design package.

Original Phase 1 budget locations stay exactly `phase1-v1`; Phase 2 policy lives in immutable `consultation_configuration`; checkpoint, repair, retention, rollback, and export byte-derived differences use the exact closed semantic projection in ADR 0009.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are provenance only.

## Implemented Slice 36 evidence

### Slice 36a — merged

PR #65 merged as `75077220ecb52256857f2b234283d36e3c0f51d2`.

It delivers explicit schema-v2 genesis, exact protected zero/fixture configuration, unchanged original Phase 1 tables and budget locations, nine empty immutable consultation operational tables, stable schema-v2 checkpoint validation, no migration/downgrade path, zero-caregiver absence, and the accepted active-database overhead bound.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

It delivers the active-database and genesis-checkpoint core of `phase1-projection-v2`, including exact side roles, fixed-order original Phase 1 rows, strict zero-caregiver absence, independent checkpoint integrity, raw checkpoint linkage before `CP(g,e)` projection, checkpoint-database semantic comparison, and exact nested/unlisted/wrong-location behavior.

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — merged

PR #67 merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

It validates exact `checkpoint_registration_repaired` current/prior `CP` linkage plus database SHA, manifest SHA, database size, and checkpoint-store bytes before projection.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

### Slice 36b2a2 — merged

PR #69 merged as `64ea9eb094a687c056a571d362c1914aaf7911f2`.

It validates normal prune, restored pre-commit failure, committed cleanup failure, `STAGE(CP(g,e))`, pending reconciliation, interruption after deletion, retry, and completion. Deleted identity and bytes come only from prior immutable artifact evidence.

Durable note: `docs/phase2/SLICE36B2A2_RETENTION_PROJECTION.md`.

### Slice 36b2a3 — merged

PR #70 merged as `054382a1ea57fa3e3c87d70d725b5a4a5415334b`.

Tests-only head `38a8933f53d09ac5c4d39748a498cf90c5fa631e` produced red run 452 before implementation. Final head `4a0f82432e780245b3258983735c4f224a2f89fc` passed run 461 with `191 passed in 19.74s`; installation, compilation, and schema-v1 genesis CLI smoke succeeded.

The rollback graph validates and projects selected checkpoint `CP`, abandoned-future archive `RA`, source candidate `RC`, transformed candidate `TC`, exact rollback events, cross-lineage latest-stable checkpoint references, preserved abandoned-future checkpoints, and lineage-aware event-sequence reuse.

Durable note: `docs/phase2/SLICE36B2A3_ROLLBACK_PROJECTION.md`.

### Slice 36b2a4 — implemented on PR #71

Branch: `slice36b2-event-export-projection`.

Base: merged PR #70 at `054382a1ea57fa3e3c87d70d725b5a4a5415334b`.

Tests-only head `9430b314f925ed09c1e8b9a49b7b21961bcd1e70` produced the intended red run 463 before the event-export projection module existed.

Implementation and corruption-test candidate `379868664f1724f7c1cd5c2c82e0db09a7dfe960` passed run 465 with `196 passed in 22.75s`; dependency installation, compilation, and schema-v1 genesis CLI smoke succeeded. The unchanged 152 Phase 1 tests remain included. Codex was not used.

The paired scenario performs one real water wake and exports through stable checkpoint boundary `13`. Each raw file is independently validated as canonical JSONL and must equal the protected Phase 1 reconstruction byte-for-byte before projection.

The export projection validates:

- exact manifest and event key sets
- UTF-8 canonical JSON lines and terminating newline
- exact event range, count, order, organism identity, and source boundary
- active source checkpoint registry and immutable artifact linkage
- recomputed raw export size and SHA-256
- source checkpoint projection to `CP(0,13)`
- prior exported `checkpoint_stabilized` identity projection to `CP(0,2)`
- exact reuse of the accepted checkpoint/repair/retention/rollback event map

Path, raw bytes, raw SHA, raw size, and result-wrapper presentation are excluded from cross-run equality only after independent validation. A byte-identical copy at another presentation path compares semantically; a changed, noncanonical, incomplete, or post-capture-modified file rejects.

Durable note: `docs/phase2/SLICE36B2A4_EVENT_EXPORT_PROJECTION.md`.

## Exact next boundary: physical projection closure

After PR #71 is reviewed and merged, create a new test-first branch from updated `main`.

Close ADR 0009 section 9 and remaining Phase 2 matrix P2-O evidence:

- schema-v2-zero active database overhead over paired schema-v1 state is at most 256 KiB
- each schema-v2-zero checkpoint/archive/candidate database overhead is at most 256 KiB over its paired schema-v1 artifact
- aggregate additional manifest/directory metadata across the retained working set is at most 1 MiB
- schema-v2-zero independently obeys the absolute 8 MiB active database limit
- every checkpoint/archive/candidate independently obeys the absolute 8 MiB artifact limit
- checkpoint store independently obeys the absolute 40 MiB limit
- runtime working set independently obeys the absolute 64 MiB limit
- enqueue and future operations preserve the exact 1 MiB next-wake reserve
- real near-ceiling checkpoint, repair, retention, rollback, and reserve paths proceed or fail without partial canonical mutation

Do not replace absolute-limit tests with paired byte equality. Legitimate schema-v2 overhead is measured but never granted a larger absolute ceiling.

Slice 37 remains blocked until all Slice 36 evidence is merged and no blocker/high/medium boundary defect remains.

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

Request lifecycle `N` is eligible through `N+2`; proposal expiry is identical. Rollback starts a fresh lineage epoch, while ADR 0007 still permits at most one completed rollback.

## Audit cadence

The next Codex use is the single Phase 2 implementation-completion audit, after every accepted matrix requirement has protected evidence and one exact CI-green candidate is ready to freeze. Do not use Codex per slice or for ordinary editing.

## Explicit exclusions

No live model/API/human caregiver, memory or skill generation, source/test generation, training, arbitrary code/SQL/shell/tools/paths/URLs/credentials, organism network/subprocess, continuous execution, personality/emotion state, caregiver-controlled authority, or generic agent framework.

## Exact restart

1. inspect Issue #61, PR #71, this handoff, and all implemented Slice 36 notes
2. verify PR #71 final head and CI; review and merge it before dependent work
3. confirm the unchanged 152 Phase 1 tests remain included and passing
4. create a physical-closure branch from updated `main`
5. implement paired overhead and independent absolute-limit evidence test-first
6. keep Codex deferred until the complete Phase 2 implementation candidate is ready for the single completion audit
