# ADR 0008: Keep caregiver consultation outside organism authority

- Status: Proposed
- Date: 2026-07-26
- Decision owners: project owner and repository maintainers
- Review issue: #59
- Design audit: Issue #59 comment `5081639464`, audited head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647`

## Context

Phase 1 is complete, independently audited, and frozen as a 152-test protected baseline. It provides one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, concrete budgets, protected action/evaluator authority, checkpoint stability, rollback evidence, and exact organism-versus-administration provenance.

Phase 2 begins the smallest deterministic experiment in external cognitive scaffolding. It does not add a chatbot, generic agent framework, long-term memory, skill learning, live model API, or direct caregiver action. It tests whether one bounded typed proposal can cross an explicit authority boundary without obtaining canonical authority or bypassing Phase 1 metabolism.

ADR 0003 requires caregiver latency outside a wake transaction and permits return only through a later short transaction. This ADR fixes the request, dispatch, fixture, ingress, proposal, disposition, authority, budget, expiry, crash, lineage, initialization, control, and test boundaries.

The independent Phase 2.0 design audit concluded:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

This revision incorporates those corrections directly: an exact zero-caregiver projection, exact proposal and expiry constraints, exact digest preimages and logical-payload accounting, and real storage-boundary evidence for the optional request extension.

## Decision

### 1. Phase 1 remains frozen

Minimal Organism Contract v0.2, ADRs 0001–0007, schema-v1 behavior, and all 152 Phase 1 tests remain supported and unchanged.

Phase 2 is an explicit schema-v2 extension. It must not:

- make a Phase 1 test conditional
- reinterpret a Phase 1 invariant
- alter registered garden actions, selector, action executor, outcome evaluators, clock rules, checkpoint rules, rollback transformation, or authority categories
- add a hidden network, subprocess, workspace, arbitrary-code, or continuous-execution route

Any contradiction discovered during implementation returns to reviewed ADR work. Code does not choose a private interpretation.

### 2. The first experiment uses newly initialized schema-v2 organisms only

The first implementation does not migrate existing schema-v1 organisms.

A Phase 2 organism is initialized with:

- database schema version `2`
- base contract version `0.2`
- consultation protocol version `1`
- protected budget configuration `phase2-zero-caregiver-v1` or `phase2-fixture-v1`
- unchanged Phase 1 garden behavior and trusted-kernel protections
- new empty protected consultation objects

Phase 1-to-Phase 2 migration, downgrade, and rollback across schema versions require a later ADR. No wake performs automatic migration.

### 3. Consultation has five explicit boundaries

No boundary silently waits, retries, queues the next operation, invokes the fixture again, adopts a proposal, or executes an action.

#### A. Garden request wake

After the unchanged Phase 1 policy selects `no_applicable_action` for an incomplete objective, a schema-v2 fixture-configured wake may create one immutable request.

The garden outcome remains exact Phase 1 behavior:

- the same input is consumed
- the same Phase 1 action, mutation, outcome, and failure records are produced
- `consecutive_failures` increments exactly once
- request creation never resets or hides failure
- no request is created on a wake that enters `maintenance_required`

Request creation is an optional savepoint extension. A request that cannot fit logical or physical budgets is skipped or rolled back without failing an otherwise valid Phase 1 core wake. The core wake still commits and checkpoints. No partial consultation row or event remains.

The caller may receive typed noncanonical status `consultation_request_not_created_storage_budget`; it is not canonical progress or failure.

When created, the request row/event commit atomically and become checkpoint-stable before dispatch.

#### B. Administrative dispatch admission

Administration admits one dispatch only after the request checkpoint is stable, using a fresh fail-fast `BEGIN IMMEDIATE` transaction.

Admission validates exact request, lineage, lifecycle expiry, status, budgets, storage, stable checkpoint, and absence of prior dispatch or terminal state. It atomically records:

- one immutable dispatch
- one conservative protected cost charge
- one administrative event

The charge records one attempt, one charged fixture invocation, and one work unit before external work. It is never refunded. The transaction commits and releases SQLite ownership before fixture execution. Repeated admission never authorizes another call.

#### C. External deterministic fixture

The fixture executes outside every SQLite write transaction.

It receives exactly:

