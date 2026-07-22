# Phase 1 Slice 20: Candidate Lineage Transformation

Status: **implemented and verified in PR #34**

Tracked by: Issue #13

## Scope

This slice transforms one verified `source_restored_untransformed` candidate into one isolated, fully validated new-lineage replacement candidate. It stops before active-database replacement or rollback completion.

The boundary is available through:

- Python API `transform_restore_candidate(runtime_root, organism_id, source_candidate_id, administrative_reason, ...)`
- CLI `sudachi rollback transform-candidate <organism_id> --candidate-id <ID> --reason <TEXT>`

It is explicit offline administration, not a normal wake or organism action.

## Fail-fast active ownership

Transformation opens the blocked active SQLite database with a fresh writable connection and attempts `BEGIN IMMEDIATE` under the protected zero-wait policy before reading mutable rollback state.

The active transaction provides one stable validation window for the rollback intent, abandoned future, selected source, source-restored candidate, and transformed publication. It changes no active row and is rolled back before return.

A competing writer produces typed `CandidateTransformBusyError`. The attempt is not queued and reads no clock.

## Administrative reason

ADR 0004 requires rollback lineage preparation to carry an administrative reason. Slice 20 accepts one explicit reason and rejects it before active access when it is:

- empty
- surrounded by whitespace
- longer than 256 characters
- contains control characters

The accepted reason is bound into both the transformed manifest and candidate-local restoration event.

## Input revalidation

Before reading the administrative clock or creating a working copy, transformation revalidates:

- canonical active status `rollback_in_progress`
- no active pending checkpoint
- the exact current-lineage `rollback_started` event at the active tip
- the protected rollback-start payload
- the complete abandoned-future archive and its digests
- exact blocked-active equality with that archive plus only the Slice 18 transition
- the selected protected checkpoint registry row
- the immutable selected checkpoint manifest and database
- the exact published source-restored candidate directory, manifest, database, identity, versions, source lineage, lifecycle, pending boundary, and source-checkpoint equality

Missing, foreign, drifted, unsafe, busy, already transformed, or inconsistent input is rejected before candidate mutation or publication.

## New lineage derivation

The new generation is derived exactly as required by ADR 0004:

```text
new_lineage_generation = abandoned_active_generation + 1
```

It is not derived from the selected checkpoint generation.

The selected checkpoint, pre-rollback archive, and published source-restored candidate are never edited.

## Isolated working transformation

The immutable source-restored candidate is copied through Python `sqlite3.Connection.backup()` into a bounded same-filesystem temporary directory under `restore-candidates/`.

Only the temporary working database is mutated. One bounded SQLite administrative transaction:

1. verifies that the source checkpoint registry row is absent from the checkpoint snapshot, as expected before registration
2. changes the organism lineage generation to the new generation
3. keeps status `rollback_in_progress`
4. clears `checkpoint_pending`, `pending_checkpoint_generation`, and `pending_checkpoint_event_sequence`
5. restores the selected protected checkpoint registry row from the blocked active database
6. sets the selected checkpoint and boundary as latest stable
7. appends exactly one next-sequence `rollback_lineage_prepared` event from `administration:rollback-candidate`
8. validates the canonical candidate and commits

The source lifecycle number, organism identity, environment state, inventory, garden, inbox, actions, failure state, timestamps, protected configuration, and all pre-target history remain unchanged.

## Candidate-local restoration fact

The appended event is the first event in the new lineage generation. Earlier restored events remain unchanged and retain their original lineage values.

Its payload records:

- explicit administrative reason
- new and abandoned lineage generations
- abandoned lifecycle and event boundary
- rollback-start event boundary
- archive identifier and archive digests
- selected checkpoint identifier, lineage, boundary, and digests
- source-restored candidate identifier and digests
- protected non-wakeable status after transformation

This event is candidate-local. Slice 20 does not append `rollback_completed` and does not write any event to the blocked active body.

