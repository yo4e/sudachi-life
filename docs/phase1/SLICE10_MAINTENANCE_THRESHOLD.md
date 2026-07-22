# Phase 1 Slice 10: Maintenance Threshold Entry

Status: **implemented and verified in PR #24**

Tracked by: Issue #13

## Scope

This slice implements the exact protected transition from a committed third consecutive classified failure into `maintenance_required`.

A separate administrative fixture starts with:

- incomplete objective
- no executable protected mutation
- `consecutive_failures = 2`
- stable checkpointed state
- two queued uniquely identified garden ticks

The first tick is claimed, observed, and classified as `no_applicable_action`. The second tick remains queued to prove that a later normal wake cannot advance after maintenance begins.

## Threshold transition

The classified wake consumes one input and one observation. It consumes zero action attempts, zero successful environment mutations, and zero caregiver, network, subprocess, or authoritative external-write capability.

Independent evaluation proves that plots, inventory, objective state, unresolved needs, and environment step are unchanged.

The failure streak advances exactly from two to three. The pending checkpoint records typed reason `consecutive_failure_limit_reached` and required post-stabilization status `maintenance_required`.

## Checkpoint registration and maintenance

The lifecycle commits pending boundary event 17. The immutable checkpoint snapshot contains:

- status `checkpoint_pending`
- checkpoint pending true
- `consecutive_failures = 3`
- maintenance reason `consecutive_failure_limit_reached`

Checkpoint registration then:

1. registers boundary 17 stable
2. clears the pending fields
3. leaves the organism in `maintenance_required` rather than `sleeping`
4. records `checkpoint_stabilized` at event 18
5. records `maintenance_entered` at event 19

The final organism remains at lifecycle one with environment step zero, objective incomplete, failure streak three, and typed maintenance reason.

## Later wake rejection

A second tick is already queued before threshold entry. A later normal wake:

- is rejected during wake acquisition because status is `maintenance_required`
- consumes no clock reading
- claims or consumes no input
- appends no event
- does not change lifecycle number, failure streak, environment, checkpoint references, or status

The queued second tick remains unclaimed and unconsumed.

## Protected test

`tests/test_maintenance_threshold.py::test_third_classified_failure_enters_maintenance_and_blocks_later_wake` protects the fixture, classified abstention, unchanged environment, exact budgets, failure transition, checkpoint snapshot, final maintenance state, typed events, and later wake rejection.

Local source-tree validation completed compileall and **34 protected tests**. A separate local editable install could not import `hatchling.build`; that environment failure is not treated as success.

GitHub Actions on Python 3.12 independently completed clean editable installation, compileall, genesis CLI smoke, and **34 protected tests**.

## Deliberately not implemented

- maintenance inspection beyond existing status reads
- maintenance exit or failure-counter clearing
- checkpoint repair or retention pruning
- lineage rollback
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

After PR #24 is merged, Slice 11 will add one explicit protected read-only maintenance-inspection boundary. It must report the typed maintenance reason, failure streak, latest stable checkpoint, and queued-input state while performing no clock reads, canonical writes, event additions, input claims, or maintenance clearing. Normal wakes must remain blocked.
