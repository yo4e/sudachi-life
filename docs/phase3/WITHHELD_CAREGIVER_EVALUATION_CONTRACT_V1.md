# Phase 3 Withheld-Caregiver Evaluation Contract v1

Status: **Proposed design — audit corrections applied; no implementation or live capability is authorized**

Tracked by: GitHub Issues #3, #132, and #135

Research basis:

- `docs/research/CAREGIVER_WITHDRAWAL_AND_RETAINED_COMPETENCE.md`
- `docs/research/WITHDRAWAL_PROTOCOL_EXTRACTION.md`

## 1. Purpose

This contract defines the evidence required to claim that one bounded SUDACHI organism converted finite external cognitive scaffolding into retained local competence.

It does not define a live caregiver transport, model provider, training algorithm, memory system, skill implementation, action-adoption route, database schema, or schema migration.

It protects one question:

> Did one predeclared developmental attempt in one organism lineage retain capability after every caregiver route became technically unavailable, without an undeclared caregiver-derived runtime scaffold, evaluator leakage or weakening, rewritten failure history, cross-episode or cross-lineage evidence substitution, or hidden cost displacement?

A narrower control result may be valid without satisfying W3 conformance or a W3 maturity claim.

## 2. Normative precedence and frozen boundaries

This proposed contract is subordinate to:

1. Minimal Organism Contract v0.2;
2. accepted ADRs 0001–0016;
3. the frozen Phase 1 protected suite and matrix;
4. the frozen Phase 2 Consultation Protocol v1, amendments, protected suite, and 213-ID evidence map.

It must not reinterpret or change:

- Phase 1 garden actions, selector, executor, evaluators, clocks, checkpoints, rollback transformation, writer categories, or tests;
- Phase 2 request, dispatch, charge, fixture, ingress, terminalization, disposition, finite-cycle, rollback-lineage, authority, physical-limit, or explicit-absence semantics;
- canonical writer categories, which remain exactly `organism` and `administration`;
- the one-completed-rollback limit in ADR 0007;
- any existing resource ceiling or budget location.

The complete protected suite must preserve test/helper blob identity, collection integrity, no-skip behavior, and assertion integrity for the frozen controls.

A later implementation requires a separate accepted ADR package and explicit project-owner confirmation for every new live or mutable capability.

## 3. Proposed versions and terms

Proposed versions:

- evaluation contract: `sudachi.withheld_caregiver_evaluation/v1`;
- availability axis: `sudachi.assistance_availability/v1`;
- W3 certification: `sudachi.w3_conformance/v1`;
- study/run-set manifest: `sudachi.developmental_study/v1`;
- developmental attempt: `sudachi.developmental_attempt/v1`;
- developmental episode: `sudachi.developmental_episode/v1`;
- availability transition: `sudachi.availability_transition/v1`;
- runtime-substrate declaration: `sudachi.runtime_substrate_declaration/v1`;
- conversion transition: `sudachi.conversion_transition/v1`;
- verification transition: `sudachi.verification_transition/v1`;
- adoption transition: `sudachi.adoption_transition/v1`;
- activation transition: `sudachi.activation_transition/v1`;
- evaluation point: `sudachi.evaluation_point/v1`;
- cost ledger: `sudachi.developmental_cost_ledger/v1`;
- final cost closure: `sudachi.developmental_cost_closure/v1`;
- capability result bundle: `sudachi.capability_result_bundle/v1`.

Terms:

