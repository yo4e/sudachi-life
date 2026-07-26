# ADR 0008: Keep caregiver consultation outside organism authority

- Status: Proposed
- Date: 2026-07-26
- Decision owners: project owner and repository maintainers
- Review issue: #59

## Context

Phase 1 is complete, independently re-audited, and frozen as a 152-test protected baseline. It provides one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, concrete budgets, protected action and evaluator authority, checkpoint stability, rollback evidence, and exact organism-versus-administration provenance.

Phase 2 begins the smallest possible experiment in external cognitive scaffolding. The purpose is not to add a chatbot, generic agent framework, long-term memory, skill learning, or live model API. The purpose is to prove that one bounded proposal can cross an explicit authority boundary without obtaining canonical authority or bypassing the Phase 1 metabolism.

ADR 0003 requires caregiver latency to remain outside a wake transaction and to return only through a later short transaction. This ADR fixes the request, dispatch, response, proposal, disposition, authority, budget, expiry, crash, initialization, comparison, and test boundaries for the first deterministic fixture.

## Decision

### 1. Phase 1 remains frozen

Minimal Organism Contract v0.2, ADRs 0001–0007, schema-v1 behavior, and the complete 152-test suite remain a supported frozen baseline.

Phase 2 is an explicit schema-v2 extension. It must not make a Phase 1 test conditional, reinterpret a Phase 1 invariant, or silently broaden organism authority.

The base `contract_version` remains `0.2`. Schema-v2 adds a consultation protocol and a protected Phase 2 budget configuration; it does not pretend to replace the accepted Phase 1 contract.

Any change to an existing Phase 1 trusted-kernel boundary requires separate review and protected regression evidence. This design authorizes no such hidden change.

### 2. The first experiment uses newly initialized schema-v2 organisms only

The first Phase 2 experiment does not migrate an existing Phase 1 organism.

A Phase 2 organism is newly initialized with:

- database schema version `2`
- consultation protocol version `1`
- one protected budget configuration: `phase2-zero-caregiver-v1` or `phase2-fixture-v1`
- unchanged Phase 1 garden actions, action selector, evaluators, clock rules, checkpoint rules, rollback rules, physical storage ceilings, and authority protections
- empty operational consultation tables

Phase 1-to-Phase 2 migration, downgrade, and rollback across schema versions require a later decision. No wake performs automatic migration.

### 3. Consultation has five explicit operational boundaries

The first consultation round has five distinct stages. No stage silently invokes the next one after a busy rejection or process restart.

#### A. Garden request wake

A schema-v2 garden wake may create at most one immutable request only after the unchanged Phase 1 policy has selected `no_applicable_action` while the objective remains incomplete.

The underlying garden lifecycle remains exactly a classified `no_applicable_action` abstention:

- it consumes the same garden tick
- it records the same Phase 1 action, mutation, and outcome accounting
- it increments `consecutive_failures` exactly once
- it never resets the failure streak merely because a request was created
- it may not create a request on a wake whose resulting failure streak enters `maintenance_required`

Request creation is an additional bounded schema-v2 effect. It does not convert failure into success or hide the original reason.

The wake commits, creates its required checkpoint, and terminates normally. It never waits for a fixture.

#### B. Administrative dispatch admission

Only after the request checkpoint is stable may administration admit one dispatch through a fresh fail-fast `BEGIN IMMEDIATE` transaction.

Dispatch admission:

- validates the exact request, current lineage, stable checkpoint, expiry, status, budgets, and absence of an earlier dispatch
- records one immutable dispatch row and one administrative event
- charges one dispatch attempt and one fixture work unit conservatively before external work begins
- commits and releases the SQLite write lock before fixture execution

The charge is not refunded if the process later crashes. Conservative pre-charging prevents hidden or undercounted external work.

A repeated dispatch admission returns the existing admitted state and must not authorize another invocation.

#### C. External deterministic fixture execution

After dispatch admission commits, the deterministic fixture executes outside every SQLite write transaction.

It receives only:

- the canonical request envelope
- the protected declared `fixture_case_id` from the dispatch admission

