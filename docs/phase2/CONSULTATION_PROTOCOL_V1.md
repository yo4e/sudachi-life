# Phase 2 Consultation Protocol v1

Status: **Accepted with ADR 0008**

This document defines the accepted source-neutral deterministic-fixture protocol for ADR 0008. It is not a live human or model interface. The caregiver side produces bounded untrusted data; it never receives organism authority.

## 1. Versions

- database schema: `2`
- base contract: `0.2`
- consultation protocol: `1`
- request schema: `sudachi.consultation.request/v1`
- dispatch schema: `sudachi.consultation.dispatch/v1`
- response schema: `sudachi.consultation.response/v1`
- proposal schema: `sudachi.consultation.proposal/v1`
- ingress receipt schema: `sudachi.consultation.ingress_receipt/v1`
- disposition schema: `sudachi.consultation.disposition/v1`
- dispatch terminal schema: `sudachi.consultation.dispatch_terminal/v1`
- cost schema: `sudachi.consultation.cost/v1`
- zero-caregiver config: `phase2-zero-caregiver-v1`
- fixture config: `phase2-fixture-v1`
- fixture adapter: `deterministic-fixture-v1`
- fixture work class: `fixture-constant-v1`
- zero-caregiver projection: `phase1-projection-v2`
- frozen Phase 1 budget configuration: `phase1-v1`

Unknown versions fail closed before canonical mutation.

## 2. Canonical values and bytes

- UTF-8 only
- strings NFC-normalized
- object keys lexicographically sorted
- arrays preserve declared order
- sets encoded as sorted unique arrays
- integers only; no floating point
- booleans only where declared
- `null` forbidden unless declared
- identifiers match `^[a-z0-9][a-z0-9._:-]{0,127}$`
- digests are lowercase SHA-256 hex
- no arbitrary SQL, Python, shell, tools, paths, URLs, credentials, executable code, hidden chat history, or opaque binary payloads

`canonical_json(value)` is UTF-8 JSON with sorted keys, no insignificant whitespace, and separators equivalent to `(',', ':')`.

`canonical_size(value)` is the byte length of the final canonical envelope after all identifiers/linkage fields are inserted.

## 3. Exact digest preimages

Every protocol digest uses:

```text
H(label, value) = sha256(
    UTF8("sudachi.consultation/v1\n" + label + "\n")
    || canonical_json(value)
)
```

Labels are exact and case-sensitive:

- `request-id`
- `dispatch-id`
- `proposal-content`
- `response-id`
- `external-package`
- `current-state-reference`
- `disposition-id`

No NUL separator, alternate prefix, pretty JSON, recursive normalization, or undeclared field exclusion is allowed.

### 3.1 Request

```text
request_id = "consultation-request:" + H("request-id", request_identity)
```

`request_identity` contains exactly:

- request schema/protocol version
- organism ID/current lineage
- current-lineage request ordinal
- request lifecycle
- reason code/requested proposal types
- observation/objective digests
- allowed action/permission IDs
- policy version, frozen Phase 1 budget config version, and consultation configuration version
- expiry lifecycle

It excludes request ID, later event sequence, wall time, and event-authority metadata.

### 3.2 Dispatch

```text
dispatch_id = "consultation-dispatch:" + H("dispatch-id", dispatch_identity)
```

`dispatch_identity` contains exactly schema/protocol, organism/current lineage, request ID, ordinal `1`, adapter version, fixture case, and work class. It excludes dispatch ID, later event sequence, and wall time.

### 3.3 Proposal

```text
proposal_content_digest = H("proposal-content", proposal_identity)
proposal_id = "consultation-proposal:" + proposal_content_digest
```

`proposal_identity` contains exactly:

- proposal schema/protocol
- request/dispatch IDs
- ordinal `1`
- proposal type
- subject reference
- proposed value
- rationale code
- confidence basis
- expiry lifecycle
- required evaluator IDs

It excludes proposal ID and response ID.

### 3.4 Response and package

```text
response_id = "consultation-response:" + H("response-id", response_identity)
```

`response_identity` contains exactly schema/protocol, request/dispatch IDs, adapter type/version/instance, response status, ordered proposal IDs/content digests, and bounded external provenance. It excludes response ID.

After response ID is inserted into final proposal linkage, package preimage is exactly:

```json
{"response": <final response envelope>, "proposals": [<final proposal envelope>]}
```

It has exactly those two keys.

```text
external_package_digest = H("external-package", package_preimage)
```

For `unavailable`, proposals is empty.

### 3.5 Current state and disposition

```text
current_state_digest = H("current-state-reference", current_state_identity)
```

The implementation issue must enumerate the versioned protected current-state projection before disposition code is accepted.

