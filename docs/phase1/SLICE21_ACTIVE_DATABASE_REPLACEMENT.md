# Phase 1 Slice 21: Protected Active-Database Replacement

Status: **implemented and verified in PR #35**

Tracked by: Issue #13

## Scope

This slice transfers canonical SQLite authority from the blocked abandoned active body to one fully verified `lineage_transformed_replacement_ready` candidate. It immediately validates the replacement and stops while the new active body is still `rollback_in_progress`.

The boundary is available through:

- Python API `replace_active_with_candidate(runtime_root, organism_id, transformed_candidate_id, ...)`
- CLI `sudachi rollback replace-active <organism_id> --candidate-id <ID>`

It is explicit offline administration, not a normal wake or organism action.

## Pre-replacement ownership and validation

The operation opens the old active database with a fresh writable connection and attempts fail-fast `BEGIN IMMEDIATE` before mutable reads.

Before crossing the filesystem authority boundary it requires and revalidates:

- canonical status `rollback_in_progress`
- no pending checkpoint
- the exact abandoned-lineage `rollback_started` event at the active tip
- the complete durable rollback-start payload
- the immutable pre-rollback archive and abandoned-future boundary
- exact blocked-active equality with that archive plus only the deliberate rollback-start transition
- the selected protected checkpoint registry row, manifest, database, integrity, and boundary
- the source-restored candidate and exact source-checkpoint equality
- the lineage-transformed candidate, its deterministic manifest, `abandoned_active_generation + 1` derivation, candidate-local restoration event, selected registry reconstruction, and replacement-ready state

Missing, foreign, drifted, unsafe, ambiguous, busy, or inconsistent state is rejected before authority transfer.

## Replacement staging

The transformed candidate artifact remains immutable. Its database is opened read-only and copied with Python `sqlite3.Connection.backup()` into one bounded temporary SQLite file in the organism directory.

The temporary replacement database must pass:

- full SQLite integrity check
- foreign-key check
- canonical-state validation with no pending checkpoint
- exact logical equality with the transformed candidate for `user_version`, schema, every canonical row, and `sqlite_sequence`

The complete runtime plus the temporary replacement must fit the protected runtime working-set limit.

The staged file is fsynced where supported before replacement.

## Closing the old active body

SQLite handles on the old active database are closed before filesystem replacement.

Immediately after closing, the operation rechecks the old active file size and SHA-256 and rechecks both transformed-candidate files. Any drift aborts before replacement and removes the temporary file.

The offline-administration rule remains normative: ordinary wakes already reject `rollback_in_progress`, and no separate rollback administrator may race this authority-transfer boundary.

## Atomic authority transfer

The staged SQLite file and active database are on the same filesystem. One `os.replace()` atomically moves the staged database to the canonical `organism.sqlite3` path.

The operation does not naively copy the live old database. The mandatory pre-rollback archive remains the immutable authoritative record of the abandoned future.

The source-restored candidate and lineage-transformed candidate remain unchanged and available for audit and recovery.

## Immediate post-replacement validation

After atomic replacement, the operation reopens the new active database, acquires fail-fast write ownership, and validates:

- SQLite integrity and foreign keys
- protected canonical state with no pending checkpoint
- organism identity and protected versions
- new lineage generation
- source lifecycle number
- selected stable checkpoint and boundary
- non-wakeable status `rollback_in_progress`
- candidate-local `rollback_lineage_prepared` at the active tip
- complete immutable checkpoint, source-candidate, archive, and transformed-candidate provenance chain
- exact logical equality between the active database and transformed-candidate database

A successful replacement creates no new event. `rollback_lineage_prepared` remains the active tip.

## Failure classes

Slice 21 distinguishes authority-transfer state explicitly.

### Failure before replacement

`ActiveReplacementError` or `ActiveReplacementRejectedError` means canonical authority never moved.

Protected failure injection before `os.replace()` and an injected `os.replace()` failure prove:

- the old active database remains byte-for-byte unchanged
- the old body remains `rollback_in_progress` with `rollback_started` at the tip
- no replacement temporary file remains
- all checkpoint, archive, and candidate artifacts remain unchanged

### Interruption after replacement

`ActiveReplacementIncompleteError` means the new database reached the canonical active path but post-replacement validation did not complete.

The new body is already a valid transformed candidate and remains non-wakeable in `rollback_in_progress`. No rollback-completion claim is made.

Repeating the same command recognizes the exact replacement state, revalidates the complete provenance chain and active-candidate equality, and returns a successful result with `recovered_existing_replacement=true` without rewriting the database.

An incompatible or drifted post-replacement body is rejected rather than treated as recovered.

## Idempotence

After successful replacement, repeating the exact command is a read-only validation operation. It changes no active row, event, counter, artifact, or file digest.

This exact-state recovery behavior covers both ordinary repeated administration and interruption immediately after authority transfer.

## Wake boundary

The replaced active database deliberately remains `rollback_in_progress`.

Normal wakes continue to reject before clock use or inbox claim. Slice 21 does not append `rollback_completed`, clear maintenance, or claim that rollback is finished.

## Protected tests

`tests/test_rollback_replace.py` proves:

- successful Python API authority transfer
- CLI exact-state recovery
- exact active-versus-transformed-candidate logical equality
- new-lineage, selected-stable, and restoration-tip validation
- preserved checkpoint, archive, source-candidate, and transformed-candidate artifacts
- normal-wake rejection after replacement
- rejection without prepared rollback state
- missing or drifted transformed-candidate rejection
- drifted source-candidate rejection
- fail-fast competing-writer rejection
- injected pre-transfer failure cleanup
- injected atomic-replace failure cleanup
- recoverable post-transfer interruption
- read-only exact repeated replacement
- rejection of drifted post-replacement active history

GitHub Actions on Python 3.12 completed clean editable installation, compileall, genesis CLI smoke, and **107 protected tests** on the implementation head.

The first PR run failed during collection because the new module imported `checkpoint` rather than the existing canonical `checkpoints` module. No protected behavior ran in that attempt. The import was corrected without weakening the design or tests, and the subsequent run passed all 107 tests.

## Deliberately out of scope

- active-path `rollback_completed`
- clearing `rollback_in_progress`
- normal-wake enablement
- first post-rollback stable checkpoint
- checkpoint, archive, or candidate deletion or pruning
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

## Exact next slice

Slice 22 should implement only rollback completion on the already replaced and fully revalidated active body.

It must acquire fail-fast active ownership, revalidate the complete replacement provenance chain, require `rollback_lineage_prepared` at the new-lineage tip, read one injected administrative clock only after validation, and atomically append one `rollback_completed` event while clearing `rollback_in_progress` to the correct stable wakeable state.

The completion payload must bind the administrative reason, selected target boundary, abandoned archive and boundary, source and transformed candidate identifiers and digests, old and new lineage generations, replacement validation, and implementation version.

Failure before commit must leave the replaced body blocked and unchanged. A repeated exact completion request must be detectable and idempotent. Slice 22 must prove normal wakeability only after the completion transaction and must not delete or prune any rollback artifact.
