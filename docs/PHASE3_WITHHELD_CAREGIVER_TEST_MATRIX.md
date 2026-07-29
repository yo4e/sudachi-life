# Phase 3 Withheld-Caregiver Evaluation Test Matrix

Status: **Proposed design evidence map; no Phase 3 implementation or live capability exists**

Tracked by: GitHub Issue #132

Normative candidates:

- proposed ADR 0017;
- `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1.md`.

The unchanged frozen Phase 1 and Phase 2 protected suites are always the first regression layers.

This matrix defines evidence required before a future implementation or scientific claim can be accepted. It does not authorize code, schema, live caregiver access, learning, memory, skills, action adoption, model calls, or new writer authority.

## A. Frozen controls and explicit absence

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-A01 | All 152 original Phase 1 tests remain byte-unchanged and passing | Original suite, blob fingerprint, no skip or assertion change |
| P3-A02 | All frozen Phase 2 protected tests and exactly 213 accepted evidence IDs remain unchanged and passing | Complete Phase 2 suite, matrix/evidence-map set equality |
| P3-A03 | Phase 1 and Phase 2 schemas, actions, selector, executor, evaluators, clocks, checkpoints, rollback, writer categories, budgets, and resource ceilings are not reinterpreted | Protected fingerprints and cross-version controls |
| P3-A04 | Canonical writer categories remain exactly `organism` and `administration` | Schema/source/runtime inspection |
| P3-A05 | Caregiver, adapter, model, evaluator, and maintainer never become canonical writer categories | Forged-authority rejection corpus |
| P3-A06 | Proposed contract acceptance does not create a live caregiver, API, chat, network, subprocess, memory, skill, training, action-adoption, continuous-loop, or generic-agent route | Import/API/CLI/source/runtime absence guards |
| P3-A07 | ADR 0007 one-completed-rollback limit remains exact | Existing rollback suite plus Phase 3 design assertions |
| P3-A08 | Existing physical ceilings and budget locations remain exact | Protected budget/configuration fingerprints |
| P3-A09 | Unknown Phase 3 design versions fail future conformance before canonical mutation | Version-adversarial design corpus |
| P3-A10 | No implementation-specific schema or transport is silently selected by the design contract | Documentation audit against open questions and exclusions |

## B. Developmental episode identity

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-B01 | Episode identity contains exactly contract, organism, lineage, schema, environment, suite, evaluator, protected configuration, baseline checkpoint, caregiver condition, substrate condition, and declared deterministic case/seed fields | Independent golden identity construction |
| P3-B02 | Episode identity excludes later result IDs, wall time, mutable status, and undeclared fields | Exact exclusion tests |
| P3-B03 | E0, E1, and E2 share exact organism, lineage, environment, suite, evaluator, protected configuration, and substrate-baseline identities | Three-point manifest equality |
| P3-B04 | Checkpoint IDs are point-specific and linked to the exact episode and lineage | Stable-checkpoint linkage tests |
| P3-B05 | No comparison crosses organism IDs | Cross-organism evidence substitution rejection |
| P3-B06 | No comparison crosses lineage generations | Old-lineage result and substrate rejection |
| P3-B07 | Rollback ends the current episode without success and requires a new episode/E0 in the new lineage | Full rollback episode scenario |
| P3-B08 | Abandoned-lineage evidence remains immutable and cannot satisfy the new lineage | Mutation and evidence-laundering corpus |
| P3-B09 | Any environment, suite, evaluator, authority, budget, or configuration version change creates a different episode | One-field mutation corpus |
| P3-B10 | Duplicate or conflicting episode identities fail closed | Idempotent duplicate and conflict tests |

