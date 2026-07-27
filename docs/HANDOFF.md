# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008–0013 are accepted. Issue #61 owns Phase 2 implementation. Slice 36, Slice 37a1–a3, Slice 38a–c, Slice 39a, Slice 40, and Slice 41 are merged.

No live caregiver, model API, human chat, network, subprocess, memory, skill generation, action adoption, or generic agent behavior is authorized.

## Cold start

Read, in order:

1. `AGENTS.md`
2. `docs/AI_COLLABORATION_OPERATIONS.md`
3. `docs/phase2/CLARIFICATION_DELEGATION.md`
4. `docs/MINIMAL_ORGANISM_CONTRACT.md`
5. accepted ADRs 0001–0013
6. `docs/PHASE1_TEST_MATRIX.md`
7. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
8. this handoff
9. `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
10. `docs/phase2/ADR0010_TEST_MATRIX_AMENDMENT.md`
11. `docs/phase2/ADR0011_TEST_MATRIX_AMENDMENT.md`
12. `docs/phase2/ADR0012_TEST_MATRIX_AMENDMENT.md`
13. `docs/phase2/ADR0013_TEST_MATRIX_AMENDMENT.md`
14. `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
15. implemented `docs/phase2/` notes
16. Issue #61 and current PRs/issues

Repository and GitHub state outrank conversation history.

## Thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

The final Phase 1 audit checked `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: all findings resolved and 152 tests passed. Those tests remain unchanged and are the schema-v1 control.

Do not change Phase 1 actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, writer categories, or protected tests for Phase 2 convenience.

PR #73 temporarily reopened shared code only for explicitly authorized physical-limit defects and merged as `c9004027a94b709802af7f590d46de862dd93d7d`. The repaired physical boundaries are re-frozen. Pre-repair bodies remain in explicit `*_impl.py` modules.

The garden wake before the schema-v2 request extension remains byte-identical in `lifecycle_impl.py`, blob `c971d77cc9beab22f5c50fb692b4f81210cbf3ed`.

## Accepted Phase 2 boundary

ADRs 0008–0013, Consultation Protocol v1, the ADR 0010–0013 matrix amendments, and the Phase 2 matrix form one accepted package.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are untrusted provenance only.

Original Phase 1 budget locations remain exactly `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Physical limits remain 8 MiB active/artifact, 40 MiB checkpoint store, 64 MiB working set, and 1 MiB next-wake reserve.

Consultation limits include 16 KiB request, 16 KiB package, 8 KiB provenance inside package, four requests/charged calls per lineage, one outstanding request, 64 KiB logical payload, and zero human/model/money/declared latency.

## Routine clarification delegation

The project owner explicitly authorizes routine recommended clarifications to be formally adopted without another human confirmation under `docs/phase2/CLARIFICATION_DELEGATION.md`.

This delegation applies only to the smallest deterministic closure of an implementation ambiguity inside already accepted scope. Every adoption still requires a focused Issue, normative ADR/document update, protected CI, and durable handoff record before implementation.

Human confirmation remains required for material changes to the research question, contract/ADR intent, frozen Phase 1, authority/security boundaries, live external capabilities, destructive migration, protected evidence, autonomy/resource scope, or unresolved contradictions between equally authoritative requirements.

## Implemented evidence

### Slice 36 — complete

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, exact zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and absolute physical limits. Final run 512: `230 passed in 32.41s`.

### Slice 37 — request boundary

- PR #81 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`; run 520: `236 passed in 33.52s`.
- PR #83 merged as `208956c40bffc0eff94307e6d326a071ee386d94`; run 533: `242 passed in 31.65s`.
- PR #85 merged as `82e17c6ccba65323315b399ea6fad345a52db5f4`; run 538: 245 tests passed.

### Slice 38 — exact protocol graph

- PR #87 merged as `16af01a84aae3d802a112228c85ec4b1849c19ee`; run 545: `261 passed in 34.10s`.
- PR #91 merged as `068b3d30b91bd0bec89344a0d27b4685b3764a65`; run 551: `275 passed in 29.84s`.
- PR #95 merged as `d5cbe115caaada4b71d58bb81527fb6179e0c913`; final run 559: `294 passed in 37.06s`.

