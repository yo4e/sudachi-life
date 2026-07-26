# Phase 2 Consultation Protocol v1

Status: **Proposed after independent design-audit corrections**

This document defines the source-neutral deterministic-fixture protocol referenced by proposed ADR 0008. It is not a live human or model interface. The caregiver side produces bounded untrusted data; it never receives organism authority.

## 1. Version identifiers

- database schema version: `2`
- base contract version: `0.2`
- consultation protocol version: `1`
- request schema: `sudachi.consultation.request/v1`
- dispatch schema: `sudachi.consultation.dispatch/v1`
- response schema: `sudachi.consultation.response/v1`
- proposal schema: `sudachi.consultation.proposal/v1`
- ingress receipt schema: `sudachi.consultation.ingress_receipt/v1`
- disposition schema: `sudachi.consultation.disposition/v1`
- dispatch terminal schema: `sudachi.consultation.dispatch_terminal/v1`
- cost schema: `sudachi.consultation.cost/v1`
- zero-caregiver budget configuration: `phase2-zero-caregiver-v1`
- deterministic fixture budget configuration: `phase2-fixture-v1`
- deterministic fixture adapter version: `deterministic-fixture-v1`
- deterministic fixture work class: `fixture-constant-v1`
- zero-caregiver projection: `phase1-projection-v1`

Unknown versions fail closed before canonical mutation.

## 2. Canonical value and byte rules

All envelope, identity, and digest-preimage values are canonical JSON-compatible values.

- UTF-8 only
- strings are NFC-normalized
- object keys are lexicographically sorted
- arrays preserve declared order
- sets are represented as sorted unique arrays
- integers only; floating-point values are forbidden
- booleans are allowed only where explicitly declared
- `null` is forbidden unless explicitly declared
- identifiers match `^[a-z0-9][a-z0-9._:-]{0,127}$`
- digests are lowercase SHA-256 hexadecimal strings
- arbitrary SQL, Python, shell, tool names, filesystem paths, URLs, credentials, executable code, hidden chat history, and opaque binary payloads are forbidden

`canonical_json(value)` is UTF-8 JSON with sorted keys, no insignificant whitespace, and separators equivalent to `(',', ':')`.

`canonical_size(value)` is the byte length of `canonical_json(value)`. Size limits are applied to final envelopes after all identifiers and linkage fields are inserted.

## 3. Exact digest preimages and identifiers

### 3.1 Domain-separated digest function

Every protocol digest uses:

```text
H(label, value) = sha256(
    UTF8("sudachi.consultation/v1\n" + label + "\n")
    || canonical_json(value)
)
```

The label is exact and case-sensitive. No trailing NUL, alternate separator, pretty printing, recursive key deletion, or implementation-specific normalization is permitted.

Protocol labels are:

- `request-id`
- `dispatch-id`
- `proposal-content`
- `response-id`
- `external-package`
- `disposition-id`
- `current-state-reference`

### 3.2 Request identity

```text
request_id = "consultation-request:" + H("request-id", request_identity)
```

`request_identity` contains exactly:

- `request_schema`
- `consultation_protocol_version`
- `organism_id`
- `lineage_generation`
- `request_ordinal`
- `request_lifecycle_number`
- `reason_code`
- `requested_proposal_types`
- `observation_digest`
- `objective_digest`
- `allowed_action_ids`
- `allowed_permission_ids`
- `policy_context_version`
- `budget_config_version`
- `expires_after_lifecycle_number`

It excludes `request_id`, the later request event sequence, wall time, and event-authority metadata.

### 3.3 Dispatch identity

```text
dispatch_id = "consultation-dispatch:" + H("dispatch-id", dispatch_identity)
```

`dispatch_identity` contains exactly:

- `dispatch_schema`
- `consultation_protocol_version`
- `organism_id`
- `lineage_generation`
- `request_id`
- `dispatch_ordinal`, exactly `1`
- `caregiver_adapter_version`
- `fixture_case_id`
- `fixture_work_class`

It excludes `dispatch_id`, the later dispatch event sequence, and wall time.

