# ADR 0008: Keep caregiver consultation outside organism authority

- Status: Proposed
- Date: 2026-07-26
- Decision owners: project owner and repository maintainers
- Review issue: #59

## Context

Phase 1 is complete, independently audited, and frozen as a 152-test protected baseline. It provides one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, concrete budgets, protected action and evaluator authority, checkpoint stability, rollback evidence, and exact organism-versus-administration provenance.

Phase 2 begins the smallest possible experiment in external cognitive scaffolding. It does not add a chatbot, generic agent framework, long-term memory, skill learning, or live model API. It tests whether one bounded proposal can cross an explicit authority boundary without obtaining canonical authority or bypassing Phase 1 metabolism.

ADR 0003 requires caregiver latency outside a wake transaction and permits return only through a later short transaction. This ADR fixes request, dispatch, response, proposal, disposition, authority, budget, expiry, crash, rollback-lineage, initialization, comparison, and test boundaries for a deterministic fixture.

## Decision

### 1. Phase 1 remains frozen

Minimal Organism Contract v0.2, ADRs 0001–0007, schema-v1 behavior, and the complete 152-test suite remain supported and frozen.

Phase 2 is an explicit schema-v2 extension. It must not make a Phase 1 test conditional, reinterpret a Phase 1 invariant, or silently broaden organism authority.

The base `contract_version` remains `0.2`. Schema-v2 adds consultation protocol v1 and a protected Phase 2 budget configuration.

Any change to an existing Phase 1 trusted-kernel boundary requires separate review and protected regression evidence.

### 2. The first experiment uses newly initialized schema-v2 organisms only

The first Phase 2 experiment does not migrate an existing Phase 1 organism.

A Phase 2 organism is newly initialized with:

- database schema version `2`
- consultation protocol version `1`
- protected budget config `phase2-zero-caregiver-v1` or `phase2-fixture-v1`
- unchanged Phase 1 garden actions, selector, evaluators, clock rules, checkpoint rules, rollback rules, physical ceilings, and authority protections
- empty operational consultation tables

Phase 1-to-Phase 2 migration, downgrade, and rollback across schema versions require a later decision. No wake performs automatic migration.

### 3. Consultation has five explicit boundaries

No boundary silently invokes the next one after a busy rejection or process restart.

#### A. Garden request wake

A schema-v2 garden wake may create one immutable request only after the unchanged Phase 1 policy selects `no_applicable_action` while the objective remains incomplete.

The garden lifecycle remains exactly a classified Phase 1 `no_applicable_action` abstention:

- it consumes the same garden tick
- it records the same Phase 1 action, mutation, and outcome accounting
- it increments `consecutive_failures` exactly once
- request creation never resets failure
- no request is created on a wake whose resulting streak enters `maintenance_required`

Request creation is an additional bounded schema-v2 effect. It does not convert failure into success or hide the original reason.

The wake commits, creates its required checkpoint, and terminates. It never waits for a fixture.

#### B. Administrative dispatch admission

Only after the request checkpoint is stable may administration admit one dispatch through a fresh fail-fast `BEGIN IMMEDIATE` transaction.

Admission:

- validates the exact request, current lineage, stable checkpoint, expiry, status, budgets, and absence of an earlier dispatch
- records one immutable dispatch and one administrative event
- conservatively charges one dispatch attempt and one fixture work unit before external work
- commits and releases SQLite write ownership before fixture execution

The charge is not refunded after process interruption. Pre-charging prevents hidden or undercounted external work.

Repeated admission returns already-admitted state and must not authorize another invocation.

#### C. External deterministic fixture execution

After admission commits, fixture execution occurs outside every SQLite write transaction.

It receives only:

- the canonical request envelope
- the protected declared `fixture_case_id`

It receives no database connection, repository workspace, filesystem path, arbitrary configuration object, action executor, evaluator, checkpoint, migration, rollback, network, subprocess, or ambient-randomness capability.

The produced package is returned to the explicit caller or harness. It is not canonical until ingress succeeds.

#### D. Administrative response ingress or dispatch terminalization

A valid fixture package may be submitted through a separate fail-fast administrative transaction.

Ingress validates versions, deterministic identifiers, request and dispatch linkage, current lineage, payload sizes, expiry, duplicate identity, adapter provenance, and protected cost expectations. It records immutable untrusted response and proposal data, a protected ingress receipt, measured-byte completion, and one administrative event.