It receives no database connection, repository workspace, filesystem path, arbitrary configuration object, action executor, evaluator handle, checkpoint authority, migration authority, rollback authority, network capability, or subprocess capability.

#### D. Administrative response ingress or dispatch terminalization

If the fixture returns a valid package, administration may ingress it through a new fail-fast `BEGIN IMMEDIATE` transaction.

Ingress validates versions, deterministic identifiers, request and dispatch linkage, current lineage, payload sizes, expiry, duplicate identity, adapter provenance, and protected cost expectations before mutation. It records immutable untrusted response/proposal data, a protected ingress receipt, and one administrative event.

The external response package contains no canonical writer authority and no authoritative cost ledger. Writer category/source belong to the administrative ingress receipt and event. Cost is protected accounting created at dispatch admission and completed with measured ingress byte counts.

Ingress may not adopt a proposal, execute an action, change an evaluator, raise a budget, clear maintenance, checkpoint, migrate, roll back, or alter prior history.

A byte-identical duplicate is idempotent. A conflicting duplicate, unknown version, malformed package, unknown request, stale lineage, over-budget payload, or invalid linkage fails closed.

When a dispatch cannot produce an ingressible response, administration records one immutable terminal outcome instead of retrying. Initial terminal reasons are:

- `dispatch_interrupted`
- `fixture_output_invalid`
- `expired_before_ingress`

The normal dispatch command records a terminal outcome after a caught fixture or ingress failure. A process crash after dispatch admission requires an explicit bounded reconciliation command. Reconciliation never invokes the fixture again.

#### E. Explicit consultation disposition wake

Disposition is not hidden inside a garden wake and does not have implicit priority over garden input.

A caller explicitly invokes a schema-v2 consultation disposition wake. It:

- uses a fresh connection and the same fail-fast `BEGIN IMMEDIATE` wake ownership rule
- begins only from `sleeping` with no pending checkpoint
- claims no garden tick
- selects the oldest queued proposal by ingress event sequence and then proposal identifier
- considers at most one proposal
- records exactly one disposition
- creates the ordinary required checkpoint
- terminates

If no proposal is queued, maintenance is required, or a checkpoint is pending, the operation returns a typed non-mutating rejection. It is never queued to run later.

The disposition wake increments the lifecycle number but does not change the Phase 1 garden `consecutive_failures` counter. It neither counts as garden progress nor as garden failure. Schema/provenance/current-state ineligibility is expressed as a typed proposal disposition. Unexpected internal errors roll back the whole wake.

The first fixture slice stops at disposition. An `accepted` proposal does not influence the existing action selector, execute an action, create memory, change policy, or promote a skill.

### 4. Initial proposal and disposition semantics are narrow

Protocol v1 permits exactly one proposal per successful response and exactly these proposal types:

- `action_candidate`
- `abstain`
- `defer`

`action_candidate` may name only an existing registered Phase 1 action and schema-valid parameters. It cannot define a new action or executable payload.

`abstain` and `defer` are bounded proposals with no direct execution or scheduling effect.

A proposal receives exactly one of:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

A proposal of type `defer` and a disposition of `deferred` are distinct: the first is caregiver data; the second is the organism evaluator's final choice not to decide the proposal.

`clarification_requested` is final in protocol v1. Clarification rounds are zero, so it creates no follow-up request.

No proposal type in the first slice has direct execution semantics. Free-form explanation, preference, demonstration, correction, question, memory, and skill proposals remain out of scope.

### 5. Canonical writer authority remains binary

The only canonical writer categories remain:

- `organism`
- `administration`

Caregiver, adapter, evaluator, and repository-maintainer roles are not SQLite writer-authority categories.

- request creation and proposal disposition use protected `organism:consultation.*` sources
- dispatch admission, response ingress, and dispatch reconciliation use protected `administration:consultation.*` sources
- caregiver identity, adapter version, and fixture case are immutable provenance data
- external response/proposal envelopes contain no `authority_category` or `authority_source`
- protected evaluator code executes under organism runtime authority; caregiver data cannot modify or self-certify it
- repository changes continue through reviewed source changes and are not runtime canonical authority