### 3.4 Proposal content and identity

```text
proposal_content_digest = H("proposal-content", proposal_identity)
proposal_id = "consultation-proposal:" + proposal_content_digest
```

`proposal_identity` contains exactly:

- `proposal_schema`
- `consultation_protocol_version`
- `request_id`
- `dispatch_id`
- `proposal_ordinal`, exactly `1`
- `proposal_type`
- `subject_reference`
- `proposed_value`
- `rationale_code`
- `confidence_basis`
- `expires_after_lifecycle_number`
- `required_evaluator_ids`

It excludes `proposal_id` and `response_id`. The final proposal envelope receives `response_id` only after the response identity is derived.

### 3.5 Response identity and package digest

```text
response_id = "consultation-response:" + H("response-id", response_identity)
```

`response_identity` contains exactly:

- `response_schema`
- `consultation_protocol_version`
- `request_id`
- `dispatch_id`
- `caregiver_adapter_type`
- `caregiver_adapter_version`
- `caregiver_instance_id`
- `response_status`
- ordered `proposal_ids`
- ordered `proposal_content_digests`
- `external_provenance`

It excludes `response_id`.

After `response_id` is inserted into every final proposal envelope, the exact package preimage is:

```json
{"response": <final response envelope>, "proposals": [<final proposal envelope>]}
```

The canonical object has exactly the two keys `response` and `proposals`.

```text
external_package_digest = H("external-package", package_preimage)
```

For `unavailable`, `proposals` is an empty array.

### 3.6 Current-state and disposition identities

The protected evaluator computes:

```text
current_state_digest = H("current-state-reference", current_state_identity)
```

`current_state_identity` is a versioned protected projection of the exact current organism, objective, registered actions, permissions, counters, lifecycle, status, and lineage used by evaluation. The implementation issue must enumerate its fields before disposition code is accepted.

```text
disposition_id = "consultation-disposition:" + H("disposition-id", disposition_identity)
```

`disposition_identity` contains exactly:

- `disposition_schema`
- `consultation_protocol_version`
- `organism_id`
- `lineage_generation`
- `request_id`
- `dispatch_id`
- `response_id`
- `proposal_id`
- `disposition`
- `reason_code`
- `disposition_lifecycle_number`
- `current_state_digest`
- `evaluator_versions`

It excludes `disposition_id`, the later disposition event sequence, and wall time.

### 3.7 Reproducibility

Protected tests construct the complete identity graph twice from identical declared inputs and require identical:

- identity objects
- preimage bytes
- identifiers and digests
- final envelopes
- package bytes
- canonical rows
- event payloads

They also prove the proposal/response graph is acyclic.

## 4. Protected budgets and exact logical-payload formula

### 4.1 Zero-caregiver configuration

`phase2-zero-caregiver-v1` sets every consultation request, dispatch, fixture, response, proposal, disposition, clarification, payload, human, model, money, and consultation-record limit to zero.

Operational consultation tables remain empty and no consultation event, source, cost, adapter import, or caregiver-derived effect is produced.

### 4.2 Fixture configuration

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
| request final-envelope bytes | 16 KiB |
| complete external-package bytes | 16 KiB |
| external provenance bytes | 8 KiB within the package limit |
| total consultation logical payload per lineage epoch | 64 KiB |
| fixture work units charged per dispatch | 1 |
| human minutes | 0 |
| model input units | 0 |
| model output units | 0 |
| money in integer minor units | 0 |
| declared fixture latency milliseconds | 0 |
| Phase 1 core canonical records in a request garden wake | at most 16 |
| additional request records in that wake | at most 2 |
| total canonical records in a request garden wake | at most 18 |
| semantic steps in a disposition wake | at most 10 |
| canonical records in a disposition wake | at most 12 |
| canonical records in dispatch admission | at most 3 |
| canonical records in response ingress | at most 5 |
| canonical records in dispatch terminalization | at most 3 |

For current lineage `g`, the exact logical-payload counter is:

```text
lineage_payload_bytes(g) =
    sum(canonical_size(final_request_envelope))
    + sum(canonical_size(accepted_external_package_preimage))
```

