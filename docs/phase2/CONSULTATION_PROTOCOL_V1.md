# Phase 2 Consultation Protocol v1

Status: **Proposed for Issue #59 review**

This document fixes the source-neutral envelope and canonical-state semantics referenced by proposed ADR 0008. It is a deterministic fixture protocol, not a live human or model interface.

## Version identifiers

- database schema version: `2`
- consultation protocol version: `1`
- request schema: `sudachi.consultation.request/v1`
- response schema: `sudachi.consultation.response/v1`
- proposal schema: `sudachi.consultation.proposal/v1`
- disposition schema: `sudachi.consultation.disposition/v1`
- cost schema: `sudachi.consultation.cost/v1`
- first budget configuration: `phase2-fixture-v1`
- deterministic fixture adapter: `deterministic-fixture-v1`
- deterministic fixture work class: `fixture-constant-v1`

Unknown versions fail closed before canonical mutation.

## Canonical value rules

All envelope values are canonical JSON-compatible values.

- UTF-8 only
- objects use lexicographically sorted keys for hashing
- arrays preserve declared order
- integers only; no floating-point numbers
- booleans are permitted only where explicitly declared
- `null` is forbidden unless explicitly declared
- strings are NFC-normalized UTF-8 and bounded by the enclosing payload limit
- identifiers match `^[a-z0-9][a-z0-9._:-]{0,127}$`
- digests are lowercase SHA-256 hexadecimal strings
- arbitrary SQL, Python, shell, tool names, filesystem paths, URLs, credentials, executable code, hidden chat history, and opaque binary payloads are forbidden

Canonical JSON bytes use UTF-8, sorted keys, no insignificant whitespace, and separators equivalent to `(',', ':')`.

## Identifier derivation

Identifiers are deterministic and content-linked.

- `request_id = consultation-request:<sha256(request identity input)>`
- `response_id = consultation-response:<sha256(response identity input)>`
- `proposal_id = consultation-proposal:<sha256(proposal identity input)>`
- `disposition_id = consultation-disposition:<sha256(disposition identity input)>`

The identity input excludes the identifier being derived and includes all immutable linkage and version fields. Tests must prove repeated construction from identical declared inputs yields identical identifiers and bytes.

## Request envelope

Schema: `sudachi.consultation.request/v1`

A request is created only by organism runtime inside a wake transaction.

### Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `request_id` | identifier | deterministic digest-derived identifier |
| `request_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `organism_id` | identifier | exact canonical organism identity |
| `lineage_generation` | integer | non-negative and equal to current canonical lineage |
| `request_event_sequence` | integer | exact creating event sequence |
| `request_lifecycle_number` | integer | exact creating lifecycle |
| `reason_code` | enum | exactly `no_applicable_action` in the first protocol |
| `requested_proposal_types` | array | non-empty sorted unique subset of allowed proposal types |
| `observation_reference` | object | event sequence and canonical observation digest |
| `objective_reference` | object | objective identifier, version, and canonical digest |
| `allowed_action_ids` | array | sorted unique existing registered action identifiers |
| `allowed_permission_ids` | array | sorted unique protected permission identifiers |
| `policy_context_version` | string | exact protected policy version |
| `budget_config_version` | string | exactly `phase2-fixture-v1` |
| `consultation_budget_snapshot` | object | exact counters and remaining limits at creation |
| `expires_after_lifecycle_number` | integer | exactly request lifecycle plus `2` |
| `authority_category` | string | exactly `organism` |
| `authority_source` | string | exactly `organism:consultation.request` |
| `provenance_parent_event_sequences` | array | sorted unique non-negative event sequences |

### Optional fields

| Field | Type | Rule |
| --- | --- | --- |
| `declared_context_summary` | object | bounded typed codes and identifiers only; no free text |

The first protocol has no clarification request field because clarification rounds are fixed at zero.

### Allowed requested proposal types

- `action_candidate`
- `abstain`
- `defer`

### Request invariants

- at most one request is created in one wake
- at most one request is outstanding per organism
- at most four requests exist over one organism lifetime
- request canonical JSON is at most 16 KiB
- the request is immutable and may not be updated or deleted
- creation emits one `consultation_request_created` event
- the wake becomes checkpoint-stable before fixture execution

## Response envelope

Schema: `sudachi.consultation.response/v1`

A response is produced outside organism authority and ingressed by administration in a separate transaction.

### Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `response_id` | identifier | deterministic digest-derived identifier |
| `response_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `request_id` | identifier | exact existing outstanding request |
| `caregiver_adapter_type` | string | exactly `deterministic_fixture` |
| `caregiver_adapter_version` | string | exactly `deterministic-fixture-v1` |
| `caregiver_instance_id` | identifier | deterministic declared fixture instance |
| `response_status` | enum | `proposals_returned` or `unavailable` |
| `proposal_ids` | array | exactly one identifier for `proposals_returned`; empty for `unavailable` |
| `payload_digest` | digest | digest of canonical response and proposal payloads |
| `cost_ledger` | object | exact cost schema fields |
| `provenance` | object | request digest, fixture case identifier, adapter versions, and parent identifiers |
| `authority_category` | string | exactly `administration` for canonical ingress |
| `authority_source` | string | exactly `administration:consultation.response_ingress` |

