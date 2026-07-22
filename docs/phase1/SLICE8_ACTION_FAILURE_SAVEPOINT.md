# Phase 1 Slice 8: Classified Action Failure and Savepoint Cost Preservation

Status: **implemented and verified in PR #22**

Tracked by: Issue #13

## Scope

This slice adds one protected, test-administered action failure without changing the canonical three-wake garden run. The fixture has an incomplete objective, exactly one executable registered action (`water_plot(bed-a)`), water inventory one, no harvestable fruit, and failure streak zero.

The injection is available only as the explicit `protected_test_failure_after_plot_write` keyword to the Python lifecycle entry point. It is absent from the CLI, inbox, policy observation, canonical organism state, and action definitions.

## Classified execution

The wake charges one action attempt, reserves one environment mutation, opens the existing `garden_action` SQLite savepoint, writes `bed-a.moisture = 1`, and then raises typed `InjectedActionFailure` at the protected `after_plot_write` point.

The executor then:

1. rolls back to the savepoint
2. releases the savepoint
3. returns the successful environment-mutation budget reservation to zero
4. preserves the charged action-attempt count at one
5. re-raises only the typed injected failure for lifecycle classification

Unrelated validation, schema, budget, or runtime exceptions are not converted into this classified outcome and still roll back the whole wake.

## Independent evaluation

The lifecycle records `action_failed` rather than `action_completed`. The independent evaluator then proves:

- the failed action matched the protected executable proposal
- every plot is byte-for-byte equivalent to the prior observation
- water and harvested inventory are unchanged
- environment step and objective state are unchanged
- unresolved needs remain two
- evaluation success is false with progress `action_failed_rolled_back`

## Accounting and boundary

The wake consumes one input, one observation, one action attempt, zero successful environment mutations, and zero caregiver, network, subprocess, or authoritative external-write capability.

Exact sequence:

- event 4: protected fixture prepared
- event 5: fixture checkpoint pending
- event 6: fixture checkpoint stabilized
- event 7: classified-failure tick received
- events 8–10: wake accepted, input claimed, observation created
- event 11: action proposed
- event 12: action failed
- event 13: evaluation completed
- event 14: failure streak updated from zero to one
- event 15: lifecycle completed as `action_failure`
- event 16: budget ledger
- event 17: lifecycle checkpoint pending
- event 18: lifecycle checkpoint stabilized

The final organism remains `sleeping` at lifecycle one with unchanged environment step zero, water one, objective incomplete, and failure streak one.

## Protected test

`tests/test_action_failure_savepoint.py::test_classified_action_failure_rolls_back_partial_write_and_preserves_cost` protects the complete fixture, injection, savepoint rollback, exact ledger, event sequence, input consumption, checkpoint manifest, and final sleeping state.

GitHub Actions on Python 3.12 completed clean installation, compileall, genesis CLI smoke, and **32 protected tests**.

## Deliberately not implemented

- budget-exhaustion classification
- maintenance-threshold entry
- checkpoint repair or retention pruning
- lineage rollback
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

Slice 9 will classify a deterministic exhausted-budget condition before any forbidden environment mutation, preserve nonnegative accounting, checkpoint the unchanged state, and sleep below the maintenance threshold.