```text
disposition_id = "consultation-disposition:" + H("disposition-id", disposition_identity)
```

Disposition identity contains exact schema/protocol, organism/current lineage, request/dispatch/response/proposal IDs, disposition/reason, disposition lifecycle, current-state digest, and evaluator versions. It excludes disposition ID, later event sequence, and wall time.

Protected golden tests prove exact preimage bytes, IDs, envelopes, package bytes, reproducibility, and no proposal/response cycle.

## 4. Budgets

### 4.1 Protected consultation configuration and zero-caregiver

The original Phase 1 `budget_config` singleton, `organism.budget_config_version`, and original event `budget_config_version` remain exactly `phase1-v1`.

Phase 2 policy exists only in the protected singleton `consultation_configuration(singleton_id, protocol_version, configuration_version, configuration_json)` defined by ADR 0009. Exactly one canonical row exists and its canonical JSON equals one repository-defined protected object. Unknown, missing, duplicate, mixed, noncanonical, or mutated configuration fails before canonical mutation.

`phase2-zero-caregiver-v1` sets all consultation request, dispatch, fixture, response, proposal, disposition, clarification, logical-payload, human, model, money, declared-latency, and consultation-record allowances to zero.

No operational consultation table row/sequence, consultation event/source, cost, adapter or fixture import/invocation, terminal/disposition, or caregiver effect exists.

`consultation_configuration.configuration_version` is included in every consultation request/dispatch identity and every consultation row/event that declares configuration. It never aliases the Phase 1 budget version.

### 4.2 Fixture

| Resource | Limit |
| --- | ---: |
| request per garden wake | 1 |
| outstanding request/current lineage | 1 |
| requests/current lineage | 4 |
| dispatch/request | 1 |
| charged fixture invocations/current lineage | 4 |
| successful response/request | 1 |
| proposal/successful response | 1 |
| proposal considered/disposition wake | 1 |
| disposition/proposal | 1 |
| clarification rounds | 0 |
| request final envelope | 16 KiB |
| complete external package | 16 KiB |
| external provenance | 8 KiB within package limit |
| logical payload/current lineage | 64 KiB |
| human/model/money/declared latency | 0 |
| Phase 1 core records/request wake | at most 16 |
| additional request records | at most 2 |
| total request-wake records | at most 18 |
| disposition semantic steps | at most 10 |
| disposition records | at most 12 |
| dispatch records | at most 3 |
| ingress records | at most 5 |
| terminalization records | at most 3 |

Exact logical payload for current lineage `g`:

```text
lineage_payload_bytes(g) =
    sum(canonical_size(final_request_envelope))
    + sum(canonical_size(successfully_ingressed_package_preimage))
```

- each request counted once
- each successfully ingressed `proposals_returned`/`unavailable` package counted once
- response/proposal/provenance already inside package and never counted again
- provenance 8 KiB is inside package 16 KiB, not extra
- duplicate ingress adds zero
- dispatch/cost/receipt/disposition/terminal metadata excluded logically but included physically
- invalid pre-mutation package adds no logical payload; bounded terminal digest/size counts physically
- checks occur before and after mutation using measured canonical bytes

Inherited physical limits remain 8 MiB active DB, 40 MiB checkpoints, 64 MiB working set, and 1 MiB next-wake active-DB reserve.

## 5. Garden request wake

A request may be created only after unchanged Phase 1 policy selects `no_applicable_action` for an incomplete objective.

Required request fields:

- IDs/schema/protocol/organism/current lineage/ordinal/event sequence/lifecycle
- reason exactly `no_applicable_action`
- sorted unique requested proposal types
- observation/objective references
- sorted allowed actions/permissions
- policy version, frozen Phase 1 budget version, and consultation configuration version
- exact pre-creation budget snapshot
- expiry exactly lifecycle + 2
- authority exactly `organism` / `organism:consultation.request`
- sorted existing parent events

Optional context is bounded typed codes/IDs only; no free text.

The core wake remains exact Phase 1 behavior: same input/action/mutation/outcome/failure accounting, failure increment once, no failure reset, and no request on maintenance entry.

### 5.1 Optional storage-safe extension

Request metadata is an optional savepoint extension after Phase 1 core records:

1. predict core, extension, checkpoint, sidecars, reserve, and working-set use
2. if extension cannot fit, write no consultation state
3. otherwise create request row/event in extension savepoint
4. measure post-write use before releasing savepoint
5. if extension crosses a limit, roll back only extension
6. commit unchanged Phase 1 core wake and ordinary checkpoint

On extension refusal:

- no request/event/source/partial cost
- Phase 1 outcome remains exact
- caller gets noncanonical `consultation_request_not_created_storage_budget`
- next-wake reserve remains

