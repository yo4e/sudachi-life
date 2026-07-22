# Phase 1 Slice 13: Successful Bounded Checkpoint Retention

Status: **implemented and verified in PR #27**

Tracked by: Issue #13

## Scope

This slice adds the successful protected retention path for stable lifecycle checkpoints.

The protected retention limit remains four. The implementation does not change protected configuration, repair checkpoints, handle prune failure, or perform rollback.

## Protected ordering

Retention runs only after a newly published checkpoint has been registered as the canonical latest stable checkpoint and checkpoint-pending state has been cleared.

The retention transaction then:

1. acquires fail-fast SQLite write ownership
2. validates stable canonical state and the exact latest checkpoint identity and boundary
3. requires exactly one checkpoint above the protected retention limit
4. orders registered checkpoints by event boundary
5. skips the latest checkpoint
6. preserves genesis when possible
7. validates the oldest eligible non-genesis artifact and registry correspondence
8. stages that artifact by same-filesystem atomic rename
9. deletes exactly one matching registry row
10. appends one typed `checkpoint_pruned` administrative event
11. commits the canonical registry and audit changes
12. removes the staged immutable artifact and verifies retained checkpoint-store byte accounting

If the SQLite transaction fails before commit, the staged artifact is restored to its original name.

## Protected fixture

The fixture performs the canonical four wake sequence:

- genesis checkpoint at boundary `2`
- water checkpoint at boundary `13`
- harvest checkpoint at boundary `24`
- objective-complete abstention checkpoint at boundary `34`
- one further objective-complete abstention checkpoint at boundary `44`

Before the fourth wake, exactly four stable checkpoints exist and no pruning has occurred.

After boundary `44` is registered and stabilized at event `45`, retention prunes the oldest eligible lifecycle checkpoint at boundary `13`. Genesis is retained.

The final retained boundaries are:

- `2` — genesis
- `24` — harvest
- `34` — first objective-complete abstention
- `44` — newest objective-complete abstention

## Administrative record

Event `46` is typed `checkpoint_pruned` with source `administration:checkpoint-retention`.

Its canonical payload records:

- protected retention limit
- retained checkpoint count
- pruned checkpoint identifier, lineage, event boundary, provenance, database bytes, and total artifact bytes
- latest stable checkpoint identifier and event boundary
- retained checkpoint-store bytes
- reason `checkpoint_retention_limit`

## Preserved state

The successful pruning path preserves:

- active canonical SQLite state
- lifecycle number `4`
- lineage generation `0`
- environment step `2`
- completed objective
- plots and inventory
- failure streak zero
- status `sleeping`
- latest stable checkpoint identifier and boundary `44`
- all four consumed inbox rows
- genesis and the three newest eligible checkpoint artifacts
- normal wake acquisition after retention

The final active event count is `46`.

## Protected test

`tests/test_checkpoint_retention.py::test_fifth_stable_checkpoint_prunes_oldest_eligible_after_registration` proves:

- no pruning at four stable checkpoints
- the fifth checkpoint is stable before pruning begins
- genesis and the latest checkpoint are retained
- the oldest eligible non-genesis checkpoint is removed first
- registry rows and checkpoint directories both finish at exactly four
- every retained checkpoint still validates
- no retention staging directory remains
- byte accounting matches the retained filesystem
- the explicit pruning event is exact
- canonical garden and inbox state are unchanged
- a new normal wake transaction can still be acquired

## Validation

Local source-tree validation completed compileall and **42 protected tests**.

A separate local clean editable install could not resolve `hatchling>=1.25` from the execution environment's package mirror. That mirror failure is not treated as success.

GitHub Actions on Python 3.12 independently completed clean editable installation, compileall, genesis CLI smoke, and **42 protected tests**.

## Deliberately not implemented

- pruning-failure maintenance warning
- checkpoint repair or orphan cleanup
- lineage-preserving rollback
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

After PR #27 is merged, Slice 14 will protect one classified checkpoint-retention pruning failure after the newer checkpoint is already stable.

It must preserve the newly stable latest checkpoint and latest-stable references, avoid a false `checkpoint_pruned` success record, restore the staged older artifact when failure occurs before canonical pruning commit or otherwise expose incomplete cleanup explicitly, record one typed maintenance warning, and leave normal wakes blocked.

It must not add checkpoint repair, orphan cleanup, maintenance clear for the new reason, lineage rollback, caregiver consultation, learning, memory, or generic planning.
