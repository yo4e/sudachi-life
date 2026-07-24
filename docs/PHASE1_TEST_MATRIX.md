# Phase 1 Contract Evaluation Matrix

Status: **Slices 1–35 plus the independent completion-audit repairs are implemented and verified on PR #57 — all 41 fixed Phase 1 evaluations complete**

This matrix maps Minimal Organism Contract v0.2 §15 evaluations to protected tests. Complete coverage means the fixed Phase 1 boundary is implemented; it does not claim learning, intelligence, personality, or caregiver independence.

| Contract evaluation | Protected test status |
| --- | --- |
| 1. Identical declared inputs produce identical canonical results | `tests/test_repeated_run_equivalence.py::test_identical_declared_inputs_produce_exact_first_wake_results` requires two independent complete first-water runs with identical declared inputs to produce identical results, canonical rows, SQLite sequence state, active database digest, checkpoint manifests and artifacts, and next-input acceptance. |
| 2. Unexpected clock reads fail | Lifecycle and administrative tests use exhausted fake clocks on rejection paths and exact declared read counts on accepted paths. Invalid authority, pending-state wake rejection, inspection, export, archive preparation, rollback source/candidate operations, and repeated completion reject without hidden clock reads. |
| 3. Backward wall time does not reorder events | `tests/test_backward_wall_time_ordering.py::test_backward_wall_time_does_not_reorder_complete_first_wake` proves canonical integer sequence order under decreasing wall timestamps. |
| 4. Seed does not change seed-garden behavior | `tests/test_seed_independence.py::test_different_declared_seeds_preserve_first_wake_behavior` normalizes only audited seed and digest-derived identities and requires the same policy, transition, evaluation, ledger, state, history, and checkpoint. |
| 5. One tick/observation/attempt/mutation maximum | Water and harvest assert one attempt/mutation; abstentions and threshold entry assert zero; classified action failure asserts one attempt and zero successful mutations; deadline exhaustion occurs before executor entry. |
| 6. Twelve-step and monotonic deadline | First-water ledger records twelve semantic steps; `tests/test_budget_exhaustion.py` proves typed monotonic deadline exhaustion before action. |
| 7. Cleanup grace is not action time | `tests/test_cleanup_grace.py` proves normal work stops at the deadline, exact cleanup grace may terminalize, and one nanosecond beyond grace rolls back the complete uncommitted lifecycle. |
| 8. Hard-zero external capabilities | Water, harvest, abstention, recovery, failure, maintenance, cleanup exhaustion, and guarded action probes assert zero caregiver, network, subprocess, and authoritative external-write use. |
| 9. No independent energy field | `tests/test_initialization.py::test_canonical_state_has_no_energy_column`. |
| 10. First canonical tick waters `bed-a` | `tests/test_first_water_success.py::test_first_water_wake_commits_evaluates_and_checkpoints`. |
| 11. Second canonical tick harvests `bed-b` | `tests/test_second_harvest_success.py::test_second_wake_harvests_and_completes_objective`. |
| 12. Third canonical tick abstains after completion | `tests/test_objective_complete_boundary.py::test_third_wake_abstains_after_objective_completion`. |
| 13. Lexicographic tie breaking | `tests/test_insertion_order_tie_breaking.py` proves canonical target ordering and decision selection are independent of physical row insertion order. |
| 14. Resource-aware harvest fallback | `tests/test_resource_aware_recovery.py::test_resource_aware_harvest_recovers_and_resets_failure_streak`. |
| 15. Specific no-applicable-action abstention | `tests/test_no_applicable_action.py` protects the exact abstention reason, unchanged environment, one failure increment, and evaluator rejection when an action exists. |
| 16. Duplicate external tick never creates another action | `tests/test_post_action_duplicate_replay.py` proves a consumed external identifier is zero-clock and byte/canonical/artifact idempotent and only a distinct identifier creates later work. |
| 17. No negative counters | SQLite constraints and exact transition assertions cover all implemented paths. The audit repair additionally rejects administrative enqueue before a storage-limit crossing and rolls back its inbox and event rows. |
| 18. Action attempt is charged before execution | `tests/test_action_failure_savepoint.py`. |
| 19. Savepoint removes partial mutation while preserving failure cost | `tests/test_action_failure_savepoint.py`. |
| 20. Budget exhaustion occurs before forbidden mutation | `tests/test_budget_exhaustion.py` and cleanup-grace tests prove the executor is never entered after normal-work exhaustion. |
| 21. Failure streak and maintenance threshold | Slices 5–12 protect increments, reset, exact threshold entry, inspection, and clear; rollback completion resets restored failure state. `tests/test_phase1_audit_schema_and_repair.py::test_maintenance_bound_pending_orphan_repairs_to_stable_maintenance` proves a published third-failure boundary stabilizes as maintenance rather than becoming unrecoverable. |
| 22. Atomic state/event commit | Genesis, lifecycle, maintenance clear, pending repair, rollback intent, candidate transformation, active replacement, rollback completion, cleanup-grace rollback, no-input rejection, process-exit rollback, and audit-repaired enqueue all preserve declared atomic boundaries. |
| 23. Sequence order is canonical | Lifecycle and administrative events are sequence-asserted; rollback preserves source history and appends lineage/completion events at exact next sequences. |
| 24. Event update/delete rejected | `tests/test_initialization.py::test_event_history_rejects_update_and_delete`; `tests/test_phase1_audit_schema_and_repair.py::test_missing_append_only_trigger_is_rejected_by_active_and_checkpoint_validation` proves a missing required trigger invalidates active and checkpoint state; `tests/test_phase1_audit_extra_trigger.py` rejects an unexpected mutating trigger while established side-effect-free test guards remain usable. |
| 25. JSONL export deterministic and non-canonical | `tests/test_event_export.py` proves exact stable-boundary validation, byte-identical output, atomic publication, isolation, and preserved wakeability. |
| 26. Competing wake has one winner and one non-queued rejection | Wake and every write-owning rollback administration boundary use protected fail-fast competing-writer rejection. |
| 27. Crash before commit preserves prior state | `tests/test_process_crash_rollback.py` exits a spawned process through `os._exit` after uncommitted canonical mutations and proves exact rollback, released ownership, and later normal completion. |
| 28. Nested wake is rejected | `tests/test_nested_wake_rejection.py` proves nested acquisition and a hidden writer fail without queued work and preserve exact body/artifacts. |
| 29. Stable genesis checkpoint before wakeable | Initialization and genesis tests protect the normal path. `tests/test_phase1_audit_schema_and_repair.py::test_genesis_published_orphan_can_be_registered` proves a valid genesis artifact published before registration failure has an explicit audited recovery path. |
| 30. Successful wake commits an exact pending boundary | Canonical fixture boundaries are asserted; the first post-rollback new-lineage wake also commits and stabilizes an exact new checkpoint. |
| 31. No later wake advances while checkpoint is pending | `tests/test_pending_second_wake_rejection.py` proves the next wake is zero-clock rejected until the existing published orphan is repaired, after which the same queued input proceeds once. |
| 32. Invalid checkpoint is not stable | Digest, directory identity, manifest, database integrity, foreign keys, and repaired protected-schema fingerprint tests reject invalid artifacts. |
| 33. Checkpoint validation covers protected identity and boundary | Initialization, lifecycle, repair, export, and rollback stages revalidate identity, lineage, registry metadata, digest, event boundary, required protected table/trigger definitions, singleton cardinality, budget configuration, seed layout, and action registry. |
| 34. Checkpoint failure preserves committed pending state | Timeout preserves the committed pending state and blocks later wakes. Audit regressions prove genesis, ordinary, and maintenance-bound published orphans can be registered idempotently without direct retry collision. |
| 35. Retention is bounded and safe | Ordinary and repaired registration use one pruning policy. `tests/test_phase1_audit_retention_and_storage.py::test_repaired_checkpoint_runs_the_same_retention_policy` restores four checkpoints after repaired registration; the post-commit cleanup test records explicit maintenance and proves bounded reconciliation. ADR 0007 continues to retain the single rollback evidence set. |
| 36–38. Rollback archive, lineage, and failure recovery | Slices 17–22 protect archive, durable intent, exact source restoration, new-lineage transformation, atomic replacement, interrupted replacement/completion recovery, completion, restored wakeability, and first new-lineage checkpoint. The audit working-set test proves later checkpoint accounting includes retained rollback archives and restore candidates. |
| 39. Protected authority cannot be modified by organism | `tests/test_protected_authority.py` applies the production action-scoped SQLite authorizer, permits only registered garden mutations, and denies protected identity, budget, action, inbox, event, registry, schema, trigger, and new-table changes before effect. |
| 40. No organism-writable external workspace | `tests/test_no_external_workspace.py` proves the executor receives no path/workspace handle and does not invoke filesystem, temporary-file, network, subprocess, or process-launch surfaces. |
| 41. Administration is distinguishable | `tests/test_authority_provenance.py` protects exact `organism:` and `administration:` namespaces, event/inbox classification, early rejection, and all fourteen CLI report mappings. |

## Independent completion-audit storage protections

The six Issue #56 findings also required cross-cutting budget evidence that is not represented by one separate §15 row:

- `tests/test_phase1_audit_retention_and_storage.py::test_enqueue_rolls_back_before_crossing_active_database_limit` proves the public administrative enqueue path cannot strand a sleeping organism above the 8 MiB canonical limit.
- `tests/test_phase1_audit_working_set.py::test_runtime_working_set_counts_sidecars_and_retained_rollback_evidence` proves the common 64 MiB accountant includes SQLite sidecars, checkpoints and staging, rollback archives, and restore candidates before later checkpoint stabilization.

PR #54 established the original complete matrix and run 317 passed **142 protected tests in 7.25 seconds**. PR #57 head `4bb632a226dd8891fbd71aec345b1298777e3614` passed clean editable installation, compileall, genesis CLI smoke, and **150 protected tests in 8.74 seconds** in GitHub Actions run 335.

Every future change to the Phase 1 baseline must preserve all 41 rows and the independent-audit regression protections, or deliberately revise the contract or an accepted ADR through review.
