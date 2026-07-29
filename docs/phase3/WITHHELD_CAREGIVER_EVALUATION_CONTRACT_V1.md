# Phase 3 Withheld-Caregiver Evaluation Contract v1

Status: **Proposed design — no implementation or live capability is authorized**

Tracked by: GitHub Issues #3 and #132

Research basis:

- `docs/research/CAREGIVER_WITHDRAWAL_AND_RETAINED_COMPETENCE.md`
- `docs/research/WITHDRAWAL_PROTOCOL_EXTRACTION.md`

## 1. Purpose

This contract defines the evidence required to claim that one bounded SUDACHI organism converted finite external cognitive scaffolding into retained local competence.

It does not define a live caregiver transport, model provider, training algorithm, memory system, skill implementation, action-adoption route, or schema migration.

The contract protects one question:

> Did the same declared developmental lineage retain a capability after the caregiver channel became unavailable, without relying on an undeclared caregiver-derived runtime scaffold, weakening the evaluator, rewriting failed history, or hiding cost in local work?

A system may satisfy a narrower control condition without satisfying the candidate SUDACHI condition.

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

A later implementation requires a separate accepted ADR package and explicit project-owner confirmation for every new live or mutable capability.

## 3. Versions and exact terms

Proposed versions:

- evaluation contract: `sudachi.withheld_caregiver_evaluation/v1`;
- assistance-availability taxonomy: `sudachi.assistance_availability/v1`;
- developmental episode manifest: `sudachi.developmental_episode/v1`;
- runtime-substrate declaration: `sudachi.runtime_substrate_declaration/v1`;
- evaluation-point manifest: `sudachi.evaluation_point/v1`;
- developmental cost ledger: `sudachi.developmental_cost_ledger/v1`;
- capability result bundle: `sudachi.capability_result_bundle/v1`.

Terms:

- **caregiver** — a human or artificial source of developmental assistance;
- **caregiving event** — one recorded request, response, correction, demonstration, explanation, constraint, preference, question, deferment, abstention, or other later-accepted typed assistance operation;
- **runtime substrate** — every state, artifact, model, prompt element, tool, router, trace, or external dependency visible to or callable by the evaluated organism;
- **caregiver-derived substrate** — runtime substrate whose content, selection, parameters, or existence depends materially on a caregiving event;
- **withheld-caregiver evaluation** — an evaluation where the caregiver channel is technically unavailable, not merely unused;
- **retained competence** — the same declared capability result remains satisfied at the withheld point after being established at the post-adoption point;
- **developmental episode** — one immutable comparison unit bound to one organism, one lineage, one environment, one evaluator bundle, one capability suite, and three ordered evaluation points;
- **hidden scaffold** — any undeclared, mismatched, or prohibited caregiver-derived runtime substrate available during evaluation.

Unknown versions and undeclared fields fail the future conformance gate. This document does not yet authorize their storage or runtime implementation.

## 4. Assistance-availability classes

Every evaluation point declares exactly one class.

### W0 — assistance available

The caregiver channel is available during evaluation, whether or not it is used.

W0 measures intervention-aided reliability or consultation efficiency. It does not demonstrate independence.

### W1 — live source unavailable; source-derived runtime artifact remains

The caregiver cannot be contacted, but at least one caregiver-derived runtime artifact remains available, including any:

- prompt example or explanation;
- retrieved memory;
- skill bank;
- demonstration or action suffix;
- recovery trace;
- external router trained or configured from caregiver evidence;
- tool, script, or code artifact derived from caregiving;
- model parameters updated from caregiving.

W1 demonstrates independence from the live source only. It does not demonstrate scaffold-free operation.

### W2 — runtime assistance channel and temporary scaffold unavailable

The caregiver channel is disabled and no caregiver-derived runtime artifact remains except an explicitly declared internalized policy or model-parameter update.

W2 demonstrates assistance-independent policy performance. It does not by itself establish an auditable artifact lineage, protected adoption, rollback evidence, or complete cost accounting.

### W3 — identity-bound verified local conversion under protected lineage

W3 requires all of the following:

1. one identity-bound developmental episode;
2. finite recorded caregiving events;
3. an exhaustive runtime-substrate declaration at every evaluation point;
4. provenance from each caregiver-derived substrate to exact caregiving events;
5. protected verification and adoption evidence;
6. technical unavailability of the caregiver channel;
7. no hidden scaffold;
8. retained capability on the same fixed suite;
9. protected evaluator and authority boundaries;
10. preserved rollback and negative-result lineage;
11. complete required cost fields;
12. no cost displacement hidden as local work.

