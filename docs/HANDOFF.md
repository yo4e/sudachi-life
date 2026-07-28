# SUDACHI Handoff

Updated: **2026-07-28**

Phase 1 is frozen. ADRs 0008–0016 are accepted. Issue #61 owns Phase 2 implementation. Slice 36, Slice 37a1–a3, Slice 38a–c, Slice 39a, Slice 40, Slice 41, and Slice 42a are merged.

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

Do not change Phase 1 actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, writer categories, or protected tests for Phase 2 convenience.

PR #73 temporarily reopened shared code only for explicitly authorized physical-limit defects and merged as `c9004027a94b709802af7f590d46de862dd93d7d`. The repaired physical boundaries are re-frozen. Pre-repair bodies remain in explicit `*_impl.py` modules.

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

It implements and protects:

- legitimate current-lineage request ordinals one through four;
- the exact fifth-request noncanonical refusal with no fifth consultation mutation;
- four dispatches and conservative charges with no fifth fixture invocation;
- the ADR 0014 maximum structural request with exactly eight eligible parents;
- the pure lineage-payload function admitting 65536 and rejecting 65537;
- the measured legal closed-v1 four-cycle maximum below 64 KiB without filler or double counting;
- ordinary checkpoint and inherited physical-limit evidence;
- preservation of the retained request and ingress implementation bodies;
- no private canonical mutation.

Durable note: `docs/phase2/SLICE42A_FINITE_CYCLE_BOUNDARIES.md`.

## Rollback and lineage boundary

Current lineage is the consultation budget epoch. Accepted rollback increments lineage, leaves prior-lineage consultation rows as immutable inactive history, and starts fresh request, charge, and logical-payload accounting for the new current lineage.

ADR 0007 permits one completed rollback per physical organism. Therefore the implementation must prove at most two consultation epochs and at most eight charged fixture invocations across one organism.

Old-lineage unresolved work must not block current-lineage work. Late packages from an abandoned lineage must fail before mutation, and old-lineage proposals must never be selected by the current disposition wake.

## Remaining boundaries

- P2-J10 and P2-M08–P2-M11 new-lineage reset, historical inactivity, old-work nonblocking behavior, and the full two-lineage charge bound.
- P2-O12/O13/O22 rollback archive/candidate/completion preservation, the one-rollback rule, consultation provenance, and corruption rejection.
- Complete ancestry/export/authority reconstruction across rollback.
- Remaining physical accounting and explicit-absence implementation-completion review.
- No private canonical mutation or manufactured lineage state.

## Exact restart

1. Merge the Slice 42a closeout PR, then begin Slice 42b test-first from updated `main`.
2. Build legitimate pre-rollback consultation history through public request, dispatch, ingress/terminalization, disposition, ordinary wake, checkpoint, and maintenance operations only.
3. Invoke the accepted public rollback path once without changing the frozen rollback transformation.
4. Prove the new current lineage begins with request ordinal one, zero current-lineage logical bytes before its first request, and a fresh four-request/four-charge epoch while old rows remain immutable history.
5. Prove old-lineage unresolved work does not block current work, late old-lineage packages fail before mutation, and old-lineage proposals are excluded from disposition selection.
6. Prove the full maximum of eight charged invocations across two epochs and reject a second completed rollback under ADR 0007.
7. Reconstruct consultation rows, events, parents, authority, archive/source/transformed-candidate/completion artifacts, and physical totals across rollback.
8. Keep all 152 Phase 1 tests unchanged and passing.
9. Do not use Codex until every accepted Phase 2 requirement has protected evidence and one exact CI-green candidate is ready.
