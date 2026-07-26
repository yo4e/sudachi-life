# SUDACHI Handoff

Updated: **2026-07-26**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36a, Slice 36b1, and Slice 36b2a1 are merged. Slice 36b2a2 retention projection is implemented test-first on draft PR #69. The exact next implementation boundary is rollback artifact projection.

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

Original Phase 1 budget locations stay exactly `phase1-v1`; Phase 2 policy lives in immutable `consultation_configuration`; and checkpoint, repair, retention, rollback, and export byte-derived differences use the exact closed semantic projection in ADR 0009.

## Implemented Slice 36 foundation

### Slice 36a — merged

PR #65 merged as `75077220ecb52256857f2b234283d36e3c0f51d2`.

It delivers explicit schema-v2 genesis, exact protected zero/fixture configuration, unchanged original Phase 1 tables and budget locations, nine empty immutable consultation operational tables, stable schema-v2 checkpoint validation, no migration/downgrade path, zero-caregiver absence, and the accepted active-database overhead bound.

Exact schema-v2 SQL profile: 19 tables, 27 triggers, normalized SHA-256 `41ee900df99b3c1b44700e2de628d3151e907c8d0069f87098eb9fd72a3f6fec`.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

Final reviewed head `46ba5b857794e63bf2e74552c2f5e84d1e042c93` passed run 433 with `175 passed in 21.95s`; install, compile, and schema-v1 genesis CLI smoke succeeded.

It delivers the active-database and genesis-checkpoint core of `phase1-projection-v2`, including exact side roles, fixed-order original Phase 1 rows, strict zero-caregiver absence, checkpoint directory/manifest/database/registry integrity, raw checkpoint linkage before `CP(g,e)` projection, checkpoint database semantic comparison, and exact treatment of nested, unlisted, and wrong-location values.

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — merged

PR #67 merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

Final candidate head `322b9138487d7c8ddbef3bed3908dadff91220a3` passed run 439 with `178 passed in 14.38s`; install, compile, and schema-v1 genesis CLI smoke succeeded.

The projection uses cumulative frozen per-run evidence for checkpoint artifacts, raw/projected event payloads, and ordered retained checkpoint boundaries. `checkpoint_registration_repaired` validates current and previous checkpoint identities plus database SHA, manifest SHA, database size, and checkpoint-store bytes before exact `CP` and byte-sentinel projection.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

### Slice 36b2a2 — draft PR #69

Branch: `slice36b2-retention-projection`.

Base: `main` at `ca32482b4f59ef704041734552dfcd81c5eb4535`, which includes merged PRs #66, #67, and #68.

Tests-only head `38bab7c49d41c16a8ef8b73da52fd4e4bd7e9f14` produced the intended red GitHub Actions run 443 because `sudachi_life.phase2_retention_projection` did not yet exist.

Implementation and corruption-test candidate `e2c87ebf9d20a09a83eba3179473fb6a24e4c356` passed run 447 with `185 passed in 16.65s`; dependency installation, compilation, and schema-v1 genesis CLI smoke succeeded.

The 185-test suite contains the unchanged 152 Phase 1 tests.

The retention extension adds cumulative noncanonical evidence for:

- prunable checkpoint artifacts captured before deletion
- committed-prune staging artifacts validated against the prior checkpoint witness
- exact raw and projected retention-event payloads
- current staged semantic boundaries

It covers:

- normal `checkpoint_pruned`
- pre-commit retention failure with candidate restoration
- post-commit staging cleanup failure and exact `STAGE(CP(g,e))`
- reconciliation-pending audit
- interruption after staging deletion and before completion audit
- retry and `checkpoint_retention_cleanup_reconciled`

Deleted artifact identity, digest, database size, and artifact size are obtained only from prior immutable evidence. They are never reconstructed from checkpoint-ID spelling.

For surviving staging, the directory manifest and database are independently validated, then their manifest digest, database digest, database size, artifact size, canonical manifest, and raw checkpoint identity must equal the pre-deletion witness before projection.

The pending reconciliation event maps its aligned raw checkpoint and staging lists through those witnesses while preserving list order. Completion follows the exact pending event sequence and reuses that validated projection after the physical staging directory has disappeared.

Protected negative evidence rejects:

- normal prune without a pre-deletion artifact witness
- a wrong raw staging directory before `STAGE` projection
- a one-byte discrepancy in `pruned_artifact_size_bytes` before sentinel replacement

The implementation does not change Phase 1 retention runtime, canonical schema, checkpoint policy, or the merged checkpoint/repair oracle.

Durable note: `docs/phase2/SLICE36B2A2_RETENTION_PROJECTION.md`.

## Exact next boundary: rollback projection

After PR #69 is reviewed and merged, create the next test-first Slice 36b2 branch from updated `main`.

Extend the same cumulative immutable evidence graph through the exact ADR 0009 rollback paths:

- pre-rollback archive identity and bytes as `RA(g,e)`
- source restore candidate as `RC(g,e)`
- transformed candidate as `TC(g,e)`
- selected checkpoint identity as `CP(g,e)`
- rollback completion and lineage linkage
- archive, source candidate, and transformed candidate integrity before projection

Do not weaken the merged checkpoint, repair, or retention layers. Raw archive/candidate identity, digest, size, manifest, and semantic database state must be independently validated before any typed replacement.

After rollback, remaining Slice 36b2 work is semantic event export and independent physical checkpoint/archive/candidate closure, including aggregate manifest/directory overhead and absolute 8/40/64 MiB plus 1 MiB reserve evidence.

Slice 37 remains blocked until all Slice 36 evidence is merged and no blocker/high/medium boundary defect remains.

## Accepted boundaries and budgets

Canonical writers remain exactly `organism` and `administration`; caregiver identity is provenance only.

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

No Codex audit was used for Slice 36b2a2.

## Explicit exclusions

No live model/API/human caregiver, memory or skill generation, source/test generation, training, arbitrary code/SQL/shell/tools/paths/URLs/credentials, organism network/subprocess, continuous execution, personality/emotion state, caregiver-controlled authority, or generic agent framework.

## Exact restart

1. inspect Issue #61, PR #69, this handoff, and the four implemented Slice 36 notes
2. verify PR #69 head and final CI; review and merge it before starting dependent work
3. confirm the unchanged 152 Phase 1 tests remain included and passing
4. create a rollback projection branch from updated `main`
5. capture archive/source/transformed candidate evidence before deletion or replacement
6. extend exact `RA`, `RC`, `TC`, and `CP` event/artifact paths test-first
7. keep Codex deferred until the complete Phase 2 implementation candidate is ready for the single completion audit
