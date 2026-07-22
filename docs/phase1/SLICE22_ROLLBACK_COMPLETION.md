# Phase 1 Slice 22: Atomic Rollback Completion

Status: **implemented and verified in PR #36**

Tracked by: Issue #13

## Scope

This slice completes one fully replaced rollback lineage and restores normal wakeability. It is the final canonical transaction in the protected rollback path implemented by Slices 17–22.

The boundary is available through:

- Python API `complete_rollback(runtime_root, organism_id, transformed_candidate_id, ...)`
- CLI `sudachi rollback complete <organism_id> --candidate-id <ID>`

It is explicit offline administration, not a normal wake or organism action.

## Fail-fast ownership and pre-mutation validation

Completion opens the replaced active SQLite database with a fresh writable connection and attempts fail-fast `BEGIN IMMEDIATE` before mutable reads.

It requires:

- canonical status `rollback_in_progress`
- no pending checkpoint
- the new lineage generation
- exact `rollback_lineage_prepared` at the active tip
- the selected stable checkpoint and source boundary

Before reading the administrative clock it revalidates:

- the immutable selected checkpoint and registry row
- the pre-rollback archive and abandoned-future boundary
- the source-restored candidate and exact checkpoint equality
- the lineage-transformed candidate and complete manifest
- exact active-versus-transformed-candidate logical equality
- protected versions, identity, lifecycle, lineage, event order, and `sqlite_sequence`

Missing, foreign, drifted, unsafe, busy, incomplete, or inconsistent provenance is rejected before clock use or mutation.

## Completion transaction

After complete validation, the operation reads exactly one injected administrative clock.

One bounded SQLite transaction:

1. changes status from `rollback_in_progress` to `sleeping`
2. resets `consecutive_failures` to zero
3. clears `maintenance_reason`
4. records the completion wall time as `last_sleep_wall_time_utc_us`
5. appends exactly one next-sequence `rollback_completed` event from `administration:rollback`
6. verifies queued input count is unchanged
7. validates canonical state with no pending checkpoint
8. commits status and completion history together

The completion event is in the new lineage and source lifecycle. Its wall time equals the restored sleeping timestamp.

## Completion payload

The canonical payload binds:

- the original bounded administrative reason accepted during Slice 20
- selected checkpoint identity, source lineage, event boundary, and digests
- abandoned lineage, lifecycle, event boundary, and rollback-start sequence
- archive identifier and archive digests
- source-restored candidate identifier and digests
- transformed candidate identifier and digests
- new lineage and restoration-event sequence
- completion-event sequence
- replacement validation fact
- implementation version
- status transition
- failure and maintenance state before and after completion
- exact queued-input count preserved

No new free-form completion reason is accepted. The reason already bound into the transformed candidate remains authoritative.

## Failure atomicity

A protected injection occurs after the sleeping-state update and completion-event insertion but before canonical validation and commit.

The injected failure proves:

- status returns to `rollback_in_progress`
- `rollback_completed` does not remain
- `rollback_lineage_prepared` remains the active tip
- normal wakes remain blocked before clock use
- environment, inbox, registry, checkpoints, archive, and both candidates remain unchanged

## Idempotence

An exact repeated completion request is recognized from:

- sleeping active state
- exact new lineage
- exact `rollback_completed` tip
- complete provenance-chain revalidation
- exact prepared history followed by one completion event
- exact declared organism changes only
- exact unchanged protected tables
- event-only `sqlite_sequence` increment

The repeated request reads no clock and changes no row, event, counter, artifact, or file.

Incompatible completed history or a different artifact chain is rejected rather than treated as completed.

## Wakeability and first post-rollback checkpoint

Before completion, normal wake is rejected with zero clock reads.

After completion, protected tests enqueue one new tick and perform a normal first-water wake. The wake:

- runs in the new lineage
- advances the source lifecycle
- commits the protected garden mutation
- creates and registers a new-lineage lifecycle checkpoint
- returns to sleeping state

The pre-rollback archive, source-restored candidate, and transformed candidate remain unchanged through this first post-rollback stable checkpoint.

## Protected tests

`tests/test_rollback_complete.py` proves:

- successful Python API completion
- narrow CLI exact-repeat completion
- one post-validation clock read
- exact status and `rollback_completed` atomic transaction
- exact completion payload
- maintenance and failure-state reset
- artifact preservation
- wake rejection before completion
- successful normal wake and new-lineage checkpoint after completion
- rejection without a replaced body
- transformed-candidate drift rejection
- archive drift rejection
- fail-fast competing-writer rejection
- injected post-event transaction rollback
- exact zero-clock repeated completion
- incompatible completed-history rejection

GitHub Actions on Python 3.12 completed clean editable installation, compileall, genesis CLI smoke, and **115 protected tests** on the implementation head.

The first implementation run found one failure: archive drift was detected correctly by the lower-level archive validator, but its `RollbackArchiveError` escaped instead of being classified as a completion rejection. The completion boundary was updated to preserve the exact cause while consistently wrapping subsystem `SudachiError` failures as `RollbackCompletionRejectedError`. The subsequent run passed all 115 tests.

## Complete protected rollback path

Slices 17–22 now provide:

1. selected source validation and abandoned-future archive
2. durable rollback intent and `rollback_started`
3. exact source-restored candidate
4. isolated new-lineage transformation and `rollback_lineage_prepared`
5. atomic canonical active replacement and immediate validation
6. atomic `rollback_completed` and restored wakeability
7. first successful post-rollback wake and stable checkpoint

No rollback artifact is deleted during this path.

## Deliberately out of scope

- rollback archive or candidate deletion
- long-term rollback-artifact retention and pruning policy
- remote export or backup policy
- JSONL import
- caregiver consultation
- learning, memory, skills, or generic recovery machinery

## Exact next action

Before implementing any rollback-artifact deletion, the repository must resolve a bounded retention policy through an accepted decision record.

The next work should define:

- which archive and candidate artifacts remain protected after the first post-rollback stable checkpoint
- whether source and transformed candidates may be reconstructed from other protected artifacts
- how multiple completed rollbacks are bounded under the runtime working-set limit
- what evidence is required before an abandoned-future archive may be removed
- how pruning failure preserves a recoverable and auditable state
- whether Phase 1 deliberately retains every rollback artifact and therefore limits the number of rollbacks instead of pruning

No deletion implementation should precede that decision.
