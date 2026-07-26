# Slice 36b2a5: Paired physical overhead evidence

## Status

Implemented test-first on PR #72. This sub-slice closes ADR 0009 and Phase 2 matrix P2-O15–P2-O17.

It follows merged PR #71 semantic event-export projection. Independent absolute-limit and real near-ceiling evidence remain outside this sub-slice.

## Test-first evidence

Tests-only head:

`32aae47219da80d56baa6a65bcf87d29b59987d8`

GitHub Actions run 470 failed before implementation because `sudachi_life.phase2_physical_projection` did not exist.

Implementation plus active-cap enforcement head:

`2464ba1eb6fe95520efcf1c6fa20e3664d6351ee`

GitHub Actions run 472 passed:

- dependency installation succeeded
- source and test compilation succeeded
- protected suite: `200 passed in 22.14s`
- schema-v1 genesis CLI smoke succeeded

The unchanged 152-test Phase 1 suite remains included. Codex was not used.

## Measurement boundary

Physical comparison begins only after the complete checkpoint/repair/retention/rollback semantic graph is independently recaptured and the paired schema-v1/schema-v2-zero projections compare exactly.

The measurement layer never matches artifacts by filename, position, or approximate size. It requires identical typed semantic token sets before byte comparison:

- `CP(g,e)` checkpoint artifacts
- `RA(g,a,s)` pre-rollback archives
- `RC(g,r,s)` source restore candidates
- `TC(g,r)` transformed candidates

Duplicate or missing tokens reject before a physical difference is calculated.

## Real paired scenarios

### Stable water state

Both controls initialize identically and perform one real water wake. The measurement covers:

- active canonical database
- genesis checkpoint `CP(0,2)`
- water checkpoint `CP(0,13)`

### Full retained rollback working set

Both controls then execute the complete protected rollback to genesis while retaining the abandoned future:

- checkpoints `CP(0,2)` and `CP(0,13)`
- archive `RA(0,14,2)`
- source candidate `RC(0,15,2)`
- transformed candidate `TC(1,3)`
- new-lineage active database after rollback completion

Every artifact has already passed its own manifest, digest, size, schema, SQLite, and cross-artifact validation before measurement.

## Accepted caps

The implementation enforces:

- schema-v2-zero active database overhead over paired schema-v1: `0..256 KiB`
- each paired checkpoint/archive/source-candidate/transformed-candidate database overhead: `0..256 KiB`
- aggregate schema-v2-zero additional non-database artifact bytes across the retained set: `0..1 MiB`

Non-database artifact bytes are measured as validated complete artifact bytes minus the validated database file size. This covers the manifest and any other protected regular-file metadata included by the Phase 1 artifact accounting boundary.

Legitimate schema-v2 structure is measured; it is not treated as permission to exceed any absolute runtime ceiling.

## Enforcement evidence

The tests first measure the real files, then lower each declared cap below the measured value:

- active database overhead cap
- per-artifact database overhead cap
- aggregate metadata overhead cap

Each lowered cap rejects the same unchanged real artifact set. The limits are therefore active validation rules, not descriptive assertions written after observing the files.

## Runtime and authority boundaries

This sub-slice adds read-only noncanonical measurement evidence only. It does not change:

- active SQLite schema or canonical state
- checkpoint, repair, retention, rollback, or export runtime
- storage budgets or admission decisions
- organism actions or authority
- any of the 152 Phase 1 tests

## Deferred boundary

After PR #72 is reviewed and merged, remaining Slice 36b2 physical work is P2-O18, P2-O19, P2-O21, and remaining P2-O22 cross-boundary evidence:

1. independent absolute 8 MiB active-database limit
2. independent absolute 8 MiB checkpoint/archive/candidate artifact limit
3. absolute 40 MiB checkpoint-store limit
4. absolute 64 MiB runtime working-set limit
5. exact 1 MiB next-wake reserve
6. real one-below, at, and one-over admission or rejection paths
7. real near-ceiling checkpoint, repair, retention, rollback, and reserve behavior without partial canonical mutation

Paired byte-threshold equality is not required near a physical ceiling. Each side must independently obey the same absolute rules.

Slice 37 remains blocked until every Slice 36 requirement is merged and no blocker, high, or medium boundary defect remains.