- **caregiver** — a human or artificial source of developmental assistance;
- **caregiving event** — one typed request, response, correction, demonstration, explanation, constraint, preference, question, deferment, abstention, or related operation;
- **runtime substrate** — every state, artifact, model, prompt element, tool, router, trace, cache, or external dependency visible to or callable by the evaluated execution path;
- **caregiver-derived substrate** — runtime substrate whose content, selection, parameters, or existence materially depends on a caregiving event;
- **externalized scaffold** — a caregiver-derived prompt, memory, skill, demonstration, trace, code/rule artifact, router, tool, or other separately addressable runtime dependency outside internalized policy/model parameters;
- **withheld-caregiver evaluation** — evaluation where every caregiver route is technically unavailable, not merely unused;
- **retained competence** — the same declared capability remains satisfied at E2 after being established at E1;
- **developmental attempt** — one preregistered member of a study/run set, assigned an immutable ordinal and terminal status whether or not it reaches E0;
- **developmental episode** — one immutable E0→E1→E2 comparison unit bound to one attempt, organism, lineage, environment, evaluator bundle, capability suite, and protected schedule;
- **hidden scaffold** — any undeclared, mismatched, mislabeled, stale, or availability-prohibited caregiver-derived runtime substrate;
- **W3 conformance** — an episode-level certification over a declared W1 or W2 substrate subtype; W3 is not an availability class;
- **W3 maturity claim** — any wording that claims developmental conversion, maturity, retained learned competence, or reduced justified caregiver dependence under W3 conformance;
- **scientific comparative claim** — a W3 maturity claim supported by a preregistered comparison family and study-level stopping rule.

Unknown versions, undeclared fields, and unknown normative states fail closed. This document does not authorize their storage or runtime implementation.

## 4. Assistance availability and W3 certification

### 4.1 Point-local availability axis

Every evaluation point declares exactly one mutually exclusive availability class:

- **W0 — assistance available.** At least one caregiver route remains technically available, whether used or not. Zero calls under W0 do not demonstrate independence.
- **W1 — live source unavailable; externalized caregiver scaffold remains.** Every caregiver route is unavailable and at least one declared externalized caregiver-derived scaffold remains active, readable, executable, or callable at runtime. W1 demonstrates live-source independence only.
- **W2 — live source and externalized caregiver scaffold unavailable.** Every caregiver route is unavailable and no externalized caregiver-derived scaffold remains active, readable, executable, or callable. Caregiver-derived capability may remain only in a fully declared internalized policy/model update; an episode with no caregiver-derived runtime substrate may also be W2.

An evaluation point cannot be W3. The W0/W1/W2 class is immutable once that point begins.

### 4.2 Orthogonal W3 certification

W3 is an episode-level certification. A W3-certified episode must retain its W1 or W2 E2 subtype in every manifest and report.

W3 certification requires:

1. one preregistered study/run-set manifest and attempt;
2. one identity-bound developmental episode;
3. finite recorded caregiving events within the current episode window;
4. exhaustive runtime-substrate declarations at E0, E1, and E2;
5. exact provenance from each caregiver-derived substrate to current-episode caregiving events;
6. four separate protected conversion, verification, adoption, and activation transitions;
7. technical unavailability of every caregiver route at E2 under the predeclared schedule;
8. no hidden scaffold;
9. retained capability on one fixed held-out outcome suite;
10. protected evaluator, information-flow, and writer-authority boundaries;
11. preserved rollback, failed-attempt, and negative-result history;
12. complete final cost closure with no displaced unmeasured work.

W3 conformance is not proof of scientific novelty. A deterministic synthetic conformance report cannot use developmental-gain or maturity wording.

## 5. Study, attempt, episode, and lineage identity

### 5.1 Pre-E0 study/run-set manifest

Before any attempt-specific caregiving or E0 execution, protected administration fixes and digest-binds:

- study ID and manifest version;
- study purpose and allowed claim tier;
- deterministic control/run generation rule;
- exact planned attempt count or an exact stopping rule;
- attempt ordinals and assignment rule;
- required failure-control conditions;
- comparison-family conditions where a scientific comparative claim is planned;
- terminal statuses exactly `scheduled`, `started`, `e0_invalid`, `development_failed`, `rolled_back`, `e2_invalid`, `completed_unsuccessful`, or `completed_successful`;
- full-population reconciliation rule;
- suite, outcome evaluator, conversion verifier, information-flow policy, protected schedule, and cost-policy identities.

