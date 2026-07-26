# ADR 0008: Keep caregiver consultation outside organism authority

- Status: Proposed
- Date: 2026-07-26
- Decision owners: project owner and repository maintainers
- Review issue: #59

## Context

Phase 1 is complete, independently re-audited, and frozen as a 152-test protected baseline. It provides one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, concrete budgets, protected action and evaluator authority, checkpoint stability, rollback evidence, and exact organism-versus-administration provenance.

Phase 2 begins the smallest possible experiment in external cognitive scaffolding. The purpose is not to add a chatbot, a generic agent framework, long-term memory, skill learning, or a live model API. The purpose is to prove that one bounded caregiver proposal can cross an explicit authority boundary without obtaining canonical authority or bypassing the Phase 1 metabolism.

ADR 0003 already requires long caregiver work to occur outside a wake transaction and to return only to a later short transaction. The remaining design questions are the exact request, response, proposal, disposition, authority, budget, expiry, initialization, comparison, and test boundaries.

## Decision

### 1. Phase 1 remains frozen

Minimal Organism Contract v0.2, ADRs 0001–0007, the Phase 1 schema and runtime behavior, and the complete 152-test suite remain a supported frozen baseline.

Phase 2 is an explicit schema-v2 extension. It must not make a Phase 1 test conditional, reinterpret a Phase 1 invariant, or silently broaden organism authority.

Any change to an existing Phase 1 trusted-kernel boundary requires separate review and protected regression evidence. The Phase 2.0 design itself does not authorize such a change.

### 2. The first experiment uses newly initialized schema-v2 organisms only

The first Phase 2 experiment does not migrate an existing Phase 1 organism.

A Phase 2 organism is newly initialized with:

- database schema version `2`
- consultation protocol version `1`
- budget configuration version `phase2-fixture-v1`
- the unchanged Phase 1 garden actions, evaluators, clock rules, checkpoint rules, rollback rules, physical storage ceilings, and authority protections
- empty Phase 2 consultation tables

Phase 1-to-Phase 2 migration, downgrade, and rollback across schema versions require a later separate decision. No wake may perform automatic migration.

### 3. Consultation uses four distinct boundaries

The first consultation round has four distinct stages.

#### A. Request wake

One organism wake may create at most one immutable consultation request after ordinary protected observation and policy evaluation establish the fixed reason `no_applicable_action` while the objective remains incomplete.

The request is recorded as canonical rows and an append-only organism event inside the existing wake transaction. The wake then commits, creates its required checkpoint, and terminates normally. It does not wait for a caregiver.

#### B. External fixture execution

Only after the request wake and checkpoint are stable may administration read the committed request and invoke the deterministic fixture.

Fixture execution occurs outside every organism wake transaction and without holding a SQLite write lock. It receives only the versioned request envelope. It receives no database connection, repository workspace, filesystem path, action executor, evaluator handle, checkpoint authority, migration authority, or rollback authority.

#### C. Administrative response ingress

Administration may submit one response envelope through a separate fail-fast `BEGIN IMMEDIATE` transaction.

Ingress validates schema versions, identifiers, request linkage, payload size, expiry eligibility, duplicate identity, adapter provenance, and cost fields before mutation. A valid response is recorded as immutable untrusted data and queued for later organism consideration.

Ingress may not adopt a proposal, execute an action, change an evaluator, raise a budget, clear maintenance, checkpoint, migrate, roll back, or alter prior history.

A byte-identical duplicate is idempotent. A conflicting duplicate, unknown version, malformed envelope, unknown request, already-consumed request, over-budget payload, or response submitted after request expiry fails closed without canonical mutation.

#### D. Disposition wake

A later organism wake may claim at most one queued proposal and record exactly one disposition:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

The disposition is append-only, idempotent, and checkpointed through the ordinary wake boundary. Current canonical state, rather than caregiver assumptions, controls the decision.

The first fixture slice stops here. An `accepted` disposition means only that the proposal was well-formed, linked, unexpired, within budget, and eligible for a later separately authorized pipeline. It does not influence the existing action selector, execute an action, create memory, change policy, or promote a skill.

Connecting an accepted `action_candidate` to action selection requires a later reviewed issue and protected tests.

### 4. Initial proposal semantics are deliberately narrow

The first fixture protocol permits exactly one proposal per response and exactly these proposal types:

- `action_candidate`
- `abstain`
- `defer`

`action_candidate` may name only an existing registered Phase 1 action and schema-valid parameters. It cannot define a new action or executable payload.

`abstain` proposes that no action be taken for a bounded reason code.

`defer` proposes that the organism postpone a decision for a bounded reason code.

