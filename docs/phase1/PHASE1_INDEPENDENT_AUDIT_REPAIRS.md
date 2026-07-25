# Phase 1 Independent Completion-Audit Repairs

Status: **Implemented on draft PR #57; first re-audit found two residual boundaries; additional repairs are green; second re-audit pending**

## Scope

Issue #56 audited Phase 1 at baseline commit `54b2be47107cd9fbad3301812d23ab90f7ea9c4e`. The audit confirmed the original 142-test baseline and identified six cross-boundary regressions. PR #57 repairs only those Phase 1 defects.

This work does not change Minimal Organism Contract v0.2 or ADRs 0001–0007. It adds no caregiver, model, network, subprocess, learning, memory, skill, arbitrary-code, continuous-execution, or Phase 2 behavior.

## Findings 1, 2, 3, and 6

The first Codex re-audit of PR #57 head `2ec29f896059ca5e476c20b6f1b05309f7d194ba` classified these findings as resolved:

1. malformed protected schema accepted and checkpointed
2. published pending checkpoints without a supported recovery path
3. pending repair bypassing checkpoint retention
6. incomplete runtime working-set accounting

The implemented repairs and protected evidence remain as described below.

### Finding 1 — protected schema integrity

- required protected tables and append-only triggers are fingerprinted from the production schema
- protected singleton cardinality, budget configuration, seed layout, and action registry are exact
- missing or changed required objects fail closed
- unexpected mutating schema objects fail closed; established side-effect-free `SELECT RAISE(ABORT, ...)` fault-injection guards remain usable

Protected tests:

- `tests/test_phase1_audit_schema_and_repair.py::test_missing_append_only_trigger_is_rejected_by_active_and_checkpoint_validation`
- `tests/test_phase1_audit_extra_trigger.py::test_unexpected_mutating_trigger_is_rejected`

### Finding 2 — pending checkpoint recovery

- repair validates and registers exactly one published orphan
- genesis, ordinary lifecycle, and maintenance-bound threshold states are supported
- genesis requires no prior registry row and provenance `genesis`
- lifecycle repair preserves the previous stable chain and provenance `lifecycle`
- final state is `sleeping` or `maintenance_required` as declared
- checkpoint creation accepts an already-published byte-identical artifact

Protected tests:

- `test_genesis_published_orphan_can_be_registered`
- `test_maintenance_bound_pending_orphan_repairs_to_stable_maintenance`
- all existing ordinary pending-repair tests

### Finding 3 — shared retention

- normal registration and repaired registration call one retention policy
- pruning loops until the protected four-checkpoint limit is restored
- genesis is not silently removed
- candidate identity, lineage, boundary, digest, protection, and storage are revalidated

Protected test:

- `test_repaired_checkpoint_runs_the_same_retention_policy`

### Finding 6 — complete working-set accounting

One no-symlink accountant covers:

- active SQLite database
- journal/WAL/shared-memory sidecars
- checkpoint store and staging
- rollback archives
- restore candidates

Checkpoint creation, repair, retention, wake preflight, and declared post-write boundaries use the common accountant.

Protected test:

- `test_runtime_working_set_counts_sidecars_and_retained_rollback_evidence`

## Finding 4 — enqueue storage and next-wake headroom

### First repair

The initial PR repair checked SQLite allocated pages before the enqueue clock read and after inbox/event writes, rolling back before the active database crossed 8 MiB.

### First re-audit residual

Codex reproduced a boundary where enqueue stopped at exactly 8 MiB. The organism remained `sleeping`, but the next wake required another SQLite page and rolled back. The finding was therefore only partially resolved.

### Additional repair

- `runtime_storage.py` defines a 1 MiB implementation reserve inside the accepted 8 MiB active-database ceiling
- enqueue requires that reserve both before its clock read and after its writes
- a rejected enqueue rolls back inbox, audit event, and sequence changes
- duplicate replay remains zero-clock and idempotent because existing identifiers are resolved before the storage preflight
- the reserve is not a new budget and does not increase the 8 MiB ceiling; it preserves capacity for one bounded Phase 1 wake

Protected tests:

- `test_enqueue_rolls_back_before_crossing_active_database_limit`
- `test_enqueue_keeps_one_bounded_wake_of_active_database_headroom`

## Finding 5 — crash-retryable retention reconciliation

### First repair

The initial PR repair recorded post-commit pruning cleanup failure as explicit maintenance and provided administrative reconciliation for `.pruning-*` staging.

### First re-audit residual

Codex interrupted reconciliation after the staging directory had been deleted but before the completion audit event committed. The filesystem cleanup was complete, but no canonical completion evidence remained. The finding was therefore only partially resolved.

### Additional repair

Reconciliation is now two-step and idempotent:

1. validate the committed prune evidence and commit `checkpoint_retention_cleanup_reconciliation_pending`
2. delete only the scheduled staging directories and fsync the checkpoint store
3. append `checkpoint_retention_cleanup_reconciled`, referencing the pending event sequence

If interruption occurs after deletion and before completion:

- the pending event remains durable
- retry recognizes the already-missing scheduled directories
- retry appends the completion event without another clock read
- ambiguous, unexpected, still-canonical, or unaudited staging fails closed

Protected tests:

- `test_post_commit_retention_cleanup_is_explicit_and_reconcilable`
- `test_retention_reconciliation_retries_after_delete_before_completion_audit`

## Validation history

- run 335: **150 passed in 8.74 seconds**
- run 336: **150 passed in 10.16 seconds**
- first Codex re-audit: findings 1/2/3/6 resolved; findings 4/5 partially resolved
- run 340 at head `b8ce12843d9692e50e770735d00f4b5379425eca`: clean installation, source/test compilation, genesis CLI smoke, and **152 passed in 10.32 seconds**

No existing protected test was deleted, weakened, skipped, or redefined.

## Second re-audit gate

PR #57 remains draft. The next external task is a read-only Codex re-audit of the final documentation-synchronized PR head.

The second re-audit must:

1. rerun the complete protected suite
2. repeat the exact Finding 4 boundary at the real 8 MiB ceiling and verify accepted enqueue leaves the next wake executable
3. interrupt Finding 5 reconciliation after deletion and verify retry produces exactly one linked completion audit without a new clock read
4. check that the two additional repairs do not reopen findings 1, 2, 3, or 6
5. post finding-by-finding evidence and one allowed final conclusion in Issue #56
6. make no tracked-file changes and introduce no Phase 2 behavior

PR #57 may be merged, Issue #13 reclosed, and the Phase 1 baseline re-frozen only after a satisfactory second re-audit.
