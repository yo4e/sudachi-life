# Slice 36b2a2: Checkpoint-retention semantic projection

## Status

Implemented test-first on draft PR #69. This sub-slice extends the merged cumulative checkpoint/repair evidence ledger through the exact retention paths accepted by ADR 0009.

Rollback, event export, and the remaining physical budget closure are not included here.

## Matrix scope

Primary evidence:

- P2-C03 exact retention projection locations
- P2-C08 paired schema-v1/schema-v2-zero retention semantics
- P2-C12 prune, failure, staging, pending reconciliation, and completed reconciliation
- P2-C14 integrity and byte recomputation before omission
- P2-C15 closed typed event paths without key-name normalization
- P2-C18 wrong identity and wrong staging-location rejection
- retention-relevant P2-O20 corruption rejection

## Test-first evidence

Tests-only head:

`38bab7c49d41c16a8ef8b73da52fd4e4bd7e9f14`

GitHub Actions run 443 failed before implementation because the declared retention projection module did not exist:

```text
ModuleNotFoundError: No module named 'sudachi_life.phase2_retention_projection'
```

The failure artifact was retained before production code was added.

Implementation and protected-corruption candidate before continuity-note synchronization:

`e2c87ebf9d20a09a83eba3179473fb6a24e4c356`

GitHub Actions run 447:

- dependency installation succeeded
- source and test compilation succeeded
- protected suite: `185 passed in 16.65s`
- schema-v1 genesis CLI smoke succeeded

The 185 tests contain the unchanged 152-test Phase 1 suite, the previously merged Phase 2 tests, six paired retention projection tests, and one explicit retention byte-corruption test.

## Closed extension boundary

`src/sudachi_life/phase2_retention_projection.py` layers one retention-specific evidence record over the merged `ZeroCaregiverEvidence` ledger. It does not change Phase 1 runtime behavior, checkpoint retention behavior, canonical schema, or the merged checkpoint/repair oracle.

The public extension provides:

- `capture_zero_caregiver_retention_evidence`
- `project_zero_caregiver_retention_state`
- `assert_zero_caregiver_retention_equivalent`
- frozen `RetentionStagingEvidence`
- frozen `ZeroCaregiverRetentionEvidence`

The retained core evidence remains the authority for validated checkpoint artifacts and their semantic `CP(g,e)` boundaries. The extension adds only:

- immutable committed-prune staging witnesses
- immutable raw/projected retention-event payload evidence
- the ordered set of currently visible staging boundaries

This evidence is noncanonical evaluation material. It grants no runtime or administrative authority and cannot mutate the organism.

## Pre-deletion artifact requirement

A normal prune removes the oldest eligible artifact before the final run state is projected. Therefore `checkpoint_pruned` cannot be validated from the final filesystem alone.

The caller must capture cumulative evidence before the prune. Later capture requires the deleted boundary to exist in that prior immutable artifact ledger. The implementation never reconstructs deleted bytes or identity from checkpoint-ID spelling.

Before projection, `checkpoint_pruned` independently validates:

- latest raw checkpoint identity against `CP(event.lineage_generation, latest_stable_event_sequence)`
- pruned raw checkpoint identity against `CP(pruned_lineage_generation, pruned_event_sequence)`
- pruned artifact bytes against the previously measured artifact size
- pruned database bytes against the previously measured database size
- retained checkpoint count against the current registry
- retained checkpoint-store bytes against the current measured store
- latest presence and pruned absence in the current registry

Only after those checks are the two declared IDs replaced by `CP` tokens and the three declared byte-derived values replaced by `<validated-byte-derived>`.

## Retention failure paths

### Pre-commit failure and restoration

For `candidate_restored=true`, capture requires:

- exact protected reason and injection point
- candidate and latest raw IDs linked to prior artifact evidence
- candidate and latest boundaries present in the registry
- no remaining staging witness for the restored candidate
- exact registered boundary list and count
- exact measured checkpoint-store bytes
- maintenance classification unchanged

The candidate and latest IDs become `CP` tokens. The measured store value becomes the byte-derived sentinel.

### Post-commit cleanup failure

For `candidate_restored=false`, capture requires:

- the candidate boundary absent from the current registry
- one current `.pruning-<raw-checkpoint-id>` directory
- a valid manifest and checkpoint database inside that directory
- manifest, database digest, database size, artifact size, and canonical manifest exactly equal to the pre-deletion checkpoint witness
- exact protected reason and injection point
- exact raw event `staging_directory`

Only after this bijection is proven does the raw directory become `STAGE(CP(g,e))`.

The physical `.pruning-` prefix is used only to inventory the accepted runtime staging artifact class. It is not a payload-key wildcard or a normalization rule. The discovered directory must then equal the exact raw checkpoint identity and the complete prior artifact witness.

## Reconciliation evidence chain

For `checkpoint_retention_cleanup_reconciliation_pending`, the implementation requires the exact key set and aligned raw `checkpoint_ids` and `staging_directories` lists. Each pair must resolve to one previously validated staging witness, and list order is preserved. The two lists become corresponding `CP` and `STAGE(CP)` tokens.

For `checkpoint_retention_cleanup_reconciled`, the implementation does not rediscover deleted directories. It follows the exact `reconciliation_pending_event_sequence`, requires one previously captured pending-event proof, verifies that `removed_staging_directories` equals the pending raw list, and then reuses the pending projected list.

This closes the interrupted path where deletion succeeds but completion audit has not yet committed. A retry can complete with zero new clock reads while retaining the prior semantic witness.

## Protected scenarios

The paired tests use identical organism identity, clocks, wake seeds, external event IDs, fault choices, and operation order for schema-v1 and schema-v2-zero controls.

They prove exact projected equality for:

- normal fifth-checkpoint prune
- pre-commit retention failure with candidate restoration
- post-commit cleanup failure with a surviving staged artifact
- reconciliation-pending audit after staged deletion
- retry and completed reconciliation

They also prove:

- normal prune is rejected without a pre-deletion artifact witness
- a wrong raw staging directory is rejected before `STAGE` projection
- a one-byte discrepancy in `pruned_artifact_size_bytes` is rejected before sentinel replacement

All unlisted event columns, event order, lineage, lifecycle, source, reason, status, maintenance state, registry boundary, and payload values remain exact.

## Explicit non-deliverables

This sub-slice does not implement:

- pre-rollback archive projection (`RA`)
- source restore candidate projection (`RC`)
- transformed candidate projection (`TC`)
- rollback-completion identity projection
- semantic JSONL event export comparison
- independent checkpoint/archive/candidate physical overhead closure
- aggregate manifest/directory overhead closure
- absolute 8/40/64 MiB and 1 MiB reserve scenarios
- any caregiver request, fixture, ingress, or disposition behavior

## Next boundary

The next Slice 36b2 sub-slice must extend the same cumulative immutable evidence graph through rollback artifacts and completion events using the exact `RA`, `RC`, `TC`, and `CP` paths accepted by ADR 0009.

It may not weaken the merged checkpoint, repair, or retention evidence layers. Slice 37 remains blocked until rollback, export, and physical closure are merged and Slice 36 has no unresolved blocker, high, or medium boundary defect.
