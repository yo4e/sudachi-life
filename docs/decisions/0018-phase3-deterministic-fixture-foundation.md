# ADR 0018: Implement Phase 3 as an additive deterministic fixture-only evaluation foundation

- Status: Proposed implementation ADR — becomes accepted only with the reviewed implementation package
- Date: 2026-08-29
- Scope authorization: Issue #145, project-owner comment 5462277737
- Accepted design basis: ADR 0017 acceptance manifest and the canonical 140-row Phase 3 effective matrix
- Implementation branch: `feat/phase3-withheld-caregiver-foundation`

## Context

Phase 1 and Phase 2 are frozen controls. The accepted Phase 3 design requires executable evidence mechanics for a preregistered E0 → E1 → caregiver-unavailable → E2 episode, but it deliberately did not choose a database schema, live caregiver transport, model provider, training path, memory/skill implementation, or action-adoption route.

Issue #145 authorizes the smallest implementation foundation that can exercise those evidence mechanics with deterministic fixtures only. It explicitly does not authorize a live human/model caregiver, provider selection, network/subprocess routes, credentials, model updates, memory/skill generation, live action adoption/execution, repeated rollback, continuous execution, new writer categories, or resource expansion.

The implementation must therefore make the accepted contract mechanically testable without reopening the frozen organism runtime or smuggling a new capability into infrastructure.

## Decision

### 1. Add a pure Phase 3 evaluation package; do not change the canonical organism body

Add `src/sudachi_life/phase3/` as a pure, deterministic evidence model and validator.

The package:

- performs no SQLite writes and defines no SQLite migration;
- imports no Phase 1 or Phase 2 runtime module;
- opens no network, subprocess, model, human-chat, credential, or external-service route;
- accepts immutable Python evidence records and returns deterministic conformance results;
- never executes a caregiver-derived artifact as organism action code;
- leaves canonical writer categories exactly `organism` and `administration`.

This first foundation is an experiment/evidence layer, not a new organism lifecycle.

### 2. Use immutable typed records for the fixture-only contract projection

The implementation defines immutable records for:

- study manifest and attempt history;
- episode identity binding;
- protected E1/E2 schedule;
- deterministic fixture caregiving record;
- conversion, verification, adoption, and activation transitions;
- availability transition;
- E0/E1/E2 evaluation points;
- capability results;
- runtime-substrate declarations;
- technical caregiver-disablement proof;
- information-flow evidence;
- cumulative cost vectors;
- reviewed fourteen-group report draft;
- external final cost-closure attestation;
- one bounded mechanical publication seal.

Unknown enum states and structurally incomplete evidence fail closed in validation.

### 3. Fix the fixture-only digest convention

The accepted design intentionally left implementation digest domains open. This ADR closes them only for the new fixture evidence package.

- Raw substrate/content bytes use ordinary SHA-256 over exact bytes.
- Canonical structured fixture records use UTF-8 canonical JSON with sorted keys, no insignificant whitespace, `ensure_ascii=false`, no NaN, preceded by one single-line domain label and LF.
- The implementation never changes the accepted Phase 3 effective-registry digest or any Phase 1/2 digest convention.

The canonical design registry remains bound to SHA-256 `12cd803c821f094b5292eb052c15dc99b8f08019c1950ffe506a6a44f228bab1`, byte length `43179`.

### 4. Implement one valid deterministic W1 fixture path and independent W0/W1/W2 classification

The canonical positive fixture is intentionally W1 at E2:

- E0 and E1 are W0 because the deterministic fixture route is technically available during development;
- one fixture demonstration is terminal before the E1 cutoff;
- conversion → verification → adoption → activation is complete before E1;
- the activated caregiver-derived fixture rule is explicitly declared as an externalized W1-permitted scaffold;
- the scheduled administration-authored transition technically disables the caregiver route before E2;
- E2 retains the target capability with the declared W1 scaffold and no live source route.

The implementation also classifies W2 when all caregiver routes are unavailable and no runtime-visible externalized caregiver-derived scaffold remains. It does **not** create a W2 model update because training/model-weight updates are out of scope.

W3 remains episode-level conformance and is never represented as a point-local availability enum.

### 5. Keep fixture caregiving non-live and non-authoritative

The first positive path accepts only `source="deterministic_fixture"` caregiving evidence. Any live source identifier fails fixture-only conformance.

Fixture caregiving content is provenance only. It cannot write protected evaluator state, mutate the frozen organism runtime, certify verification, adopt, activate, or execute an action.

### 6. Implement exact residual transition writers and terminal states

Following the accepted residual amendment:

- conversion: writer `organism`, terminal success `produced`;
- verification: writer `administration`, terminal success `passed`;
- adoption: writer `administration`, terminal success `accepted` and still inactive;
- activation: writer `administration`, terminal success `activated` at the exact stable destination checkpoint.

The validator requires exactly one ordered chain for the positive fixture and rejects duplicate kinds, wrong writers, wrong order, wrong prerequisites, wrong checkpoints, conflicting identity, or post-cutoff transitions before W3 conformance.

The pure evidence layer also implements exact immutable replay semantics: same identity plus byte-equivalent structured content returns the original record, while same identity plus different content fails with a typed conflict. This proves the accepted idempotence/conflict rule without performing a second runtime effect. A future persistent implementation must preserve the same rule transactionally.

### 7. Implement the exact attempt terminal graph at study closure

A completed fixture attempt must preserve the exact history:

`scheduled → started → exactly one terminal outcome`

The terminal set is exactly:

- `e0_invalid`;
- `development_failed`;
- `rolled_back`;
- `e2_invalid`;
- `completed_unsuccessful`;
- `completed_successful`.

