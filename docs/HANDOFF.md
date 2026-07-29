# SUDACHI Handoff

Updated: **2026-07-29**

Phase 1 and Phase 2 are frozen. Phase 3 research Issues #129 and #130 are complete. Issue #132 and draft PR #134 contain a **Proposed, design-only** withheld-caregiver evaluation package. The first independent audit in Issue #135 concluded **not ready; material design revision required**; the proposed package now contains a focused correction pass and awaits exact-head CI plus an independent focused re-audit.

No Phase 3 runtime or live caregiver capability is accepted or authorized.

No live caregiver, model API, human chat, network, subprocess, memory, skill generation, action adoption, training, continuous loop, new writer category, repeated rollback, resource expansion, generic-agent behavior, personality, or emotion state is authorized.

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
12. implemented `docs/phase2/` notes, especially `docs/phase2/SLICE42C_FINAL_CLOSURE_AUDIT.md`
13. `docs/research/CAREGIVER_WITHDRAWAL_AND_RETAINED_COMPETENCE.md`
14. `docs/research/WITHDRAWAL_PROTOCOL_EXTRACTION.md`
15. proposed `docs/decisions/0017-withheld-caregiver-evaluation-contract.md`
16. proposed `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1.md`
17. proposed `docs/PHASE3_WITHHELD_CAREGIVER_TEST_MATRIX.md`
18. Issues #3, #132, #135, draft PR #134, and current GitHub state

Repository and current GitHub state outrank conversation history. An Issue #135 exact-head synchronization comment outranks an older candidate hash in prose.

## Thesis

SUDACHI asks whether a bounded artificial organism can convert finite external cognitive scaffolding into verified local competence and preserve capability while reducing justified caregiver dependence.

```text
parent reasoning -> verified experience -> reusable skill -> cheap local behavior
```

The repository is the organism's auditable body, developmental history, skill base, and lineage record. A model may later be caregiver or organ; it is not the organism.

> As it becomes smarter, it should become smaller and quieter.

## Frozen Phase 1

The final Phase 1 audit checked `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`: all findings resolved and 152 tests passed. The 47 original Phase 1 Python test/helper blobs remain the protected schema-v1 control.

Do not change Phase 1 actions, selector, executor, evaluators, injected clocks, checkpoint rules, rollback transformation, writer categories, budgets, physical ceilings, or protected tests for later-phase convenience. Any exact frozen-boundary defect requires explicit project-owner authorization before repair.

PR #73 merged the explicitly authorized physical-limit repairs as `c9004027a94b709802af7f590d46de862dd93d7d`; repaired boundaries are re-frozen and pre-repair bodies remain in explicit `*_impl.py` modules.

Issue #117 authorized one narrow rollback-retention repair after Slice 42b exposed a deterministic defect. PR #116 merged it as `0059e0e20ececcf9e16a9b1a4376c3564cf9c391`; the repaired public rollback boundary is re-frozen and the pre-repair body remains preserved.

## Frozen Phase 2

ADRs 0008–0016, Consultation Protocol v1, the accepted matrix amendments, the 213-ID evidence map, implemented Slice 36–42c behavior, and all protected tests merged through PR #119 form the frozen Phase 2 package.

Canonical writer categories remain exactly `organism` and `administration`. Caregiver and adapter identities remain untrusted provenance only.

Original Phase 1 budget locations remain `phase1-v1`. Phase 2 policy lives only in immutable `consultation_configuration`.

Physical limits remain:

- 8 MiB active/artifact;
- 40 MiB checkpoint store;
- 64 MiB working set;
- 1 MiB next-wake reserve.

Consultation limits remain:

- 16 KiB request;
- 16 KiB package;
- 8 KiB provenance inside package;
- four requests/charged calls per lineage;
- one outstanding request;
- 64 KiB logical payload;
- zero human/model/money/declared latency.

The Phase 2 implementation stream was merged through PRs #65–#119. The final independent read-only audit in Issue #127 checked exact candidate `12de7b7d7413f343b2e5a74df369c26a5896c865` and verified:

- 395 protected tests passed;
- all 152 original Phase 1 tests passed;
- all 47 original Phase 1 Python test/helper blobs remained byte-identical;
- exactly 213 accepted and evidence-map IDs remained equal;
- schema-v1 and schema-v2 zero-caregiver behavior remained intact;
- writer categories remained exactly `organism` and `administration`;
- checkpoint, rollback, identity, digest, immutable-row, artifact, physical-limit, and no-partial-effect boundaries remained intact;
- no unauthorized live caregiver, API, chat, network, subprocess, callable/code, memory, skill, training, loop, personality/emotion, action-adoption, or selector route existed.

PR #119 merged the exact audited package as `b0941a8ba2a178fc891839198cd5dd5bf6e87719`. Phase 2 is frozen at that merge.

## Routine clarification delegation

The project owner authorizes routine recommended clarifications under `docs/phase2/CLARIFICATION_DELEGATION.md`.

Every delegated adoption still requires a focused Issue, normative document change, protected CI, and durable handoff. Material changes to research purpose, contract intent, frozen behavior, authority/security, live external capability, protected evidence, autonomy/resources, or unresolved contradictions require explicit human confirmation.

## Phase 3 research