## Validation

Before publication, the transformed candidate must pass:

- database size and SHA-256 validation
- full SQLite integrity check
- foreign-key check
- protected canonical-state validation with no pending checkpoint
- exact organism identity, protected versions, source lifecycle, new lineage, selected stable boundary, and non-wakeable status
- exact source schema and `user_version`
- exact equality for every canonical table except the three explicitly transformed tables: `organism`, `event`, and `checkpoint_registry`
- exact declared organism-column differences only
- byte-for-byte row preservation of all source history followed by one exact restoration event
- exact registry reconstruction using the selected active registry row
- exact `sqlite_sequence` preservation except one event-sequence increment
- exact agreement between manifest and transformed database

## Candidate representation

Published transformed candidates use a deterministic identifier:

```text
restore-candidates/
  rtc-g<new-generation>-rb-e<rollback-start>-from-e<source-boundary>-<source-manifest-prefix>/
    organism.sqlite3
    manifest.json
```

The manifest state is `lineage_transformed_replacement_ready` and provenance is `rollback_transformed_candidate`.

It records source-candidate, archive, checkpoint, abandoned-future, new-lineage, restoration-event, administrative-reason, wall-time, protected-version, database, and implementation metadata.

The transformed candidate is non-canonical and is never used by normal organism runtime before a later explicit replacement operation.

## Atomic publication and idempotence

The implementation validates and fsyncs the temporary database and canonical manifest, then publishes the directory through same-filesystem atomic rename.

Repeating the exact request revalidates and returns the deterministic existing candidate without reading a clock. A different administrative reason is a different semantic request and is rejected rather than silently reusing or replacing the existing candidate.

A corrupted existing transformed candidate is rejected rather than overwritten.

## Failure preservation

Protected tests inject failure:

- after the candidate-local restoration event is inserted but before the working transaction commits
- after complete temporary candidate validation but before publication
- during atomic publication

On every failure:

- no transformed final candidate is exposed
- no temporary transformed candidate remains
- the blocked active body remains byte-for-byte unchanged
- active status remains `rollback_in_progress`
- active `rollback_started` remains the tip
- the abandoned-future archive remains unchanged
- the selected checkpoint remains unchanged
- the source-restored candidate remains unchanged
- inbox, registry, environment, lineage, lifecycle, and all active history remain unchanged

## Protected tests

`tests/test_rollback_transform.py` proves:

- successful Python API and CLI transformation
- exact new-lineage derivation
- exact candidate-local restoration event and manifest
- source-history preservation
- selected registry reconstruction
- active and immutable-artifact preservation
- no-intent rejection
- missing or drifted source-candidate rejection
- selected-checkpoint drift rejection
- fail-fast competing-writer rejection
- working-transaction rollback after event insertion
- pre-publication and publication-failure cleanup
- deterministic idempotent repeat without a second clock read
- administrative-reason binding
- corrupted existing-candidate rejection
- invalid-reason rejection

GitHub Actions on Python 3.12 completed clean editable installation, compileall, genesis CLI smoke, and **96 protected tests** on the implementation head.

## Deliberately out of scope

- active database replacement
- clearing the active body's `rollback_in_progress`
- active-path `rollback_completed` history
- post-replacement completion or wakeability
- checkpoint, archive, or candidate deletion or pruning
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

## Exact next slice

Slice 21 should implement only protected active-database replacement with the verified transformed candidate and immediate post-replacement validation.

It must revalidate the blocked active intent and every referenced immutable artifact, verify that the transformed candidate remains replacement-ready, preserve the old active database in the verified pre-rollback archive, stage replacement on the same filesystem, atomically replace the active database, reopen and fully validate the new active body, and leave that body in `rollback_in_progress` if replacement succeeds.

It must provide explicit protected recovery semantics for failures around the replacement boundary and stop before appending `rollback_completed`, clearing maintenance, enabling normal wakes, or deleting any artifact.
