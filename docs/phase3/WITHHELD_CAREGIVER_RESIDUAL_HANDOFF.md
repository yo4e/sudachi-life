# Phase 3 Withheld-Caregiver Residual Handoff

Updated: **2026-07-31**

Status: **Proposed design amendment; no implementation or live capability is authorized**

This appendix supersedes the Phase 3 status and exact-restart portions of `docs/HANDOFF.md` until the base handoff is consolidated after satisfactory bounded verification and final design acceptance.

## Frozen controls

Phase 1 and Phase 2 remain frozen.

- Phase 1 control: `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`; 152 original tests; 47 original Python test/helper blobs.
- Phase 2 freeze: PR #119 merge `b0941a8ba2a178fc891839198cd5dd5bf6e87719`; 395 protected tests; exactly 213 accepted/evidence-map IDs.
- Canonical writer categories remain exactly `organism` and `administration`.
- ADR 0007 one-completed-rollback limit, budgets, resource ceilings, schemas, selectors, executors, evaluators, checkpoints, and explicit capability absence remain unchanged.

No live caregiver, model API, human chat, network, subprocess, memory, skill creation/adoption, action adoption, training, continuous loop, new writer category, repeated rollback, resource expansion, personality, or emotion state is authorized.

## Audit history

Original candidate:

- PR #134 head: `932ff2ad8d99e8d9fb2e78a16cd12a5f1e8995c9`;
- CI run 680: success, `395 passed in 55.27s`;
- Issue #135 conclusion: **not ready; material design revision required**;
- findings: `P3-D001` through `P3-D010`.

First corrected candidate:

- PR #134 head: `646459f0e9afac2bfa576ff8a0630dd4291dead4`;
- CI run 684: success, `395 passed in 65.08s`, compile/upload/schema-v1 smoke success;
- focused independent re-audit conclusion: **ready after specified documentation or matrix corrections**.

Residual-amendment candidate:

- PR #134 head: `4eb9e4816e067df8ae3a4fb6ca6c5b550646f12f`;
- CI run 686: success, `395 passed in 53.63s`, compile/upload/schema-v1 smoke success;
- bounded independent verification resolved `P3-D005`, `P3-D006`, `P3-D008`, `P3-D009`, and `P3-D011`;
- `P3-D010` remained partially resolved because the effective 140-row matrix could not be reconstructed as one unique row/cell artifact;
- conclusion: **ready after specified documentation or matrix corrections**.

## D010 literal closure

Issue #136 owns the sole remaining bounded correction.

`docs/phase3/WITHHELD_CAREGIVER_EFFECTIVE_MATRIX_LITERAL_REPLACEMENTS.md` controls the effective-matrix projection where it conflicts with Sections 7 and 8 of the residual amendment. It fixes:

- base matrix Git blob `fb693094431b3f934b7e9eae4c5685324cc4a244`;
- exact 140-row count, ordered ID set, five-cell parser, and canonical serialization;
- deterministic `REQ:<row-ID>; ` prefixing for all 126 unamended rows while preserving their other cells byte-for-byte;
- complete literal five-cell replacements for the 14 amended rows;
- exactly one leading `REQ:<row-ID>` token per effective row;
- canonical UTF-8/LF 140-row registry output, SHA-256 digest, and byte length;
- exact accepted-package binding for the base matrix, residual amendment, literal replacement specification, handoff, accepted commit, CI, and bounded verification.

The literal replacement document changes no research purpose, Phase 1/2 behavior, writer authority, runtime capability, provider, schema, budget, or resource ceiling.

## Current proposed package

PR #134 contains proposed documentation only:

- ADR 0017;
- base withheld-caregiver contract;
- base 140-ID matrix;
- residual amendment;
- D010 literal replacement specification;
- this residual handoff;
- existing base handoff synchronization.

PR #134 remains Draft and unmerged. All Phase 3 documents remain Proposed.

## Exact restart

1. Reconstruct frozen Phase 1/2 from `AGENTS.md`, `docs/HANDOFF.md`, PR #119, and Issue #127.
2. Read Issue #135 audit history and Issue #136.
3. Read proposed ADR 0017, the base contract, base matrix, residual amendment, D010 literal replacement specification, and this appendix.
4. Confirm PR #134 is Draft/unmerged and all Phase 3 documents remain Proposed.
5. Bind the final D010 candidate to one exact branch head and protected CI result in Issue #135 and PR #134.
6. Run one independent bounded read-only verification limited to `P3-D010`:
   - exact base blob;
   - exact 140-row count, set, and order;
   - 14 literal five-cell replacements;
   - byte-preserved unamended cells;
   - exactly one leading `REQ:<row-ID>` per row;
   - canonical serialization and independently reproduced SHA-256/byte length;
   - accepted-package blob-binding requirements.
7. Do not reopen resolved `P3-D005`, `P3-D006`, `P3-D008`, `P3-D009`, or `P3-D011` unless the D010 specification introduces a concrete contradiction.
8. Do not change Proposed to Accepted, merge PR #134, close Issue #136 as completed, or begin implementation before satisfactory D010 verification and final project-owner acceptance.
9. Design acceptance still does not authorize implementation.
