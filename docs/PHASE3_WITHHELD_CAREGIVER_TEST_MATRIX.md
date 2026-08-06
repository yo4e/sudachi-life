# Phase 3 Withheld-Caregiver Evaluation Test Matrix

Status: **Proposed design evidence map — audit corrections applied; no Phase 3 implementation or live capability exists**

Tracked by: GitHub Issues #132 and #135

Normative candidates:

- proposed ADR 0017;
- `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1.md`.

The unchanged frozen Phase 1 and Phase 2 protected suites are always the first regression layers. This matrix preserves the original 140 proposed IDs while correcting the semantics identified by the independent Issue #135 audit.

Every row has one unique ID, an exact normative clause/reference key, a protected requirement, an explicit fail-closed outcome, and required protected evidence. A later implementation must protect exact matrix-ID uniqueness, normative-clause coverage, exact fourteen-group report equality, complete suite collection, no-skip and assertion integrity, and frozen test/helper blob identity.

This matrix does not authorize code, schema, live caregiver access, learning, memory, skills, action adoption, model calls, training, network/subprocess access, or new writer authority.

## A. Frozen controls and explicit absence

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-A01 | §2; §17 | All 152 original Phase 1 tests retain byte-identical test/helper blobs, complete collection, no skips, unchanged assertions, and pass. | Any blob, collection, skip, assertion, or result mismatch rejects the Phase 3 candidate. | Original-suite run, blob fingerprints, collection manifest, skip/assertion guards. |
| P3-A02 | §2; §17 | The complete frozen Phase 2 suite, test/helper blobs, collection, no-skip behavior, assertions, and exactly 213 accepted evidence IDs remain unchanged and passing. | Any suite/blob/collection/skip/assertion or 213-ID set mismatch rejects the candidate. | Complete Phase 2 run, blob fingerprints, collection manifest, matrix/evidence-map set equality. |
| P3-A03 | §2 | Phase 1/2 schemas, actions, selector, executor, evaluators, clocks, checkpoints, rollback, writer categories, budgets, and ceilings are not reinterpreted. | Any semantic or fingerprint drift rejects the candidate before Phase 3 evidence. | Protected fingerprints and cross-version controls. |
| P3-A04 | §2; §8; §10 | Canonical writer categories remain exactly `organism` and `administration`. | Any additional or missing canonical writer category rejects. | Schema/source/runtime inspection and exact enum equality. |
| P3-A05 | §8; §9; §10; §11 | Caregiver, adapter, model, evaluator, verifier, custodian, and maintainer never become canonical writers. | Any forged or inferred authority rejects before mutation. | Forged-authority corpus and transaction inspection. |
| P3-A06 | §2; §18 | Contract acceptance creates no live caregiver, API, chat, network, subprocess, memory, skill, training, action-adoption, loop, or generic-agent route. | Any new callable/import/CLI/runtime route rejects acceptance. | Import, API, CLI, source, and runtime absence guards. |
| P3-A07 | §2; §5.3; §13 | ADR 0007 one-completed-rollback limit remains exact. | Repeated completed rollback or altered lineage semantics rejects. | Existing rollback suite plus Phase 3 design assertions. |
| P3-A08 | §2; §18 | Existing physical ceilings and budget locations remain exact. | Any budget relocation or ceiling increase rejects. | Protected configuration and resource fingerprint checks. |
| P3-A09 | §3; §17 | Unknown Phase 3 versions, states, or undeclared normative fields fail before canonical mutation. | Unknown input is rejected with no partial effect. | Version/state adversarial corpus. |
| P3-A10 | §1; §18 | No implementation-specific schema, transport, provider, artifact type, training method, evaluator implementation, or runtime path is silently selected. | A private implementation choice blocks acceptance. | Documentation/source audit against explicit exclusions and open questions. |

