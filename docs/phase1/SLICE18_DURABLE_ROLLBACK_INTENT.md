# Phase 1 Slice 18: Durable Rollback Intent

Status: **implemented and verified in PR #32**

Tracked by: Issue #13

## Scope

This slice durably adopts one verified pre-rollback archive as the active rollback intent. It stops before restore-candidate construction, lineage mutation, or active-database replacement.

The boundary is available through:

- Python API `begin_rollback(runtime_root, organism_id, archive_id)`
- CLI `sudachi rollback begin <organism_id> --archive-id <ID>`

It is explicit offline administration, not a normal wake or organism action.

## Fail-fast administrative ownership

Rollback begin opens the active SQLite database through a fresh writable connection and attempts `BEGIN IMMEDIATE` with the protected zero-wait policy.

No mutable active state is used for rollback selection before ownership succeeds. A competing writer produces typed `RollbackBeginBusyError`; the attempt is not queued, reads no clock, and changes no canonical or non-canonical artifact.

## Published archive validation

The caller supplies one archive identifier in the protected deterministic `pre-rb-...` format.

Before canonical mutation, rollback begin validates:

- the archive root and exact archive directory
- absence of symlinks or unexpected entries
- archive manifest format, publication status, and provenance
- archive database filename, size, and SHA-256
- archive SQLite integrity and foreign keys
- archive canonical contract, schema, environment, and budget configuration
- archived organism identity, lineage, lifecycle, status, active event boundary, and latest-stable references
- archived selected-checkpoint registry metadata
- current existence and full validation of the immutable selected checkpoint artifact

A missing, unsafe, foreign, corrupt, or selected-source-mismatched archive is rejected before a clock read or canonical mutation.

## Exact active-body equality

SQLite Online Backup produces a complete logical database snapshot but does not promise that the active file and backup artifact have identical raw file bytes. Slice 18 therefore does not compare the active file's raw SHA-256 to the backup artifact SHA-256.

Instead it:

1. validates the archive database's own recorded size and SHA-256
2. opens both active and archived SQLite databases under fail-fast active ownership
3. compares `PRAGMA user_version`
4. compares protected schema objects in deterministic order
5. compares every canonical table row in primary-key order
6. compares `sqlite_sequence` AUTOINCREMENT state
7. separately compares the manifest's organism, lineage, lifecycle, status, event, latest-stable, and version fields

Any difference is active drift and rejects rollback begin. This covers queued input, event history, registry, counters, environment, policy definitions, protected configuration, and future event-sequence behavior.

## Atomic durable intent

Only after archive, active body, latest stable checkpoint, and selected source all validate does rollback begin consume one injected administrative wall-clock reading.

One SQLite transaction then:

1. changes active status from `sleeping` or `maintenance_required` to `rollback_in_progress`
2. appends exactly one next-sequence `rollback_started` event
3. validates canonical state with no pending checkpoint
4. commits both facts together

The event source is `administration:rollback`. Its payload records:

- archive identifier, manifest SHA-256, and archive database SHA-256
- exact pre-rollback status, lineage, lifecycle, and event boundary
- latest-stable checkpoint identity and boundary
- selected checkpoint identity, lineage, boundary, manifest SHA-256, and database SHA-256

No absolute filesystem path is written into canonical history.

## Failure atomicity

A protected test-only injection occurs after the status update and `rollback_started` insertion but before validation and commit.

On this failure:

- status remains the original stable status
- no `rollback_started` event remains
- active database bytes and digest are unchanged
- archive and checkpoint artifacts are unchanged
- environment, inbox, registry, lineage, lifecycle, and event history are unchanged
- normal wake ownership remains available

This proves the status transition and audit event are one atomic fact.

## Wake blocking and repeated begin

After a successful begin, normal wake acquisition rejects `rollback_in_progress` before any clock read, input claim, event creation, or environment mutation.

A repeated begin for the same archive is rejected without a second event. A begin naming a different archive while rollback is active is also rejected without mutation.

## Protected tests

`tests/test_rollback_intent.py` proves:

- successful Python API adoption
- narrow CLI adoption
- one-clock success after complete validation
- exact `rollback_started` payload and next event sequence
- preservation of environment, inbox, registry, checkpoints, archive, lineage, and lifecycle
- zero-clock normal-wake rejection after begin
- active-state drift rejection
- foreign-archive rejection
- selected-checkpoint artifact drift rejection
- fail-fast competing-writer rejection
- pending-checkpoint rejection
- post-event injected failure rollback
- same-archive and incompatible repeated-begin rejection

GitHub Actions on Python 3.12 completed clean editable installation, compileall, genesis CLI smoke, and **72 protected tests**.

## Deliberately out of scope

- restore-candidate creation
- candidate database mutation
- lineage-generation increment
- active database replacement
- rollback completion history
- final abandoned-future linkage from the restored lineage
- checkpoint, archive, or candidate pruning
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

## Exact next slice

Slice 19 should implement only protected restore-candidate construction from the selected immutable checkpoint while the active body remains in `rollback_in_progress`.

It must revalidate the durable `rollback_started` intent, archive, selected source, and current blocked active state; restore the selected checkpoint into a bounded same-filesystem temporary candidate through SQLite's Online Backup API; validate candidate integrity, protected versions, organism identity, source lineage, source lifecycle, source event boundary, and exact checkpoint contents; and prove failure leaves the active body, durable intent, archive, source checkpoint, and all existing history unchanged.

It must stop before administratively changing the candidate lineage, appending restored-lineage history, replacing the active database, incrementing lineage generation, or completing rollback.