Only W3 is a candidate SUDACHI maturity condition. Satisfying W3 is not itself proof of scientific novelty.

## 5. Developmental episode identity

A developmental episode is identified by a digest over an exact identity object that contains:

- contract version;
- organism ID;
- lineage generation;
- database schema version;
- base contract version;
- environment version;
- capability-suite version and digest;
- evaluator-bundle version and digest;
- protected budget/configuration versions;
- baseline checkpoint ID;
- declared caregiver condition ID;
- declared substrate-baseline condition ID;
- experiment-seed or deterministic fixture-case ID where applicable.

It excludes later result IDs, wall time, and mutable status.

### 5.1 Physical organism and developmental lineage

`organism_id` identifies the physical organism record.

`lineage_generation` identifies one developmental lineage. A W3 success claim attaches to exactly one lineage generation.

Rollback:

- preserves the abandoned future as evidence;
- increments lineage according to frozen rollback semantics;
- ends the current developmental episode without a success conclusion;
- requires a new baseline evaluation and a new episode identity in the new lineage;
- never permits post-rollback results to satisfy a pre-rollback episode;
- never permits abandoned-lineage capability, cost, or substrate evidence to be substituted into the new lineage.

A physical organism may contain multiple historical episode records, but one comparison never crosses lineage generations.

### 5.2 Fixed comparison identity

Pre-development, post-adoption, and post-withdrawal points must share exactly:

- episode ID;
- organism ID;
- lineage generation;
- environment version;
- capability-suite version and digest;
- evaluator-bundle version and digest;
- protected budget/configuration versions;
- substrate-baseline condition ID.

Checkpoint IDs and declared runtime substrates may change only according to the contract.

Any evaluator, suite, environment, authority, budget, or identity change creates a different episode and invalidates direct retained-competence comparison.

## 6. Required evaluation points

Each developmental episode contains exactly three ordered required points.

### E0 — pre-development baseline

E0 occurs before episode caregiving or artifact adoption.

It records:

- the fixed capability bundle;
- all protected safety, abstention, transfer, and recovery outcomes;
- the complete runtime-substrate declaration;
- caregiver availability class;
- the baseline checkpoint;
- zero or pre-existing episode costs as exact ledger entries.

A target acquisition claim requires at least one declared target capability not to pass at E0.

### E1 — post-adoption evaluation

E1 occurs after all candidate caregiving and declared adoption operations for the episode are final.

No later caregiving event may contribute to the episode after E1 begins.

E1 records:

- exact adopted artifacts or declared model updates;
- the complete substrate declaration;
- capability results on the unchanged suite;
- all protected outcomes;
- the cumulative cost ledger;
- the stable checkpoint used for E1.

A target capability must pass at E1 before retention can be tested.

### E2 — withheld-caregiver evaluation

E2 uses the same suite and evaluator bundle after caregiver disablement.

Before the first evaluator action, protected administration must prove:

- the caregiver adapter or channel is unavailable by configuration and capability guard;
- no dispatch, human bridge, model call, live chat, network route, subprocess route, dynamic caregiver retrieval, or alternate caregiver path can execute;
- every runtime substrate is declared and digest-matched;
- every caregiver-derived substrate is permitted by the declared W class;
- all prohibited temporary scaffolds are absent;
- no post-E1 caregiving or adoption occurred;
- the E2 checkpoint and lineage are exact.

Any failure invalidates E2 before capability scoring. It is not scored as an organism capability failure; it is an experiment-integrity failure.

## 7. Capability result semantics

Capability results are per-capability typed records. Aggregate score alone is insufficient.

Each capability result declares:

- capability ID and suite version;
- result type;
- exact evaluator IDs and versions;
- deterministic input or scenario ID;
- ordered outcome evidence IDs;
- required resource counters;
- final status exactly `passed`, `failed`, `abstained`, `not_reached`, or `invalid`;
- protected safety and recovery status;
- checkpoint and episode linkage.

### 7.1 Acquisition

A target capability is acquired only when:

- E0 status is not `passed`;
- E1 status is `passed`;
- the accepted caregiving-to-artifact chain is present;
- no protected capability or safety invariant regresses beyond the suite's exact declared rule.

### 7.2 Retention

A target capability is retained only when:

- E1 status is `passed`;
- E2 status is `passed` under the declared withheld class;
- E1 and E2 use the same capability and evaluator versions;
- no hidden scaffold or integrity failure exists;
- the complete cost ledger is valid.

