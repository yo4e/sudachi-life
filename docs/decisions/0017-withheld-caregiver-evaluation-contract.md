# ADR 0017: Require identity-bound withheld-caregiver evaluation before maturity claims

- Status: Proposed
- Date: 2026-07-29
- Decision owners: project owner and repository maintainers
- Design issue: #132
- Audit issue: #135
- Research issues: #3, #129, and #130

## Context

Phase 1 and Phase 2 are frozen. Phase 2 proves only a bounded, source-neutral consultation boundary: caregiver-derived data receives no canonical writer authority and does not create live caregiver, memory, skill, training, action-adoption, or generic-agent capability.

Phase 3 research found that finite advice, support fading, no-helper evaluation, scaffold-free deployment, finite demonstration followed by autonomy, retained teacher prompts, skill banks, skill internalization, and selected burden measures are already established neighboring mechanisms. The remaining candidate is a protected integration and measurement protocol, not any one of those mechanisms alone.

The first proposed contract was independently audited in Issue #135 at exact head `932ff2ad8d99e8d9fb2e78a16cd12a5f1e8995c9`. The audit concluded **not ready; material design revision required** and identified ten defects: overlapping W classes, an inconsistent E2 disablement transition, invalid E0 acquisition evidence, cross-episode evidence laundering, evaluator-oracle leakage, bundled lifecycle transitions, fail-open opaque model updates, open attempt/stopping rules, incomplete cost closure, and clause-to-matrix drift.

On 2026-07-29 the project owner authorized the focused repair pass, including the protected evaluator and information-flow redesign. That authorization permits these proposed documentation corrections only. It is not acceptance of this ADR and does not authorize implementation or live capability.

## Decision

Adopt `docs/phase3/WITHHELD_CAREGIVER_EVALUATION_CONTRACT_V1.md` as the proposed Phase 3 design boundary, subject to corrected-candidate CI, an independent focused re-audit, final project-owner acceptance, and exact metadata synchronization.

### 1. W0, W1, and W2 form the availability axis; W3 is orthogonal

Every evaluation point declares exactly one mutually exclusive point-local class:

- **W0** — at least one caregiver route remains technically available;
- **W1** — every live caregiver route is unavailable while at least one declared externalized caregiver-derived runtime scaffold remains;
- **W2** — every live caregiver route and every externalized caregiver-derived scaffold is unavailable; capability may remain only in fully declared internalized policy/model state, or there may be no caregiver-derived runtime substrate.

**W3 is not a fourth availability class.** It is an episode-level conformance certification over an E2 subtype that remains explicitly W1 or W2. W3 requires identity-bound conversion, protected information flow, hidden-scaffold rejection, retained capability, complete attempt history, and final cost closure. W3 conformance is not proof of novelty.

### 2. Studies, attempts, episodes, and lineages are separately bound

Before E0, protected administration fixes a digest-bound study/run-set manifest containing the allowed claim tier, run-generation rule, exact attempt count or stopping rule, attempt ordinals, mandatory controls, and population-reconciliation rule.

Every scheduled or started attempt receives immutable identity and a terminal status. Every caregiving event, conversion, verification, adoption, activation, substrate entry, result, integrity proof, cost item, and report item binds the exact study, attempt, episode, organism, lineage, point/cutoff, and checkpoint.

A physical organism may have multiple episodes in one lineage, but evidence cannot cross episode IDs. Pre-E0 inherited substrate is baseline state and cannot prove acquisition in the new episode. Rollback ends the episode and attempt, preserves the abandoned future, increments lineage under frozen ADR 0007 semantics, and requires a new attempt and E0.

### 3. E0, E1, and E2 use one immutable protected schedule

The immutable schedule is fixed before E0 and includes the E1 cutoff and the sole legal E2 availability transition. The transition records authorized writer `administration`, before/after states, source/destination checkpoints, order, idempotent replay, and conflict behavior.

Point-local availability state is distinct from immutable configuration identity. The scheduled W0→W1 or W0→W2 transition remains in the same episode; any unplanned mutation, wrong writer, wrong checkpoint, or conflicting replay fails closed.