## B. Study, attempt, episode, and lineage identity

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-B01 | §5.1; §5.2 | Study and episode identities contain the exact contract, study, attempt, organism, lineage, schema, base-contract, environment, suite, evaluator, verifier, information-flow, schedule, protected configuration, baseline checkpoint, caregiver/substrate condition, and seed fields. | Any missing, extra, renamed, or mutable identity field rejects. | Independent golden identity construction and exact field-set equality. |
| P3-B02 | §5.2 | Episode identity excludes later result IDs, wall time, mutable status, and undeclared fields. | Any prohibited field changes identity or rejects parsing. | Exact exclusion and one-field mutation tests. |
| P3-B03 | §5.4 | E0, E1, and E2 share exact study ID, attempt ID, episode ID, organism, lineage, environment, suite, held-out evaluator, verifier, information-flow policy, protected schedule, protected configuration, and substrate baseline. | Any shared-identity mismatch rejects the comparison. | Three-point manifest equality. |
| P3-B04 | §5.2; §5.4; §6 | Point checkpoints are point-specific and bind exact study, attempt, episode, organism, lineage, point, and cutoff. | Wrong, stale, or unlinked checkpoint rejects the point. | Stable-checkpoint linkage and reconstruction. |
| P3-B05 | §5.2; §5.3 | No evidence or comparison crosses organism IDs. | Cross-organism substitution rejects. | Cross-organism mutation corpus. |
| P3-B06 | §5.3 | No evidence or comparison crosses lineage generations. | Old-lineage evidence rejects and remains preserved. | Rollback and stale-lineage corpus. |
| P3-B07 | §5.3; §13 | Rollback ends the episode and attempt without success and requires a new assigned attempt and E0 in the new lineage. | Post-rollback continuation or success reuse rejects. | Full rollback episode scenario. |
| P3-B08 | §5.3; §13 | Abandoned-lineage evidence remains immutable and cannot satisfy a later lineage. | Mutation, deletion, or substitution rejects. | Archive reconstruction and evidence-laundering corpus. |
| P3-B09 | §5.4 | Only the predeclared schedule transition may change point availability in one episode; any other environment, suite, evaluator, authority, budget, or configuration change invalidates or creates a new episode. | Unplanned mutation rejects the episode. | Scheduled-transition positive case and one-field mutation corpus. |
| P3-B10 | §5.1; §5.2; §13 | Attempt ordinals and episode identities are unique; exact replay is idempotent and conflicting replay fails. | Ordinal reuse, duplicate-content conflict, or silent abandonment rejects. | Duplicate, conflict, population, and replay tests. |

## C. Availability axis and W3 certification

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-C01 | §4.1 | Every evaluation point declares exactly one of mutually exclusive W0, W1, or W2; W3 is not a point class. | Zero, multiple, or W3-as-point classification rejects. | Exact enum/cardinality validation. |
| P3-C02 | §4.1; §12 | W0 means at least one caregiver route remains technically available even when call count is zero. | Available-but-unused cannot be reported as independence. | Available-zero-call control. |
| P3-C03 | §4.1; §8 | W1 requires every live caregiver route unavailable and at least one declared externalized caregiver-derived substrate active/readable/executable/callable. | Missing route proof or missing scaffold declaration rejects W1. | Prompt, skill, demonstration, router, and tool controls. |
| P3-C04 | §4.1; §8; §10.5 | W2 requires every caregiver route and externalized caregiver-derived scaffold unavailable; any retained model state is fully declared and eligible. | Any externalized scaffold, opaque update, or live route rejects W2. | Zero-scaffold, internalized-update, and empty-caregiver-derived controls. |
| P3-C05 | §4.2 | W3 is an episode-level certification that preserves the exact E2 W1 or W2 subtype. | W3 without subtype or reported as an availability class rejects. | Complete synthetic W1+W3 and W2+W3 scenarios. |
| P3-C06 | §4.1; §16 | W0 results use intervention-aided language only. | Independence or maturity wording under W0 rejects report conformance. | Report-schema negative cases. |
| P3-C07 | §4.1; §16 | W1 results may claim live-source independence but not externalized-scaffold absence. | Scaffold-free wording under W1 rejects. | Report-schema negative cases. |
| P3-C08 | §4.1; §4.2; §16 | W2 may report externalized-scaffold-free policy performance but not W3 maturity without complete certification. | Maturity wording without W3 rejects. | Report-schema negative cases. |
| P3-C09 | §4.1; §5.4 | A point-local W class is immutable after the point begins; only the predeclared inter-point transition is legal. | Post-start reclassification or unplanned transition rejects. | Immutable point manifest and transition corpus. |
| P3-C10 | §4.2; §17 | Any mandatory identity, transition, evaluator, integrity, attempt-population, or cost failure prevents W3 certification. | Partial or degraded W3 classification rejects. | Table-driven W3 failure corpus. |

