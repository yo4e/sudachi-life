# Slice 32: Second Wake Rejection Behind Pending Checkpoint

## Purpose

Close Minimal Organism Contract v0.2 evaluation 31: no later normal wake may advance while a prior committed lifecycle remains `checkpoint_pending`.

## Protected scenario

`tests/test_pending_second_wake_rejection.py` enqueues two distinct ticks before the first wake.

The first wake:

- claims only the first tick
- commits the canonical water action
- commits an exact pending checkpoint boundary at event 14
- times out during checkpoint stabilization after publishing one valid orphan checkpoint
- leaves the second tick unclaimed and unconsumed

The test captures the complete pending body, active SQLite digest, both inbox rows, canonical event history, SQLite sequences, checkpoint registry, and checkpoint artifact files.

## Second-wake rejection

A second normal wake is attempted with an empty fake clock.

It must raise typed `CheckpointRequiredError` during `WakeTransaction.acquire(...)`, before:

- any clock read
- any `wake_accepted` event
- any second-input claim or consumption
- any lifecycle-number or status change
- any database-byte, sequence, registry, or checkpoint-artifact change

The complete pending snapshot remains exact. The second tick remains `(claimed_lifecycle_number=NULL, consumed=0)`.

## Existing repair and resumed progress

The existing administrative `repair_pending_checkpoint_registration(...)` path registers the published orphan, returns the organism to `sleeping`, advances the stable boundary to event 14, and records one `checkpoint_registration_repaired` audit event at sequence 15.

The already queued second tick then runs through the canonical harvest lifecycle:

- it is claimed by lifecycle 2
- `harvest_plot(bed-b)` is selected
- independent evaluation succeeds
- environment step becomes 2
- one fruit is harvested and the objective completes
- pending boundary 24 is stabilized by event 25
- final status is `sleeping`

No replacement input or retry queue is introduced.

## Result

The existing implementation passed unchanged.

`WakeTransaction.acquire(...)` validates the committed pending boundary before the lifecycle reads its injected clock or appends wake history. The existing repair operation restores wakeability only after exact orphan validation and atomic registry/audit mutation.

No production source, schema, contract, action, evaluator, clock boundary, budget, checkpoint mechanism, or repair behavior changed.

## Validation

GitHub Actions run 290 on Python 3.12 proved the protected test and initial durable note:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **127 protected tests in 7.66 seconds**

Draft PRs #48 and #49 were closed without merge after GitHub failed to attach workflow runs to their later branch-head updates. The final replacement branch was created directly from the complete recorded commit, then received this new commit before its pull request was opened. The resulting pull-request workflow must pass on the exact complete head before merge.