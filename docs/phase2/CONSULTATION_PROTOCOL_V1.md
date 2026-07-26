# Phase 2 Consultation Protocol v1

Status: **Proposed for Issue #59 review**

This document fixes the source-neutral envelopes and canonical-state semantics referenced by proposed ADR 0008. It defines a deterministic fixture protocol, not a live human or model interface.

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

Unknown versions fail closed before canonical mutation.

## 2. Canonical value rules

All envelope and identity values are canonical JSON-compatible values.

- UTF-8 only
- objects use lexicographically sorted keys for canonical encoding
- arrays preserve declared order
- sets are represented as sorted unique arrays
- integers only; floating-point numbers are forbidden
- booleans are permitted only where explicitly declared
- `null` is forbidden unless explicitly declared
- strings are NFC-normalized UTF-8 and bounded by their enclosing limit
- identifiers match `^[a-z0-9][a-z0-9._:-]{0,127}$`
- digests are lowercase SHA-256 hexadecimal strings
- arbitrary SQL, Python, shell, tool names, filesystem paths, URLs, credentials, executable code, hidden chat history, and opaque binary payloads are forbidden

Canonical JSON bytes use UTF-8, sorted keys, no insignificant whitespace, and separators equivalent to `(',', ':')`.

## 3. Digest and identifier construction

### 3.1 General rule

Each identifier is:

```text
<prefix>:<sha256(canonical identity object)>
```

The identifier being derived is excluded from its identity object. Event sequences assigned after derivation are also excluded. Every exclusion is listed below; no implementation may invent additional normalization.

### 3.2 Request identity

```text
request_id = consultation-request:<sha256(request identity object)>
```

The request identity object contains exactly:

- `request_schema`
- `consultation_protocol_version`
- `organism_id`
- `lineage_generation`
- `request_ordinal`
- `request_lifecycle_number`
- `reason_code`
- `requested_proposal_types`
- observation digest
- objective digest
- `allowed_action_ids`
- `allowed_permission_ids`
- `policy_context_version`
- `budget_config_version`
- `expires_after_lifecycle_number`

It excludes `request_id`, `request_event_sequence`, wall timestamp, and authority event metadata.

### 3.3 Dispatch identity

```text
dispatch_id = consultation-dispatch:<sha256(dispatch identity object)>
```

The dispatch identity object contains exactly:

- `dispatch_schema`
- `consultation_protocol_version`
- `organism_id`
- `lineage_generation`
- `request_id`
- `dispatch_ordinal`, exactly `1`
- `caregiver_adapter_version`
- `fixture_case_id`
- `fixture_work_class`

It excludes `dispatch_id`, `dispatch_event_sequence`, and wall timestamp.

### 3.4 Proposal identity

```text
proposal_id = consultation-proposal:<sha256(proposal identity object)>
```

The proposal identity object contains exactly:

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

It excludes `proposal_id` and `response_id`.

The digest of this identity object is also the `proposal_content_digest` used to derive the response.

### 3.5 Response identity

```text
response_id = consultation-response:<sha256(response identity object)>
```

The response identity object contains exactly:

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
- bounded external provenance

It excludes `response_id`.

After `response_id` is derived, it is inserted into each final proposal envelope. The complete external package digest is then:

```text
sha256(canonical JSON({"response": <final response>, "proposals": [<final proposal>] }))
```

For `unavailable`, `proposals` is an empty array.

### 3.6 Disposition identity

```text
disposition_id = consultation-disposition:<sha256(disposition identity object)>
```

The disposition identity object contains exactly:

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
- `current_state_reference`
- `evaluator_versions`

It excludes `disposition_id`, `disposition_event_sequence`, and wall timestamp.

### 3.7 Reproducibility requirement

Tests must construct the complete graph twice from identical declared inputs and require identical:

- identity objects
- identifiers
- final envelopes
- content digests
- package digest
- canonical rows
- event payloads

Tests must also prove there is no response/proposal circular dependency.

## 4. Protected budget configurations

### 4.1 `phase2-zero-caregiver-v1`

Every consultation request, dispatch, fixture work, response, proposal, disposition, clarification, payload, human, model, money, and consultation-record limit is zero.

