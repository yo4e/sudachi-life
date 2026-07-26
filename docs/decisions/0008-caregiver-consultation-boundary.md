# ADR 0008: Keep caregiver consultation outside organism authority

- Status: Accepted
- Date: 2026-07-26
- Decision owners: project owner and repository maintainers
- Review issue: #59
- Design audit: Issue #59 comment `5081639464`
- Audited head: `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647`
- Corrected design CI: run 384, 152 passed

## Context

Phase 1 is complete, independently audited, and frozen as a 152-test protected baseline. It provides one canonical SQLite body, append-only sequence-ordered events, injected clocks, fail-fast write ownership, concrete budgets, protected action/evaluator authority, checkpoint stability, rollback evidence, and exact organism-versus-administration provenance.

Phase 2 begins the smallest deterministic experiment in external cognitive scaffolding. It does not add a chatbot, generic agent framework, long-term memory, skill learning, live model API, or direct caregiver action. It tests whether one bounded typed proposal can cross an explicit authority boundary without obtaining canonical authority or bypassing Phase 1 metabolism.

The independent Phase 2.0 design audit concluded:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

The required corrections were incorporated into:

- `docs/phase2/CONSULTATION_PROTOCOL_V1.md`
- `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`
- this ADR

They fix the zero-caregiver projection, proposal/expiry constraints, digest preimages, 64 KiB accounting formula, and real request-wake storage-boundary evidence.

## Decision

### 1. Phase 1 remains frozen

Minimal Organism Contract v0.2, ADRs 0001–0007, schema-v1 behavior, and all 152 Phase 1 tests remain supported and unchanged.

Phase 2 is an explicit schema-v2 extension. It must not:

- make a Phase 1 test conditional
- reinterpret a Phase 1 invariant
- alter registered garden actions, selector, action executor, outcome evaluators, clock rules, checkpoint rules, rollback transformation, or authority categories
- add hidden network, subprocess, workspace, arbitrary-code, or continuous-execution routes

Any implementation contradiction returns to reviewed ADR work. Code does not choose a private interpretation.

### 2. The first experiment uses newly initialized schema-v2 organisms only

The first implementation does not migrate existing schema-v1 organisms.

A Phase 2 organism is initialized with:

- database schema version `2`
- base contract version `0.2`
- consultation protocol version `1`
- unchanged protected Phase 1 budget configuration `phase1-v1`
- one protected `consultation_configuration` singleton with protocol version `1` and configuration `phase2-zero-caregiver-v1` or `phase2-fixture-v1`
- unchanged Phase 1 garden behavior and trusted-kernel protections
- new empty protected consultation objects

Migration, downgrade, and rollback across schema versions require a later ADR. No wake performs automatic migration.

### 3. Consultation has five explicit boundaries

No boundary silently waits, retries, queues the next operation, invokes the fixture again, adopts a proposal, or executes an action.

#### A. Garden request wake

After the unchanged Phase 1 policy selects `no_applicable_action` for an incomplete objective, a fixture-configured schema-v2 wake may create one immutable request.

The core garden outcome remains exact Phase 1 behavior:

- same input consumption
- same Phase 1 action, mutation, outcome, and failure records
- `consecutive_failures` increments exactly once
- request creation never resets or hides failure
- no request on a wake entering `maintenance_required`

Request creation is an optional savepoint extension. If consultation metadata alone cannot fit logical or physical limits, the extension is skipped or rolled back while the valid Phase 1 core wake and ordinary checkpoint still commit. No partial consultation state remains.

When created, request row/event commit atomically and become checkpoint-stable before dispatch.

#### B. Administrative dispatch admission

Administration admits one dispatch only after the request checkpoint is stable, using a fresh fail-fast `BEGIN IMMEDIATE` transaction.

Admission validates exact request, lineage, expiry, status, budgets, storage, stable checkpoint, and absence of prior dispatch/terminal state. It atomically records one dispatch, one conservative protected cost charge, and one administrative event.

One fixture attempt/work unit is charged before external work and never refunded. The transaction commits and releases SQLite ownership before fixture execution. Repeated admission never authorizes another call.

#### C. External deterministic fixture

Fixture execution occurs outside every SQLite write transaction.

It receives exactly:

- final canonical request envelope
- protected declared fixture case identifier

It receives no database, path, workspace, repository, executor, evaluator, checkpoint, migration, rollback, network, subprocess, credential, tool, or ambient-randomness capability.

Its result remains noncanonical until ingress succeeds.

#### D. Administrative ingress or terminalization

Ingress is a separate fresh fail-fast administrative transaction. Administration independently verifies exact schemas, fields, digest preimages, IDs, package digest, request/dispatch/adapter/case/lineage linkage, exact proposal shape, evaluator set, inherited expiry, canonical sizes, logical payload, and physical budgets.

Successful ingress atomically records immutable response, optional proposal, protected receipt, measured-byte cost completion, and one administrative event.