This preserves the Phase 1 provenance distinction and prevents a caregiver label from becoming an implicit write capability.

### 6. The caregiver returns data, never commands

A fixture response is a typed data package. The fixture has no access to:

- canonical database connections
- SQL or migration execution
- action execution
- evaluator modification
- permission or budget modification
- checkpoint publication or repair
- rollback preparation or completion
- source or test modification
- arbitrary tools, code, shell, subprocess, network, or filesystem paths inside organism execution

Free-form human or model text is not accepted by protocol v1. A later adapter may translate external text into the typed package outside organism authority only after a separate reviewed decision.

### 7. Identifier derivation is ordered and non-circular

All identifiers are deterministic SHA-256 identifiers over explicit canonical JSON identity objects. The identifier being derived and later-assigned event sequence fields are excluded from their identity objects.

Derivation order is fixed:

1. derive `request_id` from request identity fields, including a canonical request ordinal, but excluding `request_event_sequence`
2. derive `dispatch_id` from `request_id`, lineage, adapter version, fixture case, and dispatch ordinal
3. derive `proposal_id` from `request_id`, `dispatch_id`, proposal ordinal, and proposal content; it excludes `response_id`
4. derive `response_id` from request/dispatch linkage, response status, adapter provenance, ordered proposal identifiers, and proposal content digests
5. insert `response_id` into the final proposal linkage and compute the complete external package digest
6. derive `disposition_id` from request/response/proposal linkage, considering lifecycle, current-state digest, evaluator versions, disposition, and reason; it excludes `disposition_event_sequence`

Tests must prove that the graph has no circular dependency and that identical declared inputs produce identical identifiers, envelopes, package digests, rows, and events.

### 8. Independent protected evaluation precedes disposition

Before recording a disposition, organism runtime independently validates:

- request, dispatch, response, proposal, and protocol versions
- exact identifier, digest, event, and provenance linkage
- request reason and observation/objective references
- current organism identity and lineage generation
- current canonical state rather than fixture assumptions
- registered action and parameter schemas when applicable
- permissions and protected authority
- concrete counters, payload sizes, and expiry
- duplicate, contradiction, ambiguity, and stale-state conditions

The fixture cannot mark its proposal successful. Outcome evaluation for any later action remains the existing protected Phase 1 evaluator boundary.

### 9. Consultation budgets are concrete and small

The `phase2-zero-caregiver-v1` configuration sets every consultation request, dispatch, response, proposal, disposition, work, and cost limit to zero.

The `phase2-fixture-v1` configuration fixes:

| Resource | Limit |
| --- | ---: |
| requests created per garden wake | 1 |
| outstanding requests per organism | 1 |
| requests over one organism lifetime | 4 |
| dispatch admissions per request | 1 |
| charged fixture invocations over one organism lifetime | 4 |
| successful responses per request | 1 |
| proposals per successful response | 1 |
| proposals considered per disposition wake | 1 |
| dispositions per proposal | 1 |
| clarification rounds | 0 |
| request canonical JSON bytes | 16 KiB |
| response-plus-proposal canonical JSON bytes | 16 KiB |
| provenance subset bytes | 8 KiB |
| total consultation logical payload bytes per organism | 64 KiB |
| fixture work units charged per dispatch | 1 |
| human minutes | 0 |
| model input units | 0 |
| model output units | 0 |
| money in integer minor units | 0 |
| declared fixture latency milliseconds | 0 |
| Phase 1 core canonical records in a garden wake | at most 16 |
| additional request records in that garden wake | at most 2 |
| total canonical records in a request garden wake | at most 18 |
| semantic steps in a disposition wake | at most 10 |
| canonical records in a disposition wake | at most 12 |
| canonical records in one dispatch admission | at most 3 |
| canonical records in one response ingress | at most 5 |
| canonical records in one dispatch terminalization | at most 3 |

Logical payload limits supplement rather than replace the existing physical active-database, checkpoint-store, and runtime-working-set ceilings.

Every Phase 2 administrative write must perform predicted and post-write physical accounting and preserve the existing 1 MiB active-database reserve for one complete next wake. The implementation must prove that a maximum permitted disposition wake and its checkpoint fit inside that reserve. If the proof fails, implementation stops and returns to design review; the reserve is not silently reduced.