Schema-v2 operational consultation tables remain empty and no consultation event or source is emitted.

### 4.2 `phase2-fixture-v1`

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
| external provenance subset bytes | 8 KiB |
| total consultation logical payload bytes per organism | 64 KiB |
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

All administrative writes perform predicted and post-write active-database and working-set accounting and preserve the existing 1 MiB next-wake reserve.

## 5. Request envelope

Schema: `sudachi.consultation.request/v1`

A request is created only by organism runtime inside a schema-v2 garden wake.

### 5.1 Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `request_id` | identifier | exact deterministic identifier |
| `request_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `organism_id` | identifier | exact canonical organism identity |
| `lineage_generation` | integer | non-negative and current |
| `request_ordinal` | integer | lifetime request count plus one; `1..4` |
| `request_event_sequence` | integer | exact creating event sequence |
| `request_lifecycle_number` | integer | exact creating garden lifecycle |
| `reason_code` | enum | exactly `no_applicable_action` |
| `requested_proposal_types` | array | sorted unique non-empty subset of allowed types |
| `observation_reference` | object | event sequence and canonical observation digest |
| `objective_reference` | object | objective identifier, version, and canonical digest |
| `allowed_action_ids` | array | sorted unique registered action identifiers |
| `allowed_permission_ids` | array | sorted unique protected permission identifiers |
| `policy_context_version` | string | exact protected policy version |
| `budget_config_version` | string | exactly `phase2-fixture-v1` |
| `consultation_budget_snapshot` | object | exact counters and remaining limits before creation |
| `expires_after_lifecycle_number` | integer | exactly request lifecycle plus `2` |
| `authority_category` | string | exactly `organism` |
| `authority_source` | string | exactly `organism:consultation.request` |
| `provenance_parent_event_sequences` | array | sorted unique existing earlier event sequences |

Optional field:

| Field | Type | Rule |
| --- | --- | --- |
| `declared_context_summary` | object | bounded typed codes and identifiers only; no free text |

Allowed requested proposal types:

- `action_candidate`
- `abstain`
- `defer`

### 5.2 Request admission

Request admission occurs only after the unchanged Phase 1 policy selects `no_applicable_action` for an incomplete objective.

A request is created only when:

- budget config is `phase2-fixture-v1`
- no request is currently outstanding
- fewer than four lifetime requests exist
- the resulting garden failure streak remains below the maintenance threshold
- request bytes and physical reserve fit

The garden lifecycle remains a Phase 1 `no_applicable_action` abstention and increments `consecutive_failures` exactly once. Request creation never resets or replaces that accounting.

A zero-caregiver configuration produces no consultation row, event, source, or hidden adapter import.

### 5.3 Request invariants

- at most one request per garden wake
- at most one outstanding request
- at most four lifetime requests
- request JSON at most 16 KiB
- request row and event commit atomically
- request row is immutable
- creation emits one `consultation_request_created` organism event
- the request wake becomes checkpoint-stable before dispatch admission
- no request is created on the wake that enters maintenance

## 6. Dispatch admission

Schema: `sudachi.consultation.dispatch/v1`

Dispatch admission is an administrative operation with its own fresh fail-fast `BEGIN IMMEDIATE` transaction.

### 6.1 Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `dispatch_id` | identifier | exact deterministic identifier |
| `dispatch_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `organism_id` | identifier | exact canonical identity |
| `lineage_generation` | integer | exact current lineage |
| `request_id` | identifier | exact eligible request |
| `dispatch_ordinal` | integer | exactly `1` |
| `caregiver_adapter_type` | string | exactly `deterministic_fixture` |
| `caregiver_adapter_version` | string | exactly `deterministic-fixture-v1` |
| `caregiver_instance_id` | identifier | deterministic declared fixture instance |
| `fixture_case_id` | identifier | protected declared fixture case |
| `fixture_work_class` | string | exactly `fixture-constant-v1` |
| `dispatch_event_sequence` | integer | exact administrative event sequence |
| `authority_category` | string | exactly `administration` |
| `authority_source` | string | exactly `administration:consultation.dispatch_admitted` |

### 6.2 Admission checks

Admission requires:

- schema-v2 and protocol-v1 support
- `sleeping` status
- no pending checkpoint
- request checkpoint registered stable at or beyond the request event boundary
- current lineage equals request lineage
- current lifecycle is not beyond request expiry
- no prior dispatch for the request
- request is not otherwise terminal
- dispatch, lifetime work, logical payload, active database, reserve, and working-set budgets fit

### 6.3 Conservative cost charge

The same transaction creates one protected immutable cost row charging:

- `dispatch_attempts = 1`
- `fixture_invocations_charged = 1`
- `fixture_work_units_charged = 1`
- all human/model/money/latency fields at zero
- exact request payload bytes
- response/provenance payload bytes initially zero

This is a conservative charge. It remains charged if the process crashes before the fixture call.

### 6.4 Dispatch invariants

- one dispatch admission maximum per request
- admission row, cost row, and event commit atomically
- fixture code is not called before this commit
- repeated admission never authorizes another call
- no SQLite write lock remains held during fixture execution
- dispatch and cost rows are immutable

## 7. External deterministic fixture

The fixture function receives exactly two declared values:

1. the canonical request envelope
2. the protected `fixture_case_id`

It returns one external package or raises one bounded fixture error.

The fixture receives no connection, state path, workspace, repository handle, action executor, evaluator, budget mutator, checkpoint handle, rollback handle, network client, subprocess launcher, or ambient randomness.

Fixture case selection is explicit test/configuration input. Repeated execution for identical request bytes and case ID produces identical output bytes, but protocol v1 permits only one charged attempt.

## 8. External response envelope

Schema: `sudachi.consultation.response/v1`

The external response is untrusted caregiver data. It contains no canonical writer authority and no authoritative cost ledger.

### 8.1 Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `response_id` | identifier | exact deterministic identifier |
| `response_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `request_id` | identifier | exact parent request |
| `dispatch_id` | identifier | exact admitted dispatch |
| `caregiver_adapter_type` | string | exactly `deterministic_fixture` |
| `caregiver_adapter_version` | string | exactly `deterministic-fixture-v1` |
| `caregiver_instance_id` | identifier | exact admitted instance |
| `response_status` | enum | `proposals_returned` or `unavailable` |
| `proposal_ids` | array | exactly one for success; empty for unavailable |
| `proposal_content_digests` | array | matches proposal IDs; empty for unavailable |
| `provenance` | object | request digest, dispatch ID, fixture case, adapter versions, bounded parent identifiers |

Forbidden in the external response:

- `authority_category`
- `authority_source`
- canonical event sequence
- budget limit
- authoritative cost value
- permission, evaluator, checkpoint, migration, rollback, or execution command

### 8.2 Status semantics

#### `proposals_returned`

- contains exactly one proposal
- the proposal is eligible for later ingress and disposition validation

#### `unavailable`

- contains zero proposals
- indicates a completed deterministic fixture result
- terminalizes the request after valid ingress
- creates no proposal and no disposition
- permits no retry

## 9. Proposal envelope

Schema: `sudachi.consultation.proposal/v1`

### 9.1 Common fields

| Field | Type | Rule |
| --- | --- | --- |
| `proposal_id` | identifier | exact deterministic identifier |
| `proposal_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `request_id` | identifier | exact request |
| `dispatch_id` | identifier | exact dispatch |
| `response_id` | identifier | exact final parent response |
| `proposal_ordinal` | integer | exactly `1` |
| `proposal_type` | enum | `action_candidate`, `abstain`, or `defer` |
| `subject_reference` | object | exact objective, observation, or action subject |
| `proposed_value` | object | exact type-specific structure |
| `rationale_code` | identifier | bounded code; no free text |
| `confidence_basis` | object | typed case/evidence references; no probability required |
| `expires_after_lifecycle_number` | integer | no later than parent request expiry |
| `required_evaluator_ids` | array | sorted unique protected evaluator identifiers |

### 9.2 `action_candidate`

`proposed_value` contains exactly:

- `action_id`: one identifier present in request `allowed_action_ids`
- `parameters`: object conforming to the existing registered action parameter schema

It contains no code, SQL, path, tool, new action, permission request, or budget change.

### 9.3 `abstain`