Every scheduled or started attempt remains in the study population. Post-hoc stopping, silent abandonment, ordinal reuse, and omission are invalid. The concrete count may be chosen by a later accepted design, but the rule cannot be chosen after results.

### 5.2 Attempt and episode identity

A developmental episode identity contains exactly:

- contract version;
- study ID;
- attempt ID and ordinal;
- organism ID;
- lineage generation;
- database schema version;
- base contract version;
- environment version;
- capability-suite version and digest;
- held-out outcome-evaluator version and digest;
- conversion-verifier version and digest;
- information-flow-policy version and digest;
- protected schedule version and digest;
- protected budget/configuration versions;
- baseline checkpoint ID;
- caregiver-condition ID;
- substrate-baseline-condition ID;
- deterministic fixture-case or experiment-seed ID where applicable.

It excludes later result IDs, wall time, and mutable status.

Every caregiving event, transformation, verification, disposition, adoption, activation, substrate entry, cost entry, result, integrity record, disablement proof, and report evidence item binds exact study, attempt, episode, organism, lineage, point/cutoff, and checkpoint identities.

### 5.3 Organism and lineage

`organism_id` identifies the physical organism record. `lineage_generation` identifies one developmental lineage.

Rollback:

- preserves the abandoned future as evidence;
- increments lineage according to frozen semantics;
- ends the current episode and attempt without success;
- requires a new attempt assignment, E0, and episode identity in the new lineage;
- forbids post-rollback results from satisfying the prior episode;
- forbids abandoned-lineage capability, cost, transition, or substrate evidence from satisfying the new lineage.

A physical organism may contain multiple historical episodes in one lineage, but no evidence item can cross episode IDs. Pre-E0 inherited substrate is declared as baseline state and cannot establish acquisition for the current episode.

### 5.4 Fixed comparison identity and protected schedule

E0, E1, and E2 share exactly:

- study ID;
- attempt ID;
- episode ID;
- organism ID;
- lineage generation;
- environment version;
- capability-suite identity;
- held-out outcome-evaluator identity;
- conversion-verifier identity;
- information-flow-policy identity;
- protected schedule identity;
- protected budget/configuration versions;
- substrate-baseline-condition ID.

The immutable protected schedule is fixed before E0 and includes:

- the exact E1 cutoff event rule;
- the only legal E2 caregiver-disablement transition;
- authorized writer exactly `administration`;
- before and after availability values;
- required source and destination checkpoints;
- transition ordering;
- idempotent replay result;
- conflict and wrong-checkpoint failure behavior.

Point-local availability state and the transition event are recorded separately from immutable configuration identity. The scheduled W0→W1 or W0→W2 transition does not create a new episode. Any unplanned availability change, wrong writer, wrong checkpoint, conflicting replay, budget mutation, evaluator mutation, or other configuration change invalidates the episode or creates a new episode as predeclared.

## 6. Required evaluation points

Every episode contains exactly three ordered points.

### 6.1 E0 — valid pre-development baseline

E0 occurs after attempt registration and before current-episode caregiving, conversion, adoption, or activation.

E0 records:

- every capability result and complete suite-case reconciliation;
- protected safety, abstention, transfer, and recovery outcomes;
- complete runtime-substrate declaration;
- point-local W0/W1/W2 availability class;
- stable checkpoint;
- initial cumulative cost ledger;
- point-integrity, infrastructure, reachability, and suite-completeness status.

Acquisition analysis is forbidden unless E0 integrity is valid, every required case is reached or has a predeclared valid status, the checkpoint is valid, and the suite is complete.

### 6.2 E1 — post-activation evaluation

E1 occurs only after all current-episode caregiving and all conversion, verification, adoption, and activation transitions are terminal and the predeclared E1 cutoff is committed.

No later caregiving event, conversion, verification, adoption, activation, or model update may contribute to the episode.

E1 records exact active artifacts/updates, complete substrate declaration, unchanged-suite results, protected outcomes, cumulative costs, and one stable checkpoint.

### 6.3 E2 — withheld-caregiver evaluation