### Response status semantics

#### `proposals_returned`

- contains exactly one proposal
- the proposal is queued for a later disposition wake
- the request remains outstanding until one disposition exists

#### `unavailable`

- contains zero proposals
- records one completed fixture invocation and its zero human/model/money costs
- terminates the request as unavailable
- creates no proposal and no disposition
- permits no retry in the first budget configuration

### Response ingress invariants

- one response maximum per request
- one dispatch attempt maximum per request
- byte-identical duplicate ingress is idempotent
- conflicting duplicate ingress fails closed
- response-plus-proposal canonical JSON is at most 16 KiB
- the provenance subset is at most 8 KiB
- ingress after request expiry fails without canonical mutation
- valid ingress emits one `consultation_response_ingressed` administrative event
- response rows are immutable and may not be updated or deleted
- ingress does not create a checkpoint and does not execute organism behavior

## Proposal envelope

Schema: `sudachi.consultation.proposal/v1`

### Common required fields

| Field | Type | Rule |
| --- | --- | --- |
| `proposal_id` | identifier | deterministic digest-derived identifier |
| `proposal_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `request_id` | identifier | exact parent request |
| `response_id` | identifier | exact parent response |
| `proposal_type` | enum | `action_candidate`, `abstain`, or `defer` |
| `subject_reference` | object | exact objective, observation, or action subject reference |
| `proposed_value` | object | type-specific bounded structure |
| `rationale_code` | identifier | bounded enum-like code; no free text |
| `confidence_basis` | object | typed fixture case and evidence references; no scalar probability required |
| `expires_after_lifecycle_number` | integer | no later than the parent request expiry |
| `required_evaluator_ids` | array | sorted unique protected evaluator identifiers |

### `action_candidate`

`proposed_value` contains exactly:

- `action_id`: one identifier present in the request `allowed_action_ids`
- `parameters`: an object conforming to the existing registered action parameter schema

It may not contain code, SQL, paths, tools, new action definitions, permission requests, or budget changes.

### `abstain`

`proposed_value` contains exactly:

- `reason_code`: one bounded identifier

It has no direct execution effect.

### `defer`

`proposed_value` contains exactly:

- `reason_code`: one bounded identifier

It has no direct scheduling or retry effect in the first protocol.

### Proposal invariants

- exactly one proposal per `proposals_returned` response
- proposal rows are immutable and may not be updated or deleted
- a proposal can receive at most one disposition
- no proposal directly enters action selection in the first implementation slice

## Disposition envelope

Schema: `sudachi.consultation.disposition/v1`

A disposition is created only by organism runtime in a later wake transaction.

### Required fields

| Field | Type | Rule |
| --- | --- | --- |
| `disposition_id` | identifier | deterministic digest-derived identifier |
| `disposition_schema` | string | exact schema identifier |
| `consultation_protocol_version` | integer | exactly `1` |
| `request_id` | identifier | exact request linkage |
| `response_id` | identifier | exact response linkage |
| `proposal_id` | identifier | exact proposal linkage |
| `disposition` | enum | `accepted`, `rejected`, `deferred`, or `clarification_requested` |
| `reason_code` | identifier | exact protected evaluator outcome code |
| `disposition_event_sequence` | integer | exact append-only event sequence |
| `disposition_lifecycle_number` | integer | exact considering lifecycle |
| `current_state_reference` | object | canonical state/event digest used for independent evaluation |
| `evaluator_versions` | object | exact protected evaluator identifiers and versions |
| `authority_category` | string | exactly `organism` |
| `authority_source` | string | exactly `organism:consultation.disposition` |
| `provenance_parent_event_sequences` | array | exact request/response/current-state parent sequences |

### Disposition semantics

#### `accepted`

The proposal is well-formed, correctly linked, unexpired, within budget, permitted, and consistent with current canonical state. In the first slice, it is recorded only and has no action effect.

#### `rejected`

The proposal is ineligible. Initial reason codes include:

- `expired`
- `stale_observation`
- `unknown_action`
- `invalid_parameters`
- `permission_denied`
- `budget_exhausted`
- `contradictory_state`
- `provenance_invalid`

Ingress-level malformed or unknown-version responses do not reach this stage; they fail before canonical mutation.

#### `deferred`

The proposal is valid but the organism elects not to decide it in the current bounded experiment. Because one disposition is final, no hidden retry occurs.

#### `clarification_requested`

The proposal is schema-valid but materially ambiguous under protected evaluation. The disposition is recorded, but clarification rounds are zero, so no follow-up request is created.

### Disposition invariants

- at most one proposal is considered per wake
- exactly one disposition maximum per proposal
- repeated wake cannot create a second disposition
- the disposition wake uses ordinary transaction, event, budget, failure, checkpoint, and maintenance boundaries
- disposition rows are immutable and may not be updated or deleted

## Cost ledger

Schema: `sudachi.consultation.cost/v1`

Required fields:

| Field | Type | First fixture value |
| --- | --- | ---: |
| `fixture_invocations` | integer | `1` |
| `fixture_work_units` | integer | `1` |
| `declared_latency_milliseconds` | integer | `0` |
| `human_minutes` | integer | `0` |
| `model_input_units` | integer | `0` |
| `model_output_units` | integer | `0` |
| `money_minor_units` | integer | `0` |
| `request_payload_bytes` | integer | measured canonical bytes |
| `response_payload_bytes` | integer | measured canonical bytes |
| `provenance_payload_bytes` | integer | measured canonical bytes |

Cost values are immutable audit data. The caregiver cannot set budget limits. Ingress validates declared values against the deterministic fixture adapter and budget configuration.

## Canonical state model

The implementation SQL is deferred to the implementation issue, but it must preserve these normalized immutable concepts:

- consultation requests
- consultation responses
- consultation proposals
- consultation dispositions
- consultation cost ledgers

Each concept has protected identity, version, linkage, and digest constraints. Update and delete are forbidden. Uniqueness enforces:

- one response per request
- one proposal per response when present
- one disposition per proposal

Outstanding and terminal state is derived from immutable rows rather than maintained through caregiver-writable status flags.

## Deterministic fixture cases

The first fixture adapter must provide declared cases for:

- valid `action_candidate`
- valid `abstain`
- valid `defer`
- unavailable caregiver
- stale observation
- expired before ingress
- expired after ingress but before disposition
- unknown action identifier
- invalid action parameters
- contradictory current state
- byte-identical duplicate response
- conflicting duplicate response
- malformed response
- unknown schema version
- over-budget payload

Fixture case selection is a declared test/configuration input, never ambient randomness or hidden network behavior.

## Explicit exclusions

Protocol v1 accepts no:

- live model or human text
- free-form rationale
- memory or skill payload
- source or test patch
- arbitrary code, SQL, shell, tool, path, URL, or credential
- new action definition
- budget, permission, evaluator, checkpoint, migration, or rollback command
- network or subprocess capability inside organism execution
