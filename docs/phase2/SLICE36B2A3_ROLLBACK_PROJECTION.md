# Slice 36b2a3: Zero-caregiver rollback artifact projection

## Status

Implemented test-first on PR #70. This sub-slice extends the accepted `phase1-projection-v2` evidence graph through the complete Phase 1 rollback chain.

It follows merged PR #69, which closed retention projection. Semantic event export and the remaining physical overhead and absolute-limit evidence are not included here.

## Matrix scope

Primary evidence:

- P2-C03 exact rollback event and artifact projection locations
- P2-C08 paired schema-v1/schema-v2-zero rollback semantics
- P2-C13 exact `RA`, `RC`, `TC`, and `CP` linkage
- P2-C14 integrity before byte/path omission
- P2-C18 wrong identity and wrong-location rejection
- rollback-relevant P2-O20 projected digest and linkage corruption rejection

## Test-first evidence

Tests-only head:

`38a8933f53d09ac5c4d39748a498cf90c5fa631e`

GitHub Actions run 452 failed before implementation because `sudachi_life.phase2_rollback_projection` did not exist. The failure preceded every runtime implementation commit.

The full implementation plus lineage-sequence collision test reached head:

`b66a93c2b99b6f48ea06d3b13e47f028297d4c9e`

GitHub Actions run 458 passed:

- dependency installation succeeded
- source and test compilation succeeded
- protected suite: `191 passed in 15.59s`
- schema-v1 genesis CLI smoke succeeded

The unchanged 152-test Phase 1 suite remains included. Codex was not used.

## Paired semantic scenario

The primary pair uses identical organism IDs, clocks, inputs, seeds, selected semantic boundaries, administrative reasons, and operation order.

Each side:

1. initializes one stable organism
2. performs one real water wake and stabilizes checkpoint boundary `13`
3. preserves the pre-rollback body at active event sequence `14`
4. selects genesis checkpoint boundary `2`
5. records `rollback_started` at abandoned-lineage sequence `15`
6. builds one immutable source restore candidate
7. transforms it into new lineage generation `1`
8. records `rollback_lineage_prepared` at new-lineage sequence `3`
9. atomically replaces canonical authority
10. records `rollback_completed` at new-lineage sequence `4`

The semantic identities are:

- selected checkpoint: `CP(0,2)`
- abandoned-future archive: `RA(0,14,2)`
- source restore candidate: `RC(0,15,2)`
- transformed candidate: `TC(1,3)`

## Artifact validation before projection

Every rollback artifact is validated through the existing protected Phase 1 runtime validators before semantic replacement.

The rollback evidence layer independently retains:

- raw directory and manifest identity
- manifest SHA-256
- database SHA-256
- measured database size
- measured complete artifact size
- canonical manifest JSON
- projected semantic SQLite state

### Pre-rollback archive

The archive must link exactly to:

- abandoned lineage, lifecycle, status, and active event boundary
- latest stable checkpoint
- selected checkpoint
- selected checkpoint manifest/database digest and size
- immutable archived database bytes

Only after validation are its directory and `archive_id` replaced by `RA`, checkpoint IDs replaced by `CP`, schema version normalized, and declared byte-derived fields replaced by `<validated-byte-derived>`.

### Source restore candidate

The source candidate must validate as an exact SQLite restoration of the selected checkpoint and link to the same archive and durable `rollback_started` event. Its raw ID becomes `RC` only after the source checkpoint, archive, candidate manifest, candidate database, and all declared digests and sizes agree.

### Transformed candidate

The transformed candidate must pass the existing complete artifact-chain validator. Its database must contain the exact isolated lineage transformation and `rollback_lineage_prepared` event. Its raw ID becomes `TC` only after exact `RC`, `RA`, and `CP` linkage and all declared source/archive/selected/transformed byte evidence pass.

## Cross-lineage latest-stable checkpoint reference

After transformation, the organism belongs to new lineage generation `1` while its latest stable checkpoint is still the selected old-lineage checkpoint `CP(0,2)`.

The ordinary core projection assumes a normal same-lineage latest checkpoint. The rollback adapter therefore resolves `organism.latest_stable_checkpoint_id` by exact raw checkpoint ID plus event sequence against the complete validated artifact map. It does not invent `CP(1,2)` from the organism lineage.

This rule is isolated to rollback projection. The merged core, repair, and retention public contracts remain unchanged.

## Preserved abandoned future

After canonical replacement, the active registry rewinds to the selected source boundary. The later water checkpoint at `CP(0,13)` remains physically present as abandoned-future evidence.

Rollback capture permits visible checkpoint artifacts to be a strict superset of the active registry only when every extra artifact is found with matching raw ID, lineage/event boundary, manifest digest, database digest, and database size in a validated pre-rollback archive registry.

An unrelated unregistered checkpoint is rejected rather than treated as rollback evidence.

## Lineage-aware event evidence

Rollback event evidence is keyed by:

```text
(lineage_generation, event_sequence, event_type)
```

This is required because Phase 1 rollback rewinds event sequence numbering in the new lineage.

A protected second scenario rolls back to the latest checkpoint. It produces both:

- lineage `0`, event sequence `15`: `rollback_started`
- lineage `1`, event sequence `15`: `rollback_completed`

Both remain independently validated and projected. A sequence-only ledger would silently overwrite one branch and is not accepted.

## Exact event projection

`rollback_started` validates and projects exact latest/selected checkpoint and archive identities plus four declared digest paths.

`rollback_lineage_prepared` requires the exact protected key set, projects selected checkpoint, archive, and source candidate identities, and replaces exactly six declared digest paths.

`rollback_completed` projects selected checkpoint, archive, source candidate, and transformed candidate identities and replaces exactly eight declared digest paths.

No suffix, prefix, recursive, wildcard, regex-by-key, or global key-name normalization is used.

## Protected negative evidence

Tests reject a modified `rollback_started.archive_database_sha256` before sentinel replacement.

The full paired paths also require exact runtime validation of every archive and candidate manifest, database, directory entry set, protected schema, foreign keys, digest, size, and cross-artifact link before equality is considered.

## Runtime and authority boundaries

This sub-slice adds noncanonical comparison evidence only. It does not change:

- Phase 1 rollback preparation, intent, restoration, transformation, replacement, or completion
- canonical SQLite schema or writer authority
- checkpoint retention or one-completed-rollback policy
- organism actions, selector, executor, evaluator, clocks, or budgets
- any of the 152 Phase 1 tests

## Deferred boundary

After PR #70 is reviewed and merged, remaining Slice 36b2 work is:

1. semantic event export projection and independent raw export validation
2. checkpoint/archive/candidate overhead evidence
3. aggregate manifest/directory metadata overhead
4. absolute 8 MiB active/artifact, 40 MiB checkpoint-store, 64 MiB working-set, and 1 MiB next-wake reserve scenarios

Slice 37 remains blocked until every Slice 36 requirement is merged and no blocker, high, or medium boundary defect remains.
