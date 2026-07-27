# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008–0012 are accepted. Issue #61 owns Phase 2 implementation. Slice 36, Slice 37a1–a3, Slice 38a–c, Slice 39a, and Slice 40 are merged.

No live caregiver, model API, human chat, network, subprocess, memory, skill generation, action adoption, or generic agent behavior is authorized.

## Cold start

Read, in order:

1. `AGENTS.md`
2. `docs/AI_COLLABORATION_OPERATIONS.md`
3. `docs/MINIMAL_ORGANISM_CONTRACT.md`
4. accepted ADRs 0001–0012
5. `docs/PHASE1_TEST_MATRIX.md`
6. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
7. this handoff
8. `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
9. `docs/phase2/ADR0010_TEST_MATRIX_AMENDMENT.md`
10. `docs/phase2/ADR0011_TEST_MATRIX_AMENDMENT.md`
11. `docs/phase2/ADR0012_TEST_MATRIX_AMENDMENT.md`
12. `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
13. implemented `docs/phase2/` notes
14. Issue #61 and current PRs/issues

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

ADRs 0008–0012, Consultation Protocol v1, the ADR 0010–0012 matrix amendments, and the Phase 2 matrix form one accepted package.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are untrusted provenance only.

Original Phase 1 budget locations remain exactly `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Physical limits remain 8 MiB active/artifact, 40 MiB checkpoint store, 64 MiB working set, and 1 MiB next-wake reserve.

Consultation limits include 16 KiB request, 16 KiB package, 8 KiB provenance inside package, four requests/charged calls per lineage, one outstanding request, 64 KiB logical payload, and zero human/model/money/declared latency.

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

### Slice 39a — dispatch admission and deterministic fixture

PR #99 merged as `b7c434aed249ed0bc52160db66e594824186890e`.

Final exact PR head `64720b736fcab47b5ebfff26155ab17728f47b14`, run 569: `316 passed in 56.74s` plus installation, compilation, and schema-v1 genesis CLI smoke.

It implements exact admission, conservative precharge, no-retry idempotence, commit-before-fixture lock release, real reserve refusal, and a capability-minimal deterministic fixture.

Durable note: `docs/phase2/SLICE39A_DISPATCH_ADMISSION_FIXTURE.md`.

### Slice 40 — exact ingress and terminalization

PR #103 merged as `f0238f108b2eb05a6774ca68a0b056eb12772dd1`.

Final exact PR head `e6221bb42ad5e94ddd4d0c2e576975d64693464c`, run 580: `338 passed in 73.21s` plus installation, compilation, and schema-v1 genesis CLI smoke.

It implements:

- raw-size-before-parse and exact canonical package acceptance;
- atomic response/optional proposal/receipt/completion/event ingress;
- exact `unavailable` zero-proposal final state;
- exact invalid, expired, and interrupted terminal branches;
- success/terminal duplicate idempotence and conflict rejection;
- busy rejection and explicit same-byte resubmission;
- logical payload accounting without metadata double count;
- real active/reserve refusal;
- spawned process exit after admission, retained charge, and explicit interruption reconciliation without fixture recall;
- no checkpoint, lifecycle, garden, action, maintenance, retry, refund, memory, or skill effect.

Durable note: `docs/phase2/SLICE40_INGRESS_TERMINALIZATION.md`.

## Remaining boundaries

- Exact four-request/four-charge and mixed 64 KiB boundaries require legitimate repeated disposition/terminal cycles.
- Rollback must prove new-lineage epoch reset and old-lineage late-package rejection.
- Maximum-envelope and complete request→dispatch→response→proposal→receipt→disposition reconstruction require the explicit disposition wake.
- Do not create private canonical rows or manufacture ordinals, charges, lineage, or disposition state.

## Exact restart

1. Audit the accepted disposition specification before implementation:
   - disposition ID digest preimage;
   - exact envelope and current-state reference;
   - exact protected reason-code set;
   - event type, source, payload, direct parents, and outcome shape;
   - lifecycle/checkpoint atomic ordering and failure behavior.
2. If any immutable value is missing, open one focused design-clarification Issue and stop before code.
3. Otherwise implement the separate caller-selected disposition wake test-first against P2-L01–L14 and applicable M/N/O requirements.
4. Consider at most one proposal, use current state over fixture assumptions, increment lifecycle, preserve garden failure streak, and checkpoint.
5. Never claim garden input, execute an action, create memory/skills, retry consultation, or expand authority.
6. Keep all 152 Phase 1 tests unchanged and passing.
7. Do not use Codex until every accepted Phase 2 requirement has protected evidence and one exact CI-green completion candidate is ready.
