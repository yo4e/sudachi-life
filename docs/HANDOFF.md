# SUDACHI Handoff

Updated: **2026-07-26**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36a is implemented on draft PR #65; verify its current GitHub state before beginning Slice 36b.

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

The design audit reviewed PR #60 head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647` and concluded:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

A focused re-audit of ADR 0009 confirmed the zero-caregiver checkpoint/artifact contradiction and concluded:

> ADR 0009 is ready after specified documentation or matrix corrections.

Those corrections are accepted. The original Phase 1 budget stays exactly `phase1-v1`; Phase 2 policy lives in an immutable `consultation_configuration`; and byte-derived checkpoint/repair/retention/rollback/export identities use the exact semantic projection in ADR 0009.

## Current implementation: Slice 36a

Issue #61 splits Slice 36 into:

- 36a: schema-v2 genesis and protected configuration
- 36b: full `phase1-projection-v2` semantic artifact oracle

PR #65 implements 36a for P2-A01–A05, P2-B01–B12, genesis/configuration P2-C06–C07, and P2-O15.

Delivered behavior:

- schema-v1 remains the default API/CLI path
- schema-v2 requires explicit schema version and one accepted consultation configuration
- original Phase 1 tables, budget singleton, event budget versions, and default public status remain unchanged
- one exact immutable `consultation_configuration` singleton
- nine empty immutable operational consultation tables
- foreign-key/linkage, successful-response proposal, cost-completion, and response-versus-terminal guards fixed at genesis
- schema-v2 checkpoint-stable genesis and version-aware checkpoint validation
- no migration/downgrade surface
- strict zero-caregiver genesis absence
- schema-v2 active DB overhead within the accepted 256 KiB cap

Exact protected schema-v2 SQL profile:

- 19 tables
- 27 triggers
- normalized SHA-256 `41ee900df99b3c1b44700e2de628d3151e907c8d0069f87098eb9fd72a3f6fec`

Test-first history:

- run 409 failed at collection because `sudachi_life.phase2_schema` did not exist
- implementation candidates preserve all 152 Phase 1 tests and add protected genesis/configuration/profile tests
- durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`

If PR #65 is still open, finish its exact-head CI and merge before any 36b work. If merged, treat 36a as complete.

## Next implementation: Slice 36b

Slice 36b owns:

- P2-C01–C05
- P2-C08–C18
- P2-O16–O22

It must implement the closed typed `phase1-projection-v2` oracle across:

- normal and maintenance checkpoints
- checkpoint registration repair
- retention prune/failure/reconciliation
- rollback archive/source candidate/transformed candidate/completion
- event export
- per-side digest/size/linkage/integrity validation
- exact no-wildcard location guards
- paired and real near-ceiling physical evidence

Slice 37 remains blocked until both 36a and 36b are merged and no blocker/high/medium boundary defect remains.

## Five operational boundaries

1. **Garden request wake** preserves exact Phase 1 `no_applicable_action` outcome/failure truth and uses an optional storage-safe request extension.
2. **Administrative dispatch admission** commits and charges before external work, then releases SQLite ownership.
3. **External deterministic fixture** receives only the request envelope and declared case, with no authority/capability handles.
4. **Administrative ingress or terminalization** verifies exact data and never automatically retries fixture work.
5. **Explicit disposition wake** considers at most one proposal, checkpoints, and has no action/memory/skill effect in the first implementation.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver identity is provenance only.

## Accepted budgets and lifecycle rules

- schema-v2 new organisms only; no migration/downgrade
- base contract `0.2`
- request envelope ≤16 KiB
- complete external package ≤16 KiB
- provenance ≤8 KiB inside package limit
- four requests/four charged fixture calls per current lineage
- one current-lineage outstanding request
- 64 KiB exact logical payload per current lineage
- zero human/model/money/declared latency
- active DB 8 MiB
- checkpoints 40 MiB
- working set 64 MiB
- next-wake reserve 1 MiB

Request lifecycle `N` is eligible through `N+2`; proposal expiry is identical. Considering lifecycle `N+3` or later rejects as expired.

Rollback starts a fresh lineage epoch. ADR 0007 bounds one physical organism to at most two epochs/eight charged fixture invocations.

## Audit cadence

The Phase 2 design audit and focused ADR 0009 correction re-audit are complete. The next Codex audit occurs once only after the full accepted Phase 2 implementation, every matrix item has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze.

Do not use Codex for each slice, PR, ordinary bug, or documentation edit.

## Explicit exclusions

No live model/API/human caregiver, memory or skill generation, source/test generation, training, arbitrary code/SQL/shell/tools/paths/URLs/credentials, organism network/subprocess, continuous execution, personality/emotion state, caregiver-controlled authority, or generic agent framework.

## Exact restart

1. inspect Issue #61, PR #65, and `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`
2. if PR #65 is open, verify exact-head CI and complete review/merge
3. after PR #65 merges, create a new Slice 36b branch from updated `main`
4. write failing protected tests for the exact semantic artifact projection
5. implement only the declared 36b C/O matrix scope
6. keep all 152 Phase 1 tests unchanged and passing
7. do not begin Slice 37 until all Slice 36 evidence is merged

No critical decision may remain only in chat.
