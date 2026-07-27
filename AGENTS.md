# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI. Reconstruct the project from repository and current GitHub state before proposing or changing anything. Repository and GitHub state outrank conversation history.

## Read order

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/AI_COLLABORATION_OPERATIONS.md`
4. `docs/ORIGIN.md`
5. `docs/MINIMAL_ORGANISM_CONTRACT.md`
6. accepted `docs/decisions/` files in numeric order
7. `docs/ARCHITECTURE.md`
8. `docs/ROADMAP.md`
9. `docs/IMPLEMENTATION_DISCIPLINE.md`
10. `docs/PHASE1_TEST_MATRIX.md`
11. implemented `docs/phase1/` notes
12. implemented `docs/phase2/` notes
13. `docs/RESEARCH_QUESTIONS.md`
14. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
15. preliminary `docs/research/` notes
16. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
17. `docs/HANDOFF.md`
18. current Issues and PRs
19. for Phase 2: accepted ADRs 0008 and 0009, Consultation Protocol v1, the Phase 2 matrix, and Issue #59/#63 audit reports

## Core question

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and retain capability while requiring less justified caregiver assistance.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

Do not flatten SUDACHI into a generic agent, chatbot, virtual pet, or self-modifying loop.

## Frozen Phase 1

Normative precedence:

1. Minimal Organism Contract v0.2
2. accepted ADRs 0001–0007
3. protected Phase 1 tests and `docs/PHASE1_TEST_MATRIX.md`

Phase 1 passed final independent audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: all six findings resolved, no new blocker/high/medium defect, and 152 tests passed.

Phase 1 body and trusted kernel are frozen. Phase 2 must not condition or reinterpret Phase 1 tests, alter garden actions, selector, executor, evaluators, clocks, checkpoints, rollback, or authority, or add hidden network, subprocess, workspace, arbitrary-code, or continuous-execution routes.

PR #73 reopened the shared kernel only for explicitly authorized absolute-limit defects discovered by protected real-file tests. The pre-repair bodies are retained in explicit `*_impl.py` modules and the narrow guards are documented in `docs/phase2/SLICE36B2A6_ABSOLUTE_PHYSICAL_LIMITS.md`. After PR #73 merges, those boundaries are re-frozen; the wrappers are not permission for general Phase 1 redesign.

## Accepted Phase 2 consultation boundary

ADRs 0008 and 0009, Consultation Protocol v1, and the Phase 2 matrix are the accepted design package. Issue #61 owns implementation.

Accepted invariants include:

- original Phase 1 `budget_config` and every original budget-version location remain exactly `phase1-v1`
- Phase 2 policy lives only in one protected immutable `consultation_configuration` singleton
- checkpoint, repair, retention, rollback, and export byte-derived identities use exact ADR 0009 locations and typed tokens
- projected-away SHA, size, and path values are independently recomputed and physically bounded on each side
- no wildcard, recursive key walk, suffix/prefix match, regex-by-key, or global key-name normalization
- schema-v2 overhead caps do not replace absolute 8/40/64 MiB and 1 MiB reserve limits

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are provenance only.

## Operational boundaries

1. Garden request wake preserves exact Phase 1 outcome and failure truth and uses only an optional storage-safe request extension.
2. Administrative dispatch admission commits and charges before external fixture work and releases SQLite ownership first.
3. The deterministic fixture receives only the final request envelope and declared case, with no authority or runtime capability handles.
4. Administrative ingress or terminalization validates exact schemas, identities, sizes, lineage, and physical budgets and never automatically retries fixture work.
5. Explicit disposition wake considers at most one proposal, checkpoints, and has no selector, action, memory, or skill effect in the first implementation.

Proposal types: `action_candidate`, `abstain`, `defer`.

Dispositions: `accepted`, `rejected`, `deferred`, `clarification_requested`.

Clarification rounds: zero.

## Slice 36 implementation state

### Slice 36a — merged

PR #65 merged as `75077220ecb52256857f2b234283d36e3c0f51d2`.

It implements schema-v2 genesis, exact protected zero/fixture configuration, unchanged Phase 1 tables and budget locations, immutable consultation objects, stable schema-v2 checkpoint validation, no migration/downgrade path, zero-caregiver absence, and the genesis active-database overhead bound.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

It implements the active-database and genesis-checkpoint core of `phase1-projection-v2`: exact side roles, fixed-order original Phase 1 rows, declared schema-version normalization, strict zero-caregiver absence, independent checkpoint integrity, raw checkpoint linkage before `CP(g,e)`, checkpoint semantic comparison, and exact nested/unlisted/wrong-location behavior.

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — merged

PR #67 merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

It extends cumulative immutable evidence through exact checkpoint-repair identity, digest, size, previous-boundary, and checkpoint-store projection paths.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

### Slice 36b2a2 — merged

PR #69 merged as `64ea9eb094a687c056a571d362c1914aaf7911f2`.

It closes normal retention prune, restored pre-commit failure, committed staging failure, exact `STAGE(CP)`, pending reconciliation, interruption after deletion, retry, and completion. Deleted or staged identity and bytes must match prior immutable evidence before projection.

Durable note: `docs/phase2/SLICE36B2A2_RETENTION_PROJECTION.md`.

### Slice 36b2a3 — merged

PR #70 merged as `054382a1ea57fa3e3c87d70d725b5a4a5415334b`.

Final head `4a0f82432e780245b3258983735c4f224a2f89fc` passed run 461 with `191 passed in 19.74s`. It validates exact `CP`, `RA`, `RC`, and `TC` linkage, cross-lineage checkpoint references, abandoned-future preservation, and lineage-aware event-sequence reuse.

Durable note: `docs/phase2/SLICE36B2A3_ROLLBACK_PROJECTION.md`.

### Slice 36b2a4 — merged

PR #71 merged as `d7ce1703eaaf9aca1a33f72add4a9dfa707e7abe`.

Final head `31736c45ff1879002991a6249c86ffa86c0f07b8` passed run 468 with `196 passed in 19.01s` plus successful installation, compilation, and schema-v1 genesis CLI smoke.

It independently validates canonical JSONL, exact export manifest/event schemas, event range/count/order, source checkpoint, reconstructed bytes, raw size, and raw SHA before semantic projection.

Durable note: `docs/phase2/SLICE36B2A4_EVENT_EXPORT_PROJECTION.md`.

### Slice 36b2a5 — merged

PR #72 merged as `3cd46b5929d6bc5dea8b0cbede417b40e792ce72`.

Final run 475 passed with `200 passed in 20.09s`. It measures paired schema-v1/schema-v2-zero active and `CP`/`RA`/`RC`/`TC` database overhead at at most 256 KiB and aggregate additional non-database metadata at at most 1 MiB.

Durable note: `docs/phase2/SLICE36B2A5_PHYSICAL_OVERHEAD.md`.

### Slice 36b2a6 — implemented on PR #73

Branch: `slice36b2-absolute-physical-limits`.

Base: merged PR #72 at `3cd46b5929d6bc5dea8b0cbede417b40e792ce72`.

Code head `409b82962cee00f59e573b6bf5c90d0d9d426cb6` passed run 502 with `222 passed in 32.16s`, including all unchanged 152 Phase 1 tests, dependency installation, compilation, and schema-v1 genesis CLI smoke.

It closes P2-O18, P2-O19, P2-O21, and P2-O22 with real schema-v2-zero files:

- active and artifact 8 MiB boundaries
- checkpoint-store 40 MiB boundary
- runtime working-set 64 MiB boundary
- exact 1 MiB next-wake reserve
- exact and one-over checkpoint publication, pending repair, retention, rollback archive, source candidate, and transformed candidate paths
- idempotent RA/RC/TC reentry admission at the same absolute working-set limit
- no retained newly published artifact, deleted existing artifact, or rejected canonical registration
- raw zero-caregiver configuration and empty operational tables in active, `CP`, `RA`, `RC`, and `TC` SQLite bodies

Protected tests found and closed Issues #74–#78 plus the same-turn post-write registration-growth defect under explicit project-owner authorization. No accepted limit, authority, idempotence, retention choice, or semantic rule changed.

Durable notes:

- `docs/phase2/SLICE36B2A6_ABSOLUTE_PHYSICAL_LIMITS.md`
- `docs/phase2/SLICE36B2A6_ACTIVE_REPAIR_ADDENDUM.md`

PR #73 remains the merge gate until final documentation CI is green, review is complete, and the PR is merged.

## Accepted budgets and expiry

- schema-v2 new organisms only; no migration/downgrade
- base contract remains `0.2`
- request envelope ≤16 KiB
- complete external package ≤16 KiB
- provenance ≤8 KiB within package
- four requests and four charged fixture invocations per current lineage
- one outstanding current-lineage request
- 64 KiB exact logical payload per lineage
- zero human/model/money/declared fixture latency
- active database/artifact 8 MiB
- checkpoint store 40 MiB
- working set 64 MiB
- next-wake reserve 1 MiB

## Implementation discipline

Every slice maps to accepted matrix IDs. The unchanged 152-test Phase 1 suite is always the first regression layer.

If implementation reveals a contradiction, return to reviewed ADR work. Code must not choose a private interpretation.

## Codex audit cadence

Codex audits are high-cost gates, not per-slice or per-PR review.

1. Phase 2 design audit: completed in Issue #59.
2. Focused zero-caregiver correction re-audit: completed in Issue #63.
3. Phase 2 implementation audit: run once after every accepted matrix requirement has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green implementation candidate is ready to freeze.

No Codex audit was used for retention, rollback, event export, paired overhead, or absolute physical-limit closure.

## Exact restart point

1. inspect Issue #61, PR #73, `docs/HANDOFF.md`, and all implemented Slice 36 notes
2. verify PR #73 final documentation head and CI
3. review and merge PR #73; close Issues #74–#78 as completed and re-freeze the narrow Phase 1 boundaries
4. create Slice 37 from updated `main`
5. implement request-envelope/storage-safe extension requirements test-first
6. keep all 152 Phase 1 tests unchanged and passing
7. request Codex only when the complete Phase 2 implementation candidate is ready for the single completion audit

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
