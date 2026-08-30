# Phase 3 Deterministic Fixture Foundation — Implementation Evidence Map

Status: **Implementation-package evidence map; not yet frozen**

Scope: Issue #145 / ADR 0018

Accepted design binding:

- audited Phase 3 design candidate: `c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c`;
- canonical effective-registry SHA-256: `12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1`;
- canonical effective-registry byte length: `43179`;
- exact atomic design-key count: `140`.

## Purpose

This map states what the first fixture-only implementation proves, what remains inherited from the frozen Phase 1/2 controls, and what is deliberately not introduced. It is a traceability map, not a claim that every future live-capability implementation is complete.

The implementation is additive under `src/sudachi_life/phase3/`; it does not alter the Phase 1/2 organism runtime, schemas, budgets, checkpoint mechanics, rollback implementation, or writer categories.

## Exact 140-key ownership map

The accepted residual amendment defines these groups as the entire atomic key set. Every key is owned by exactly one row below.

| Accepted keys | Count | Fixture-foundation evidence | Status in this package |
|---|---:|---|---|
| `P3-A01`–`P3-A10` | 10 | immutable episode binding; exact contract/registry constants; frozen-boundary absence tests | implemented + inherited frozen controls |
| `P3-B01`–`P3-B10` | 10 | study manifest, exact attempt ordinal set, `scheduled → started → terminal` history, closure reconciliation | implemented |
| `P3-C01`–`P3-C10` | 10 | immutable protected schedule, W0/W1/W2 classifier, administration-authored W0→W1 fixture transition | implemented for deterministic fixture path |
| `P3-D01`–`P3-D12` | 12 | exact ordered E0/E1/E2 points, E0 validity, E1 terminal caregiving/transition gate, E2 pre-score integrity | implemented for deterministic fixture path |
| `P3-E01`–`P3-E14` | 14 | typed per-capability results, acquisition baseline, E1 pass, E2 retention, protected-capability preservation | implemented for deterministic fixture path |
| `P3-F01`–`P3-F12` | 12 | separate conversion/verification/adoption/activation records with residual-amendment writers/status/order/checkpoints | implemented as immutable evidence validation + pure idempotent/conflict replay; persistent storage transaction remains future work |
| `P3-G01`–`P3-G10` | 10 | verifier/evaluator identity separation, disjoint stores/paths/caches evidence, zero preterminal leakage, invocation reconciliation | implemented as deterministic protected evidence |
| `P3-H01`–`P3-H12` | 12 | exhaustive declared substrate fields, independently reconstructed fixture digest/size checks, W1/W2 permission, technical caregiver-disablement proof | implemented for closed fixture substrate surface |
| `P3-I01`–`P3-I10` | 10 | negative attempt states and population visibility; failed/rolled-back attempts cannot receive W3; frozen ADR 0007 runtime remains authoritative | implemented evidence shape + inherited rollback control; no new rollback capability |
| `P3-J01`–`P3-J12` | 12 | closed mandatory cost vector, measured/not-applicable/unmeasured semantics, monotonic cumulative accounting and status stability | implemented for fixture accounting |
| `P3-K01`–`P3-K14` | 14 | exact semantically bound 14-group reviewed draft, external closure attestation, one bounded no-retry/no-edit seal | implemented for deterministic report package |
| `P3-L01`–`P3-L14` | 14 | exact 140-ID generator, canonical registry constants, design-manifest binding, existing full protected CI, explicit no-overclaim | implemented + inherited CI/design-package controls |
| **Total** | **140** | | |

This table covers every accepted key exactly once by range cardinality: `10+10+10+12+14+12+10+12+10+12+14+14 = 140`.

## Residual-amendment hot rows

The audit-corrected rows receive direct implementation coverage:

| Accepted row(s) | Required residual behavior | Protected evidence |
|---|---|---|
| `P3-B10`, `P3-J12` | exact attempt graph, current-attempt ordinal binding, successful-W3 terminal state, and incomplete-population rejection | attempt graph, ordinal-binding, and failed-terminal tests; study validator |
| `P3-D04` | all caregiving records and all four transitions terminal before E1 | `test_nonterminal_caregiving_blocks_e1_and_w3`; cutoff/order validation |
| `P3-F06`–`P3-F10` | exact transition writers, distinct identities, terminal states, order, prerequisites, checkpoints, idempotent exact replay and same-ID conflict | transition validator; writer/distinct-ID tests; immutable replay test |
| `P3-G03`, `P3-G04`, `P3-G10` | absolute held-out deny-list, verifier/evaluator separation, disjoint execution domains, terminal-only disclosure | `test_heldout_leakage_invalidates_w3`; information-flow validator |
| `P3-K14` | reviewed draft → external closure → one bounded mechanical seal; no retry/edit; report semantics remain bound after digest recomputation | report semantic-binding test; publication-seal test; closure/seal validator |
| `P3-L13`, `P3-L14` | exact accepted registry binding, exact key count, protected-suite/frozen-boundary evidence, no novelty overclaim | design-binding tests, 140-ID test, existing workflow, ADR 0018 |