Rules:

- each created request is counted exactly once
- each successfully ingressed `proposals_returned` or `unavailable` package is counted exactly once
- response, proposal, and external provenance are already contained in the package preimage and are not counted again
- the 8 KiB provenance limit is a subset of the 16 KiB package limit, not an additional allowance
- byte-identical duplicate ingress adds zero bytes
- dispatch, cost, receipt, disposition, and terminal metadata are excluded from the logical-payload counter but remain subject to physical database and working-set ceilings
- a package that fails pre-mutation validation is not added to logical payload; its bounded digest/declared size terminal evidence still counts physically
- the 64 KiB check is performed before mutation and again after mutation using measured canonical bytes

All Phase 2 writes remain subject to the inherited 8 MiB active-database ceiling, 40 MiB checkpoint-store ceiling, 64 MiB working-set ceiling, and 1 MiB next-wake active-database reserve.

## 5. Request envelope and optional request extension

Schema: `sudachi.consultation.request/v1`

A request may be created only inside a schema-v2 garden wake after the unchanged Phase 1 policy selects `no_applicable_action` for an incomplete objective.

Required final-envelope fields:

- `request_id`
- `request_schema`
- `consultation_protocol_version`
- `organism_id`
- `lineage_generation`
- `request_ordinal`
- `request_event_sequence`
- `request_lifecycle_number`
- `reason_code`, exactly `no_applicable_action`
- sorted unique `requested_proposal_types`
- `observation_reference`
- `objective_reference`
- sorted unique `allowed_action_ids`
- sorted unique `allowed_permission_ids`
- `policy_context_version`
- `budget_config_version`, exactly `phase2-fixture-v1`
- `consultation_budget_snapshot`
- `expires_after_lifecycle_number`, exactly request lifecycle plus `2`
- `authority_category`, exactly `organism`
- `authority_source`, exactly `organism:consultation.request`
- sorted unique existing `provenance_parent_event_sequences`

Optional declared context contains bounded typed codes and identifiers only. Free text is forbidden.

Request admission requires:

- fixture budget configuration
- no current-lineage outstanding request
- fewer than four current-lineage requests
- resulting Phase 1 failure streak below the maintenance threshold
- request and lineage logical limits fit
- the maximum resulting wake and checkpoint preserve all physical ceilings and the 1 MiB reserve

### 5.1 Phase 1 outcome remains authoritative

The garden wake remains a Phase 1 `no_applicable_action` abstention:

- the same garden input is consumed
- the same Phase 1 action, mutation, and outcome records are produced
- `consecutive_failures` increments exactly once
- request creation never resets or hides failure
- no request is created on a wake that enters `maintenance_required`

### 5.2 Storage-safe optional extension

Request creation is an optional extension to the otherwise valid Phase 1 wake. It must never turn a Phase 1 core wake that fits into a failed wake merely because consultation metadata does not fit.

The implementation uses an extension savepoint after the Phase 1 core records are established:

1. predict core-wake, request-extension, checkpoint, active-database, reserve, and working-set use
2. if the request extension cannot fit, skip it without writing a consultation row or event
3. otherwise create the request row and request event inside the extension savepoint
4. perform post-write measured accounting before releasing the savepoint
5. if the extension crosses a logical or physical limit, roll back only the extension savepoint
6. commit the unchanged Phase 1 core wake and publish its ordinary checkpoint

When the extension is skipped or rolled back:

- no request, consultation event, consultation source, or partial cost exists
- the canonical Phase 1 outcome remains exact
- the caller receives typed noncanonical status `consultation_request_not_created_storage_budget`
- the next-wake reserve remains available

If the Phase 1 core wake or its checkpoint cannot fit, existing frozen Phase 1 failure behavior applies; Phase 2 does not redefine it.

When a request is created, its row and event are atomic and the resulting wake checkpoint must be stable before dispatch admission.

## 6. Dispatch admission and conservative charge

Schema: `sudachi.consultation.dispatch/v1`