E2 begins only after the predeclared availability transition reaches its exact destination checkpoint.

Before the first capability scoring action, protected administration must prove:

- every caregiver route is unavailable by the scheduled state and capability guard;
- no dispatch, human bridge, model call, live chat, network route, subprocess route, dynamic caregiver retrieval, fallback, or alternate path can execute;
- no queued response, cached live output, unresolved package, stale proposal, or pre-cutoff response can affect scoring;
- every runtime substrate is declared and digest/size/access-state matched;
- every caregiver-derived substrate is permitted by the declared W1 or W2 subtype and has complete current-episode transition evidence;
- every prohibited externalized scaffold is absent for W2;
- no post-E1 caregiving, conversion, verification, adoption, activation, or model update occurred;
- checkpoint, attempt, episode, organism, and lineage are exact;
- held-out outcome evaluator sequestration remains intact.

Any failure invalidates E2 before scoring, records a typed experiment-integrity result, and prevents W3 certification. It is not scored as organism capability failure.

E2 records the final capability bundle, integrity bundle, substrate declaration, final cumulative ledger snapshot, and destination checkpoint.

## 7. Capability result semantics

Results are per-capability typed records. Aggregate score alone is insufficient.

Each result declares capability/suite identity, held-out evaluator identity, deterministic scenario, ordered evidence, required resource counters, checkpoint, complete identity linkage, and status exactly `passed`, `failed`, `abstained`, `not_reached`, or `invalid`.

### 7.1 Acquisition

A target capability is acquired only when:

- E0 point integrity, reachability, checkpoint validity, and suite completeness are valid;
- E0 status is exactly `failed`, or exactly `abstained` only when the suite fixed that abstention as acquisition-eligible before E0;
- E0 status is not `invalid` or `not_reached` and is not infrastructure failure, hidden fallback, timeout, tool failure, or unplanned refusal;
- E1 is `passed`;
- a complete accepted current-episode caregiving→conversion→verification→adoption→activation chain exists after E0 and before the E1 cutoff;
- no protected invariant regresses beyond a rule fixed before E0.

### 7.2 Retention and preservation

A target capability is retained only when E1 and E2 are `passed` under exact suite/evaluator identity, E2 integrity is valid, W3 certification is valid, and final cost closure is complete.

Every capability that passed at E0 and was marked protected before E0 must pass at E1 and E2 unless the suite predeclares another exact typed expectation.

No post-hoc exclusion, reweighting, threshold change, evaluator substitution, or case filtering is permitted.

Protected abstention may pass only when predeclared by the suite. Timeout, unavailable service, tool failure, hidden fallback, or unplanned refusal is not abstention competence.

## 8. Runtime-substrate declaration and hidden scaffold

Every point declares every dependency available to the organism or evaluator-facing execution path.

Required classes include `model_weights`, `prompt_example`, `retrieved_memory`, `skill_bank`, `deterministic_code`, `rule`, `test`, `action_trace`, `demonstration`, `recovery_suffix`, `router`, `external_tool`, `fixture`, `environment_state`, `protected_evaluator`, `conversion_verifier`, `protected_runtime`, `cache`, and `other_declared`.

Each entry declares:

- substrate ID, class, and version;
- canonical digest;
- canonical byte size and independently measured byte size as separate fields;
- active, executable, readable, and callable booleans;
- **custodian** exactly `organism`, `administration`, `protected_experiment_infrastructure`, or `environment`;
- origin exactly `genesis`, `caregiver_derived`, `organism_derived`, `administration_protected`, or `environment`;
- current-episode source caregiving-event IDs when caregiver-derived;
- conversion, verification, adoption, and activation evidence IDs;
- study, attempt, episode, organism, lineage, point, cutoff, and checkpoint linkage;
- W1/W2 permission;
- capability dependency.

`custodian` is inventory metadata and never grants writer authority. Canonical writer categories remain exactly `organism` and `administration`.

An empty class list is valid only when independent source/runtime inspection proves absence.

