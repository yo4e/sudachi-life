# Phase 2 Consultation Protocol v1

Status: **Proposed for Issue #59 review**

This document fixes source-neutral envelopes and canonical-state semantics referenced by proposed ADR 0008. It defines a deterministic fixture protocol, not a live human/model interface.

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
- zero-caregiver budget config: `phase2-zero-caregiver-v1`
- fixture budget config: `phase2-fixture-v1`
- fixture adapter version: `deterministic-fixture-v1`
- fixture work class: `fixture-constant-v1`

Unknown versions fail closed before canonical mutation.

## 2. Canonical value rules

All envelope/identity values are canonical JSON-compatible values.

- UTF-8 only
- object keys sorted lexicographically for encoding
- arrays preserve declared order
- sets represented as sorted unique arrays
- integers only; no floating point
- booleans only where declared
- `null` forbidden unless declared
- strings NFC-normalized and bounded
- identifiers match `^[a-z0-9][a-z0-9._:-]{0,127}$`
- digests are lowercase SHA-256 hex
- SQL, Python, shell, tools, paths, URLs, credentials, executable code, hidden chat history, and opaque binary payloads forbidden

Canonical JSON uses UTF-8, sorted keys, no insignificant whitespace, separators equivalent to `(',', ':')`.

## 3. Lineage budget epoch

The consultation budget epoch is exactly current `lineage_generation`.

Phase 1 rollback restores an older checkpoint and creates a new lineage. Protocol v1 does not modify rollback transformation to carry abandoned-future mutable counters.

Rules:

- request ordinals/counters include only rows whose lineage equals current lineage
- outstanding work includes only current-lineage rows
- old-lineage rows remain immutable historical evidence
- old-lineage rows never authorize dispatch, ingress, disposition, or current budget use
- external packages must match current lineage
- rollback begins a new bounded consultation epoch
- `phase2-fixture-v1` permits four charged invocations per lineage epoch
- ADR 0007 permits at most one completed rollback, bounding total charged invocations across one physical organism to at most eight

No cross-lineage global four-call claim is made.

## 4. Digest and identifier construction

### 4.1 General rule

Each identifier is:

```text
<prefix>:<sha256(canonical identity object)>
```

The derived identifier and later-assigned event sequence are excluded only where explicitly listed.

### 4.2 Request identity

```text
request_id = consultation-request:<sha256(request identity object)>
```

Identity object contains exactly:

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

### 4.3 Dispatch identity

```text
dispatch_id = consultation-dispatch:<sha256(dispatch identity object)>
```

Identity object contains exactly:

- `dispatch_schema`
- protocol version
- organism ID
- lineage generation
- request ID
- dispatch ordinal `1`
- adapter version
- fixture case ID
- fixture work class

It excludes dispatch ID/event sequence/wall timestamp.

### 4.4 Proposal identity

```text
proposal_id = consultation-proposal:<sha256(proposal identity object)>
```

Identity object contains exactly:

- proposal schema/protocol
- request ID
- dispatch ID
- proposal ordinal `1`
- proposal type
- subject reference
- proposed value
- rationale code
- confidence basis
- expiry lifecycle
- required evaluator IDs

It excludes proposal ID and response ID.

Its digest is `proposal_content_digest`.

### 4.5 Response identity

```text
response_id = consultation-response:<sha256(response identity object)>
```

Identity object contains exactly:

- response schema/protocol
- request ID
- dispatch ID
- adapter type/version/instance
- response status
- ordered proposal IDs
- ordered proposal content digests
- bounded external provenance

It excludes response ID.

After response ID derivation, it is inserted into final proposal linkage. Complete package digest is:

```text
sha256(canonical JSON({"response": <final response>, "proposals": [<final proposal>] }))
```

For unavailable response, proposals is empty.

### 4.6 Disposition identity

```text
disposition_id = consultation-disposition:<sha256(disposition identity object)>
```

Identity object contains exactly:

- disposition schema/protocol
- organism ID
- current lineage
- request/dispatch/response/proposal IDs
- disposition/reason
- disposition lifecycle
- current-state reference
- evaluator versions

It excludes disposition ID/event sequence/wall timestamp.

### 4.7 Reproducibility