### 7.3 Existing-capability preservation

Every capability that passed at E0 and is marked protected for the episode must pass at E1 and E2, unless the suite explicitly declares a different typed expectation before E0.

No post-hoc exclusion, reweighting, threshold change, or evaluator substitution is permitted.

### 7.4 Abstention

Correct protected abstention may be a passing outcome only when the capability suite declares it before E0.

Unplanned refusal, timeout, unavailability, or hidden caregiver fallback does not count as abstention competence.

## 8. Runtime-substrate declaration

Every evaluation point contains one exhaustive declaration of every runtime dependency available to the organism or evaluator-facing execution path.

### 8.1 Required substrate classes

The declaration must support at least:

- `model_weights`;
- `prompt_example`;
- `retrieved_memory`;
- `skill_bank`;
- `deterministic_code`;
- `rule`;
- `test`;
- `action_trace`;
- `demonstration`;
- `recovery_suffix`;
- `router`;
- `external_tool`;
- `fixture`;
- `environment_state`;
- `protected_evaluator`;
- `protected_runtime`;
- `other_declared`.

### 8.2 Exact entry requirements

Each entry declares:

- substrate ID;
- class;
- version;
- canonical digest;
- canonical or measured byte size;
- active/inactive state;
- executable/readable/callable flags as declared booleans;
- authority owner exactly `organism`, `administration`, or protected external experiment infrastructure;
- origin exactly `genesis`, `caregiver_derived`, `organism_derived`, `administration_protected`, or `environment`;
- exact source caregiving-event IDs when caregiver-derived;
- exact adoption or update evidence ID;
- checkpoint and lineage linkage;
- whether permitted in W0, W1, W2, and W3;
- whether required for the evaluated capability.

An empty list is valid only when independent source and runtime inspection prove that no substrate of that class exists.

### 8.3 Hidden-scaffold prohibition

E2 is invalid if any of the following exists:

- undeclared runtime substrate;
- declaration/runtime digest mismatch;
- caregiver-derived substrate with missing source-event provenance;
- active prompt, memory, skill, demonstration, trace, router, tool, or code path prohibited by the declared W class;
- alternate caregiver route not covered by the disablement guard;
- dynamic retrieval from an undeclared store;
- evaluator or environment modification derived from episode caregiving;
- caregiver-derived content mislabeled as organism-derived or protected infrastructure;
- a dependency used during scoring but marked inactive or not required;
- a silent model or artifact update after E1.

The evaluation must retain the failure evidence and stop before capability scoring.

## 9. Caregiving evidence and typed outcomes

This contract does not authorize a live caregiver protocol. A later design must define the exact transport and schemas.

Any future W3-conformant episode must nevertheless record typed evidence for:

- assistance request;
- response source and caregiver identity;
- assistance class;
- bounded content digest and size;
- provenance and provider/product version where applicable;
- clarification relation;
- declared confidence or abstention;
- latency and cost evidence;
- candidate transformation;
- protected verification result;
- final disposition;
- adopted substrate or declared update.

Required assistance classes must be able to represent at least:

- demonstration;
- correction;
- constraint;
- explanation;
- preference;
- question;
- defer;
- abstain.

Required final outcomes must include:

- `accepted`;
- `rejected`;
- `deferred`;
- `clarification_requested`;
- `misleading_detected`;
- `inconsistent_detected`;
- `unrepresentable`;
- `expired`;
- `invalid`.

Caregiver identity and content remain untrusted provenance. They never create canonical authority.

## 10. Verified local conversion

Every caregiver-derived substrate active at E1 or E2 must have one explicit conversion record.

The record declares:

- source caregiving-event IDs;
- candidate substrate ID/class/version/digest/size;
- transformation method ID and version;
- protected evaluator bundle;
- verification inputs and outputs;
- accepted or rejected result;
- adopting writer category;
- activation checkpoint;
- deactivation, supersession, or rollback linkage;
- exact cost contribution.

### 10.1 Inspectable artifacts

Code, rules, tests, memories, prompts, skills, demonstrations, traces, and routers must be locally inspectable, versioned, digest-bound, and attributable.

### 10.2 Model-parameter updates

A weight update is not exempt from declaration.

It must declare:

- base model identity and digest where technically available;
- update method and training-data class;
- exact permitted caregiver-output transformation class;
- resulting model identity/digest;
- training compute and storage;
- provider/legal review reference;
- verification evidence.

This contract does not authorize model training or infer permission to train on provider output.

