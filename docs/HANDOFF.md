# SUDACHI Handoff

Updated: **2026-07-27**

Phase 1 is frozen. ADRs 0008, 0009, and 0010 are accepted. Issue #61 owns Phase 2 implementation. Slice 36, Slice 37a1–a3, and Slice 38a–c are merged.

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

PRs #65, #66, #67, #69, #70, #71, #72, and #73 implement schema-v2 genesis, exact zero-caregiver projection, checkpoint repair, retention, rollback, event export, paired overhead, and absolute physical limits. Final run 512: `230 passed in 32.41s`.

### Slice 37 — request boundary

- PR #81 merged as `268fc5a8571f50cf19d7c8db15f975b40b1cd05c`; run 520: `236 passed in 33.52s`.
- PR #83 merged as `208956c40bffc0eff94307e6d326a071ee386d94`; run 533: `242 passed in 31.65s`.
- PR #85 merged as `82e17c6ccba65323315b399ea6fad345a52db5f4`; run 538: 245 tests passed.

### Slice 38a — canonical request graph

PR #87 merged as `16af01a84aae3d802a112228c85ec4b1849c19ee`; run 545: `261 passed in 34.10s`.

### Slice 38b — proposal graph

PR #91 merged as `068b3d30b91bd0bec89344a0d27b4685b3764a65`; run 551: `275 passed in 29.84s`.

### ADR 0010

PR #94 merged as `b98bfdbd3de52e192f18328d6a294c8a683fa998`. Issues #88/#89/#92/#93 are completed.

It closes exact dispatch identity, external provenance, response/package cardinality, current-state projection, disposition identity, and Protocol-v1 request-context absence.

### Slice 38c — dispatch/response/package protocol graph

PR #95 merged as `d5cbe115caaada4b71d58bb81527fb6179e0c913`.

Final exact PR head `c420c6153281b08d125666c1efd4a56b642282d8`, run 559: `294 passed in 37.06s` plus installation, compilation, and schema-v1 genesis CLI smoke.

It closes P2-H04, H07–H09, the pure graph portion of H11, P2-I01, I10, and response/package-side I11 without SQLite mutation or fixture execution.

Durable note: `docs/phase2/SLICE38C_DISPATCH_RESPONSE_PACKAGE.md`.

## Current design gate

Slice 39 requires one canonical dispatch row, one conservative cost-charge row, and one administrative event to commit atomically before fixture execution.

The accepted documents do **not** define:

- the exact `consultation_cost_charge.charge_id` value;
- the exact dispatch-admission `event.event_type`;
- the exact event payload field set and whether it embeds the final dispatch envelope, the charge ledger, or typed links only.

These are protected immutable canonical identities, not presentation details. Code must not invent them privately.

P2-D07/D08 and P2-E10 remain dependent on later legitimate terminalization/disposition cycles. Do not manufacture request ordinal four.

## Exact restart

1. Merge the Slice 38c closeout documentation PR.
2. Resolve the exact charge ID and dispatch-admission event schema through reviewed design clarification.
3. Implement Slice 39 administrative dispatch admission/precharge:
   - fresh fail-fast transaction;
   - exact sleeping/stable/current-lineage/unexpired/nonterminal/no-prior-dispatch checks;
   - atomic dispatch, charge, and event;
   - physical reserve checks;
   - commit and release SQLite before fixture execution;
   - no checkpoint or action effect;
   - no hidden retry.
4. Implement the deterministic fixture boundary outside SQLite ownership.
5. Keep all 152 Phase 1 tests unchanged and passing.
6. Do not use Codex until the complete Phase 2 implementation candidate is CI-green and ready for the single completion audit.
