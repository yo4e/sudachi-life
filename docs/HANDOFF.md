# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36, Slice 37a1, and Slice 37a2 are merged. Remaining request-core evidence is the next implementation boundary.

No live caregiver integration is authorized.

Read `AGENTS.md`, `docs/AI_COLLABORATION_OPERATIONS.md`, Minimal Organism Contract v0.2, accepted ADRs 0001–0009, the Phase 1 matrix, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, this handoff, Consultation Protocol v1, the accepted Phase 2 matrix, implemented Phase 2 notes, and current Issues/PRs.

## Thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

Repository is auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

The final Phase 1 audit checked `main` at `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338` and found all six findings resolved, no new blocker/high/medium defect, and 152 tests passing. Those 152 tests remain unchanged and form the schema-v1 control.

Do not alter Phase 1 garden actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, authority categories, or protected tests for Phase 2 convenience.

PR #73 temporarily reopened shared Phase 1 code only for explicit real-file absolute-limit defects. It merged as `c9004027a94b709802af7f590d46de862dd93d7d`. Pre-repair bodies remain in `*_impl.py` modules. The narrow shared physical boundaries are re-frozen; do not treat the wrappers as general redesign permission.

The pre-request-extension garden wake body remains byte-identical in `lifecycle_impl.py` at blob `c971d77cc9beab22f5c50fb692b4f81210cbf3ed`. Slice 37 may add only the accepted schema-v2 optional request extension around that retained body; it is not permission to redesign Phase 1 wake semantics.

## Accepted Phase 2 design

ADRs 0008 and 0009, Consultation Protocol v1, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` form one accepted design package.

Original Phase 1 budget locations stay exactly `phase1-v1`; Phase 2 policy lives in immutable `consultation_configuration`; checkpoint, repair, retention, rollback, export, and physical evidence use the exact closed rules in ADR 0009.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are provenance only.

## Implemented Slice 36 evidence

### Slice 36a — merged

PR #65 merged as `75077220ecb52256857f2b234283d36e3c0f51d2`.

It delivers schema-v2 genesis, exact protected zero/fixture configuration, unchanged Phase 1 tables and budget locations, immutable consultation objects, stable schema-v2 checkpoint validation, zero-caregiver absence, and the genesis active-database overhead bound.

Durable note: `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md`.

### Slice 36b1 — merged

PR #66 merged as `700dca34a70eca24ee024f07067f0f6fcb1f3f11`.

It delivers the active-database and genesis-checkpoint core of `phase1-projection-v2`, including exact side roles, fixed-order original Phase 1 rows, strict zero-caregiver absence, independent checkpoint integrity, raw checkpoint linkage before `CP(g,e)`, and exact nested/unlisted/wrong-location behavior.

Durable note: `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md`.

### Slice 36b2a1 — merged

PR #67 merged as `ccc2178a15e10ef3c93966cd2b5bbd3ec5d89f35`.

It validates exact pending-checkpoint repair identity, digest, size, previous-boundary, and checkpoint-store evidence before projection.

Durable note: `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md`.

### Slice 36b2a2 — merged

PR #69 merged as `64ea9eb094a687c056a571d362c1914aaf7911f2`.

It validates normal prune, restored pre-commit failure, committed cleanup failure, `STAGE(CP(g,e))`, pending reconciliation, interruption after deletion, retry, and completion. Deleted identity and bytes come only from prior immutable evidence.

Durable note: `docs/phase2/SLICE36B2A2_RETENTION_PROJECTION.md`.

### Slice 36b2a3 — merged

PR #70 merged as `054382a1ea57fa3e3c87d70d725b5a4a5415334b`.

Final head `4a0f82432e780245b3258983735c4f224a2f89fc` passed run 461 with `191 passed in 19.74s`. It validates exact `CP`, `RA`, `RC`, and `TC` artifact/event linkage, cross-lineage checkpoint references, abandoned-future preservation, and lineage-aware event-sequence reuse.

Durable note: `docs/phase2/SLICE36B2A3_ROLLBACK_PROJECTION.md`.

### Slice 36b2a4 — merged

PR #71 merged as `d7ce1703eaaf9aca1a33f72add4a9dfa707e7abe`.

Final head `31736c45ff1879002991a6249c86ffa86c0f07b8` passed run 468 with `196 passed in 19.01s`; installation, compilation, and schema-v1 genesis CLI smoke succeeded.

It independently validates raw canonical JSONL, exact manifest/event schemas, event range/count/order, active source-checkpoint linkage, reconstructed bytes, raw size, and raw SHA before semantic event projection.

Durable note: `docs/phase2/SLICE36B2A4_EVENT_EXPORT_PROJECTION.md`.

### Slice 36b2a5 — merged

PR #72 merged as `3cd46b5929d6bc5dea8b0cbede417b40e792ce72`.

Final run 475 passed with `200 passed in 20.09s`. Real paired schema-v1/schema-v2-zero scenarios enforce active and each `CP`/`RA`/`RC`/`TC` database overhead at at most 256 KiB and aggregate additional non-database artifact bytes at at most 1 MiB.

Durable note: `docs/phase2/SLICE36B2A5_PHYSICAL_OVERHEAD.md`.

### Slice 36b2a6 — merged

PR #73 merged as `c9004027a94b709802af7f590d46de862dd93d7d`.

Final exact PR head `e1ef85e71ddefef06c9940145e6d27db0c22d39b` passed GitHub Actions run 512 with `230 passed in 32.41s`. Installation, compilation, and schema-v1 genesis CLI smoke succeeded. The unchanged 152 Phase 1 tests remain included. Codex was not used.

Protected real-file evidence closes P2-O18, P2-O19, P2-O21, and P2-O22 across active/artifact 8 MiB, checkpoint-store 40 MiB, working-set 64 MiB, exact 1 MiB next-wake reserve, and all checkpoint/repair/retention/rollback publication, reentry, replacement, and completion paths.

Issues #74–#79 are closed as completed. Each shared repair was explicitly owner-authorized and limited to physical admission, cleanup, or transaction rollback. No accepted limit, authority, idempotence, retention choice, lineage rule, or semantic behavior changed.

Durable notes:

- `docs/phase2/SLICE36B2A6_ABSOLUTE_PHYSICAL_LIMITS.md`
- `docs/phase2/SLICE36B2A6_ACTIVE_REPAIR_ADDENDUM.md`

Slice 36 is complete.

## Implemented Slice 37 evidence

### Slice 37a1 — merged

PR #81 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`.