E2 is invalid for any undeclared substrate; digest or size mismatch; missing current-episode provenance; missing transition record; wrong availability permission; alternate caregiver route; undeclared retrieval or cache; caregiver-derived evaluator/environment modification; forged origin; used dependency declared inactive/unreadable/unexecutable/uncallable; stale episode/lineage evidence; or silent model/artifact update after E1.

The failure stops scoring and remains in the study population.

## 9. Caregiving evidence

This contract does not authorize a live caregiver protocol. A later ADR must define transport and schemas.

Every future caregiving record binds the complete identity tuple from §5.2 and records request, source/caregiver identity, typed assistance class, bounded content digest/size, provenance/product version where applicable, clarification relation, confidence/abstention, latency/cost, and terminal outcome.

Supported assistance classes must represent demonstration, correction, constraint, explanation, preference, question, defer, and abstain.

Terminal outcomes must include `accepted`, `rejected`, `deferred`, `clarification_requested`, `misleading_detected`, `inconsistent_detected`, `unrepresentable`, `expired`, and `invalid`.

Caregiver identity and content remain untrusted provenance and never create canonical authority.

## 10. Four protected conversion transitions

Every caregiver-derived substrate active at E1 or E2 requires four separate immutable linked records.

### 10.1 Conversion record

Records conversion ID, source caregiving events, candidate identity/class/version/digest/size, transformation method/version, authoring writer, inputs/outputs, cost, and status exactly `produced`, `failed`, or `invalid`.

Conversion produces no active substrate and cannot certify correctness.

### 10.2 Verification record

Records verification ID, conversion ID, separate conversion-verifier identity, bounded disclosed inputs/outputs, probe/retry ordinal, cost, and status exactly `passed`, `failed`, or `invalid`.

Verification cannot adopt or activate.

### 10.3 Adoption record

Records adoption ID, verification ID, candidate identity, authorized adopting writer exactly `organism` or `administration` as fixed by a later ADR, disposition, reason, cost, and status exactly `accepted`, `rejected`, or `invalid`.

Accepted-but-inactive is a required representable state. Adoption cannot activate by itself.

### 10.4 Activation record

Records activation ID, accepted adoption ID, authorized activation writer exactly `organism` or `administration` as fixed by a later ADR, source checkpoint, destination stable checkpoint, active substrate identity, cost, and status exactly `activated`, `deactivated`, `superseded`, `rolled_back`, or `invalid`.

Activation requires one accepted adoption and the exact predeclared stable checkpoint. Wrong order, wrong writer, wrong checkpoint, partial failure, conflicting replay, or activation of a rejected candidate has no partial runtime effect and fails closed.

Exact duplicate replay is idempotent. A same-ID/different-content replay is conflict. Supersession and deactivation preserve prior records. Rollback follows ADR 0007 and ends the episode.

### 10.5 Model-parameter updates

A model update is eligible for W2 or W3 only when all of the following are mandatory and digest-bound:

- base model identity and digest;
- resulting model identity and digest;
- update method/version and training-data class;
- permitted caregiver-output transformation class;
- training compute and storage;
- verification evidence and all four transitions.

If any mandatory identity, digest, method, data-class, compute/storage, or verification evidence cannot be produced, the model update is unsupported and ineligible before scoring. It cannot pass using `unmeasured` or “technically unavailable.”

Provider/legal/privacy review metadata is separately typed and may record unavailable or not applicable without weakening identity and integrity evidence. Technical conformance never implies permission to train or transform provider output.

## 11. Protected verifier, outcome evaluator, and information flow

Before E0, protected administration fixes and digest-binds:

- one conversion verifier;
- one sequestered held-out outcome evaluator and capability suite;
- one information-flow policy;
- verifier probe/retry budgets;
- disclosed feedback fields, recipients, timing, and cardinality.