## D. E0, E1, E2, and acquisition validity

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-D01 | §6 | Every episode contains exactly one ordered E0, E1, and E2 after attempt registration. | Missing, duplicate, unordered, or pre-registration point rejects. | Cardinality and event-order assertions. |
| P3-D02 | §6.1; §7.1 | E0 occurs before current-episode caregiving, conversion, adoption, or activation. | Any prior current-episode developmental event invalidates E0. | Event-window proof. |
| P3-D03 | §6.1 | E0 records complete cases/results, protected outcomes, substrate declaration, W class, checkpoint, costs, and integrity/reachability/completeness status. | Missing field or incomplete case reconciliation makes E0 acquisition-ineligible. | Exact manifest and suite-case set equality. |
| P3-D04 | §6.2; §10 | E1 starts only after all four current-episode lifecycle transitions are terminal and the protected cutoff is committed. | Pending or post-cutoff transition invalidates E1. | Cutoff and terminal-chain proof. |
| P3-D05 | §6.2 | E1 records exact active substrates/updates, complete declaration, results, protected outcomes, cumulative costs, and stable checkpoint. | Missing or mismatched E1 evidence rejects retention. | Exact linkage reconstruction. |
| P3-D06 | §5.4; §6.3; §12 | E2 begins only after the predeclared availability transition reaches its exact destination checkpoint. | Unscheduled, wrong-writer, wrong-checkpoint, or incomplete transition invalidates E2. | Transition and checkpoint proof. |
| P3-D07 | §5.4; §6.3; §11 | E2 reuses exact held-out suite/evaluator identity and preserves sequestration. | Evaluator/suite drift or leakage invalidates E2. | Digest equality, role separation, and leakage guards. |
| P3-D08 | §6.3 | E2 verifies channel unavailability, pending-work absence, substrate integrity, identity, and evaluator sequestration before scoring. | Any failed precondition stops scoring with typed integrity result. | Call-order guards and failure injection. |
| P3-D09 | §6.3 | An E2 integrity failure produces no capability score or partial W3 result and remains in study population. | Any partial score or omitted invalid attempt rejects. | No-score/no-partial-result and population reconciliation. |
| P3-D10 | §6.2; §6.3 | No post-E1 caregiving, conversion, verification, adoption, activation, model update, or queued work affects E2. | Post-cutoff contribution invalidates E2. | Cutoff and pending-work adversarial corpus. |
| P3-D11 | §5.4; §6 | Injected wall-time movement cannot change point order, cutoff eligibility, or schedule state. | Wall-time-sensitive eligibility rejects. | Backward/forward injected-time tests. |
| P3-D12 | §6; §7 | Each point binds one stable checkpoint, exact runtime state, complete case set, and valid point integrity. | Unstable, incomplete, or unreachable point rejects claim analysis. | Checkpoint reconstruction and complete-point gate. |

