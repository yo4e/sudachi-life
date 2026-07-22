# Phase 1 Slice 19: Verified Restore-Candidate Construction

Status: **implemented and verified in PR #33**

Tracked by: Issue #13

## Scope

This slice constructs one isolated restore candidate from the selected immutable checkpoint named by the durable rollback intent. It stops before candidate lineage transformation, active-database replacement, or rollback completion.

The boundary is available through:

- Python API `build_restore_candidate(runtime_root, organism_id)`
- CLI `sudachi rollback build-candidate <organism_id>`

It is explicit offline administration, not a normal wake or organism action.

## Fail-fast administrative ownership

Candidate construction opens the active SQLite database with a fresh writable connection and attempts `BEGIN IMMEDIATE` under the protected zero-wait policy.

The transaction prevents any competing writer from changing the blocked active body while intent, archive, source checkpoint, and candidate metadata are validated. Candidate construction changes no canonical row and rolls the ownership transaction back before returning.

A competing writer produces typed `RestoreCandidateBusyError`. The attempt is not queued and creates no candidate artifact.

## Durable intent validation

Candidate construction requires:

- canonical status `rollback_in_progress`
- no pending checkpoint
- one current-lineage `rollback_started` event at the active event tip
- the event to be the exact successor of the archived abandoned-future boundary
- exact protected event source, lineage, lifecycle, schema, environment, and budget versions
- the protected rollback-start payload shape

The payload must match the active organism identity, lineage, lifecycle, latest-stable checkpoint, and latest-stable boundary.

## Archive and blocked-active validation

The referenced pre-rollback archive is fully revalidated before candidate creation:

- exact directory shape with no symlinks or unexpected entries
- manifest format, publication status, and provenance
- archive database size and SHA-256
- SQLite integrity, foreign keys, protected configuration, identity, lineage, lifecycle, event boundary, and selected-source registry metadata
- manifest digest and database digest recorded by `rollback_started`

The current blocked active body must still be exactly the archived abandoned future plus only the deliberate Slice 18 transition:

- organism status changes from the archived stable status to `rollback_in_progress`
- one exact `rollback_started` row is appended at the tip
- the event AUTOINCREMENT sequence advances by one

`PRAGMA user_version`, protected schema, every other canonical table row, every prior event, and every other `sqlite_sequence` entry must remain identical.

## Selected source validation

The selected source must still be exactly one protected retained checkpoint in the active lineage. Its registry row, manifest, directory identity, database size, database SHA-256, manifest SHA-256, provenance, protected versions, source lifecycle, pending boundary, and SQLite integrity are revalidated.

Missing, foreign, drifted, unsafe, ambiguous, busy, or inconsistent intent is rejected before candidate creation.

## Candidate construction and validation

The selected checkpoint database is opened read-only and restored through Python `sqlite3.Connection.backup()` into a bounded temporary directory under `restore-candidates/`.

Naive live-file copy is not used.

Before publication, the temporary candidate must pass:

- candidate database size and SHA-256 validation
- full SQLite integrity check
- foreign-key check
- protected canonical-state validation with the source checkpoint still pending
- exact organism identity, source lineage, source lifecycle, contract, schema, environment, and budget configuration
- exact source event boundary and pending-checkpoint boundary
- exact equality with the selected checkpoint for `user_version`, protected schema, every canonical table row, and `sqlite_sequence`

SQLite Online Backup is treated as a complete logical snapshot, not as a promise of raw-file-byte equality.

## Candidate representation

Published candidates live outside the active database, checkpoint registry, and rollback archive store:

```text
restore-candidates/
  rc-g<active-generation>-rb-e<rollback-start>-from-e<source-boundary>-<source-digest>/
    organism.sqlite3
    manifest.json
```

The manifest records:

- restore-candidate format version and deterministic candidate identifier
- organism and active lineage identity
- rollback-start event sequence
- archive identifier and archive digests
- selected checkpoint identity
- source lineage, lifecycle, event boundary, provenance, database size, and digests
- protected contract, schema, environment, and budget versions
- candidate database size and SHA-256
- snapshot method, implementation version, publication status, and `source_restored_untransformed` state

The candidate is non-canonical and is never read or written by normal organism runtime.

## Bounded atomic publication

The active database, checkpoint store, rollback archives, existing candidates, and temporary candidate must fit the protected runtime working-set limit before snapshot creation.

The candidate database must fit the protected checkpoint-artifact byte limit.

The implementation writes the candidate database and canonical manifest into a same-filesystem temporary directory, validates them, fsyncs files and directories where supported, and atomically renames the directory only after validation.

Repeating the command against the same durable intent validates and returns the existing deterministic candidate.

## Failure preservation

Protected tests inject failure:

- after temporary candidate validation and before publication
- during atomic publication

On either failure:

- no final candidate exists
- no temporary candidate remains
- active status remains `rollback_in_progress`
- the single `rollback_started` event remains unchanged
- active SQLite bytes and digest remain unchanged
- the abandoned-future archive remains unchanged
- the selected checkpoint remains unchanged
- lineage, lifecycle, environment, inbox, registry, and all prior history remain unchanged

A corrupted existing candidate is rejected rather than silently replaced.

## Protected tests

`tests/test_rollback_candidate.py` proves:

- successful Python API construction
- narrow CLI construction
- exact candidate manifest and deterministic identifier
- exact logical equality with the selected checkpoint
- idempotent repeated construction
- unchanged blocked active body on success
- rejection without durable rollback intent
- missing archive rejection
- non-intent active-tip rejection
- selected-checkpoint drift rejection
- fail-fast competing-writer rejection
- injected pre-publication failure cleanup
- atomic publication failure cleanup
- corrupted existing-candidate rejection

GitHub Actions on Python 3.12 completed clean editable installation, compileall, genesis CLI smoke, and **81 protected tests**.

## Deliberately out of scope

- candidate lineage-generation change
- candidate administrative restoration history
- candidate transition out of the source checkpoint-pending state
- active database replacement
- clearing active `rollback_in_progress`
- rollback-completed history
- final abandoned-future linkage from the restored lineage
- checkpoint, archive, or candidate pruning
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

## Exact next slice

Slice 20 should implement only administrative transformation of one verified source-restored candidate into a fully validated new-lineage replacement candidate.

It must revalidate the blocked active intent, archive, source-restored candidate, and selected checkpoint; derive the new lineage generation from the abandoned active generation; update only the isolated candidate through one bounded administrative transaction; record the target and abandoned boundaries in candidate-local rollback restoration history; clear source checkpoint-pending fields in the transformed candidate; and validate the transformed candidate completely.

It must stop before replacing the active database, clearing the active body's `rollback_in_progress`, deleting any artifact, or recording rollback completion in the active path.