External packages contain no canonical writer authority and no authoritative cost, budget, permission, evaluator, checkpoint, migration, rollback, scheduling, or execution command. Writer authority belongs to protected administration.

Byte-identical duplicate ingress is idempotent. A valid package rejected only by busy ownership or pending checkpoint may be explicitly resubmitted with identical already-produced bytes without fixture recall or another charge.

Invalid, expired, or interrupted admitted work receives one explicit terminal outcome. Reconciliation never invokes the fixture again.

#### E. Explicit disposition wake

Disposition is a separate caller-selected organism work class, not hidden inside a garden wake and not given implicit priority.

It:

- uses a fresh fail-fast wake transaction
- requires fixture-configured schema-v2, `sleeping`, and no pending checkpoint
- claims no garden input
- selects oldest queued current-lineage proposal by ingress event sequence then proposal ID
- considers at most one proposal
- independently validates current state, exact schemas, linkage, evaluators, permissions, budgets, and considering-lifecycle expiry
- records one final disposition
- increments lifecycle while preserving the Phase 1 garden failure streak
- creates the ordinary checkpoint

The first implementation stops at disposition. `accepted` does not enter the selector, execute action, change garden state, create memory, or promote a skill.

### 4. Caregiver returns exact typed data, never commands

Protocol v1 permits exactly three proposal types:

- `action_candidate`
- `abstain`
- `defer`

Every proposal uses the exact common field set and type-specific shape fixed in the protocol.

Common constraints:

- proposal expiry equals linked request expiry exactly
- fixture cannot shorten or extend expiry
- confidence basis exactly identifies linked fixture case
- required evaluator IDs equal the protected type-specific set
- no undeclared field is accepted

Type-specific boundaries:

- `action_candidate` names only a request-allowed registered Phase 1 action with schema-valid parameters
- `abstain` carries only protected reason `no_supported_action`
- `defer` carries only protected reason `await_state_change` and no schedule/retry/wake command

One proposal receives exactly one final disposition:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

Clarification rounds are zero, so clarification is final.

Free-form explanation, preference, demonstration, correction, question, memory, skill, source/test patch, arbitrary code, and tool commands remain out of scope.

### 5. Canonical writer authority remains binary

Only canonical writer categories:

- `organism`
- `administration`

Caregiver, adapter, evaluator, and repository maintainer are not SQLite writer categories.

- request/disposition use protected `organism:consultation.*` sources
- dispatch/ingress/terminalization use protected `administration:consultation.*` sources
- caregiver identity, adapter version, fixture case, and external provenance are immutable untrusted provenance
- external response/proposal envelopes contain no authority fields
- repository-defined evaluators remain protected organism-runtime code

### 6. Digest derivation is exact and acyclic

All protocol digests use:

```text
H(label, value) = sha256(
    UTF8("sudachi.consultation/v1\n" + label + "\n")
    || canonical_json(value)
)
```

Exact labels, identity objects, exclusions, separators, canonical bytes, and package preimage are normative. No alternative NUL, formatting, implicit normalization, or undeclared exclusion is permitted.

Derivation order:

1. request identity/ID
2. dispatch identity/ID
3. proposal identity/content digest/ID
4. response identity/ID
5. insert response ID into final proposal linkage
6. package digest over exactly `{response, proposals}`
7. current-state digest
8. disposition identity/ID

Proposal identity excludes response ID, preventing a cycle. Later event sequences are excluded only where explicitly declared.

### 7. Independent evaluation precedes disposition

Organism runtime independently validates versions, exact fields, identities, preimages, IDs, digests, parents, observation/objective references, organism/lineage/current state, action schemas, permissions, evaluator set, counters, payload sizes, expiry, duplicates, contradiction, ambiguity, and staleness.

Fixture output never certifies success. Any later action remains under existing Phase 1 executor/evaluator authority and requires a later design decision.

### 8. Consultation budgets use current lineage

Current `lineage_generation` is the consultation budget epoch.

- at most four requests per lineage
- at most four charged fixture invocations per lineage
- at most one current-lineage outstanding request
- at most 64 KiB logical consultation payload per lineage
- old-lineage rows remain immutable historical evidence and inactive
- rollback starts a fresh bounded epoch
- ADR 0007 permits at most one completed rollback, so a physical organism has at most two epochs/eight charged fixture invocations

Exact logical payload:

```text
sum(final request envelope canonical bytes)
+ sum(successfully ingressed complete external package canonical bytes)
```

The package contains response, proposal, and provenance, so none is counted twice. Provenance is inside the package limit. Duplicate ingress adds zero logical bytes. Metadata remains subject to physical ceilings.

Limits:

- request final envelope: 16 KiB
- complete external package: 16 KiB
- external provenance: 8 KiB within package limit
- total current-lineage logical payload: 64 KiB
- zero human/model/money/declared latency
- exact record/step caps from protocol
- 8 MiB active database
- 40 MiB checkpoint store
- 64 MiB working set
- 1 MiB next-wake active-database reserve

### 9. Expiry is lifecycle-based

A request created in lifecycle `N` is eligible for dispatch/ingress through committed lifecycle `N+2`.

