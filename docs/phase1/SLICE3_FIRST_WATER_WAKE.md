# Phase 1 Slice 3: First Canonical Water Wake

Status: **implemented and verified in PR #17**

Tracked by: Issue #13

## Scope

This slice completes exactly one normal SUDACHI-0 lifecycle for the protected seed garden:

1. accept one previously enqueued `synthetic:garden_tick`
2. acquire fail-fast SQLite write ownership
3. claim the oldest eligible tick
4. build one deterministic complete observation
5. select `water_plot(bed-a)` through the fixed protected policy
6. load and consume the protected per-wake budget vector
7. execute the transition inside a SQLite savepoint
8. independently evaluate canonical state
9. consume the claimed tick
10. append bounded lifecycle and budget records
11. commit an exact checkpoint-pending boundary
12. create, validate, publish, and register an immutable checkpoint
13. return to sleeping state and terminate

## Exact transition

The successful wake changes only:

- `bed-a.moisture`: `0 -> 1`
- `inventory.water_units`: `1 -> 0`
- `environment_state.environment_step`: `0 -> 1`
- `organism.lifecycle_number`: `0 -> 1`

`bed-b` remains mature, moist, and contains one fruit. The protected objective therefore remains incomplete.

## Budget accounting

The accepted wake consumes:

- one input event
- one observation
- one action attempt
- one successful environment mutation
- twelve semantic lifecycle steps
- nine organism lifecycle records, including the budget ledger and terminal pending record

It consumes zero caregiver consultations, network calls, subprocess calls, and authoritative external mutable writes.

Action-attempt cost is charged before execution. Successful mutation capacity is reserved after precondition validation and before state change. Recoverable action execution uses a savepoint.

## Canonical event boundary

After genesis and input enqueueing, the first wake appends:

1. `wake_accepted`
2. `input_claimed`
3. `observation_created`
4. `action_proposed`
5. `action_completed`
6. `evaluation_completed`
7. `lifecycle_completed`
8. `budget_ledger`
9. `checkpoint_pending`

The exact pending boundary is event sequence 13. Checkpoint stabilization is an administrative record at sequence 14 and points back to boundary 13.

## Checkpoint failure

The lifecycle transaction commits before checkpoint publication. If checkpoint validation or its monotonic deadline fails, the organism remains in canonical `checkpoint_pending` state. The previously stable genesis checkpoint remains registered, and no later wake may proceed until repair or stabilization is implemented.

## Protected verification

PR #17 passed GitHub Actions on Python 3.12 with 25 protected tests. The new tests prove:

- exact first-water state and event results
- complete nonnegative budget accounting with hard-zero capabilities
- input consumption and lifecycle numbering
- immutable lifecycle checkpoint contents and lineage boundary
- committed pending state when checkpoint stabilization exceeds its deadline

The existing suite continues to prove initialization, append-only events, deterministic clocks, idempotent input, fail-fast locking, claim rollback, and sorted observations.

## Deliberate limits

Slice 3 does not implement:

- harvest
- objective-complete abstention
- failure streak or maintenance transitions
- checkpoint repair or retention pruning
- rollback
- JSONL export
- any caregiver, learning, memory, or skill system

The exact next slice is the second canonical wake: `harvest_plot(bed-b)` followed by independent objective-completion evaluation and a stable checkpoint.