E0 is acquisition-eligible only when point integrity, reachability, checkpoint validity, and complete suite reconciliation are valid. Acquisition requires an exact predeclared negative status—normally `failed`, or a specifically allowed abstention—not `invalid`, `not_reached`, infrastructure failure, hidden fallback, timeout, or unplanned refusal.

### 4. Runtime substrate and model updates fail closed

Every runtime dependency is declared with exact identity, canonical digest, canonical and independently measured size, access states, non-authority `custodian`, provenance, lifecycle IDs, availability permission, and complete study/attempt/episode/lineage/checkpoint linkage.

Undeclared, mismatched, mislabeled, stale, cross-episode, cross-lineage, or availability-prohibited state is hidden scaffold and invalidates E2 before scoring.

A W2/W3 model update requires base and result identities/digests, update method and data class, compute/storage accounting, verification evidence, and all four lifecycle transitions. Missing mandatory evidence makes the update unsupported and ineligible; “technically unavailable” is not a conformance exception. Technical conformance never implies provider permission or transformation rights.

### 5. Conversion, verification, adoption, and activation are four transitions

Caregiver content remains untrusted provenance. Canonical writer categories remain exactly `organism` and `administration`.

A future implementation must represent four separate immutable linked transitions:

1. conversion produces a candidate but does not certify it;
2. verification uses a separate protected verifier but cannot adopt or activate;
3. adoption records accepted, rejected, or invalid disposition and supports accepted-but-inactive state;
4. activation requires accepted adoption and the exact stable checkpoint before runtime effect.

Each transition defines identity, status, inputs, authorized writer, ordering, cost, idempotence, conflict, no-partial-effect failure, supersession, deactivation, and rollback linkage. This ADR chooses no schema, artifact type, or implementing writer for later adoption/activation.

### 6. Conversion verification and held-out outcome evaluation are separated

Before E0, protected administration fixes distinct digest-bound identities for:

- a conversion verifier;
- a sequestered held-out outcome evaluator and capability suite;
- an information-flow policy;
- verifier probe/retry budgets and exactly disclosed feedback.

Held-out cases, expectations, scores, thresholds, and per-case results are unavailable to the organism, caregiver, converter, adoption authority, and activation authority until the attempt is terminal, except for information explicitly allowed by the pre-E0 policy. Every probe, retry, disclosure, recipient, and evaluator invocation is logged and reconciled.

Verifier/evaluator aliasing, case leakage, result leakage, adaptive probing beyond budget, retry exhaustion, or evaluator-targeted artifacts invalidates W3 conformance. Evaluator output never directly mutates organism state.

### 7. Negative attempts and failure controls are mandatory evidence

Every scheduled or started attempt remains in the study population. Post-hoc stopping, silent abandonment, ordinal reuse, and omission are invalid.

Any W3 maturity wording requires predeclared controls for misleading, inconsistent, ambiguous, unrepresentable, prematurely withdrawn, dependency-producing, hidden-scaffold, stale episode/lineage, evaluator-targeting, opaque-update, displaced-cost, outage/abstention, replay/conflict, and harmful-activation cases.

A deterministic conformance report may test synthetic mechanics but cannot claim developmental gain or maturity. A scientific comparative claim additionally requires the predeclared comparison family fixed by the contract where technically and legally applicable.

### 8. Complete costs end at one immutable closure boundary

Unknown is not zero. Mandatory fields are `measured`, `not_applicable` with protected reason, or `unmeasured`; mandatory `unmeasured` fields invalidate W3 cost completeness.

The ledger covers caregiver and experimenter labor, verifier/evaluator work, integrity investigation, report work, model/service use, environment operations, compute, storage, failures, and retries in exact declared units.

Before W3 certification, one immutable final cost-closure record reconciles E0, E1, E2, lifecycle transitions, integrity handling, administration, compute, storage, failures, evidence packaging, and report preparation/review. Premature closure, late in-scope cost, visible-but-unmeasured labor, unmatched events, or vector mismatch fails closed. No scalar maturity score is accepted.

### 9. Reporting and matrix coverage are exact

Every W3 report contains the exact fourteen top-level evidence groups fixed in the contract, including complete study population, valid E0, all lifecycle transitions, W1/W2 subtype, evaluator sequestration, final cost closure, failed attempts, stopping-rule reconciliation, and exact version provenance.

