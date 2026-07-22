# Phase 1 Slice 7: Resource-Aware Harvest Recovery

Status: **implemented and verified in PR #21**

Tracked by: Issue #13

## Scope

This slice protects a recovery capability already present in the fixed Phase 1 policy without changing the canonical three-wake garden run. An explicit administrative test fixture creates a stable state in which:

- the objective is incomplete
- `bed-a` is a dry living sprout
- no water is available
- `bed-b` is mature with one harvestable fruit
- harvested inventory is empty
- `consecutive_failures = 1`

One uniquely identified garden tick then causes SUDACHI-0 to:

1. acquire fail-fast SQLite write ownership
2. claim one oldest eligible tick
3. build one complete deterministic observation
4. prove that watering is not executable because water inventory is zero
5. select `harvest_plot(bed-b)` as the next executable protected action
6. reserve one action attempt and one environment mutation before change
7. execute the exact harvest transition inside a savepoint
8. independently verify positive progress
9. reset `consecutive_failures` from one to zero
10. commit an exact checkpoint-pending boundary
11. publish and register a verified lifecycle checkpoint
12. return to sleep

The fixture is explicit test administration. It is not caregiver input and does not participate in policy selection.

## Protected decision and evaluation

The observation exposes:

- `water_units = 0`
- `water_plot.applicable_targets = []`
- `harvest_plot.applicable_targets = ["bed-b"]`

The fixed policy therefore skips impossible watering and selects the first executable harvest target. It does not interpret one unavailable resource as evidence that every action is unavailable.

The independent evaluator proves:

- `bed-a` remains dry and unchanged
- `bed-b.fruit` changes from one to zero
- harvested inventory changes from zero to one
- water inventory remains zero
- environment step changes from zero to one
- the objective remains incomplete because the dry sprout is unresolved
- unresolved needs decrease from two to one
- progress is positive

A successful action resets the prior failure streak from one to zero. The lifecycle records this change explicitly as `failure_streak_updated` with reason `successful_action`.

## Budget and event accounting

The wake consumes:

- one input event
- one observation
- one action attempt
- one environment mutation
- zero caregiver consultations
- zero network calls
- zero subprocess calls
- zero authoritative external writes

Exact protected sequence:

- event 4: protected recovery fixture prepared
- event 5: fixture checkpoint pending boundary
- event 6: fixture checkpoint stabilized
- event 7: recovery tick received
- event 8: wake accepted
- event 9: input claimed
- event 10: observation created
- event 11: action proposed
- event 12: action completed
- event 13: evaluation completed
- event 14: failure streak updated from one to zero
- event 15: lifecycle completed
- event 16: budget ledger
- event 17: lifecycle checkpoint pending boundary
- event 18: lifecycle checkpoint stabilized

The final organism remains `sleeping` at lifecycle 1 with environment step 1, objective incomplete, harvested fruit 1, and failure streak 0.

## Protected test

`tests/test_resource_aware_recovery.py::test_resource_aware_harvest_recovers_and_resets_failure_streak` proves:

- the complete resource-aware wake
- exact action selection and budget use
- exact harvest transition and positive progress
- failure-streak reset
- exact event ordering
- stable checkpoint manifest validation
- preservation of the dry unresolved need and incomplete objective

GitHub Actions on Python 3.12 completed clean installation, compileall, genesis CLI smoke, and **31 protected tests**.

## Deliberately not implemented

- injected action failure
- classified savepoint recovery after partial mutation
- budget-exhaustion classification
- maintenance-threshold entry
- checkpoint repair or retention pruning
- rollback lineage
- deterministic JSONL export
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

Slice 8 will introduce one protected injected action failure after mutation begins inside a savepoint. It must prove that partial environment changes disappear, the action attempt remains charged in the committed classified outcome, no false success is recorded, the failure streak increments exactly once below the maintenance threshold, a checkpoint stabilizes the result, and the organism returns to sleep.