## C. Assistance-availability taxonomy

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-C01 | Every evaluation point declares exactly one of W0, W1, W2, or W3 | Exact enum/cardinality validation |
| P3-C02 | W0 means the caregiver route remains technically available even when call count is zero | Available-but-unused control |
| P3-C03 | W1 requires live source absence and at least one declared caregiver-derived runtime substrate | Prompt/skill/demonstration controls |
| P3-C04 | W2 requires caregiver-route and temporary-scaffold absence, permitting only explicitly declared internalized policy/model updates | Zero-skill/empty-scaffold synthetic control |
| P3-C05 | W3 requires all identity, conversion, hidden-scaffold, evaluator, rollback, cost, and retention invariants | Complete synthetic W3 conformance scenario |
| P3-C06 | A W0 result cannot be reported as independence | Report-schema rejection |
| P3-C07 | A W1 result cannot be reported as scaffold-free | Report-schema rejection |
| P3-C08 | A W2 result cannot be reported as protected artifact-lineage maturity without W3 evidence | Report-schema rejection |
| P3-C09 | Assistance class cannot be changed after evaluation begins | Immutable manifest and post-start mutation rejection |
| P3-C10 | W3 classification is invalidated by any mandatory integrity or cost failure | Table-driven W3 failure corpus |

## D. E0, E1, and E2 evaluation points

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-D01 | Every episode contains exactly one ordered E0, E1, and E2 | Cardinality/order assertions |
| P3-D02 | E0 occurs before episode caregiving or adoption | Event-sequence proof |
| P3-D03 | E0 records the complete capability bundle, protected outcomes, substrate declaration, availability class, checkpoint, and initial costs | Exact manifest field set |
| P3-D04 | E1 begins only after all episode caregiving and adoption operations are final | Cutoff-event and no-later-operation proof |
| P3-D05 | E1 records exact adopted artifacts/updates, substrate declaration, capability outcomes, costs, and stable checkpoint | Exact linkage reconstruction |
| P3-D06 | E2 begins only after checkpoint-stable caregiver disablement | Disablement checkpoint proof |
| P3-D07 | E2 reuses the exact capability suite and evaluator bundle | Digest equality and mutation rejection |
| P3-D08 | E2 verifies channel unavailability and substrate integrity before first capability scoring action | Clock/call/evaluator-order guards |
| P3-D09 | An integrity failure stops E2 before scoring and records a typed experiment-integrity failure | No-score/no-partial-result tests |
| P3-D10 | No post-E1 caregiving, adoption, model update, artifact activation, or hidden queue can affect E2 | Cutoff and pending-work adversarial corpus |
| P3-D11 | Backward or forward wall time cannot change point order or eligibility | Injected-time adversarial tests |
| P3-D12 | Each point binds one stable checkpoint and exact runtime state | Active/checkpoint reconstruction |

## E. Runtime-substrate declaration and hidden scaffold

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-E01 | Every runtime dependency available to the organism or scoring path is declared | Source/runtime inventory and guarded dependency enumeration |
| P3-E02 | Supported classes include model weights, prompts, memory, skill banks, code, rules, tests, traces, demonstrations, recovery suffixes, routers, tools, fixtures, environment, protected evaluators, protected runtime, and typed other | Exact enum tests |
| P3-E03 | Every entry contains exact ID, class, version, digest, size, active/callable flags, authority, origin, provenance, adoption/update, checkpoint/lineage, W-class permission, and capability dependency | Golden entry and missing/extra-field corpus |
| P3-E04 | Empty class lists require independent proof that no such runtime substrate exists | Absence guard and malicious hidden object |
| P3-E05 | Caregiver-derived entries link to exact caregiving-event IDs | Missing/wrong/cross-lineage provenance rejection |
| P3-E06 | Every active caregiver-derived entry links to one accepted conversion/update record | Orphan active-substrate rejection |
| P3-E07 | Runtime bytes and declared digest/size match exactly | One-byte and size mutation corpus |
| P3-E08 | Active runtime dependencies cannot be declared inactive or not required | Instrumented-use contradiction test |
| P3-E09 | Undeclared prompt, memory, skill, demonstration, trace, router, tool, code, cache, or alternate model invalidates E2 | Hidden-scaffold corpus |
| P3-E10 | Caregiver-derived content mislabeled as organism-derived or protected infrastructure invalidates E2 | Origin-forgery corpus |
| P3-E11 | Evaluator or environment modification derived from episode caregiving invalidates E2 | Protected-infrastructure contamination tests |
| P3-E12 | Dynamic retrieval from undeclared stores invalidates E2 before scoring | Guarded retrieval probes |
| P3-E13 | Silent model/artifact update after E1 invalidates E2 | Digest and event-cutoff tests |
| P3-E14 | Hidden-scaffold failure evidence is retained and cannot be suppressed | Immutable integrity record and report inclusion |

