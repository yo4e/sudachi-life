# Phase 1 Independent Completion-Audit Repairs

Status: **Implemented on draft PR #57; GitHub Actions run 335 passed 150 protected tests; independent re-audit pending**

## Scope

Issue #56 performed a read-only audit of Phase 1 at baseline commit `54b2be47107cd9fbad3301812d23ab90f7ea9c4e`. The audit confirmed the original 142-test baseline and identified six cross-boundary regressions. PR #57 repairs only those Phase 1 defects.

This work does not change Minimal Organism Contract v0.2 or ADRs 0001–0007. It does not add caregiver consultation, a model adapter, network access, subprocess access, learning, memory, skills, arbitrary code execution, continuous execution, or any Phase 2 behavior.

## Finding 1 — malformed protected schema accepted and checkpointed

### Repair

- `src/sudachi_life/schema_contract.py` constructs the required protected schema signature from the production schema and verifies every required table and append-only trigger definition.
- Active and checkpoint validation also verify protected singleton cardinality, exact budget configuration, seed plot layout, and action registry.
- Missing or changed required objects fail closed.
- Additional schema objects fail closed except side-effect-free test-only trigger guards whose body is only `SELECT RAISE(ABORT, ...)`; an unexpected mutating trigger is rejected.

### Protected evidence

- `tests/test_phase1_audit_schema_and_repair.py::test_missing_append_only_trigger_is_rejected_by_active_and_checkpoint_validation`
- `tests/test_phase1_audit_extra_trigger.py::test_unexpected_mutating_trigger_is_rejected`
- the existing maintenance-clear injected-abort trigger remains usable, so the original fault-injection boundary is not weakened

## Finding 2 — published pending checkpoints lacked a supported recovery path

### Repair

Pending registration repair is split into explicit validation and commit stages:

- `checkpoint_repair_validate.py` validates one exact published orphan and accepts three declared pending states: genesis, ordinary lifecycle, and maintenance-bound failure threshold.
- genesis requires no prior registry row and provenance `genesis`.
- ordinary and maintenance-bound lifecycle checkpoints require the previous stable registry/artifact chain and provenance `lifecycle`.
- `checkpoint_repair_commit.py` preserves the correct final status: `sleeping` for genesis/ordinary repair and `maintenance_required` for threshold-bound repair.
- the repair remains one fail-fast administrative SQLite transaction and appends typed audit provenance.
- checkpoint creation recognizes an already-published byte-identical artifact instead of failing only because its final directory exists.

### Protected evidence

- `tests/test_phase1_audit_schema_and_repair.py::test_genesis_published_orphan_can_be_registered`
- `tests/test_phase1_audit_schema_and_repair.py::test_maintenance_bound_pending_orphan_repairs_to_stable_maintenance`
- all pre-existing ordinary pending-repair tests continue to pass

## Finding 3 — pending repair bypassed checkpoint retention

### Repair

- normal checkpoint registration and repaired checkpoint registration both call `enforce_checkpoint_retention(...)`.
- the shared policy prunes oldest eligible non-genesis stable checkpoints until the protected limit is restored; it does not assume the registry is exactly one over the limit.
- retention revalidates latest stable identity, registry/artifact agreement, protected status, manifest lineage/boundary/digest, and storage accounting for every candidate.

### Protected evidence

- `tests/test_phase1_audit_retention_and_storage.py::test_repaired_checkpoint_runs_the_same_retention_policy`
- existing successful-retention and injected pre-commit retention-failure tests continue to pass

## Finding 4 — administrative enqueue bypassed the active-database limit

### Repair

- `src/sudachi_life/runtime_storage.py` measures SQLite allocated pages inside the current connection.
- `enqueue_garden_tick(...)` checks the active-database limit before its clock read and again after the inbox/event writes but before commit.
- a crossing rejects with a typed input error and rolls back the complete enqueue transaction, including the inbox row, audit event, and SQLite sequence changes.
- the diagnostic identifies rollback or quarantine as the explicit recovery route for an already-oversized historical database; it does not silently delete queued input.

