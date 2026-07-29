# Phase 3 Withheld-Caregiver Evaluation Contract v1

Status: **Proposed design — no implementation or live capability is authorized**

Tracked by: GitHub Issues #3 and #132

Research basis:

- `docs/research/CAREGIVER_WITHDRAWAL_AND_RETAINED_COMPETENCE.md`
- `docs/research/WITHDRAWAL_PROTOCOL_EXTRACTION.md`

## 1. Purpose

This contract defines the evidence required to claim that one bounded SUDACHI organism converted finite external cognitive scaffolding into retained local competence.

It does not define a live caregiver transport, model provider, training algorithm, memory system, skill implementation, action-adoption route, or schema migration.

It protects one question:

> Did one declared developmental lineage retain capability after the caregiver channel became technically unavailable, without an undeclared caregiver-derived runtime scaffold, evaluator weakening, rewritten failure history, cross-lineage evidence substitution, or hidden cost displacement?

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

## 3. Proposed versions and terms

Proposed versions:

- evaluation contract: `sudachi.withheld_caregiver_evaluation/v1`;
- assistance taxonomy: `sudachi.assistance_availability/v1`;
- developmental episode: `sudachi.developmental_episode/v1`;
- runtime-substrate declaration: `sudachi.runtime_substrate_declaration/v1`;
- evaluation point: `sudachi.evaluation_point/v1`;
- cost ledger: `sudachi.developmental_cost_ledger/v1`;
- capability result bundle: `sudachi.capability_result_bundle/v1`.

Terms:

- **caregiver** — a human or artificial source of developmental assistance;
- **caregiving event** — one later-accepted typed request, response, correction, demonstration, explanation, constraint, preference, question, deferment, abstention, or related operation;
- **runtime substrate** — every state, artifact, model, prompt element, tool, router, trace, or external dependency visible to or callable by the evaluated execution path;
- **caregiver-derived substrate** — runtime substrate whose content, selection, parameters, or existence materially depends on a caregiving event;
- **externalized scaffold** — a caregiver-derived prompt, memory, skill, demonstration, trace, code/rule artifact, router, tool, or other separately addressable runtime dependency outside internalized policy/model parameters;
- **withheld-caregiver evaluation** — evaluation where the caregiver route is technically unavailable, not merely unused;
- **retained competence** — the same declared capability remains satisfied at E2 after being established at E1;
- **developmental episode** — one immutable comparison unit bound to one organism, one lineage, one environment, one evaluator bundle, one capability suite, and three ordered evaluation points;
- **hidden scaffold** — any undeclared, mismatched, mislabeled, or W-class-prohibited caregiver-derived runtime substrate.

Unknown versions and undeclared fields fail a future conformance gate. This document does not authorize their storage or runtime implementation.

## 4. Assistance-availability classes

Every evaluation point declares exactly one class.

### W0 — assistance available

The caregiver route remains technically available during evaluation, whether or not it is used.

W0 measures intervention-aided reliability or consultation efficiency. Zero calls under an available route do not demonstrate independence.

### W1 — live source unavailable; externalized caregiver scaffold remains

The caregiver route is unavailable, but at least one declared externalized caregiver-derived scaffold remains available at runtime, including a prompt example, explanation, retrieved memory, skill bank, demonstration, action suffix, recovery trace, code/rule artifact, router, or tool.

W1 demonstrates independence from the live source only. It does not demonstrate scaffold-free operation.

### W2 — live source and externalized caregiver scaffold unavailable

The caregiver route is unavailable and no externalized caregiver-derived scaffold remains. Capability may remain only in an explicitly declared internalized policy or model-parameter update.

W2 demonstrates assistance-independent policy performance. It does not by itself establish event-level provenance, inspectable artifact lineage, protected adoption, rollback evidence, or complete cost accounting.

### W3 — identity-bound verified local conversion under protected lineage

W3 is not a stricter synonym for W2. It is the candidate SUDACHI condition in which the caregiver route is unavailable and every active caregiver-derived dependency, whether an inspectable local artifact or a declared model update, is governed by the complete protected conversion protocol.

W3 requires:

1. one identity-bound developmental episode;
2. finite recorded caregiving events;
3. an exhaustive runtime-substrate declaration at E0, E1, and E2;
4. exact provenance from each caregiver-derived substrate to caregiving events;
5. protected verification and adoption evidence;
6. technical unavailability of every caregiver route;
7. no hidden scaffold;
8. retained capability on one fixed suite;
9. protected evaluator and writer-authority boundaries;
10. preserved rollback and negative-result lineage;
11. complete mandatory cost fields;
12. no cost displacement hidden as local work.

Only W3 is a candidate SUDACHI maturity condition. Satisfying W3 is not proof of scientific novelty.

## 5. Developmental episode identity