If the core Phase 1 wake/checkpoint cannot fit, frozen Phase 1 behavior applies.

Created request row/event are atomic and checkpoint-stable before dispatch.

## 6. Dispatch

Fresh fail-fast administrative transaction requiring schema-v2, sleeping, no pending checkpoint/rollback/quarantine, stable request checkpoint, current lineage, unexpired/nonterminal request, no prior dispatch, and fitting budgets.

It atomically records one dispatch, one cost charge, and one administrative event.

Charge: one attempt, one fixture invocation, one work unit, exact request bytes, zero human/model/money/latency. Commit and release SQLite before fixture. Never refund. Repeated admission never authorizes another call.

## 7. Fixture

Runs only after dispatch commit and outside every SQLite write transaction.

Receives exactly final request envelope and declared case ID. Receives no DB/path/workspace/repository/executor/evaluator/checkpoint/migration/rollback/network/subprocess/credential/tool/randomness capability.

Output is noncanonical before ingress.

## 8. Response and exact proposal schemas

### 8.1 Response

Exact fields: response ID/schema/protocol, request/dispatch IDs, adapter type `deterministic_fixture`, adapter version `deterministic-fixture-v1`, instance ID, status, ordered proposal IDs/content digests, bounded provenance.

Statuses:

- `proposals_returned`: exactly one proposal
- `unavailable`: zero proposals

### 8.2 Proposal common fields

Exact fields:

- proposal ID/schema/protocol
- request/dispatch/response IDs
- ordinal `1`
- type
- subject reference
- proposed value
- rationale code
- confidence basis
- expiry
- sorted unique required evaluator IDs

Common constraints:

- expiry equals linked request expiry exactly
- confidence basis exactly `{"basis_type":"deterministic_fixture_case","fixture_case_id":<dispatch case>}`
- evaluator IDs equal protected type set
- all references match current-lineage request/dispatch
- no undeclared field

### 8.3 Action candidate

- subject exactly `{"action_id":<request-allowed action>}`
- value exactly `{"parameters":<registered schema-valid object>}`
- rationale exactly `existing_action_applicable`
- evaluators exactly `action-schema-v1`, `current-state-v1`, `permission-v1`

Cannot define action/code/tool/path/SQL/permission/budget.

### 8.4 Abstain

- subject exactly linked objective reference
- value exactly `{"reason_code":"no_supported_action"}`
- rationale exactly `no_supported_action`
- evaluators exactly `abstain-policy-v1`, `current-state-v1`

### 8.5 Defer

- subject exactly linked objective reference
- value exactly `{"reason_code":"await_state_change"}`
- rationale exactly `await_state_change`
- evaluators exactly `current-state-v1`, `defer-policy-v1`

No schedule, wake time, retry, or state effect.

External package contains no writer authority or authoritative cost/budget/permission/evaluator/checkpoint/migration/rollback/execution command.

## 9. Ingress

Fresh fail-fast administrative transaction.

Before mutation administration verifies raw size before JSON parse, exact versions/fields, all preimages/IDs/digests, request/dispatch/adapter/case/lineage/expiry/cardinality linkage, exact proposal schema/evaluator set, canonical sizes, logical formula, and all physical ceilings.

Successful ingress atomically records response, optional proposal, protected receipt, measured-byte completion, and one administrative event.

Receipt authority is exactly administration / `administration:consultation.response_ingress`, with package digest, measured bytes, and exact parents.

Ingress cannot adopt/execute/clear maintenance/checkpoint/migrate/rollback/change budgets or permissions.

Byte-identical duplicate is idempotent and adds no event/clock/charge/payload. Conflicting duplicate fails closed. Busy/pending-only rejection permits explicit identical-byte resubmission without fixture recall. `unavailable` terminalizes with no proposal/disposition.

## 10. Terminalization

Reasons:

- `dispatch_interrupted`
- `fixture_output_invalid`
- `expired_before_ingress`

Caught failure terminalizes explicitly. Crash after dispatch leaves charged unresolved work. Explicit reconciliation may record interruption but never invokes fixture. Response and terminal are mutually exclusive. Repeated terminalization is idempotent. Only bounded rejected digest/size/reason/linkage/event is retained.

## 11. Disposition wake

Separate caller-selected work class, no hidden priority.

Fresh fail-fast wake requiring fixture-configured schema-v2, sleeping, no pending checkpoint. Claims no garden input; selects oldest current-lineage proposal by ingress sequence then proposal ID; considers one; validates exact schemas/linkage/current state/permissions/evaluators/budgets/considering-lifecycle expiry; records one disposition; increments lifecycle while preserving garden failure streak; checkpoints.

Dispositions:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

