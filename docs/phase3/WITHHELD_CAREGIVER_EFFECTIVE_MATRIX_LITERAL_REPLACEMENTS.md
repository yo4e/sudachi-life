# Phase 3 Withheld-Caregiver Effective Matrix Literal Replacements

Status: **Proposed normative matrix closure — no implementation or live capability is authorized**

Tracked by: GitHub Issues #132, #135, and #136; draft PR #134

Controls and replaces Sections 7 and 8 of `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1_RESIDUAL_AMENDMENT.md` where they define the effective 140-row matrix projection.

## 1. Fixed inputs

The projection input is exactly:

- base matrix path: `docs/PHASE3_WITHHELD_CAREGIVER_TEST_MATRIX.md`;
- base matrix Git blob: `fb693094431b3f934b7e9eae4c5685324cc4a244`;
- base matrix row count: exactly 140;
- base matrix ordered ID set: exactly the declared `P3-A01` through `P3-L14` section ranges, with no missing, duplicate, unknown, or extra ID;
- literal replacement ID set: exactly `P3-B10`, `P3-D04`, `P3-F06`, `P3-F07`, `P3-F08`, `P3-F09`, `P3-F10`, `P3-G03`, `P3-G04`, `P3-G10`, `P3-J12`, `P3-K14`, `P3-L13`, and `P3-L14`.

Any input-blob, row-count, order, ID-set, header, or five-cell parsing mismatch rejects reconstruction.

## 2. Mechanical substitution algorithm

An independent verifier reconstructs the effective matrix using only the fixed base blob and the literal table in Section 4:

1. Decode the base blob as UTF-8 with LF line endings.
2. Parse only Markdown table rows whose first cell matches the exact ordered 140-ID registry. Each parsed row must contain exactly five cells: `ID`, `Normative clause`, `Protected requirement`, `Fail-closed outcome`, and `Required evidence`.
3. Reject a missing, duplicate, unknown, extra, reordered, empty, or malformed row or cell.
4. For each ID not in the literal replacement set, retain cells 1, 3, 4, and 5 byte-for-byte and replace cell 2 with the exact string `REQ:<ID>; <original cell 2>`.
5. For each ID in the literal replacement set, discard all five base cells and substitute the exact five cells from Section 4.
6. Validate that every effective row contains exactly one `REQ:<row-ID>` token, appearing at the beginning of cell 2, and no other `REQ:` token.
7. Serialize the canonical effective registry as UTF-8, LF only, no trailing spaces, one row per line, final newline present, using exactly:

   `| <cell 1> | <cell 2> | <cell 3> | <cell 4> | <cell 5> |`

8. The canonical registry contains no headings or separator rows and exactly 140 serialized rows in base order.
9. Record the SHA-256 digest and byte length of the canonical effective registry in final acceptance metadata.
10. Final acceptance metadata must bind the exact accepted commit, base-matrix blob, this literal-replacement file blob, residual-amendment blob, generated registry SHA-256 and bytes, protected CI run, bounded-verification conclusion, and Phase 3 handoff blob.

Any alternative overlay, section-level interpretation, row split, in-cell paraphrase, serialization, or generated digest is nonconforming.

## 3. Unamended rows

For the 126 IDs outside the replacement set, the only permitted change is the deterministic `REQ:<row-ID>; ` prefix in cell 2. Cells 1, 3, 4, and 5 remain byte-identical to the fixed base-matrix blob.

## 4. Literal five-cell replacement table