Dispatch admission is a fresh fail-fast administrative `BEGIN IMMEDIATE` transaction.

It requires:

- schema-v2/protocol-v1 support
- `sleeping` status
- no pending checkpoint, rollback, or quarantine
- stable request checkpoint at or beyond the request event boundary
- exact current lineage and organism
- current lifecycle not beyond request expiry
- no prior dispatch and no terminal state
- all logical and physical budgets fit

The transaction records exactly one immutable dispatch, one protected cost charge, and one administrative event.

The cost charge records:

- `dispatch_attempts = 1`
- `fixture_invocations_charged = 1`
- `fixture_work_units_charged = 1`
- exact request bytes
- zero human, model, money, and declared-latency values

The transaction commits and releases SQLite ownership before fixture execution. Charges are never refunded. Repeated admission returns already-admitted state and never authorizes a second fixture invocation.

## 7. External deterministic fixture

Fixture execution occurs only after dispatch admission commits and outside every SQLite write transaction.

The fixture receives exactly:

- the final canonical request envelope
- the protected declared `fixture_case_id`

It receives no database handle, path, workspace, repository handle, executor, evaluator, checkpoint, migration, rollback, network, subprocess, credential, tool, or ambient randomness capability.

Its result remains noncanonical until ingress succeeds.

## 8. Exact response and proposal schemas

### 8.1 Response

Schema: `sudachi.consultation.response/v1`

Required fields:

- `response_id`
- `response_schema`
- `consultation_protocol_version`
- `request_id`
- `dispatch_id`
- `caregiver_adapter_type`, exactly `deterministic_fixture`
- `caregiver_adapter_version`, exactly `deterministic-fixture-v1`
- `caregiver_instance_id`
- `response_status`
- ordered `proposal_ids`
- ordered `proposal_content_digests`
- bounded `external_provenance`

Allowed statuses:

- `proposals_returned`, with exactly one proposal
- `unavailable`, with zero proposals

### 8.2 Common proposal fields

Every `sudachi.consultation.proposal/v1` final envelope contains exactly:

- `proposal_id`
- `proposal_schema`
- `consultation_protocol_version`
- `request_id`
- `dispatch_id`
- `response_id`
- `proposal_ordinal`, exactly `1`
- `proposal_type`
- `subject_reference`
- `proposed_value`
- `rationale_code`
- `confidence_basis`
- `expires_after_lifecycle_number`
- sorted unique `required_evaluator_ids`

Constraints common to every proposal:

- `expires_after_lifecycle_number` equals the linked request expiry exactly; the fixture cannot shorten or extend it
- `confidence_basis` is exactly `{"basis_type":"deterministic_fixture_case","fixture_case_id":<linked dispatch case>}`
- `required_evaluator_ids` equals the protected type-specific set below; the fixture cannot add, remove, or rename evaluators
- every identifier and reference must match the linked current-lineage request and dispatch
- no undeclared field is accepted

### 8.3 `action_candidate`

- `subject_reference` is exactly `{"action_id":<one request allowed_action_id>}`
- `proposed_value` is exactly `{"parameters":<canonical object matching the registered action parameter schema>}`
- `rationale_code` is exactly `existing_action_applicable`
- `required_evaluator_ids` is exactly `[
  "action-schema-v1",
  "current-state-v1",
  "permission-v1"
]`

The proposal may name only an already registered Phase 1 action. It cannot define an action, executable payload, SQL, tool, path, permission, or budget.

### 8.4 `abstain`

- `subject_reference` is exactly the linked request objective reference
- `proposed_value` is exactly `{"reason_code":"no_supported_action"}`
- `rationale_code` is exactly `no_supported_action`
- `required_evaluator_ids` is exactly `[
  "abstain-policy-v1",
  "current-state-v1"
]`

### 8.5 `defer`

- `subject_reference` is exactly the linked request objective reference
- `proposed_value` is exactly `{"reason_code":"await_state_change"}`
- `rationale_code` is exactly `await_state_change`
- `required_evaluator_ids` is exactly `[
  "current-state-v1",
  "defer-policy-v1"
]`