A developmental episode identity contains exactly:

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
- caregiver-condition ID;
- substrate-baseline-condition ID;
- deterministic fixture-case or experiment-seed ID where applicable.

It excludes later result IDs, wall time, and mutable status.

### 5.1 Organism and lineage

`organism_id` identifies the physical organism record. `lineage_generation` identifies one developmental lineage.

A W3 success claim attaches to one lineage generation.

Rollback:

- preserves the abandoned future as evidence;
- increments lineage according to frozen semantics;
- ends the current episode without success;
- requires a new E0 and episode identity in the new lineage;
- forbids post-rollback results from satisfying the prior episode;
- forbids abandoned-lineage capability, cost, conversion, or substrate evidence from satisfying the new lineage.

A physical organism may contain multiple historical episodes. One retained-competence comparison never crosses lineage.

### 5.2 Fixed comparison identity

E0, E1, and E2 share exactly:

- episode ID;
- organism ID;
- lineage generation;
- environment version;
- capability-suite version and digest;
- evaluator-bundle version and digest;
- protected budget/configuration versions;
- substrate-baseline-condition ID.

Point checkpoint IDs and declared active substrates may change only according to the contract.

Any environment, suite, evaluator, authority, budget, configuration, organism, or lineage change creates a different episode.

## 6. Required evaluation points

Every episode contains exactly three ordered points.

### E0 — pre-development baseline

E0 occurs before episode caregiving or artifact adoption and records:

- every capability result;
- protected safety, abstention, transfer, and recovery outcomes;
- the complete runtime-substrate declaration;
- availability class;
- stable checkpoint;
- initial cost ledger.

A target acquisition claim requires at least one declared target capability not to pass at E0.

### E1 — post-adoption evaluation

E1 occurs after all episode caregiving and adoption operations are final.

No later caregiving event or substrate activation may contribute to the episode after E1 begins.

E1 records:

- exact adopted artifacts or declared model updates;
- complete substrate declaration;
- results on the unchanged suite;
- protected outcomes;
- cumulative costs;
- stable checkpoint.

A target capability must pass at E1 before retention is tested.

### E2 — withheld-caregiver evaluation

E2 uses the same suite and evaluator bundle after checkpoint-stable caregiver disablement.

Before scoring, protected administration must prove:

- every caregiver route is unavailable by configuration and capability guard;
- no dispatch, human bridge, model call, live chat, network route, subprocess route, dynamic caregiver retrieval, or fallback caregiver path can execute;
- every runtime substrate is declared and digest-matched;
- every caregiver-derived substrate is permitted by W3 and has valid conversion evidence;
- every W-class-prohibited scaffold is absent;
- no post-E1 caregiving, adoption, activation, or model update occurred;
- checkpoint and lineage are exact;
- no queued response, cached live output, unresolved package, or stale proposal can affect scoring.

Failure invalidates E2 before capability scoring and retains a typed experiment-integrity record. It is not scored as organism capability failure.

## 7. Capability result semantics

Results are per-capability typed records. Aggregate score alone is insufficient.

Each result declares:

- capability ID and suite version;
- exact evaluator IDs and versions;
- deterministic scenario ID;
- ordered outcome evidence IDs;
- required resource counters;
- status exactly `passed`, `failed`, `abstained`, `not_reached`, or `invalid`;
- protected safety/recovery status;
- checkpoint and episode linkage.

### Acquisition

A target capability is acquired only when:

- E0 is not `passed`;
- E1 is `passed`;
- an accepted caregiving-to-substrate chain exists;
- no protected invariant regresses beyond a rule fixed before E0.

### Retention

A target capability is retained only when:

- E1 and E2 are `passed`;
- E1 and E2 use exact suite/evaluator identity;
- E2 integrity is valid;
- mandatory cost completeness is valid.

### Existing capability preservation

Every capability that passed at E0 and was marked protected before E0 must pass at E1 and E2 unless the suite predeclares another exact typed expectation.

No post-hoc exclusion, reweighting, threshold change, or evaluator substitution is permitted.

### Abstention

Protected abstention may pass only when predeclared by the suite. Timeout, unavailable service, tool failure, hidden fallback, or unplanned refusal is not abstention competence.

## 8. Runtime-substrate declaration

Every point declares every dependency available to the organism or evaluator-facing execution path.

Required substrate classes include:

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

Each entry declares:

- substrate ID, class, and version;
- canonical digest and canonical/measured byte size;
- active state and executable/readable/callable booleans;
- **custodian** exactly `organism`, `administration`, `protected_experiment_infrastructure`, or `environment`;
- origin exactly `genesis`, `caregiver_derived`, `organism_derived`, `administration_protected`, or `environment`;
- source caregiving-event IDs when caregiver-derived;
- adoption/update evidence ID;
- checkpoint and lineage linkage;
- W-class permission;
- capability dependency.

