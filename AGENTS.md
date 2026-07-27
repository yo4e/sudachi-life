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
6. accepted `docs/decisions/` files in numeric order, including ADRs 0010–0012
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
18. Issue #61 and current Issues/PRs
19. Consultation Protocol v1, ADR 0010–0012 matrix amendments, the Phase 2 matrix, and Issue #59/#63 audit reports

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

ADRs 0008–0012, Consultation Protocol v1, the ADR 0010–0012 matrix amendments, and the Phase 2 matrix form one accepted design package. Issue #61 owns implementation.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are untrusted provenance only.

Original Phase 1 budget locations remain exactly `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Operational boundaries remain explicit:

1. Garden request wake preserves the frozen Phase 1 outcome and uses only an optional storage-safe request extension.
2. Administrative dispatch commits one dispatch, one conservative charge, and one admission event before fixture execution and releases SQLite ownership first.
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

### Slice 39a — dispatch admission and fixture boundary

PR #99 merged as `b7c434aed249ed0bc52160db66e594824186890e`.

Final exact PR head `64720b736fcab47b5ebfff26155ab17728f47b14`, run 569: `316 passed in 56.74s` plus install, compile, and schema-v1 CLI smoke.

It implements fresh fail-fast administrative admission, exact stable/current-lineage/expiry checks, atomic ADR 0011 event/dispatch/charge, conservative precharge, idempotent no-retry reentry, real reserve refusal, commit-before-fixture lock release, and a capability-minimal deterministic fixture.

Durable note: `docs/phase2/SLICE39A_DISPATCH_ADMISSION_FIXTURE.md`.

### Slice 40 — package ingress and terminalization

PR #103 merged as `f0238f108b2eb05a6774ca68a0b056eb12772dd1`.

Final exact PR head `e6221bb42ad5e94ddd4d0c2e576975d64693464c`, run 580: `338 passed in 73.21s` plus install, compile, and schema-v1 CLI smoke.

It implements exact raw-size-before-parse and canonical package acceptance; atomic response/optional proposal/receipt/completion/event ingress; exact invalid/expired/interrupted terminal branches; duplicate idempotence; busy resubmission; logical payload accounting; real reserve refusal; and spawned process-crash reconciliation without fixture recall.

Durable note: `docs/phase2/SLICE40_INGRESS_TERMINALIZATION.md`.

## Open boundaries

- P2-D07/D08, P2-E10, P2-F08, exact mixed 64 KiB boundaries, and lineage reset require legitimate repeated disposition/rollback cycles. Do not manufacture ordinals, charges, or lineage state through private canonical mutation.
- The next implementation slice is the explicit disposition wake, but every immutable disposition identity, event type, payload, outcome shape, reason-code set, and checkpoint linkage must be audited against accepted documents before code is written.

## Exact restart point

1. Audit Consultation Protocol v1, ADR 0010 disposition clarification, schema, and matrix for every exact disposition/outcome/event identity.
2. If any immutable value is under-specified, open one focused design-clarification Issue and stop before implementation.
3. Otherwise implement the separate caller-selected disposition wake test-first against P2-L01–L14 and applicable M/N/O requirements.
4. Preserve current state over fixture assumptions, consider at most one proposal, increment lifecycle, preserve the garden failure streak, and create a checkpoint.
5. Never claim garden input, execute an action, create memory/skills, retry consultation, or expand authority.
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