External response and proposal packages contain no canonical writer authority and no authoritative cost ledger. Writer category and source belong to the administrative receipt and event. Protected cost is created at dispatch admission.

Ingress may not adopt a proposal, execute an action, change evaluator, budget, or permission, clear maintenance, checkpoint, migrate, roll back, or alter prior history.

A byte-identical duplicate is idempotent. A conflicting duplicate, unknown version, malformed package, unknown request, stale lineage, over-budget package, or invalid linkage fails closed.

A valid package rejected only because the database is busy or a checkpoint is pending may be explicitly resubmitted later using the same already-produced bytes. This is not fixture retry and does not spend another fixture charge. No automatic queue or wait exists.

When a dispatch cannot produce an ingressible response, administration records one immutable terminal outcome instead of retrying:

- `dispatch_interrupted`
- `fixture_output_invalid`
- `expired_before_ingress`

Caught fixture or validation failure is terminalized by the normal administrative workflow. Process crash after dispatch admission requires explicit bounded reconciliation. Reconciliation never invokes the fixture again.

#### E. Explicit consultation disposition wake

Disposition is not hidden inside a garden wake and has no implicit priority over garden input.

A caller explicitly invokes a schema-v2 disposition wake. It:

- uses a fresh connection and fail-fast `BEGIN IMMEDIATE`
- begins only from `sleeping` with no pending checkpoint
- claims no garden tick
- selects the oldest queued proposal by ingress event sequence, then proposal identifier
- considers at most one proposal
- records exactly one disposition
- creates the ordinary required checkpoint
- terminates

No-work, maintenance, busy, unsupported, or pending-checkpoint attempts are typed, non-mutating, and never queued.

The disposition wake increments lifecycle number but preserves the Phase 1 garden `consecutive_failures` counter. It is neither garden progress nor garden failure. Proposal ineligibility becomes a typed disposition. Unexpected internal errors roll back the whole wake.

The first fixture implementation stops at disposition. `accepted` does not influence the existing action selector, execute an action, create memory, change policy, or promote a skill.

### 4. Initial proposal and disposition semantics are narrow

Protocol v1 permits one proposal per successful response and exactly:

- `action_candidate`
- `abstain`
- `defer`

`action_candidate` may name only an existing registered Phase 1 action and schema-valid parameters. It cannot define a new action or executable payload.

`abstain` and `defer` are bounded data with no direct execution or scheduling effect.

One proposal receives exactly one final disposition:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

Proposal type `defer` and disposition `deferred` are distinct. `clarification_requested` is final because clarification rounds are zero.

Free-form explanation, preference, demonstration, correction, question, memory, and skill proposals remain out of scope.

### 5. Canonical writer authority remains binary

The only canonical writer categories remain:

- `organism`
- `administration`

Caregiver, adapter, evaluator, and repository maintainer are not SQLite writer categories.

- request and disposition use protected `organism:consultation.*` sources
- dispatch, ingress, and reconciliation use protected `administration:consultation.*` sources
- caregiver identity, adapter version, and fixture case are immutable provenance
- external response and proposal contain no `authority_category` or `authority_source`
- evaluator code is protected repository-defined code under organism runtime authority
- repository changes remain reviewed source changes, not runtime authority

### 6. Caregiver returns data, never commands

The fixture has no access to:

- canonical database connections
- SQL or migration execution
- action execution
- evaluator modification
- permission or budget modification
- checkpoint publication or repair
- rollback preparation or completion
- source or test modification
- arbitrary code, shell, tools, subprocess, network, or filesystem paths inside organism execution

Free-form human or model text is not accepted. Later text adaptation requires separate reviewed scope.

### 7. Identifier derivation is ordered and non-circular

Identifiers are deterministic SHA-256 values over explicit canonical identity objects. Derived identifiers and later-assigned event sequences are excluded only where declared.

Derivation order:

1. `request_id` from request identity, current lineage, and per-lineage request ordinal; excludes request event sequence
2. `dispatch_id` from request, lineage, adapter, fixture case, and dispatch ordinal
3. `proposal_id` from request and dispatch, proposal ordinal, and proposal content; excludes response ID
4. `response_id` from request and dispatch, status, adapter provenance, ordered proposal IDs, and proposal content digests
5. insert response ID into final proposal linkage and compute the complete package digest
6. `disposition_id` from request, dispatch, response, proposal, considering lifecycle, current-state digest, evaluator versions, disposition, and reason; excludes event sequence