`custodian` is inventory metadata. It never grants canonical writer authority, which remains exactly `organism` or `administration`.

An empty class list is valid only when independent source/runtime inspection proves absence.

### Hidden-scaffold prohibition

E2 is invalid for any:

- undeclared substrate;
- declaration/runtime digest or size mismatch;
- missing caregiver-event provenance;
- missing accepted conversion/update record;
- active substrate prohibited by the declared W class;
- alternate caregiver route;
- undeclared dynamic retrieval;
- caregiver-derived evaluator/environment modification;
- caregiver-derived content mislabeled as organism-derived or protected infrastructure;
- used dependency declared inactive or not required;
- silent model or artifact update after E1.

The failure stops scoring and remains auditable.

## 9. Caregiving evidence and outcomes

This contract does not authorize a live caregiver protocol. A later ADR must define exact transport and schemas.

Any future W3-conformant episode must record typed evidence for:

- assistance request;
- source and caregiver identity;
- assistance class;
- bounded content digest and size;
- provenance and product/version where applicable;
- clarification relation;
- confidence or abstention;
- latency and cost;
- candidate transformation;
- protected verification;
- final disposition;
- adopted substrate or model update.

Future assistance classes must represent at least:

- demonstration;
- correction;
- constraint;
- explanation;
- preference;
- question;
- defer;
- abstain.

Future terminal outcomes must include:

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

Every caregiver-derived substrate active at E1 or E2 has one explicit conversion record declaring:

- source caregiving-event IDs;
- candidate substrate identity, class, version, digest, and size;
- transformation method and version;
- protected evaluator bundle;
- verification inputs and outputs;
- accepted/rejected result;
- adopting writer category;
- activation checkpoint;
- deactivation, supersession, or rollback linkage;
- exact cost contribution.

Inspectable artifacts are local, versioned, digest-bound, and attributable.

A model-parameter update is not exempt. It declares, where technically available:

- base model identity/digest;
- update method and training-data class;
- permitted caregiver-output transformation class;
- resulting model identity/digest;
- training compute and storage;
- provider/legal review reference;
- verification evidence.

This contract does not authorize model training or infer permission to train on provider output.

Caregiver content that affects runtime behavior without an accepted conversion record is hidden scaffold.

## 11. Protected evaluator and authority

The evaluator bundle and capability suite are protected experiment infrastructure fixed and digest-bound before E0.

The organism and caregiver cannot:

- write or replace evaluators;
- modify capability definitions, thresholds, weights, scenarios, expected abstentions, or failure mappings;
- select only favorable cases after observing outcomes;
- suppress, delete, or rewrite negative results;
- alter budget or cost rules;
- redefine substrate classes or W-class permissions;
- authorize adoption;
- transfer writer authority.

Canonical writer categories remain exactly `organism` and `administration`.

Evaluator identity and substrate custodian are not writer categories. Protected administration may record evaluator evidence; evaluator output does not directly mutate organism state.

A later implementation preserves proposal, verification, and adoption separation at least as strict as Phase 2.

## 12. Caregiver disablement proof

A future E2 implementation proves unavailability through all of:

1. accepted configuration with caregiver allowance zero/disabled;
2. absence of live adapter capability handles;
3. guarded imports and source inspection;
4. zero post-cutoff dispatch, bridge, network, subprocess, model-call, and human-intervention events;
5. zero post-cutoff caregiver cost;
6. fail-closed probes against alternate paths;
7. exact substrate declaration;
8. checkpoint-stable disablement;
9. no usable queued/cached/unresolved caregiver output;
10. independent reconstruction of disablement evidence.

Choosing not to call an available caregiver is W0.

## 13. Rollback and negative futures

ADR 0007 remains authoritative.

Research interpretation:

- rollback archives the failed or abandoned future;
- harmful, misleading, inconsistent, unrepresentable, dependency-producing, and rejected assistance remains visible;
- rollback never converts a failed episode into success;
- the new lineage starts a new episode/E0;
- rejected substrates and failed verification remain auditable;
- negative results cannot be deleted to reduce apparent caregiver burden or improve retention rate;
- the one-completed-rollback limit remains exact.

A W3 report includes unsuccessful episodes, not only the surviving lineage.

## 14. Required failure controls

A strong W3 claim requires predeclared controls for:

- misleading assistance;
- inconsistent assistance;
- correct advice outside organism representation/action capacity;
- ambiguous advice;
- premature withdrawal;
- delayed withdrawal and dependency persistence;
- hidden-scaffold injection;
- stale/wrong-lineage artifact reuse;
- evaluator targeting or test weakening;
- cost displacement into retries, compute, storage, or experimenter labor;
- caregiver outage/abstention;
- organism abstention;
- rollback after harmful adoption.