Budget exhaustion produces a typed bounded result and no hidden retry. No scalar energy field is introduced.

### 10. Expiry and terminal state are lifecycle-based

A request created in lifecycle `N` has `expires_after_lifecycle_number = N + 2`.

Dispatch admission and response ingress require the current committed lifecycle number to be at most that value. A disposition wake evaluates eligibility using its new considering lifecycle number.

A response may ingress while valid and later become stale before disposition; the disposition wake then records `rejected` with reason `expired`.

Ambient wall time never determines canonical eligibility. Injected timestamps may be audit metadata, but lifecycle and event sequence remain authoritative.

Request state is derived from immutable rows:

- a request with no dispatch and current lifecycle beyond expiry is terminally expired for admission purposes and no longer counts as outstanding
- an admitted dispatch remains outstanding until a response or dispatch terminal outcome exists, even if lifecycle expiry passes
- an `unavailable` response is terminal and has no proposal or disposition
- a dispatch terminal outcome is terminal and has no response, proposal, or disposition
- a successful response remains outstanding until its proposal has one disposition
- a disposition is final

No caregiver-writable mutable status flag is authoritative.

### 11. Maintenance and concurrent work remain explicit

Creating a request never prevents later garden wakes. Current-state divergence is therefore possible and must be evaluated at disposition.

Dispatch admission requires `sleeping`, a stable checkpoint, and a currently eligible request. Response ingress or dispatch terminalization for an already admitted dispatch may record immutable administrative evidence while status is `sleeping` or `maintenance_required`; they may not clear maintenance or run organism behavior.

A consultation disposition wake requires `sleeping`. If the organism enters maintenance before disposition, the proposal remains queued until existing protected administration clears maintenance or rollback abandons that lineage. No automatic retry or maintenance bypass occurs.

### 12. Provenance is complete and immutable

Every request records its ordinal, creating event sequence, lifecycle, lineage generation, observation/objective references, policy and budget versions, permitted actions, expiry, parent events, and canonical envelope digest.

Every dispatch records its request, lineage, adapter, fixture case, charged work, admission event, and protected cost-ledger linkage.

Every external response records request/dispatch linkage, adapter identity, response status, ordered proposal identifiers, and bounded provenance. The protected ingress receipt records writer authority, ingress event, measured bytes, and complete package digest separately.

Every proposal records request, dispatch, response, type, bounded value, rationale code, confidence basis, expiry, and evaluator identifiers.

Every disposition records request/response/proposal linkage, evaluator versions, current-state digest, exact reason, lifecycle, event sequence, and parent events.

Every dispatch terminal outcome records dispatch linkage, bounded reason, optional rejected-package digest and measured bytes, and its administrative event.

Prior rows and events are immutable. Correction never edits earlier history.

### 13. Zero-caregiver behavior has two controls

#### Frozen Phase 1 control

The existing 152-test suite runs unchanged against schema-v1 organisms with no consultation capability.

#### Phase 2 zero-caregiver control

A newly initialized schema-v2 organism using `phase2-zero-caregiver-v1`:

- creates no request
- admits no dispatch
- invokes no fixture
- ingresses no response
- records no proposal, disposition, terminal outcome, or consultation cost
- emits no consultation event or source
- performs no caregiver-derived action

For identical declared inputs, compare schema-v2 with schema-v1 using a protected Phase 1-relevant projection:

1. normalize only existing `schema_version` and `budget_config_version` values
2. compare every original Phase 1 table row, column, event payload, and original-table SQLite sequence entry exactly
3. require all operational consultation tables and their sequences to be empty
4. require no consultation source, event type, inbox work item, cost entry, or action effect
5. compare ordinary behavior, status, lifecycle outcomes, authority provenance, checkpoint eligibility, and rollback eligibility

Schema-v2 must add consultation state through new protected objects rather than new columns in original Phase 1 tables. SQLite files and checkpoint digests are not expected to be byte-identical because schema-v2 contains additional empty objects.

### 14. Narrow extension points

The first implementation may add only:

- schema-v2 initialization and exact validation
- protected immutable consultation request, dispatch, response, proposal, ingress receipt, cost, disposition, and dispatch-terminal tables
- source-neutral typed envelopes and deterministic identifier/digest functions
- one bounded request decision inside the existing schema-v2 `no_applicable_action` garden path
- one administrative dispatch-admission path
- one deterministic fixture call outside all write transactions
- one administrative response-ingress path
- one administrative dispatch-terminal reconciliation path
- one explicit organism consultation-disposition wake
- read-only consultation status/reporting
- protected tests and the Phase 2 matrix

The first implementation may not alter registered garden actions, action executor authority, ordinary action selector, outcome evaluators, Phase 1 checkpoint semantics, rollback semantics, external workspace restrictions, clock access rules, or Phase 1 tests.

### 15. Planned independent audit cadence

After Issue #59, this ADR, protocol v1, budgets, no-migration decision, zero-caregiver projection, state machine, and protected test matrix are internally coherent, one read-only Codex design audit reviews the exact draft PR head.

There is no per-slice Codex audit requirement. A later single implementation audit occurs before the implemented Phase 2 baseline is frozen.

## Consequences

### Positive

- caregiver latency cannot hold organism write ownership
- external data cannot directly mutate protected state or execute actions
- dispatch work is charged before the non-atomic external boundary
- process interruption cannot authorize hidden retry
- caregiver provenance is separated from canonical writer authority
- identifier derivation is reproducible and non-circular
- garden and disposition work selection is explicit
- Phase 1 remains a stable regression control
- finite work, storage, cost, and lifetime limits are concrete
- action influence is deferred until the proposal boundary is proven

### Negative

- the first accepted proposal produces no action benefit
- conservative dispatch charging may count work that a crash prevented from completing
- an interrupted dispatch needs explicit reconciliation
- a queued proposal can wait behind maintenance until maintenance is cleared or lineage is abandoned
- the experiment requires a new schema-v2 initializer
- the four-request lifetime cap is intentionally too small for long-lived operation
- no clarification round is possible
- byte-identical comparison with schema-v1 is impossible

These limitations are intentional. Phase 2.0 proves authority-safe plumbing, not useful caregiver intelligence.

## Rejected alternatives

### Let the fixture execute a registered action directly

Rejected because it collapses proposal, evaluation, action, and authority boundaries.

### Let an accepted action candidate influence the existing selector immediately

Rejected because it combines new ingress semantics with action selection and mutation before the proposal boundary is independently protected.

### Run fixture consultation inside the wake transaction

Rejected because caregiver latency would hold write ownership and violate ADR 0003.

### Compute fixture output before charging or recording dispatch

Rejected because a process crash could create hidden unaccounted work or duplicate invocation.

### Retry an admitted dispatch after a crash

Rejected because exactly-once external work cannot be proven across the non-atomic boundary. Protocol v1 charges once and reconciles without retry.

### Put administrative authority fields or budget claims in the caregiver response

Rejected because untrusted data must not declare its own writer authority or authoritative cost.

### Add caregiver as a canonical writer category

Rejected because caregiver is a data producer, not a SQLite authority principal.

### Use one automatic wake selector for garden and proposal work

Rejected because hidden priority would change Phase 1 input behavior and complicate deterministic starvation analysis. The caller chooses an explicit bounded wake class.

### Begin with a live human or model caregiver

Rejected because deterministic source-neutral plumbing must be verified before privacy, consent, provider, retention, pricing, and operational concerns are introduced.

### Migrate existing Phase 1 organisms immediately

Rejected because migration, rollback lineage, checkpoint compatibility, and failure recovery would enlarge the first experiment without testing the core boundary.

### Permit unbounded request history

Rejected because finite organism storage and caregiver use are core experimental variables.

## Scope

This ADR authorizes design review only while its status is Proposed.

Acceptance may authorize a separate test-first implementation issue for deterministic fixture plumbing. It does not itself authorize implementation, live APIs, live human interaction, long-term memory, skill creation or promotion, model training, arbitrary code, network/subprocess access inside organism execution, continuous execution, personality/emotion features, or a generic agent framework.
