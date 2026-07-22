# Phase 1 Slice 17: Rollback Source Validation and Pre-Rollback Archive

Status: **implemented and verified in PR #31**

Tracked by: Issue #13

## Scope

This slice adds the first offline rollback foundation accepted by ADR 0004. It stops before active-database replacement or lineage mutation.

The boundary is available through:

- Python API `prepare_rollback_archive(runtime_root, organism_id, source_event_sequence)`
- CLI `sudachi rollback prepare <organism_id> --event-sequence <N>`

It is explicit administration, not an organism action or normal wake.

## Fail-fast administrative ownership

Preparation opens the active database with a fresh writable connection and attempts `BEGIN IMMEDIATE` with the existing zero-wait SQLite policy.

The transaction is used only to prevent any normal wake or competing writer from advancing the active organism while source validation and snapshot creation occur. No canonical row is changed. The transaction is rolled back before the operation returns.

A competing writer produces typed `RollbackPreparationBusyError`. The attempt is not queued and creates no archive artifact.

## Stable active-state requirement

Preparation requires:

- a valid canonical active SQLite database
- no pending checkpoint
- status `sleeping` or `maintenance_required`
- a protected latest-stable registry row matching the active lineage and latest stable event boundary
- complete current event history through the active maximum event sequence

`checkpoint_pending`, `rollback_in_progress`, quarantined, missing, or otherwise invalid active states are rejected before publication.

## Selected rollback source

The caller supplies one positive canonical event sequence.

Exactly one protected retained `checkpoint_registry` row must exist at that boundary. This intentionally distinguishes:

- a retained stable checkpoint
- a pruned or missing checkpoint
- an ambiguous duplicate boundary
- a foreign or mismatched artifact

The selected checkpoint must:

- belong to the active lineage
- not be newer than the active latest-stable boundary
- have exactly `organism.sqlite3` and `manifest.json`
- pass existing checkpoint integrity and foreign-key validation
- match organism identity, lineage, lifecycle boundary, contract, schema, environment, budget configuration, database size, database digest, and manifest digest

No source checkpoint is copied, changed, registered, deleted, or pruned.

## Complete active-state archive

After source validation, the implementation creates a complete snapshot of the current active SQLite body, not merely the selected rollback checkpoint.

The selected checkpoint describes the intended restoration source. The pre-rollback archive preserves the abandoned active future that would otherwise be lost by a later replacement.

The implementation:

1. keeps fail-fast administrative ownership on the active database
2. opens a separate read-only snapshot connection
3. uses Python `sqlite3.Connection.backup()` to a temporary destination database
4. validates full SQLite integrity, foreign keys, protected canonical state, active status, active event boundary, latest-stable references, and selected-source registry metadata
5. computes exact database size and SHA-256
6. writes a deterministic canonical manifest
7. fsyncs the database, manifest, and temporary directory where supported
8. atomically renames the temporary directory to its final same-filesystem name
9. validates the published archive again
10. rolls back and closes the administrative ownership transaction

## Archive representation

Published archives live outside the checkpoint registry:

```text
rollback-archives/
  pre-rb-g<active-generation>-e<active-boundary>-to-e<source-boundary>-<digest>/
    organism.sqlite3
    manifest.json
```

The manifest records:

- rollback archive format version
- archive identifier
- organism identifier
- active lineage, lifecycle, status, and event boundary
- active latest-stable checkpoint identity and boundary
- selected rollback checkpoint identity, lineage, event boundary, provenance, digests, and bytes
- contract, schema, environment, and budget configuration versions
- archive database digest and bytes
- snapshot method, implementation version, publication status, and `pre_rollback` provenance

The archive is immutable and non-canonical. It is not a stable lifecycle checkpoint and does not participate in ordinary checkpoint retention.

## Bounded publication

The predicted active database, checkpoint store, existing rollback archives, and temporary archive must fit the protected runtime working-set limit before snapshot creation.

The archive database must fit the protected checkpoint-artifact byte limit.

A protected test-only failure injection occurs after the temporary snapshot and manifest validate but before atomic publication. On this failure:

- no final archive exists
- no temporary artifact remains
- active SQLite bytes and digest are unchanged
- canonical events, inbox, registry, status, lineage, and checkpoint artifacts are unchanged
- a later normal wake can still acquire ownership

## Idempotent exact preparation

The archive identifier is derived from active lineage, active event boundary, selected source boundary, and active database digest.

Repeating preparation against the exact same active body and selected source validates and returns the existing archive rather than replacing it with divergent content.

## Protected tests

`tests/test_rollback_preparation.py` and `tests/test_rollback_foreign_source.py` prove:

- exact successful source selection and archive manifest
- complete active snapshot contents
- Python API and narrow CLI behavior
- unchanged canonical database, status, events, inbox, registry, and checkpoints
- preserved normal wakeability
- missing or pruned source rejection
- ambiguous duplicate-boundary rejection
- foreign-organism checkpoint rejection
- unsafe checkpoint-directory rejection
- fail-fast competing-writer rejection
- pending-checkpoint rejection
- injected post-snapshot failure cleanup and canonical-state preservation

GitHub Actions on Python 3.12 completed clean editable installation, compileall, genesis CLI smoke, and **63 protected tests**.

## Deliberately out of scope

- persistent `rollback_in_progress` adoption
- active database replacement
- candidate database lineage transformation
- lineage-generation increment
- rollback-completed canonical events
- final abandoned-future linkage from the restored branch
- checkpoint or archive pruning
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

## Exact next slice

Slice 18 should atomically adopt one existing verified pre-rollback archive as a durable rollback intent.

It must revalidate that the active database still exactly matches the archive's recorded digest, lineage, lifecycle, status, event boundary, latest-stable references, and selected checkpoint. It should then enter protected `rollback_in_progress` state and record a typed administrative rollback-start fact atomically, blocking normal wakes.

It must stop before copying or transforming the selected checkpoint candidate, replacing the active database, incrementing lineage generation, or completing rollback.
