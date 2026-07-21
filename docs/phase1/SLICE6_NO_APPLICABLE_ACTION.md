# Phase 1 Slice 6: Classified No-Applicable-Action Abstention

Status: **implemented and verified in PR #20**

Tracked by: Issue #13

## Scope

This slice adds one protected classified failure outcome without changing the canonical three-wake garden run. An explicit administrative test fixture creates a stable state in which:

- the objective is incomplete
- `bed-a` is a dry living sprout
- no water is available
- `bed-b` has no fruit
- harvested inventory is empty
- no protected mutating action is executable

One uniquely identified garden tick then causes SUDACHI-0 to:

1. acquire fail-fast SQLite write ownership
2. claim one oldest eligible tick
3. build one complete deterministic observation
4. select typed `no_applicable_action` abstention before entering a mutating executor
5. consume no action-attempt or environment-mutation budget
6. independently verify the blocked incomplete state
7. increment `consecutive_failures` exactly once
8. commit an exact checkpoint-pending boundary
9. publish and register a verified lifecycle checkpoint
10. return to sleep below the protected maintenance threshold

The fixture is explicit test administration. It is not caregiver input and does not participate in policy selection.

## Protected decision and evaluation

The fixed policy order remains:

1. abstain with `objective_already_complete` when the objective is complete
2. water the lexicographically first executable dry plot
3. harvest the lexicographically first executable fruit
4. abstain with `no_applicable_action` when the objective is incomplete and neither protected mutation is executable

The independent evaluator rejects the blocked abstention unless all of the following are true:

- the prior observation is incomplete
- all plots are unchanged
- inventory is unchanged
- environment step is unchanged
- recomputed objective remains incomplete
- no water action is executable with available inventory
- no harvest action is executable
- at least one unresolved need remains
- the unresolved-need count is unchanged

The evaluation is recorded as unsuccessful progress classification, not as an exception or transaction rollback.

## Budget and event accounting

The wake consumes:

- one input event
- one observation
- zero action attempts
- zero environment mutations
- zero caregiver consultations
- zero network calls
- zero subprocess calls
- zero authoritative external writes

There is no `action_proposed` or `action_completed` event. The lifecycle records one `action_abstained` event and one `failure_streak_updated` event.

Exact protected sequence:

- event 4: protected fixture prepared
- event 5: fixture checkpoint pending boundary
- event 6: fixture checkpoint stabilized
- event 7: blocked test tick received
- event 8: wake accepted
- event 9: input claimed
- event 10: observation created
- event 11: `action_abstained`
- event 12: evaluation completed
- event 13: failure streak updated from zero to one
- event 14: lifecycle completed
- event 15: budget ledger
- event 16: lifecycle checkpoint pending boundary
- event 17: lifecycle checkpoint stabilized

The final organism remains `sleeping` at lifecycle 1 with environment step 0, objective incomplete, and failure streak 1. The maintenance threshold is 3 and is deliberately not entered in this slice.

## Protected tests

`tests/test_no_applicable_action.py` proves:

- the complete classified wake and exact budget ledger
- no environment transition
- exact failure-streak increment
- exact event ordering and checkpoint boundary
- stable checkpoint manifest validation
- rejection of `no_applicable_action` when an executable protected action exists

GitHub Actions on Python 3.12 completed clean installation, compileall, genesis CLI smoke, and **30 protected tests**.

A local source-tree run also passed 30 tests and compileall. A separate local clean editable install was blocked because the execution environment package mirror could not resolve `hatchling`; GitHub Actions independently verified the clean install.

## Deliberately not implemented

- resource-aware recovery from a prior failure
- budget-exhaustion classification
- injected action failure and savepoint cost preservation
- maintenance-threshold entry
- checkpoint repair or retention pruning
- rollback lineage
- deterministic JSONL export
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

Slice 7 will use a protected fixture with a dry plot, no water, one harvestable fruit, and failure streak 1. The fixed policy must skip impossible watering, harvest the fruit, independently prove positive progress, reset the failure streak to zero, checkpoint, and sleep.