## F. Caregiving evidence and verified conversion

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-F01 | Future caregiving records bind request, response source, caregiver identity, typed class, content digest/size, provenance, clarification, confidence/abstention, latency/cost, transformation, verification, disposition, and adoption/update | Exact evidence-chain reconstruction |
| P3-F02 | Supported assistance classes can represent demonstration, correction, constraint, explanation, preference, question, defer, and abstain | Exact enum and unknown rejection |
| P3-F03 | Final outcomes include accepted, rejected, deferred, clarification requested, misleading detected, inconsistent detected, unrepresentable, expired, and invalid | Exact enum and terminal cardinality |
| P3-F04 | Caregiver identity/content remains untrusted provenance and never certifies adoption | Forged-authority and self-certification rejection |
| P3-F05 | Every active caregiver-derived substrate has exactly one accepted conversion/update chain | Duplicate/missing/conflicting chain rejection |
| P3-F06 | Conversion records bind source events, candidate identity/digest/size, method, evaluator, evidence, result, writer, activation checkpoint, deactivation/supersession/rollback, and exact cost | Golden conversion object |
| P3-F07 | Inspectable artifacts are local, versioned, digest-bound, and attributable | Artifact inventory and corruption tests |
| P3-F08 | Model updates declare base/result identities, method, data class, legal review, compute, storage, and verification | Synthetic declared-update conformance test |
| P3-F09 | An undeclared weight update is hidden scaffold | Model-digest mismatch rejection |
| P3-F10 | Provider permission is never inferred from technical conformance | Documentation and report guard |
| P3-F11 | Rejected candidate artifacts never become active runtime substrate | Activation-authority adversarial test |
| P3-F12 | Proposal, verification, and adoption remain distinct protected operations | Event/order and authority-boundary tests |

## G. Protected evaluator and authority

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-G01 | Capability suite and evaluator bundle are fixed and digest-bound before E0 | Pre-E0 manifest and mutation guards |
| P3-G02 | Organism and caregiver cannot write, replace, configure, or select evaluators | API/source/runtime capability absence |
| P3-G03 | Organism and caregiver cannot alter task definitions, thresholds, weights, scenarios, abstention expectations, or failure mappings | One-field mutation corpus |
| P3-G04 | Post-observation test selection or favorable-case filtering rejects | Selection-log and complete-suite reconciliation |
| P3-G05 | Negative results cannot be suppressed, deleted, or rewritten | Immutable results and export reconstruction |
| P3-G06 | Evaluator output does not directly mutate organism state | Transaction and authority inspection |
| P3-G07 | Protected administration may record evaluator evidence but cannot privately redefine evaluator semantics | Exact version/digest validation |
| P3-G08 | Caregiver output never certifies correctness or adoption | Self-approval rejection |
| P3-G09 | Any evaluator/suite version change creates a new episode rather than amending the old comparison | Version-fork test |
| P3-G10 | A later adoption boundary is at least as strict as Phase 2 proposal/verification/disposition separation | Cross-protocol design audit |