Each control has a predeclared typed expectation and cannot be omitted after results are observed.

## 15. Developmental cost ledger

The ledger uses exact integers and declared units. Unknown is never zero.

Every field status is exactly:

- `measured`;
- `not_applicable`;
- `unmeasured`.

W3 cost completeness requires every mandatory field to be `measured` or `not_applicable` with a protected reason. Any mandatory `unmeasured` field invalidates cost completeness.

Mandatory human fields:

- active caregiver, monitoring, intervention, artifact-review, and maintenance time in integer milliseconds;
- consultation, demonstration, correction, clarification, abstention, and rejection counts.

Mandatory model/service fields:

- calls, input/output tokens, total measured latency, retries, failures, monetary cost in integer minor units with currency code, provider/product/model/version, and retained-data/service class.

Mandatory environment/experiment fields:

- interactions, resets, failed episodes, evaluator calls, fixture calls, administrative operations, and wall-duration research metadata.

Mandatory compute/storage fields:

- training/inference CPU and accelerator time by declared device class;
- peak working-set bytes;
- active-state bytes;
- checkpoint-store bytes;
- caregiver-derived and total runtime-substrate bytes;
- retained artifact/log bytes.

Reduced caregiver burden is not a developmental gain if protected capability is maintained only through an undeclared or unmeasured increase elsewhere.

Reports present the complete cost vector. No scalar maturity/efficiency score is permitted unless a later ADR fixes formula, units, weights, missing-data behavior, and target suite before E0.

## 16. Controls and baselines

### Mandatory deterministic conformance controls

Before any live capability, a future implementation must support:

- no-caregiver control;
- deterministic-fixture control;
- synthetic W0/W1/W2/W3 declarations;
- hidden-scaffold rejection;
- wrong-lineage rejection;
- evaluator-mutation rejection;
- incomplete-cost rejection;
- rollback/abandoned-future preservation.

### Mandatory research baselines for a strong claim

Where technically and legally applicable:

- no-caregiver;
- deterministic fixture;
- persistent prompt/skill bank;
- internalized weights;
- finite-demonstration policy;
- W3 declared local-artifact condition;
- misleading caregiver;
- inconsistent caregiver;
- premature withdrawal.

A first implementation may build only deterministic conformance plumbing. It cannot publish a W3 scientific result without the comparison family.

## 17. Reporting requirements

Every developmental-gain report includes:

1. episode and lineage identity;
2. capability not passed at E0;
3. finite caregiving events;
4. accepted and rejected conversions;
5. E0/E1/E2 per-capability outcomes;
6. complete substrate declarations;
7. disablement evidence;
8. hidden-scaffold validation;
9. complete cost vectors;
10. protected-capability regressions;
11. rollback and failed-episode history;
12. comparison conditions;
13. limitations and unmeasured fields;
14. repository commit and contract/matrix/suite/evaluator versions.

W0 may report intervention efficiency. W1 may report live-source independence. W2 may report assistance-independent policy performance. Only valid W3 may use the candidate maturity framing.

## 18. Explicit exclusions

This proposed contract does not authorize:

- live human chat or model calls;
- network or subprocess access;
- arbitrary code/callable execution or credentials;
- model training;
- memory/skill creation or adoption;
- action adoption/execution from caregiver proposals;
- continuous execution;
- new writer categories;
- schema migration;
- repeated rollback;
- increased budgets/resource ceilings;
- personality, emotion, affection, or virtual-pet mechanics;
- public novelty claims.

## 19. Acceptance and implementation gates

This contract becomes accepted only after:

1. proposed ADR and evidence matrix are complete;
2. one exact documentation candidate passes ordinary protected CI;
3. an independent read-only design audit checks the contract against frozen Phase 1/2 and the research evidence;
4. findings are resolved without private semantic interpretation;
5. the project owner explicitly accepts any material research-boundary change;
6. accepted status, exact commit, audit conclusion, and next action are recorded.

Acceptance still does not authorize runtime implementation.

A later implementation requires separate scope/ADRs, a protected implementation matrix, deterministic controls before live sources, current provider/legal/privacy/cost review where applicable, explicit owner authorization for live capability, and independent implementation audit before freeze.

## 20. Open design questions

Code must not privately decide:

- database schema/table names;
- canonical digest domain/preimages;
- human/model caregiver transport;
- first artifact types;
- whether model updates are allowed;
- capability suite/evaluator bundle;
- experiment duration/episode count;
- provider/legal transformation classes;
- model/hardware environment;
- repeated rollback after the seed experiment;
- any scalar maturity metric.

## 21. Exact next gate

Independently audit:

- proposed ADR 0017;
- this contract;
- `docs/PHASE3_WITHHELD_CAREGIVER_TEST_MATRIX.md`;
- one exact CI-green documentation candidate.

No implementation begins at this gate.