`defer` carries no wake time, schedule, retry command, or direct state effect.

External response and proposal packages contain no canonical writer authority and no authoritative cost, budget, permission, evaluator, checkpoint, migration, rollback, or execution command.

## 9. Administrative response ingress

Ingress is a separate fresh fail-fast administrative transaction.

Before mutation administration independently verifies:

- raw package input does not exceed 16 KiB before JSON parsing
- canonical versions and exact field sets
- all identity preimages, identifiers, and digests
- request, dispatch, adapter, case, organism, and current-lineage linkage
- expiry and cardinality
- exact proposal-type schema and protected evaluator set
- canonical and measured byte limits
- lineage logical-payload formula
- active database, reserve, checkpoint store, and working-set ceilings

Successful ingress atomically records immutable response, optional proposal, protected ingress receipt, measured-byte cost completion, and one administrative event.

The receipt carries:

- `authority_category = administration`
- `authority_source = administration:consultation.response_ingress`
- external package digest
- measured request/package/provenance bytes
- exact parent event linkage

Ingress cannot adopt a proposal, execute an action, clear maintenance, checkpoint, migrate, roll back, or alter protected budgets or permissions.

A byte-identical duplicate is idempotent and consumes no additional logical payload, event, clock read, or fixture charge. A conflicting duplicate fails closed.

A valid package rejected only because write ownership is busy or a checkpoint is pending may be explicitly resubmitted with identical already-produced bytes. The fixture is not invoked again.

`unavailable` terminalizes the request with no proposal or disposition.

## 10. Dispatch terminalization and reconciliation

Schema: `sudachi.consultation.dispatch_terminal/v1`

Allowed terminal reasons:

- `dispatch_interrupted`
- `fixture_output_invalid`
- `expired_before_ingress`

Caught fixture or validation failure is terminalized through an explicit administrative operation. A process crash after dispatch admission leaves one charged unresolved dispatch. Explicit bounded reconciliation may record interruption but never invokes the fixture.

Response and terminal rows are mutually exclusive. Repeated terminalization is idempotent. Terminal evidence may retain only the bounded rejected-package digest, measured size, reason, linkage, and event; it does not retain arbitrary rejected bytes.

## 11. Explicit disposition wake

Schema: `sudachi.consultation.disposition/v1`

A caller explicitly invokes this work class. It is not hidden inside a garden wake and has no implicit priority over garden input.

The wake:

- uses a fresh fail-fast wake transaction
- requires schema-v2, fixture configuration, `sleeping`, and no pending checkpoint
- claims no garden input
- selects the oldest queued current-lineage proposal by ingress event sequence and then proposal ID
- considers at most one proposal
- independently validates exact schemas, linkage, current state, permissions, evaluators, budgets, and considering-lifecycle expiry
- records exactly one final disposition
- increments lifecycle while preserving Phase 1 garden `consecutive_failures`
- creates the ordinary required checkpoint

Final dispositions:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

Clarification is final because clarification rounds are zero. The first implementation records disposition only; no disposition enters the existing selector, executes an action, changes garden state, creates memory, or promotes a skill.

## 12. Lineage, expiry, and derived state

The consultation budget epoch is current `lineage_generation`.

- only current-lineage rows are active or budget-counting
- old-lineage rows remain immutable historical evidence
- rollback begins a fresh bounded four-call epoch
- ADR 0007 permits at most one completed rollback, so one physical organism has at most two epochs and eight charged fixture invocations
- abandoned-lineage packages and proposals fail before mutation

A request created in lifecycle `N` is eligible for dispatch and ingress through committed lifecycle `N+2`.

A proposal inherits exactly the request expiry. Disposition eligibility uses the new considering lifecycle:

- considering lifecycle through `N+2`: eligible if all other checks pass
- considering lifecycle `N+3` or later: final `rejected` with protected reason `expired`

Wall time never determines canonical eligibility.

Current-lineage state is derived from immutable rows:

