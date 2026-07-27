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
18. Issue #61, Issues #88/#89, and current PRs
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

## Accepted Phase 2 boundary

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

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and absolute limits.

Final Slice 36 head `e1ef85e71ddefef06c9940145e6d27db0c22d39b`, run 512: `230 passed in 32.41s` plus install, compile, and schema-v1 CLI smoke.

Read `docs/phase2/SLICE36*.md`. Issues #74–#79 are closed.

### Slice 37 — request boundary implemented so far

- PR #81 / Slice 37a1 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`; run 520: `236 passed in 33.52s`.
- PR #83 / Slice 37a2 merged as `208956c40bffc0eff94307e6d326a071ee386d94`; run 533: `242 passed in 31.65s`.
- PR #85 / Slice 37a3 merged as `82e17c6ccba65323315b399ea6fad345a52db5f4`; run 538: 245 tests passed.

These slices implement exact request creation, storage-safe optional rollback, real physical accounting, backward-wall-time independence, and nested/competing wake fail-fast evidence.

Read:

- `docs/phase2/SLICE37A1_REQUEST_WAKE_CORE.md`
- `docs/phase2/SLICE37A2_REQUEST_STORAGE_SAFETY.md`
- `docs/phase2/SLICE37A3_REQUEST_TIME_CONCURRENCY.md`

### Slice 38a — merged

PR #87 merged as `16af01a84aae3d802a112228c85ec4b1849c19ee`.

Final PR head `a571b769834fa223ed4afc5ef1d84e41cdbbee9a`, run 546 passed all steps. Code/test head `a3637c723da9696ebe618ed6d2ca5e7f3f467da9`, run 545: `261 passed in 34.10s`.

It closes P2-H01, the core of P2-H02, P2-H03, and request-side P2-D11. Shared `phase2_protocol.py` defines canonical bytes, exact digest labels, request identity/ID, and final request validation.

The prior request constructor remains byte-identical in `phase2_request_impl.py`, blob `46881e023d990f5c7ce393cac7060958419383c0`. Public validation occurs immediately before event write inside the request savepoint.

Durable note: `docs/phase2/SLICE38A_CANONICAL_DIGEST_REQUEST_SCHEMA.md`.

## Open requirements and design clarifications

- P2-D07/D08 require later terminalization/disposition cycles; do not bypass the frozen maintenance threshold with private state mutation.
- P2-E10 needs an exact reviewed maximum request-envelope interpretation; do not invent optional context fields.
- Issue #88 blocks P2-H04 and Slice 39 dispatch identity: protocol section 3.2 omits `configuration_version` from its exact list while section 4.1 requires it.
- Issue #89 blocks P2-I01 and P2-H07–H09: exact external-provenance fields are not enumerated.
- P2-H10 needs the versioned protected current-state projection before disposition identity code.

## Exact restart point

1. Continue Slice 38 with proposal identity and type-specific proposal validators only.
2. Map work to P2-H05/H06 and P2-I02–P2-I09.
3. Use `phase2_protocol.py`; do not duplicate canonical or digest logic.
4. Reject extra/missing fields, free text, unknown action, invalid parameters, wrong evaluator set, expiry mismatch, and any authority/cost/budget/permission/execution command.
5. Do not construct dispatch identity, response provenance/package, or disposition identity until the relevant design clarification is accepted.
6. Keep all 152 Phase 1 tests unchanged and passing.
7. Do not use Codex until the complete Phase 2 implementation candidate is CI-green and ready for the single completion audit.

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
