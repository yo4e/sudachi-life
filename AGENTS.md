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
19. for Phase 2: ADRs 0008 and 0009, Consultation Protocol v1, the Phase 2 matrix, and Issue #59/#63 audit reports

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

Phase 1 passed final independent audit at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`. All 152 protected tests remain unchanged and form the schema-v1 control.

Phase 2 must not reinterpret or change Phase 1 garden actions, selector, executor, evaluators, clocks, checkpoint rules, rollback transformation, writer categories, or protected tests.

PR #73 temporarily reopened shared code only for explicitly authorized physical-limit defects and merged as `c9004027a94b709802af7f590d46de862dd93d7d`. Those physical boundaries are re-frozen. Pre-repair bodies remain in explicit `*_impl.py` modules.

The pre-request-extension garden wake remains byte-identical in `lifecycle_impl.py`, blob `c971d77cc9beab22f5c50fb692b4f81210cbf3ed`.

## Accepted Phase 2 consultation boundary

ADRs 0008 and 0009, Consultation Protocol v1, and the Phase 2 matrix form one accepted design package. Issue #61 owns implementation.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are untrusted provenance only.

Original Phase 1 budget locations remain exactly `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Operational boundaries remain explicit:

1. Garden request wake preserves the frozen Phase 1 outcome and uses only an optional storage-safe request extension.
2. Administrative dispatch commits and charges before fixture execution and releases SQLite ownership first.
3. The deterministic fixture receives only the final request envelope and declared case, with no runtime authority handles.
4. Administrative ingress or terminalization validates exact typed bytes and never automatically retries fixture work.
5. Explicit disposition considers at most one proposal, checkpoints, and does not execute an action or create memory/skills.

Proposal types: `action_candidate`, `abstain`, `defer`.

Dispositions: `accepted`, `rejected`, `deferred`, `clarification_requested`.

Clarification rounds: zero.

## Accepted limits

- request envelope: 16 KiB
- complete external package: 16 KiB
- provenance: 8 KiB within package
- four requests and four charged fixture invocations per current lineage
- one outstanding current-lineage request
- 64 KiB logical consultation payload per lineage
- zero human/model/money/declared fixture latency
- active database and individual database artifact: 8 MiB
- checkpoint store: 40 MiB
- runtime working set: 64 MiB
- next-wake reserve: 1 MiB

## Implementation state

### Slice 36 — complete

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, exact zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and independent absolute physical limits.

Final Slice 36 head `e1ef85e71ddefef06c9940145e6d27db0c22d39b`, run 512: `230 passed in 32.41s` plus install, compile, and schema-v1 CLI smoke.

Read the `docs/phase2/SLICE36*.md` notes for exact evidence. Issues #74–#79 are closed.

### Slice 37a1 — merged

PR #81 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`.

Final head `27d55d2853afb8f09530481dffa537f91b78640e`, run 520: `236 passed in 33.52s`.

It implements the bounded fixture request-wake core and exact request identity/envelope/checkpoint evidence.

Durable note: `docs/phase2/SLICE37A1_REQUEST_WAKE_CORE.md`.

### Slice 37a2 — merged

PR #83 merged as `208956c40bffc0eff94307e6d326a071ee386d94`.

Final head `41def40ffee3369194eae45734accccae1ce180c`, run 533: `242 passed in 31.65s`.

It closes P2-E01–P2-E09 and P2-D12 with real sidecar/checkpoint/working-set/reserve accounting and exact extension-only rollback.

Durable note: `docs/phase2/SLICE37A2_REQUEST_STORAGE_SAFETY.md`.

### Slice 37a3 — merged

PR #85 merged as `82e17c6ccba65323315b399ea6fad345a52db5f4`.

Final head `2d147d8acc1a4bd4f8750c499e5f94209b05ff55`, run 538: 245 tests passed; install, compile, and schema-v1 CLI smoke succeeded.

It closes P2-D14 backward-wall-time independence and P2-D15 nested/competing wake fail-fast evidence. No production source changed.

Durable note: `docs/phase2/SLICE37A3_REQUEST_TIME_CONCURRENCY.md`.

## Open request requirements

- P2-D07/D08 require later terminalization or disposition cycles to make four requests reachable without bypassing the frozen maintenance threshold.
- P2-D11 belongs with exact typed-envelope validation because request creation accepts no untrusted fields.
- P2-E10 remains blocked because optional typed request context is permitted but its exact field set is not enumerated. Do not invent private context fields merely to fill 16 KiB.

## Exact restart point

1. Start Slice 38 from updated `main` after the Slice 37a3 closeout documentation merge.
2. Follow Issue #61 order: Slice 38 digest graph/typed external schemas before Slice 39 dispatch.
3. Map work to P2-H01–P2-H11 and P2-I01–P2-I11.
4. Begin test-first with shared canonical JSON and domain-separated digest vectors, then exact request, dispatch, proposal, response, package, and disposition schemas.
5. Close P2-D11 through the exact-field/forbidden-content validator evidence.
6. If the accepted documents leave an exact field set contradictory or incomplete, stop and return to reviewed design work. Code must not choose a private interpretation.
7. Keep all original 152 Phase 1 tests unchanged and passing.
8. Do not use Codex until the complete Phase 2 implementation candidate is CI-green and ready for the single completion audit.

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