## E. Runtime substrate and hidden scaffold

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-E01 | §8 | Every dependency available to the organism or evaluator-facing scoring path is declared. | Any undeclared dependency invalidates E2 before scoring. | Source/runtime inventory and guarded dependency enumeration. |
| P3-E02 | §8 | Supported classes include weights, prompts, memory, skills, code, rules, tests, traces, demonstrations, recovery suffixes, routers, tools, fixtures, environment, evaluators, verifier, runtime, cache, and typed other. | Unknown or collapsed class rejects. | Exact enum tests. |
| P3-E03 | §8 | Each entry contains exact ID/class/version, canonical digest, separate canonical/measured sizes, active/executable/readable/callable flags, non-writer custodian, origin, provenance, four transition IDs, full identity linkage, W permission, and capability dependency. | Missing/extra/misnamed field or authority substitution invalidates declaration. | Golden entry and exact field-set corpus. |
| P3-E04 | §8 | An empty substrate class requires independent proof of absence. | Unproved emptiness invalidates E2. | Absence guard and malicious hidden object. |
| P3-E05 | §5.2; §8; §9 | Caregiver-derived entries link only to exact current-episode caregiving events after valid E0 and before E1 cutoff. | Missing, inherited, cross-episode, or out-of-window provenance rejects acquisition/W3. | Provenance-window and replay corpus. |
| P3-E06 | §8; §10 | Every active caregiver-derived entry links to one complete accepted conversion-verification-adoption-activation chain. | Orphan, partial, duplicate, or rejected chain invalidates active substrate. | Lifecycle-chain reconstruction. |
| P3-E07 | §8; §10.5 | Runtime bytes, canonical/measured size, and declared digest match exactly, including model state. | One-byte, size, or identity mismatch invalidates E2. | Independent byte/digest measurement and mutation corpus. |
| P3-E08 | §8 | Used runtime dependencies cannot be declared inactive, unreadable, unexecutable, uncallable, or unnecessary. | Use/declaration contradiction invalidates E2. | Instrumented-use contradiction tests. |
| P3-E09 | §8 | Undeclared prompt, memory, skill, demonstration, trace, router, tool, code, cache, alternate model, or recovery suffix is hidden scaffold. | Detection stops scoring and preserves integrity evidence. | Hidden-scaffold corpus. |
| P3-E10 | §8 | Caregiver-derived content mislabeled as organism-derived, environment, or protected infrastructure invalidates E2. | Origin forgery rejects. | Origin-forgery corpus. |
| P3-E11 | §8; §11 | Episode caregiving cannot modify evaluator, verifier, cases, schedule, or environment semantics. | Caregiver-derived protected-infrastructure contamination invalidates attempt. | Contamination tests. |
| P3-E12 | §8; §12 | Dynamic retrieval or cache access from undeclared stores invalidates E2 before scoring. | Any successful hidden retrieval stops scoring. | Guarded retrieval/cache probes. |
| P3-E13 | §6.3; §8; §10.5 | Any silent model or artifact update after E1 or without exact identity/transition evidence invalidates E2. | Digest/event mismatch rejects, never downgrades to unknown. | Digest, event-cutoff, and opaque-update tests. |
| P3-E14 | §8; §13; §16 | Hidden-scaffold failure evidence remains immutable and appears in population/report reconciliation. | Suppression, deletion, or omission rejects report. | Immutable integrity record and export reconstruction. |

## F. Caregiving and four lifecycle transitions

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-F01 | §5.2; §9 | Every caregiving record binds full identity, typed class, content digest/size, provenance, clarification, confidence/abstention, latency/cost, and terminal outcome. | Missing identity or evidence field rejects the chain. | Exact caregiving-record reconstruction. |
| P3-F02 | §9 | Assistance classes represent demonstration, correction, constraint, explanation, preference, question, defer, and abstain. | Unknown class rejects. | Exact enum tests. |
| P3-F03 | §9 | Terminal outcomes include accepted, rejected, deferred, clarification requested, misleading/inconsistent detected, unrepresentable, expired, and invalid. | Missing, multiple, or unknown terminal state rejects. | Exact enum/cardinality tests. |
| P3-F04 | §9; §10 | Caregiver identity/content remains untrusted provenance and never verifies, adopts, or activates. | Self-certification or caregiver authority rejects before effect. | Forged-authority tests. |
| P3-F05 | §8; §10 | Every active caregiver-derived substrate has exactly one complete current-episode four-transition chain. | Missing, partial, duplicate, inherited, or conflicting chain rejects. | Chain set equality and replay corpus. |
| P3-F06 | §10.1 | Conversion is an immutable candidate-producing transition with exact source events, method, candidate identity/digest/size, writer, inputs/outputs, cost, and status. | Conversion cannot activate or certify; malformed conversion rejects. | Golden conversion object and no-effect tests. |
| P3-F07 | §10.2; §11 | Verification is a separate immutable transition using the distinct conversion verifier, bounded disclosures, probe/retry ordinal, cost, and status. | Verifier alias, budget excess, or verification-as-adoption rejects. | Golden verification and role/budget tests. |
| P3-F08 | §10.3 | Adoption is a separate immutable disposition with authorized canonical writer, accepted/rejected/invalid status, reason, cost, and accepted-but-inactive state. | Unauthorized, self-approved, or auto-active adoption rejects. | Golden adoption and authority tests. |
| P3-F09 | §10.4 | Activation is a separate immutable checkpoint transition requiring accepted adoption, authorized writer, exact checkpoint, active identity, cost, and lifecycle status. | Wrong order/writer/checkpoint, rejected candidate, or partial effect rejects. | Golden activation and transaction-failure corpus. |
| P3-F10 | §10.4 | Exact replay is idempotent; conflicting replay, partial failure, supersession, deactivation, and rollback preserve immutable prior records. | Conflict or partial runtime effect rejects. | Replay/conflict/failure/supersession tests. |
| P3-F11 | §10.5 | Model updates require exact base/result identities/digests, method/data class, compute/storage, verification, and all four transitions. | Any missing mandatory evidence makes update unsupported and ineligible before scoring. | Synthetic declared and opaque-update corpus. |
| P3-F12 | §10.5; §18 | Technical conformance never infers provider permission, legal transformation rights, or authorization to train. | Permission claim without separate accepted review rejects report/scope. | Documentation and report guards. |

