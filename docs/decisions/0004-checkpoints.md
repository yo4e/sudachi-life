# ADR 0004: Checkpoints, Recovery, and Rollback Lineage

- **Status:** Accepted
- **Date:** 2026-07-21
- **Issue:** #1
- **Scope:** SUDACHI-0 seed architecture

## Context

SUDACHI must recover from corruption or a bad developmental step without treating a raw file copy as a trustworthy checkpoint.

ADR 0001 establishes one SQLite database per organism as the sole canonical live store. ADR 0002 defines clock metadata and sequence-based ordering. ADR 0003 holds one bounded `BEGIN IMMEDIATE` transaction across a wake and releases it at commit, rollback, or connection close.

A checkpoint system must solve several different problems:

- create a consistent snapshot of the canonical SQLite database
- prove that the snapshot is complete and belongs to the intended organism
- identify the exact event and schema boundary represented
- avoid exposing a partial copy as valid
- prevent another wake from advancing while a required checkpoint is missing
- restore a snapshot without silently destroying the abandoned history
- distinguish a restored branch from the abandoned future
- keep storage bounded

A checkpoint is a recovery artifact. It is not a second live source of truth.

## Decision

### 1. A checkpoint is an immutable directory containing a database snapshot and manifest

Each published checkpoint is one immutable directory inside the organism's allowed checkpoint directory.

It contains at least:

```text
checkpoint/
  organism.sqlite3
  manifest.json
```

The manifest records:

- checkpoint format version
- checkpoint identifier
- organism identifier
- lineage generation
- schema version
- contract version
- canonical event-sequence boundary
- lifecycle or state revision when available
- creation wall timestamp in UTC microseconds
- database filename and byte size
- SHA-256 digest of the database file
- snapshot method and implementation version
- checkpoint status and provenance category

The snapshot database and manifest are immutable after publication.

A checkpoint is not canonical operational state while the active database exists. Only one active SQLite database is authoritative at a time.

### 2. Checkpoints use SQLite's supported backup facilities

Phase 1 creates the snapshot with Python's `sqlite3.Connection.backup()` interface, which uses SQLite's Online Backup API.

It must not create a checkpoint by naively copying a live database file.

For the small Phase 1 database, the backup is copied in one bounded operation to a new temporary destination database. The source must be at a declared committed boundary and protected from further lifecycle advancement by the pending-checkpoint rule below.

`VACUUM INTO` is not the default checkpoint mechanism. It can produce a consistent compact copy, but the Online Backup API has a direct Python interface, uses fewer CPU cycles, and does not rewrite logical row layout merely to create a recovery snapshot.

A future ADR may change the snapshot method after measurement.

### 3. Every initialization and successful wake creates a required stable checkpoint

Initialization and every successful lifecycle transaction set a canonical pending checkpoint boundary before committing.

The transaction stores at least:

- `checkpoint_pending = true`
- pending lineage generation
- pending canonical event-sequence boundary
- pending schema and contract versions

After that transaction commits, no later wake may advance the organism until the pending boundary has a verified published checkpoint and the checkpoint is registered as stable.

This creates a two-stage lifecycle:

```text
lifecycle transaction commits with checkpoint pending
  -> snapshot is created and verified
  -> checkpoint is published atomically
  -> short registration transaction marks it stable
  -> organism may wake again
```

The lifecycle state is durable after the first commit, but it is not eligible for another developmental step until checkpoint stabilization succeeds.

### 4. Checkpoint creation occurs after the wake transaction commits

The SQLite backup is created after ADR 0003's canonical wake transaction commits and releases its write lock.

The checkpoint creator opens a source connection at the pending boundary and a new destination connection for the temporary snapshot.

The pending-checkpoint flag causes any competing wake to acquire the runtime transaction, observe the pending state, return a typed `checkpoint_required` or equivalent result, and roll back without advancing the organism.

Administrative checkpoint repair is allowed to operate while that flag is set.

The checkpoint operation must be bounded. It must not retry forever if a connection or filesystem operation is busy.

### 5. Publication is all-or-nothing at the artifact level

Checkpoint files are first created in a unique temporary directory on the same filesystem as the final checkpoint directory.

Before publication:

1. close the destination database connection
2. run database validation
3. verify organism, schema, contract, lineage, and event-boundary metadata
4. compute the database byte size and SHA-256 digest
5. write a deterministic manifest
6. flush files and directory metadata using the strongest supported local mechanism

The temporary directory is then renamed or replaced into its final unique checkpoint path using an atomic same-filesystem operation supported and tested on the target platform.

A directory that has not reached the final published name is not a checkpoint. Temporary or incomplete artifacts are ignored and may be quarantined or deleted by administration.

The final checkpoint identifier includes stable metadata and a digest component, for example:

```text
cp-g000002-e000000184-7f3a2c1d
```

The exact zero padding and digest-prefix length are implementation details, but identifiers must not depend on local time alone.

### 6. Validation is mandatory before stability

A candidate checkpoint is stable only when all required checks pass.

Phase 1 validation includes:

- SHA-256 digest and file-size match
- SQLite opens successfully in read-only mode
- `PRAGMA integrity_check` returns `ok`
- `PRAGMA foreign_key_check` returns no rows
- organism identifier matches
- lineage generation matches the pending boundary
- schema and contract versions match the manifest
- canonical event boundary exists and no later event exists in the snapshot
- required protected configuration is present
- no pending migration is recorded

Because Phase 1 databases are intentionally small, full `integrity_check` is preferred at checkpoint creation and restore. A future measured optimization may use `quick_check` for routine screening while retaining full validation at declared boundaries.

### 7. Registration is a short canonical transaction

After artifact publication, a fresh `BEGIN IMMEDIATE` transaction verifies that the active database still has the same pending boundary.

If it matches, the transaction:

- registers the checkpoint identifier and manifest digest
- records the stable boundary
- clears the pending-checkpoint flag
- appends a checkpoint-stabilized administrative event or equivalent audit fact

If it does not match, the artifact is not registered against that active state and is treated as orphaned pending investigation.

Checkpoint registration does not recursively require another checkpoint. The stable checkpoint represents the preceding lifecycle boundary; administrative registration metadata can be reconstructed from the immutable manifest if rollback restores the snapshot.

### 8. Checkpoint failure blocks further wakes but does not erase the committed lifecycle

If snapshot creation, validation, publication, or registration fails:

- the active database remains at the committed lifecycle boundary
- the pending-checkpoint flag remains set
- normal wakes are rejected
- the latest earlier stable checkpoint remains available
- an explicit administrative repair command may retry creation or register a valid orphan artifact

The system must not pretend that the failed checkpoint exists, silently clear the flag, or continue accumulating uncheckpointed lifecycle changes.

### 9. Genesis and bounded retention are required

Initialization creates a genesis checkpoint before the organism becomes wakeable.

Phase 1 uses a protected `checkpoint_retention_limit` with a default of **4 stable lifecycle checkpoints**, including genesis while it remains within the retained set.

Retention rules:

- never delete the latest stable checkpoint
- never prune until a newer checkpoint is stable and registered
- retain genesis when possible; if the limit would force its deletion, archive or explicit policy change is required rather than silent removal
- prune oldest eligible stable checkpoints first
- failed pruning does not invalidate the newly stable checkpoint; it produces an explicit maintenance warning
- temporary and orphan artifacts do not count as stable checkpoints and have a separate cleanup policy

A pre-rollback archive described below is protected until at least one new post-rollback stable checkpoint exists. Afterwards it enters the same explicit retention or archival policy.

The default is deliberately small for the seed organism. Changing it is a protected configuration change and must remain measurable as storage cost.

### 10. Rollback is an explicit offline administrative operation

Phase 1 rollback is not an organism action and is not performed concurrently with ordinary wakes.

The operator or controlling test must place the organism into maintenance and ensure no scheduler or wake process is running.

The rollback procedure is:

1. acquire a runtime write transaction on the active database
2. validate the selected stable checkpoint and current active state
3. set protected maintenance state to `rollback_in_progress` and commit
4. create and publish a verified pre-rollback archive of the current active database
5. copy the selected immutable checkpoint into a new temporary candidate database
6. validate the candidate against its manifest
7. modify only the candidate in an administrative transaction to prepare the new lineage
8. close and flush the candidate
9. atomically replace the active database with the candidate on the same filesystem
10. reopen and validate the new active database
11. append rollback-completion audit data and clear maintenance state in a short transaction

