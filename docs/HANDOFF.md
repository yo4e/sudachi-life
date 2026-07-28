# SUDACHI Handoff

Updated: **2026-07-28**

Phase 1 is frozen. ADRs 0008–0016 are accepted. Issue #61 owns Phase 2 implementation completion and the final implementation-audit gate. Slice 36, Slice 37a1–a3, Slice 38a–c, Slice 39a, Slice 40, Slice 41, Slice 42a, and Slice 42b are merged.

No live caregiver, model API, human chat, network, subprocess, memory, skill generation, action adoption, or generic agent behavior is authorized.

## Cold start

Read, in order:

1. `AGENTS.md`
2. `docs/AI_COLLABORATION_OPERATIONS.md`
3. `docs/phase2/CLARIFICATION_DELEGATION.md`
4. `docs/MINIMAL_ORGANISM_CONTRACT.md`
5. accepted ADRs 0001–0016
6. `docs/PHASE1_TEST_MATRIX.md`
7. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
8. this handoff
9. `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
10. ADR 0010–0016 matrix amendments
11. `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
12. implemented `docs/phase2/` notes
13. Issue #61 and current PRs/issues

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

Do not change Phase 1 actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, writer categories, or protected tests for Phase 2 convenience. Any exact frozen-boundary defect requires explicit project-owner authorization before repair.

PR #73 temporarily reopened shared code only for explicitly authorized physical-limit defects and merged as `c9004027a94b709802af7f590d46de862dd93d7d`. The repaired physical boundaries are re-frozen. Pre-repair bodies remain in explicit `*_impl.py` modules.

Issue #117 explicitly authorized one narrow rollback-retention reconciliation repair after tests-only Slice 42b exposed a deterministic post-retention rollback defect. PR #116 merged the repair as `0059e0e20ececcf9e16a9b1a4376c3564cf9c391`. The pre-repair `rollback_transform_impl.py` remains byte-identical at blob `91f77ff91929f53be46dc9b74a3d1558ddd89b00`; the repaired public rollback boundary is re-frozen.

The garden wake before the schema-v2 request extension remains byte-identical in `lifecycle_impl.py`, blob `c971d77cc9beab22f5c50fb692b4f81210cbf3ed`.

## Accepted Phase 2 boundary

ADRs 0008–0016, Consultation Protocol v1, the ADR 0010–0016 matrix amendments, and the Phase 2 matrix form one accepted package.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are untrusted provenance only.