Protected tests must prove acyclic dependency and exact reproducibility.

### 8. Independent protected evaluation precedes disposition

Organism runtime independently validates:

- request, dispatch, response, proposal, and protocol versions
- identifiers, digests, event, and provenance linkage
- reason and observation or objective references
- current identity and lineage
- current canonical state
- registered action and parameter schema
- permissions and authority
- counters, payload sizes, and expiry
- duplicates, contradiction, ambiguity, and stale state

The fixture cannot certify success. Any later action remains under the existing Phase 1 evaluator authority.

### 9. Consultation budgets use a lineage budget epoch

Rollback restores an older checkpoint and increments `lineage_generation`. Phase 1 rollback intentionally does not consult abandoned-future artifacts to reconstruct mutable counters. Protocol v1 therefore does not claim a cross-lineage lifetime counter.

The consultation budget epoch is exactly the current `lineage_generation`.

- request ordinals and counters use only current-lineage rows
- old-lineage consultation rows remain immutable historical evidence but are never active work
- external packages must match current lineage
- rollback starts a fresh bounded consultation epoch
- ADR 0007 permits at most one completed rollback, so at most two lineage epochs and eight charged fixture invocations exist in one physical organism

A global cross-lineage limit would require changing rollback transformation or introducing another authority, so it is rejected for protocol v1.

`phase2-zero-caregiver-v1` sets every consultation request, dispatch, response, proposal, disposition, work, payload, and cost limit to zero.

`phase2-fixture-v1` fixes:

| Resource | Limit |
| --- | ---: |
| requests created per garden wake | 1 |
| outstanding requests in current lineage | 1 |
| requests per lineage budget epoch | 4 |
| dispatch admissions per request | 1 |
| charged fixture invocations per lineage epoch | 4 |
| successful responses per request | 1 |
| proposals per successful response | 1 |
| proposals considered per disposition wake | 1 |
| dispositions per proposal | 1 |
| clarification rounds | 0 |
| request JSON bytes | 16 KiB |
| response-plus-proposal JSON bytes | 16 KiB |
| provenance subset bytes | 8 KiB |
| total consultation logical payload per lineage epoch | 64 KiB |
| fixture work units charged per dispatch | 1 |
| human minutes | 0 |
| model input units | 0 |
| model output units | 0 |
| money minor units | 0 |
| declared fixture latency ms | 0 |
| Phase 1 core records in request garden wake | at most 16 |
| extra request records in that wake | at most 2 |
| total records in request garden wake | at most 18 |
| semantic steps in disposition wake | at most 10 |
| records in disposition wake | at most 12 |
| records in dispatch admission | at most 3 |
| records in response ingress | at most 5 |
| records in dispatch terminalization | at most 3 |

Logical limits supplement existing active-database, checkpoint-store, and working-set ceilings.

Every Phase 2 administrative write performs predicted and post-write accounting and preserves the existing 1 MiB active-database reserve. Implementation must prove that the maximum disposition wake plus checkpoint fits. If it does not, return to design review; never silently reduce the reserve.

Budget exhaustion is typed and bounded with no hidden retry. No scalar energy exists.

### 10. Expiry and terminal state are lifecycle-based

A request created in lifecycle `N` has expiry `N + 2`.

Dispatch and ingress require the current committed lifecycle at most expiry. Disposition eligibility uses the new considering lifecycle.

A response may ingress validly and become stale before disposition; the later wake records `rejected` with reason `expired`.

Wall time never controls canonical eligibility.

Current-lineage request state is derived from immutable rows:

- no dispatch and lifecycle beyond expiry: terminally expired for admission and no longer outstanding
- admitted dispatch: outstanding until response or dispatch terminal, even after expiry
- unavailable response: terminal, with no proposal or disposition
- dispatch terminal: terminal, with no response, proposal, or disposition
- successful response: outstanding until one disposition
- disposition: final

Rows from earlier lineage generations are historical and never count as current outstanding work or current epoch budget.

### 11. Maintenance and concurrent work remain explicit

Request creation does not block later garden wakes; current state may diverge before disposition.

Dispatch admission requires `sleeping`, no pending checkpoint, and an eligible current-lineage request.

Ingress or terminalization for an already admitted current-lineage dispatch may record evidence while `sleeping` or `maintenance_required`, but only with no pending checkpoint and no rollback or quarantine. It cannot clear maintenance or run organism behavior.