## G. Verifier, held-out evaluator, information flow, and authority

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-G01 | §5.1; §11 | Suite, held-out outcome evaluator, conversion verifier, and information-flow policy are fixed and digest-bound before E0. | Late creation or identity drift invalidates attempt. | Pre-E0 manifest and digest guards. |
| P3-G02 | §11 | Verifier and held-out evaluator have distinct non-aliased identities and execution roles. | Aliasing invalidates W3. | Object/process/identity alias tests. |
| P3-G03 | §11 | Held-out cases, expected outputs, scores, thresholds, and per-case results remain sequestered until terminal status except predeclared feedback. | Case or result leakage invalidates attempt. | Leakage corpus and access logs. |
| P3-G04 | §11 | The pre-E0 policy fixes disclosed fields, recipients, timing, and verifier probe/retry cardinality. | Undeclared disclosure or adaptive probing invalidates attempt. | Golden policy and disclosure reconciliation. |
| P3-G05 | §11 | Every verifier/evaluator call, probe, retry, disclosed field, and recipient is logged and reconciled. | Missing or excess invocation/disclosure invalidates attempt. | Invocation ledger set equality. |
| P3-G06 | §11 | Organism and caregiver cannot write, replace, configure, weaken, reweight, select, suppress, or authorize verifier/evaluator/suite/schedule/cost rules. | Any such capability or mutation rejects. | API/source/runtime absence and mutation corpus. |
| P3-G07 | §11 | Protected administration records evidence but cannot privately redefine fixed semantics or exceed policy budgets. | Semantic drift or unauthorized feedback invalidates attempt. | Version/digest and budget validation. |
| P3-G08 | §10; §11 | Caregiver output never certifies correctness, adoption, or activation. | Self-approval rejects before canonical/runtime effect. | Self-certification corpus. |
| P3-G09 | §5.4; §11 | Evaluator, verifier, suite, information-flow, or schedule version change creates a new episode or invalidates the current one. | In-place amendment rejects comparison. | Version-fork tests. |
| P3-G10 | §11 | Evaluator output does not directly mutate organism state, and outcome feedback appears only after terminal attempt status. | Direct mutation or early outcome feedback invalidates attempt. | Transaction, access-order, and authority inspection. |

## H. Capability, claims, population, and reporting

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-H01 | §6; §7 | Results are per capability and reconcile every required suite case; aggregate-only evidence is insufficient. | Missing capability/case evidence rejects claim. | Per-capability and case-set equality. |
| P3-H02 | §7 | Result statuses are exactly passed, failed, abstained, not reached, or invalid. | Unknown or collapsed status rejects. | Exact enum tests. |
| P3-H03 | §5.2; §7 | Each result binds full study/attempt/episode/organism/lineage/point/checkpoint identity, suite/evaluator versions, scenario, ordered evidence, resources, and protected outcomes. | Missing or cross-boundary linkage rejects. | Golden result and mutation corpus. |
| P3-H04 | §6.1; §7.1 | Acquisition requires valid complete E0 with exactly eligible negative status, E1 pass, and a complete current-episode post-E0/pre-cutoff lifecycle chain. | Invalid/not-reached/infrastructure/hidden-fallback/unplanned-abstention or inherited evidence rejects acquisition. | Eligible and excluded E0 status matrix. |
| P3-H05 | §7.2; §15 | Retention requires E1/E2 pass under exact suite/evaluator identity, valid E2/W3 integrity, and complete final cost closure. | Any missing condition rejects retention. | Three-point retention scenario. |
| P3-H06 | §7.2 | Every protected E0 capability satisfies its predeclared E1/E2 expectation. | Unapproved regression rejects W3. | Protected regression corpus. |
| P3-H07 | §7.2; §11 | No post-hoc case exclusion, threshold change, reweighting, evaluator substitution, or favorable filtering is accepted. | Observed-outcome targeting invalidates attempt/report. | Manifest/report mutation corpus. |
| P3-H08 | §7.1; §7.2 | Abstention counts as eligible/pass only when the suite predeclares that exact semantics before E0. | Unplanned abstention rejects acquisition/pass. | Expected/unexpected abstention cases. |
| P3-H09 | §7.1 | Timeout, tool/service failure, unavailable caregiver, hidden fallback, or refusal cannot masquerade as competence. | Misclassification rejects point validity. | Failure-classification tests. |
| P3-H10 | §14; §16 | Claim language is tiered: deterministic conformance, W3 maturity, and scientific comparative claim each require exact evidence. | Overclaiming beyond registered tier rejects report. | Report-language and claim-tier validation. |
| P3-H11 | §5.1; §13; §16 | Reports reconcile every scheduled/started attempt, unsuccessful episode, rollback, and abandoned lineage under the predeclared stopping rule. | Omission, ordinal reuse, or post-hoc stopping rejects. | Study-population set equality. |
| P3-H12 | §16; §17 | Every W3 report contains exactly the fourteen required top-level evidence groups and exact repository/contract/matrix/study/suite/verifier/evaluator/schedule/evidence-map versions. | Missing, extra, renamed, merged, or silently omitted group rejects report. | Exact 14-group schema and set-equality test. |

