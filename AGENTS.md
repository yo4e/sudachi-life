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
19. for Phase 2: accepted ADRs 0008 and 0009, `docs/phase2/CONSULTATION_PROTOCOL_V1.md`, `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`, and the Issue #59 and #63 audit reports

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

Phase 1 passed final independent audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: Findings 1–6 resolved, no new blocker/high/medium defect, and 152 tests passed. Issues #13 and #56 are closed. PR #57 merged as `c92aa8efd0b9800afd637ce1f1d16d3223bdeb3b`.

Phase 1 body and trusted kernel are frozen. Phase 2 must not condition or reinterpret Phase 1 tests, alter garden actions/selector/executor/evaluators/clocks/checkpoints/rollback/authority, or add hidden network, subprocess, workspace, arbitrary-code, or continuous-execution routes.

## Accepted Phase 2 Consultation Boundary

ADRs 0008 and 0009, Consultation Protocol v1, and the Phase 2 Consultation Boundary Test Matrix are the accepted Phase 2 design package. Issue #61 owns implementation.

The independent design audit reviewed PR #60 head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647` and concluded:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

The accepted package incorporates:

- exact `phase1-projection-v2` zero-caregiver semantic artifact comparison under ADR 0009
- exact proposal field sets, type-specific values, evaluator sets, and inherited expiry
- exact domain-separated digest preimages and acyclic identity graph
- exact per-lineage 64 KiB formula without double counting
- optional request-extension savepoint and real 8 MiB/reserve boundary evidence

A focused read-only re-audit of PR #64 head `e4f3527518cbc4e4ff8ab239a90f48bfa47fdbb8` confirmed the ADR 0008 contradiction and concluded ADR 0009 was ready after specified documentation/matrix corrections. Those corrections passed CI and ADR 0009 is accepted. No further design re-audit is planned unless the same boundary changes materially again.

### Accepted zero-caregiver correction

- original Phase 1 `budget_config` and all original budget-version locations remain exactly `phase1-v1`
- Phase 2 policy lives in one protected immutable `consultation_configuration` singleton
- checkpoint, repair, retention, rollback, and export byte-derived identities use the exact semantic tokens and locations in ADR 0009
- projected-away SHA/size/path values are independently recomputed and physically bounded on each side
- no wildcard, recursive, suffix, prefix, or global key-name normalization is allowed
- schema-v2 structural overhead is capped and absolute 8/40/64 MiB plus 1 MiB reserve tests remain mandatory

### Five boundaries

1. **Garden request wake** preserves exact Phase 1 outcome/failure truth. Request metadata is an optional savepoint extension; extension-only storage refusal cannot fail the valid core wake.
2. **Administrative dispatch admission** uses a fresh fail-fast transaction, requires a stable current-lineage request, charges before external work, and releases SQLite ownership before fixture execution.
3. **External deterministic fixture** receives only the final request envelope and declared case, with no DB/path/workspace/executor/evaluator/checkpoint/rollback/network/subprocess/credential/tool/randomness capability.
4. **Administrative ingress or terminalization** independently verifies exact schemas, preimages, IDs, proposal constraints, expiry, sizes, lineage, and physical budgets. It never grants caregiver authority or automatically retries fixture work.
5. **Explicit disposition wake** is caller-selected, claims no garden input, considers at most one proposal, preserves the garden failure streak, checkpoints, and has no selector/action/memory/skill effect in the first implementation.

Proposal types: `action_candidate`, `abstain`, `defer`.

Final dispositions: `accepted`, `rejected`, `deferred`, `clarification_requested`.

Clarification rounds: zero.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identity are provenance only.

## Slice 36 implementation state

Issue #61 splits Slice 36 into two reviewable boundaries.

### Slice 36a — schema-v2 genesis and protected configuration

PR #65 implements:

- explicit schema-v2 initialization while schema-v1 remains the default
- exact zero/fixture protected consultation configuration objects
- unchanged original Phase 1 tables, budget singleton, event budget version, and default public status
- one immutable `consultation_configuration` singleton
- nine empty immutable operational consultation tables
- fixed foreign-key/linkage and response-versus-terminal guards before later slices write rows
- schema-v2 checkpoint-stable genesis and version-aware checkpoint validation
- no migration/downgrade surface
- strict zero-caregiver genesis absence
- active database overhead within the accepted 256 KiB cap

The exact SQLite schema-v2 profile is 19 tables plus 27 triggers, normalized SHA-256 `41ee900df99b3c1b44700e2de628d3151e907c8d0069f87098eb9fd72a3f6fec`.

Test-first evidence:

- red CI run 409: missing `sudachi_life.phase2_schema`
- later green candidate runs preserve all 152 Phase 1 tests and add protected Phase 2 genesis/profile tests
- durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`

PR #65 must be merged before Slice 36b begins. If GitHub already shows it merged, treat Slice 36a as complete.

### Slice 36b — semantic artifact projection oracle

After 36a, implement the accepted closed `phase1-projection-v2` oracle for:

- P2-C01–P2-C05
- P2-C08–P2-C18
- P2-O16–P2-O22

It must cover checkpoint, repair, retention, rollback, and event export artifacts with independent per-side integrity and no wildcard projection.

Slice 37 remains blocked until 36a and 36b are both merged and no blocker/high/medium boundary defect remains.

## Accepted budgets and expiry

- newly initialized schema-v2 organisms only; no migration/downgrade
- base contract remains `0.2`
- request envelope at most 16 KiB
- complete external package at most 16 KiB
- provenance at most 8 KiB within package limit
- four requests and four charged fixture invocations per current lineage
- one current-lineage outstanding request
- 64 KiB logical payload per current lineage, exactly request-envelope bytes plus successfully ingressed complete-package bytes
- zero human/model/money/declared latency for deterministic fixture
- 8 MiB active database
- 40 MiB checkpoint store
- 64 MiB working set
- 1 MiB next-wake active-database reserve

A request created at lifecycle `N` is eligible through `N+2`. Every proposal inherits that expiry exactly. Disposition at considering lifecycle `N+3` or later rejects as expired.

Rollback starts a fresh current-lineage epoch. Old-lineage rows remain immutable historical evidence and inactive. ADR 0007 bounds one physical organism to at most two epochs/eight charged fixture invocations.

## Implementation discipline

Every slice must map to accepted matrix IDs. The unchanged 152-test Phase 1 suite is always the first regression layer.

The first implementation may add only schema-v2 initialization/validation, exact typed envelopes/digests, request extension, dispatch/precharge, deterministic fixture boundary, ingress/terminalization, explicit disposition, reporting, and protected tests.

It may not add live caregiver/API/human chat, memory, skills, source/test generation, model training, arbitrary Python/shell/SQL/tools/paths/URLs/credentials, organism network/subprocess, continuous execution, personality/emotion state, caregiver authority, or a generic agent framework.

If implementation reveals a contradiction, return to reviewed ADR work. Code must not choose a private interpretation.

## Codex audit cadence

Codex audits are high-cost gates, not per-slice or per-PR review.

1. Phase 2 design audit: completed in Issue #59.
2. Focused zero-caregiver correction re-audit: completed in Issue #63; corrections accepted as ADR 0009.
3. Phase 2 implementation audit: run once after every accepted matrix requirement has protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green implementation candidate is ready to freeze.

Avoid audit-repair-reaudit ping-pong unless evidence is insufficient, a gate remains blocked, or a repair materially changes the same certified boundary.

## Exact restart point

1. verify Phase 1 closure and accepted ADRs 0008–0009
2. inspect Issue #61, PR #65, and `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`
3. if PR #65 is open, complete its CI/review/merge without starting 36b
4. if PR #65 is merged, create a new Slice 36b branch from updated `main`
5. implement the exact semantic artifact oracle for the declared C/O matrix IDs
6. keep all 152 Phase 1 tests unchanged and passing
7. request one implementation audit only when the complete Phase 2 candidate is ready to freeze

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