The following 14 rows are complete literal replacements. Every character in all five cells is normative for the effective matrix.

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-B10 | REQ:P3-B10; residual amendment §4; literal closure §4 | Attempt ordinals and episode identities are unique. Attempt lifecycle is exactly nonterminal `scheduled`, then nonterminal `started`, then exactly one immutable terminal outcome from `e0_invalid`, `development_failed`, `rolled_back`, `e2_invalid`, `completed_unsuccessful`, or `completed_successful`. Exact same-ID same-content replay is idempotent. | Remaining `scheduled` or `started` at closure, skipping `started`, backward transition, ordinal reuse, silent abandonment, omission, or a second different terminal outcome rejects the complete study and blocks W3. | Exact lifecycle and terminal enums, legal-transition graph, replay and conflict corpus, rollback linkage, and final population set equality. |
| P3-D04 | REQ:P3-D04; residual amendment §6; literal closure §4 | E1 starts only after every current-attempt caregiving record and conversion, verification, adoption, and activation record is terminal, then the predeclared E1 cutoff is committed. Caregiving records include requests, responses, clarifications, deferrals, abstentions, unresolved packages, queued work, and pending source work. | Any pending caregiving item, nonterminal transition, cutoff-before-terminal order, or post-cutoff caregiving, transition, activation, or model update invalidates E1 with no partial score. | Terminal caregiving-set equality, four-transition terminal-chain proof, pending request, response, package, clarification, deferral, abstention, queued-work cases, and cutoff-order adversarial tests. |
| P3-F06 | REQ:P3-F06; residual amendment §3.1; literal closure §4 | Conversion is an immutable `organism`-written transition from no current-attempt conversion to exactly `produced`, `failed`, or `invalid`. `produced` creates a candidate only and cannot verify, adopt, activate, supersede, deactivate, or create runtime effect. | Wrong writer, missing identity or input, wrong source state, unknown or multiple terminal state, conflicting replay, transaction failure, or any verification, adoption, activation, or runtime side effect rejects with no partial effect. | Exact writer and state enums, identity and input linkage, idempotent replay, conflict, transaction rollback, no-side-effect, and lineage-rollback tests. |
| P3-F07 | REQ:P3-F07; residual amendment §3.2; literal closure §4 | Verification is an immutable `administration`-written transition from one exact `produced` conversion to exactly `passed`, `failed`, or `invalid`, using independently scoped verifier evidence. It cannot mutate the candidate, adopt, activate, supersede, deactivate, or create runtime effect. | Wrong writer, absent or non-produced conversion, evaluator aliasing, unknown or multiple terminal state, conflicting replay, transaction failure, candidate mutation, or downstream/runtime side effect rejects with no partial effect. | Exact writer and state enums, produced-conversion prerequisite, independent verifier evidence, replay and conflict corpus, transaction rollback, candidate immutability, and no-runtime-effect tests. |
| P3-F08 | REQ:P3-F08; residual amendment §3.3; literal closure §4 | Adoption is an immutable `administration`-written transition from one exact `passed` verification to exactly `accepted`, `rejected`, or `invalid`. `accepted` is accepted-but-inactive and creates no runtime effect. `rejected` and `invalid` can never activate. | Wrong writer, absent or non-passed verification, unknown or multiple terminal state, conflicting replay, transaction failure, runtime effect before activation, or activation from rejected or invalid adoption rejects with no partial effect. | Exact writer and state enums, passed-verification prerequisite, accepted-but-inactive proof, rejected and invalid nonactivation, replay and conflict corpus, transaction rollback, and no-runtime-effect tests. |
| P3-F09 | REQ:P3-F09; residual amendment §3.4; literal closure §4 | Activation is an immutable `administration`-written transition from one exact `accepted` adoption and the exact predeclared stable checkpoint to exactly `activated`, `failed`, or `invalid`. Only `activated` may create runtime effect at the destination checkpoint. | Wrong writer, absent accepted adoption, wrong or unstable checkpoint, unknown or multiple terminal state, conflicting replay, transaction failure, runtime effect before committed activation, or effect at another checkpoint rejects with no partial effect. | Exact writer and state enums, accepted-adoption and checkpoint prerequisites, destination-state reconstruction, replay and conflict corpus, transaction rollback, and preactivation no-effect tests. |
| P3-F10 | REQ:P3-F10; residual amendment §3; literal closure §4 | Conversion, verification, adoption, and activation each bind exact study, attempt, episode, organism, lineage, point or cutoff, input and output IDs, payload digest, checkpoints where applicable, and costs. Exact replay is idempotent, same-ID different-content conflicts, and record creation plus canonical effect is one protected transaction. Rollback preserves every record and blocks further current-attempt effect. Supersession and deactivation apply only through separate immutable administration-authored records after activation. | Any missing linkage, wrong order, wrong writer, unknown state, missing prerequisite, conflict, partial transaction, rewritten history, preactivation supersession or deactivation, or post-rollback current-attempt effect rejects the chain and W3. | Four-transition identity reconstruction, writer and order matrix, same and conflicting replay, injected partial failures, rollback preservation, post-rollback exclusion, supersession, and deactivation tests for every transition. |
| P3-G03 | REQ:P3-G03; residual amendment §2; literal closure §4 | Before true terminal attempt status, held-out cases, expected outputs, thresholds, scores, per-case results, outcome-evaluator outputs, and every direct or derived representation are unavailable to the organism, caregiver, converter, conversion verifier, adoption authority, activation authority, and every development recipient. | Any preterminal direct, derived, cached, logged, aliased, or predeclared held-out outcome disclosure invalidates the attempt for W3 before scoring. | Recipient deny-list tests, direct and derivative leakage corpus, conversion-verifier access denial, cache and log probes, and predeclared-leakage adversarial case. |
| P3-G04 | REQ:P3-G04; residual amendment §2; literal closure §4 | The pre-E0 information-flow policy may disclose only independently scoped conversion-verifier outputs and fixed non-outcome operational metadata. It cannot waive held-out denial. Verifier and evaluator inputs, stores, execution paths, outputs, caches, logs, and capability handles are disjoint. Verifier probe and retry limits are exact and every invocation and disclosure is reconciled. | Policy waiver, shared store or path, aliasing, hidden derivative route, undeclared recipient or field, adaptive probe, excess retry, missing invocation, or reconciliation mismatch invalidates the attempt. | Golden policy, disjoint-store and path reconstruction, handle-alias tests, invocation and disclosure ledger equality, derivative-route probes, and retry-budget boundaries. |
| P3-G10 | REQ:P3-G10; residual amendment §2; literal closure §4 | Outcome-evaluator output is disclosed only after one true terminal attempt outcome. It never directly mutates organism state. Preterminal development feedback originates solely from the independently scoped conversion verifier and contains no held-out outcome or derivative. | Early outcome disclosure, terminal-status spoofing, evaluator-driven canonical or runtime mutation, indirect verifier forwarding, or outcome-derived development feedback invalidates the attempt and W3. | Terminal-order guards, output-release transaction tests, direct-mutation absence, verifier-forwarding attack corpus, derivative detection, and immutable disclosure logs. |
| P3-J12 | REQ:P3-J12; residual amendment §4; literal closure §4 | Every scheduled attempt ordinal appears exactly once in the study population and traverses `scheduled` to `started` to exactly one immutable terminal outcome. Only the six declared terminal outcomes satisfy final reconciliation. Negative, invalid, rolled-back, and unsuccessful attempts remain immutable evidence. | Any still-scheduled or still-started attempt, missing or duplicate ordinal, skipped state, multiple terminal outcomes, silent abandonment, deleted negative attempt, post-hoc stopping, or population mismatch rejects the report and W3. | Attempt ledger set and order equality, exact nonterminal and terminal enum tests, transition graph, incomplete-study cases, negative-attempt retention, stopping-rule, replay, and conflict tests. |
| P3-K14 | REQ:P3-K14; residual amendment §5; literal closure §4 | Finalization is exactly Stage 1 immutable reviewed cost-bearing draft, then one external immutable final cost-closure attestation over the draft digest and complete measured vector, then one deterministic bounded non-semantic publication seal. All substantive work through Stage 1 is costed. Closure and seal use pre-E0 fixed non-comparative publication-overhead counters and cannot edit, review, retry, or collect evidence. | Premature closure, late in-scope cost, unmeasured labor, unmatched event, vector mismatch, semantic publication edit, seal retry or bound excess, or reused edited draft or closure invalidates publication and W3 cost completeness. A substantive correction requires a new immutable Stage 1 draft and closure. | Stage ordering and digest linkage, complete vector reconciliation, fixed allowance counters, no-edit and no-review seal inspection, injected seal failure and retry rejection, late-cost cases, and immutable prior-version retention. |
| P3-L13 | REQ:P3-L13; residual amendment §9; literal closure §§1-5 | PR, Issues, residual handoff, and final acceptance metadata identify the exact candidate head, protected CI, bounded audit conclusions, `P3-D001` through `P3-D011` dispositions, Issue #136 D010 closure, unchanged frozen Phase 1 and Phase 2 boundaries, exact package blobs, generated effective-registry digest and bytes, and the next gate. | Any stale, contradictory, missing, moved-head, wrong-CI, wrong-blob, wrong-digest, or implementation-authorizing metadata blocks acceptance and merge processing. | Cross-surface exact-head, CI, finding, blob, generated-digest, frozen-boundary, Draft or Proposed status, and next-action equality checks. |
| P3-L14 | REQ:P3-L14; residual amendment §§6-9; literal closure §§1-5 | The effective registry is reconstructed only from base blob `fb693094431b3f934b7e9eae4c5685324cc4a244` and this literal table by the fixed algorithm. It has exactly 140 rows in exact order, one unique expected ID and exactly one leading requirement-key token per row, five nonempty cells, literal amended rows, byte-preserved unamended cells, exact fourteen-group draft and closure-seal gates, E1 all-caregiving-terminal gate, protected-suite integrity, and no novelty overclaim. | Any input-blob drift, alternative overlay, row or cell paraphrase, missing, duplicate, extra, reordered or empty row, wrong requirement-key token, canonical serialization or digest mismatch, report or suite set mismatch, E1 gate failure, or novelty overclaim blocks acceptance. | Independent base-blob parser, literal substitution, canonical serializer, exact ID, order, cell, and requirement-key equality, generated SHA-256 and byte-length reproduction, package-blob binding, report and closure envelope equality, E1 pending-work corpus, protected-suite integrity, and novelty-language audit. |

## 5. Accepted-package binding

The final accepted package must include and bind exact Git blobs for:

- proposed ADR 0017;
- the base contract;
- base matrix blob `fb693094431b3f934b7e9eae4c5685324cc4a244`;
- the residual amendment;
- this literal replacement specification;
- the Phase 3 residual handoff;
- the exact accepted commit.

It must also record the independently reproduced canonical effective-registry SHA-256 digest and byte length. A later edit to any bound input creates a new candidate and requires regeneration, protected CI, and the applicable independent audit gate.

## 6. Scope

This document is a documentation and evidence-map closure only. It changes no Phase 1 or Phase 2 behavior, writer authority, rollback rule, budget, resource ceiling, schema, provider permission, runtime capability, or implementation authorization. All Phase 3 documents remain Proposed until the remaining gate is independently satisfied and the project owner records final acceptance.