### Protected evidence

- `tests/test_phase1_audit_retention_and_storage.py::test_enqueue_rolls_back_before_crossing_active_database_limit`
- existing idempotence, authority, concurrency, ordering, and replay tests continue to pass

## Finding 5 — post-commit retention cleanup failure was hidden

### Repair

- retention still commits the registry deletion and `checkpoint_pruned` event before deleting the staged artifact, so the new stable checkpoint is not invalidated.
- failure to delete `.pruning-*` records `checkpoint_retention_failed`, enters explicit protected maintenance, and preserves the staged evidence.
- `reconcile_checkpoint_retention_staging(...)` removes only a staging directory whose registry row is absent and whose exact `checkpoint_pruned` audit event exists; it then appends `checkpoint_retention_cleanup_reconciled`.
- ambiguous, still-canonical, or unaudited staging is rejected rather than deleted.

### Protected evidence

- `tests/test_phase1_audit_retention_and_storage.py::test_post_commit_retention_cleanup_is_explicit_and_reconcilable`
- existing pre-commit injected retention-failure classification remains protected

## Finding 6 — ordinary checkpoint and repair accounting omitted rollback evidence

### Repair

`runtime_storage.py` provides one no-symlink accountant for:

- active SQLite database
- approved SQLite journal/WAL/shared-memory sidecars
- complete checkpoint store, including temporary and pruning staging directories
- rollback archives
- restore candidates

Checkpoint preflight, publication, retention, repaired registration, wake preflight, and declared post-write boundaries use the shared accounting functions. Unsafe symlinks or non-regular entries fail closed.

### Protected evidence

- `tests/test_phase1_audit_working_set.py::test_runtime_working_set_counts_sidecars_and_retained_rollback_evidence`
- rollback evidence-retention and later wake/checkpoint tests remain green

## Implementation structure

The original public APIs remain available through `sudachi_life.checkpoints` and `sudachi_life.checkpoint_repair`. Internal responsibilities are separated to keep validation, registration, retention, reconciliation, and storage accounting independently testable:

- `checkpoint_core.py`
- `checkpoint_creation.py`
- `checkpoint_retention.py`
- `checkpoint_retention_prune.py`
- `checkpoint_retention_reconcile.py`
- `checkpoint_retention_warning.py`
- `checkpoint_repair_types.py`
- `checkpoint_repair_validate.py`
- `checkpoint_repair_commit.py`
- `runtime_storage.py`
- `schema_contract.py`

The fixed garden policy, action/evaluation semantics, authority namespaces, rollback policy, caregiver-zero budget, and Phase 1 contract remain unchanged.

## Validation history

- run 332: source/tests compiled; **144 passed / 5 failed**; failures exposed integration mismatches in fault-injection compatibility and new test setup
- run 333: **149 passed in 9.97 seconds**
- run 334: **149 passed / 1 failed**; remaining failure was the safe abort-guard parser test
- run 335 at head `4bb632a226dd8891fbd71aec345b1298777e3614`: clean editable installation, source/test compilation, genesis CLI smoke, and **150 passed in 8.74 seconds**

No existing protected test was deleted, weakened, skipped, or redefined to obtain the green result.

## Re-audit gate

PR #57 remains draft. The next task is an independent read-only Codex re-audit of the latest PR head against each of the six original Issue #56 findings.

The re-audit must:

1. inspect the latest PR #57 head rather than the old baseline commit
2. rerun the complete protected suite
3. reproduce or otherwise verify each original finding against the repair
4. classify every finding as resolved, partially resolved, unresolved, or superseded by a new verified defect
5. report any new regression with exact evidence and minimal reproduction
6. post a finding-by-finding report and one allowed final conclusion in Issue #56
7. make no tracked-file changes and introduce no Phase 2 behavior

PR #57 may be merged, Issue #13 reclosed, and the 150-test Phase 1 baseline re-frozen only after a satisfactory re-audit.