No proposal type in the first slice has direct execution semantics. `explanation`, `preference`, `demonstration`, `correction`, free-form `question`, memory, and skill proposals remain out of scope.

`clarification_requested` is a disposition available for evidence and boundary testing, but the first fixture configuration permits zero clarification rounds and therefore creates no follow-up request.

### 5. Canonical writer authority remains binary

The only canonical writer authority categories remain:

- `organism`
- `administration`

Caregiver, adapter, evaluator, and repository-maintainer roles are not additional SQLite writer-authority categories.

- request creation and proposal disposition use protected `organism:consultation.*` sources
- response ingress uses protected `administration:consultation.*` sources
- caregiver identity and adapter versions are immutable provenance data inside the untrusted response envelope
- evaluators are protected repository-defined code executed under organism runtime authority; a caregiver cannot modify or self-certify them
- repository changes continue to require ordinary reviewed source changes and are not runtime canonical authority

This preserves the Phase 1 provenance distinction and prevents a caregiver label from becoming an implicit write capability.

### 6. The caregiver returns data, never commands

A caregiver response is a typed proposal envelope. The caregiver has no access to:

- canonical database connections
- SQL or migration execution
- action execution
- evaluator modification
- permission or budget modification
- checkpoint publication or repair
- rollback preparation or completion
- source or test modification
- arbitrary tools, code, shell, subprocess, network, or filesystem paths inside organism execution

Free-form human or model text is not accepted by the first protocol. A later adapter may translate external text into the typed envelope outside organism authority, but that requires a separate reviewed scope.

### 7. Independent protected evaluation precedes disposition

Before recording a disposition, the organism must independently validate:

- request, response, and proposal schema versions
- exact identifier and provenance linkage
- request reason and observation/objective references
- current organism identity and lineage generation
- current canonical state
- existing registered action and parameter schema when applicable
- permissions and protected authority
- concrete counters, payload sizes, and expiry
- duplicate, contradiction, ambiguity, and stale-state conditions

The caregiver cannot mark its own proposal successful. Outcome evaluation for any later action remains the existing protected Phase 1 evaluator boundary.

### 8. Consultation budgets are concrete and small

The first fixture budget configuration is fixed as follows.

| Resource | Limit |
| --- | ---: |
| requests created per wake | 1 |
| outstanding requests per organism | 1 |
| consultation requests over one organism lifetime | 4 |
| fixture dispatch attempts per request | 1 |
| fixture invocations over one organism lifetime | 4 |
| responses accepted per request | 1 |
| proposals per response | 1 |
| proposals considered per wake | 1 |
| dispositions per proposal | 1 |
| clarification rounds | 0 |
| request canonical JSON bytes | 16 KiB |
| complete response plus proposal canonical JSON bytes | 16 KiB |
| provenance subset within a response | 8 KiB |
| total consultation canonical payload bytes per organism | 64 KiB |
| deterministic fixture work units per invocation | 1 |
| human minutes | 0 |
| model input units | 0 |
| model output units | 0 |
| money in integer minor units | 0 |
| declared fixture latency milliseconds | 0 |

Logical payload limits supplement rather than replace the existing physical active-database, checkpoint-store, and runtime-working-set ceilings. Consultation tables, indexes, SQLite sidecars, checkpoints, staging, and rollback evidence remain included in the existing physical accounting.

Budget exhaustion produces a typed, auditable rejection or abstention and no hidden retry.

No scalar energy field is introduced.

### 9. Expiry is lifecycle-based

A request created in lifecycle `N` has `expires_after_lifecycle_number = N + 2`.

A disposition is eligible only when its recorded lifecycle number is less than or equal to that value. A disposition in lifecycle `N + 3` or later is rejected as expired.

Dispatch and ingress must also occur before the request has become ineligible according to the current committed lifecycle number.

A response may be ingressed while valid and later become stale before its disposition wake; the later wake then records one `rejected` disposition with an expiry reason.

Ambient wall time never determines canonical eligibility. Injected wall and monotonic clocks may produce audit metadata, but event sequence and lifecycle number remain authoritative.

### 10. Provenance is complete and immutable

Every request records its creating event sequence, lifecycle, lineage generation, observation/objective references, policy and budget versions, permitted action identifiers, expiry, and parent event sequences.

Every response records the request identifier, adapter type/version/instance, response status, exact proposal identifier, cost ledger, canonical payload digest, and any supersession reference. The first fixture allows no superseding response after one response has been accepted for a request.

Every proposal records its request and response identifiers, type, bounded value, rationale code, confidence basis, expiry, and required evaluator identifiers.

