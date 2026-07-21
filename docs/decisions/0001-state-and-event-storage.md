# ADR 0001: Canonical State and Event Storage

- **Status:** Accepted
- **Date:** 2026-07-21
- **Issue:** #1
- **Scope:** SUDACHI-0 seed architecture

## Context

SUDACHI-0 needs durable organism state, append-only event history, atomic lifecycle commits, deterministic ordering, recovery boundaries, and reproducible experiment exports.

The Minimal Organism Contract requires that:

- durable state survives process termination
- state changes and event recording do not diverge after failure
- event history is append-only
- failures do not silently corrupt state
- rollback and checkpoints remain possible
- deterministic runs do not depend on incidental filesystem ordering

The initial candidates were:

1. SQLite as the only canonical store
2. SQLite for current state plus a canonical JSONL event log
3. separate JSON or similar state files plus JSONL history

Using more than one canonical durable resource would create a cross-resource commit problem. A lifecycle could update state successfully but fail before appending JSONL, or append an event while failing to persist the state it describes. Solving that correctly would require a second transaction protocol before SUDACHI has implemented its first lifecycle.

SQLite provides transactional grouping in one local application file. Its official documentation states that changes within one transaction occur completely or not at all, including interruption by process, operating-system, or power failure under the documented assumptions. SQLite also provides supported backup mechanisms for consistent snapshots.

## Decision

### 1. SQLite is the sole canonical durable store

Each SUDACHI organism instance has one canonical SQLite database inside its allowed state directory.

The database is authoritative for:

- organism identity and metadata
- schema and contract versions
- current durable state
- concrete budgets and counters
- queued and observed events
- append-only lifecycle and action outcomes
- provenance records
- checkpoint metadata and stable event boundaries

The exact table schema is an implementation concern constrained by the contract and later ADRs. No JSON, JSONL, YAML, Git file, cache, or in-memory object is a second source of truth.

### 2. State mutation and event recording share one transaction

A successful lifecycle commit must write all logically related durable changes in one SQLite transaction.

At minimum, the transaction boundary must cover:

- consumed or updated durable input-event status
- resulting organism state
- budget consumption
- the lifecycle outcome
- newly appended audit events
- the stable event-sequence boundary needed by checkpoint logic

If the transaction does not commit, none of those changes are considered to have happened.

The exact transaction-opening and duplicate-wake strategy is deferred to ADR 0003. The checkpoint representation and timing are deferred to ADR 0004.

### 3. Canonical event order uses a database sequence

Every canonical event receives a monotonically increasing integer sequence within the organism database.

The sequence, not a timestamp, defines canonical event order.

Timestamps may be stored as metadata after ADR 0002 defines clock semantics. Equal, missing, adjusted, or non-monotonic timestamps must not make event order ambiguous.

An external event identifier may also exist for idempotency or provenance, but it does not replace the canonical sequence.

### 4. Canonical events are append-only

Committed event rows may not be updated or deleted during normal organism operation.

Phase 1 must enforce append-only behavior at more than one level:

- the organism exposes no update or delete event action
- the storage layer does not provide normal event-mutation methods
- database-level constraints or triggers reject event update and deletion where practical
- migrations and explicit administrative repair, if ever required, operate outside organism authority and leave an auditable record

Derived views, indexes, queues, and current-state projections may change. Historical event facts do not.

### 5. JSONL is a non-canonical export only

JSONL may be generated for:

- human inspection
- experiment packaging
- analysis with external tools
- publication supplements
- debugging and audit review

JSONL is never written as part of the authoritative lifecycle transaction.

An export must be reproducible from a declared committed database boundary and must include or accompany enough manifest information to identify:

- organism identifier
- schema version
- contract version
- first and last exported event sequence
- export format version
- source checkpoint or database boundary when applicable

Records are emitted in canonical event-sequence order. Export failure does not roll back or invalidate the organism database. Deleting an export does not delete organism memory.

Phase 1 does not import JSONL back into canonical state. Any future import or replay format requires a separate decision and validation design.

### 6. Use one database file per organism, on a local filesystem

Phase 1 supports one canonical database per organism instance.

The database and any SQLite-managed sidecar files must remain inside the organism's allowed state directory. Network filesystems, cloud synchronization folders, and shared multi-host access are outside the Phase 1 support boundary.

Multiple independent organism databases may exist, but cross-organism atomic transactions are not required.

### 7. Journal mode is conservative until locking and checkpoint ADRs are accepted

ADR 0001 does not require write-ahead logging.

