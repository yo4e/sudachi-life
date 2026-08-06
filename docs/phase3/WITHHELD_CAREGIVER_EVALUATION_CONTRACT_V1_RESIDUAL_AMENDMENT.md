# Phase 3 Withheld-Caregiver Evaluation Contract v1 — Residual Audit Amendment

Status: **Proposed normative amendment — no implementation or live capability is authorized**

Tracked by: GitHub Issues #132 and #135; draft PR #134

Amends:

- proposed ADR 0017;
- `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1.md`;
- `docs/PHASE3_WITHHELD_CAREGIVER_TEST_MATRIX.md`.

## 1. Purpose and precedence

Issue #135 independently re-audited exact head `646459f0e9afac2bfa576ff8a0630dd4291dead4` and concluded **ready after specified documentation or matrix corrections**. It left bounded residuals in `P3-D005`, `P3-D006`, `P3-D008`, `P3-D009`, and `P3-D010`, and added `P3-D011`.

This amendment is normative for those residuals. Where it conflicts with proposed ADR 0017, the base contract, or the base matrix, this amendment controls. Unamended clauses remain Proposed and unchanged. The effective proposed package is the base ADR, base contract, base matrix, and this amendment together.

This amendment changes no Phase 1/2 source, test, schema, authority, budget, resource ceiling, rollback rule, or runtime capability.

## 2. Absolute held-out outcome isolation — closes P3-D005

Before E0, protected administration fixes distinct digest-bound identities and disjoint access-control domains for:

- the conversion verifier and its independently scoped verifier inputs/outputs;
- the held-out outcome evaluator, held-out cases, expected outputs, thresholds, scores, per-case results, and derivatives;
- verifier and evaluator input stores, execution paths, output stores, caches, logs, and capability handles;
- the information-flow policy and verifier probe/retry budget.

Before the attempt reaches a true terminal outcome:

1. the only permitted development feedback is conversion-verifier output derived solely from independently scoped verifier inputs, plus non-outcome operational metadata fixed before E0;
2. the organism, caregiver, converter, **conversion verifier**, adoption authority, activation authority, and every other development recipient are prohibited from accessing held-out cases, expectations, thresholds, scores, per-case results, outcome-evaluator output, or any direct or derived representation of them;
3. no pre-E0 policy may waive, narrow, relabel, or route around that prohibition;
4. verifier and evaluator stores, paths, caches, outputs, and capability handles must be disjoint and independently reconstructed;
5. every probe, retry, input/output digest, disclosure, derivative, recipient, and invocation is logged and reconciled.

Predeclared outcome leakage, indirect verifier access, shared store/path/cache, aliasing, derivative leakage, adaptive probing beyond budget, retry exhaustion, or evaluator-targeted artifacts invalidates the attempt for W3 before scoring. Outcome-evaluator output is disclosed only after terminal attempt status and never directly mutates organism state.

## 3. Exact four-transition semantics — closes P3-D006

Canonical writer categories remain exactly `organism` and `administration`.

Every transition binds exact study, attempt, episode, organism, lineage, point/cutoff, input IDs, output IDs, payload digest, source checkpoint, destination checkpoint where applicable, and cost evidence.

For **each transition separately**:

- exact same-ID/same-content replay is idempotent and returns the original result;
- same-ID/different-content or a second incompatible terminal result is conflict;
- record creation and any canonical effect are one protected transaction with no partial effect on failure;
- unknown state, wrong writer, wrong order, missing prerequisite, conflict, or transaction failure rejects before runtime effect;
- rollback preserves the record, prevents further current-attempt effect, and links the abandoned future under ADR 0007;
- supersession/deactivation is allowed only where stated below.

### 3.1 Conversion

- permitted canonical writer: exactly `organism`;
- source state: no current-attempt conversion for the ID;
- terminal states: exactly `produced`, `failed`, or `invalid`;
- `produced` creates a candidate only and never verifies, adopts, activates, supersedes, or deactivates;
- supersession/deactivation: not applicable to the conversion record.

### 3.2 Verification

