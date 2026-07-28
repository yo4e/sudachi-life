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

Phase 2 must not reinterpret or change Phase 1 garden actions, selector, executor, evaluators, clocks, checkpoint rules, rollback transformation, writer categories, or protected tests without explicit project-owner authorization for one exact defect.

PR #73 temporarily reopened shared code only for explicitly authorized physical-limit defects and merged as `c9004027a94b709802af7f590d46de862dd93d7d`. Those physical boundaries are re-frozen. Pre-repair bodies remain in explicit `*_impl.py` modules.

Issue #117 explicitly authorized one narrow rollback-retention reconciliation repair after tests-only Slice 42b exposed a deterministic post-retention rollback defect. PR #116 merged the repair as `0059e0e20ececcf9e16a9b1a4376c3564cf9c391`. The pre-repair `rollback_transform_impl.py` remains byte-identical at blob `91f77ff91929f53be46dc9b74a3d1558ddd89b00`; the repaired public rollback boundary is re-frozen.

The pre-request-extension garden wake remains byte-identical in `lifecycle_impl.py`, blob `c971d77cc9beab22f5c50fb692b4f81210cbf3ed`.

## Accepted Phase 2 boundary

ADRs 0008–0016, Consultation Protocol v1, the ADR 0010–0016 matrix amendments, and the Phase 2 matrix form one accepted design package. Issue #61 owns implementation completion and the final implementation-audit gate.

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

Durable note: `docs/phase2/SLICE42A_FINITE_CYCLE_BOUNDARIES.md`.

### Slice 42b — rollback lineage epochs

PR #116 merged as `0059e0e20ececcf9e16a9b1a4376c3564cf9c391`.

Final exact PR head `7f9b718f8b65f71e411a5ed632257ed5609d3ede`, run 614: `365 passed in 46.13s` plus install, compile, protected enforcement, and schema-v1 CLI smoke.

It closes one full old-lineage epoch, one accepted public rollback, one full fresh-lineage epoch, exactly eight maximum charges across the physical organism, second-rollback rejection, zero fresh-lineage payload before ordinal one, immutable inactive old rows, nonblocking unresolved old work, pre-mutation stale-package rejection, old-proposal exclusion, event/export/authority reconstruction, rollback artifact preservation, and inherited physical limits.

Tests-only run 611 exposed the rollback-retention temporal-skew defect. Issue #117 authorized the exact wrapper repair; all 152 Phase 1 tests remain unchanged, and dedicated schema-v1 regression now protects rollback after checkpoint pruning and the next ordinary checkpoint.

Durable note: `docs/phase2/SLICE42B_ROLLBACK_LINEAGE.md`.

## Open gate

Issue #120 completed the single independent Phase 2 implementation audit at `44e363e874679537fef43d9f78e382ecf5dc5d3e` and found one high and three medium implementation defects. The conclusion was **not ready to freeze; specified repairs required**.

Issue #121 owns the accepted repairs. PR #119 now contains the repaired implementation and evidence:

- repair implementation head `6cc312a4e2ac64f866babe7cbab44aca8493b24d`;
- ordinary CI head `579e7098e66b679c5d69baa8290e452e4ab10db6`, run 636: `381 passed in 52.21s`;
- install, compile, protected enforcement, and schema-v1 CLI smoke passed;
- original 152 Phase 1 tests remain unchanged;
- durable note: `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`.

The repairs close the arbitrary caller-supplied fixture callable, terminalize caught fixture failure exactly once, admit and preserve canonical stable maintenance state during ingress/terminalization, and validate the exact stable checkpoint artifact before dispatch effects. They do not change ADR 0008–0016 or Protocol v1 meaning and add no live external capability.

Because the prior audit conclusion blocks the phase gate and the repairs touch capability, persistence, checkpoint, and terminalization boundaries, one focused read-only completion re-audit is required under `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`. PR #119 must remain unmerged and Issue #61/#121 must remain open until that conclusion is satisfactory.

## Exact restart point

1. Reconstruct from PR #119, Issue #120, Issue #121, and `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`.
2. Confirm the final exact re-audit candidate includes `6cc312a4e2ac64f866babe7cbab44aca8493b24d` and run 636 evidence, plus only documentation closeout changes after `579e7098e66b679c5d69baa8290e452e4ab10db6`.
3. Confirm all temporary repair scripts/workflows are absent and all original 152 Phase 1 tests are unchanged.
4. Request one focused read-only completion re-audit against the final exact PR #119 head.
5. Require the reviewer to independently inspect all four Issue #120 findings, affected cross-boundaries, the 213-ID evidence map, Phase 1 byte identity, schema-v1 support, physical accounting, authority, rollback, and explicit-absence surfaces.
6. Do not modify or merge the candidate while the re-audit is running.
7. If the conclusion is satisfactory, merge PR #119, close Issue #121 and Issue #61, update the final handoff, and freeze Phase 2.
8. Request human confirmation for any new finding that would change contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.

## End-of-work protocol

- update `docs/HANDOFF.md`
- update matrices and durable notes
- update relevant Issues and PRs
- report tests, CI, failures, and skipped checks honestly
- keep no critical decision only in chat
- preserve repository language policy

Repository prose, code, Issues, ADRs, and tests are English. Intentional Japanese README lines remain the standing exception.
