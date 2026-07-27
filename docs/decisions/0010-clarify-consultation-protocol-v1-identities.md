# ADR 0010: Clarify Consultation Protocol v1 exact identities

- Status: Accepted
- Date: 2026-07-27
- Decision owner: project owner
- Implementation issue: #61
- Clarification issues: #88, #89, #92, #93

## Context

ADRs 0008 and 0009, Consultation Protocol v1, and the Phase 2 matrix intentionally require exact schemas and digest preimages. Slice 38 implementation exposed four places where the accepted text did not define one implementable exact object:

1. the dispatch identity exact list omitted `configuration_version` while another normative clause required it;
2. external provenance had a byte limit but no exact schema;
3. the versioned current-state projection required before disposition was not enumerated;
4. optional request context was permitted but not defined, so a maximum request envelope could not be constructed honestly.

The project owner explicitly adopted the recommended clarifications. This ADR is normative. Where it conflicts with Consultation Protocol v1 or the Phase 2 matrix, this ADR supersedes only the clauses and rows named below. All other accepted boundaries remain unchanged.

## Decision

### 1. Dispatch identity includes consultation configuration

`dispatch_identity` contains exactly these fields:

```json
{
  "adapter_version": "deterministic-fixture-v1",
  "configuration_version": "phase2-fixture-v1",
  "dispatch_ordinal": 1,
  "dispatch_schema": "sudachi.consultation.dispatch/v1",
  "fixture_case_id": "<declared case identifier>",
  "lineage_generation": 0,
  "organism_id": "<organism identifier>",
  "protocol_version": 1,
  "request_id": "consultation-request:<sha256>",
  "work_class": "fixture-constant-v1"
}
```

The values shown as placeholders are validated against the linked current-lineage request and the protected declared fixture case. The exact digest remains:

```text
dispatch_id = "consultation-dispatch:" + H("dispatch-id", dispatch_identity)
```

It excludes dispatch ID, later event sequence, wall time, cost, authority metadata, and fixture output.

The final dispatch envelope contains exactly the identity fields plus:

- `dispatch_id`
- `event_sequence`
- `authority`, exactly `{"source":"administration:consultation.dispatch","writer_category":"administration"}`

The first deterministic fixture accepts these declared case identifiers:

- `valid-action-candidate`
- `valid-abstain`
- `valid-defer`
- `unavailable`
- `stale-observation`
- `expiry-before-ingress`
- `expiry-after-ingress`
- `unknown-action`
- `invalid-parameters`
- `contradictory-state`
- `identical-duplicate`
- `conflicting-duplicate`
- `malformed-response`
- `unknown-schema`
- `over-budget`
- `fixture-exception`
- `crash-after-admission`
- `abandoned-lineage-package`

No undeclared case is admitted.

### 2. External provenance is one closed three-field object

Protocol v1 external provenance contains exactly:

```json
{
  "fixture_case_id": "<linked dispatch case identifier>",
  "provenance_schema": "sudachi.consultation.provenance/v1",
  "source_type": "deterministic-fixture"
}
```

All three fields are required. Empty provenance is forbidden. `fixture_case_id` must equal the linked dispatch case and be one of the protected declared cases above.

Provenance contains no authority, writer category, cost, budget, permission, evaluator command, action command, checkpoint, migration, rollback, schedule, code, SQL, shell, path, URL, credential, tool, free text, human identity, model identity, or opaque payload.

The response identity contains exactly:

- `response_schema`
- `protocol_version`
- `request_id`
- `dispatch_id`
- `adapter_type`, exactly `deterministic-fixture`
- `adapter_version`, exactly `deterministic-fixture-v1`
- `adapter_instance_id`, exactly `deterministic-fixture-instance-v1`
- `status`
- ordered `proposal_ids`
- ordered `proposal_content_digests`
- `external_provenance`

The final response envelope contains exactly those fields plus `response_id`.

Cardinality is exact:

- `proposals_returned`: one proposal ID and one matching content digest;
- `unavailable`: both arrays empty.

