# Phase 2 Consultation Protocol v1

Status: **Proposed for Issue #59 ordinary review**

This document fixes source-neutral envelopes and canonical-state semantics referenced by proposed ADR 0008. It defines a deterministic fixture protocol, not a live human or model interface.

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

The identifier being derived is excluded from its identity object. Event sequences assigned after derivation are also excluded. Every exclusion is explicit; no implementation may invent additional normalization.

### 3.2 Request identity

`request_id` is derived from exactly:

- request schema and protocol version
- organism identity and current lineage generation
- current-lineage request ordinal
- request lifecycle number
- reason code and requested proposal types
- observation and objective digests
- allowed action and permission identifiers
- policy context and budget configuration versions
- expiry lifecycle

It excludes request ID, request event sequence, wall timestamp, and event-authority metadata.

### 3.3 Dispatch identity

`dispatch_id` is derived from exactly:

- dispatch schema and protocol version
- organism identity and current lineage
- request ID
- dispatch ordinal, exactly `1`
- adapter version
- fixture case identifier
- fixture work class

It excludes dispatch ID, dispatch event sequence, and wall timestamp.

### 3.4 Proposal identity

`proposal_id` is derived from exactly:

- proposal schema and protocol version
- request ID and dispatch ID
- proposal ordinal, exactly `1`
- proposal type
- subject reference
- proposed value
- rationale code
- confidence basis
- expiry lifecycle
- required evaluator identifiers

It excludes proposal ID and response ID. The digest of this identity object is the proposal content digest.

### 3.5 Response identity

`response_id` is derived from exactly:

- response schema and protocol version
- request ID and dispatch ID
- adapter type, version, and instance identity
- response status
- ordered proposal IDs
- ordered proposal content digests
- bounded external provenance

It excludes response ID.

After response ID is derived, it is inserted into final proposal linkage. The complete external package digest is then SHA-256 over canonical JSON containing the final response and ordered proposal envelopes.

For `unavailable`, the proposal array is empty.

### 3.6 Disposition identity

`disposition_id` is derived from exactly:

- disposition schema and protocol version
- organism identity and current lineage
- request, dispatch, response, and proposal identifiers
- disposition and reason code
- considering lifecycle number
- current-state reference
- evaluator versions

It excludes disposition ID, disposition event sequence, and wall timestamp.

### 3.7 Reproducibility requirement

Protected tests construct the complete graph twice from identical declared inputs and require identical identity objects, identifiers, envelopes, content digests, package digest, canonical rows, and event payloads.

They must also prove there is no response/proposal circular dependency.

## 4. Protected budget configurations

### 4.1 `phase2-zero-caregiver-v1`

Every consultation request, dispatch, fixture work, response, proposal, disposition, clarification, payload, human, model, money, and consultation-record limit is zero.

Operational consultation tables remain empty and no consultation event or source is emitted.

### 4.2 `phase2-fixture-v1`

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
| request canonical JSON bytes | 16 KiB |
| response-plus-proposal canonical JSON bytes | 16 KiB |
| external provenance subset bytes | 8 KiB |
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

All administrative writes perform predicted and post-write active-database and working-set accounting and preserve the existing 1 MiB next-wake reserve.

## 5. Request envelope

Schema: `sudachi.consultation.request/v1`

A request is created only by organism runtime inside a schema-v2 garden wake.

Required fields:

- `request_id`
- `request_schema`
- `consultation_protocol_version`
- `organism_id`
- `lineage_generation`
- `request_ordinal`
- `request_event_sequence`
- `request_lifecycle_number`
- `reason_code`, exactly `no_applicable_action`
- sorted unique requested proposal types
- observation and objective references
- sorted unique allowed action and permission identifiers
- policy and budget configuration versions
- exact budget snapshot before creation
- expiry lifecycle, exactly request lifecycle plus two
- `authority_category = organism`
- `authority_source = organism:consultation.request`
- sorted unique existing parent event sequences

