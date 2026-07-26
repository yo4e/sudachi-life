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

Phase 1 passed final independent audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: all six findings resolved, no new blocker/high/medium defect, and 152 tests passed. Issues #13 and #56 are closed. PR #57 merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

Phase 1 body and trusted kernel are frozen. Phase 2 must not condition or reinterpret Phase 1 tests, alter garden actions/selector/executor/evaluators/clocks/checkpoints/rollback/authority, or add hidden network, subprocess, workspace, arbitrary-code, or continuous-execution routes.

## Accepted Phase 2 Consultation Boundary

ADRs 0008 and 0009, Consultation Protocol v1, and the Phase 2 matrix are the accepted design package. Issue #61 owns implementation.

The Phase 2 design audit completed in Issue #59. A focused read-only re-audit in Issue #63 confirmed the zero-caregiver artifact contradiction and accepted ADR 0009 after specified corrections.

Accepted invariants include:

- original Phase 1 `budget_config` and all original budget-version locations remain exactly `phase1-v1`
- Phase 2 policy lives only in one protected immutable `consultation_configuration` singleton
- checkpoint, repair, retention, rollback, and export byte-derived identities use exact ADR 0009 locations and typed tokens
- projected-away SHA/size/path values are independently recomputed and physically bounded on each side
- no wildcard, recursive key walk, suffix/prefix match, regex-by-key, or global key-name normalization
- schema-v2 overhead caps do not replace the absolute 8/40/64 MiB and 1 MiB reserve limits

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are provenance only.

## Operational boundaries

1. Garden request wake preserves exact Phase 1 outcome/failure truth and uses only an optional storage-safe request extension.
2. Administrative dispatch admission commits and charges before external fixture work and releases SQLite ownership first.
3. The deterministic fixture receives only the final request envelope and declared case, with no authority or runtime capability handles.
4. Administrative ingress or terminalization validates exact schemas, identities, sizes, lineage, and physical budgets and never automatically retries fixture work.
5. Explicit disposition wake considers at most one proposal, checkpoints, and has no selector/action/memory/skill effect in the first implementation.

Proposal types: `action_candidate`, `abstain`, `defer`.

Dispositions: `accepted`, `rejected`, `deferred`, `clarification_requested`.

Clarification rounds: zero.

## Slice 36 implementation state

### Slice 36a — merged

PR #65 merged as `75077220ecb52256857f2b234283d36e3c0f51d2`.

It implements explicit schema-v2 genesis, exact protected zero/fixture configuration, unchanged original Phase 1 tables and budget locations, nine empty immutable consultation operational tables, stable schema-v2 checkpoint validation, no migration/downgrade path, zero-caregiver absence, and the accepted active-database overhead bound.

Exact schema-v2 SQL profile: 19 tables, 27 triggers, normalized SHA-256 `41ee900df99b3c1b44700e2de628d3151e907c8d0069f87098eb9fd72a3f6fec`.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

Final reviewed head `46ba5b857794e63bf2e74552c2f5e84d1e042c93` passed run 433 with `175 passed in 21.95s` plus successful install, compile, and schema-v1 genesis CLI smoke.

It implements the active-database and genesis-checkpoint core of `phase1-projection-v2`:

- explicit schema-v1 left and schema-v2-zero right controls
- fixed-order original Phase 1 rows and original AUTOINCREMENT sequences
- exact declared schema-version normalization only
- strict zero-caregiver absence
- independent checkpoint directory/manifest/database/registry integrity
- raw organism, registry, manifest, directory, and stabilized-event linkage before `CP(g,e)` projection
- checkpoint database Phase 1 semantic state retained in equality
- nested, unlisted, added, and wrong-location values remain exact

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — current merge gate

PR #67 implements pending-checkpoint repair evidence.

Test-first evidence:

- tests-only head `53c3d4c1795c54d5872c113a0aa2e65653c9b412`
- red run 435: merged 36b1 lacked the evidence-ledger API
- implementation head before documentation synchronization `18c97c130be81f7d72c17a49d02c15fa3a5f9a58`
- run 436: `178 passed in 12.95s`; install, compile, and schema-v1 genesis CLI smoke succeeded

The oracle now has cumulative frozen per-run evidence for checkpoint artifacts, raw/projected event payloads, and ordered retained checkpoint boundaries. Existing evidence may be extended only when its immutable raw artifact and event facts remain identical.

For exact `checkpoint_registration_repaired` paths, capture independently validates:

- repaired raw checkpoint identity against its `CP(lineage,event)` artifact
- previous raw checkpoint identity against its exact prior `CP` boundary, including null/zero genesis semantics
- database SHA, manifest SHA, and database size against the artifact
- checkpoint-store bytes against the measured store

Only the two declared checkpoint identity paths and four declared byte-derived paths are projected. Every unlisted field, event column, sequence, source, lineage, lifecycle, and authority remains exact.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

PR #67 requires one final exact-head green CI result after continuity synchronization before ready/merge.

### Remaining Slice 36b2

After PR #67 merges, continue in bounded sub-slices:

1. retention prune, pre-commit failure, post-commit staging failure, pending reconciliation, interruption, and retry completion
2. rollback archive, source candidate, transformed candidate, and completion
3. semantic event export
4. checkpoint/archive/candidate overhead, aggregate metadata, and absolute physical-limit evidence

Retention must capture validated prunable artifact evidence before deletion. Later `checkpoint_pruned`, retention-failure, and reconciliation events must be checked against that immutable witness, not reconstructed from ID spelling.

Exact `CP`, `STAGE`, `RA`, `RC`, and `TC` locations remain those accepted by ADR 0009. Do not weaken the merged 36b1 core.

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

The first implementation may add only accepted schema-v2 initialization/validation, exact typed envelopes/digests, request extension, dispatch/precharge, deterministic fixture boundary, ingress/terminalization, explicit disposition, reporting, projection evidence, and protected tests.

It may not add live caregiver/API/human chat, memory, skills, source/test generation, training, arbitrary Python/shell/SQL/tools/paths/URLs/credentials, organism network/subprocess, continuous execution, personality/emotion state, caregiver authority, or a generic agent framework.

If implementation reveals a contradiction, return to reviewed ADR work. Code must not choose a private interpretation.

## Codex audit cadence

Codex audits are high-cost gates, not per-slice or per-PR review.

1. Phase 2 design audit: completed in Issue #59.
2. Focused zero-caregiver correction re-audit: completed in Issue #63.
3. Phase 2 implementation audit: run once after every accepted matrix requirement has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green implementation candidate is ready to freeze.

## Exact restart point

1. verify Phase 1 closure and accepted ADRs 0008–0009
2. inspect Issue #61, PR #67, `docs/HANDOFF.md`, and `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`
3. if PR #67 is open, verify its final exact-head CI and complete review/squash merge
4. create the retention projection sub-slice from updated `main`
5. capture prunable/staged artifact evidence before deletion and extend the exact typed map through prune/failure/reconciliation
6. keep all 152 Phase 1 tests unchanged and passing
7. request the implementation audit only when the complete Phase 2 candidate is ready to freeze

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