## I. Protected schedule and caregiver disablement

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-I01 | §5.4; §12 | The pre-E0 protected schedule fixes the sole legal E2 transition, before/after values, writer `administration`, and source/destination checkpoints. | Unregistered or incomplete schedule rejects the episode. | Golden schedule identity. |
| P3-I02 | §5.4; §12 | Only `administration` may execute the scheduled transition at the exact source checkpoint. | Wrong writer or checkpoint rejects with no partial effect. | Authority/checkpoint adversarial tests. |
| P3-I03 | §5.4; §12 | Exact duplicate transition replay is idempotent; conflicting replay fails and preserves state. | Conflict or double effect rejects. | Replay/conflict tests. |
| P3-I04 | §6.3; §12 | No live adapter handle, dispatch, bridge, model call, chat, network, subprocess, or human intervention is callable after cutoff. | Any usable route invalidates E2 before scoring. | Capability guards, source inspection, and event reconciliation. |
| P3-I05 | §6.3; §12 | No alternate/fallback route, unresolved response, cached live output, queued package, or stale proposal is usable during E2. | Any pending/alternate path invalidates E2. | Pending-work and alternate-path probes. |
| P3-I06 | §12; §15 | Caregiver events and caregiver costs remain exactly zero after cutoff while verification/evaluation costs remain separately measured. | Post-cutoff caregiver event/cost invalidates E2; hidden local cost invalidates closure. | Ledger/event reconstruction. |
| P3-I07 | §5.4; §6.3; §12 | Disablement reaches the exact destination checkpoint before E2 and remains checkpoint-stable. | Unstable or stale state invalidates E2. | Active/checkpoint equality. |
| P3-I08 | §12 | An independent validator reconstructs schedule execution, route absence, events, costs, substrates, and pending-work absence. | Unreconstructable proof invalidates E2. | Separate validator/harness. |
| P3-I09 | §4.1; §12 | Choosing not to invoke an available route remains W0. | Zero calls alone cannot classify W1/W2. | Available-zero-call control. |
| P3-I10 | §6.3 | Disablement failure produces typed integrity evidence, no capability score, and no partial W3 claim. | Any score or omitted failure rejects. | Pre-score failure injection. |

