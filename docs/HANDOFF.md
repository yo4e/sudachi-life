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

## Implementation-completion audits and repairs

Issue #120 audited exact candidate `44e363e874679537fef43d9f78e382ecf5dc5d3e` and concluded **not ready to freeze; specified repairs required**. Issue #121 accepted four repairs without changing the accepted contract.

Issue #122 audited `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`, independently confirmed Findings 1–3 closed, and found the remaining Finding 4 checkpoint-linkage defect. Issue #123 repaired exact manifest fields, active organism binding, complete request-row equality, and complete active/snapshot request-event row equality in the Phase 2 dispatch boundary only.

Issue #124 began the final closure audit at `b0ac020dee450238b4267b76eb59addef036618c`. Its interim record confirmed the earlier Finding 4 reproductions closed, Findings 1–3 still closed, the 47 original Phase 1 blobs byte-identical, the independent Phase 1 control at 152 passed, the full candidate at 385 passed, exactly 213 accepted/evidence-map IDs, schema-v1 support, and explicit capability absence.

The interim audit found one medium semantic-linkage gap: coherent mutations to both the active and checkpoint `consultation_request_created` event could pass because the two rows were compared to each other without reconstructing the accepted event from the validated request.

Issue #125 owns the narrow repair. Before any dispatch clock read or mutation, the Phase 2 boundary now reconstructs and checks the exact event sequence, organism, lineage, lifecycle, type, source, canonical request payload/size, schema, environment, and budget semantics against both active and checkpoint rows, then retains complete row equality including wall time.

Protected coherent mutations cover payload, source, lineage, lifecycle, schema, environment, budget, event type, and organism; a missing event is rejected through canonical foreign-key validation. All reject with zero clock, dispatch, charge, admission event, terminal, completion, or fixture effect.

Exact Issue #125 implementation head: `3ddf1116b0aecc4842d257131e3e62481729db58`. Strict isolated verification: `395 passed in 49.62s`, plus install and source/test compilation. The shared frozen Phase 1 checkpoint validator and original Phase 1 tests/helpers are unchanged. Temporary repair helpers/workflows are absent after cleanup.

The repaired candidate adds no live caregiver, model API, human chat, network, subprocess, arbitrary code/callable, memory, skill, training, continuous loop, personality/emotion state, action adoption, or proposal-to-Phase-1-selector route. Writer categories remain exactly `organism` and `administration`.

## Remaining gate

PR #119 remains open and unmerged. Issues #61/#121/#123/#124/#125 remain open. Phase 2 is not frozen. Issue #124 contains an interim finding rather than a final conclusion.

One final focused independent read-only closure audit is required at one exact ordinary-CI-green PR #119 head. It must independently test coherent active-and-snapshot request-event mutations and verify no regression across Findings 1–3 or the complete 213-ID gate.

## Exact restart

1. Read PR #119; Issues #61/#120/#121/#122/#123/#124/#125; the evidence map; and the Slice 42c notes.
2. Verify the final PR candidate contains request-event semantic repair head `3ddf1116b0aecc4842d257131e3e62481729db58` and only durable documentation closeout afterward.
3. Confirm all 395 protected tests pass under ordinary CI, schema-v1 CLI smoke passes, and all temporary helpers/workflows are absent.
4. Confirm all 47 original Phase 1 Python test/helper blobs remain byte-identical and the 152-test control remains green.
5. Request one final focused read-only audit against the exact fixed head.
6. Require a conclusion of `ready to freeze`, `ready to freeze after specified documentation-only corrections`, or `not ready to freeze; specified repairs required`.
7. Do not merge PR #119, close completion Issues, or declare Phase 2 frozen before a satisfactory conclusion.
8. After a satisfactory conclusion, merge PR #119, update final evidence/handoff, close Issues #125/#123/#121/#61, and freeze Phase 2.
9. Request human confirmation for any finding that changes contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.
