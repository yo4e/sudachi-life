# Phase 1 Slice 23: Single Completed Rollback Admission Guard

Status: **implemented and verified in PR #38**

Tracked by: Issue #13

## Scope

This slice enforces ADR 0007 at the earliest protected rollback-preparation boundary. Phase 1 permits one completed rollback per organism and retains the complete archive and candidate evidence set without deletion or pruning.

The existing Python API and CLI remain unchanged:

- `prepare_rollback_archive(runtime_root, organism_id, source_event_sequence, ...)`
- `sudachi rollback prepare <organism_id> --event-sequence <N>`

The operation remains explicit offline administration rather than a normal wake or organism action.

## Admission order

Rollback preparation continues to:

1. open the canonical active SQLite body
2. acquire fail-fast `BEGIN IMMEDIATE`
3. validate canonical state with no pending checkpoint
4. read the singleton organism row and require stable sleeping or maintenance state

It now then counts canonical events whose type is exactly `rollback_completed`.

Eligibility requires a count of zero. One or more completed rollback events cause typed `RollbackPreparationRejectedError` before:

- latest-checkpoint registry lookup
- selected-source validation
- checkpoint artifact inspection
- rollback archive-root creation
- working-set prediction
- SQLite Online Backup
- temporary or final artifact creation

The rejection path has no clock boundary and performs no canonical or artifact mutation.

## Preserved first rollback path

The guard does not change the first permitted rollback path. An organism with zero `rollback_completed` events may still:

1. prepare one verified abandoned-future archive
2. record durable rollback intent
3. build the exact source-restored candidate
4. transform the candidate into the new lineage
5. replace canonical authority atomically
6. record `rollback_completed`
7. perform the first new-lineage wake and stabilize its checkpoint

Every archive and candidate remains immutable and retained.

## Protected tests

`tests/test_single_rollback_retention.py` adds two protected scenarios.

### Second preparation rejection

The test completes the full first rollback, performs the first new-lineage water wake, and stabilizes its checkpoint. It then:

- snapshots the canonical database and all checkpoint, archive, and candidate bytes
- replaces the private selected-source validator with a failure sentinel
- attempts a second rollback preparation
- requires typed rejection reporting one completed rollback
- proves selected-source validation was never reached
- proves the canonical database and every artifact remain byte-identical
- proves no second rollback archive directory exists

### Independent organism eligibility

The test completes one rollback for the first organism, initializes a separate second organism, and proves the second organism can prepare its own first rollback archive from its genesis checkpoint. The first organism remains unchanged.

## Deliberately out of scope

- rollback archive or candidate deletion
- rollback artifact pruning
- repeated rollback support within one organism
- schema or contract changes
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

## Verification

GitHub Actions run 219 on Python 3.12 completed successfully for PR #38:

- clean editable installation
- source and test compilation
- **117 protected tests passed in 6.31 seconds**
- genesis CLI smoke test

No implementation correction was required. The workflow remains the existing public-repository `ubuntu-latest` runner with the existing bounded pytest-log artifact.

## Exact next action

Keep PR #38 ready for human review and merge. After merge, reconstruct current `main`, open issues, and open pull requests before selecting Slice 24. Do not extend this branch into rollback-artifact deletion, pruning, repeated rollback support, or another Phase 1 evaluation.
