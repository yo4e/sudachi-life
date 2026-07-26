# SUDACHI Handoff

Updated: **2026-07-26**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36a, Slice 36b1, and Slice 36b2a1 are merged. The exact next boundary is test-first retention projection.

No live caregiver integration is authorized.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, Minimal Organism Contract v0.2, accepted ADRs 0001–0009, the Phase 1 matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, this handoff, the accepted Consultation Protocol v1, the accepted Phase 2 matrix, implemented Phase 2 notes, and current Issues/PRs.

## Thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

Repository is auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

Issues #13 and #56 are closed. PR #57 merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

The final Phase 1 audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and found all six findings resolved, no new blocker/high/medium defect, and 152 tests passing. Phase 1 remains the unchanged schema-v1 control.

Do not alter Phase 1 garden actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, authority categories, or protected tests for Phase 2 convenience.

## Accepted Phase 2 design

ADRs 0008 and 0009, Consultation Protocol v1, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` form one accepted design package.

The Phase 2 design audit and focused ADR 0009 re-audit are complete. Original Phase 1 budget locations stay exactly `phase1-v1`; Phase 2 policy lives in immutable `consultation_configuration`; and checkpoint, repair, retention, rollback, and export byte-derived differences use the exact closed semantic projection in ADR 0009.

## Implemented Slice 36 foundation

### Slice 36a — merged

PR #65 merged as `75077220ecb52256857f2b234283d36e3c0f51d2`.

It delivers explicit schema-v2 genesis, exact protected zero/fixture configuration, unchanged original Phase 1 tables and budget locations, nine empty immutable consultation operational tables, stable schema-v2 checkpoint validation, no migration/downgrade path, zero-caregiver absence, and the accepted active-database overhead bound.

Exact schema-v2 SQL profile: 19 tables, 27 triggers, normalized SHA-256 `41ee900df99b3c1b44700e2de628d3151e907c8d0069f87098eb9fd72a3f6fec`.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

Final reviewed head `46ba5b857794e63bf2e74552c2f5e84d1e042c93` passed run 433 with `175 passed in 21.95s`; install, compile, and schema-v1 genesis CLI smoke succeeded.

It delivers the active-database and genesis-checkpoint core of `phase1-projection-v2`, including exact side roles, fixed-order original Phase 1 rows, strict zero-caregiver absence, checkpoint directory/manifest/database/registry integrity, raw checkpoint linkage before `CP(g,e)` projection, checkpoint database semantic comparison, and exact treatment of nested/unlisted/wrong-location values.

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — merged

PR #67 merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

Final candidate head `322b9138487d7c8ddbef3bed3908dadff91220a3` passed run 439 with `178 passed in 14.38s`; install, compile, and schema-v1 genesis CLI smoke succeeded.

The projection now uses cumulative frozen per-run evidence captured at deterministic operation boundaries. Evidence independently preserves:

- raw checkpoint identity, manifest/database digest, measured database/artifact size, canonical manifest, and projected internal Phase 1 state
- canonical event raw payload and its exact validated projected payload
- ordered retained checkpoint boundaries

Evidence extends only when previously captured raw checkpoint and event facts remain identical. It is noncanonical test/evaluation evidence, grants no authority, and changes no runtime behavior.

For `checkpoint_registration_repaired`, capture validates before projection:

- current raw checkpoint ID against `CP(lineage_generation,event_sequence)`
- prior raw checkpoint ID against its exact previous `CP` boundary, including null/zero genesis semantics
- database SHA, manifest SHA, and database size against the repaired artifact
- checkpoint-store bytes against the measured store

Only the two exact identity paths and four declared byte-derived paths are replaced. Every other event/state value remains exact.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

## Exact next boundary: retention projection

Create a new test-first branch from `main` at or after `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

The retention sub-slice must cover:

- normal `checkpoint_pruned`
- pre-commit retention failure with candidate restoration
- post-commit staging cleanup failure and `STAGE(CP(g,e))`
- reconciliation-pending audit
- interruption after staging deletion and before completion audit
- retry and `checkpoint_retention_cleanup_reconciled`

The evidence ledger must capture validated prunable or staged artifact evidence before deletion. Later events must be verified against that immutable witness. Deleted bytes may not be reconstructed from checkpoint ID spelling.

Exact `CP` and `STAGE` locations remain those accepted by ADR 0009. No wildcard, recursive key walk, suffix/prefix match, regex-by-key, or global key-name normalization is allowed.

After retention, remaining Slice 36b2 work is rollback (`RA`/`RC`/`TC`), semantic event export, and physical checkpoint/archive/candidate closure.

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

The next Codex use is the single Phase 2 implementation-completion audit, after every accepted matrix requirement has protected evidence and one exact CI-green candidate is ready to freeze. Do not use Codex per slice or ordinary edit.

## Explicit exclusions

No live model/API/human caregiver, memory or skill generation, source/test generation, training, arbitrary code/SQL/shell/tools/paths/URLs/credentials, organism network/subprocess, continuous execution, personality/emotion state, caregiver-controlled authority, or generic agent framework.

## Exact restart

1. inspect Issue #61, this handoff, and the three implemented Slice 36 notes
2. verify PR #67 is merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`
3. create a retention projection branch from updated `main`
4. capture validated prunable/staged artifact evidence before deletion and write failing paired tests
5. extend the cumulative ledger through exact prune/failure/reconciliation event paths
6. keep all 152 Phase 1 tests unchanged and passing
7. do not begin Slice 37 before all Slice 36 evidence is merged

No critical decision may remain only in chat.
