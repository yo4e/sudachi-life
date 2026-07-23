# Phase 1 Slice 24: Backward Wall-Time Event Ordering

Status: **implemented and verified in PR #39**

Tracked by: Issue #13

## Scope

This slice closes Minimal Organism Contract v0.2 evaluation 3 with one complete canonical first-wake scenario in which wall time repeatedly moves backward while monotonic time continues forward.

The slice adds protected coverage only. No production code, schema, clock semantics, event format, action, evaluator, budget, checkpoint, or rollback behavior changes.

## Protected scenario

`tests/test_backward_wall_time_ordering.py` starts from the ordinary initialized organism and then:

1. enqueues one `synthetic:garden_tick` with a wall timestamp earlier than genesis
2. supplies five wake and checkpoint clock readings whose wall timestamps continue decreasing
3. supplies increasing monotonic readings so lifecycle and checkpoint deadlines remain valid
4. performs the complete canonical first-water wake
5. stabilizes the exact lifecycle checkpoint and returns the organism to sleep

The scenario proves that the fixed policy still waters `bed-a`, evaluation reports positive success, lifecycle 1 completes, environment step becomes 1, pending boundary 13 stabilizes, and the final canonical event count is 14.

## Canonical order proof

The protected test reads canonical history in `event_sequence` order and requires the exact sequence 1 through 14:

1. `organism_initialized`
2. genesis `checkpoint_pending`
3. genesis `checkpoint_stabilized`
4. `input_enqueued`
5. `wake_accepted`
6. `input_claimed`
7. `observation_created`
8. `action_proposed`
9. `action_completed`
10. `evaluation_completed`
11. `lifecycle_completed`
12. `budget_ledger`
13. lifecycle `checkpoint_pending`
14. lifecycle `checkpoint_stabilized`

The wall timestamps decrease across genesis, enqueue, wake, budget completion, and checkpoint stabilization. Event identity and order nevertheless remain the database sequence, never timestamp order.

## Clock boundary

The test preserves the existing declared clock contract:

- wall time may repeat or move backward
- monotonic readings determine elapsed deadlines
- the wake consumes exactly five declared readings
- no timestamp becomes an implicit identifier, seed, or ordering key

## Verification

GitHub Actions run 225 on Python 3.12 completed:

- clean editable installation
- source and test compilation
- **118 protected tests passed in 8.37 seconds**
- genesis CLI smoke test

No implementation correction was required.

## Deliberately out of scope

- seed-independence comparison
- full repeated-run canonical equivalence
- cleanup-grace behavior
- altered insertion-order tie breaking
- duplicate-input replay after action
- process-crash execution
- nested-wake rejection
- schema, contract, environment, budget, or action changes
- caregiver, learning, memory, skills, or later-phase machinery

## Exact next action

After PR #39 is merged, reconstruct current `main`, inspect open issues and pull requests, and select the next incomplete fixed Phase 1 evaluation as Slice 25. The earliest remaining explicit comparison is evaluation 4, seed independence, but repository truth must be checked before creating the branch.