Two independent constructions from identical declared inputs must produce identical identity objects, IDs, envelopes, content/package digests, rows, and event payloads.

Tests must prove no response/proposal circular dependency.

## 5. Protected budget configurations

### 5.1 `phase2-zero-caregiver-v1`

All consultation request, dispatch, fixture work, response, proposal, disposition, clarification, payload, human, model, money, and consultation-record limits are zero.

Operational consultation tables remain empty. No consultation event/source or fixture import/invocation occurs.

### 5.2 `phase2-fixture-v1`

| Resource | Limit |
| --- | ---: |
| requests per eligible garden wake | 1 |
| outstanding requests in current lineage | 1 |
| requests per lineage epoch | 4 |
| dispatch admissions per request | 1 |
| charged fixture invocations per lineage epoch | 4 |
| successful responses per request | 1 |
| proposals per successful response | 1 |
| proposals considered per disposition wake | 1 |
| dispositions per proposal | 1 |
| clarification rounds | 0 |
| request JSON bytes | 16 KiB |
| response-plus-proposal JSON bytes | 16 KiB |
| external provenance bytes | 8 KiB |
| total logical consultation payload per lineage | 64 KiB |
| fixture work units charged per dispatch | 1 |
| human minutes | 0 |
| model input units | 0 |
| model output units | 0 |
| money minor units | 0 |
| declared fixture latency ms | 0 |
| Phase 1 core records in request garden wake | <=16 |
| extra request records | <=2 |
| total request garden-wake records | <=18 |
| disposition wake semantic steps | <=10 |
| disposition wake records | <=12 |
| dispatch admission records | <=3 |
| response ingress records | <=5 |
| dispatch terminal records | <=3 |

All administrative writes perform predicted/post-write active DB and working-set accounting and preserve the inherited 1 MiB next-wake reserve.

## 6. Request envelope

Schema: `sudachi.consultation.request/v1`

Created only by organism runtime inside schema-v2 garden wake.

### 6.1 Required fields

| Field | Rule |
| --- | --- |
| `request_id` | exact deterministic ID |
| `request_schema` | exact schema |
| `consultation_protocol_version` | `1` |
| `organism_id` | canonical identity |
| `lineage_generation` | exact current lineage |
| `request_ordinal` | current-lineage request count + 1; `1..4` |
| `request_event_sequence` | exact creating event |
| `request_lifecycle_number` | exact garden lifecycle |
| `reason_code` | `no_applicable_action` |
| `requested_proposal_types` | sorted unique non-empty allowed subset |
| `observation_reference` | event sequence + canonical digest |
| `objective_reference` | ID/version/digest |
| `allowed_action_ids` | sorted unique registered IDs |
| `allowed_permission_ids` | sorted unique protected IDs |
| `policy_context_version` | exact policy version |
| `budget_config_version` | `phase2-fixture-v1` |
| `consultation_budget_snapshot` | current-lineage counters/remaining limits |
| `expires_after_lifecycle_number` | request lifecycle + 2 |
| `authority_category` | `organism` |
| `authority_source` | `organism:consultation.request` |
| `provenance_parent_event_sequences` | sorted unique existing earlier current-lineage events |

Optional `declared_context_summary` is bounded typed codes/IDs only, no free text.

Allowed requested types:

- `action_candidate`
- `abstain`
- `defer`

### 6.2 Admission

Request admission occurs only after unchanged Phase 1 policy selects `no_applicable_action` for incomplete objective.

Create request only when:

- config is fixture config
- no current-lineage outstanding request
- fewer than four current-lineage requests
- resulting garden failure streak remains below maintenance threshold
- logical/physical/reserve budgets fit

Garden lifecycle remains Phase 1 no-applicable abstention and increments `consecutive_failures` exactly once. Request never resets/replaces accounting.

Zero-caregiver config creates no consultation row/event/source/import.

### 6.3 Invariants

- one request/wake
- one current-lineage outstanding request
- four requests/current lineage
- request <=16 KiB
- row/event atomic and immutable
- one `consultation_request_created` organism event
- stable request checkpoint before dispatch
- no request on maintenance-entering wake

## 7. Dispatch admission

Schema: `sudachi.consultation.dispatch/v1`