Original Phase 1 budget locations remain exactly `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Physical limits remain 8 MiB active/artifact, 40 MiB checkpoint store, 64 MiB working set, and 1 MiB next-wake reserve.

Consultation limits include 16 KiB request, 16 KiB package, 8 KiB provenance inside package, four requests/charged calls per lineage, one outstanding request, 64 KiB logical payload, and zero human/model/money/declared latency.

## Routine clarification delegation

The project owner authorizes routine recommended clarifications to be formally adopted without separate confirmation under `docs/phase2/CLARIFICATION_DELEGATION.md`.

Every delegated adoption still requires a focused Issue, normative ADR/document change, protected CI, and durable handoff. Material changes to research purpose, contract/ADR intent, frozen Phase 1, authority/security, live external capabilities, destructive migration, protected evidence, autonomy/resources, or unresolved normative contradictions require explicit human confirmation.

## Implemented evidence

### Slice 36

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and absolute physical limits. Final run 512: `230 passed in 32.41s`.

### Slice 37

- PR #81: request wake core, run 520 `236 passed in 33.52s`.
- PR #83: storage-safe request extension, run 533 `242 passed in 31.65s`.
- PR #85: wall-time and concurrency evidence, run 538 245 tests passed.

### Slice 38

- PR #87: exact digest/request schema, run 545 `261 passed in 34.10s`.
- PR #91: exact proposal schema, run 551 `275 passed in 29.84s`.
- PR #95: exact dispatch/response/package graph, run 559 `294 passed in 37.06s`.

### Accepted clarifications

- ADR 0010: PR #94, merge `b98bfdbd3de52e192f18328d6a294c8a683fa998`; Issues #88/#89/#92/#93 closed.
- ADR 0011: PR #98, merge `c392ee160a2a056e9fa450138c845ce1f2980fd3`; Issue #96 closed.
- ADR 0012: PR #102, merge `2721e472791d6221683ba62fdfc0a442fc1ea6c0`; Issue #101 closed.
- ADR 0013: PR #106, merge `62336bbed44ff32470936c3eedc11f276f491d11`; Issue #105 closed.
- ADR 0014: PR #110, merge `b5d1ae3ae9ed46855f285c8539e4c2ed7891dbc3`; Issue #109 closed. The legal largest request has exactly eight eligible parent events.
- ADRs 0015 and 0016: PR #113, merge `fc194cba5f90d0c0c1f81907646f4e661dc80bc7`; Issues #111/#112 closed. They fix the exact fifth-request refusal and the pure 64 KiB/one-over evidence plus legal four-cycle maximum.

### Slice 39

PR #99 merged as `b7c434aed249ed0bc52160db66e594824186890e`. Final head `64720b736fcab47b5ebfff26155ab17728f47b14`, run 569: `316 passed in 56.74s` plus install, compile, and schema-v1 smoke.

### Slice 40

PR #103 merged as `f0238f108b2eb05a6774ca68a0b056eb12772dd1`. Final head `e6221bb42ad5e94ddd4d0c2e576975d64693464c`, run 580: `338 passed in 73.21s` plus install, compile, and schema-v1 smoke.

### Slice 41

PR #107 merged as `a1176a3afa55931b409696e8d5b50ab6992f129f`. Final head `d6cb713aae5df2ed3e12740bbc474a89cbbb2df8`, run 593: `358 passed in 42.65s` plus install, compile, and schema-v1 smoke.

It implements exact disposition identity/envelope/mapping, oldest proposal selection, four-event organism transaction, fixed ledger, lifecycle/failure/input/garden invariants, checkpoint publication/repair, rollback-before-commit, finality, concurrency, physical refusal, and capability absence.

### Slice 42a

PR #114 merged as `716834b9bd3200989db2d078fb8c108b499a09b9`.

Final exact PR head `1cbfbb8dd0e649d0e83570ffd9c05baecff39619`, run 607: `360 passed in 115.98s` plus install, compile, and schema-v1 smoke.

It implements legitimate request ordinals one through four, the exact fifth-request refusal, four conservative charges, the ADR 0014 eight-parent largest request, the pure 65536/65537 payload guard, the legal four-cycle maximum, ordinary checkpoint and physical-limit evidence, retained implementation-body proof, and no private canonical mutation.

Durable note: `docs/phase2/SLICE42A_FINITE_CYCLE_BOUNDARIES.md`.

### Slice 42b

PR #116 merged as `0059e0e20ececcf9e16a9b1a4376c3564cf9c391`.

Final exact PR head `7f9b718f8b65f71e411a5ed632257ed5609d3ede`, run 614: `365 passed in 46.13s` plus install, compile, protected enforcement, and schema-v1 CLI smoke.

It implements and protects:

- one complete four-request/four-charge old-lineage epoch;
- one accepted public rollback and one complete fresh-lineage epoch;
- exactly eight maximum charged fixture invocations across one physical organism;
- rejection of a second completed rollback under ADR 0007;
- fresh request ordinal one and zero fresh-lineage logical bytes before its first request;
- immutable inactive old-lineage rows;
- old unresolved work not blocking current work;
- pre-mutation late old-package rejection and old-proposal exclusion;
- consultation rows, event export, parent/authority, archive/source/transformed-candidate/completion, and physical-limit reconstruction across rollback;
- schema-v1 rollback after retention and the next ordinary checkpoint.

Tests-only run 611 exposed the rollback-retention temporal-skew defect. Issue #117 authorized the exact wrapper repair; all original 152 Phase 1 tests remain unchanged.

Durable note: `docs/phase2/SLICE42B_ROLLBACK_LINEAGE.md`.

## Implementation-completion gate

No additional Consultation Boundary behavior is authorized or required before the implementation-completion audit.

The remaining work is evidence closure and independent review:

- map every accepted P2-A through P2-P matrix row to exact protected implementation evidence;
- verify all 152 Phase 1 tests remain byte-unchanged and included;
- verify schema-v1 support, zero-caregiver behavior, deterministic-fixture behavior, and explicit-absence surfaces at one exact candidate head;
- assemble accepted ADRs, implementation notes, completed matrix mapping, CI evidence, and current Issues;
- run the single independent read-only Phase 2 implementation audit required by `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`;
- repair only accepted findings and freeze Phase 2 only after a satisfactory completion conclusion.

## Exact restart

1. Merge the Slice 42b closeout PR, then reconstruct from updated `main`.
2. Treat merge `0059e0e20ececcf9e16a9b1a4376c3564cf9c391` and exact head run 614 as the merged implementation baseline, subject only to closeout documentation commits.
3. Build a complete P2-A–P2-P implementation-evidence map without weakening or reinterpreting any accepted row.
4. Confirm the original 152 Phase 1 tests are byte-unchanged and included in the exact green candidate.
5. Confirm no live caregiver/API/human chat, network, subprocess, memory, skill, action-adoption, arbitrary-code, or continuous-execution surface exists.
6. Request one read-only independent Phase 2 implementation audit against one exact candidate commit; do not use per-slice or iterative audit calls.
7. Record findings with severity, exact invariant, file/symbol evidence, matrix coverage, and recommended disposition.
8. Repair accepted findings through ordinary protected work and repeat the audit only if the policy's gate-level conditions require it.
9. Close Issue #61 and freeze Phase 2 only after all completion-gate checkboxes and the independent audit conclusion are satisfied.
10. Request human confirmation for any finding that would change contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.
