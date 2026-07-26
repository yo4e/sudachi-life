# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36a, Slice 36b1, Slice 36b2a1, and Slice 36b2a2 are merged. Slice 36b2a3 rollback projection is implemented test-first on PR #70. The exact next implementation boundary after PR #70 merges is semantic event-export projection.

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

Issues #13 and #56 are closed. PR #57 merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

The final Phase 1 audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and found all six findings resolved, no new blocker/high/medium defect, and 152 tests passing. Those 152 tests remain unchanged and form the schema-v1 control.

Do not alter Phase 1 garden actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, authority categories, or protected tests for Phase 2 convenience.

## Accepted Phase 2 design

ADRs 0008 and 0009, Consultation Protocol v1, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` form one accepted design package.

Original Phase 1 budget locations stay exactly `phase1-v1`; Phase 2 policy lives in immutable `consultation_configuration`; checkpoint, repair, retention, rollback, and export byte-derived differences use the exact closed semantic projection in ADR 0009.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are provenance only.

## Implemented Slice 36 foundation

### Slice 36a — merged

PR #65 merged as `75077220ecb52256857f2b234283d36e3c0f51d2`.

It delivers explicit schema-v2 genesis, exact protected zero/fixture configuration, unchanged original Phase 1 tables and budget locations, nine empty immutable consultation operational tables, stable schema-v2 checkpoint validation, no migration/downgrade path, zero-caregiver absence, and the accepted active-database overhead bound.

Exact schema-v2 SQL profile: 19 tables, 27 triggers, normalized SHA-256 `41ee900df99b3c1b44700e2de628d3151e907c8d0069f87098eb9fd72a3f6fec`.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

It delivers the active-database and genesis-checkpoint core of `phase1-projection-v2`, including exact side roles, fixed-order original Phase 1 rows, strict zero-caregiver absence, independent checkpoint integrity, raw checkpoint linkage before `CP(g,e)` projection, checkpoint-database semantic comparison, and exact nested/unlisted/wrong-location behavior.

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — merged

PR #67 merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

The cumulative evidence ledger validates exact `checkpoint_registration_repaired` current/prior `CP` linkage plus database SHA, manifest SHA, database size, and checkpoint-store bytes before projection.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

### Slice 36b2a2 — merged

PR #69 merged as `64ea9eb094a687c056a571d362c1914aaf7911f2`.

Tests-only head `38bab7c49d41c16a8ef8b73da52fd4e4bd7e9f14` produced the intended red run 443 before the retention projection module existed. Final pre-merge head `99d2b6db078572748e0e275b64955949bf9e9aec` passed run 450 with `185 passed in 15.55s`; installation, compilation, and schema-v1 genesis CLI smoke succeeded.

The retention layer validates normal prune, restored pre-commit failure, committed cleanup failure, `STAGE(CP(g,e))`, pending reconciliation, interruption after deletion, retry, and completion. Deleted identity and bytes come only from prior immutable artifact evidence.

Durable note: `docs/phase2/SLICE36B2A2_RETENTION_PROJECTION.md`.

### Slice 36b2a3 — implemented on PR #70

Branch: `slice36b2-rollback-projection`.

Base: merged PR #69 at `64ea9eb094a687c056a571d362c1914aaf7911f2`.

Tests-only head `38a8933f53d09ac5c4d39748a498cf90c5fa631e` produced the intended red run 452 before the rollback projection module existed.

Implementation plus the lineage-sequence collision test reached code/test candidate `b66a93c2b99b6f48ea06d3b13e47f028297d4c9e`. Run 458 passed with `191 passed in 15.59s`; dependency installation, compilation, and schema-v1 genesis CLI smoke succeeded. The unchanged 152 Phase 1 tests remain included. Codex was not used.

The paired rollback scenario performs one real water wake, then selects genesis and completes the full protected rollback chain:

- selected checkpoint `CP(0,2)`
- abandoned-future archive `RA(0,14,2)`
- source restore candidate `RC(0,15,2)`
- transformed candidate `TC(1,3)`
- `rollback_completed` at new-lineage event sequence `4`

Archive, source candidate, transformed candidate, manifests, database bytes, sizes, protected SQLite state, and exact cross-artifact links are independently validated before typed identity or byte-sentinel replacement.

After authority replacement, active registry state rewinds to the selected checkpoint while later checkpoint `CP(0,13)` remains physically retained as abandoned-future evidence. An extra visible checkpoint is accepted only when a validated pre-rollback archive registry proves the same raw identity, boundary, manifest digest, database digest, and size.

The new-lineage organism may retain an old-lineage latest-stable checkpoint reference. Rollback projection resolves that reference by exact raw checkpoint ID plus event sequence against the validated artifact map; it does not invent a same-lineage token.

Rollback events are keyed by `(lineage_generation, event_sequence, event_type)`. A protected scenario proves old-lineage `rollback_started` and new-lineage `rollback_completed` may both use sequence `15` without evidence overwrite.

Durable note: `docs/phase2/SLICE36B2A3_ROLLBACK_PROJECTION.md`.

## Exact next boundary: semantic event export

After PR #70 is reviewed and merged, create a new test-first branch from updated `main`.

Implement ADR 0009 export treatment and matrix P2-C16/P2-C17:

- validate canonical JSONL bytes independently on each side
- validate exact event range, count, order, and source-checkpoint linkage
- project exported event records through the already accepted exact event map
- replace export manifest `source_checkpoint_id` with the matching `CP` token
- exclude presentation path, raw export bytes, raw export SHA, and raw export size from cross-run equality only after independent validation
- keep every canonical event/state difference visible

Do not weaken checkpoint, repair, retention, or rollback evidence. Do not use wildcard, recursive key walk, suffix/prefix match, regex-by-key, or global key-name normalization.

After event export, remaining Slice 36b2 work is physical closure:

- independent checkpoint/archive/candidate overhead
- aggregate manifest/directory metadata overhead
- absolute 8 MiB active database and artifact limits
- absolute 40 MiB checkpoint-store limit
- absolute 64 MiB working-set limit
- exact 1 MiB next-wake reserve scenarios

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

1. inspect Issue #61, PR #70, this handoff, and all implemented Slice 36 notes
2. verify PR #70 final head and CI; review and merge it before dependent work
3. confirm the unchanged 152 Phase 1 tests remain included and passing
4. create an event-export projection branch from updated `main`
5. validate raw JSONL, manifest, range/count/order, digest/size, and source-checkpoint linkage before semantic comparison
6. keep Codex deferred until the complete Phase 2 implementation candidate is ready for the single completion audit
