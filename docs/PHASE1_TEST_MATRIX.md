# Phase 1 Contract Evaluation Matrix

Status: **Slices 1–35 plus the independent completion-audit repairs are implemented and verified on PR #57 — all 41 fixed Phase 1 evaluations complete**

This matrix maps Minimal Organism Contract v0.2 §15 evaluations to protected tests. Complete coverage means the fixed Phase 1 boundary is implemented; it does not claim learning, intelligence, personality, or caregiver independence.

| Contract evaluation | Protected test status |
| --- | --- |
| 1. Identical declared inputs produce identical canonical results | `tests/test_repeated_run_equivalence.py::test_identical_declared_inputs_produce_exact_first_wake_results` requires two independent complete first-water runs with identical declared inputs to produce identical results, canonical rows, SQLite sequence state, active database digest, checkpoint manifests and artifacts, and next-input acceptance. |
| 2. Unexpected clock reads fail | Lifecycle and administrative tests use exhausted fake clocks on rejection paths and exact declared read counts on accepted paths. Invalid authority, pending-state wake rejection, inspection, export, archive preparation, rollback source/candidate operations, repeated completion, and interrupted retention-reconciliation retry reject or recover without hidden clock reads. |
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
| 17. No negative counters | SQLite constraints and exact transition assertions cover all implemented paths. Audit repairs reject administrative enqueue before crossing the active limit or consuming the reserved next-wake headroom and roll back inbox/event rows. |
| 18. Action attempt is charged before execution | `tests/test_action_failure_savepoint.py`. |
| 19. Savepoint removes partial mutation while preserving failure cost | `tests/test_action_failure_savepoint.py`. |
| 20. Budget exhaustion occurs before forbidden mutation | `tests/test_budget_exhaustion.py` and cleanup-grace tests prove the executor is never entered after normal-work exhaustion. |
| 21. Failure streak and maintenance threshold | Slices 5–12 protect increments, reset, exact threshold entry, inspection, and clear; rollback completion resets restored failure state. `test_maintenance_bound_pending_orphan_repairs_to_stable_maintenance` proves a published third-failure boundary stabilizes as maintenance. |
| 22. Atomic state/event commit | Genesis, lifecycle, maintenance clear, pending repair, rollback stages, cleanup-grace rollback, process-exit rollback, enqueue rollback, and two-step retention reconciliation preserve their declared canonical transaction boundaries. |
| 23. Sequence order is canonical | Lifecycle and administrative events are sequence-asserted; rollback preserves source history; retention cleanup completion references its exact pending audit event sequence. |
| 24. Event update/delete rejected | Existing append-only tests plus audit schema tests reject missing required triggers and unexpected mutating triggers while established side-effect-free fault-injection guards remain usable. |
| 25. JSONL export deterministic and non-canonical | `tests/test_event_export.py` proves exact stable-boundary validation, byte-identical output, atomic publication, isolation, and preserved wakeability. |
| 26. Competing wake has one winner and one non-queued rejection | Wake and every write-owning rollback administration boundary use protected fail-fast competing-writer rejection. |
| 27. Crash before commit preserves prior state | `tests/test_process_crash_rollback.py` proves exact rollback and released ownership. Retention reconciliation separately protects the filesystem-after-commit boundary through durable pending evidence and retry. |
| 28. Nested wake is rejected | `tests/test_nested_wake_rejection.py` proves nested acquisition and a hidden writer fail without queued work and preserve exact body/artifacts. |
| 29. Stable genesis checkpoint before wakeable | Initialization protects the normal path; `test_genesis_published_orphan_can_be_registered` protects recovery from publication-before-registration failure. |
| 30. Successful wake commits an exact pending boundary | Canonical fixture boundaries and the first post-rollback new-lineage checkpoint are exact. |
| 31. No later wake advances while checkpoint is pending | `tests/test_pending_second_wake_rejection.py` proves zero-clock rejection until explicit orphan repair. |
| 32. Invalid checkpoint is not stable | Digest, directory identity, manifest, integrity, foreign keys, and protected-schema fingerprint checks reject invalid artifacts. |
| 33. Checkpoint validation covers protected identity and boundary | Initialization, lifecycle, repair, export, and rollback revalidate identity, lineage, registry metadata, digest, event boundary, protected schema, singleton cardinality, budget configuration, seed layout, and action registry. |
| 34. Checkpoint failure preserves committed pending state | Timeout preserves pending state; genesis, ordinary, and maintenance-bound published orphans have explicit idempotent registration repair. |
| 35. Retention is bounded and safe | Normal and repaired registration share one pruning policy. Post-commit cleanup failure records maintenance. Reconciliation first commits a pending audit, then deletes staging, then commits a linked completion; retry after deletion-before-completion finishes without another clock read. |
| 36–38. Rollback archive, lineage, and failure recovery | Slices 17–22 protect archive, durable intent, source restoration, new lineage, atomic replacement, interruption recovery, completion, restored wakeability, and first new-lineage checkpoint. Working-set tests include retained rollback evidence. |
| 39. Protected authority cannot be modified by organism | `tests/test_protected_authority.py` permits only registered garden mutations and denies protected identity, budget, action, inbox, event, registry, schema, trigger, and new-table changes before effect. |
| 40. No organism-writable external workspace | `tests/test_no_external_workspace.py` proves the executor receives no path/workspace handle and does not invoke filesystem, temporary-file, network, subprocess, or process-launch surfaces. |
| 41. Administration is distinguishable | `tests/test_authority_provenance.py` protects exact `organism:` and `administration:` namespaces, event/inbox classification, early rejection, and all fourteen CLI report mappings. |

## Independent completion-audit storage and recovery protections

The Issue #56 findings also require cross-cutting evidence not represented by one separate §15 row:

- `test_enqueue_rolls_back_before_crossing_active_database_limit` proves public enqueue cannot cross the 8 MiB active-database limit.
- `test_enqueue_keeps_one_bounded_wake_of_active_database_headroom` proves the last accepted enqueue leaves a full bounded-wake reserve and the oldest accepted input can still complete and checkpoint.
- `test_post_commit_retention_cleanup_is_explicit_and_reconcilable` proves cleanup failure is visible maintenance and can be reconciled.
- `test_retention_reconciliation_retries_after_delete_before_completion_audit` proves deletion-before-completion interruption leaves durable pending evidence and retry appends exactly one linked completion without a clock read.
- `test_runtime_working_set_counts_sidecars_and_retained_rollback_evidence` proves the 64 MiB accountant includes SQLite sidecars, checkpoints/staging, rollback archives, and restore candidates.

PR #54 established the original complete matrix with 142 tests. PR #57 run 340 at head `b8ce12843d9692e50e770735d00f4b5379425eca` passed clean installation, compileall, genesis CLI smoke, and **152 protected tests in 10.32 seconds**.

Every future change to the Phase 1 baseline must preserve all 41 rows and the independent-audit regression protections, or deliberately revise the contract or an accepted ADR through review.