`proposed_value` contains exactly:

- `reason_code`: bounded identifier

It has no direct execution effect.

### 9.4 `defer`

`proposed_value` contains exactly:

- `reason_code`: bounded identifier

It has no scheduling or retry effect.

### 9.5 Proposal invariants

- exactly one proposal for `proposals_returned`
- no proposal for `unavailable`
- proposal row is immutable after ingress
- one disposition maximum
- no proposal enters action selection in protocol v1

## 10. Response ingress

Schema for protected receipt: `sudachi.consultation.ingress_receipt/v1`

Response ingress is a separate administrative `BEGIN IMMEDIATE` transaction. The caller supplies the external package bytes; administration computes identifiers, canonical bytes, measured sizes, and digests independently.

### 10.1 Receipt fields

| Field | Type | Rule |
| --- | --- | --- |
| `ingress_receipt_id` | identifier | deterministic from dispatch and package digest |
| `ingress_receipt_schema` | string | exact schema identifier |
| `organism_id` | identifier | exact canonical identity |
| `lineage_generation` | integer | exact current and dispatch lineage |
| `request_id` | identifier | exact request |
| `dispatch_id` | identifier | exact dispatch |
| `response_id` | identifier | exact verified response |
| `external_package_digest` | digest | computed from final response/proposals package |
| `response_payload_bytes` | integer | exact canonical response bytes |
| `proposal_payload_bytes` | integer | exact canonical proposal bytes, or zero |
| `provenance_payload_bytes` | integer | exact bounded provenance bytes |
| `ingress_event_sequence` | integer | exact administrative event sequence |
| `authority_category` | string | exactly `administration` |
| `authority_source` | string | exactly `administration:consultation.response_ingress` |

### 10.2 Ingress validation

Before mutation, ingress validates:

- exact protocol and envelope versions
- all identifier derivations
- complete package digest
- exact request and admitted dispatch linkage
- current organism and lineage
- one response maximum
- response/proposal cardinality and allowed types
- current lifecycle not beyond request expiry
- adapter/instance/case provenance equals dispatch admission
- request, response, proposal, provenance, and total logical byte limits
- active database, 1 MiB reserve, checkpoint store, and working-set limits
- protected zero human/model/money/latency expectations

### 10.3 Ingress effects

A valid ingress atomically creates:

- one response row
- zero or one proposal row
- one ingress receipt row
- one administrative event
- measured-byte completion fields in a separate immutable cost-completion row when required by normalization

No existing cost charge is reduced.

Ingress does not checkpoint, dispose, execute, clear maintenance, migrate, or roll back.

### 10.4 Duplicate and failure behavior

- a byte-identical duplicate returns idempotently with no new row, event, clock read, or artifact
- a conflicting duplicate fails closed
- malformed, unknown-version, stale-lineage, expired, over-limit, or incorrectly linked packages fail closed
- if called by the normal dispatch command, a caught non-ingressible fixture result is followed by dispatch terminalization
- a standalone adversarial ingress test may verify exact no-mutation rejection before separately terminalizing its admitted dispatch

## 11. Dispatch terminalization and reconciliation

Schema: `sudachi.consultation.dispatch_terminal/v1`

A dispatch with no valid ingressed response is terminalized exactly once through administration.

### 11.1 Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `dispatch_terminal_id` | identifier | deterministic from dispatch and reason |
| `dispatch_terminal_schema` | string | exact schema identifier |
| `organism_id` | identifier | exact identity |
| `lineage_generation` | integer | exact dispatch lineage |
| `request_id` | identifier | exact request |
| `dispatch_id` | identifier | exact admitted dispatch |
| `terminal_reason` | enum | allowed bounded reason |
| `rejected_package_digest` | digest or absent | present only when invalid bytes existed |
| `rejected_package_bytes` | integer | zero or exact measured bytes |
| `terminal_event_sequence` | integer | exact administrative event |
| `authority_category` | string | exactly `administration` |
| `authority_source` | string | exactly `administration:consultation.dispatch_terminal` |

Allowed reasons:

- `dispatch_interrupted`
- `fixture_output_invalid`
- `expired_before_ingress`

### 11.2 Rules