### Accepted clarifications

- ADR 0010: PR #94, merge `b98bfdbd3de52e192f18328d6a294c8a683fa998`; Issues #88/#89/#92/#93 completed.
- ADR 0011: PR #98, merge `c392ee160a2a056e9fa450138c845ce1f2980fd3`; Issue #96 completed.
- ADR 0012: PR #102, merge `2721e472791d6221683ba62fdfc0a442fc1ea6c0`; Issue #101 completed.
- ADR 0013: PR #106, merge `62336bbed44ff32470936c3eedc11f276f491d11`; Issue #105 completed.

### Slice 39a — dispatch admission and deterministic fixture

PR #99 merged as `b7c434aed249ed0bc52160db66e594824186890e`.

Final exact PR head `64720b736fcab47b5ebfff26155ab17728f47b14`, run 569: `316 passed in 56.74s` plus installation, compilation, and schema-v1 genesis CLI smoke.

Durable note: `docs/phase2/SLICE39A_DISPATCH_ADMISSION_FIXTURE.md`.

### Slice 40 — exact ingress and terminalization

PR #103 merged as `f0238f108b2eb05a6774ca68a0b056eb12772dd1`.

Final exact PR head `e6221bb42ad5e94ddd4d0c2e576975d64693464c`, run 580: `338 passed in 73.21s` plus installation, compilation, and schema-v1 genesis CLI smoke.

Durable note: `docs/phase2/SLICE40_INGRESS_TERMINALIZATION.md`.

### Slice 41 — exact explicit disposition wake

PR #107 merged as `a1176a3afa55931b409696e8d5b50ab6992f129f`.

Final exact PR head `d6cb713aae5df2ed3e12740bbc474a89cbbb2df8`, run 593: `358 passed in 42.65s` plus installation, compilation, and schema-v1 genesis CLI smoke.

It implements:

- exact current-state and disposition preimages, IDs, final envelope, authority, and parents;
- all six disposition/reason branches;
- oldest eligible current-lineage proposal selection and immutable finality;
- exact four-event organism transaction, five-field outcome, and fixed ledger;
- lifecycle increment while preserving garden failure streak, input, environment, inventory, and plots;
- ordinary checkpoint publication and existing pending registration repair;
- precommit rollback and restored proposal eligibility;
- same-process and spawned fail-fast ownership without queueing;
- real active/reserve, checkpoint-store, and working-set refusal;
- no fixture, action execution, network, subprocess, memory, or skill effect.

Durable note: `docs/phase2/SLICE41_DISPOSITION_WAKE.md`.

## Remaining boundaries

- Exact four-request/four-charge and mixed 64 KiB boundaries require legitimate repeated terminal/disposition cycles.
- The largest structural request must be produced by legal protocol-v1 state, not filler.
- Rollback must prove the fresh current-lineage epoch and fail-closed old-lineage packages/proposals.
- Complete event ancestry, export, authority, physical, and explicit-absence closure remains before the implementation audit.
- Do not create private rows or manufacture ordinals, charges, dispositions, lineage, or payload size.

## Exact restart

1. Audit every remaining unchecked Phase 2 matrix row against merged Slices 36–41.
2. Begin Slice 42 test-first using only legitimate repeated request→dispatch→ingress/terminal→disposition cycles and the accepted rollback path.
3. Close the fourth request/charge success, fifth refusal, largest structural request, mixed 64 KiB boundary/one-over, new-lineage reset, old-lineage rejection, complete event reconstruction, and remaining physical/absence evidence.
4. Do not modify frozen Phase 1 semantics or manufacture canonical state.
5. Keep all 152 Phase 1 tests unchanged and passing.
6. Use routine clarification delegation only within its documented limits; request human confirmation for material boundary changes.
7. Do not use Codex until every accepted Phase 2 requirement has protected evidence and one exact CI-green completion candidate is ready.