If failure occurs before replacement, the existing active database remains in maintenance and the operation can resume or abort explicitly.

If failure occurs after replacement but before completion, the restored candidate remains in maintenance and ordinary wakes reject it until rollback recovery completes.

The pre-rollback archive is mandatory. Rollback may remove events from the active future, but it must not make the abandoned future unauditable.

### 11. Automated recovery defaults to the latest stable checkpoint

A generic `rollback` or automatic corruption-recovery operation selects the latest stable checkpoint whose manifest and database pass validation.

Choosing an older checkpoint requires an explicit administrative checkpoint identifier and a recorded reason.

The system must not choose a checkpoint solely by filename modification time.

### 12. Rollback creates a new lineage generation

Rollback does not claim that abandoned post-checkpoint events never happened.

The active database contains a protected integer `lineage_generation`.

On rollback, the candidate generation becomes:

```text
abandoned_active_generation + 1
```

not merely the target checkpoint's generation plus one.

The rollback transaction records:

- new lineage generation
- selected checkpoint identifier and boundary
- pre-rollback archive identifier and abandoned boundary
- administrative reason
- rollback wall timestamp
- implementation version

Canonical event order within the restored database still uses ADR 0001's integer sequence. Cross-lineage event identity uses organism identifier, lineage generation, and event sequence together.

The selected immutable checkpoint itself is never edited.

### 13. Post-checkpoint history is preserved outside the restored active branch

Events after the selected checkpoint boundary disappear from the restored active database because that is the purpose of rollback.

They remain available in the immutable pre-rollback archive and its manifest.

Research or audit tools may compare active and abandoned branches, but the organism does not merge abandoned events back automatically.

A future branch-merging or memory-salvage mechanism requires a separate design and cannot be smuggled into rollback.

### 14. External mutable filesystem state is not checkpointed in Phase 1

Phase 1 checkpoints cover the canonical SQLite database only.

ADR 0005 must choose a seed environment whose mutable authoritative state fits inside that database or is deterministically regenerated from it.

Exports, logs, and immutable experiment artifacts may live outside the database but are not restored as organism state.

If a future action mutates authoritative external files, that phase requires a new cross-resource checkpoint and adoption design. SQLite checkpoint success must not be misrepresented as atomic recovery of unrelated filesystem effects.

### 15. Checkpoints are not Git commits

Git remains source and developmental lineage for repository-controlled artifacts.

Runtime checkpoint databases are not committed to the source repository by default. They may contain experiment state, private human input, or large binary history.

Published research packages may include selected redacted checkpoints through an explicit export process with provenance and privacy review.

## Consequences

### Positive

- Every developmental step has a declared stable recovery boundary before another wake.
- Partial database copies are never published as valid checkpoints.
- Checkpoint integrity, identity, schema, and event boundary are independently verifiable.
- A failed checkpoint blocks further development rather than creating an unbounded unprotected tail.
- Rollback preserves the abandoned future as an auditable archive.
- Lineage generation distinguishes restored development from the abandoned branch.
- Mutable Phase 1 state remains in one SQLite authority.
- Storage growth is bounded by an explicit protected retention limit.

### Negative

- Every successful wake requires a second backup and registration phase.
- A checkpoint failure can leave the organism alive but intentionally unable to wake until repaired.
- Checkpoint directories and manifests add filesystem operations outside the canonical transaction.
- Rollback is an offline administrative procedure, not a seamless concurrent operation.
- Full integrity checks and per-wake backups may become expensive as the database grows.
- Retaining an abandoned pre-rollback archive increases temporary storage cost.

### Neutral or deferred

- ADR 0005 must keep Phase 1 authoritative environment state compatible with database-only checkpoints.
- ADR 0006 must account for checkpoint storage and maintenance cost in concrete budgets or experiment accounting.
- Contract review must clarify the exact relationship among lifecycle success, pending checkpoint state, and reported outcomes.
- Later phases may reduce checkpoint cadence only through a new measured decision.
- Encryption, remote backup, replication, and confidential checkpoint handling are outside Phase 1.

