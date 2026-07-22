# Phase 1 Slice 9: Classified Lifecycle Budget Exhaustion Before Mutation

Status: **implemented and verified in PR #23**

Tracked by: Issue #13

## Scope

This slice adds one operational pre-action monotonic deadline check and one protected deterministic exhaustion fixture without changing the canonical three-wake garden run or the protected budget configuration.

The fixture has an incomplete objective, exactly one executable registered action (`water_plot(bed-a)`), water inventory one, no harvestable fruit, and failure streak zero. Its fake clock is a complete declared deterministic input, not an organism-controlled switch.

## Deadline boundary

Every fixed-policy wake now performs one injected clock reading after decision selection and before any mutating executor is entered.

For the protected fixture:

- wake start monotonic time is `10,000,000 ns`
- the pre-action reading is `2,011,000,000 ns`
- observed lifecycle work time is therefore `2,001 ms`
- the protected lifecycle work limit remains `2,000 ms`
- the protected configuration remains `phase1-v1`

The runtime detects typed `lifecycle_wall_time_exhausted_before_action` before it records an action proposal, charges an action attempt, reserves a successful mutation, opens the action savepoint, or writes any environment row.

The classification is accepted only while the detection reading remains inside the protected cleanup-grace envelope. Exceeding both the work deadline and cleanup envelope is not reclassified by this slice and still aborts the outer wake.

## Independent evaluation

The independent evaluator:

- re-reads the canonical protected budget configuration and proves it equals `PHASE1_BUDGETS`
- proves the selected water action was otherwise executable
- proves every plot is unchanged
- proves water and harvested inventory are unchanged
- proves environment step and objective state are unchanged
- proves unresolved needs remain two
- records evaluation success false with progress `budget_exhausted_before_action`

## Accounting and boundary

The wake consumes one input and one observation. It consumes zero action attempts, zero successful environment mutations, and zero caregiver, network, subprocess, or authoritative external-write capability.

The typed exhaustion records:

- budget name `lifecycle_wall_time_ms`
- configured value `2000`
- consumed value `2001`
- remaining value `0`
- attempted forbidden operation `execute_garden_action`
- environment step `0`
- state mutation occurred `false`

Exact sequence:

- event 4: protected fixture prepared
- event 5: fixture checkpoint pending
- event 6: fixture checkpoint stabilized
- event 7: budget-exhaustion tick received
- events 8–10: wake accepted, input claimed, observation created
- event 11: budget exhausted
- event 12: evaluation completed
- event 13: failure streak updated from zero to one
- event 14: lifecycle completed as `budget_exhaustion`
- event 15: budget ledger
- event 16: lifecycle checkpoint pending
- event 17: lifecycle checkpoint stabilized

The final organism remains `sleeping` at lifecycle one with unchanged environment step zero, water one, objective incomplete, and failure streak one.

## Normal-path compatibility

Normal wakes now consume five declared clock readings: wake start, pre-action check, wake finish, checkpoint start, and checkpoint finish. Wall timestamps in the canonical three-wake tests remain unchanged.

The source-tree canonical sequence remains:

- water checkpoint boundary 13
- harvest checkpoint boundary 24
- objective-complete abstention boundary 34
- final event count 35
- final status `sleeping`

## Protected test

`tests/test_budget_exhaustion.py::test_lifecycle_budget_exhaustion_prevents_action_and_checkpoints` protects the complete fixture, pre-action deadline detection, typed payload, unchanged environment, exact nonnegative ledger, input consumption, failure increment, event sequence, checkpoint manifest, and final sleeping state.

Local source-tree validation completed compileall, the canonical three-wake CLI sequence, and **33 protected tests**. A separate local clean editable install could not resolve `hatchling>=1.25` from the execution environment's package mirror; that mirror failure is not treated as success.

GitHub Actions on Python 3.12 independently completed clean editable installation, compileall, genesis CLI smoke, and **33 protected tests**.

## Deliberately not implemented

- maintenance-threshold entry
- cleanup-grace deadline classification beyond the protected Slice 9 fixture
- checkpoint repair or retention pruning
- lineage rollback
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

After PR #23 is merged, Slice 10 will start from `consecutive_failures = 2`, commit one further classified failure, stabilize its checkpoint, enter `maintenance_required` at exactly three failures, and reject later normal wakes without advancing.