## J. Failure controls, rollback, and study stopping

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-J01 | §14 | Misleading assistance has a predeclared detection/rejection or harm expectation. | Post-hoc omission or favorable recoding rejects W3 maturity claim. | Deterministic misleading fixture. |
| P3-J02 | §14 | Inconsistent assistance remains as contradictory evidence and cannot be collapsed. | Suppression or favorable merge rejects. | Contradiction corpus. |
| P3-J03 | §14 | Correct but unrepresentable assistance terminates as unrepresentable without silent coercion. | Coercion or hidden adoption rejects. | Representation-boundary fixture. |
| P3-J04 | §9; §14 | Ambiguous assistance receives typed clarification or terminal rejection under predeclared policy. | Silent interpretation or unlogged retry rejects. | Ambiguity and clarification fixture. |
| P3-J05 | §5.1; §14 | Premature withdrawal and dependency collapse are registered conditions in the run-generation rule. | Unregistered or omitted condition blocks maturity/comparative claim. | Scheduled cutoff scenarios. |
| P3-J06 | §4.1; §14 | Delayed withdrawal remains W0 while any route is available and cannot count as maturity. | Misclassification rejects report. | W0 dependency control. |
| P3-J07 | §8; §14 | Hidden-scaffold injection is a typed integrity failure before scoring. | Any score or omission rejects. | Prompt/skill/router/tool/cache injection corpus. |
| P3-J08 | §5.2; §8; §14 | Stale, inherited, wrong-episode, or wrong-lineage substrate reuse rejects before scoring/acquisition. | Reuse invalidates chain and remains evidence. | Cross-episode/lineage replay tests. |
| P3-J09 | §11; §14 | Evaluator targeting, case leakage, result leakage, verifier aliasing, or probe-budget excess invalidates W3. | Adaptive oracle use rejects attempt. | Protected-evaluator attack corpus. |
| P3-J10 | §5.3; §13; §14 | Rollback after harmful activation preserves all transitions and ends episode/attempt without success. | Erasure or continued success path rejects. | Full rollback evidence scenario. |
| P3-J11 | §5.1; §5.3; §13 | A new lineage receives a new registered attempt/E0 and cannot inherit success, conversion, or cost evidence. | Inherited claim evidence rejects. | Fresh-attempt reconstruction. |
| P3-J12 | §5.1; §13; §16 | Every scheduled/started attempt has a terminal status and reconciles to the fixed count/stopping rule; negative attempts cannot be deleted. | Population mismatch, silent abandonment, or post-hoc stopping rejects report. | Attempt ledger and exact population reconciliation. |

## K. Complete cost ledger and final closure

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-K01 | §15 | Every cost field status is exactly measured, not applicable, or unmeasured; unknown is never zero. | Unknown/zero conflation or unknown status rejects. | Exact enum and zero/unknown controls. |
| P3-K02 | §15 | W3 cost completeness rejects every mandatory unmeasured field. | Any mandatory unmeasured field prevents W3. | Field-by-field missing corpus. |
| P3-K03 | §15 | Not-applicable fields require a protected typed reason. | Missing/invalid reason rejects completeness. | Reason validation. |
| P3-K04 | §15 | Caregiver, monitoring, intervention, artifact review, maintenance, experimenter development, evaluator operation, integrity investigation, report preparation, and report review labor use integer milliseconds. | Visible but unmeasured labor invalidates closure. | Boundary/unit and activity-mapping tests. |
| P3-K05 | §15 | Consultation, demonstration, correction, clarification, abstention, rejection, transition, and failure counts reconcile with event history. | Count/event mismatch invalidates closure. | Independent ledger reconstruction. |
| P3-K06 | §15 | Model/service calls, tokens, latency, retries, failures, money, provider/product/model/version, and retained-data class reconcile with evidence. | Missing or unmatched service cost invalidates closure. | Synthetic provider ledger corpus. |
| P3-K07 | §15 | Environment interactions, resets, failed attempts, evaluator/verifier/fixture calls, administrative operations, and wall-duration metadata are exact. | Counter mismatch invalidates closure. | Harness counter equality. |
| P3-K08 | §10.5; §15 | Training/inference CPU and accelerator time use declared integer units/device classes, including eligible model updates. | Missing compute evidence makes update unsupported or closure incomplete. | Synthetic compute accounting. |
| P3-K09 | §8; §15 | Working set, active state, checkpoint store, caregiver-derived/total substrate, retained artifact/log/evidence, and report-package bytes are independently measured. | Byte mismatch or unmeasured mandatory storage invalidates closure. | Filesystem/database reconciliation. |
| P3-K10 | §15 | Development, review, maintenance, investigation, evaluator, and reporting work are visible and mapped exhaustively. | Unmapped labor invalidates closure. | Protected external-work records and mapping equality. |
| P3-K11 | §15; §16 | Reports expose the complete cost vector and final closure identity without scalar collapse. | Omitted dimensions or silent scalarization rejects report. | Report-schema validation. |
| P3-K12 | §15; §18 | No scalar maturity score exists unless a later pre-E0 accepted ADR fixes formula, weights, units, and missing-data behavior. | Unaccepted scalar score rejects. | API/documentation absence guard. |
| P3-K13 | §15 | Reduced caregiver burden cannot be claimed when any displaced local cost is mandatory-unmeasured or unreconciled. | Comparative burden claim rejects. | Displaced-cost report corpus. |
| P3-K14 | §5.2; §15 | One immutable final closure after all E2, integrity, retries, storage, packaging, and report review binds exact identities and reconciles every vector; late cost creates a new closure version. | Premature closure, late in-scope cost, unmatched event, or vector mismatch invalidates W3. | Closure cutoff, late-cost, versioning, and vector-reconciliation tests. |

