# ADR 0017: Require identity-bound withheld-caregiver evaluation before maturity claims

- Status: Proposed
- Date: 2026-07-29
- Decision owners: project owner and repository maintainers
- Design issue: #132
- Research issues: #3, #129, and #130

## Context

Phase 1 and Phase 2 are frozen.

Phase 2 proves that bounded caregiver-derived proposals can cross a source-neutral consultation boundary without receiving canonical writer authority, changing the Phase 1 selector, executing an action, creating memory, promoting a skill, or adding live external capability.

Phase 3 research found that neighboring systems already demonstrate:

- finite advice and intervention budgets;
- assistance requests gated by uncertainty, risk, alignment, or competence;
- full no-helper evaluation;
- scaffold-free deployment;
- finite human demonstration followed by autonomous behavior;
- teacher explanations retained in prompts after the live teacher is gone;
- persistent and pruned skill banks;
- skill internalization into model parameters;
- versioned, tested, accepted, rejected, refined, and pruned skills;
- selected prompt, intervention, data, and user-burden cost measures.

The research therefore rules out a broad SUDACHI contribution based only on reduced caregiver calls, support fading, no-helper execution, skill creation, skill pruning, or lower inference overhead.

The unresolved candidate is an integration and measurement protocol:

> one persistent bounded individual records finite caregiving, converts accepted assistance into declared and verified local capability, and retains that capability under technically unavailable caregiver access while evaluator authority, rollback lineage, hidden scaffolding, protected capabilities, and complete costs remain auditable

Without an exact contract, reduced caregiver use can be manufactured by:

- leaving the channel available but unused;
- retaining explanations, demonstrations, action traces, routers, or skill banks at runtime;
- silently updating weights;
- changing the evaluator or capability suite;
- crossing organism or lineage identity;
- deleting failed developmental futures;
- hiding cost in local compute, storage, retries, or experimenter labor.

## Decision

Adopt `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1.md` as the proposed Phase 3 design-only boundary, subject to independent design audit and explicit acceptance.

The contract defines four assistance-availability classes:

- **W0** — assistance remains available;
- **W1** — the live source is unavailable but source-derived runtime artifacts remain;
- **W2** — the assistance channel and temporary scaffold are unavailable, with capability retained in a policy or model parameters;
- **W3** — identity-bound verified local conversion under protected lineage and complete cost accounting.

Only W3 is a candidate SUDACHI maturity condition.

### 1. One comparison never crosses lineage

A developmental episode binds one organism ID, one lineage generation, one schema, one environment, one evaluator bundle, one capability suite, one protected configuration set, and one substrate baseline.

Rollback ends the episode without a success conclusion. The new lineage requires a new baseline and a new episode identity. Abandoned-lineage evidence remains immutable and cannot be substituted into the new lineage.

### 2. Three evaluation points are mandatory

Every episode contains:

- E0 pre-development baseline;
- E1 post-adoption evaluation;
- E2 withheld-caregiver evaluation.

The evaluator bundle, capability suite, environment, authority boundary, and protected configuration remain exact across all three points.

A target capability must fail or remain unsupported at E0, pass at E1, and pass at E2. Existing protected capabilities must not regress.

### 3. Caregiver unavailability is technical, not behavioral

E2 requires the caregiver route to be disabled before scoring.

Choosing not to call an available caregiver is W0.

E2 fails experiment integrity if any live or alternate caregiver path, unresolved response, cached live output, dynamic retrieval route, or prohibited external capability remains usable.

### 4. Every runtime substrate is declared

Each evaluation point must declare and digest every runtime dependency, including model weights, prompts, memories, skills, code, rules, tests, demonstrations, action traces, recovery suffixes, routers, tools, fixtures, environment state, protected evaluator code, and protected runtime code.

Every caregiver-derived substrate must link to exact caregiving events and one accepted conversion or update record.

Undeclared, mismatched, mislabeled, or prohibited caregiver-derived runtime state is hidden scaffold. E2 stops before capability scoring and retains the integrity-failure evidence.

### 5. Proposal, verification, and adoption remain separate

Caregiver content remains untrusted provenance.

Canonical writer categories remain exactly `organism` and `administration`.

Caregiver, adapter, model, evaluator, and repository maintainer do not become SQLite writer categories.

A later implementation must preserve a separation at least as strict as Phase 2:

1. caregiving evidence is received as untrusted bounded data;
2. a candidate substrate or update is derived;
3. protected evaluators independently verify it;
4. a protected adoption boundary records acceptance or rejection;
5. only accepted evidence may become active runtime substrate.

This ADR does not choose the first artifact type or authorize any adoption implementation.

### 6. Evaluators and suites are fixed before development

The evaluator bundle and capability suite are protected experiment infrastructure.

The organism and caregiver cannot modify, select after observation, weaken, reweight, suppress, or replace them.

Any version or digest change creates a different episode and cannot support the original retained-competence comparison.

### 7. Failed developmental futures remain evidence

Misleading, inconsistent, harmful, unrepresentable, prematurely withdrawn, dependency-producing, and rejected assistance remain visible.

Rollback preserves the abandoned future according to ADR 0007. It never converts a failed episode into a successful one.

A W3 report includes failed episodes and negative controls, not only the surviving lineage.

### 8. Complete costs are part of the result

The developmental cost ledger records exact integer fields for:

- human time and interventions;
- consultations, demonstrations, corrections, clarifications, and abstentions;
- model calls, tokens, latency, retries, failures, and money;
- environment interactions and resets;
- training and inference compute;
- active, checkpoint, substrate, working-set, and retained-evidence bytes;
- artifact review, maintenance, and experimenter work.

Unknown is not zero.

A required field is `measured`, `not_applicable` with protected reason, or `unmeasured`. A W3 cost-completeness claim rejects mandatory `unmeasured` fields.

No scalar maturity score is accepted by this ADR.

### 9. Controls precede live capability

A first future implementation must begin with deterministic conformance controls:

- no caregiver;
- deterministic fixture;
- synthetic W0–W3 substrate declarations;
- hidden-scaffold rejection;
- wrong-lineage rejection;
- evaluator-mutation rejection;
- incomplete-cost rejection;
- rollback and abandoned-future preservation.

A strong scientific claim later requires comparison with persistent prompt/skill support, internalized-weight support, finite-demonstration learning, misleading and inconsistent caregivers, and premature withdrawal where technically and legally applicable.

### 10. This is design-only

Acceptance of this ADR and contract does not authorize:

- a live human or model caregiver;
- human chat;
- network or subprocess access;
- arbitrary code or callable execution;
- credentials;
- memory or skill creation;
- model training;
- action adoption;
- schema migration;
- new writer authority;
- repeated rollback;
- increased budgets or resource ceilings;
- continuous execution;
- personality or emotion state.

Each capability requires a later scoped ADR, protected matrix, current provider/legal/privacy/cost review where applicable, explicit project-owner confirmation, deterministic controls, and independent implementation audit.

## Rationale

The distinction between W0, W1, W2, and W3 prevents an experiment from calling every reduction in live assistance “maturity.”

The identity and lineage binding prevent evidence laundering across rollbacks, forks, restored bodies, or different evaluator versions.

The runtime-substrate declaration makes prompts, demonstrations, traces, skills, routers, tools, code, and weight updates visible rather than treating only live model calls as dependence.

The hidden-scaffold rule converts a vague absence claim into a fail-closed integrity condition.

Protected evaluation prevents organism or caregiver improvement from changing the measuring stick.

Complete cost vectors protect the project motto from a cheap illusion: a quieter caregiver channel paired with exploding local computation, storage, retries, or human maintenance.

Deterministic conformance controls permit the contract to be tested before any live caregiver or learning mechanism is accepted.

## Consequences

### Positive

- broad caregiver-withdrawal claims become falsifiable;
- live-source absence and scaffold absence are separated;
- every caregiver-derived runtime dependency becomes auditable;
- capability retention is compared on one exact lineage and suite;
- evaluator and writer authority remain protected;
- harmful assistance and abandoned futures remain visible;
- hidden cost cannot silently substitute for caregiver burden;
- deterministic fixture work can precede live capability;
- Phase 1 and Phase 2 remain frozen controls.

### Negative

- W3 evidence is substantially more expensive than reporting fewer calls or higher task success;
- every runtime dependency requires inventory and digest evidence;
- weight updates remain difficult to inspect even when declared;
- complete cost measurement adds instrumentation and experimenter burden;
- rollback ends the current episode and requires a new baseline;
- strong claims require multiple substrate and failure-control conditions;
- some provider or model conditions may be legally or operationally unavailable.

## Rejected alternatives

### Count only caregiver calls

Rejected because better gating or an available-but-unused channel can reduce calls without increasing local competence.

### Treat no live caregiver as scaffold-free

Rejected because prompts, demonstrations, action suffixes, skill banks, routers, code, or updated weights may preserve caregiver dependence.

### Compare aggregate score only

Rejected because aggregate gains can hide protected-capability regressions, unsafe behavior, failed abstention, or selective task removal.

### Allow evaluator updates during an episode

Rejected because the comparison would no longer use one measuring stick.

### Carry successful evidence across rollback

Rejected because rollback creates a new lineage and preserves the abandoned future as evidence rather than rewriting it.

### Ignore local costs

Rejected because the project explicitly asks whether competence can survive while becoming smaller and quieter, not merely while moving expense elsewhere.

### Require live caregiver implementation before testing the contract

Rejected because the authority, hidden-scaffold, identity, cost, and evidence rules can and should be tested first with deterministic synthetic controls.

### Define one scalar maturity score now

Rejected because no accepted weighting exists across capability, caregiver burden, compute, storage, latency, abstention, and safety.

## Required evidence before acceptance

- proposed contract complete and internally consistent;
- proposed Phase 3 test/evidence matrix complete;
- exact documentation candidate passes the full protected suite;
- independent read-only design audit checks frozen Phase 1/2 compatibility, W0–W3 semantics, identity binding, substrate completeness, evaluator authority, rollback, cost completeness, controls, and exclusions;
- every accepted finding is repaired in documentation before status changes;
- project-owner confirmation for any material research-boundary change;
- exact accepted commit, audit result, and next action recorded in `docs/HANDOFF.md` and Issues.

## Scope

This proposed ADR defines only a research-evaluation contract and its evidence gate.

It does not define a database schema, transport, caregiver adapter, model provider, artifact implementation, capability suite, evaluator implementation, training method, runtime budget, or Phase 3 implementation plan.