Final exact PR head `27d55d2853afb8f09530481dffa537f91b78640e` passed GitHub Actions run 520 with `236 passed in 33.52s`. Installation, compilation, and schema-v1 genesis CLI smoke succeeded. All original 152 Phase 1 tests remain unchanged and included. Codex was not used.

Delivered evidence:

- request only after fixture-configured schema-v2 incomplete-objective `no_applicable_action`;
- unchanged Phase 1 abstention failure and exactly one failure-streak increment;
- no request for schema-v1, zero-caregiver, applicable action, objective completion, maintenance entry, request limit, or an outstanding request;
- exact request identity, digest preimage, ID, final canonical envelope, event linkage, and event-sequence exclusion;
- one immutable request row and one request event in a dedicated savepoint;
- exact request preserved in the ordinary stable lifecycle checkpoint;
- an outstanding request does not block a later caller-selected garden wake.

Durable note: `docs/phase2/SLICE37A1_REQUEST_WAKE_CORE.md`.

### Slice 37a2 — merged

PR #83 merged as `208956c40bffc0eff94307e6d326a071ee386d94`.

Final exact PR head `41def40ffee3369194eae45734accccae1ce180c` passed GitHub Actions run 533 with `242 passed in 31.65s`. Installation, compilation, and schema-v1 genesis CLI smoke succeeded. All original 152 Phase 1 tests remain unchanged and included. Codex was not used.

Delivered evidence closes P2-E01–P2-E09 and P2-D12:

- conservative pre-write projection includes active allocation, real journal/WAL/SHM, request row/event bytes, checkpoint tail, resulting checkpoint/manifest, checkpoint store, working set, and 1 MiB reserve;
- post-write page allocation is remeasured before savepoint release;
- request-only refusal leaves no consultation row/event/source/sequence/cost and returns exact noncanonical reason;
- refusal commits exact retained Phase 1 state and ordinary checkpoint;
- a real 7 MiB active body preserves the 1 MiB reserve and completes two queued wakes;
- real WAL/SHM bytes are independently reconciled into the projection;
- a core body above 8 MiB raises the unchanged Phase 1 error and rolls back instead of becoming optional refusal;
- normal request/checkpoint success remains under all inherited physical limits.

Durable note: `docs/phase2/SLICE37A2_REQUEST_STORAGE_SAFETY.md`.

Still open in the request boundary:

- P2-D07/D08: request epoch and ordinal across expiry and rollback;
- P2-D11: exact-field and forbidden free-text adversarial corpus;
- P2-D14: backward wall-time independence;
- P2-D15: competing and nested wake fail-fast evidence;
- P2-E10: maximum-size request evidence. The optional typed context field set is not enumerated by the accepted protocol, so no private context fields may be invented to fill 16 KiB.

## Accepted boundaries and budgets

- schema-v2 new organisms only; no migration/downgrade
- request envelope ≤16 KiB
- complete external package ≤16 KiB
- provenance ≤8 KiB inside package limit
- four requests/four charged fixture calls per current lineage
- one outstanding current-lineage request
- 64 KiB exact logical payload per lineage
- zero human/model/money/declared fixture latency
- active database/artifact 8 MiB
- checkpoint store 40 MiB
- working set 64 MiB
- next-wake reserve 1 MiB

## Audit cadence

The next Codex use is the single Phase 2 implementation-completion audit, after every accepted matrix requirement has protected evidence and one exact CI-green candidate is ready to freeze. Do not use Codex per slice or for ordinary editing.

## Explicit exclusions

No live model/API/human caregiver, memory or skill generation, source/test generation, training, arbitrary code/SQL/shell/tools/paths/URLs/credentials, organism network/subprocess, continuous execution, personality/emotion state, caregiver-controlled authority, or generic agent framework.

## Exact restart

1. start the next request-core sub-slice from `main` at or after `208956c40bffc0eff94307e6d326a071ee386d94` plus this closeout documentation merge;
2. map it to P2-D07/D08, P2-D11, P2-D14, and P2-D15 without changing the accepted request identity/envelope;
3. prove four current-lineage requests and exact ordinal behavior through lifecycle expiry and rollback epoch changes;
4. add exact-field/forbidden-free-text validation and backward-wall-time evidence;
5. add competing and nested wake fail-fast evidence without hidden retry or queueing;
6. leave P2-E10 blocked unless an exact reviewed maximum-envelope interpretation is available;
7. keep all original 152 Phase 1 tests unchanged and passing;
8. keep Codex deferred until the complete Phase 2 implementation candidate is ready for the single completion audit.