Every matrix row has a unique ID, exact normative clause/reference key, protected requirement, explicit fail-closed outcome, and plausible protected evidence. Independent gates verify matrix-ID uniqueness, normative clause coverage, exact report-field equality, and complete protected-suite collection/no-skip/assertion/blob integrity.

### 10. This remains design-only

Acceptance of this ADR and contract does not authorize code, schemas, migrations, live human/model caregivers, chat, APIs, network, subprocesses, arbitrary callables, credentials, model training, memory, skills, action adoption, new writer categories, repeated rollback, resource expansion, continuous execution, personality, or emotion state.

Each future capability requires separately accepted scope/ADRs, protected matrices, deterministic controls, current provider/legal/privacy/cost review where applicable, explicit project-owner authorization, and an independent implementation audit before freeze.

## Rationale

The corrected design prevents several false maturity claims:

- W3 cannot hide whether runtime retention is W1 externalized scaffold or W2 internalized state;
- scheduled disablement does not masquerade as an illicit configuration mutation;
- failed or invalid E0 cannot manufacture acquisition;
- old same-lineage work cannot be laundered into a new episode;
- the outcome evaluator cannot become a development oracle;
- accepted-but-inactive and failed lifecycle states remain visible;
- opaque weight changes cannot pass without identity and cost evidence;
- abandoned attempts and post-hoc stopping remain countable;
- local labor and reporting cost cannot fall outside the ledger;
- the matrix cannot silently drift from normative clauses.

These protections make the research question falsifiable while preserving frozen Phase 1/2 behavior and authority.

## Consequences

### Positive

- assistance availability and W3 conformance become deterministic orthogonal axes;
- acquisition, retention, and study-population claims have closed causal boundaries;
- evaluator leakage and adaptive test targeting become explicit integrity failures;
- every caregiver-derived runtime effect requires a complete four-transition chain;
- all failed attempts, rollbacks, hidden scaffolds, and cost displacement remain reportable;
- deterministic conformance work can precede any live capability.

### Negative

- W3 evidence is expensive and operationally demanding;
- outcome-evaluator sequestration and complete invocation accounting require protected infrastructure;
- opaque provider-managed updates may be ineligible;
- attempt registration and stopping rules reduce experimental flexibility;
- complete cost closure adds labor and instrumentation;
- a corrected candidate still requires independent focused re-audit before acceptance.

## Rejected alternatives

### Keep W3 as a fourth availability class

Rejected because valid W3 episodes necessarily retain a W1 or W2 substrate subtype, making the classes overlap.

### Disable the caregiver through an unplanned E2 configuration edit

Rejected because it breaks episode identity or permits uncontrolled mutation. Disablement must be part of the pre-E0 protected schedule.

### Treat every non-passing E0 as absence of capability

Rejected because invalid, unreachable, or infrastructure-failed baselines do not prove acquisition.

### Reuse one protected evaluator for development feedback and outcome scoring

Rejected because repeated feedback turns the held-out measure into an optimization oracle.

### Bundle conversion through activation in one record

Rejected because authority, order, accepted-but-inactive state, conflicts, and partial failure cannot be protected mechanically.

### Permit opaque model updates with incomplete identity

Rejected because W2/W3 retention cannot be attributed or reconstructed without exact base/result identity and update evidence.

### Report only completed episodes

Rejected because omitted attempts and post-hoc stopping can manufacture success.

### Close costs at E1 or before reporting work

Rejected because E2 integrity, retries, storage, investigation, and reporting can displace caregiver cost after E1.

## Required evidence before acceptance

- corrected proposed contract and matrix are internally consistent;
- all Issue #135 findings P3-D001 through P3-D010 have explicit dispositions;
- one exact corrected documentation candidate passes the full protected suite;
- one independent focused read-only re-audit confirms the corrections at that exact head;
- project-owner authorization for the evaluator/information-flow repair is durably recorded;
- final acceptance, commit, CI, audit conclusion, and next action are synchronized in the PR, Issues, and `docs/HANDOFF.md`.

Acceptance still does not authorize implementation.

## Scope

This proposed ADR defines only a research-evaluation contract and evidence gate. It does not define a database schema, transport, caregiver adapter, provider, artifact implementation, capability suite, evaluator implementation, training method, runtime budget, or Phase 3 implementation plan.