- no dispatch and lifecycle beyond expiry: terminal for dispatch and no longer outstanding
- admitted dispatch: outstanding until response or terminal outcome, even after expiry
- unavailable response: terminal
- successful response: outstanding until disposition
- dispatch terminal or disposition: final

No caregiver-writable mutable status flag exists.

## 13. Maintenance, checkpoints, and rollback

- request creation does not block later garden wakes
- dispatch requires sleeping and a stable request checkpoint
- ingress and terminalization may record already-admitted evidence while sleeping or maintenance-required, but never behind a pending checkpoint, rollback, or quarantine
- ingress and terminalization cannot clear maintenance
- disposition requires sleeping and cannot bypass maintenance
- garden and disposition wakes checkpoint
- dispatch, ingress, and terminalization do not checkpoint
- rollback increments lineage and makes prior-lineage consultation rows inactive
- ADR 0007 rollback limit and evidence retention remain unchanged

## 14. Canonical state concepts

Schema-v2 uses new protected immutable objects for:

- requests
- dispatch admissions
- protected cost charges and measured-byte completions
- responses
- proposals
- ingress receipts
- dispositions
- dispatch terminal outcomes

No new column is added to an original Phase 1 table. All identities, versions, digests, links, cardinalities, uniqueness rules, and update/delete protections are exact.

## 15. Exact zero-caregiver projection

The zero-caregiver comparison runs paired schema-v1 and schema-v2-zero organisms from identical declared inputs and clocks.

`phase1-projection-v1` is computed as follows:

1. select every original Phase 1 table and every original Phase 1 column, ordered by the original primary key or declared deterministic order
2. for original columns named exactly `schema_version`, compare schema-v1 value `1` with schema-v2 value `2` as the one permitted version difference
3. for original columns named exactly `budget_config_version`, compare the schema-v1 protected budget value with `phase2-zero-caregiver-v1` as the one permitted budget-config difference
4. for original event payloads, normalize only top-level keys named exactly `schema_version` and `budget_config_version` to the schema-v1 expected values
5. nested keys, other key spellings, additional keys, missing keys, event types, sequences, authority, sources, parent links, and every other payload value are compared exactly
6. compare every other original row and column value exactly after canonical encoding
7. require all operational consultation tables empty
8. require no consultation-table `sqlite_sequence` entry, consultation event, source, cost, adapter invocation, disposition, terminal outcome, or caregiver-derived effect
9. compare status, lifecycle, failure streak, behavior, checkpoint eligibility, rollback eligibility, and authority behavior exactly

The projection does not compare raw SQLite bytes or checkpoint digests because schema-v2 contains additional empty protected objects. No wildcard, recursive, or semantic normalization beyond steps 2–4 is permitted.

## 16. Deterministic fixture cases

The implementation provides declared cases for:

- valid action candidate
- valid abstain
- valid defer
- unavailable
- stale observation
- expired before ingress
- expired after ingress before disposition
- unknown action
- invalid parameters
- contradictory current state
- byte-identical duplicate package
- conflicting duplicate package
- malformed response
- unknown schema
- over-budget package
- fixture exception
- process interruption after dispatch admission
- abandoned-lineage package after rollback

Case selection is declared input, never randomness or network behavior.

## 17. Explicit exclusions

Protocol v1 accepts no:

- live model or human text
- free-form rationale
- memory or skill payload
- source or test patch
- arbitrary code, SQL, shell, tool, path, URL, credential, or executable payload
- new action definition
- caregiver-declared writer authority or authoritative cost
- budget, permission, evaluator, checkpoint, migration, rollback, or execution command
- network or subprocess capability inside organism execution
- continuous or always-on execution

## 18. Review and audit cadence

Protocol v1 is reviewed with ADR 0008 and the Phase 2 test matrix.

One independent read-only design audit has been completed at PR #60 head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647`. Its required documentation and matrix corrections are incorporated by later commits on the same design branch. Under the project audit policy, these bounded corrections are verified through ordinary review and CI rather than automatic audit-repair-reaudit ping-pong.

A separate independent read-only implementation audit occurs only after the accepted design is fully implemented, the complete protected matrix has evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze.