- permitted canonical writer: exactly `administration`;
- source state: one exact `produced` conversion;
- terminal states: exactly `passed`, `failed`, or `invalid`;
- verification records independently scoped evidence only and cannot adopt, activate, supersede, deactivate, or mutate the candidate;
- supersession/deactivation: not applicable.

### 3.3 Adoption

- permitted canonical writer: exactly `administration`;
- source state: one exact `passed` verification;
- terminal states: exactly `accepted`, `rejected`, or `invalid`;
- `accepted` is explicitly accepted-but-inactive and creates no runtime effect;
- `rejected` and `invalid` can never activate;
- supersession/deactivation: not applicable before activation.

### 3.4 Activation

- permitted canonical writer: exactly `administration`;
- source state: one exact `accepted` adoption and the exact predeclared stable checkpoint;
- terminal states: exactly `activated`, `failed`, or `invalid`;
- only `activated` may create runtime effect at the destination checkpoint;
- separate immutable administration-authored lifecycle records may later mark an activated substrate `superseded`, `deactivated`, or `rolled_back`; they never rewrite activation history.

## 4. Attempt lifecycle and population closure — closes P3-D008 and P3-D011

Attempt lifecycle/current states are exactly:

- `scheduled`;
- `started`.

They are **nonterminal** and never satisfy final population reconciliation.

Attempt terminal outcomes are exactly:

- `e0_invalid`;
- `development_failed`;
- `rolled_back`;
- `e2_invalid`;
- `completed_unsuccessful`;
- `completed_successful`.

The only legal state graph is:

> `scheduled → started → exactly one terminal outcome`

Every scheduled ordinal must traverse that graph. A terminal outcome is immutable; exact replay is idempotent and a different second terminal outcome conflicts. Backward transition, skipping `started`, remaining `scheduled` or `started` at study closure, silent abandonment, omission, ordinal reuse, post-hoc stopping, or population mismatch invalidates the complete study and blocks W3 reporting.

Rollback records terminal outcome `rolled_back`, preserves the abandoned future, and requires a new attempt/E0 in the new lineage where ADR 0007 permits.

## 5. Acyclic cost and report finalization — closes P3-D009

Finalization is exactly two stages.

### Stage 1 — immutable reviewed cost-bearing draft

All scheduled attempts, E2, integrity handling, verifier/evaluator retries, storage measurement, evidence packaging, report preparation, and human/protected review complete. The immutable reviewed draft contains the exact fourteen report groups except the external final-closure attestation and publication seal. All substantive work through Stage 1 is included in the developmental cost vector.

### Stage 2 — external closure and one mechanical seal

Protected administration creates one immutable final cost-closure attestation over the reviewed-draft digest and complete measured vector. A pre-E0 policy fixes the only allowed post-cutoff operation: one deterministic, bounded, non-semantic serialization/digest/link step that publishes the unchanged reviewed draft, closure attestation, and seal.

The seal performs no editing, interpretation, human review, retry, or evidence collection. Closure generation and the one seal operation use pre-E0 fixed maximum byte/operation allowances and separately reported non-comparative publication-overhead counters; they are not used in caregiver-burden or developmental-efficiency comparisons.

If the seal fails, exceeds its fixed bound, needs retry, or reveals a semantic/report defect, publication fails closed. Substantive work returns to a new Stage-1 draft and new closure. Prior drafts and closures remain immutable evidence. No existing draft or closure may be edited.

Premature closure, unallowed post-cutoff work, late in-scope cost, unmeasured labor, unmatched event, vector mismatch, semantic publication edit, or seal retry invalidates W3 cost completeness.

## 6. E1 caregiving gate — closes the concrete P3-D010 drift

E1 begins only after **every current-attempt caregiving record** and all four transitions are terminal, then the predeclared E1 cutoff is committed.

Caregiving records include requests, responses, clarifications, deferrals, abstentions, unresolved packages, queued/pending source work, and every other current-attempt caregiver item. A pending request/response/package, nonterminal transition, cutoff-before-terminal ordering, or post-cutoff caregiving/transition/model update invalidates E1 with no partial score.

## 7. Atomic 140-key registry and effective matrix projection — closes P3-D010

