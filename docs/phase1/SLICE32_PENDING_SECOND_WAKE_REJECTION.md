# Slice 32: Second Wake Rejection Behind Pending Checkpoint

## Purpose

Close Minimal Organism Contract v0.2 evaluation 31: no later normal wake may advance while a prior committed lifecycle remains `checkpoint_pending`.

## Protected scenario

`tests/test_pending_second_wake_rejection.py` enqueues two distinct ticks before the first wake.

The first wake:

- claims only the first tick
- commits the canonical water action
- commits an exact pending checkpoint boundary
- times out during checkpoint stabilization after publishing one valid orphan checkpoint
- leaves the second tick unclaimed and unconsumed

The test captures the complete pending body, active SQLite digest, both inbox rows, canonical event history, SQLite sequences, checkpoint registry, and checkpoint artifact files.

A second normal wake is then attempted with an empty fake clock. It must raise typed `CheckpointRequiredError` during wake acquisition before any clock read, `wake_accepted` event, or second-input claim. The complete pending snapshot and artifact set must remain exact.

The existing administrative `repair_pending_checkpoint_registration(...)` path then registers the published orphan, returns the organism to `sleeping`, and records one audit event. The already queued second tick must subsequently run through the canonical harvest lifecycle and complete the objective.

## Result

Pending test-first GitHub Actions evidence. No production conclusion is claimed until the standard workflow completes.