## Implementation-specific protected requirements

| ID | Requirement | Fail-closed result | Evidence |
|---|---|---|---|
| `P3IF-01` | Phase 3 package has no live external runtime route and no SQLite/Phase1/Phase2 runtime coupling | test failure / no candidate freeze | `test_phase3_explicit_absence.py` |
| `P3IF-02` | writer categories remain exactly `organism` and `administration` | conformance/CI failure | `test_canonical_writer_categories_remain_exactly_two` |
| `P3IF-03` | positive fixture is exact W1 at E2 and W3 is not a point class | conformance failure | positive fixture + availability-axis tests |
| `P3IF-04` | E2 caregiver route is technically unavailable, not merely unused | E2 invalid before retention | disablement validator + nonzero-route test |
| `P3IF-05` | every fixture caregiving record is terminal before cutoff and comes only from deterministic fixture | E1/W3 invalid | caregiving validator + nonterminal test |
| `P3IF-06` | four transitions are separate, distinctly identified, and ordered with exact writers/statuses | W3 invalid | transition validator + writer/distinct-ID tests |
| `P3IF-07` | caregiver-derived W1 substrate has complete current-episode provenance and digest/size reconstructed from the closed fixture payload registry | E2 invalid | substrate validator + permission/size/digest tests |
| `P3IF-08` | W2 classification contains no runtime-visible externalized caregiver-derived scaffold | classification/integrity failure | availability classifier + W2 unit path |
| `P3IF-09` | held-out evaluator remains isolated from development recipients | W3 invalid | information-flow validator + leakage test |
| `P3IF-10` | acquisition requires valid E0 negative status and E1 pass; retention requires E2 pass with clean conformance; raw strings cannot masquerade as typed success states | no retained-capability credit | capability validator + positive fixture + raw-status test |
| `P3IF-11` | capabilities protected at E0 cannot silently regress | W3 invalid | protected-regression test |
| `P3IF-12` | study population has exact planned ordinals, current-attempt ordinal binding, terminal state history, and a successful W3 terminal outcome | study/W3 invalid | study validator + attempt graph/ordinal/failed-terminal tests |
| `P3IF-13` | mandatory cost `unmeasured` is distinct from measured zero and blocks final completeness | cost/W3 invalid | unmeasured-cost test |
| `P3IF-14` | measured cumulative cost cannot decrease or regress to an incompatible status | cost/W3 invalid | cost monotonic validator + measured-to-unmeasured test |
| `P3IF-15` | Stage-1 draft has exactly fourteen groups in accepted order and is semantically reconstructed from episode evidence | report/W3 invalid | exact-group + semantic-binding tests |
| `P3IF-16` | closure binds draft and final vector after Stage 1 | W3 invalid | closure validator |
| `P3IF-17` | publication seal is one bounded non-semantic operation, zero retry/edit | publication/W3 invalid | seal test |
| `P3IF-18` | accepted 140-key set and registry digest/byte constants remain exact | CI failure | design-binding and 140-ID tests |
| `P3IF-19` | deterministic fixture report cannot claim maturity/developmental effectiveness/novelty, even if report/closure/seal digests are recomputed consistently | package invalid for fixture scope | report semantic-binding test + positive report limitations + ADR 0018 |

## 2026-08-30 bounded self-audit hardening

A risk-scoped implementation review of PR #146 found that broad repository-history reconstruction was unnecessary to expose several fail-closed gaps. The candidate was hardened before independent audit to reject:

- failed or rolled-back current attempts receiving W3 conformance;
- current-attempt ordinal drift from the immutable episode binding;
- four transition kinds sharing one transition identity;
- self-attested substrate digest/size metadata that does not match the closed deterministic fixture payload corpus;
- semantically altered fourteen-group reports whose draft/closure/seal hashes were recomputed consistently;
- cumulative measured cost reverting to `unmeasured` or another incompatible status;
- raw string values masquerading as accepted `StrEnum` states.