Administrative fresh fail-fast `BEGIN IMMEDIATE`.

### 7.1 Required fields

| Field | Rule |
| --- | --- |
| `dispatch_id` | exact deterministic ID |
| `dispatch_schema` | exact schema |
| protocol | `1` |
| organism/lineage | exact current |
| `request_id` | eligible current-lineage request |
| `dispatch_ordinal` | `1` |
| adapter type | `deterministic_fixture` |
| adapter version | `deterministic-fixture-v1` |
| adapter instance | deterministic declared ID |
| `fixture_case_id` | protected declared case |
| work class | `fixture-constant-v1` |
| `dispatch_event_sequence` | exact administrative event |
| authority | `administration:consultation.dispatch_admitted` |

### 7.2 Admission checks

Require:

- schema2/protocol1
- sleeping
- no pending checkpoint
- stable checkpoint at/beyond request event
- request lineage equals current lineage
- current lifecycle <= expiry
- no prior dispatch
- request nonterminal
- current-lineage dispatch/work/payload budgets fit
- physical ceilings/reserve fit

### 7.3 Conservative cost charge

Same transaction creates immutable cost charge:

- `dispatch_attempts=1`
- `fixture_invocations_charged=1`
- `fixture_work_units_charged=1`
- human/model/money/latency all zero
- request payload bytes exact
- response/provenance measured completion absent until ingress

Charge remains if process crashes before call.

### 7.4 Invariants

- one admission/request
- dispatch + cost + event atomic
- no fixture before commit
- repeated admission never authorizes call
- no write lock during fixture
- rows immutable
- no checkpoint/action

## 8. External deterministic fixture

Fixture receives exactly:

1. canonical request envelope
2. protected `fixture_case_id`

Returns one external package or bounded error.

No DB/state path/workspace/repository/executor/evaluator/budget/checkpoint/rollback/network/subprocess/randomness handle.

Fixture package is returned to explicit caller/harness. It remains noncanonical until ingress.

Identical request/case yields identical bytes, but only one charged fixture attempt is allowed.

## 9. External response envelope

Schema: `sudachi.consultation.response/v1`

Untrusted caregiver data; no writer authority or authoritative cost.

### 9.1 Required fields

| Field | Rule |
| --- | --- |
| `response_id` | exact deterministic ID |
| response schema/protocol | exact/current |
| request/dispatch | exact parent linkage |
| adapter type/version/instance | exact dispatch provenance |
| `response_status` | `proposals_returned` or `unavailable` |
| `proposal_ids` | one for success; empty unavailable |
| `proposal_content_digests` | matches proposal IDs; empty unavailable |
| `provenance` | request digest, dispatch, case, adapter, bounded parents |

Forbidden:

- authority category/source
- canonical event sequence
- budget limit
- authoritative cost
- permission/evaluator/checkpoint/migration/rollback/execution command

### 9.2 Status

`proposals_returned`: exactly one proposal.

`unavailable`: zero proposals; valid fixture result; terminal after ingress; no retry/disposition.

## 10. Proposal envelope

Schema: `sudachi.consultation.proposal/v1`

### 10.1 Common fields

| Field | Rule |
| --- | --- |
| proposal ID/schema/protocol | exact |
| request/dispatch/response IDs | exact |
| proposal ordinal | `1` |
| type | action_candidate/abstain/defer |
| subject reference | exact objective/observation/action subject |
| proposed value | exact type-specific object |
| rationale code | bounded; no free text |
| confidence basis | typed case/evidence; no required probability |
| expiry | <= parent request expiry |
| required evaluators | sorted unique protected IDs |

`action_candidate` value: existing allowed `action_id` + registered-schema parameters only.

`abstain` value: bounded `reason_code` only.

`defer` value: bounded `reason_code` only; no scheduling/retry effect.

Proposal is immutable, exactly one on success, none unavailable, one disposition max, no action selection.

## 11. Response ingress

Protected receipt schema: `sudachi.consultation.ingress_receipt/v1`

Separate administrative fresh fail-fast transaction. Caller supplies external package bytes; administration independently computes IDs, canonical bytes, sizes, and digests.

### 11.1 Receipt fields