Every proposal inherits exactly that request expiry. Disposition uses the new considering lifecycle:

- through `N+2`: eligible if all other checks pass
- at `N+3` or later: final `rejected` with protected reason `expired`

Wall time never controls canonical eligibility.

### 10. Maintenance, checkpoints, crash, and rollback remain explicit

- request does not block later garden wakes
- dispatch requires sleeping and stable request checkpoint
- ingress/terminalization may record admitted evidence while sleeping or maintenance-required, never behind pending checkpoint/rollback/quarantine
- ingress/terminalization cannot clear maintenance
- disposition requires sleeping and cannot bypass maintenance
- garden/disposition wakes checkpoint
- dispatch/ingress/terminalization do not checkpoint
- crash after dispatch admission remains conservatively charged until explicit terminal reconciliation
- rollback increments lineage and makes prior-lineage consultation rows inactive
- abandoned-lineage packages/proposals fail before mutation
- ADR 0007 one-rollback rule/evidence retention remain unchanged

### 11. Zero-caregiver control uses the ADR 0009 semantic artifact projection

ADR 0009 supersedes the original `phase1-projection-v1` text and defines `phase1-projection-v2`.

The original Phase 1 budget singleton and every original `budget_config_version` location remain exactly `phase1-v1`. Phase 2 policy lives only in the protected `consultation_configuration` singleton.

Paired schema-v1/schema-v2-zero scenarios compare exact canonical behavior, event order, authority, lifecycle, failure, maintenance, checkpoint boundaries, retention choices, and rollback semantics after independently validating each side and replacing only the exact schema-version and byte-provenance locations listed by ADR 0009.

The projection explicitly covers normal and maintenance checkpoints, orphan registration repair, retention prune/failure/reconciliation, rollback archive/source candidate/transformed candidate/completion, and semantic event export. Projected-away IDs, digests, sizes, aggregate byte counts, and directory names remain independently recomputed and physically bounded on each side.

No wildcard, recursive walk, suffix match, prefix match, or global key-name normalization is permitted. Near physical ceilings, schema-v2 obeys the same absolute limits through dedicated real-file tests rather than claiming byte-threshold equality with schema-v1.

### 12. Protected evidence is normative

`docs/PHASE2_CONSULTATION_TEST_MATRIX.md` is the required implementation evidence map.

It includes real, not mock-only, tests for:

- exact zero-caregiver projection
- optional request savepoint and real 8 MiB/reserve boundary where core wake fits but extension does not
- fail-fast concurrency/process crash
- fixture lock/capability absence
- exact digest preimages and acyclic graph
- exact proposal fields/types/expiry/evaluator sets
- exact 64 KiB formula and no double counting
- ingress idempotence/same-byte resubmission
- terminal reconciliation without retry
- disposition lifecycle/checkpoint behavior
- lineage/rollback filtering
- physical DB/checkpoint/working-set/reserve ceilings
- explicit absence of live APIs, free text, memory, skills, training, arbitrary code, network/subprocess, continuous operation, and personality/emotion state

No test may weaken, skip, condition, or redefine the 152-test Phase 1 baseline.

### 13. Audit cadence

The completed Phase 2.0 design audit was followed by one focused read-only re-audit of the implementation-blocking zero-caregiver contradiction. The focused audit reviewed PR #64 head `e4f3527518cbc4e4ff8ab239a90f48bfa47fdbb8` and concluded that ADR 0009 is ready after specified documentation or matrix corrections.

ADR 0009 and the synchronized protocol/matrix provide those corrections. No further automatic design re-audit is required unless the correction materially changes the same semantic artifact boundary again.

A separate independent read-only Phase 2 implementation audit is required after this accepted design is fully implemented, all matrix requirements have protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze.

## Consequences

Positive:

- external latency never holds organism write ownership
- caregiver data cannot declare authority, mutate protected state, or execute action
- work is charged before non-atomic boundary
- crash cannot authorize hidden retry
- exact proposal constraints prevent caregiver-controlled expiry/evaluator drift
- exact digest/size rules are reproducible
- optional request metadata cannot strand a valid Phase 1 wake
- zero-caregiver behavior remains a strict control

Negative:

- accepted proposals provide no action benefit in first implementation
- conservative charge may count work a crash prevented
- interrupted dispatch requires explicit reconciliation
- queued proposal may wait behind maintenance
- request extension may be omitted near storage limits
- rollback starts a fresh four-call epoch; physical maximum is eight rather than global four
- schema-v1/v2 files and checkpoint digests are not byte-identical
- clarification cannot round-trip

These limitations are intentional. The first Phase 2 implementation proves authority-safe plumbing, not caregiver intelligence.

## Scope

Acceptance authorizes creation of a separate test-first implementation Issue for deterministic fixture plumbing mapped to the accepted matrix.

It does not authorize live APIs/humans, memory, skills, training, arbitrary code, organism network/subprocess, continuous execution, personality/emotion features, or a generic agent framework.
