# Phase 1 Slice 26: Exact Repeated-Run Canonical Equivalence

Status: **implemented and verified in PR #42**

Tracked by: Issue #13

## Scope

This slice closes Minimal Organism Contract v0.2 evaluation 1 with an exact comparison between two complete canonical first-water runs whose declared inputs are identical.

The slice adds protected coverage only. It does not change production code, schema, clock semantics, fixed policy, action execution, evaluation, budgets, event format, checkpoint machinery, or rollback behavior.

## Protected scenario

`tests/test_repeated_run_equivalence.py::test_identical_declared_inputs_produce_exact_first_wake_results`:

1. initializes two independent runtime roots with the same organism identifier, versions, seed-garden state, and genesis clock reading
2. enqueues the same uniquely identified `synthetic:garden_tick` with the same injected clock reading
3. supplies the same declared seed and the same five wake and checkpoint clock readings
4. performs one complete first-water wake in each runtime
5. compares every declared and derived result without normalization
6. supplies the same next tick to both sleeping organisms and proves exact continued canonical equivalence

## Exact comparison

The test requires equality of:

- complete `WakeResult.as_dict()` values
- complete protected status values
- policy decision and independent evaluation
- concrete budget ledger
- lifecycle number, pending boundary 13, stable event 14, lineage, and final sleeping state
- checkpoint identifier, database digest, manifest digest, size, and complete manifest contents
- lifecycle checkpoint database bytes and logical canonical contents
- active canonical SQLite database bytes and logical contents
- protected schema definitions
- every canonical table row
- SQLite `sqlite_sequence` state and `user_version`
- complete checkpoint-store relative file set
- every checkpoint artifact size and SHA-256 digest
- acceptance of the same next external tick after stabilization

No declared input, audit value, digest, identifier, timestamp, path-relative artifact name, or canonical field is normalized.

## Exact result

Both runs:

- select `water_plot(bed-a)`
- change `bed-a.moisture` from `0` to `1`
- consume the one water unit
- advance environment step from `0` to `1`
- produce positive independent evaluation
- consume the same bounded budget vector
- commit checkpoint-pending boundary 13
- publish the same digest-derived checkpoint identifier
- append `checkpoint_stabilized` at event 14
- return to `sleeping`
- accept the same next tick with the same inbox identity and event history

The active SQLite files and complete checkpoint stores are byte-equivalent across the two independent runtime roots.

## Verification

GitHub Actions run 241 on Python 3.12 completed:

- clean editable installation
- source and test compilation
- **120 protected tests passed in 6.75 seconds**
- genesis CLI smoke test

No production correction was required.

## Deliberately out of scope

- generic replay machinery
- changing randomness or seed semantics
- cleanup-grace classification
- insertion-order tie-breaking fixtures
- duplicate-input replay after action
- process-crash execution
- nested-wake handling
- schema, contract, environment, action, evaluator, checkpoint, or rollback changes
- caregiver, learning, memory, skills, or later-phase machinery

## Exact next action

After PR #42 is merged, reconstruct current `main`, Issue #13, and open pull requests. The next incomplete fixed evaluation is evaluation 7: protected cleanup grace cannot be used for additional organism work. Define the narrow classified boundary before changing production code, add the protected test first, and make a production correction only if required by the accepted contract.