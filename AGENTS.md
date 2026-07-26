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

It implements schema-v2 genesis, exact protected zero/fixture configuration, unchanged original Phase 1 tables and budget locations, empty immutable consultation operational tables, stable schema-v2 checkpoint validation, no migration/downgrade path, zero-caregiver absence, and the accepted active-database overhead bound.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

It implements the active-database and genesis-checkpoint core of `phase1-projection-v2`: exact side roles, fixed-order original Phase 1 rows, declared schema-version normalization, strict zero-caregiver absence, independent checkpoint integrity, raw checkpoint linkage before `CP(g,e)` projection, checkpoint semantic comparison, and exact nested/unlisted/wrong-location behavior.

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — merged

PR #67 merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

It extends cumulative immutable evidence through exact checkpoint-repair identity, digest, size, and checkpoint-store projection paths.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

### Slice 36b2a2 — merged

PR #69 merged as `64ea9eb094a687c056a571d362c1914aaf7911f2`.

It closes normal retention prune, pre-commit restoration, committed staging failure, exact `STAGE(CP)`, pending reconciliation, interruption after deletion, retry, and completion. Raw deleted or staged identity and bytes must match prior immutable evidence before projection.

Durable note: `docs/phase2/SLICE36B2A2_RETENTION_PROJECTION.md`.

### Slice 36b2a3 — merged

PR #70 merged as `054382a1ea57fa3e3c87d70d725b5a4a5415334b`.

Tests-only head `38a8933f53d09ac5c4d39748a498cf90c5fa631e` produced red run 452. Final head `4a0f82432e780245b3258983735c4f224a2f89fc` passed run 461 with `191 passed in 19.74s` plus successful installation, compilation, and schema-v1 genesis CLI smoke.

It validates exact `CP`, `RA`, `RC`, and `TC` artifact/event linkage, cross-lineage latest-stable checkpoint references, abandoned-future checkpoint preservation, and lineage-aware event-sequence reuse.

Durable note: `docs/phase2/SLICE36B2A3_ROLLBACK_PROJECTION.md`.

### Slice 36b2a4 — implemented on PR #71

Branch: `slice36b2-event-export-projection`.

Base: merged PR #70 at `054382a1ea57fa3e3c87d70d725b5a4a5415334b`.

Tests-only head `9430b314f925ed09c1e8b9a49b7b21961bcd1e70` produced red run 463 before implementation.

Implementation and corruption-test candidate `379868664f1724f7c1cd5c2c82e0db09a7dfe960` passed run 465 with `196 passed in 22.75s` plus successful installation, compilation, and schema-v1 genesis CLI smoke. The unchanged 152 Phase 1 tests remain included.

The projection independently validates raw canonical JSONL, exact manifest and event schemas, event range/count/order, active source-checkpoint linkage, reconstructed bytes, raw size, and raw SHA before semantic replacement.

It projects export manifest `source_checkpoint_id` to `CP`, applies the accepted exact event map to each exported event, and normalizes only exact schema-version fields.

Presentation path, raw bytes, raw SHA, raw size, and API wrapper fields are excluded only after validation. Byte-identical copies at another path compare semantically; changed, noncanonical, incomplete, or post-capture-modified files reject.

Durable note: `docs/phase2/SLICE36B2A4_EVENT_EXPORT_PROJECTION.md`.

### Exact next boundary — physical projection closure

After PR #71 is reviewed and merged, create a test-first branch from updated `main`.

Close ADR 0009 section 9 and remaining P2-O evidence:

- schema-v2-zero active database overhead is at most 256 KiB over paired schema-v1
- each schema-v2-zero checkpoint/archive/candidate database overhead is at most 256 KiB over its pair
- aggregate extra manifest/directory metadata is at most 1 MiB
- schema-v2-zero independently obeys absolute 8 MiB active/artifact limits
- checkpoint store independently obeys 40 MiB
- runtime working set independently obeys 64 MiB
- enqueue and future operations preserve the exact 1 MiB next-wake reserve
- real near-ceiling checkpoint, repair, retention, rollback, and reserve scenarios leave no partial canonical mutation

Do not replace absolute-limit evidence with paired byte equality. Legitimate structural overhead does not authorize larger absolute ceilings.

Slice 37 remains blocked until all Slice 36 evidence is merged and no blocker/high/medium boundary defect remains.

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

A request created at lifecycle `N` is eligible through `N+2`. Proposal expiry is identical. Rollback begins a fresh lineage epoch while ADR 0007 still permits at most one completed rollback.

## Implementation discipline

Every slice maps to accepted matrix IDs. The unchanged 152-test Phase 1 suite is always the first regression layer.

If implementation reveals a contradiction, return to reviewed ADR work. Code must not choose a private interpretation.

## Codex audit cadence

Codex audits are high-cost gates, not per-slice or per-PR review.

1. Phase 2 design audit: completed in Issue #59.
2. Focused zero-caregiver correction re-audit: completed in Issue #63.
3. Phase 2 implementation audit: run once after every accepted matrix requirement has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green implementation candidate is ready to freeze.

No Codex audit was used for retention, rollback, or event-export projection.

## Exact restart point

1. verify Phase 1 closure and accepted ADRs 0008–0009
2. inspect Issue #61, PR #71, `docs/HANDOFF.md`, and all implemented Slice 36 notes
3. verify PR #71 final head and CI, then review and merge it before dependent work
4. create a physical-closure branch from updated `main`
5. implement paired overhead and independent absolute-limit evidence test-first
6. keep all 152 Phase 1 tests unchanged and passing
7. request the Codex implementation audit only when the complete Phase 2 candidate is ready to freeze

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
