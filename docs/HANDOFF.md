# SUDACHI Handoff

Updated: **2026-08-06**

Phase 1 and Phase 2 are frozen. The Phase 3 withheld-caregiver evaluation contract is now an **Accepted design package** through `docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md`.

The accepted semantic and cryptographic design reference remains exact audited candidate `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c`. The later acceptance-metadata commit and PR #134 merge commit are administrative wrappers and do not alter the audited package inputs.

No Phase 3 implementation or live caregiver capability is accepted or authorized.

No live caregiver, model API, human chat, network, subprocess, memory, skill generation, action adoption or execution, training, continuous loop, new writer category, repeated rollback, resource expansion, generic-agent behavior, personality, or emotion state is authorized.

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
15. `docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md`
16. the accepted audited inputs at candidate `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c`:
    - `docs/decisions/0017-withheld-caregiver-evaluation-contract.md`
    - `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1.md`
    - `docs/PHASE3_WITHHELD_CAREGIVER_TEST_MATRIX.md`
    - `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1_RESIDUAL_AMENDMENT.md`
    - `docs/phase3/WITHHELD_CAREGIVER_EFFECTIVE_MATRIX_LITERAL_REPLACEMENTS.md`
    - `docs/phase3/WITHHELD_CAREGIVER_RESIDUAL_HANDOFF.md`
17. Issues #3, #132, #135, #136, PR #134, and current GitHub state

Repository and current GitHub state outrank conversation history. The acceptance manifest is the authoritative package-level status record. The embedded `Proposed` labels in the audited input blobs record their pre-acceptance audit state and are intentionally preserved byte-for-byte.

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

## Phase 3 research basis

Issue #129 completed the first bounded evidence pass. PR #131 merged `docs/research/CAREGIVER_WITHDRAWAL_AND_RETAINED_COMPETENCE.md` after ordinary CI passed all 395 protected tests.

Issue #130 completed full-text protocol extraction. PR #133 merged `docs/research/WITHDRAWAL_PROTOCOL_EXTRACTION.md` after ordinary CI passed all 395 protected tests.

Research conclusion:

- assistance fading, competence-gated intervention, full no-helper evaluation, scaffold-free deployment, finite demonstration followed by autonomy, skill internalization, and versioned/tested/pruned skill lifecycles are established neighboring mechanisms;
- a live source can disappear while prompts, demonstrations, traces, routers, tools, recovery suffixes, or skill banks remain at runtime;
- the remaining plausible SUDACHI candidate is a protected integration and measurement protocol, not any one mechanism;
- bounded negative search does not prove novelty.

No code, schema, writer category, authority boundary, budget, resource ceiling, or runtime capability changed in the research passes.

## Accepted Phase 3 design package

### Accepted audited candidate

- exact audited candidate head: `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c`;
- exact base: `6e4aeabbdd25dc8a04dc6118458ef8cb61fe102f`;
- range: seven documentation files only;
- no `src/` or `tests/` change;
- ordinary CI: Test run 689 / workflow run `30640978451`, success;
- protected suite: `395 passed in 93.78s`;
- independent protected suite: `395 passed in 17.39s`;
- original Phase 1 protected subset: `152 passed in 3.32s`;
- Phase 2 matrix/evidence-map sets: exactly `213/213` and set-equal.

Accepted package-input blobs:

- ADR 0017: `72a6b1503f8ec0b6755bda77ecd649b9965cc442`;
- base contract: `99fa9bbd061bdee30d4ee10d8315cf0d37cb90d1`;
- base matrix: `fb693094431b3f934b7e9eae4c5685324cc4a244`;
- residual amendment: `00809bd097238b55d53495a477e2308d271460d1`;
- corrected literal specification: `2010516128d355c54c32f8422021abfc8fd58beb`;
- residual handoff: `612adb974289e01a5d7c2b8203f7432be6ea5382`;
- pre-acceptance handoff: `37e479342cfeceed3d868de0d5f91d7c06341939`.

### Canonical effective matrix registry

The final P3-D010 verification independently reconstructed the complete registry with Python and Ruby and obtained the same output:

- exactly 140 rows and 140 unique IDs in declared A01–L14 order;
- exactly five nonempty cells per row;
- 14 exact literal replacements;
- 126 byte-preserved unamended rows except for the required cell-2 prefix;
- exactly one `REQ:<row-ID>; ` token per row at the beginning of cell 2;
- corrected `P3-L14` contains no additional literal `REQ:` occurrence;
- canonical SHA-256: `12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1`;
- canonical byte length: `43179`.

The earlier diagnostic digest `77ed87159dc40444516a93d0f82041b15c35c9012d90bdc6ebac6e53cd641ff3` at `43154` bytes remains rejected and noncanonical.

### Audit disposition and acceptance

Issue #135's audit chain identified and closed the original findings `P3-D001` through `P3-D010`; the later bounded `P3-D011` was also closed.

Final Issue #135 comment `5199730734` concluded:

> ready to accept after audit metadata synchronization

On 2026-08-06 the project owner explicitly accepted the Phase 3 withheld-caregiver evaluation contract design at the exact audited candidate and authorized acceptance metadata synchronization, completion of Issue #136, and PR #134 merge processing. Implementation and live capability remain separately gated and unauthorized.

`docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md` is the authoritative package-level acceptance record. It changes the package status to **Accepted** without rewriting the independently audited input blobs.

## Exact restart

1. Treat Phase 1 and Phase 2 as frozen controls.
2. Treat `docs/phase3/WITHHELD_CAREGIVER_ACCEPTANCE.md` as the authoritative acceptance status and package-binding record.
3. Preserve exact audited candidate `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c`, its six package-input blobs, and canonical registry digest/bytes.
4. Consult PR #134 and Issues #132/#135/#136 for the acceptance-metadata commit and final merge state; GitHub state outranks stale prose.
5. Do not begin Phase 3 implementation, provider selection, live caregiver integration, schema work, model updates, memory/skill work, or any new runtime capability without a separately accepted implementation scope and explicit project-owner authorization.
6. Any future implementation must have its own ADR package, protected matrix, deterministic controls, current provider/legal/privacy/cost review where applicable, protected CI, and independent implementation audit before freeze.
7. Keep canonical writer categories exactly `organism` and `administration` unless the project owner explicitly authorizes a new design change.
