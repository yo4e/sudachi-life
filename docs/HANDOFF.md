# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36 and Slice 37a1–a3 are merged. The exact next implementation boundary is Slice 38 digest graph and typed external schemas.

No live caregiver, model API, human chat, network, subprocess, memory, skill generation, action adoption, or generic agent behavior is authorized.

## Cold start

Read, in order:

1. `AGENTS.md`
2. `docs/AI_COLLABORATION_OPERATIONS.md`
3. `docs/MINIMAL_ORGANISM_CONTRACT.md`
4. accepted ADRs 0001–0009
5. `docs/PHASE1_TEST_MATRIX.md`
6. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
7. this handoff
8. `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
9. `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
10. implemented `docs/phase2/` notes
11. current Issue #61 and open PRs

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

ADRs 0008 and 0009, Consultation Protocol v1, and the Phase 2 matrix form one accepted package.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are untrusted provenance only.

Original Phase 1 budget locations remain exactly `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Accepted physical limits remain:

- active database and individual database artifact: 8 MiB
- checkpoint store: 40 MiB
- runtime working set: 64 MiB
- next-wake reserve: 1 MiB

Accepted consultation limits include:

- request envelope: 16 KiB
- complete external package: 16 KiB
- provenance: 8 KiB inside the package limit
- four requests and four charged fixture invocations per current lineage
- one outstanding current-lineage request
- 64 KiB logical payload per lineage
- zero human/model/money/declared fixture latency

## Implemented evidence

### Slice 36 — complete

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, exact zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and independent absolute physical limits.

Final Slice 36 code head `e1ef85e71ddefef06c9940145e6d27db0c22d39b`, run 512: `230 passed in 32.41s` plus install, compile, and schema-v1 CLI smoke.

Durable notes are under `docs/phase2/SLICE36*.md`. Issues #74–#79 are closed.

### Slice 37a1 — request-wake core

PR #81 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`.

Final head `27d55d2853afb8f09530481dffa537f91b78640e`, run 520: `236 passed in 33.52s`.

It proves request eligibility after incomplete-objective `no_applicable_action`, exact Phase 1 failure truth, maintenance exclusion, exact request identity/envelope/event linkage, savepoint atomicity, stable checkpoint preservation, and later garden-wake availability.

Durable note: `docs/phase2/SLICE37A1_REQUEST_WAKE_CORE.md`.

### Slice 37a2 — storage-safe request extension

PR #83 merged as `208956c40bffc0eff94307e6d326a071ee386d94`.

Final head `41def40ffee3369194eae45734accccae1ce180c`, run 533: `242 passed in 31.65s`.

It closes P2-E01–P2-E09 and P2-D12 with real active pages, journal/WAL/SHM, checkpoint, checkpoint-store, working-set, and reserve accounting. Extension-only refusal returns `consultation_request_not_created_storage_budget`, leaves no consultation mutation, and preserves the exact retained core and ordinary checkpoint. Core physical failure remains unchanged.

Durable note: `docs/phase2/SLICE37A2_REQUEST_STORAGE_SAFETY.md`.

### Slice 37a3 — time and concurrency

PR #85 merged as `82e17c6ccba65323315b399ea6fad345a52db5f4`.

Final head `2d147d8acc1a4bd4f8750c499e5f94209b05ff55`, run 538: 245 tests passed; install, compile, and schema-v1 CLI smoke succeeded.

It closes:

- P2-D14: backward wall time does not affect request identity, ordinal, event linkage, or lifecycle expiry;
- P2-D15: nested and competing-process wakes fail fast before request mutation, are not queued or retried, and leave the input for one later explicit wake.

No production source changed.

Durable note: `docs/phase2/SLICE37A3_REQUEST_TIME_CONCURRENCY.md`.

## Open request requirements

- P2-D07/D08: four requests and exact ordinal/epoch behavior require later request terminalization or disposition cycles; do not bypass the frozen maintenance threshold with private state mutation.
- P2-D11: exact-field and forbidden-free-text evidence belongs with Slice 38 typed validators because request creation accepts no untrusted fields.
- P2-E10: maximum-size request evidence is blocked because optional typed request context is permitted but its exact field set is not enumerated. Do not invent private fields merely to fill 16 KiB.

## Exact restart

1. Start Slice 38 from `main` after the Slice 37a3 closeout documentation merge.
2. Follow Issue #61 ordering: Slice 38 before dispatch.
3. Implement test-first P2-H01–P2-H11 and P2-I01–P2-I11.
4. Begin with the shared canonical JSON and domain-separated digest core, then exact request/dispatch/proposal/response/package field validators.
5. Resolve any exact-field contradiction through reviewed design work; code must not choose a private interpretation.
6. Keep all 152 Phase 1 tests unchanged and passing.
7. Do not use Codex until every accepted Phase 2 requirement has protected evidence and one exact CI-green completion candidate is ready.