- one terminal outcome maximum per dispatch
- no terminal outcome if a response already exists
- no response may ingress after terminalization
- no fixture retry is authorized
- a caught fixture error is terminalized by the normal command
- a process crash after admission requires explicit `reconcile-dispatch`
- reconciliation validates exact admitted unresolved dispatch and current lineage
- reconciliation may run while status is `sleeping` or `maintenance_required`, but not during pending checkpoint, rollback, or quarantine
- terminal row and event commit atomically

## 12. Explicit disposition wake

Schema: `sudachi.consultation.disposition/v1`

The disposition wake is a separate organism work class from the garden wake.

### 12.1 Admission and selection

The caller explicitly invokes it. It uses a fresh connection and fail-fast `BEGIN IMMEDIATE` before mutable reads.

It is accepted only when:

- schema version is `2`
- status is `sleeping`
- no checkpoint is pending
- budget config is `phase2-fixture-v1`
- at least one ingressed proposal has no disposition

It claims no garden inbox row.

Selection order is:

1. smallest `ingress_event_sequence`
2. smallest `proposal_id`

At most one proposal is considered.

A no-work, maintenance, pending-checkpoint, busy, unsupported-version, or invalid-state attempt is typed, non-mutating, non-queued, and consumes no organism clock reading unless the accepted wake boundary explicitly requires one.