Protected test count after these code repairs, before this documentation synchronization: **427 passed in 51.76s**, GitHub Actions Test run **703** / workflow run `33259558065`.

This self-audit is not the independent freeze audit because the reviewer participated in implementation. It is pre-audit hardening evidence only.

## 2026-08-30 independent-audit repair pass

Issue #147 independently audited exact candidate `8c14d6acaa76c5c523ff42e48e7498b6c1b24b2a` and concluded **not ready to freeze; specified implementation repairs required**. The accepted repair scope comprised the four independent-audit findings plus two bounded residuals recovered from the earlier incomplete Codex audit. The source/test repair commit is `003cf4fe40f8d2355dc81acb67169a8cc9ea1341`; GitHub Actions Test run **708** / workflow run `33288494461` passed **438 tests in 59.64s** before this documentation synchronization.

The repaired implementation strengthens only protected Phase 3 evidence and tests:

- **Study preregistration / `P3-B01`, `P3IF-12`:** the fixture-relevant `StudyManifest` now carries and validates manifest version, study purpose, deterministic run-generation rule, stopping/count rule, attempt-assignment rule, full-population reconciliation rule, mandatory failure controls, comparison-family scope, exact cost-policy identity, and a pre-E0 publication policy. Post-hoc cost-policy or study-purpose mutation fails closed.
- **Information flow / `P3-G01`, `P3-G03`–`P3-G05`, `P3-G10`, `P3IF-09`:** a digest-bound `InformationFlowPolicy` fixes verifier/evaluator identities, disjoint store/path/cache domains, allowed feedback fields/recipients/timing/cardinality, and probe/retry budgets. Immutable invocation records carry exact identity, role, input/output digests, recipients, disclosures, held-out access, derivative-leak, targeting, probe, and retry evidence. The validator reconstructs and reconciles this ledger to the final verifier/evaluator cost counters; summary booleans are no longer sufficient evidence.
- **Publication finalization / `P3-K14`, `P3IF-17`:** a pre-E0 `PublicationPolicy` fixes the only allowed closure/seal operation and its byte/operation limits. Closure and seal byte usage is reconstructed from deterministic serialized payloads and checked against the fixed policy, with zero retry/edit semantics preserved.
- **Point and nested identity / `P3-B01`, `P3-B04`, `P3-D03`, `P3-D12`:** E0 must use the exact baseline checkpoint. Nested capability results, cost vectors, point integrity evidence, disablement, information-flow evidence, reviewed draft, closure, and seal bind an exact `EvidenceIdentity`; foreign episode, lineage, point, cutoff, or checkpoint evidence fails closed.
- **Version provenance / `P3-L13`, `P3-L14`:** repository provenance must be an exact 40- or 64-hex commit identifier. The report also projects study-manifest, information-flow-policy, and publication-policy digests.

Protected adversarial coverage now includes post-hoc study/cost-policy mutation, information-flow policy and invocation-ledger mutation, undeclared recipients, publication-policy and byte-counter mutation, foreign E0/nested identities, and invalid repository commit provenance.

These repairs do **not** change the research purpose, frozen Phase 1/2 behavior, canonical writer categories, live/external capability boundary, or resource scope. PR #146 still compares to `main` as exactly the same 12 additive Phase 3 files.

This repair pass is implementation work, not an independent re-audit. A fresh reviewer must audit the final documentation-synchronized exact candidate before freeze/merge.

## Deliberately absent capabilities

The package contains no implementation of:

- live human caregiver or free-form chat;
- hosted/local model caregiver;
- network or subprocess caregiver transport;
- credentials or provider selection;
- arbitrary callable or executable caregiver output;
- memory/skill generation as a new organism capability;
- training, distillation, or model-weight update;
- live proposal/action adoption or execution;
- a second rollback mechanism;
- continuous execution;
- new writer categories;
- budget/resource expansion.

Those absences are scope controls, not missing functionality to be filled opportunistically.

## Freeze evidence still required

Before this implementation package can be declared frozen:

1. pass ordinary GitHub Actions with the complete pre-existing protected suite plus the new Phase 3 tests at the final synchronized head;
2. verify Phase 1 original protected blobs and Phase 2 accepted evidence remain intact through the existing controls;
3. record one exact candidate head and CI run;
4. obtain one independent read-only implementation audit using Issue #147's bounded, risk-scoped audit packet;
5. repair any accepted independent-audit findings without weakening the contract or tests;
6. synchronize this map, `docs/HANDOFF.md`, Issue #145, and the PR before freeze/merge completion.