- the final canonical request envelope
- the protected declared fixture case identifier

It receives no database, path, workspace, repository, executor, evaluator, checkpoint, migration, rollback, network, subprocess, credential, tool, or ambient-randomness capability.

Its result is noncanonical until ingress succeeds.

#### D. Administrative ingress or dispatch terminalization

Ingress is a separate fresh fail-fast administrative transaction. Administration independently recomputes and validates:

- exact schemas and field sets
- domain-separated digest preimages, IDs, and package digest
- request, dispatch, adapter, case, organism, and current-lineage linkage
- exact proposal-type schema, evaluator set, and inherited expiry
- canonical byte sizes and lineage logical-payload formula
- active database, reserve, checkpoint-store, and working-set ceilings

Successful ingress atomically records immutable response, optional proposal, protected receipt, measured-byte cost completion, and one administrative event.

External packages contain no canonical writer authority and no authoritative cost, budget, permission, evaluator, checkpoint, migration, rollback, scheduling, or execution command. Writer authority belongs to the protected administrative receipt and event.

Byte-identical duplicate ingress is idempotent. A package rejected only because the database is busy or a checkpoint is pending may be explicitly resubmitted with identical already-produced bytes without fixture recall or another charge.

Invalid, expired, or interrupted admitted work receives one explicit terminal outcome. Reconciliation never invokes the fixture again.

#### E. Explicit disposition wake

Disposition is a separate caller-selected organism work class, not hidden inside a garden wake and not given implicit priority.

It:

- uses a fresh fail-fast wake transaction
- requires schema-v2 fixture configuration, `sleeping`, and no pending checkpoint
- claims no garden input
- selects the oldest queued current-lineage proposal by ingress event sequence then proposal ID
- considers at most one proposal
- independently validates current state, exact schemas, linkage, evaluators, permissions, budgets, and considering-lifecycle expiry
- records one final disposition
- increments lifecycle while preserving the Phase 1 garden failure streak
- creates the ordinary checkpoint

The first implementation stops at disposition. `accepted` does not enter the existing selector, execute an action, change garden state, create memory, or promote a skill.

### 4. Caregiver returns exact typed data, never commands

Protocol v1 permits one proposal in a successful response and exactly three proposal types:

- `action_candidate`
- `abstain`
- `defer`

Every proposal has the exact common field set and type-specific shape defined in `docs/phase2/CONSULTATION_PROTOCOL_V1.md`.

Common constraints include:

- proposal expiry equals the linked request expiry exactly
- fixture cannot shorten or extend expiry
- confidence basis exactly identifies the linked deterministic fixture case
- required evaluator IDs equal the protected type-specific set
- no undeclared field is accepted

Type-specific boundaries:

- `action_candidate` may name only a request-allowed registered Phase 1 action with schema-valid parameters
- `abstain` carries only the protected `no_supported_action` reason
- `defer` carries only the protected `await_state_change` reason and no schedule, retry, or wake command

One proposal receives exactly one final disposition:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

Clarification rounds are zero, so `clarification_requested` is final.

Free-form explanation, preference, demonstration, correction, question, memory, skill, source patch, test patch, arbitrary code, and tool commands remain out of scope.

### 5. Canonical writer authority remains binary

The only canonical writer categories remain:

- `organism`
- `administration`

Caregiver, adapter, evaluator, and repository maintainer are not SQLite writer categories.

- request and disposition use protected `organism:consultation.*` sources
- dispatch, ingress, and terminalization use protected `administration:consultation.*` sources
- caregiver identity, adapter version, fixture case, and external provenance are immutable untrusted provenance
- external response/proposal envelopes contain no `authority_category` or `authority_source`
- repository-defined evaluators remain protected organism-runtime code

### 6. Identifier and digest derivation is exact and acyclic

All protocol digests use the exact domain-separated function defined in the protocol:

```text
H(label, value) = sha256(
    UTF8("sudachi.consultation/v1\n" + label + "\n")
    || canonical_json(value)
)
```

The exact labels and identity objects are normative. No alternative separator, NUL, pretty JSON, implicit normalization, or undeclared field exclusion is permitted.

Derivation order is:

1. request identity and ID
2. dispatch identity and ID
3. proposal identity, proposal-content digest, and proposal ID
4. response identity and ID
5. insert response ID into final proposal linkage
6. external package digest over exactly `{response, proposals}`
7. current-state digest
8. disposition identity and ID

Proposal identity excludes response ID, preventing a cycle. Later event sequences are excluded only where explicitly declared and are inserted into final canonical envelopes/events afterward.

### 7. Independent protected evaluation precedes disposition

Organism runtime independently validates:

- protocol and object versions
- exact fields, identities, preimages, IDs, digests, and parent links
- request reason and observation/objective references
- organism identity and current lineage
- current canonical state and lifecycle
- registered action and parameter schema
- permissions and protected evaluator set
- counters, payload sizes, expiry, duplicates, contradiction, ambiguity, and stale state

Fixture output never certifies success. Any later action remains under existing Phase 1 executor/evaluator authority and requires a later design decision.

### 8. Consultation budgets use a lineage epoch

Rollback restores an older checkpoint and increments `lineage_generation`. Frozen Phase 1 rollback intentionally does not use abandoned-future evidence as mutable authority. Protocol v1 therefore uses current lineage as the consultation budget epoch.

- at most four requests per lineage
- at most four charged fixture invocations per lineage
- at most one current-lineage outstanding request
- at most 64 KiB logical consultation payload per lineage
- old-lineage rows remain immutable historical evidence and are inactive
- rollback starts a fresh bounded epoch
- ADR 0007 permits at most one completed rollback, so a physical organism has at most two epochs and eight charged fixture invocations

The exact logical-payload formula is:

```text
sum(final request envelope canonical bytes)
+ sum(successfully ingressed complete external package canonical bytes)
```

The complete package already includes response, proposal, and external provenance, so none is counted twice. The provenance limit is inside the package limit. Duplicate ingress adds zero logical bytes. Metadata remains subject to physical budgets even when excluded from logical payload.

Fixture limits include:

- request final envelope: 16 KiB
- complete external package: 16 KiB
- external provenance: 8 KiB within package limit
- total current-lineage logical payload: 64 KiB
- zero human minutes, model units, money, and declared latency
- exact per-wake/per-operation record and semantic-step caps from the protocol

All operations also obey:

- 8 MiB active database
- 40 MiB checkpoint store
- 64 MiB working set
- existing 1 MiB next-wake active-database reserve

### 9. Expiry and terminal state are lifecycle-based

A request created in lifecycle `N` is eligible for dispatch and ingress through committed lifecycle `N+2`.

Every proposal inherits exactly that request expiry. Disposition uses the new considering lifecycle:

- through `N+2`: eligible if every other check passes
- at `N+3` or later: final `rejected` with protected reason `expired`

Wall time never controls canonical eligibility.

Current-lineage state is derived from immutable rows:

- pre-dispatch request beyond expiry: terminal for dispatch and no longer outstanding
- admitted dispatch: outstanding until response or terminal outcome
- unavailable response: terminal
- successful response: outstanding until disposition
- dispatch terminal or disposition: final

No caregiver-writable mutable status flag exists.

### 10. Maintenance, checkpoints, crash, and rollback remain explicit

- request creation does not block later garden wakes
- dispatch requires sleeping and stable request checkpoint
- ingress/terminalization may record admitted evidence while sleeping or maintenance-required, but never behind pending checkpoint, rollback, or quarantine
- ingress/terminalization cannot clear maintenance
- disposition requires sleeping and cannot bypass maintenance
- garden and disposition wakes checkpoint
- dispatch, ingress, and terminalization do not checkpoint
- crash after dispatch admission remains conservatively charged and unresolved until explicit terminal reconciliation
- rollback increments lineage and makes prior-lineage consultation rows inactive
- abandoned-lineage packages/proposals fail before mutation
- ADR 0007 one-rollback rule and complete evidence retention remain unchanged

### 11. Zero-caregiver control is an exact projection, not a contradictory equality claim

Paired schema-v1 and schema-v2-zero organisms use identical declared inputs and clocks.

`phase1-projection-v1`:

1. compares every original Phase 1 table and column in deterministic order
2. permits only the declared value difference for original columns named exactly `schema_version`
3. permits only the declared value difference for original columns named exactly `budget_config_version`
4. normalizes only top-level original event-payload keys with those exact names
5. compares every nested key, other key spelling, additional/missing key, event type, sequence, authority, source, parent, and other value exactly
6. requires operational consultation tables empty and without sequence entries
7. requires no consultation event, source, cost, adapter invocation, terminal, disposition, or effect
8. compares behavior, status, lifecycle, failure streak, checkpoint eligibility, rollback eligibility, and authority exactly

Raw SQLite files and checkpoint digests are not claimed equal because schema-v2 contains additional empty protected objects. No wildcard, recursive, or semantic normalization is allowed.

### 12. Required protected evidence

`docs/PHASE2_CONSULTATION_TEST_MATRIX.md` is normative for implementation acceptance.

It requires real, not mock-only, evidence for:

- unchanged Phase 1 regression behavior
- exact zero-caregiver projection
- request extension savepoint and real 8 MiB/reserve boundary where core wake fits but consultation extension does not
- fail-fast concurrency and process crashes
- fixture lock absence and capability absence
- exact digest preimages and acyclic graph
- exact proposal field/type/expiry/evaluator constraints
- exact 64 KiB formula and no double-counting
- ingress idempotence and same-byte resubmission
- terminal reconciliation without retry
- disposition lifecycle/checkpoint behavior
- lineage filtering and rollback interactions
- physical database, checkpoint, working-set, and reserve ceilings
- explicit absence of live APIs, free text, memory, skills, training, arbitrary code, network/subprocess, continuous operation, and personality/emotion state

No test may weaken, skip, condition, or redefine the 152-test Phase 1 baseline.

### 13. Audit cadence

The Phase 2.0 design audit reviewed PR #60 head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647` and requested bounded documentation/test-matrix corrections.

Those corrections are incorporated through ordinary reviewed commits and green CI. Under `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`, a second design audit is not automatic; audit-repair-reaudit ping-pong is avoided unless evidence remains insufficient or a repair changes the same boundary so substantially that the design conclusion no longer applies.

A separate independent read-only Phase 2 implementation audit is required after the accepted design is fully implemented, all matrix requirements have protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze.

## Consequences

### Positive

- fixture latency never holds organism write ownership
- external data cannot declare authority, mutate protected state, or execute action
- external work is charged before the non-atomic boundary
- crash cannot authorize hidden retry
- exact proposal schemas prevent caregiver-controlled expiry/evaluator drift
- exact digest preimages are reproducible and non-circular
- exact logical-payload accounting prevents double-counting ambiguity
- optional request extension cannot strand an otherwise valid Phase 1 wake
- zero-caregiver behavior remains a strict, testable control
- finite work, storage, and cost limits remain concrete

### Negative

- accepted proposals provide no action benefit in the first implementation
- conservative charge may count work a crash prevented
- interrupted dispatch requires explicit reconciliation
- queued proposal may wait behind maintenance
- request extension may be omitted near storage limits
- rollback begins a fresh four-call epoch; the physical maximum is eight rather than a global four
- schema-v1 and schema-v2 files/checkpoint digests are not byte-identical
- clarification cannot round-trip

These limitations are intentional. The first Phase 2 implementation proves authority-safe plumbing, not caregiver intelligence.

## Rejected alternatives

Rejected:

- fixture executes an action directly
- accepted proposal immediately enters selector
- fixture runs inside a wake transaction
- external output is computed before dispatch charge
- admitted fixture is automatically retried after crash
- caregiver package declares writer authority, evaluator set, expiry, or authoritative cost
- caregiver becomes a canonical writer category
- automatic unified garden/proposal scheduler
- global four-call counter across rollback lineages
- failing the Phase 1 core wake solely because optional request metadata does not fit
- vague digest/size formulas left to implementation
- wildcard zero-caregiver normalization
- live human/model caregiver first
- immediate Phase 1 migration
- unbounded consultation history

## Scope

While Proposed, this ADR authorizes design review and corrections only.

Acceptance may authorize a separate test-first implementation Issue for deterministic fixture plumbing. It does not authorize live APIs/humans, memory, skills, training, arbitrary code, organism network/subprocess, continuous execution, personality/emotion features, or a generic agent framework.