## H. Capability, retention, and reporting semantics

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-H01 | Results are recorded per capability; aggregate-only evidence is insufficient | Missing per-capability rejection |
| P3-H02 | Result statuses are exactly passed, failed, abstained, not reached, or invalid | Exact enum tests |
| P3-H03 | Result records bind capability/evaluator versions, scenario, ordered evidence, resources, protected outcomes, checkpoint, and episode | Golden result object |
| P3-H04 | Acquisition requires target not passed at E0 and passed at E1 with an accepted conversion chain | Three-point target scenario |
| P3-H05 | Retention requires passed at E1 and E2 under exact suite/evaluator identity and valid integrity/cost evidence | Three-point retention scenario |
| P3-H06 | Every protected E0 capability passes at E1 and E2 unless a different typed expectation was fixed before E0 | Regression corpus |
| P3-H07 | No post-hoc task exclusion, threshold change, reweighting, or evaluator substitution is accepted | Report and manifest mutation corpus |
| P3-H08 | Protected abstention counts as passing only when predeclared by the suite | Expected/unexpected abstention cases |
| P3-H09 | Timeout, tool failure, unavailable caregiver, or hidden fallback cannot masquerade as abstention competence | Failure-classification tests |
| P3-H10 | W0 reports use intervention-aided or efficiency language, W1 reports live-source independence, W2 reports assistance-independent policy performance, and only valid W3 may use the candidate maturity claim | Report-schema validation |
| P3-H11 | Reports include unsuccessful episodes and abandoned lineages | Complete episode-set reconciliation |
| P3-H12 | Every claim identifies repository commit, contract, matrix, suite, evaluator, and evidence-map versions | Exact report provenance |

## I. Caregiver disablement

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-I01 | Accepted configuration sets caregiver allowance to zero or disabled before E2 | Exact protected configuration equality |
| P3-I02 | No live adapter capability handle exists during E2 | Capability guard and object-graph inspection |
| P3-I03 | No dispatch, bridge, model call, live chat, network, subprocess, or human-intervention event occurs after cutoff | Event and guarded-call reconciliation |
| P3-I04 | No alternate or fallback caregiver route remains callable | Adversarial alternate-path probes |
| P3-I05 | No unresolved pre-cutoff response, cached live output, queued package, or stale proposal is usable during E2 | Pending-work corpus |
| P3-I06 | Caregiver costs remain exactly zero after the E1 cutoff | Ledger and event reconstruction |
| P3-I07 | Disablement is checkpoint-stable before E2 | Active/checkpoint equality |
| P3-I08 | Independent reconstruction verifies disablement evidence | Separate validator/harness |
| P3-I09 | Choosing not to invoke an available route classifies as W0 | Available-zero-call control |
| P3-I10 | Disablement failure produces no capability score or partial success claim | Pre-score failure injection |

## J. Rollback and harmful-assistance controls

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-J01 | Misleading assistance has a predeclared expected detection/rejection or harm outcome | Deterministic misleading fixture |
| P3-J02 | Inconsistent assistance is preserved and cannot be collapsed into one favorable response | Contradiction corpus |
| P3-J03 | Correct but unrepresentable assistance records `unrepresentable` without silent coercion | Representation-boundary fixture |
| P3-J04 | Ambiguous assistance requires typed clarification or final rejection according to future accepted protocol | Ambiguity fixture |
| P3-J05 | Premature withdrawal and dependency collapse are explicit experiment conditions | Scheduled cutoff scenarios |
| P3-J06 | Delayed withdrawal does not count as maturity when the channel remains available | W0 dependency control |
| P3-J07 | Hidden-scaffold injection is an integrity failure | Prompt/skill/router/tool injection corpus |
| P3-J08 | Stale or wrong-lineage artifact reuse rejects before scoring | Rollback/stale substrate tests |
| P3-J09 | Evaluator-targeting or test-weakening assistance rejects | Protected-suite attack fixture |
| P3-J10 | Rollback retains harmful/failed lineage evidence and ends the episode | Full rollback evidence scenario |
| P3-J11 | New lineage starts a new E0 and cannot inherit success or cost evidence | Fresh-episode reconstruction |
| P3-J12 | No negative episode or rejected artifact can be deleted to improve reported rates | Retention/export reconciliation |

