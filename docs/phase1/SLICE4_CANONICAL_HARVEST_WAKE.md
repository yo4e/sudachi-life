# Phase 1 Slice 4: Canonical Harvest Wake

Status: **implemented and verified in PR #18**

Tracked by: Issue #13

## Scope

This slice extends the existing fixed seed-garden lifecycle by exactly one registered mutating action. After the stable water checkpoint, a second uniquely identified `synthetic:garden_tick` causes SUDACHI-0 to:

1. acquire fail-fast SQLite write ownership
2. claim the oldest eligible tick
3. build one complete deterministic observation
4. find no executable water target
5. select `harvest_plot(bed-b)` through the protected policy
6. charge one action attempt and reserve one successful mutation
7. execute the harvest inside a SQLite savepoint
8. independently re-read and evaluate canonical state
9. consume the tick and append bounded lifecycle records
10. commit an exact checkpoint-pending boundary
11. publish and register the lifecycle checkpoint
12. return to `sleeping` and terminate

## Exact transition

Starting from the stable first-water checkpoint, the second wake changes only:

- `bed-b.fruit`: `1 -> 0`
- `inventory.harvested_fruit`: `0 -> 1`
- `environment_state.environment_step`: `1 -> 2`
- `environment_state.objective_complete`: `false -> true`
- `organism.lifecycle_number`: `1 -> 2`

`bed-a` remains watered, water inventory remains zero, and no protected configuration changes.

## Independent evaluation

The evaluator does not accept the executor's success claim. It re-reads every plot, inventory value, environment step, and objective condition. It proves that:

- only the selected mature plot lost exactly one fruit
- water inventory did not change
- harvested inventory gained exactly one fruit
- the environment advanced exactly one step
- unresolved needs changed from one to zero
- the protected objective is now complete

## Budget and event boundaries

The second wake consumes the same protected vector as the first mutating wake:

- one input event
- one observation
- one action attempt
- one successful environment mutation
- zero caregiver, network, subprocess, and external mutable-write capability
- twelve semantic lifecycle steps
- nine organism lifecycle records

The second input receipt is event sequence 15. The second wake commits its pending checkpoint at sequence 24. Administrative checkpoint stabilization is sequence 25 and points back to boundary 24.

## Protected completion boundary

Slice 4 deliberately does not implement objective-complete abstention. A third tick at completed state is rejected inside the outer wake transaction. The attempted claim and provisional lifecycle records roll back, leaving the third tick unclaimed and canonical lifecycle 2 unchanged.

This prevents an unimplemented policy branch from inventing another mutation.

## Verification

PR #18 passed GitHub Actions on Python 3.12 with **28 protected tests**, including:

- the exact second harvest transition
- independent objective-completion evaluation
- complete nonnegative budget accounting
- both consumed input identities and lifecycle numbers
- stable lifecycle checkpoint 2 at event boundary 24
- real CLI execution of initialization, water, harvest, and status
- rollback of a third attempted mutation before abstention exists

## Deliberate limits

Slice 4 does not implement:

- objective-complete abstention
- no-applicable-action or budget-exhaustion abstention
- classified failure streaks or maintenance transitions
- checkpoint repair or retention pruning
- rollback lineage
- deterministic JSONL export
- any caregiver, learning, memory, or skill system

The exact next slice is Slice 5: commit the third canonical tick as the justified `objective_already_complete` abstention, with zero action attempts and zero environment mutations, then checkpoint and sleep.
