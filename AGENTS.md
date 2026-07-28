# AGENTS.md

This file is the continuity contract for AI collaborators working on SUDACHI.

## Cold-start rule

Assume you remember nothing about SUDACHI. Reconstruct the project from repository and current GitHub state before proposing or changing anything. Repository and GitHub state outrank conversation history.

## Read order

1. `README.md`
2. `docs/CHATGPT_PROJECT_HANDOFF.md`
3. `docs/AI_COLLABORATION_OPERATIONS.md`
4. `docs/phase2/CLARIFICATION_DELEGATION.md`
5. `docs/ORIGIN.md`
6. `docs/MINIMAL_ORGANISM_CONTRACT.md`
7. accepted `docs/decisions/` files in numeric order, including ADRs 0010–0016
8. `docs/ARCHITECTURE.md`
9. `docs/ROADMAP.md`
10. `docs/IMPLEMENTATION_DISCIPLINE.md`
11. `docs/PHASE1_TEST_MATRIX.md`
12. implemented `docs/phase1/` notes
13. implemented `docs/phase2/` notes
14. `docs/RESEARCH_QUESTIONS.md`
15. `docs/PARENT_MODEL_PROVIDER_REVIEW.md`
16. preliminary `docs/research/` notes
17. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
18. `docs/HANDOFF.md`
19. Issue #61 and current Issues/PRs
20. Consultation Protocol v1, ADR 0010–0016 matrix amendments, the Phase 2 matrix, and Issue #59/#63 audit reports

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

ADRs 0008–0016, Consultation Protocol v1, the ADR 0010–0016 matrix amendments, and the Phase 2 matrix form one accepted design package. Issue #61 owns implementation.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are untrusted provenance only.

Original Phase 1 budget locations remain exactly `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Operational boundaries remain explicit:

1. Garden request wake preserves the frozen Phase 1 outcome and uses only an optional storage-safe request extension.
2. Administrative dispatch commits one dispatch, one conservative charge, and one admission event before fixture execution and releases SQLite ownership first.
3. The deterministic fixture receives only the final request envelope and declared case, with no runtime authority handles.
4. Administrative ingress or terminalization validates exact typed bytes and never automatically retries fixture work.
5. Explicit disposition considers at most one proposal, increments lifecycle, preserves the garden failure streak, checkpoints, and does not execute an action or create memory/skills.

Proposal types: `action_candidate`, `abstain`, `defer`.

Dispositions: `accepted`, `rejected`, `deferred`, `clarification_requested`.

Clarification rounds: zero.

## Routine clarification delegation

The project owner authorizes routine recommended clarifications to be formally adopted without a separate chat confirmation only under the exact limits in `docs/phase2/CLARIFICATION_DELEGATION.md`.

A delegated clarification must be the smallest deterministic closure of an ambiguity inside already accepted scope, must be documented in a focused Issue and reviewed ADR/documentation PR, and must pass protected CI before becoming canonical.

Human confirmation remains required for changes to the research question, contract or ADR intent, frozen Phase 1, authority/security boundaries, live external capabilities, destructive migration, protected evidence, material autonomy/resource scope, or an unresolved contradiction between equally authoritative requirements.

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

## Implemented state

### Slice 36 — complete

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and absolute physical limits. Final run 512: `230 passed in 32.41s`.

### Slice 37 — request boundary

- PR #81 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`; run 520: `236 passed in 33.52s`.
- PR #83 merged as `208956c40bffc0eff94307e6d326a071ee386d94`; run 533: `242 passed in 31.65s`.
- PR #85 merged as `82e17c6ccba65323315b399ea6fad345a52db5f4`; run 538: 245 tests passed.

### Slice 38 — exact protocol graph

- PR #87 merged as `16af01a84aae3d802a112228c85ec4b1849c19ee`; run 545: `261 passed in 34.10s`.
- PR #91 merged as `068b3d30b91bd0bec89344a0d27b4685b3764a65`; run 551: `275 passed in 29.84s`.
- PR #95 merged as `d5cbe115caaada4b71d58bb81527fb6179e0c913`; final run 559: `294 passed in 37.06s`.

The prior request constructor remains byte-identical in `phase2_request_impl.py`, blob `46881e023d990f5c7ce393cac7060958419383c0`.

### Accepted clarifications

- ADR 0010: PR #94, merge `b98bfdbd3de52e192f18328d6a294c8a683fa998`; Issues #88/#89/#92/#93 closed.
- ADR 0011: PR #98, merge `c392ee160a2a056e9fa450138c845ce1f2980fd3`; Issue #96 closed.
- ADR 0012: PR #102, merge `2721e472791d6221683ba62fdfc0a442fc1ea6c0`; Issue #101 closed.
- ADR 0013: PR #106, merge `62336bbed44ff32470936c3eedc11f276f491d11`; Issue #105 closed.
- ADR 0014: PR #110, merge `b5d1ae3ae9ed46855f285c8539e4c2ed7891dbc3`; Issue #109 closed. It fixes P2-E10 to the exact eight-parent eligible request path.
- ADRs 0015 and 0016: PR #113, merge `fc194cba5f90d0c0c1f81907646f4e661dc80bc7`; Issues #111/#112 closed. They fix the exact fifth-request refusal and separate the pure 64 KiB/one-over guard from the legal closed-v1 maximum.