Phase 1 begins from SQLite's rollback-journal transaction model unless ADR 0003 or ADR 0004 documents and tests a reason to select WAL. WAL may improve concurrency, but Phase 1 does not need concurrent readers and writers, and WAL introduces additional sidecar and checkpoint behavior.

Regardless of journal mode, the application must not copy a live database file naively and call it a checkpoint. ADR 0004 must use a supported consistent-snapshot mechanism such as SQLite's backup facilities or an equivalently validated process.

### 8. Schema evolution is explicit

The canonical database stores an explicit schema version.

Schema changes require:

- a versioned migration
- a transaction
- validation before and after migration
- compatibility notes for checkpoints and exports
- an event or administrative audit record

The organism cannot migrate its own protected schema during Phase 1.

## Consequences

### Positive

- Current state and event history cannot diverge because of a failed dual write.
- Lifecycle durability has one transaction boundary.
- Deterministic order does not depend on wall-clock timestamps.
- Append-only history can be enforced and queried efficiently.
- Checkpoints can be defined against a database snapshot and event sequence.
- JSONL remains available without becoming another authority.
- The design uses Python's standard SQLite support and requires no service process.

### Negative

- SQLite becomes a foundational dependency and file format.
- Humans cannot treat a text log in Git as the live organism state.
- Database inspection requires SQLite-aware tools or project commands.
- Migrations must be designed and tested.
- A damaged database may affect both current state and history, making checkpoint discipline essential.
- Direct manual database editing is powerful and must be considered administrative intervention.

### Neutral or deferred

- This ADR does not choose the Python storage abstraction or exact schema.
- This ADR does not define clock values or timestamp generation.
- This ADR does not define stale-lock recovery or concurrent wake behavior.
- This ADR does not define checkpoint cadence or retention.
- This ADR does not define the seed environment.
- This ADR does not decide the energy metaphor.

## Alternatives rejected

### Canonical SQLite state plus canonical JSONL history

Rejected because it introduces a cross-resource atomicity problem. Two canonical resources can disagree after a crash or partial write.

### Canonical JSONL plus reconstructable current state

Rejected for Phase 1 because replay, migration, validation, compaction, lock handling, and corruption recovery would all need to be solved before the first lifecycle. This may be useful as an experiment artifact later, not as the seed source of truth.

### Canonical JSON or YAML state plus JSONL events

Rejected because replacement of the state file and append of the event log cannot be committed atomically with ordinary filesystem operations.

### Git as the live database

Rejected because Git is the developmental and source lineage, not the runtime transaction engine. Committing every lifecycle would couple organism operation to repository mutation and would not by itself solve atomic state/event updates.

### External database server

Rejected because PostgreSQL or another service adds deployment, authentication, networking, and operational complexity with no Phase 1 requirement.

## Required implementation invariants

The later implementation and fixed tests must demonstrate:

1. a committed lifecycle contains its state change and audit events together
2. an exception or process interruption before commit leaves neither partial state nor partial events
3. canonical event sequence is unique and strictly increasing
4. event update and deletion are rejected
5. state cannot reference a future or nonexistent committed event boundary
6. JSONL export order is deterministic for a fixed database boundary
7. repeated export from unchanged canonical state produces semantically identical records and manifest boundaries
8. export failure does not alter canonical state
9. deleting or modifying an export does not alter canonical state
10. the database declares and validates its schema version
11. unsupported database location or sidecar placement is rejected or clearly reported
12. checkpoint creation uses a consistent SQLite snapshot mechanism after ADR 0004 is accepted

## Operational notes for later implementation

These are implementation constraints, not a complete schema:

- enable and verify foreign-key enforcement on each connection
- make transaction ownership explicit rather than relying on accidental autocommit behavior
- use parameterized statements
- close connections deterministically
- run SQLite integrity checks at defined administrative or recovery points, not on every normal read
- distinguish organism actions from administrative inspection, migration, export, and repair
- do not expose arbitrary SQL execution to the organism

## References

- SQLite, “SQLite Is Transactional”: https://www.sqlite.org/transactional.html
- SQLite, “Atomic Commit In SQLite”: https://www.sqlite.org/atomiccommit.html
- SQLite, “Transaction”: https://www.sqlite.org/lang_transaction.html
- SQLite, “Write-Ahead Logging”: https://www.sqlite.org/wal.html
- SQLite, “SQLite Backup API”: https://www.sqlite.org/backup.html
- SQLite, “SQLite As An Application File Format”: https://www.sqlite.org/appfileformat.html

## Follow-up

Proceed to ADR 0002, which must define clock injection, timestamp representation, and deterministic time behavior without changing the sequence-based event-order decision made here.