Optional declared context is limited to bounded typed codes and identifiers. No free text is accepted.

Request admission requires:

- fixture budget configuration
- no current-lineage outstanding request
- fewer than four current-lineage requests
- resulting garden failure streak below maintenance threshold
- logical and physical limits fit

The garden lifecycle remains a Phase 1 `no_applicable_action` abstention and increments `consecutive_failures` exactly once. Request creation never resets or replaces that accounting.

The request row and event are immutable, commit atomically, and become checkpoint-stable before dispatch admission.

## 6. Dispatch admission

Schema: `sudachi.consultation.dispatch/v1`

Dispatch admission is an administrative operation with a fresh fail-fast `BEGIN IMMEDIATE` transaction.

Required linkage includes:

- deterministic dispatch identity
- exact organism and current lineage
- exact eligible request
- dispatch ordinal `1`
- deterministic fixture adapter identity, version, case, and work class
- administrative event sequence and protected source

Admission requires schema-v2 support, `sleeping`, no pending checkpoint, a stable request checkpoint, current lineage, unexpired request, no prior dispatch, nonterminal request, and all logical and physical budgets fitting.

The same transaction creates one immutable protected cost charge:

- one dispatch attempt
- one charged fixture invocation
- one charged work unit
- zero human, model, money, and declared-latency values
- exact request payload bytes
- response and provenance bytes initially zero

The transaction commits before fixture execution. The charge is never refunded. Repeated admission cannot authorize a second invocation.

## 7. External deterministic fixture

Fixture execution occurs only after dispatch admission commits and outside every SQLite write transaction.

The fixture receives exactly:

- the canonical request envelope
- the protected fixture case identifier

It receives no database handle, path, workspace, repository handle, executor, evaluator, checkpoint, rollback, network, subprocess, or randomness capability.

The output is a noncanonical external package until ingress succeeds.

## 8. External response and proposal package

Response schema: `sudachi.consultation.response/v1`

Required response data includes deterministic response identity, request and dispatch linkage, exact adapter provenance, response status, ordered proposal identifiers and content digests, and bounded external provenance.

Allowed statuses:

- `proposals_returned`
- `unavailable`

`proposals_returned` contains exactly one proposal. `unavailable` contains none.

Proposal schema: `sudachi.consultation.proposal/v1`

Allowed proposal types:

- `action_candidate`
- `abstain`
- `defer`

`action_candidate` may reference only an existing action allowed by the request and schema-valid parameters. It cannot define code, tools, paths, SQL, permissions, budgets, or a new action.

External packages contain no writer-authority fields and no authoritative cost, budget, permission, evaluator, checkpoint, migration, rollback, or execution command.

## 9. Administrative response ingress

Ingress uses a new fresh fail-fast administrative transaction.

Administration independently recomputes identifiers, canonical bytes, content digests, package digest, measured byte counts, and exact request, dispatch, adapter, case, lineage, expiry, and cardinality linkage before mutation.

Successful ingress creates immutable response, proposal when present, ingress receipt, measured-byte cost completion, and one administrative event atomically.

The protected receipt carries:

- `authority_category = administration`
- `authority_source = administration:consultation.response_ingress`
- package digest
- measured bytes
- exact parent event linkage

Ingress cannot adopt, execute, clear maintenance, checkpoint, migrate, roll back, or alter protected budgets or permissions.

Byte-identical duplicate ingress is idempotent. Conflicting duplicate or invalid package fails closed.

A valid package rejected only by busy ownership or pending checkpoint may be explicitly resubmitted with identical bytes. Fixture execution is not repeated and no additional fixture charge is created.

`unavailable` terminalizes the request with no proposal or disposition.

## 10. Dispatch terminalization and reconciliation

Schema: `sudachi.consultation.dispatch_terminal/v1`

Allowed terminal reasons:

- `dispatch_interrupted`
- `fixture_output_invalid`
- `expired_before_ingress`

