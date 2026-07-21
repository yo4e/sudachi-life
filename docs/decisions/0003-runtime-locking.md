# ADR 0003: Runtime Locking and Duplicate Wake Rejection

- **Status:** Accepted
- **Date:** 2026-07-21
- **Issue:** #1
- **Scope:** SUDACHI-0 seed architecture

## Context

SUDACHI-0 executes one bounded wake cycle and terminates. Two processes must not advance the same organism concurrently.

Without an exclusive wake boundary, two processes could:

- load the same state
- consume the same input event
- make independent decisions
- spend the same budget twice
- append conflicting outcomes
- create checkpoints from incompatible histories

ADR 0001 selects one SQLite database per organism as the sole canonical durable store and requires logically related lifecycle changes to share one transaction. ADR 0002 defines injected wall and monotonic clocks and explicitly rejects wall time as an ordering authority.

SQLite already provides cross-process file locking and allows only one write transaction at a time. `BEGIN IMMEDIATE` attempts to start a write transaction at once and fails with `SQLITE_BUSY` when another write transaction is active. SQLite also releases file locks and rolls back an uncommitted rollback-journal transaction when a process or connection terminates under the documented recovery model.

The design must distinguish:

- the mechanism that provides mutual exclusion
- diagnostic metadata about the current wake
- canonical lifecycle records committed after success

A durable lease row based on timestamps would duplicate SQLite's locking, introduce stale-lock recovery, and incorrectly make wall time part of mutual exclusion.

## Decision

### 1. The SQLite write transaction is the authoritative wake lock

A wake uses one fresh SQLite connection and attempts `BEGIN IMMEDIATE` before reading mutable organism state or consuming input.

If `BEGIN IMMEDIATE` succeeds, that connection owns the exclusive right to advance the organism until the transaction commits, rolls back, or the connection closes.

If it fails because the database is busy or another writer is active, the wake does not proceed.

No separate file lock, PID file, timestamp lease, or committed lock row is authoritative in Phase 1.

### 2. Lock acquisition is fail-fast and does not queue another wake

Wake-lock acquisition uses a zero wait or equivalent immediate busy policy.

A process that cannot acquire the write transaction returns a typed result such as:

```text
wake_rejected_busy
```

The exact public name is an implementation detail, but the result must be distinguishable from:

- invalid state
- corruption
- action failure
- budget exhaustion
- caregiver abstention

The losing process does not wait for the first wake to finish and then silently run as a second queued wake. A caller may explicitly retry later as a new attempt.

The result should be described as database or runtime busy rather than asserting that a specific second wake was definitely responsible; recovery, administrative work, or another writer may also hold the lock.

### 3. No mutable state is read before lock acquisition

The wake path may validate the database path and open a connection before acquisition, but it must not:

- load organism state
- inspect the event queue for decision making
- compute a next action
- reserve budgets
- create a checkpoint boundary

until `BEGIN IMMEDIATE` succeeds.

This prevents a time-of-check/time-of-use gap between observing state and obtaining write ownership.

Read-only commands such as `status` are separate operations and must not be reused as the start of a wake transaction.

### 4. One transaction spans the canonical wake

After acquisition, the same SQLite transaction covers the canonical lifecycle work required by ADR 0001:

- state validation
- selection or claiming of bounded input
- durable budget changes
- lifecycle outcome
- append-only canonical events
- final state
- stable event boundary used by checkpoint logic

The transaction commits only after the lifecycle outcome is valid.

Any exception, validation failure, cancellation, or commit failure causes rollback and connection closure.

The implementation must use `try`/`finally` or an equivalent structured boundary so every path ends in commit, rollback, or close.

### 5. Phase 1 keeps the write transaction bounded

Holding a write transaction across unbounded planning, network access, user interaction, or caregiver waiting would block future attempts and make failure recovery difficult.

Therefore, while the wake transaction is open, Phase 1 permits only bounded local work required by the deterministic lifecycle. It must not:

- wait for a human or model caregiver
- access the network
- sleep for backoff
- run an unbounded subprocess
- await an external approval
- retry indefinitely

Later phases that need long-running or interactive work must separate proposal generation from a short adoption transaction through a new ADR. They must not lengthen the Phase 1 lock silently.

### 6. An in-database runtime record is diagnostic, not a second lock

The schema may include a singleton runtime row or lifecycle-attempt fields for validation and diagnostics, but their authority is limited.

Inside the uncommitted transaction, the wake may set diagnostic values such as:

- lifecycle sequence or attempt number
- started wall timestamp
- declared budgets
- implementation version

On successful commit, canonical history records the completed outcome.

On rollback or process death, uncommitted “running” values disappear. The previously committed sleeping or stable state remains.

A persisted timestamp, PID, hostname, thread identifier, or random owner token must not be used to steal or override the SQLite lock.

### 7. There is no automatic stale-lock lease in Phase 1

Phase 1 does not declare a lock stale because a wall-clock duration elapsed.

SQLite file locks are released when the owning connection or process terminates, and rollback-journal recovery handles an interrupted write transaction. If the operating system still regards the writer as alive or the filesystem does not provide correct locking semantics, SUDACHI must report busy rather than guess.

Manual database repair or force-unlocking is not an organism action. Any future administrative recovery mechanism must verify process and filesystem state and leave an audit record.

### 8. Process identity is non-canonical diagnostic metadata

Operating-system process ID, hostname, thread ID, and ephemeral tokens may appear in local diagnostic logs.

They must not:

- affect deterministic action selection
- define canonical lifecycle identity
- appear in canonical event content required to reproduce Phase 1 behavior
- authorize a wake

Canonical lifecycle identity should be derived from database-controlled sequence values committed within the transaction.

### 9. Read-only access remains possible but bounded

Under the rollback-journal model selected by ADR 0001, a writer holding a reserved lock can coexist with existing readers until commit requires stronger access.

Read-only commands must:

- use short-lived connections
- finish and close cursors promptly
- avoid long reports inside an open read transaction
- never mutate state
- report busy or retry only through an explicit bounded user-facing policy

A read-only command must not delay wake commit indefinitely.

### 10. Commit contention is an explicit failure

Lock acquisition success does not justify an unbounded wait during commit.

If commit cannot complete because another connection or filesystem condition blocks it, the wake uses a bounded database policy, reports an explicit storage-busy or commit failure, rolls back where possible, and closes the connection.

Phase 1 must not use an injected organism clock to simulate SQLite's internal lock waiting. Deterministic tests create competing connections and assert outcomes directly without relying on long real sleeps.

### 11. One database path defines one lock domain

All wake processes for one organism must open the same canonical database path.

The following are unsupported while an organism may be awake:

- copying the live database and treating the copy as the same organism
- moving or renaming the database
- replacing it through cloud synchronization
- accessing it from multiple hosts
- using a network filesystem whose locking behavior has not been validated

Forking or copying an organism requires an explicit sleeping-state administrative procedure and later identity rules.

### 12. Nested and reentrant wakes are prohibited

A wake must not invoke another wake for the same organism.

Each wake uses its own fresh connection. Attempting to begin another wake from inside the lifecycle is an error even if it occurs in the same process.

Helper functions receive the existing transaction context rather than opening hidden write connections.

## Consequences

### Positive

- Mutual exclusion relies on SQLite's cross-process write lock rather than a second custom lease protocol.
- A crash releases the authoritative lock and rolls back uncommitted canonical changes.
- No stale timestamp row can permanently strand the organism.
- State is not read before exclusive write ownership is obtained.
- The same transaction provides wake ownership and atomic canonical persistence.
- Duplicate attempts are rejected instead of silently queued.
- Deterministic behavior does not depend on PID, hostname, or wall-clock lease age.

### Negative

- The SQLite write transaction remains open for the bounded lifecycle.
- Long read transactions may interfere with commit in rollback-journal mode.
- A busy result cannot always prove that the competing writer is another wake.
- A failed competing attempt may not be recorded in the canonical database because it could not obtain write authority.
- External side effects cannot be made atomic merely by holding the SQLite transaction.

