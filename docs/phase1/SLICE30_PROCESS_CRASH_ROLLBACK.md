# Slice 30: Real Process-Crash Wake Rollback

## Purpose

Close the remaining execution proof for Minimal Organism Contract v0.2 evaluation 27: a process exit before wake commit must preserve the prior canonical state and release the SQLite write lock.

This is an external protected-test harness. It does not add subprocess access, crash hooks, or fault-injection capabilities to the organism runtime.

## Protected crash harness

`tests/test_process_crash_rollback.py` initializes one organism, enqueues one normal garden tick, and captures the complete stable state before starting a spawned child process.

The child process:

1. acquires `WakeTransaction` through the normal fail-fast `BEGIN IMMEDIATE` boundary
2. claims the queued input
3. inserts one representative uncommitted event and advances the in-transaction event sequence
4. mutates `bed-a` moisture, water inventory, and environment step
5. changes the organism row to a pending lifecycle boundary
6. proves those uncommitted changes are visible inside the child transaction
7. sends that proof to the parent through a test-harness pipe
8. exits with `os._exit(73)` without commit, rollback, context-manager exit, or connection cleanup

The proof observed inside the child includes:

- inbox claim `(lifecycle 1, unconsumed)`
- one extra event at sequence 5
- organism lifecycle 1 in `checkpoint_pending`
- wet `bed-a`
- zero water units
- environment step 1

## Parent recovery proof

The parent requires the child to reach the crash boundary and exit within strict ten-second timeouts.

After exit, the parent opens the canonical database and acquires a new `BEGIN IMMEDIATE` transaction. This proves the former process no longer owns the write lock and triggers any required SQLite rollback-journal recovery.

The parent then requires exact equality with the pre-crash stable snapshot for:

- active SQLite SHA-256
- protected status and organism row
- environment, garden, and inventory rows
- inbox claim and consumption state
- complete canonical event history
- SQLite sequence state
- checkpoint registry
- every retained checkpoint artifact name, size, and SHA-256

The uncommitted crash-marker event and every child mutation are absent. The original tick is again unclaimed and unconsumed.

## Continued normal wakeability

After recovery, the parent runs the normal first-water lifecycle for the original tick.

The protected test requires:

- five exact injected clock readings
- claim of `process-crash-tick`
- `water_plot(bed-a)`
- successful independent evaluation
- lifecycle 1, environment step 1, zero remaining water
- exact stable event count 14
- final `sleeping` status
- original inbox row claimed and consumed exactly once
- no committed crash-marker event

## Test-first correction

GitHub Actions run 275 initially reported one failing assertion while all 124 existing tests passed. The failing assertion required the SQLite rollback-journal pathname to be absent after recovery.

That condition exceeded the accepted contract. SQLite may leave, truncate, or reuse a non-canonical journal file depending on implementation details. SUDACHI requires exact canonical state recovery and released write ownership, not a specific journal-file deletion policy.

The test was narrowed by removing only that pathname assertion. No production code or contract changed.

## Validation

Standard GitHub Actions run 276 on Python 3.12 passed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **125 protected tests in 6.38 seconds**

## Boundary preserved

Slice 30 adds only a protected multiprocessing test harness and durable documentation. It does not:

- expose subprocess execution to organism code
- add a production crash or fault-injection interface
- change SQLite journal mode or transaction semantics
- add recovery retries or generic replay machinery
- change schema, contract, actions, evaluators, budgets, checkpoints, or rollback rules
