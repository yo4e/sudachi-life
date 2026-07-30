# Phase 3 Withheld-Caregiver Residual Handoff

Updated: **2026-07-30**

Status: **Proposed design amendment; no implementation or live capability is authorized**

This appendix supersedes the Phase 3 status and exact-restart portions of `docs/HANDOFF.md` until the base handoff is consolidated after satisfactory bounded verification.

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
- focused independent re-audit: independent `395 passed`, Phase 1 `152 passed`, 47/47 Phase 1 blobs unchanged, 90/90 frozen Phase 2 test/helper blobs unchanged, 213/213 Phase 2 IDs exact;
- conclusion: **ready after specified documentation or matrix corrections**.

The focused re-audit marked `P3-D001`, `P3-D002`, `P3-D003`, `P3-D004`, and `P3-D007` resolved. It left bounded residuals in `P3-D005`, `P3-D006`, `P3-D008`, `P3-D009`, and `P3-D010`, and added `P3-D011`.

## Residual amendment

`docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1_RESIDUAL_AMENDMENT.md` is the controlling proposed amendment for the bounded residuals. It adds:

- absolute preterminal held-out outcome denial including the conversion verifier, with disjoint verifier/evaluator stores, paths, caches, outputs, and capability handles;
- exact per-transition writers and source/terminal/replay/conflict/no-partial-effect/supersession/deactivation/rollback semantics;
- exact attempt graph `scheduled → started → one terminal outcome`, with `scheduled` and `started` nonterminal;
- two-stage reviewed-draft / external closure / one mechanical seal finalization;
- exact 140-key atomic registry and deterministic `REQ:<row-ID>` effective matrix projection;
- exact accepted-package blob binding;
- an E1 gate requiring all current-attempt caregiving records and all four transitions terminal before cutoff.

The amendment changes no frozen Phase 1/2 behavior and authorizes no runtime implementation.

## Current candidate

- branch: `design/phase3-withheld-caregiver-contract`;
- residual-amendment commit: `febbe3da8020595752f3e1fc9c91f79e05273e65`;
- base remains: `6e4aeabbdd25dc8a04dc6118458ef8cb61fe102f`;
- PR #134 remains Draft and unmerged;
- ADR 0017, base contract, base matrix, residual amendment, and this appendix remain Proposed;
- ordinary protected CI for the final appendix-synchronized head is pending.

## Exact restart

1. Reconstruct frozen Phase 1/2 from `AGENTS.md`, `docs/HANDOFF.md`, PR #119, and Issue #127.
2. Read both Issue #135 audits.
3. Read proposed ADR 0017, the base contract, the base 140-ID matrix, the residual amendment, and this appendix.
4. Confirm PR #134 is Draft/unmerged and all Phase 3 documents remain Proposed.
5. Synchronize Issue #135 and PR #134 to the final appendix-synchronized exact head and ordinary CI result.
6. Run one independent bounded read-only verification limited to:
   - absolute held-out outcome denial and disjoint data paths;
   - all four transition semantics;
   - exact attempt state graph and terminal subset;
   - acyclic finalization;
   - exact 140-key/`REQ:`/blob binding;
   - E1 all-caregiving-terminal gate.
7. Do not perform a new broad redesign unless bounded verification finds a material contradiction.
8. Do not change Proposed to Accepted, merge PR #134, or begin implementation before satisfactory bounded verification and final project-owner acceptance.
9. Design acceptance still does not authorize implementation.