## Alternatives rejected

### Copy the SQLite file with ordinary filesystem copy

Rejected because a live copy can be incomplete or inconsistent and does not use SQLite's supported snapshot semantics.

### Make JSONL the recovery checkpoint

Rejected because JSONL is non-canonical under ADR 0001 and does not capture the full validated database state, schema, indexes, and constraints.

### Create the checkpoint before committing the lifecycle

Rejected because the snapshot would not contain the state it is intended to protect.

### Allow later wakes while checkpoint creation retries in the background

Rejected because multiple uncheckpointed lifecycle changes could accumulate and make “latest stable” ambiguous.

### Store the only checkpoint inside the active database

Rejected because corruption of the active database would damage both live state and its recovery copy.

### Replace the active database without a pre-rollback archive

Rejected because post-checkpoint events would vanish from all auditable storage and developmental lineage would be falsified.

### Reuse the target checkpoint's lineage generation

Rejected because new post-rollback events could be confused with an abandoned branch that used the same sequence range.

### Commit runtime checkpoint databases to Git automatically

Rejected because it couples every lifecycle to source-control mutation, causes binary repository growth, and may publish sensitive experiment state.

### Keep every checkpoint forever

Rejected because unbounded storage contradicts the project's finite-resource principle.

## Required implementation invariants

The later implementation and fixed tests must demonstrate:

1. initialization cannot become wakeable before a genesis checkpoint is stable
2. a successful lifecycle commit sets an exact pending checkpoint boundary
3. no later wake advances while a checkpoint is pending
4. the Online Backup API produces a snapshot matching the pending boundary
5. incomplete temporary directories are never accepted as checkpoints
6. digest, size, integrity, foreign-key, identity, schema, contract, lineage, and event-boundary checks are enforced
7. registration clears pending only when the active boundary still matches
8. snapshot failure leaves committed state intact and pending
9. a valid orphan artifact can be recovered and registered explicitly
10. repeated checkpoint creation from unchanged state produces equivalent database content boundaries and deterministic manifest fields except declared creation metadata
11. retention never removes the latest stable checkpoint before a newer one is stable
12. rollback refuses an invalid or mismatched checkpoint
13. rollback creates a verified pre-rollback archive before active replacement
14. failure before replacement preserves the old active database in maintenance
15. failure after replacement leaves the restored database in maintenance and recoverable
16. rollback increments lineage generation from the abandoned active generation
17. restored events and new events remain distinguishable from abandoned-lineage events
18. default recovery selects the latest valid stable checkpoint by registered boundary, not file modification time
19. the immutable source checkpoint is not modified during restore
20. external mutable files are not falsely reported as restored in Phase 1
21. checkpoint retention and byte cost are measurable

## Operational notes for later implementation

- use separate source and destination SQLite connections for backup
- create the destination in a unique same-filesystem temporary directory
- close the destination before hashing and publication
- open validation connections in read-only mode
- run both `integrity_check` and `foreign_key_check`
- use deterministic JSON serialization for manifests
- treat manifest and database paths as untrusted input during restore; prevent path traversal
- fsync files and parent directories where the platform supports it
- use `os.replace` or an equivalently tested atomic same-filesystem publication primitive
- never overwrite an existing checkpoint identifier
- do not follow symlinks inside the checkpoint store
- require explicit free-space and size-limit checks before snapshot and rollback
- separate lifecycle events from administrative checkpoint and rollback events

## References

- SQLite, “SQLite Backup API”: https://www.sqlite.org/backup.html
- SQLite, “Online Backup API”: https://www.sqlite.org/c3ref/backup_finish.html
- SQLite, `PRAGMA integrity_check`, `quick_check`, and `foreign_key_check`: https://www.sqlite.org/pragma.html
- SQLite, “VACUUM”: https://www.sqlite.org/lang_vacuum.html
- Python, `sqlite3.Connection.backup()`: https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup

## Follow-up

Proceed to ADR 0005. The seed environment must fit this checkpoint boundary: authoritative mutable environment state should live inside SQLite or be deterministically regenerated, and one bounded action must have measurable outcomes without external network or caregiver access.
