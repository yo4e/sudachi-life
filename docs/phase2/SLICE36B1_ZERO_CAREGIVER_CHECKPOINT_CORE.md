# Slice 36b1: Zero-caregiver checkpoint projection core

## Status

Implemented test-first on PR #66. This sub-slice covers the canonical active database and genesis checkpoint core of accepted `phase1-projection-v2`.

It does not yet close repair, retention, rollback, event-export, or near-ceiling physical evidence. Those remain Slice 36b2.

## Matrix scope

Primary evidence:

- P2-C01–P2-C05 for canonical active-state and genesis-checkpoint projection
- P2-C08–P2-C10 for paired genesis equality and checkpoint semantic boundaries
- P2-C14–P2-C15 for integrity-before-projection and no wildcard normalization
- P2-C18 for wrong-location rejection
- P2-O20 for projected digest/link corruption rejection

## Test-first evidence

Tests-only head:

`3a784e6c3bebc8914569b347701aa8677e6215c7`

GitHub Actions run 426 failed because the projection module did not exist:

```text
ModuleNotFoundError: No module named 'sudachi_life.phase2_projection'
```

The failure artifact was retained before implementation.

## Implemented core

`src/sudachi_life/phase2_projection.py` now provides:

- `project_zero_caregiver_state`
- `assert_zero_caregiver_equivalent`
- `ZeroCaregiverProjectionError`

The comparison independently validates both sides before equality:

- left side must be schema-v1
- right side must be schema-v2 with exact `phase2-zero-caregiver-v1`
- all original Phase 1 tables and original AUTOINCREMENT sequences are projected in fixed order
- only declared top-level schema-version locations are normalized
- fixture configuration and every operational consultation row, sequence, event, or source are rejected
- checkpoint directories, manifests, databases, registry rows, and semantic boundaries are validated before byte-derived values are omitted
- `organism.latest_stable_checkpoint_id`, registry checkpoint IDs, and `checkpoint_stabilized` IDs must link to the same raw artifact before becoming `CP(g,e)`
- checkpoint database Phase 1 semantic state is included in the comparison, so recomputing a valid digest cannot hide a canonical artifact-state difference
- nested or unlisted keys remain exact

The current implementation is deliberately a checkpoint/genesis core. A checkpoint database containing earlier registered checkpoint history is not yet the full retained-history projection; Slice 36b2 must extend the exact typed artifact graph rather than weakening this core.

## Protected regressions

The protected tests prove:

- paired schema-v1/schema-v2-zero genesis projects to exact equality while raw database bytes differ
- fixture configuration is not accepted as a zero-caregiver control
- an unlisted event-payload checkpoint key remains visible
- a nested `schema_version` key is not normalized
- corrupted projected-away registry digest is detected before omission
- checkpoint directory identity is bijective with manifest and registry
- side roles cannot be swapped or replaced with two schema-v1 runs
- organism and stabilized-event checkpoint IDs are linked before projection
- a semantically modified checkpoint database remains different even after all digest and size links are recomputed consistently

## Final validation

Candidate head before durable-note synchronization:

`b48e20b2ea917fc4f6a0cbe85ee124b3d04c8a9e`

GitHub Actions run 430:

- dependency installation succeeded
- source and test compilation succeeded
- protected suite: `175 passed in 13.85s`
- schema-v1 genesis CLI smoke succeeded

The 175 tests contain the unchanged 152-test Phase 1 suite, 13 Slice 36a tests, and 10 Slice 36b1 tests.

## Deferred Slice 36b2 boundary

Slice 36b2 must extend the same closed typed map to:

- checkpoint registration repair
- retention prune, failure, pending reconciliation, and completed reconciliation
- pre-rollback archive, source restore candidate, transformed candidate, and rollback completion
- semantic event export
- independent checkpoint/archive/candidate physical overhead
- aggregate manifest/directory overhead
- absolute 8/40/64 MiB and 1 MiB reserve scenarios

It must implement exact `CP`, `RA`, `RC`, `TC`, and `STAGE` locations from ADR 0009. It may not introduce recursive, wildcard, suffix, prefix, or global key-name normalization.

Slice 37 remains blocked until Slice 36b2 is merged and Slice 36 has no unresolved blocker, high, or medium boundary defect.
