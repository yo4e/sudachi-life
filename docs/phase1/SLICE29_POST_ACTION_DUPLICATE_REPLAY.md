# Slice 29: Post-Action Duplicate Input Replay

## Purpose

Close Minimal Organism Contract v0.2 evaluation 16: replaying an external tick identifier must never produce a duplicate action.

The protected scenario covers replay after the original input has already been claimed, consumed, acted on, checkpointed, and returned to stable sleep.

## Scenario

`tests/test_post_action_duplicate_replay.py` performs the following sequence:

1. enqueue `consumed-replay-tick`
2. complete and stabilize the canonical first water action
3. capture the complete stable active and artifact state
4. enqueue `consumed-replay-tick` again with an empty fake clock
5. attempt a normal wake without adding any distinct input
6. enqueue `distinct-followup-tick`
7. complete and stabilize the canonical harvest action

## Exact replay boundary

Before replay, the test captures:

- active SQLite SHA-256
- protected status and organism row
- environment, garden, and inventory rows
- complete inbox rows
- complete canonical event history
- checkpoint registry
- SQLite sequence state
- every retained checkpoint file name, size, and SHA-256

The duplicate enqueue must:

- return `inserted=False`
- return the original inbox identifier
- return the original received wall time
- consume zero clock readings
- add no inbox row
- append no `input_enqueued` event
- change no canonical row or SQLite sequence
- change no active database byte
- change no checkpoint artifact

The original inbox row remains claimed by lifecycle 1 and consumed.

## No duplicate lifecycle or action

A normal wake attempted immediately after replay has no claimable input.

The test requires:

- one declared start-clock reading
- typed `NoInputEventError`
- rollback of the uncommitted `wake_accepted` event
- exact equality with the complete pre-replay stable snapshot
- exactly one committed `action_completed` event

Therefore the replay cannot create a second lifecycle, observation, decision, action attempt, mutation, checkpoint boundary, or artifact.

## Independent later progress

A later distinct identifier remains independently accepted.

The second complete wake:

- claims only `distinct-followup-tick`
- harvests `bed-b`
- completes the objective
- advances to lifecycle 2 and environment step 2
- produces exactly the second committed action
- leaves the original replayed identifier represented by one inbox row and one action only

## Result

The existing implementation passed unchanged.

`enqueue_garden_tick(...)` checks the unique external identifier before reading the injected clock and returns the existing canonical row. `claim_oldest_garden_tick(...)` selects only unconsumed and unclaimed rows. Failure to find one raises inside the outer transaction, so the tentative wake history is rolled back.

No production source, schema, contract, action, evaluator, clock boundary, budget, checkpoint, or rollback behavior changed.

## Validation

GitHub Actions run 269 on Python 3.12 passed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **124 protected tests in 10.15 seconds**

## Boundary preserved

Slice 29 adds no generic replay machinery, retry loop, deduplication cache, or alternate input authority. SQLite remains the only canonical inbox and event source.