### Neutral or deferred

- ADR 0004 must define checkpoint creation without extending the lock indefinitely.
- ADR 0005 must ensure the seed environment can be updated within the bounded local transaction model or through a safely staged effect protocol.
- Contract review must reconcile any external filesystem action with SQLite transaction atomicity.
- Later caregiver phases require a proposal/adoption split rather than holding the transaction while waiting.
- A future multi-host organism would require a different storage and locking ADR.

## Alternatives rejected

### Committed singleton lock row with owner and lease expiry

Rejected because it duplicates SQLite locking, survives crashes as stale state, requires clock-based stealing, and creates a dangerous distinction between the row and the actual file lock.

### PID or lock file

Rejected as the authoritative mechanism because stale files survive crashes, process IDs can be reused, cross-platform semantics vary, and the lock would not automatically share the canonical transaction boundary.

### Read state first, then acquire a write lock before persistence

Rejected because another wake could advance the organism between the read and acquisition.

### `BEGIN DEFERRED`

Rejected for wake acquisition because it does not obtain write ownership until a later statement. Two wakes could both begin and read before one fails to upgrade.

### `BEGIN EXCLUSIVE`

Rejected because Phase 1 does not need to block all readers for the whole lifecycle. `BEGIN IMMEDIATE` obtains write ownership while allowing bounded readers under the rollback-journal model.

### Waiting for the lock and then running automatically

Rejected because simultaneous triggers would become sequential hidden wakes. The losing attempt must be explicit and a retry must be a new caller decision.

### In-process mutex only

Rejected because it cannot coordinate separate processes.

### External lock service

Rejected because it adds a service, networking, credentials, and another availability dependency to a local single-organism Phase 1.

## Required implementation invariants

The later implementation and fixed tests must demonstrate:

1. a wake executes `BEGIN IMMEDIATE` before reading mutable organism state
2. two competing connections cannot both pass wake acquisition
3. the losing connection returns an explicit busy rejection and does not act
4. the losing attempt is not silently queued to execute after the winner
5. a crash or forced connection close rolls back uncommitted state and releases the write lock
6. a subsequent wake can proceed after the crashed connection is gone and recovery completes
7. no persisted lease timestamp, PID, or token can override the SQLite lock
8. nested wake attempts are rejected
9. helper code does not open hidden write connections during a wake
10. success commits state and events together
11. failure before commit leaves the prior committed state and event boundary intact
12. a short read-only status connection can coexist without mutating state
13. a deliberately long reader produces an explicit bounded commit failure rather than an unbounded hang
14. lock results do not alter deterministic canonical output through process identity or current wall time
15. unsupported database paths or multi-host assumptions are rejected or clearly reported

## Operational notes for later implementation

- create a fresh SQLite connection for each wake
- set transaction behavior explicitly; do not rely on accidental autocommit defaults
- attempt acquisition before creating cursors that read mutable state
- configure acquisition to fail immediately on busy
- close all cursors and the connection deterministically
- distinguish `SQLITE_BUSY` from corruption, permission, and schema errors
- keep status and administrative reads short
- do not expose `BEGIN`, `COMMIT`, `ROLLBACK`, or arbitrary SQL to organism actions
- use real concurrent connections or subprocesses for locking tests; do not fake the lock with mocks

## References

- SQLite, “Transaction”: https://www.sqlite.org/lang_transaction.html
- SQLite, “File Locking And Concurrency In SQLite Version 3”: https://www.sqlite.org/lockingv3.html
- SQLite, “Result and Error Codes”: https://www.sqlite.org/rescode.html
- SQLite, “Set A Busy Timeout”: https://www.sqlite.org/c3ref/busy_timeout.html

## Follow-up

Proceed to ADR 0004. It must define checkpoint representation, validation, cadence, rollback granularity, and how a consistent SQLite snapshot is created without introducing a second canonical state or holding the runtime lock indefinitely.