The base matrix's existing 140 row IDs are the exact canonical atomic requirement keys. Range notation below means every zero-padded integer in the inclusive range and no other ID:

- `P3-A01`–`P3-A10`;
- `P3-B01`–`P3-B10`;
- `P3-C01`–`P3-C10`;
- `P3-D01`–`P3-D12`;
- `P3-E01`–`P3-E14`;
- `P3-F01`–`P3-F12`;
- `P3-G01`–`P3-G10`;
- `P3-H01`–`P3-H12`;
- `P3-I01`–`P3-I10`;
- `P3-J01`–`P3-J12`;
- `P3-K01`–`P3-K14`;
- `P3-L01`–`P3-L14`.

The set contains exactly 140 unique keys.

The effective matrix is deterministically reconstructed as follows:

1. for every base row, prepend `REQ:<row-ID>; ` to the existing `Normative clause` cell;
2. the row's `Protected requirement` plus `Fail-closed outcome` is the canonical atomic normative text;
3. each row must retain one nonempty protected-evidence field;
4. replace the effective semantics of `P3-B10`, `P3-D04`, `P3-F06`–`P3-F10`, `P3-G03`, `P3-G04`, `P3-G10`, `P3-J12`, `P3-K14`, `P3-L13`, and `P3-L14` with Sections 2–6 and 8 of this amendment;
5. any unknown, missing, duplicate, extra, or empty key/row rejects;
6. acceptance metadata binds exact repository commit and Git blob identities for ADR 0017, the base contract, base matrix, this amendment, and the Phase 3 handoff appendix;
7. any normative edit or blob/version mismatch creates a new candidate requiring registry equality, protected CI, and the applicable audit gate.

Broad section labels alone cannot satisfy clause coverage. Exact 140-key equality, accepted-package blob equality, exact fourteen-group draft equality, one closure/seal envelope, complete protected-suite integrity, and the E1 caregiving gate require independent protected evidence.

## 8. Effective replacement requirements

The effective requirements for the specifically amended rows are:

- `P3-B10` / `P3-J12`: exact nonterminal/terminal enums, legal state graph, immutable terminal result, incomplete-population rejection, replay/conflict and abandonment tests;
- `P3-D04`: all caregiving records and all four transitions terminal before E1, with pending request/response/package and cutoff-order adversarial cases;
- `P3-F06`–`P3-F10`: each transition's exact writer, source/terminal states, idempotence, conflict, transaction/no-partial-effect behavior, supersession/deactivation applicability, and rollback tests;
- `P3-G03`, `P3-G04`, `P3-G10`: absolute preterminal held-out outcome deny-list including the conversion verifier, disjoint paths/stores/caches, derivative-leakage and predeclared-leakage tests, and terminal-only outcome disclosure;
- `P3-K14`: two-stage reviewed-draft/closure/seal finalization, fixed seal allowance/counters, no retry/edit, and new-version behavior;
- `P3-L13`: exact residual-correction head, CI, audit conclusion, residual/P3-D011 status, frozen-boundary status, and next gate across PR/Issues/handoff appendix;
- `P3-L14`: exact 140-key/`REQ:` reconstruction, accepted-package blobs, exact report/closure/seal structure, E1 caregiving gate, protected-suite integrity, and no novelty overclaim.

## 9. Acceptance and next gate

This amendment remains Proposed. The effective package may move toward acceptance only after:

1. one exact amendment candidate passes the complete protected CI;
2. Issue #135 is synchronized to that exact head and CI;
3. one independent bounded read-only verification checks only the residual corrections in this amendment;
4. any surviving bounded defect is repaired and reverified;
5. final project-owner acceptance and exact metadata are recorded.

Acceptance still does not authorize Phase 3 implementation or live capability.

## 10. Explicit exclusions

This amendment does not authorize code, schema, migration, live caregiver, human chat, model/API call, network, subprocess, arbitrary callable, credentials, training, memory, skill creation/adoption, action adoption/execution, new writer category, repeated rollback, resource expansion, continuous execution, personality/emotion state, provider permission, or public novelty claim.