## L. Controls, clause coverage, audit, and gates

| ID | Normative clause | Protected requirement | Fail-closed outcome | Required evidence |
| --- | --- | --- | --- | --- |
| P3-L01 | §14; §17 | No-caregiver deterministic control exists before live capability work. | Missing control blocks implementation authorization and maturity claims. | Deterministic empty-caregiver scenario. |
| P3-L02 | §14; §17 | Deterministic-fixture control exists before live capability work. | Missing fixture blocks conformance acceptance. | Exact fixture scenario. |
| P3-L03 | §4; §17 | Synthetic W0, W1+W3, and W2+W3 declarations exercise the orthogonal classification model without live sources. | Old W0-W3 single-axis harness or missing subtype blocks acceptance. | Table-driven conformance harness. |
| P3-L04 | §8; §11; §12; §13; §15 | Hidden scaffold, wrong episode/lineage, evaluator leakage, schedule conflict, incomplete cost, and rollback controls are mandatory. | Missing negative control blocks acceptance. | Complete negative-control set. |
| P3-L05 | §5.1; §14 | A scientific comparative claim uses a pre-E0 registered comparison family and count/stopping rule where applicable. | Unregistered comparison or post-hoc stopping rejects scientific claim. | Study manifest and experiment matrix. |
| P3-L06 | §14; §17 | Deterministic conformance may precede research experiments but cannot claim developmental gain or maturity. | Overclaiming rejects report. | Claim-tier scope guard. |
| P3-L07 | §17; §19 | Proposed ADR, contract, and matrix receive an independent focused re-audit against one exact CI-green corrected head. | Self-review or stale-head audit cannot satisfy gate. | Issue #135 exact-head audit evidence. |
| P3-L08 | §17 | Every Issue #135 finding P3-D001 through P3-D010 has an explicit correction/disposition and focused re-audit verdict. | Missing finding disposition blocks acceptance. | Finding-to-clause/matrix reconciliation. |
| P3-L09 | §17 | Documentation corrections, project-owner confirmation, and CI precede any status change to Accepted. | Premature status change rejects release gate. | Git history and metadata assertions. |
| P3-L10 | §17; §18 | Contract acceptance remains separate from implementation authorization. | Runtime implementation or capability inference from acceptance rejects scope. | ADR/contract exclusion checks. |
| P3-L11 | §2; §18 | Every future capability requires separate scope/ADRs, protected matrix, current legal/provider review where applicable, owner authorization, and implementation audit. | Missing later gate blocks capability. | Later-phase checklist. |
| P3-L12 | §18 | Open schema, transport, artifact, model-update permission, evaluator implementation, experiment count, provider/legal, hardware, rollback, and scalar choices are not privately decided in code. | Private choice blocks implementation/acceptance. | Source inspection and design audit. |
| P3-L13 | §17 | Handoff, PR, and Issues identify exact corrected head, CI, audit status, findings, unchanged frozen boundaries, and next gate. | Stale or contradictory metadata blocks acceptance. | Durable continuity and exact-head check. |
| P3-L14 | §16; §17 | Matrix IDs are unique; every normative clause/reference is covered; exact 14 report groups and complete protected-suite integrity have set-equality gates; no public novelty claim is made. | Any ID/clause/report/suite set mismatch or novelty overclaim blocks acceptance. | Independent matrix parser, report-schema equality, suite integrity, and repository text audit. |

## Acceptance rule

This proposed matrix and contract may move to Accepted only after:

1. all 140 IDs are unique and the exact expected ID set is present;
2. every normative contract clause and the exact fourteen report groups have protected set-equality coverage;
3. complete Phase 1/2 collection, no-skip, assertion, result, evidence-ID, and test/helper blob integrity passes;
4. every Issue #135 finding P3-D001 through P3-D010 has a documented correction;
5. one exact corrected candidate passes ordinary protected CI;
6. one independent focused read-only re-audit reaches an explicit acceptance conclusion on that exact head;
7. the project owner confirms the evaluator/information-flow redesign and final acceptance;
8. exact commit, CI, audit, status, and next-gate metadata are synchronized.

Acceptance still does not authorize Phase 3 runtime implementation.