### 10.3 No silent residue

Caregiver content that affects runtime behavior but lacks an accepted conversion record is hidden scaffold and invalidates E2.

## 11. Protected evaluator and authority

The evaluator bundle and capability suite are protected experiment infrastructure.

They must be fixed and digest-bound before E0.

The organism and caregiver must not:

- write or replace evaluators;
- modify capability definitions, thresholds, weights, scenarios, expected abstentions, or failure mappings;
- select only favorable test cases after observing outcomes;
- suppress, delete, or rewrite negative results;
- alter budget or cost rules;
- redefine substrate classes or permitted W-class dependencies;
- authorize adoption;
- transfer canonical writer authority.

Canonical writer categories remain exactly `organism` and `administration`.

Evaluator identity is not a writer category. Protected administration may record evaluator evidence; evaluator output does not directly mutate organism state.

Any later implementation must preserve a proposal/verification/adoption separation at least as strict as the Phase 2 consultation boundary.

## 12. Caregiver disablement proof

A future E2 implementation must prove technical unavailability through all of:

1. accepted configuration with caregiver allowance zero or disabled;
2. absence of live adapter capability handles;
3. guarded imports and source inspection;
4. zero dispatch, bridge, network, subprocess, model-call, or human-intervention events;
5. zero caregiver cost after the E1 cutoff;
6. fail-closed probes against every declared alternate path;
7. exact runtime-substrate declaration;
8. checkpoint-stable disablement before E2;
9. no hidden queued response, cached live response, or unresolved pre-cutoff work usable during E2;
10. an independent reconstruction of the disablement evidence.

Choosing not to call an available caregiver is W0, not W2 or W3.

## 13. Rollback and negative developmental futures

Frozen ADR 0007 remains authoritative.

The contract adds research interpretation only:

- a rollback archives the failed or abandoned developmental future;
- harmful, misleading, inconsistent, or dependency-producing assistance remains visible in that lineage;
- rollback never converts a failed episode into a successful one;
- the new lineage starts a new episode with a new E0 baseline;
- rejected candidate artifacts and failed verification records remain auditable;
- no negative result may be deleted to reduce apparent caregiver burden or improve retention rate;
- the single completed rollback limit remains exact unless a later owner-approved ADR changes it.

A W3 report must include unsuccessful episodes, not only the surviving lineage.

## 14. Required failure controls

A strong W3 research claim requires declared controls for:

- misleading assistance;
- internally inconsistent assistance;
- correct advice outside the organism's representational or action capacity;
- ambiguous advice requiring clarification;
- premature caregiver withdrawal;
- delayed withdrawal and dependency persistence;
- hidden-scaffold injection;
- stale or wrong-lineage artifact reuse;
- evaluator-targeting or test weakening;
- cost displacement into retries, compute, storage, or experimenter labor;
- caregiver outage;
- caregiver abstention;
- organism abstention;
- rollback after harmful adoption.

Each control has a predeclared expected typed outcome and cannot be omitted after observing results.

## 15. Developmental cost ledger

The cost ledger uses exact integers and declared units. Unknown is never encoded as zero.

Each field has status exactly:

- `measured`;
- `not_applicable`;
- `unmeasured`.

A W3 success claim requires every mandatory field to be `measured` or `not_applicable` with a protected reason. Any mandatory `unmeasured` field invalidates the cost-completeness claim.

### 15.1 Mandatory human fields

- active caregiver time in integer milliseconds;
- monitoring time in integer milliseconds;
- intervention time in integer milliseconds;
- artifact-review time in integer milliseconds;
- maintenance time in integer milliseconds;
- consultations;
- demonstrations;
- corrections;
- clarifications;
- abstentions;
- rejected interventions.

### 15.2 Mandatory model/service fields

- model calls;
- input tokens;
- output tokens;
- total measured latency in integer milliseconds;
- retries;
- failed calls;
- monetary cost in integer minor currency units with currency code;
- provider/product/model/version identity;
- retained-data or external-service class where applicable.

### 15.3 Mandatory environment and experiment fields

- environment interactions;
- environment resets;
- failed episodes;
- evaluator invocations;
- deterministic fixture invocations;
- experimenter administrative operations;
- wall-duration evidence as non-eligibility research metadata.

### 15.4 Mandatory compute and storage fields

- training CPU time in integer milliseconds;
- training accelerator time in integer milliseconds by declared device class;
- inference CPU time in integer milliseconds;
- inference accelerator time in integer milliseconds by declared device class;
- peak working-set bytes;
- active-state bytes;
- checkpoint-store bytes;
- caregiver-derived substrate bytes;
- total runtime-substrate bytes;
- artifact and log bytes retained for audit.