## K. Complete developmental cost ledger

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-K01 | Every cost field status is exactly measured, not applicable, or unmeasured; unknown is never zero | Exact enum and zero/unknown controls |
| P3-K02 | W3 cost completeness rejects mandatory unmeasured fields | Field-by-field missing corpus |
| P3-K03 | Not-applicable fields require a protected reason | Missing/invalid reason rejection |
| P3-K04 | Human active, monitoring, intervention, review, and maintenance time use exact integer milliseconds | Boundary and unit validation |
| P3-K05 | Consultation, demonstration, correction, clarification, abstention, and rejection counts reconcile with event history | Independent ledger reconstruction |
| P3-K06 | Model calls, tokens, latency, retries, failures, money, provider/product/model/version, and retained-data class reconcile with external evidence | Synthetic provider ledger corpus |
| P3-K07 | Environment interactions, resets, failed episodes, evaluator/fixture calls, and administrative operations are exact | Harness counters and event equality |
| P3-K08 | Training/inference CPU and accelerator time use declared integer units and device classes | Synthetic compute accounting |
| P3-K09 | Working set, active state, checkpoint store, caregiver-derived substrate, total substrate, and retained-evidence bytes are independently measured | Filesystem/database reconciliation |
| P3-K10 | Artifact review, experimenter work, and maintenance labor are visible rather than hidden | Protected external-work records |
| P3-K11 | Complete cost vectors are reported without silently collapsing to one scalar | Report-schema validation |
| P3-K12 | No scalar maturity score exists unless a later pre-E0 accepted ADR fixes formula, weights, units, and missing-data rules | API/documentation absence guard |
| P3-K13 | Reduced caregiver burden cannot be claimed when a mandatory displaced cost is unmeasured | Comparative report rejection |
| P3-K14 | Cost records bind exact episode, point, lineage, checkpoint, and source evidence | Cross-point/lineage mutation corpus |

## L. Controls, baselines, and design/implementation gates

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P3-L01 | No-caregiver control exists before live capability work | Deterministic empty-caregiver scenario |
| P3-L02 | Deterministic-fixture control exists before live capability work | Exact fixture scenario |
| P3-L03 | Synthetic W0–W3 substrate declarations exercise classification without live sources | Table-driven conformance harness |
| P3-L04 | Hidden-scaffold, wrong-lineage, evaluator-mutation, incomplete-cost, and rollback controls are mandatory | Complete negative-control set |
| P3-L05 | A strong scientific claim compares persistent prompt/skill, internalized-weight, finite-demonstration, W3 local-artifact, misleading, inconsistent, and premature-withdrawal conditions where applicable | Predeclared experiment matrix |
| P3-L06 | Deterministic conformance implementation may precede the complete research comparison but cannot publish W3 results | Scope/report guard |
| P3-L07 | Proposed ADR, contract, and this matrix receive one independent read-only design audit against one exact CI-green candidate | Audit Issue with fixed head and conclusion |
| P3-L08 | Audit findings are recorded with severity, invariant ID, exact section, evidence, and disposition | Audit finding schema |
| P3-L09 | Accepted documentation corrections precede any status change to Accepted | Git history and status assertion |
| P3-L10 | Contract acceptance does not authorize implementation | ADR/contract explicit exclusion check |
| P3-L11 | Every later capability requires separate scope, ADR, matrix, current legal/provider review where applicable, explicit owner confirmation, and implementation audit | Later-phase gate checklist |
| P3-L12 | Open questions remain unresolved in documentation and are not privately decided in code | Source inspection and design audit |
| P3-L13 | Handoff and Issues identify changed, incomplete, and next work exactly | Durable continuity check |
| P3-L14 | No public novelty claim is made from this design package | Repository text search and review |

## Acceptance rule

This proposed matrix and contract may move to Accepted only after:

1. every proposed invariant is internally consistent and mapped;
2. the complete frozen protected suite passes on one exact documentation candidate;
3. one independent read-only design audit reaches an explicit acceptance conclusion;
4. accepted findings are repaired without weakening frozen controls;
5. the project owner confirms any material research-boundary change;
6. exact accepted commit, audit evidence, and next gate are recorded.

Acceptance still does not authorize Phase 3 runtime implementation.