### 12.2 Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `disposition_id` | identifier | exact deterministic identifier |
| `disposition_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `organism_id` | identifier | exact canonical identity |
| `lineage_generation` | integer | exact current lineage |
| `request_id` | identifier | exact request |
| `dispatch_id` | identifier | exact dispatch |
| `response_id` | identifier | exact response |
| `proposal_id` | identifier | exact proposal |
| `disposition` | enum | accepted/rejected/deferred/clarification_requested |
| `reason_code` | identifier | exact protected evaluator result |
| `disposition_event_sequence` | integer | exact append-only event sequence |
| `disposition_lifecycle_number` | integer | exact considering lifecycle |
| `current_state_reference` | object | canonical current-state/event digest |
| `evaluator_versions` | object | exact protected evaluator IDs and versions |
| `authority_category` | string | exactly `organism` |
| `authority_source` | string | exactly `organism:consultation.disposition` |
| `provenance_parent_event_sequences` | array | exact existing earlier parent events |

### 12.3 Evaluation and semantics

The protected evaluator recomputes linkage, lineage, current state, action/parameter validity, permissions, budgets, expiry, contradiction, ambiguity, and provenance.

#### `accepted`

The proposal is eligible under current state. It is recorded only and has no action effect.

#### `rejected`

Initial reasons include:

- `expired`
- `stale_observation`
- `unknown_action`
- `invalid_parameters`
- `permission_denied`
- `budget_exhausted`
- `contradictory_state`
- `provenance_invalid`

Ingress-level malformed packages do not reach disposition.

#### `deferred`

The evaluator chooses not to decide the proposal. The disposition is final and creates no hidden retry.

#### `clarification_requested`

The package is schema-valid but evidence is materially ambiguous. The disposition is final; clarification budget zero creates no follow-up request.

### 12.4 Wake effects and accounting

An accepted disposition wake:

- increments lifecycle number
- appends one disposition row and one disposition event
- records bounded lifecycle/budget outcome data
- marks the ordinary checkpoint boundary
- commits and stabilizes through existing checkpoint machinery
- changes no garden, inventory, environment, action attempt, or mutation state
- preserves the Phase 1 garden `consecutive_failures` counter exactly

Unexpected internal exceptions roll back. Proposal ineligibility becomes a disposition rather than a garden failure.

Repeated wake cannot create a second disposition.

## 13. Request state derivation

Request state is derived from immutable rows and current canonical lifecycle.

### `awaiting_dispatch`

- request exists
- no dispatch exists
- current lifecycle is at or before expiry

### `expired_before_dispatch`

- request exists
- no dispatch exists
- current lifecycle is beyond expiry

This state no longer counts against the one-outstanding-request limit.

### `dispatch_admitted`

- dispatch exists
- no response and no dispatch terminal exists

This remains outstanding even after expiry and requires response ingress or terminal reconciliation.

### `proposal_queued`

- successful response and proposal exist
- no disposition exists

This remains outstanding until disposition, including when later expired.

### `unavailable`

- response status is unavailable
- no proposal or disposition exists

Terminal.

### `dispatch_terminal`

- dispatch terminal row exists
- no response, proposal, or disposition exists

Terminal.

### `disposed`

- one disposition exists

Terminal.

No mutable caregiver-writable status flag is authoritative.

## 14. Maintenance, checkpoint, and rollback behavior

- request creation never occurs on a garden wake that enters maintenance
- later garden wakes are not blocked by a request; current state can diverge
- dispatch admission requires sleeping and a stable request checkpoint
- response ingress and dispatch terminalization for an already admitted dispatch may record immutable evidence while sleeping or maintenance-required
- disposition wake requires sleeping and cannot clear maintenance
- every committed garden or disposition wake requires ordinary checkpoint stabilization
- dispatch, ingress, and terminal administration do not publish checkpoints
- checkpoint validation includes exact schema-v2 consultation objects and linkage
- rollback may restore a checkpoint before later dispatch/response/disposition rows
- external data from an abandoned lineage fails current-lineage validation
- the existing one-completed-rollback limit and complete evidence retention remain unchanged

## 15. Physical storage rules

Consultation rows, indexes, triggers, SQLite sidecars, checkpoints, staging, rollback archives, source candidates, and transformed candidates count toward existing Phase 1 physical ceilings.

Every dispatch admission, ingress, and terminalization transaction:

1. predicts post-write active database and working-set use
2. requires the write to remain within all hard ceilings
3. preserves the existing 1 MiB next-wake reserve
4. remeasures after writes before commit
5. rolls back on violation

Disposition wakes use the same pre/post storage accounting as other wakes. Protected tests must prove a maximum permitted disposition wake and checkpoint fit within the reserve.

## 16. Deterministic fixture cases

Protocol v1 provides declared cases for:

- valid action candidate
- valid abstain proposal
- valid defer proposal
- unavailable response
- ambiguous evidence producing clarification requested
- stale observation
- expired before dispatch
- expired before ingress
- expired after ingress before disposition
- unknown action identifier
- invalid action parameters
- contradictory current state
- byte-identical duplicate package
- conflicting duplicate package
- malformed response
- unknown schema version
- over-budget package
- fixture exception
- process interruption after dispatch admission

Case selection is declared input, never randomness or network behavior.

## 17. Canonical state concepts

Implementation SQL is deferred to a separate implementation issue, but schema-v2 must preserve normalized immutable concepts for:

- consultation requests
- consultation dispatch admissions
- consultation protected cost charges and measured-byte completions
- consultation responses
- consultation proposals
- consultation ingress receipts
- consultation dispositions
- consultation dispatch terminal outcomes

All identities, versions, digests, links, cardinalities, and no-update/no-delete protections are exact.

Uniqueness enforces:

- one dispatch per request
- one response or one dispatch terminal outcome per dispatch
- zero or one proposal per response according to status
- one ingress receipt per accepted response package
- one disposition per proposal

No new column is added to an original Phase 1 table. Schema-v2 extension state uses new protected objects.

## 18. Zero-caregiver projection

For a schema-v2 organism using `phase2-zero-caregiver-v1`:

1. normalize only existing `schema_version` and `budget_config_version`
2. compare every original Phase 1 table row, column, event payload, and original-table SQLite sequence entry exactly against schema-v1
3. require all operational consultation tables and sequences empty
4. require no consultation event/source, dispatch, fixture import, cost, or effect
5. compare ordinary status, behavior, checkpoints, rollback eligibility, and authority reports

The additional empty schema objects make SQLite bytes and checkpoint digests different; no other semantic normalization is permitted.

## 19. Explicit exclusions

Protocol v1 accepts no:

- live model or human text
- free-form rationale
- memory or skill payload
- source or test patch
- arbitrary code, SQL, shell, tool, path, URL, or credential
- new action definition
- caregiver-declared writer authority or authoritative cost
- budget, permission, evaluator, checkpoint, migration, rollback, or execution command
- network or subprocess capability inside organism execution
- continuous or always-on execution
