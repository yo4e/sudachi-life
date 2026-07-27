# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008 and 0009 are accepted. Issue #61 owns Phase 2 implementation. Slice 36, Slice 37a1–a3, and Slice 38a are merged.

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
11. Issue #61, Issues #88/#89, and open PRs

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

Physical limits remain 8 MiB active/artifact, 40 MiB checkpoint store, 64 MiB working set, and 1 MiB next-wake reserve.

Consultation limits include 16 KiB request, 16 KiB package, 8 KiB provenance inside package, four requests/charged calls per lineage, one outstanding request, 64 KiB logical payload, and zero human/model/money/declared latency.

## Implemented evidence

### Slice 36 — complete

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, exact zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and absolute physical limits.

Final Slice 36 head `e1ef85e71ddefef06c9940145e6d27db0c22d39b`, run 512: `230 passed in 32.41s` plus install, compile, and schema-v1 CLI smoke.

Read `docs/phase2/SLICE36*.md`. Issues #74–#79 are closed.

### Slice 37a1 — request-wake core

PR #81 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`.

Final head `27d55d2853afb8f09530481dffa537f91b78640e`, run 520: `236 passed in 33.52s`.

Durable note: `docs/phase2/SLICE37A1_REQUEST_WAKE_CORE.md`.

### Slice 37a2 — storage-safe extension

PR #83 merged as `208956c40bffc0eff94307e6d326a071ee386d94`.

Final head `41def40ffee3369194eae45734accccae1ce180c`, run 533: `242 passed in 31.65s`.

It closes P2-E01–P2-E09 and P2-D12 with real sidecar/checkpoint/working-set/reserve accounting and exact extension-only rollback.

Durable note: `docs/phase2/SLICE37A2_REQUEST_STORAGE_SAFETY.md`.

### Slice 37a3 — time and concurrency

PR #85 merged as `82e17c6ccba65323315b399ea6fad345a52db5f4`.

Final head `2d147d8acc1a4bd4f8750c499e5f94209b05ff55`, run 538: 245 tests passed plus install, compile, and schema-v1 CLI smoke.

It closes P2-D14 and P2-D15 without production source changes.

Durable note: `docs/phase2/SLICE37A3_REQUEST_TIME_CONCURRENCY.md`.

### Slice 38a — canonical digest and request schema

PR #87 merged as `16af01a84aae3d802a112228c85ec4b1849c19ee`.

Final exact PR head `a571b769834fa223ed4afc5ef1d84e41cdbbee9a`, run 546 passed all steps. Code/test head `a3637c723da9696ebe618ed6d2ca5e7f3f467da9`, run 545: `261 passed in 34.10s`.

It closes P2-H01, the core of P2-H02, P2-H03, and the request side of P2-D11. Shared `phase2_protocol.py` owns exact canonical bytes, digest labels, request identity/ID, and final request validation.

The prior request constructor remains byte-identical in `phase2_request_impl.py`, blob `46881e023d990f5c7ce393cac7060958419383c0`. The public wrapper validates before event write inside the existing savepoint.

Durable note: `docs/phase2/SLICE38A_CANONICAL_DIGEST_REQUEST_SCHEMA.md`.

## Open design clarifications

- Issue #88: dispatch identity exact list omits `configuration_version` in protocol section 3.2 while section 4.1 requires it in every dispatch identity. P2-H04 and Slice 39 dispatch must not choose privately.
- Issue #89: exact external-provenance field set is not enumerated. P2-I01 and P2-H07–H09 response/package vectors must not use an opaque or invented schema.
- P2-H10 requires the versioned protected current-state projection before disposition identity code.
- P2-E10 requires an exact reviewed maximum request-envelope interpretation. Do not invent optional context fields merely to fill 16 KiB.

## Remaining request requirements

P2-D07/D08 depend on later terminalization/disposition cycles. The frozen maintenance threshold must not be bypassed with private state mutation.

## Exact restart

1. Continue independent Slice 38 proposal identity and type-specific proposal validation that does not construct a dispatch identity or response provenance.
2. Map it to P2-H05/H06 and P2-I02–P2-I09.
3. Use the shared canonical/digest core from Slice 38a.
4. Reject extra fields, free text, authority/cost/budget/permission commands, unknown action, invalid parameters, wrong evaluator set, and expiry mismatch.
5. Do not implement H04, H07–H10, I01, or response/package/disposition code until the relevant design clarifications are accepted.
6. Keep all 152 Phase 1 tests unchanged and passing.
7. Do not use Codex until every accepted Phase 2 requirement has protected evidence and one exact CI-green completion candidate is ready.
