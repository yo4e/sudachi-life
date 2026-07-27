# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008–0012 are accepted. Issue #61 owns Phase 2 implementation. Slice 36, Slice 37a1–a3, Slice 38a–c, and Slice 39a are merged.

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

These close the request/dispatch/proposal/response/package identity graph and exact proposal/provenance/package schemas.

### Accepted clarifications

- ADR 0010: PR #94, merge `b98bfdbd3de52e192f18328d6a294c8a683fa998`; Issues #88/#89/#92/#93 completed.
- ADR 0011: PR #98, merge `c392ee160a2a056e9fa450138c845ce1f2980fd3`; Issue #96 completed.
- ADR 0012: project-owner acceptance of Issue #101 fixes typed receipt/completion/terminal IDs, success-ingress event and receipt evidence, rejected raw-byte digest, terminal event/envelope, direct parents, measured-byte rules, and branch atomicity/idempotence. Documentation merge remains the adoption closeout gate.

### Slice 39a — dispatch admission and deterministic fixture

PR #99 merged as `b7c434aed249ed0bc52160db66e594824186890e`.

Final exact PR head `64720b736fcab47b5ebfff26155ab17728f47b14`, run 569: `316 passed in 56.74s` plus installation, compilation, and schema-v1 genesis CLI smoke.

It implements:

- fresh fail-fast administrative ownership;
- sleeping/stable/current-lineage/lifecycle-expiry admission;
- one exact atomic ADR 0011 event/dispatch/charge write set;
- conservative precharge and request-byte equality;
- commit and lock release before fixture execution;
- byte-identical idempotent reentry without clock, charge, event, or fixture retry;
- ordinary success and real reserve-refusal physical evidence;
- capability-minimal deterministic fixture bytes;
- no checkpoint, lifecycle, garden, action, response, proposal, receipt, terminal, or disposition effect.

Durable note: `docs/phase2/SLICE39A_DISPATCH_ADMISSION_FIXTURE.md`.

## Remaining boundaries

- P2-F06 still needs spawned process-crash evidence; fixture exception/interruption already retains the conservative charge.
- P2-F08 and request P2-D07/D08/E10 require legitimate terminalization/disposition cycles. Do not create private rows or manufacture ordinals/charges.
- Fixture output remains noncanonical until Slice 40.

## Exact restart

1. Merge the ADR 0012 documentation PR and close Issue #101.
2. Begin Slice 40 test-first against the applicable P2-J/K/N/O requirements and ADR 0012 amendment.
3. Check raw package size before parsing and accept only byte equality with independently reconstructed canonical package bytes.
4. Successful ingress atomically writes response, optional proposal, receipt, cost completion, and one `consultation_response_ingressed` event.
5. Invalid, expired, or interrupted admitted work atomically writes terminal, cost completion, and one `consultation_dispatch_terminalized` event.
6. Preserve exact typed aliases, two direct parents, reason-specific rejected-byte fields, measured sizes, duplicate idempotence, and same-byte resubmission after busy/pending-only rejection.
7. Reconciliation may create only `dispatch_interrupted`; no ingress, terminal, duplicate, or reconciliation path invokes the fixture.
8. Do not checkpoint, increment lifecycle, clear maintenance, execute an action, create memory/skills, retry, or refund.
9. Keep all 152 Phase 1 tests unchanged and passing.
10. Do not use Codex until every accepted Phase 2 requirement has protected evidence and one exact CI-green completion candidate is ready.