- deterministic receipt ID from dispatch + package digest
- exact schema
- organism/current lineage
- request/dispatch/response IDs
- complete external package digest
- response/proposal/provenance byte counts
- exact ingress event sequence
- `authority_category=administration`
- `authority_source=administration:consultation.response_ingress`

### 11.2 Preconditions

- status sleeping or maintenance-required
- no pending checkpoint
- no rollback/quarantine
- dispatch exists in current lineage
- no dispatch terminal
- current lifecycle <= request expiry
- exact protocol/envelope versions
- all ID derivations/package digest valid
- adapter/instance/case equals dispatch
- response/proposal cardinality/type valid
- logical limits, current-lineage epoch limit, physical limits, reserve fit
- protected zero human/model/money/latency expectations

Current garden state consistency is not required at ingress; it is evaluated later at disposition.

### 11.3 Effects

Atomically create:

- response row
- zero/one proposal row
- ingress receipt
- administrative event
- separate immutable measured-byte cost completion when normalized schema needs it

No original cost charge is reduced.

No checkpoint, disposition, action, maintenance clear, migration, or rollback.

### 11.4 Duplicates/failure

- byte-identical duplicate: idempotent, no new row/event/clock/artifact
- conflicting duplicate: fail closed
- malformed/version/lineage/expiry/limit/link failure: fail closed
- busy/pending-checkpoint rejection may be explicitly retried later using identical already-produced bytes; never automatically queued and never re-invokes fixture
- invalid fixture output is later terminalized once

## 12. Dispatch terminalization and reconciliation

Schema: `sudachi.consultation.dispatch_terminal/v1`

One terminal outcome for admitted dispatch with no valid response.

### 12.1 Fields

- deterministic terminal ID
- exact schema
- organism + dispatch lineage
- request/dispatch IDs
- terminal reason
- optional rejected-package digest
- rejected-package byte count
- terminal event sequence
- `administration:consultation.dispatch_terminal`

Reasons:

- `dispatch_interrupted`
- `fixture_output_invalid`
- `expired_before_ingress`

### 12.2 Preconditions/rules

- status sleeping or maintenance-required
- no pending checkpoint/rollback/quarantine
- dispatch current-lineage and unresolved
- one terminal max
- no terminal after response
- no response after terminal
- no fixture retry
- caught fixture error terminalized by normal workflow
- process crash requires explicit `reconcile-dispatch`
- reconciliation invokes no fixture
- row/event atomic, immutable, no checkpoint

## 13. Explicit disposition wake

Schema: `sudachi.consultation.disposition/v1`

Separate organism work class from garden wake.

### 13.1 Admission/selection

Caller explicitly invokes it. Fresh connection and fail-fast `BEGIN IMMEDIATE` before mutable reads.

Require:

- schema2
- sleeping
- no pending checkpoint
- fixture config
- queued current-lineage proposal without disposition

Claims no garden inbox row.

Selection:

1. smallest ingress event sequence
2. smallest proposal ID

At most one proposal.

No-work/maintenance/pending/busy/unsupported/invalid attempts are typed, nonmutating, nonqueued, and consume zero clock where rejection path is specified.

### 13.2 Required fields

- deterministic disposition ID/schema/protocol
- organism/current lineage
- request/dispatch/response/proposal IDs
- disposition: accepted/rejected/deferred/clarification_requested
- protected reason code
- event sequence
- considering lifecycle
- current-state reference
- evaluator versions
- `organism:consultation.disposition`
- exact existing earlier current-lineage parent events

### 13.3 Evaluation

Protected evaluator recomputes linkage, lineage, current state, action/parameter validity, permission, budget, expiry, contradiction, ambiguity, provenance.

`accepted`: eligible; recorded only, no action effect.

`rejected` initial reasons:

- expired
- stale_observation
- unknown_action
- invalid_parameters
- permission_denied
- budget_exhausted
- contradictory_state
- provenance_invalid

`deferred`: evaluator does not decide; final, no retry.

`clarification_requested`: schema-valid but materially ambiguous; final, no follow-up due zero clarification budget.

### 13.4 Effects/accounting

Accepted disposition wake:

- increments lifecycle
- appends one disposition row/event
- records bounded lifecycle/budget outcome
- marks ordinary checkpoint pending
- commits/stabilizes via existing checkpoint machinery
- changes no garden/inventory/environment/action-attempt/mutation state
- preserves Phase 1 garden failure streak exactly

Unexpected internal exceptions roll back. Ineligible proposal becomes disposition, not garden failure. Repeated wake cannot create second disposition.

## 14. Current-lineage request state derivation

Only rows matching current lineage can be active.

### `awaiting_dispatch`

Request current-lineage, no dispatch, lifecycle <= expiry.

### `expired_before_dispatch`

Request current-lineage, no dispatch, lifecycle > expiry. Terminal for admission; no longer outstanding.

### `dispatch_admitted`

Current-lineage dispatch exists, no response/terminal. Outstanding even after expiry; needs response or terminal reconciliation.

### `proposal_queued`

Current-lineage success response/proposal, no disposition. Outstanding until disposition, even if later expired.

### `unavailable`

Current-lineage unavailable response; terminal, no proposal/disposition.

### `dispatch_terminal`

Current-lineage terminal row; terminal, no response/proposal/disposition.

### `disposed`

Current-lineage disposition; terminal.

Old-lineage rows are `historical_lineage` and never active/outstanding/budget-counting.

No mutable caregiver-writable status flag is authoritative.

## 15. Maintenance, checkpoint, rollback

- no request on maintenance-entering garden wake
- later garden wakes not blocked by request; state may diverge
- dispatch requires sleeping/stable request checkpoint
- ingress/terminal for already-admitted current-lineage dispatch may run sleeping/maintenance-required, with no pending checkpoint
- disposition requires sleeping; never clears/bypasses maintenance
- committed garden/disposition wakes checkpoint normally
- dispatch/ingress/terminal admin transactions do not checkpoint
- checkpoint validation covers exact schema2 objects/linkage
- rollback may restore checkpoint before later consultation rows
- rollback increments lineage; prior-lineage rows become historical
- external package from abandoned lineage fails before mutation
- existing one-completed-rollback limit/evidence retention unchanged

## 16. Physical storage

Consultation rows/indexes/triggers/sidecars/checkpoints/staging/rollback archives/candidates count toward inherited physical ceilings.

Each dispatch/ingress/terminal transaction:

1. predicts active DB/working set
2. requires hard ceilings
3. preserves 1 MiB next-wake reserve
4. remeasures after writes before commit
5. rolls back on violation

Disposition uses same pre/post accounting as other wakes. Tests prove maximum disposition plus checkpoint fits reserve.

## 17. Deterministic fixture cases

Declared cases:

- valid action candidate
- valid abstain
- valid defer
- unavailable
- ambiguous evidence -> clarification requested
- stale observation
- expired before dispatch
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

Case selection is declared input, never randomness/network.

## 18. Canonical state concepts

Implementation SQL is deferred, but schema2 must normalize immutable concepts:

- requests
- dispatch admissions
- protected cost charges
- measured-byte cost completions
- responses
- proposals
- ingress receipts
- dispositions
- dispatch terminal outcomes

All IDs/versions/digests/links/cardinalities/no-update/no-delete protections exact.

Uniqueness:

- one dispatch/request within lineage
- one response or one terminal/dispatch
- zero/one proposal/response by status
- one receipt/accepted response package
- one disposition/proposal

No new column in original Phase 1 table. Extension uses new protected objects.

## 19. Zero-caregiver projection

For schema2 zero config:

1. normalize only existing schema/budget config values
2. compare every original Phase 1 row, column, event payload, original-table sequence exactly
3. require operational consultation tables/sequences empty
4. require no consultation event/source/dispatch/import/cost/effect
5. compare status/behavior/checkpoints/rollback/authority

Extra empty schema objects make SQLite bytes/checkpoint digests differ; no other semantic normalization allowed.

## 20. Explicit exclusions

No:

- live model/human text
- free-form rationale
- memory/skill payload
- source/test patch
- arbitrary code/SQL/shell/tool/path/URL/credential
- new action definition
- caregiver-declared writer authority/cost
- budget/permission/evaluator/checkpoint/migration/rollback/execution command
- network/subprocess inside organism execution
- continuous/always-on execution
