# ADR 0013: Fix exact disposition-wake evidence and reason mapping

- Status: Accepted
- Date: 2026-07-27
- Decision owner: project owner
- Implementation issue: #61
- Clarification issue: #105

## Context

ADR 0010 fixes the exact current-state identity, current-state digest, disposition identity, and disposition ID preimage. ADR 0008 and Consultation Protocol v1 require a separate caller-selected organism disposition wake that considers at most one current-lineage proposal, independently evaluates current canonical state, records one final disposition, increments lifecycle while preserving the garden failure streak, commits a pending checkpoint, and publishes the ordinary checkpoint.

The accepted design did not enumerate every immutable value needed for canonical disposition state: the final envelope, complete disposition/reason mapping, event and outcome payloads, direct parents, fixed budget ledger, checkpoint ordering, and idempotence after transaction or checkpoint interruption.

The project owner explicitly adopted Issue #105's recommended clarification. This ADR is normative. It supersedes only the disposition clauses and matrix rows named below. Every other accepted Phase 1 and Phase 2 boundary remains unchanged.

## Decision

### 1. Current-state and disposition identities remain ADR 0010

```text
current_state_digest = H("current-state-reference", current_state_identity)
disposition_id = "consultation-disposition:" + H("disposition-id", disposition_identity)
```

`current_state_identity` and `disposition_identity` remain exactly the closed ADR 0010 objects. `disposition_schema` is exactly `sudachi.consultation.disposition/v1`.

### 2. Final disposition envelope

The final envelope contains exactly the ADR 0010 disposition-identity fields plus:

- `authority`;
- `current_state_reference`;
- `disposition_id`;
- `event_sequence`;
- `parent_event_sequences`.

Authority is exactly:

```json
{
  "source": "organism:consultation.disposition",
  "writer_category": "organism"
}
```

`current_state_reference` is the complete exact ADR 0010 `current_state_identity`, constructed from current canonical rows inside the disposition wake transaction. It is never copied from fixture output. Its independently recomputed digest must equal `current_state_digest` in the disposition identity.

`parent_event_sequences` contains exactly three sorted unique existing current-lineage event sequences:

1. the selected proposal's ingress event sequence;
2. the current latest-stable checkpoint boundary event sequence;
3. the disposition wake's preceding `wake_accepted` event sequence.

All three precede the disposition event. Request, dispatch, response, and proposal ancestry remains reconstructable through immutable row links.

### 3. Closed disposition and reason mapping

After exact schema, identity, linkage, lineage, configuration, physical-budget, evaluator-set, and permission validation, the first implementation applies this complete mapping in precedence order:

1. proposal considered at a lifecycle greater than linked request expiry:
   - disposition `rejected`;
   - reason `expired`.
2. `action_candidate` whose protected action-schema, permission, and current-state evaluators all pass:
   - disposition `accepted`;
   - reason `required_evaluators_passed`.
3. structurally valid and permitted `action_candidate` that is not applicable to current canonical state:
   - disposition `rejected`;
   - reason `action_not_applicable_current_state`.
4. `abstain` when current canonical state confirms no request-allowed supported action is applicable:
   - disposition `accepted`;
   - reason `no_supported_action_confirmed`.
5. `abstain` when current canonical state has at least one request-allowed supported action:
   - disposition `clarification_requested`;
   - reason `proposal_contradicts_current_state`.
6. unexpired `defer`:
   - disposition `deferred`;
   - reason `await_state_change`.

No other disposition/reason combination is valid.

Schema, ID, digest, linkage, lineage, permission, evaluator-set, unknown-action, and parameter corruption fail before disposition mutation. They do not create a rejected disposition.

Clarification is final because the protected clarification-round limit is zero. It creates no request, dispatch, fixture call, retry, question, or follow-up.

### 4. Exact disposition event and outcome

The disposition event is:

- event type `consultation_disposition_created`;
- source `organism:consultation.disposition`;
- lifecycle equal to the considering lifecycle;
- event sequence shared by the event row, disposition row, and final envelope.

Its payload contains exactly `disposition` and `outcome`.

`disposition` is the exact final disposition envelope.

`outcome` contains exactly:

```json
{
  "disposition": "accepted | rejected | deferred | clarification_requested",
  "disposition_id": "consultation-disposition:<digest>",
  "input_consumed": false,
  "proposal_id": "consultation-proposal:<digest>",
  "reason_code": "<exact protected reason>"
}
```

There is no separate outcome table and no caregiver-authored evaluation result. Protected evaluator versions remain inside the disposition identity.

### 5. Exact disposition-wake event order

One successful disposition transaction writes exactly four organism events, in this order:

1. `wake_accepted`
   - source `organism:consultation.disposition`;
   - payload exactly `{"work_class":"consultation_disposition"}`.
2. `consultation_disposition_created`
   - payload exactly `{"disposition":<final envelope>,"outcome":<exact outcome>}`.
3. `consultation_disposition_budget_ledger`
   - payload exactly the fixed ledger below.
4. `checkpoint_pending`
   - source `organism:consultation.disposition`;
   - payload exactly:

```json
{
  "final_status": "sleeping",
  "lifecycle_number": 1,
  "reason": "committed_disposition_wake"
}
```

The `lifecycle_number` value shown as `1` is the typed example. Canonically it equals the considering lifecycle number, which is prior committed lifecycle plus one.

No garden `input_claimed`, `observation_created`, selector, action, evaluation, failure-streak update, or garden `lifecycle_completed` event is created.

### 6. Exact disposition budget ledger

The ledger payload contains exactly:

```json
{
  "canonical_records_limit": 12,
  "canonical_records_used": 4,
  "configuration_version": "phase2-fixture-v1",
  "phase1_budget_config_version": "phase1-v1",
  "semantic_steps_limit": 10,
  "semantic_steps_used": 8
}
```

The event row's inherited `budget_config_version` remains exactly `phase1-v1`. The payload binds the separate protected consultation configuration without changing the Phase 1 budget singleton.

All four dispositions use the same fixed record and semantic-step counts. No Phase 1 input, action, environment, caregiver, network, subprocess, or external-write counter is consumed.

### 7. Lifecycle and checkpoint ordering

- The fresh fail-fast transaction starts from schema-v2 fixture configuration, `sleeping`, no pending checkpoint, and no maintenance reason.
- `considering_lifecycle_number` and `disposition_lifecycle_number` equal prior committed lifecycle plus one.
- The selected proposal is the oldest eligible current-lineage proposal by ingress event sequence, then proposal ID.
- At most one proposal is considered.
- The garden failure streak is copied unchanged.
- No inbox row is claimed or consumed.
- The disposition row, four events, organism lifecycle/status update, and pending-checkpoint boundary commit atomically.
- Organism status becomes `checkpoint_pending`, with the fourth event as the pending boundary.
- After commit and lock release, the existing lifecycle checkpoint creator publishes and registers the ordinary checkpoint.
- Successful stabilization returns the organism to `sleeping`.
- Publication or registration interruption leaves the same explicit repairable pending-checkpoint state used by a garden wake. Existing administrative checkpoint repair stabilizes it without repeating the disposition.
- Disposition creates no maintenance transition and cannot run from maintenance.

### 8. Idempotence and conflicts

- A proposal with an existing disposition is final and is not selected again.
- Repeating the caller-selected disposition wake after successful disposition selects the next eligible proposal or reports no eligible proposal. It does not replay an existing disposition.
- Competing, nested, and process-overlap wake attempts fail fast and queue no hidden work.
- A crash before transaction commit leaves no disposition and restores selection eligibility.
- A crash after transaction commit but before checkpoint stabilization leaves one disposition and one pending checkpoint. Explicit checkpoint repair stabilizes it without another disposition.

### 9. Non-authorized effects

No disposition path may:

- claim garden input;
- invoke the fixture, caregiver, model, API, network, or subprocess;
- execute or enqueue an action;
- change garden, environment, or inventory state;
- reset or increment the garden failure streak;
- create a request, dispatch, response, proposal, memory, or skill;
- clear maintenance;
- migrate or roll back;
- retry consultation;
- expand authority, budgets, permissions, evaluator sets, or proposal semantics.

## Superseded text

This ADR supersedes only:

- Consultation Protocol v1 sections 3.5 and 11 to the extent needed to close the final disposition envelope, mapping, event/outcome, budget ledger, and checkpoint ordering;
- ADR 0008 section 3.E only to the extent of these exact immutable values;
- Phase 2 matrix rows P2-H10, P2-L01–P2-L14, and applicable P2-M/P2-N/P2-O rows to the extent specified by the synchronized amendment.

## Consequences

- Slice 41 may implement disposition without private canonical names or reason semantics.
- Current canonical state, not caregiver or fixture assertion, controls disposition.
- Accepted proposals still execute no action and create no memory or skill.
- Disposition uses the existing checkpoint publication and repair machinery without modifying frozen Phase 1 garden semantics.
- The original 152 Phase 1 tests remain unchanged and passing.
- Any new disposition, reason, evaluator, event, parent, outcome field, budget count, action effect, or clarification round requires a later reviewed protocol version or ADR.