Clarification final because zero rounds. First implementation records disposition only; no selector/action/garden/memory/skill effect.

## 12. Lineage and expiry

Current lineage is budget epoch. Old-lineage rows are immutable history and inactive. Rollback starts fresh four-call epoch. ADR 0007 permits one rollback: at most two epochs/eight charged calls. Abandoned packages/proposals fail before mutation.

Request at lifecycle `N` eligible for dispatch/ingress through `N+2`. Proposal inherits exact request expiry. Disposition considering lifecycle through `N+2` may be eligible; `N+3` or later is final rejected/expired. Wall time never controls eligibility.

Derived state:

- pre-dispatch expired: no longer outstanding
- admitted dispatch: outstanding until response/terminal
- unavailable: terminal
- successful response: outstanding until disposition
- terminal/disposition: final

No caregiver-writable status flag.

## 13. Maintenance, checkpoint, rollback

- request does not block later garden wakes
- dispatch requires sleeping/stable request checkpoint
- ingress/terminalization may record admitted evidence while sleeping or maintenance-required, never behind pending checkpoint/rollback/quarantine
- cannot clear maintenance
- disposition requires sleeping and cannot bypass maintenance
- garden/disposition checkpoint; admin dispatch/ingress/terminal do not
- rollback increments lineage and deactivates prior-lineage rows
- ADR 0007 evidence/limit unchanged

## 14. Canonical objects

New protected immutable objects: requests, dispatches, cost charges/completions, responses, proposals, receipts, dispositions, terminal outcomes.

No original Phase 1 table gains a column. IDs/versions/digests/links/cardinalities/uniqueness/update-delete protections are exact.

## 15. Exact zero-caregiver semantic artifact projection

ADR 0009 is normative for `phase1-projection-v2`. Paired schema-v1/schema-v2-zero scenarios use identical declared inputs, clocks, administrative reasons, fault choices, selected semantic boundaries, and operation order.

Each run is first validated independently. The cross-run projection then:

1. keeps the original Phase 1 budget singleton and every original budget-version location exactly `phase1-v1`
2. normalizes only the exact original schema-version locations declared by ADR 0009
3. maps checkpoint IDs, rollback archive/candidate IDs, retention staging names, canonical event payload references, and export source identities only at the exact table/column or event-type/JSON paths declared by ADR 0009
4. omits exact byte-derived SHA, size, and aggregate-byte locations only after recomputation, one-to-one linkage validation, and absolute physical-budget validation on each side
5. compares every unlisted original table field, event, sequence, authority source, parent, payload key/value, manifest field, and semantic boundary exactly
6. requires the exact protected `consultation_configuration` singleton and zero operational consultation rows/sequences/events/imports/effects

The projection covers normal and maintenance checkpoint stabilization, registration repair, retention prune/failure/reconciliation, rollback archive/source candidate/transformed candidate/completion, and semantic event export. Administrative presentation paths and raw bytes are noncanonical and are validated separately.

No wildcard, recursive walk, suffix/prefix match, global key-name normalization, or added/missing-key masking is allowed.

Schema-v2 structural overhead is tested separately: at most 256 KiB for the active database and each checkpoint/archive/candidate database relative to its paired schema-v1 artifact, at most 1 MiB aggregate additional manifest/directory metadata, and exact compliance with the inherited 8/40/64 MiB ceilings and 1 MiB reserve. Cross-version byte-threshold equality at a physical ceiling is not claimed.

## 16. Fixture cases

Required declared cases: valid action/abstain/defer, unavailable, stale observation, expiry before ingress, expiry after ingress, unknown action, invalid parameters, contradictory state, identical duplicate, conflicting duplicate, malformed response, unknown schema, over-budget, fixture exception, crash after admission, abandoned-lineage package.

Case selection is declared, never random/network.

## 17. Explicit exclusions

No live model/human text, free-form rationale, memory/skill payload, source/test patch, arbitrary code/SQL/shell/tool/path/URL/credential, new action, caregiver-declared authority/cost, budget/permission/evaluator/checkpoint/migration/rollback/execution command, organism network/subprocess, or continuous execution.

## 18. Audit status

The independent Phase 2.0 design audit was followed by one focused read-only re-audit of ADR 0009 at PR #64 head `e4f3527518cbc4e4ff8ab239a90f48bfa47fdbb8`. The focused audit confirmed the contradiction and concluded:

> ADR 0009 is ready after specified documentation or matrix corrections.

ADR 0009 and the synchronized evidence map incorporate those corrections. No further automatic design re-audit is required unless the semantic artifact boundary changes materially again. A separate implementation audit occurs after the accepted protocol is implemented, all matrix evidence exists, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to freeze.
