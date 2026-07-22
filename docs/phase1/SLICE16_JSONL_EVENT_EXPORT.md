# Phase 1 Slice 16: Deterministic Non-Canonical JSONL Event Export

Status: **implemented and verified in PR #30**

Tracked by: Issue #13

## Scope

This slice adds one explicit administrative read-only export boundary for canonical event history.

The boundary is available through:

- Python API `export_stable_events(runtime_root, organism_id, event_sequence)`
- CLI `sudachi export events <organism_id> --event-sequence <N>`

It is not an organism action, does not run during a wake, and does not create a second canonical history.

## Declared source boundary

The caller must provide one positive canonical event sequence that identifies exactly one protected row in `checkpoint_registry`.

Before materializing any output, the exporter opens the active SQLite database with `mode=ro`, begins one read transaction, and requires:

- canonical schema and protected configuration validation
- no pending checkpoint
- stable `sleeping` or `maintenance_required` status
- exactly one registered protected checkpoint at the declared event boundary
- checkpoint lineage equal to the active lineage
- a valid immutable checkpoint directory and manifest
- registry and manifest agreement on organism identity, lineage, contract, schema, environment, budget configuration, event boundary, database digest, database bytes, and manifest digest
- complete append-only canonical event history from sequence `1` through the declared boundary
- the boundary event to belong to the declared checkpoint lineage

An unregistered event sequence, invalid checkpoint artifact, foreign lineage, incomplete event range, or pending checkpoint is rejected before an export file is published.

## Canonical JSONL representation

The first line is a manifest record containing:

- export format `sudachi-event-jsonl`
- export format version `1`
- organism identifier
- source lineage generation
- source checkpoint identifier
- contract, schema, environment, and budget-configuration versions
- first and last exported event sequences
- exported event count

Every later line is one event record in increasing canonical `event_sequence` order. Each event includes its organism identity, lineage generation, lifecycle number, wall timestamp, type, source, parsed JSON payload, and protected version fields.

Serialization uses sorted JSON keys, compact separators, UTF-8, and exactly one newline per record. The export contains no creation timestamp, random identifier, process identity, filesystem metadata, or hidden clock read. Repeating the export against unchanged canonical state produces byte-identical output.

## Bounded atomic publication

The output path is fixed beneath the organism's non-canonical `exports/` directory:

```text
events-g<lineage>-e<boundary>.jsonl
```

The complete validated output is bounded by the protected runtime working-set limit. Publication then:

1. creates a unique temporary file in the same `exports/` directory
2. writes and fsyncs the complete bytes
3. validates temporary size and byte equality
4. atomically replaces the deterministic final path
5. fsyncs the containing directory where supported
6. removes any remaining temporary file on failure

A protected test-only partial-write injection exists only as the Python keyword `protected_test_fail_after_bytes`. It is absent from the CLI and canonical state.

If a partial temporary write fails, a previously published export remains unchanged and no partial final artifact appears.

## Authority and isolation

JSONL remains a disposable derived artifact:

- SQLite is the sole canonical live store
- lifecycle code never dual-writes JSONL
- export code has no writable SQLite connection
- no export import path exists
- deleting or modifying an export cannot affect canonical state
- export bytes are never consulted by wake, checkpoint, policy, evaluation, or status logic

Protected tests compare active database bytes and digest, canonical status, event rows, inbox rows, checkpoint-registry rows, and immutable checkpoint artifacts before and after export operations.

## Protected tests

`tests/test_event_export.py` proves:

- exact manifest and event ordering for the genesis stable boundary
- byte-identical repeated export from unchanged canonical state
- canonical JSONL payload parsing and deterministic filename
- narrow CLI publication and JSON result
- export creation leaves all canonical and checkpoint state unchanged
- arbitrary export modification leaves canonical state unchanged
- export deletion leaves canonical state unchanged
- a later normal water wake remains possible after export creation, modification, and deletion
- an injected partial temporary write preserves the prior final export
- an injected write failure leaves no temporary artifact and changes no canonical state
- unregistered event boundaries are rejected without mutation
- pending-checkpoint state is rejected without mutation

GitHub Actions on Python 3.12 completed clean editable installation, compileall, genesis CLI smoke, and **55 protected tests**.

## Deliberately out of scope

- JSONL import or replay
- lifecycle dual-writing
- organism-controlled export
- export-triggered canonical audit events
- arbitrary export destinations
- rollback or lineage restoration
- checkpoint or orphan deletion
- caregiver consultation
- learning, memory, skills, or generic planning

## Exact next slice

Slice 17 should implement the smallest protected rollback foundation accepted by ADR 0004: offline administrative selection and complete validation of one retained stable checkpoint plus creation of a verified pre-rollback archive, stopping before active-database replacement or lineage mutation.

It must prove that invalid, foreign, missing, pruned, or ambiguous source checkpoints cannot begin rollback and that archive creation failure leaves the active organism, checkpoint registry, inbox, events, and wakeability unchanged.

It must not yet replace the active database, increment lineage generation, delete the abandoned future, import JSONL, add caregiver behavior, or add generic recovery machinery.
