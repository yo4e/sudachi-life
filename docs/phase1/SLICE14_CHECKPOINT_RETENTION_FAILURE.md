# Phase 1 Slice 14: Classified Checkpoint-Retention Failure

Status: **implemented locally; GitHub validation pending in PR #28**

Tracked by: Issue #13

## Scope

This slice protects one deterministic checkpoint-retention pruning failure only after the newer lifecycle checkpoint is stable and registered.

The failure is injected after the oldest eligible artifact has been moved to its same-filesystem staging name and before the canonical checkpoint registry or pruning audit history is changed.

## Protected ordering

The canonical fourth objective-complete wake first:

1. commits pending checkpoint boundary `44`
2. publishes and verifies its immutable checkpoint artifact
3. registers boundary `44` as the canonical latest stable checkpoint
4. clears checkpoint-pending state
5. records `checkpoint_stabilized` at event `45`
6. begins retention only after the newer checkpoint is stable

The protected test-only failure then occurs at `after_artifact_stage_before_registry_mutation`.

## Classified failure handling

The retention transaction rolls back before canonical pruning commit and restores the staged boundary-`13` artifact to its original immutable directory name.

A second bounded administrative transaction then validates:

- stable canonical state
- exact latest checkpoint identity and boundary `44`
- five canonical checkpoint-registry rows
- five matching immutable checkpoint directories
- every retained checkpoint manifest and database
- absence of a `.pruning-*` staging directory
- exact checkpoint-store byte accounting

It then atomically:

- sets status to `maintenance_required`
- records maintenance reason `checkpoint_retention_pruning_failed`
- appends one typed `checkpoint_retention_failed` event from `administration:checkpoint-retention`

No `checkpoint_pruned` event is recorded.

## Protected fixture outcome

The final state is:

- lifecycle number `4`
- lineage generation `0`
- environment step `2`
- objective complete
- failure streak `0`
- latest stable checkpoint boundary `44`
- checkpoint stabilization event `45`
- checkpoint-retention failure event `46`
- event count `46`
- status `maintenance_required`
- maintenance reason `checkpoint_retention_pruning_failed`
- retained checkpoint boundaries `2`, `13`, `24`, `34`, and `44`

Genesis, the restored boundary-`13` checkpoint, and the newest boundary-`44` checkpoint all remain valid. The garden, inventory, objective, lineage, latest-stable references, and four consumed inbox rows remain unchanged.

Read-only maintenance inspection reports the new typed reason and the exact latest stable checkpoint. A later ordinary wake rejects before any clock read or state change.

## Protected test

`tests/test_checkpoint_retention_failure.py::test_retention_failure_restores_candidate_and_enters_maintenance` proves:

- the fifth checkpoint is stable before failure injection
- the failure occurs only after artifact staging and before registry mutation
- the staged artifact is restored
- all five registry rows and artifacts remain
- latest-stable identity and boundary remain exact
- every checkpoint validates
- byte accounting matches the restored filesystem
- no staging directory remains
- no false `checkpoint_pruned` event exists
- exactly one typed failure warning exists
- maintenance inspection remains read-only and accurate
- later ordinary wake rejection consumes zero clock readings

Local source-tree validation completed compileall and **43 protected tests**.

A separate local clean editable install could not resolve `hatchling>=1.25` from the execution environment's package mirror. That mirror failure is not treated as success. GitHub Actions must independently complete clean installation and the protected suite before merge.

## Deliberately not implemented

- checkpoint repair or orphan cleanup
- maintenance clear for the retention-failure reason
- post-commit staged-artifact cleanup recovery
- lineage-preserving rollback
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

The next slice must be selected from the remaining Contract v0.2 evaluation matrix only after PR #28 is independently verified and merged. Checkpoint repair and orphan cleanup are the leading boundary, but the exact scope must be confirmed against current Issue #13 and repository state before implementation.
