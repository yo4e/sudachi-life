# Slice 27: Protected Cleanup-Grace Boundary

## Purpose

Close Minimal Organism Contract v0.2 evaluation 7: protected cleanup grace cannot be used for additional organism work.

The accepted Phase 1 budget configuration provides:

- 2000 ms for normal organism lifecycle work
- 250 ms of runtime-only cleanup grace

Cleanup grace is reserved for typed terminal reporting, rollback, validation, and connection closure. It is not additional action-selection or execution time.

## Test-first finding

The existing lifecycle already checked the monotonic deadline immediately before executor entry. A mutating decision detected after 2000 ms therefore produced:

- zero action attempts
- zero environment mutations
- no retry or second decision
- no caregiver, network, subprocess, or external-write use

However, the runtime reused the pre-action clock reading when finalizing the classified exhaustion. It did not read the injected clock after terminal records were prepared. As a result, it could not prove that terminalization itself remained inside the 250 ms cleanup reserve, and an overrun could proceed into checkpoint stabilization instead of rolling back the uncommitted wake.

GitHub Actions run 247 captured this expected test-first failure:

- the exact-boundary case consumed four readings instead of the required five
- the one-nanosecond-overrun case reached checkpoint code and exhausted the fake clock
- 120 existing tests passed and the two new boundary tests failed

## Production correction

`WakeBudgetLedger.finish_exhausted(...)` now receives the elapsed monotonic time measured at the explicit terminalization boundary.

It requires that the supplied elapsed time:

1. is nonnegative
2. is not earlier than the original exhaustion-detection reading
3. is no greater than `lifecycle_wall_time_ms + cleanup_grace_ms`

Elapsed time exactly equal to 2250 ms is accepted. A value greater than 2250 ms raises `BudgetExhaustedError` with the typed reason that protected cleanup grace expired before lifecycle terminalization.

`perform_garden_wake(...)` now performs one declared injected clock read after the terminal events have been prepared and before the budget ledger and checkpoint-pending boundary are finalized. Successful classified exhaustion records this terminalization elapsed time in the budget ledger. The original `ProtectedBudgetExhaustion` continues to record the earlier pre-action detection elapsed time.

## Protected cases

`tests/test_cleanup_grace.py` proves two adjacent boundaries.

### Exact upper boundary

At 2001 ms, normal work stops before executor entry. Terminalization reaches exactly 2250 ms and is accepted.

The test requires:

- five exact clock reads including the new terminalization boundary
- zero action attempts and environment mutations
- zero caregiver use
- no action-proposed, action-completed, or action-failed event
- a classified exhaustion whose detection elapsed remains 2001 ms
- a budget ledger whose complete terminalization elapsed is 2250 ms

### One nanosecond beyond grace

Normal work again stops at 2001 ms, but terminalization reaches 2250 ms plus one nanosecond.

The test requires:

- `BudgetExhaustedError` before checkpoint work
- exactly three clock reads and no hidden later read
- rollback of every uncommitted lifecycle event and state change
- unchanged status, event history, SQLite sequence state, garden, inventory, and environment
- the queued input remains unclaimed and unconsumed

No classified committed lifecycle is allowed to claim cleanup success after the reserve expires.

## Validation

Standard GitHub Actions on Python 3.12 passed:

- run 255 proved the production-and-test head: **122 protected tests in 7.02 seconds**
- run 260 proved the complete implementation, durable note, matrix, collaboration guidance, and continuity head: **122 protected tests in 8.38 seconds**
- clean editable installation passed
- source and test compilation passed
- genesis CLI smoke passed

The temporary branch-only patch workflow used to work around connector whole-file editing limits was removed before standard validation. The final pull-request diff contains only production source, protected tests, and durable documentation.

## Boundary preserved

Slice 27 does not change:

- the 2000 ms lifecycle limit
- the 250 ms cleanup-grace limit
- action, evaluator, environment, schema, or contract definitions
- checkpoint budgets or behavior
- failure-streak classification
- caregiver or external capability budgets

It adds one explicit deterministic clock boundary and enforces the already accepted cleanup-grace contract.