Any missing ordinal, duplicate ordinal, nonterminal attempt at closure, skipped `started`, or current-attempt identity mismatch blocks conformance.

This package records `rolled_back` as a possible terminal outcome but does not implement another rollback mechanism. Frozen ADR 0007 remains authoritative.

### 8. Make E2 technical unavailability explicit

The E2 disablement proof must bind the accepted schedule and exact source/destination checkpoints and must show zero:

- live adapter handles;
- post-cutoff dispatches;
- human bridges;
- model calls;
- network calls;
- subprocess calls;
- human interventions;
- caregiver cost units;
- queued/cached usable caregiver outputs.

Guarded-import, source-inspection, alternate-path-probe, and independent-reconstruction flags must all pass. A nonzero route or incomplete proof invalidates E2 before capability retention is credited.

### 9. Fail closed on hidden or inconsistent substrate evidence

Every declared substrate binds exact study/attempt/episode/organism/lineage/point/checkpoint identity, class, origin, custodian, SHA-256, canonical size, independently measured size, access state, W1/W2 permission, and capability dependency.

Caregiver-derived runtime substrate additionally requires current-episode caregiving provenance and all four transition IDs. Caregiver-derived evaluator, verifier, or environment modification is rejected.

For W1, runtime-visible caregiver-derived externalized substrate must be explicitly W1-permitted. For W2, any runtime-visible caregiver-derived externalized substrate is rejected.

### 10. Implement explicit zero-versus-unknown cost semantics

The fixture cost vector has an exact closed field set spanning the mandatory human, model/service, experiment/environment, compute, and storage classes from the accepted contract.

Each field is exactly one of:

- `measured` with a nonnegative integer;
- `not_applicable` with no numeric value and a protected reason;
- `unmeasured` with no numeric value and a reason.

A final W3 fixture closure rejects every mandatory `unmeasured` field. Measured zero is therefore distinguishable from unknown.

Cumulative measured values may not decrease between E0, E1, E2, and final closure.

### 11. Implement two-stage report finalization

The Stage-1 reviewed draft has exactly fourteen machine groups corresponding one-to-one with Contract §16:

1. `study_population`
2. `identity`
3. `e0_baseline`
4. `caregiving_events`
5. `lifecycle_transitions`
6. `capability_outcomes`
7. `substrate_declarations`
8. `caregiver_disablement`
9. `integrity`
10. `cost_vectors`
11. `protected_outcomes`
12. `negative_history`
13. `limitations`
14. `version_provenance`

The Stage-1 cost group carries the complete final vector/digest but only a pending external-closure marker. Stage 2 then creates an immutable cost-closure attestation over the reviewed-draft digest and one mechanical publication seal. The seal permits exactly one bounded serialization/link operation, zero retries, and zero semantic edits.

The fixture report explicitly states that it is deterministic conformance evidence only and makes no developmental-gain, maturity, scientific-effectiveness, or novelty claim.

## Protected evidence strategy

New tests must cover at least:

- the positive W1 E0/E1/E2 path;
- W0/W1/W2 point classification;
- exact 140 accepted atomic requirement IDs and accepted registry constants;
- nonterminal caregiving before E1;
- transition writer/order/prerequisite rejection;
- substrate digest/size/provenance/permission rejection;
- technical-disablement route rejection;
- held-out leakage rejection;
- exact attempt graph and population reconciliation;
- unmeasured mandatory cost rejection;
- protected-capability regression;
- exact fourteen-group report structure;
- publication-seal no-retry/no-edit rule;
- absence of live external imports, SQLite/Phase1/Phase2 runtime coupling, and any third writer category.

The existing repository test workflow remains unchanged and therefore continues to run the complete frozen Phase 1/2 protected suite alongside these tests.

## Consequences

### Positive

- Phase 3 evidence mechanics become executable without adding a live capability.
- Phase 1/2 frozen code remains byte-untouched by the implementation package.
- Fail-closed integrity, cost, report, and availability semantics can be audited before any real caregiver decision.
- The first valid E2 path is honest about being W1, avoiding an unauthorized model-update shortcut to W2.
- The later independent audit has a small additive surface to inspect.

### Negative

- This does not yet demonstrate real learning, maturity, or caregiver-independent competence.
- It does not persist Phase 3 records in the canonical SQLite organism body.
- It does not implement a live caregiver, W2 model internalization, memory/skill generation, or action adoption.
- A future persistent replay implementation must preserve the same idempotence/conflict rules transactionally.

## Rejected alternatives

### Add Phase 3 tables directly to schema-v2 now

Rejected because it would widen the frozen Phase 2 canonical body before the fixture evidence model has been independently audited.

### Make the first positive fixture W2 via a synthetic weight update

Rejected because Issue #145 explicitly excludes model-weight updates and training.

### Treat fixture non-use as caregiver withdrawal

Rejected. E2 requires technical route unavailability and explicit zero-route evidence.

### Reuse the held-out evaluator as the conversion verifier

Rejected by the accepted information-flow boundary.

### Let fixture advice write or execute an action

Rejected because caregiver material remains untrusted provenance and live action adoption/execution is out of scope.

## Freeze gate

This ADR and its implementation are not frozen merely because the PR passes ordinary CI. Before freeze:

1. the implementation evidence map must be synchronized;
2. the full protected suite must pass with Phase 1/2 controls intact;
3. one exact candidate head must receive an independent read-only implementation audit;
4. accepted audit findings must be repaired and revalidated;
5. `docs/HANDOFF.md`, Issue #145, and the PR must record the final candidate, CI, audit conclusion, and next gate.