The normal administrative workflow terminalizes caught fixture or validation failures. A crash after dispatch admission leaves one charged unresolved dispatch. An explicit bounded reconciliation command may record interruption but may never invoke the fixture again.

Response and terminal rows are mutually exclusive. Repeated terminalization is idempotent.

## 11. Explicit disposition wake

Disposition schema: `sudachi.consultation.disposition/v1`

A caller explicitly invokes the disposition work class. It is not hidden inside a garden wake and has no implicit priority.

The wake:

- uses a fresh fail-fast wake transaction
- requires schema-v2, fixture budget configuration, `sleeping`, and no pending checkpoint
- claims no garden input
- selects the oldest queued current-lineage proposal by ingress event sequence and then proposal ID
- considers at most one proposal
- independently validates current state, versions, linkage, permissions, budgets, and expiry
- records exactly one final disposition and one ordinary checkpoint boundary
- increments lifecycle while preserving Phase 1 garden `consecutive_failures`

Final dispositions:

- `accepted`
- `rejected`
- `deferred`
- `clarification_requested`

The first implementation records disposition only. No disposition enters the existing action selector or changes garden state.

Clarification is final because clarification rounds are zero.

## 12. Lineage, expiry, and derived state

Consultation budget epoch is current `lineage_generation`.

Only current-lineage rows can be active or budget-counting. Old-lineage rows remain immutable historical evidence.

Rollback starts a fresh bounded epoch. ADR 0007 permits at most one completed rollback, bounding one physical organism to at most two consultation epochs and eight charged fixture invocations.

A request created in lifecycle `N` is eligible through `N+2`. Wall time never determines canonical eligibility.

Current-lineage state is derived from immutable rows:

- pre-dispatch expired request is terminal for admission and no longer outstanding
- admitted dispatch remains outstanding until response or terminal outcome
- unavailable response is terminal
- successful response remains outstanding until disposition
- terminal dispatch and disposition are final

No caregiver-writable mutable status flag exists.

## 13. Maintenance, checkpoint, and rollback interactions

- request creation does not block later garden wakes
- dispatch requires sleeping and stable request checkpoint
- ingress and terminalization may record already-admitted evidence while sleeping or maintenance-required, but never behind a pending checkpoint, rollback, or quarantine
- ingress and terminalization cannot clear maintenance
- disposition requires sleeping and cannot bypass maintenance
- garden and disposition wakes checkpoint
- dispatch, ingress, and terminalization do not checkpoint
- rollback increments lineage and makes prior-lineage consultation rows inactive
- abandoned-lineage packages and proposals fail before mutation
- ADR 0007 rollback limit and evidence retention remain unchanged

## 14. Canonical state concepts

Implementation SQL is deferred to the implementation Issue, but schema-v2 must normalize immutable concepts for:

- requests
- dispatch admissions
- protected cost charges and measured-byte completions
- responses
- proposals
- ingress receipts
- dispositions
- dispatch terminal outcomes

All identities, versions, digests, links, cardinalities, no-update, and no-delete protections are exact.

No new column is added to an original Phase 1 table. Extension uses new protected objects.

## 15. Zero-caregiver projection

For schema-v2 zero-caregiver configuration:

1. normalize only existing schema and budget configuration values
2. compare every original Phase 1 row, column, event payload, and original-table sequence exactly
3. require operational consultation tables and sequences empty
4. require no consultation event, source, dispatch, import, cost, or effect
5. compare status, behavior, checkpoints, rollback, and authority

Extra empty schema objects make SQLite bytes and checkpoint digests differ. No other semantic normalization is allowed.

## 16. Deterministic fixture cases

The implementation provides declared fixture cases for:

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

Case selection is a declared input, never randomness or network behavior.

## 17. Explicit exclusions

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

## 18. Review and audit cadence

Protocol v1 is accepted through ordinary repository review with ADR 0008 and the Phase 2 test matrix.

There is no separate Codex design audit. One independent read-only Codex audit is run only after the complete Phase 2 implementation and protected matrix are finished and the exact candidate baseline is ready to be judged for freezing.