Disposition requires `sleeping`. If maintenance begins first, the proposal waits until protected administration clears maintenance or rollback abandons that lineage. No automatic retry or maintenance bypass occurs.

### 12. Provenance is complete and immutable

Request, dispatch, response, proposal, ingress receipt, disposition, cost, and dispatch-terminal records preserve exact version, lineage, identifier, digest, event, budget, and parent linkage.

All rows and events are immutable. Correction never edits prior history.

### 13. Zero-caregiver behavior has two controls

#### Frozen Phase 1 control

All 152 tests run unchanged against schema-v1 with no consultation capability.

#### Schema-v2 zero-caregiver control

`phase2-zero-caregiver-v1`:

- creates no request
- admits no dispatch
- invokes no fixture
- ingresses no response
- records no proposal, disposition, terminal, or cost
- emits no consultation event or source
- performs no caregiver-derived action

Protected Phase 1-relevant projection:

1. normalize only existing `schema_version` and `budget_config_version`
2. compare every original Phase 1 row, column, event payload, and original-table SQLite sequence exactly
3. require operational consultation tables and sequences empty
4. require no consultation source, event, inbox, cost, or effect
5. compare behavior, status, lifecycle, authority, checkpoint, and rollback eligibility

Schema-v2 adds new protected objects, never new columns to original Phase 1 tables. SQLite bytes and checkpoint digests differ because empty objects exist.

### 14. Narrow extension points

The first implementation may add only:

- schema-v2 initialization and validation
- immutable request, dispatch, cost, response, proposal, receipt, disposition, and dispatch-terminal objects
- typed envelopes and deterministic identifier and digest functions
- request admission inside the schema-v2 no-applicable-action garden path
- administrative dispatch admission
- deterministic fixture execution outside write transactions
- administrative response ingress
- administrative dispatch-terminal reconciliation
- explicit organism disposition wake
- read-only consultation reporting
- protected tests and matrix evidence

It may not alter registered garden actions, executor authority, selector, outcome evaluators, Phase 1 checkpoint or rollback semantics, external workspace rules, clock rules, or Phase 1 tests.

### 15. Independent audit cadence

There is no separate Codex audit for this design decision.

Issue #59 and this ADR are accepted through ordinary repository review. Phase 2 is then implemented through bounded test-first slices mapped to `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`.

Run one independent read-only Codex audit only after the complete Phase 2 implementation, unchanged Phase 1 suite, Phase 2 protected matrix, and CI evidence form a candidate baseline ready to freeze.

No per-slice, per-PR, or intermediate design audit is required.

## Consequences

### Positive

- fixture latency never holds organism write ownership
- external data cannot mutate protected state or execute an action
- work is charged before the non-atomic boundary
- crash cannot authorize hidden fixture retry
- writer authority is separate from caregiver provenance
- identifier graph is acyclic and reproducible
- garden and disposition selection are explicit
- Phase 1 remains the stable control
- finite work, storage, and cost limits are concrete
- action influence waits for later review

### Negative

- accepted proposal gives no action benefit in the first implementation
- conservative charge may count work a crash prevented
- interrupted dispatch requires explicit reconciliation
- queued proposal may wait behind maintenance
- rollback begins a new four-call lineage epoch; with ADR 0007 the maximum total is eight rather than a global four
- a new schema-v2 initializer is required
- clarification cannot round-trip
- schema-v1 and schema-v2 files are not byte-identical

These limitations are intentional. The first Phase 2 implementation proves authority-safe plumbing, not caregiver intelligence.

## Rejected alternatives

Rejected alternatives include:

- fixture executes an action directly
- accepted proposal immediately influences the selector
- fixture runs inside a wake transaction
- fixture output is computed before dispatch charge
- admitted dispatch is automatically retried after crash
- caregiver package declares writer authority or authoritative cost
- caregiver becomes a canonical writer category
- automatic unified garden and proposal scheduler
- global four-call counter across rollback lineages
- live human or model caregiver first
- immediate Phase 1 migration
- unbounded consultation history

Each is rejected because it collapses authority boundaries, hides work or retries, alters frozen Phase 1 behavior, or violates finite storage and cost requirements.

## Scope

While Proposed, this ADR authorizes design review only.

Acceptance may authorize a separate test-first implementation Issue for deterministic fixture plumbing. It does not itself authorize live APIs or humans, memory, skills, training, arbitrary code, network or subprocess access inside organism execution, continuous execution, personality or emotion features, or a generic agent framework.