Issue #129 completed the first bounded evidence pass. PR #131 merged `docs/research/CAREGIVER_WITHDRAWAL_AND_RETAINED_COMPETENCE.md` after ordinary CI passed all 395 protected tests.

Issue #130 completed full-text protocol extraction. PR #133 merged `docs/research/WITHDRAWAL_PROTOCOL_EXTRACTION.md` after ordinary CI passed all 395 protected tests.

Research conclusion:

- assistance fading, competence-gated intervention, full no-helper evaluation, scaffold-free deployment, finite demonstration followed by autonomy, skill internalization, and versioned/tested/pruned skill lifecycles are established neighboring mechanisms;
- a live source can disappear while prompts, demonstrations, traces, routers, tools, recovery suffixes, or skill banks remain at runtime;
- the remaining plausible SUDACHI candidate is a protected integration and measurement protocol, not any one mechanism;
- bounded negative search does not prove novelty.

No code, schema, writer category, authority boundary, budget, resource ceiling, or runtime capability changed in the research passes.

## Proposed Phase 3 package

Issue #132 and draft PR #134 contain:

- ADR 0017, status **Proposed**;
- `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1.md`, status **Proposed**;
- `docs/PHASE3_WITHHELD_CAREGIVER_TEST_MATRIX.md`, status **Proposed**.

The original exact audit candidate was `932ff2ad8d99e8d9fb2e78a16cd12a5f1e8995c9`, with Test run 680 successful and `395 passed in 55.27s`. Issue #135 independently audited that exact head and concluded:

> not ready; material design revision required

The audit findings were:

1. `P3-D001` — W3 overlapped W1/W2;
2. `P3-D002` — fixed configuration conflicted with E2 disablement;
3. `P3-D003` — invalid or not-reached E0 could establish acquisition;
4. `P3-D004` — same-lineage cross-episode evidence could be laundered;
5. `P3-D005` — the outcome evaluator could become a development oracle;
6. `P3-D006` — conversion, verification, adoption, and activation were not four protected transitions;
7. `P3-D007` — opaque model updates had a fail-open exception;
8. `P3-D008` — failed-attempt population and stopping rules were open;
9. `P3-D009` — the cost ledger lacked a final closure boundary;
10. `P3-D010` — the matrix could pass while contract clauses drifted.

On 2026-07-29 the project owner authorized the focused correction pass, including the evaluator/information-flow redesign. That authorization permits proposed documentation repair only; it is not final contract acceptance or implementation authorization.

## Corrected proposed semantics

The focused correction pass now proposes:

- W0/W1/W2 as the mutually exclusive point-local availability axis;
- W3 as an orthogonal episode-level certification that preserves its E2 W1 or W2 subtype;
- a pre-E0 study/run-set manifest with attempt ordinals, exact count or stopping rule, terminal statuses, and full-population reconciliation;
- evidence binding across exact study, attempt, episode, organism, lineage, point/cutoff, and checkpoint identities;
- a pre-E0 immutable protected schedule containing the sole legal E1 cutoff and E2 availability transition;
- acquisition only from a valid, reachable, complete E0 with an explicitly eligible negative status;
- separate immutable conversion, verification, adoption, and activation transitions with accepted-but-inactive state, authority, ordering, idempotence, conflict, and no-partial-effect rules;
- a distinct conversion verifier and sequestered held-out outcome evaluator under a pre-E0 information-flow and probe/retry policy;
- mandatory identity, digest, method, data-class, compute/storage, and verification evidence for any W2/W3 model update; opaque updates are unsupported rather than fail-open;
- mandatory failure controls, failed-attempt retention, claim tiers, and stopping-rule reconciliation;
- one immutable final cost closure after E2, integrity handling, evidence packaging, and report review;
- an exact fourteen-group W3 report;
- the original 140 matrix IDs retained, with normative clause references, explicit fail-closed outcomes, exact clause/report-set equality gates, and full Phase 1/2 collection/no-skip/assertion/blob integrity.

No corrected document chooses a database schema, transport, live source, provider, artifact type, model-update permission, evaluator implementation, experiment count, hardware environment, or scalar maturity score.

No corrected document authorizes live caregiver, memory, skills, training, model/API, network, subprocess, action adoption, new writer authority, repeated rollback, resource expansion, or other Phase 3 runtime capability.

## Exact restart

1. Treat Phase 1 and Phase 2 as frozen controls.
2. Read Issue #135's original independent audit and all findings `P3-D001` through `P3-D010`.
3. Inspect the corrected proposed ADR 0017, contract, and 140-ID matrix in draft PR #134.
4. Confirm the PR remains Draft and every Phase 3 document remains Proposed.
5. Run ordinary protected CI on the final corrected PR #134 head and synchronize the exact head/run/results in PR #134 and Issue #135.
6. Run one **independent focused read-only re-audit** against that exact CI-green head. The authoring assistant's review does not count as independent.
7. Require the re-audit to map every original finding to exact corrected clauses and matrix IDs and conclude one of the required Issue #135 outcomes.
8. Do not change Proposed to Accepted, merge PR #134, or begin implementation until the focused re-audit is satisfactory and final project-owner acceptance is recorded.
9. Acceptance of the design package still does not authorize implementation; future capability work requires separately accepted scope, matrices, controls, provider/legal review where applicable, owner authorization, and independent implementation audit.
