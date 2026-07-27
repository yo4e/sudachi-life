# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008, 0009, and 0010 are accepted. Issue #61 owns Phase 2 implementation. Slice 36, Slice 37a1–a3, and Slice 38a–b are merged.

No live caregiver, model API, human chat, network, subprocess, memory, skill generation, action adoption, or generic agent behavior is authorized.

## Cold start

Read, in order:

1. `AGENTS.md`
2. `docs/AI_COLLABORATION_OPERATIONS.md`
3. `docs/MINIMAL_ORGANISM_CONTRACT.md`
4. accepted ADRs 0001–0010
5. `docs/PHASE1_TEST_MATRIX.md`
6. `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`
7. this handoff
8. `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
9. `docs/phase2/ADR0010_TEST_MATRIX_AMENDMENT.md`
10. `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
11. implemented `docs/phase2/` notes
12. Issue #61 and current PRs/issues

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

ADRs 0008, 0009, and 0010, Consultation Protocol v1, the ADR 0010 matrix amendment, and the Phase 2 matrix form one accepted package.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities are untrusted provenance only.

Original Phase 1 budget locations remain exactly `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Physical limits remain 8 MiB active/artifact, 40 MiB checkpoint store, 64 MiB working set, and 1 MiB next-wake reserve.

Consultation limits include 16 KiB request, 16 KiB package, 8 KiB provenance inside package, four requests/charged calls per lineage, one outstanding request, 64 KiB logical payload, and zero human/model/money/declared latency.

## Implemented evidence

### Slice 36 — complete

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, exact zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and absolute physical limits.

Final Slice 36 head `e1ef85e71ddefef06c9940145e6d27db0c22d39b`, run 512: `230 passed in 32.41s` plus install, compile, and schema-v1 CLI smoke.

### Slice 37 — request boundary

- PR #81 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`; run 520: `236 passed in 33.52s`.
- PR #83 merged as `208956c40bffc0eff94307e6d326a071ee386d94`; run 533: `242 passed in 31.65s`.
- PR #85 merged as `82e17c6ccba65323315b399ea6fad345a52db5f4`; run 538: 245 tests passed.

These implement exact request creation, storage-safe extension rollback, real physical accounting, backward-wall-time independence, and nested/competing wake fail-fast behavior.

### Slice 38a — canonical digest and request schema

PR #87 merged as `16af01a84aae3d802a112228c85ec4b1849c19ee`.

Final PR head `a571b769834fa223ed4afc5ef1d84e41cdbbee9a`; code/test run 545: `261 passed in 34.10s`.

It closes P2-H01, H02 core, H03, and request-side D11. Shared `phase2_protocol.py` owns canonical bytes, digest labels, request identity/ID, and final request validation.

The prior request constructor remains byte-identical in `phase2_request_impl.py`, blob `46881e023d990f5c7ce393cac7060958419383c0`.

### Slice 38b — proposal identity and exact types

PR #91 merged as `068b3d30b91bd0bec89344a0d27b4685b3764a65`.

Final PR head `3a0affde5e2bbd28491a02f442cd48cb82df66cf`; run 552 passed all steps. Implementation run 551: `275 passed in 29.84s`.

It closes P2-H05/H06, P2-I02–I09, and proposal-side I11 for exact action-candidate, abstain, and defer identities and rejection corpus.

Durable note: `docs/phase2/SLICE38B_PROPOSAL_SCHEMA.md`.

## ADR 0010 accepted clarifications

The project owner formally accepted the recommended resolutions of Issues #88, #89, #92, and #93.

ADR 0010 fixes:

- dispatch identity includes `configuration_version`;
- external provenance is exactly a three-field deterministic-fixture object;
- response identity, final response, and package cardinality are closed;
- `sudachi.consultation.current_state/v1` is the exact disposition projection;
- disposition identity is closed;
- Protocol v1 has no optional request context;
- P2-E10 tests the largest structural closed-v1 request, not artificial filler toward 16 KiB.

No database migration or Phase 1 change is authorized by the clarification.

## Remaining request requirements

P2-D07/D08 require later terminalization/disposition cycles. Do not bypass the frozen maintenance threshold with private state mutation.

P2-E10 is now defined by ADR 0010 and may be implemented with a real schema-v2 request/checkpoint fixture.

## Exact restart

1. Merge the Slice 38b closeout and ADR 0010 documentation PR.
2. Close Issues #88, #89, #92, and #93 as completed by ADR 0010.
3. Implement Slice 38c exact dispatch identity, response/provenance, proposal-response graph, and package validators using the shared canonical/digest core.
4. Map Slice 38c to P2-H04, H07–H09, H11, P2-I01, I10, response-side I11, and the ADR 0010 matrix amendment.
5. Implement the real P2-E10 largest structural request/checkpoint evidence without adding context fields.
6. Then begin Slice 39 administrative dispatch/precharge/fixture boundary.
7. Keep all 152 Phase 1 tests unchanged and passing.
8. Do not use Codex until every accepted Phase 2 requirement has protected evidence and one exact CI-green completion candidate is ready.