### Slice 39a — dispatch admission and fixture boundary

PR #99 merged as `b7c434aed249ed0bc52160db66e594824186890e`.

Final exact PR head `64720b736fcab47b5ebfff26155ab17728f47b14`, run 569: `316 passed in 56.74s` plus install, compile, and schema-v1 CLI smoke.

Durable note: `docs/phase2/SLICE39A_DISPATCH_ADMISSION_FIXTURE.md`.

### Slice 40 — package ingress and terminalization

PR #103 merged as `f0238f108b2eb05a6774ca68a0b056eb12772dd1`.

Final exact PR head `e6221bb42ad5e94ddd4d0c2e576975d64693464c`, run 580: `338 passed in 73.21s` plus install, compile, and schema-v1 CLI smoke.

Durable note: `docs/phase2/SLICE40_INGRESS_TERMINALIZATION.md`.

### Slice 41 — explicit disposition wake

PR #107 merged as `a1176a3afa55931b409696e8d5b50ab6992f129f`.

Final exact PR head `d6cb713aae5df2ed3e12740bbc474a89cbbb2df8`, run 593: `358 passed in 42.65s` plus install, compile, and schema-v1 CLI smoke.

It implements exact current-state/disposition identities and envelope, all six protected outcomes, oldest eligible proposal selection, the exact four-event organism transaction and fixed ledger, lifecycle increment with failure-streak/garden/input invariants, ordinary checkpoint publication and repair, precommit rollback, finality, same-process/spawned fail-fast ownership, and real active/reserve/checkpoint-store/working-set refusal.

Durable note: `docs/phase2/SLICE41_DISPOSITION_WAKE.md`.

### Slice 42a — finite consultation cycle boundaries

PR #114 merged as `716834b9bd3200989db2d078fb8c108b499a09b9`.

Final exact PR head `1cbfbb8dd0e649d0e83570ffd9c05baecff39619`, run 607: `360 passed in 115.98s` plus install, compile, and schema-v1 CLI smoke.

It closes legitimate request ordinals one through four, the exact noncanonical fifth refusal, four conservative charges with no fifth invocation, the ADR 0014 eight-parent largest structural request, the pure 65536/65537 accounting guard, the measured legal closed-v1 payload maximum, ordinary checkpoint and physical-limit evidence, and no-private-mutation proof.

The pre-ADR 0016 ingress runtime and retained request constructor remain byte-identical in their explicit `*_impl.py` modules.

Durable note: `docs/phase2/SLICE42A_FINITE_CYCLE_BOUNDARIES.md`.

## Open boundaries

- P2-J10 and P2-M08–P2-M11 require one accepted rollback through the public path, a fresh request/charge/logical-payload epoch, and historical inactive old-lineage rows.
- Old-lineage unresolved work must not block current-lineage work, and late old-lineage packages/proposals must fail before mutation.
- P2-M10 and ADR 0007 require the full two-lineage maximum of eight charged invocations and rejection of a second completed rollback.
- Complete event export, authority/ancestry reconstruction, rollback artifact preservation, physical accounting, and remaining explicit-absence review remain before the implementation-completion audit.

## Exact restart point

1. Merge the Slice 42a closeout PR, then begin Slice 42b test-first from updated `main`.
2. Build legitimate pre-rollback consultation history only through public request, dispatch, ingress/terminalization, disposition, ordinary wake, checkpoint, and maintenance operations.
3. Invoke the accepted public rollback path once; do not alter the frozen rollback transformation or manufacture lineage state.
4. Prove the new current lineage starts with request ordinal one, zero current-lineage logical bytes before its first request, and a fresh four-request/four-charge epoch while all old rows remain immutable historical evidence.
5. Prove old-lineage unresolved work does not block current work, late old-lineage packages fail before mutation, and old-lineage proposals are excluded from disposition selection.
6. Prove at most eight charged invocations across the two allowed epochs, preserve rollback archive/source/transformed-candidate/completion evidence, and reject a second completed rollback under ADR 0007.
7. Reconstruct consultation rows, events, parents, authority, checkpoint/rollback artifacts, and physical totals across both lineages without private canonical mutation.
8. Keep all 152 Phase 1 tests unchanged and passing.
9. Use routine clarification delegation only within its documented limits; request human confirmation for material boundary changes.
10. Do not use Codex until every accepted Phase 2 requirement has protected evidence and one exact CI-green completion candidate is ready.

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