### 15.5 Cost displacement rule

Reduced caregiver burden is not a developmental gain if protected capability is maintained only by an undeclared or unmeasured increase in another required cost field.

Reports must present the complete cost vector. A scalar maturity or efficiency score is prohibited unless its formula, units, weights, missing-data behavior, and target suite are fixed before E0 in a later accepted ADR.

## 16. Required conditions and baselines

The contract distinguishes conformance tests from scientific comparison.

### 16.1 Mandatory conformance controls

Any future implementation must first support without live capability:

- no-caregiver control;
- deterministic-fixture control;
- hidden-scaffold rejection control;
- wrong-lineage evidence rejection;
- evaluator mutation rejection;
- incomplete cost-ledger rejection;
- rollback/abandoned-future evidence preservation;
- W0/W1/W2/W3 classification validation using synthetic declared substrates.

### 16.2 Mandatory research baselines for a strong claim

A later strong caregiver-withdrawal claim must compare, where technically and legally applicable:

- no-caregiver baseline;
- deterministic-fixture baseline;
- persistent prompt or skill-bank condition;
- internalized-weight condition;
- finite-demonstration policy condition;
- W3 declared local-artifact condition;
- misleading-caregiver condition;
- inconsistent-caregiver condition;
- premature-withdrawal condition.

A first implementation may build only deterministic conformance plumbing. It may not publish a W3 scientific result without the required comparison family.

## 17. Reporting requirements

Every reported developmental gain must include:

1. episode and lineage identity;
2. capability that did not pass at E0;
3. finite caregiving events;
4. accepted and rejected conversion records;
5. E0, E1, and E2 per-capability outcomes;
6. complete substrate declarations for all three points;
7. caregiver-disablement evidence;
8. hidden-scaffold validation;
9. complete cost vectors;
10. protected-capability regression results;
11. rollback and failed-episode history;
12. comparison condition results;
13. evidence limitations and unmeasured fields;
14. exact repository commit and protected test/evidence-map versions.

A report may say “intervention efficiency improved” under W0 or “live-source independence” under W1. It must not call either result W3 maturity.

## 18. Explicit exclusions

This proposed contract does not authorize:

- live human chat;
- commercial or local model calls;
- network access;
- subprocess execution;
- arbitrary code or callable execution;
- credentials;
- model training;
- memory creation;
- skill generation or adoption;
- action adoption or execution from caregiver proposals;
- continuous execution;
- new writer categories;
- schema migration;
- repeated rollback;
- increased budgets or resource ceilings;
- personality, emotion, affection, or virtual-pet mechanics;
- public novelty claims.

## 19. Acceptance and implementation gates

This contract becomes accepted only after:

1. the proposed ADR and evidence matrix are complete;
2. one exact documentation candidate passes ordinary protected CI;
3. one independent read-only design audit checks the contract against frozen Phase 1/2 and the research evidence;
4. audit findings are resolved without private semantic interpretation;
5. the project owner explicitly accepts any material new research or capability boundary;
6. the accepted status, exact commit, audit conclusion, and next action are recorded in the repository and Issues.

Acceptance of this contract still does not authorize runtime implementation.

A later implementation requires:

- separate scoped Issues and ADRs;
- a protected Phase 3 implementation matrix;
- deterministic synthetic/fixture plumbing before live sources;
- current provider/legal/privacy/cost review where applicable;
- explicit project-owner authorization for every live capability;
- an independent implementation audit before any Phase 3 freeze.

## 20. Open design questions

The following remain deliberately unresolved and must not be decided in code:

- exact database schema and table names;
- exact canonical digest domain and preimages;
- exact transport for human or model caregiving;
- exact artifact types supported by the first implementation;
- whether any model-parameter update is allowed;
- exact capability suite and evaluator bundle;
- exact experiment duration and number of episodes;
- exact provider and legal transformation classes;
- exact local model or hardware environment;
- whether repeated rollback is ever needed after the seed experiment;
- whether a scalar maturity metric should ever exist.

## 21. Exact next gate

Create and independently audit:

- proposed ADR 0017 adopting this contract as a design-only research boundary;
- `docs/PHASE3_WITHHELD_CAREGIVER_TEST_MATRIX.md` mapping every contract invariant to required protected evidence;
- an exact design-audit Issue naming the candidate commit and frozen controls.

No implementation begins at this gate.