The conversion verifier and held-out outcome evaluator must be distinct identities and non-aliased execution roles. Held-out cases, expected outputs, scores, thresholds, and per-case results are unavailable to the organism, caregiver, converter, adoption authority, and activation authority until the attempt is terminal, except for feedback explicitly permitted by the pre-E0 policy.

Every verifier and evaluator invocation, probe, retry, disclosed field, and recipient is logged and reconciled. Case leakage, result-feedback leakage, adaptive probing beyond budget, retry exhaustion, evaluator-targeted artifacts, or verifier/evaluator aliasing invalidates the attempt for W3.

The organism and caregiver cannot write, replace, configure, weaken, reweight, select, suppress, or authorize the verifier, evaluator, suite, schedule, cost rules, or writer categories.

Evaluator output does not directly mutate organism state. Caregiver output never certifies correctness, adoption, or activation.

## 12. Caregiver disablement proof

A future E2 implementation proves the one predeclared availability transition through:

1. exact protected schedule identity;
2. authorized writer `administration`;
3. exact before/after values and source/destination checkpoints;
4. idempotent duplicate behavior and conflicting-replay rejection;
5. absence of live adapter handles;
6. guarded imports and source inspection;
7. zero post-cutoff dispatch, bridge, network, subprocess, model-call, and human-intervention events;
8. zero post-cutoff caregiver cost;
9. fail-closed alternate-path probes;
10. exact substrate declaration;
11. no usable queued/cached/unresolved caregiver output;
12. independent reconstruction.

Choosing not to call an available caregiver is W0.

## 13. Rollback, attempts, and negative futures

ADR 0007 remains authoritative.

Every scheduled/started attempt receives an immutable identity before E0 and a terminal status. Misleading, inconsistent, harmful, ambiguous, unrepresentable, prematurely withdrawn, dependency-producing, rejected, invalid, and rolled-back attempts remain visible and reconcile to the study manifest.

Rollback archives the failed future, never converts failure into success, starts a new lineage/attempt/E0 where permitted, and preserves rejected substrates and failed transitions.

A W3 report includes every scheduled/started attempt and unsuccessful episode, not only the surviving lineage.

## 14. Mandatory failure controls and claim tiers

For any W3 maturity wording, the study manifest must predeclare controls for misleading assistance, inconsistent assistance, correct-but-unrepresentable advice, ambiguous advice, premature withdrawal, delayed withdrawal/dependency persistence, hidden-scaffold injection, stale/wrong-episode or wrong-lineage reuse, evaluator targeting/leakage, opaque model update, cost displacement, caregiver outage/abstention, organism abstention, transition replay/conflict, and rollback after harmful activation.

A **deterministic W3 conformance report** may test synthetic mechanics only and must not claim developmental gain, maturity, or scientific effectiveness.

A **W3 maturity claim** requires all mandatory failure controls and full study-population reconciliation.

A **scientific comparative claim** additionally requires a pre-E0 comparison family including, where technically and legally applicable, no caregiver, deterministic fixture, persistent prompt/skill, internalized weights, finite demonstration, W3 local artifact, misleading caregiver, inconsistent caregiver, and premature withdrawal.

No control may be omitted after outcomes are observed.

## 15. Developmental cost ledger and final closure

The ledger uses exact integers and declared units. Unknown is never zero.

Every field status is exactly `measured`, `not_applicable`, or `unmeasured`. W3 cost completeness requires every mandatory field to be `measured` or `not_applicable` with a protected reason.

Mandatory human fields include active caregiver, monitoring, intervention, artifact review, maintenance, experimenter development, evaluator operation, integrity investigation, report preparation, and report review time in integer milliseconds, plus typed event counts.

Mandatory model/service fields include calls, input/output tokens, measured latency, retries, failures, money in integer minor units with currency, provider/product/model/version, and retained-data/service class.

Mandatory environment/experiment fields include interactions, resets, failed attempts, evaluator/verifier/fixture calls, administrative operations, and research wall-duration metadata.

Mandatory compute/storage fields include training/inference CPU and accelerator time by device class; peak working set; active state; checkpoint store; caregiver-derived and total runtime substrate; retained artifact/log/evidence; and report-package bytes.