Every disposition records its request, response, and proposal identifiers, evaluator versions, current-state reference, exact reason code, and parent event sequences.

Prior envelopes and dispositions are immutable. Correction never edits earlier history.

### 11. Zero-caregiver behavior has two controls

#### Frozen Phase 1 control

The existing 152-test Phase 1 suite runs unchanged against schema-v1 organisms with no caregiver capability.

#### Phase 2 zero-caregiver control

A newly initialized schema-v2 organism with consultation lifetime budget `0`:

- creates no request
- performs no fixture dispatch
- accepts no response
- records no proposal or disposition
- records no caregiver cost
- performs no caregiver-derived action
- emits no consultation event

For identical declared inputs, compare the Phase 2 body with Phase 1 using a protected Phase 1-relevant projection:

1. normalize only declared contract, schema, and budget configuration version fields
2. compare every original Phase 1 table row and original-table SQLite sequence entry exactly
3. require every Phase 2 consultation table to be empty
4. require no consultation source, event type, inbox work item, cost entry, or action effect
5. compare ordinary behavior, status, lifecycle outcomes, authority provenance, checkpoint eligibility, and rollback eligibility under the same declared inputs

Phase 2 SQLite files and checkpoint digests are not expected to be byte-identical to schema-v1 files because schema-v2 contains additional empty protected objects. The protected projection, not ad hoc normalization, defines equivalence.

### 12. Narrow extension points

The first implementation may add only:

- schema-v2 initialization and validation
- protected consultation tables, indexes, and append-only constraints
- source-neutral request, response, proposal, disposition, provenance, and cost types
- one bounded request decision after the existing no-applicable-action determination
- one administrative deterministic-fixture dispatch path outside wake transactions
- one administrative immutable response-ingress path
- one later-wake proposal-disposition path
- read-only status/reporting for consultation state
- protected tests and a Phase 2 test matrix

The first implementation may not alter the existing registered garden actions, action executor authority, ordinary action selector, outcome evaluators, Phase 1 checkpoint semantics, rollback semantics, external workspace restrictions, clock access rules, or Phase 1 tests.

### 13. Planned independent audit cadence

After Issue #59, this ADR, the protocol schemas, budgets, migration decision, zero-caregiver projection, and protected test matrix are complete, one read-only Codex design audit will review the Phase 2.0 boundary.

There is no per-slice Codex audit requirement. A later single implementation audit occurs before the implemented Phase 2 baseline is frozen.

## Consequences

### Positive

- caregiver latency cannot hold the organism write transaction
- caregiver data cannot directly mutate canonical state or execute actions
- Phase 1 remains a stable regression control
- the first experiment has concrete finite work, storage, cost, and lifetime limits
- duplicate, stale, contradictory, malformed, and unavailable fixture cases can be tested without a live service
- action influence is deferred until the proposal boundary itself is proven

### Negative

- the first accepted proposal produces no action benefit
- the experiment requires a new schema-v2 initializer rather than reusing an existing organism
- the four-request lifetime cap is intentionally too small for long-lived operation
- no clarification round is possible
- byte-identical comparison with Phase 1 is impossible because schema-v2 adds protected objects

These limitations are intentional. Phase 2.0 proves authority-safe plumbing, not useful caregiver intelligence.

## Rejected alternatives

### Allow the fixture to execute a registered action directly

Rejected because it collapses proposal, evaluation, action, and authority boundaries.

### Let an accepted action candidate immediately influence the existing selector

Rejected for the first slice because a defect would combine new ingress semantics with action selection and mutation before the proposal boundary is independently protected.

### Run fixture consultation inside the wake transaction

Rejected because caregiver latency would hold write ownership and violate ADR 0003.

### Add caregiver as a canonical writer-authority category

Rejected because the caregiver is an untrusted data producer, not a SQLite authority principal.

### Begin with a live human or model caregiver

Rejected because source-neutral deterministic plumbing must be verified before privacy, consent, provider, retention, pricing, and operational concerns are introduced.

### Migrate existing Phase 1 organisms immediately

Rejected because schema migration, rollback lineage, checkpoint compatibility, and failure recovery would enlarge the first experiment without testing the core consultation boundary.

### Permit unbounded request history

Rejected because finite organism storage and caregiver use are core experimental variables.

## Scope

This ADR authorizes design review only while its status is Proposed.

Acceptance of this ADR may authorize creation of a separate test-first implementation issue for deterministic fixture consultation plumbing. It does not itself authorize implementation, live APIs, live human interaction, long-term memory, skill creation or promotion, model training, arbitrary code, network/subprocess access inside organism execution, continuous execution, personality/emotion features, or a generic agent framework.
