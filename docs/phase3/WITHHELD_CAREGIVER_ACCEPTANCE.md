# Phase 3 Withheld-Caregiver Evaluation Contract Acceptance

Status: **Accepted design — implementation and live capability remain unauthorized**

Accepted by: project owner

Acceptance date: 2026-08-06

Tracked by: GitHub Issues #132, #135, and #136; PR #134

## 1. Accepted audited candidate

The project owner accepts the Phase 3 withheld-caregiver evaluation design package based on the final independent audit of the following exact candidate:

- repository: `yo4e/sudachi-life`;
- branch: `design/phase3-withheld-caregiver-contract`;
- audited candidate head: `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c`;
- exact base: `6e4aeabbdd25dc8a04dc6118458ef8cb61fe102f`;
- changed range at the audited candidate: seven documentation files only;
- no `src/` or `tests/` change.

The accepted package inputs at that exact audited head are:

- ADR 0017 blob: `72a6b1503f8ec0b6755bda77ecd649b9965cc442`;
- base contract blob: `99fa9bbd061bdee30d4ee10d8315cf0d37cb90d1`;
- base matrix blob: `fb693094431b3f934b7e9eae4c5685324cc4a244`;
- residual amendment blob: `00809bd097238b55d53495a477e2308d271460d1`;
- corrected literal specification blob: `2010516128d355c54c32f8422021abfc8fd58beb`;
- residual handoff blob: `612adb974289e01a5d7c2b8203f7432be6ea5382`;
- audited `docs/HANDOFF.md` blob: `37e479342cfeceed3d868de0d5f91d7c06341939`.

## 2. Canonical effective registry

The final independent bounded read-only verification reconstructed the 140-row effective registry with two independent implementations and obtained the same canonical output:

- row count: `140`;
- amended rows: `14`;
- byte-preserved unamended rows: `126`;
- SHA-256: `12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1`;
- byte length: `43179`;
- serialization: UTF-8, LF only, exact base order, five nonempty cells per row, one final newline;
- requirement-key rule: exactly one leading `REQ:<row-ID>; ` token in cell 2 of every effective row and no other literal `REQ:` occurrence.

The prior diagnostic digest `77ed87159dc40444516a93d0f82041b15c35c9012d90bdc6ebac6e53cd641ff3` at `43154` bytes remains rejected and noncanonical.

## 3. Validation and audit conclusion

Exact-head CI for the audited candidate:

- Test run 689 / workflow run `30640978451`: success;
- protected suite: `395 passed in 93.78s`;
- install, compile, protected-output upload, enforcement, and schema-v1 CLI smoke: success.

Independent final verification:

- local protected suite: `395 passed in 17.39s`;
- original Phase 1 protected subset: `152 passed in 3.32s`;
- all 47 original Phase 1 Python test/helper blobs remained byte-identical;
- accepted Phase 2 matrix/evidence-map sets remained exactly `213/213` and set-equal;
- `P3-D010`: **resolved**;
- final conclusion: **ready to accept after audit metadata synchronization**;
- authoritative audit record: Issue #135 comment `5199730734`.

Across the complete Issue #135 audit chain, the original findings `P3-D001` through `P3-D010` are resolved. The later bounded finding `P3-D011` is also resolved.

## 4. Acceptance semantics

This file is the authoritative package-level acceptance record.

The six audited package-input documents are intentionally preserved byte-for-byte at the accepted candidate head. Their embedded `Proposed` labels record the state in which the exact blobs were independently audited. They are not rewritten after verification because doing so would create different bound inputs and invalidate the published blob identities and audit binding.

For repository interpretation after this acceptance:

- ADR 0017 is an **Accepted design decision** through this manifest;
- the Phase 3 withheld-caregiver evaluation contract is an **Accepted design contract** through this manifest;
- the 140-row Phase 3 effective matrix and its residual/literal specifications are an **Accepted protected design matrix package** through this manifest;
- this acceptance overlay supersedes the pre-acceptance `Proposed` status labels without altering the audited bytes;
- the audited candidate head remains the semantic and cryptographic design-package reference;
- the later acceptance-metadata commit and PR merge commit are administrative wrappers and must be recorded separately in GitHub metadata.

## 5. Frozen and authorization boundaries

Phase 1 and Phase 2 remain frozen. Canonical writer categories remain exactly `organism` and `administration`.

This acceptance does **not** authorize Phase 3 implementation or live capability. It does not authorize code, schemas, migrations, a live human or model caregiver, chat, APIs, network access, subprocesses, arbitrary callables, credentials, memory, skill generation, training, action adoption or execution, provider use, model updates, repeated rollback, continuous execution, personality or emotion state, or resource expansion.

Any implementation or live capability requires separately accepted scope, implementation ADRs, protected matrices and controls, current provider/legal/privacy/cost review where applicable, explicit project-owner authorization, protected CI, and an independent implementation audit before freeze.

## 6. Next authorized action

The acceptance authorizes only administrative completion of the design package:

1. synchronize this acceptance, the canonical registry digest/bytes, CI, audit conclusion, and exact package bindings in `docs/HANDOFF.md`, PR #134, and Issues #132/#135/#136;
2. run protected CI on the acceptance-metadata head;
3. verify that the acceptance-metadata range changes no audited package input, source, test, runtime, schema, authority, or resource boundary;
4. close Issue #136 as completed;
5. mark PR #134 ready and merge it;
6. record the merge commit and leave implementation explicitly unauthorized.
