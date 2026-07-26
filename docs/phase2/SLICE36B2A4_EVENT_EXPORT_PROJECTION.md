# Slice 36b2a4: Semantic event-export projection

## Status

Implemented test-first on PR #71. This sub-slice closes ADR 0009 semantic event-export treatment and Phase 2 matrix P2-C16/P2-C17.

It follows merged PR #70 rollback projection. Physical checkpoint/archive/candidate overhead and absolute storage-limit evidence remain outside this sub-slice.

## Test-first evidence

Tests-only head:

`9430b314f925ed09c1e8b9a49b7b21961bcd1e70`

GitHub Actions run 463 failed before implementation because `sudachi_life.phase2_event_export_projection` did not exist.

Implementation head with missing-event and post-capture corruption tests:

`379868664f1724f7c1cd5c2c82e0db09a7dfe960`

GitHub Actions run 465 passed:

- dependency installation succeeded
- source and test compilation succeeded
- protected suite: `196 passed in 22.75s`
- schema-v1 genesis CLI smoke succeeded

The unchanged 152-test Phase 1 suite remains included. Codex was not used.

## Paired scenario

Both controls use identical organism IDs, genesis clocks, input IDs, enqueue clocks, wake seeds, wake clocks, source event boundary, and export operation order.

Each side performs one real water wake and exports through stable checkpoint boundary `13`.

Raw schema-v1 and schema-v2-zero JSONL bytes differ because the export contains raw schema versions and raw checkpoint identities. After independent validation and the exact semantic projection, both exports compare identically.

The projected export contains:

- source checkpoint `CP(0,13)` in the manifest
- prior genesis `checkpoint_stabilized` identity `CP(0,2)` in the event stream
- schema sentinel only at the exact manifest and event schema-version fields
- exact unchanged event range `1..13`, count `13`, order, authority, lifecycle, lineage, clocks, environment version, budget version, and every unlisted payload value

## Independent raw-file validation

The projection reads the published file as a noncanonical artifact and requires:

- a regular non-symlink file
- valid UTF-8
- one canonical JSON object per line
- a terminating newline
- exact manifest key set
- exact event-record key set
- manifest first, followed only by event records
- exact organism identity
- first sequence `1`
- contiguous sequence order through the source boundary
- exact manifest range and count
- exact export format and format version

It then invokes the existing protected Phase 1 export reconstruction for the declared boundary. That reconstruction independently validates active canonical state, source checkpoint registry, immutable source checkpoint artifact, versions, lineage, digests, size, and complete canonical event history.

The published bytes must equal the independently reconstructed bytes byte-for-byte before any semantic replacement occurs.

## Source checkpoint linkage

The raw manifest `source_checkpoint_id`, lineage generation, and last event sequence must resolve to exactly one checkpoint artifact in the cumulative validated projection evidence and to one active registry boundary.

Only after those checks does `source_checkpoint_id` become its exact `CP(g,e)` token.

## Event semantic projection

The export records are not normalized through a generic JSON walk.

The implementation obtains the already validated active projection from the complete checkpoint/repair/retention/rollback evidence graph, finds each event by its exact sequence, and replaces only:

- event `payload` with the exact protected projected payload for that event type and path
- event `schema_version` with `<schema-version>`

All other exported event fields must equal the projected canonical event row exactly.

This reuses the accepted closed event map, including exact checkpoint, repair, retention, and rollback rules where those events are present in an eligible export boundary.

## Noncanonical presentation exclusions

The following are not cross-run canonical equality fields:

- filesystem path
- raw file bytes
- raw file SHA-256
- raw file size
- API result wrapper presentation

They are excluded only after each side independently validates and recomputes them.

A byte-identical copy at a different presentation path produces the same semantic projection. The copied file is still revalidated completely.

## Protected negative evidence

The tests reject:

- a canonical-looking event payload changed from canonical SQLite history
- a noncanonical JSON line with extra whitespace
- a missing event record
- a file changed after evidence capture but before projection

Projection re-reads and revalidates the physical file at use time. A stale evidence object cannot authorize changed export bytes.

## Runtime and authority boundaries

This sub-slice adds noncanonical validation and comparison evidence only. It does not change:

- Phase 1 export generation or publication
- canonical SQLite state
- checkpoint, repair, retention, or rollback runtime
- organism action or authority surfaces
- any of the 152 Phase 1 tests

## Deferred boundary

After PR #71 is reviewed and merged, remaining Slice 36b2 work is physical closure:

1. schema-v2-zero checkpoint/archive/candidate database overhead, each at most 256 KiB over the paired schema-v1 artifact
2. aggregate additional manifest/directory metadata, at most 1 MiB across the retained working set
3. independent absolute 8 MiB active-database and artifact limits
4. independent absolute 40 MiB checkpoint-store limit
5. independent absolute 64 MiB runtime working-set limit
6. exact 1 MiB next-wake reserve scenarios
7. real near-ceiling checkpoint, repair, retention, rollback, and reserve behavior without partial canonical mutation

Slice 37 remains blocked until every Slice 36 requirement is merged and no blocker, high, or medium boundary defect remains.
