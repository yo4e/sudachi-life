# Slice 36b2a1: Pending-checkpoint repair evidence

## Status

Implemented test-first on PR #67. This sub-slice extends the merged Slice 36b1 checkpoint core through the exact `checkpoint_registration_repaired` projection paths accepted by ADR 0009.

Retention, rollback, event export, and remaining physical closure are not included here.

## Matrix scope

Primary evidence:

- P2-C03 exact repair projection locations
- P2-C08 paired schema-v1/schema-v2-zero repair semantics
- P2-C11 current/previous checkpoint identity and SHA/size/store-byte validation
- P2-C14 integrity before omission
- P2-C18 wrong identity/location rejection
- repair-relevant P2-O20 corruption rejection

## Test-first evidence

Tests-only head:

`53c3d4c1795c54d5872c113a0aa2e65653c9b412`

GitHub Actions run 435 failed because the merged 36b1 core did not expose the repair evidence API:

```text
ImportError: cannot import name 'BYTE_DERIVED_SENTINEL'
```

The red result preceded the implementation commit.

Implementation head before durable-note synchronization:

`18c97c130be81f7d72c17a49d02c15fa3a5f9a58`

GitHub Actions run 436:

- dependency installation succeeded
- source and test compilation succeeded
- protected suite: `178 passed in 12.95s`
- schema-v1 genesis CLI smoke succeeded

The 178 tests are the unchanged 152 Phase 1 tests, 23 merged Slice 36a/36b1 tests, and 3 pending-repair evidence tests.

## Cumulative immutable evidence

`phase2_projection` now defines frozen evidence records for:

- checkpoint artifact identity, manifest/database digest, database size, measured artifact size, canonical manifest, and projected internal Phase 1 state
- canonical event raw payload and its exact validated semantic projection
- the ordered current retained checkpoint boundary set

`capture_zero_caregiver_evidence(paths, previous=...)` merges only identical immutable evidence. A previously captured checkpoint or event cannot silently change. The evidence is per-run and bound to the declared organism identity.

The ledger is required because later retention and rollback may remove or replace artifacts after their byte-derived fields have already been validated. It records validated operation-boundary evidence; it does not create canonical organism state, grant authority, or relax any physical limit.

## Repair projection

For `checkpoint_registration_repaired`, capture requires the exact protected payload key set and independently validates:

- repaired raw `checkpoint_id` against the artifact at `CP(payload.lineage_generation, payload.event_sequence)`
- prior raw checkpoint ID against `CP(payload.lineage_generation, payload.previous_latest_stable_event_sequence)`, with the exact null/zero genesis rule
- `database_sha256` against the repaired database artifact
- `manifest_sha256` against canonical manifest bytes
- `database_size_bytes` against the actual database file length
- `checkpoint_store_bytes` against the measured current checkpoint store

Only after all checks pass are the two checkpoint identities replaced with typed `CP` tokens and the four byte-derived values replaced with `<validated-byte-derived>`.

The canonical event row, event type, source, sequence, lineage, lifecycle, and every unlisted payload field remain exact.

## Paired protected scenario

Both controls use identical:

- organism ID
- genesis clock
- input ID and enqueue clock
- wake seed and timeout clock readings
- repair clock
- operation order and fault choice

Each run independently publishes a pending orphan, enters `checkpoint_pending`, performs the narrow administrative repair, captures its own artifact/event evidence, and then compares after projection.

The pair proves:

- repaired current boundary maps to `CP(0,13)`
- previous stable boundary maps to `CP(0,2)`
- raw schema-v1/schema-v2 digests, sizes, and IDs may differ
- status, lifecycle, event order, authority source, repair reason, and all nonprojected values remain exact

## Adversarial evidence

Protected tests reject:

- a one-byte discrepancy in `checkpoint_store_bytes`
- a repair event linked to the wrong raw checkpoint ID
- any changed raw event payload after evidence capture
- conflicting checkpoint evidence for the same semantic boundary

## Deferred boundary

The next sub-slice must extend the same cumulative ledger through:

- `checkpoint_pruned`
- pre-commit retention failure
- post-commit cleanup failure and `STAGE(CP(g,e))`
- pending reconciliation, interruption after deletion, and retry completion

It must capture prunable artifact evidence before deletion and validate later events against that prior immutable witness. It may not infer deleted artifact bytes from an ID pattern or normalize values by key name.

Rollback, event export, and remaining physical budget evidence follow after retention closure. Slice 37 remains blocked until all Slice 36 evidence is merged.