After the derived response ID is inserted into the final proposal linkage, the external package preimage remains exactly `{"response":...,"proposals":[...]}`. It contains one proposal for `proposals_returned` and none for `unavailable`.

### 3. Current-state reference is a versioned closed projection

`current_state_identity` is measured inside the fresh disposition wake transaction after canonical validation and before any disposition mutation. It contains exactly:

- `current_state_schema`, exactly `sudachi.consultation.current_state/v1`
- `protocol_version`, exactly `1`
- `configuration_version`, exactly the protected active configuration
- `budget_config_version`, exactly `phase1-v1`
- `organism_id`
- `lineage_generation`
- `considering_lifecycle_number`, exactly the lifecycle being entered by the disposition wake
- `organism_status`, exactly `sleeping` at admission
- `consecutive_failures`
- `latest_stable_checkpoint_id`, required and non-null
- `latest_stable_event_sequence`
- `garden_observation`
- `request_reference`
- `proposal_reference`

`garden_observation` is exactly the repository `GardenObservation.as_dict()` result built from the current canonical `environment_state`, `inventory`, `garden_plot`, and protected `action_definition` rows in their existing deterministic order.

`request_reference` contains exactly:

```json
{
  "expiry_lifecycle_number": 0,
  "permission_ids": [],
  "request_id": "consultation-request:<sha256>"
}
```

The values must equal the linked immutable request. `permission_ids` preserves the request's sorted unique declared order.

`proposal_reference` contains exactly:

```json
{
  "content_digest": "<sha256>",
  "proposal_id": "consultation-proposal:<sha256>",
  "proposal_type": "<accepted proposal type>",
  "required_evaluator_ids": []
}
```

The values must equal the linked immutable proposal. Evaluator IDs preserve the protected type-specific order.

The digest remains:

```text
current_state_digest = H("current-state-reference", current_state_identity)
```

It excludes wall time, the later disposition event sequence, presentation paths, and any caregiver assertion about current state.

`disposition_identity` contains exactly:

- `disposition_schema`
- `protocol_version`
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
- `evaluator_versions`, exactly the proposal's protected ordered `required_evaluator_ids`

It excludes disposition ID, later event sequence, and wall time.

### 4. Protocol v1 has no optional request context

Protocol v1 defines no `context` field or other optional request field. The closed request envelope already implemented and validated by Slice 38a is the complete legal protocol-v1 request envelope. Any extra context, padding, free text, repeated identifier collection, or opaque field rejects.

For protocol v1:

- request parent events contain at most the 16 Phase 1 core records from the current lifecycle;
- request arrays retain their already-declared fixed protected cardinalities and order;
- integer magnitude is not an envelope-padding mechanism;
- P2-E10 means the largest **structural** request produced by a protected fixture: maximum-length legal organism identifier, request ordinal four, all declared action/permission/proposal-type entries, and the full 16-parent current-lifecycle set;
- the real successful request and its ordinary checkpoint must preserve all inherited physical limits and the 1 MiB next-wake reserve.

The 16 KiB request limit remains a hard ceiling, not a target that authorizes filler data.

## Superseded text

This ADR supersedes only:

- Consultation Protocol v1 section 3.2's dispatch identity list;
- section 3.4's previously opaque external provenance;
- section 3.5's deferred current-state projection;
- section 5's optional-context sentence;
- Phase 2 matrix rows P2-D11, P2-E10, P2-H04, P2-H07–P2-H10, P2-I01, and P2-J03 to the extent specified by the synchronized amendment.

## Consequences

- Dispatch, response/package, ingress, and disposition work may proceed without private schema choices.
- Caregiver/adapter data remains untrusted provenance and obtains no canonical authority.
- Request identity remains unchanged; no migration or schema-v2 table alteration is required.
- The existing 152-test Phase 1 baseline and all frozen Phase 1 semantics remain unchanged.
- Any future additional request context, provenance field, adapter, fixture case, or current-state field requires a later reviewed protocol version or ADR.