One immutable final cost-closure record is required before W3 certification. It binds the complete study/attempt/episode identity and a cutoff after all scheduled attempt operations, E2, integrity handling, verifier/evaluator retries, storage measurement, evidence packaging, report preparation, and report review are complete.

The closure reconciles E0, E1, E2, transition, integrity, administration, compute, storage, failure, and reporting vectors. Premature closure, any late in-scope cost, visible-but-unmeasured labor, unmatched event, or vector mismatch invalidates cost completeness. A corrected closure is a new immutable version; prior closures remain evidence.

No scalar maturity/efficiency score is permitted unless a later ADR fixes formula, units, weights, missing-data behavior, and target suite before E0.

## 16. Reporting requirements

Every W3 report contains exactly these 14 top-level evidence groups:

1. study/run-set manifest and full attempt-population reconciliation;
2. attempt, episode, organism, and lineage identity;
3. valid complete E0 acquisition baseline;
4. finite current-episode caregiving events;
5. conversion, verification, adoption, activation, rejection, supersession, and rollback records;
6. E0/E1/E2 per-capability outcomes;
7. complete E0/E1/E2 substrate declarations and W1/W2 subtype;
8. scheduled caregiver-disablement evidence;
9. hidden-scaffold and evaluator-sequestration validation;
10. final cost closure and complete cost vectors;
11. protected-capability regressions and abstention/safety/recovery outcomes;
12. failed attempts, unsuccessful episodes, abandoned lineages, and stopping-rule reconciliation;
13. comparison conditions, limitations, unsupported substrates, and unmeasured/non-applicable disclosures;
14. repository commit plus contract, matrix, study, suite, verifier, evaluator, schedule, and evidence-map versions.

W0 may report intervention-aided performance. W1 may report live-source independence. W2 may report externalized-scaffold-free policy performance. Only a valid W3 certification may use W3 conformance language, and only the claim tiers in §14 may use maturity or scientific-comparison wording.

The required 14-field set is exact: missing, extra, renamed, merged, or silently omitted groups fail report conformance.

## 17. Matrix, controls, and acceptance gates

`docs/PHASE3_WITHHELD_CAREGIVER_TEST_MATRIX.md` is the proposed protected evidence map for this contract.

Every matrix row must include:

- one unique matrix ID;
- one exact normative clause/reference key;
- one protected requirement;
- one explicit fail-closed outcome;
- plausible protected evidence.

Acceptance requires independent equality checks for:

- unique matrix-ID set;
- normative clause/reference coverage set;
- exact 14-field report set;
- complete protected-suite collection, no-skip, assertion, and frozen test/helper blob integrity.

Design-conformance controls remain separate from later scientific baselines. Acceptance of documentation remains separate from implementation authorization.

This contract becomes Accepted only after one exact corrected candidate passes protected CI, an independent focused re-audit confirms all Issue #135 findings resolved, project-owner confirmation is recorded for the evaluator/information-flow redesign, and exact metadata is synchronized.

Acceptance still does not authorize runtime implementation.

## 18. Explicit exclusions and open questions

This proposed contract does not authorize live human chat or model calls; network or subprocess access; arbitrary code/callable execution or credentials; model training; memory/skill creation or adoption; action adoption/execution; continuous execution; new writer categories; schema migration; repeated rollback; increased budgets/resource ceilings; personality/emotion mechanics; or public novelty claims.

Code must not privately decide database schema/table names, digest domains, caregiver transport, first artifact types, whether model updates are allowed, suite/evaluator implementation, experiment count/stopping rule, provider/legal transformation classes, model/hardware environment, repeated rollback, or scalar metrics.

## 19. Exact next gate

Run one independent focused read-only re-audit of proposed ADR 0017, this contract, the Phase 3 matrix, Issue #135 findings P3-D001 through P3-D010, and one exact CI-green corrected PR #134 head.

No implementation begins at this gate.
