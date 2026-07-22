# Phase 1 Contract Evaluation Matrix

Status: **Slices 1–18 implemented — Phase 1 incomplete**

This matrix maps Minimal Organism Contract v0.2 §15 evaluations to protected tests. Partial coverage is labeled honestly and is not evidence that the full evaluation has passed.

| Contract evaluation | Protected test status |
| --- | --- |
| 1. Identical declared inputs produce identical canonical results | Partial: deterministic initialization, the canonical three-wake policy, blocked-state, resource-aware recovery, classified action-failure, classified budget-exhaustion, maintenance-threshold, exact maintenance-inspection outcomes, and byte-identical repeated JSONL export are covered; full repeated-run canonical equivalence remains planned |
| 2. Unexpected clock reads fail | `tests/test_clock.py::test_unexpected_clock_read_fails`; successful wakes consume five declared readings including the pre-action deadline check; the classified exhausted wake consumes four; maintenance inspection, JSONL export, and rollback archive preparation consume no clock; rollback begin consumes one reading only after complete validation, while all protected rejection paths consume zero |
| 3. Backward wall time does not reorder events | Event sequence is canonical; complete first-wake backward-time scenario remains planned |
| 4. Seed does not change seed-garden behavior | Fixed first-water policy ignores the declared seed; explicit comparative test remains planned |
| 5. One tick/observation/attempt/mutation maximum | water and harvest assert one attempt/mutation; abstentions and maintenance-threshold entry assert zero; classified action failure asserts one attempt and zero successful mutations; classified pre-action exhaustion asserts zero attempts and mutations |
| 6. Twelve-step and monotonic deadline | First-water ledger records twelve steps; `tests/test_budget_exhaustion.py::test_lifecycle_budget_exhaustion_prevents_action_and_checkpoints` proves typed lifecycle deadline exhaustion before action |
| 7. Cleanup grace is not action time | Planned with classified failure and cleanup tests |
| 8. Hard-zero external capabilities | water, harvest, both abstentions, recovery, classified action failure, classified budget exhaustion, and maintenance-threshold entry assert zero caregiver, network, subprocess, and external-write consumption |
| 9. No independent energy field | `tests/test_initialization.py::test_canonical_state_has_no_energy_column` |
| 10. First canonical tick waters `bed-a` | `tests/test_first_water_success.py::test_first_water_wake_commits_evaluates_and_checkpoints` |
| 11. Second canonical tick harvests `bed-b` | `tests/test_second_harvest_success.py::test_second_wake_harvests_and_completes_objective` |
| 12. Third canonical tick abstains after completion | `tests/test_objective_complete_boundary.py::test_third_wake_abstains_after_objective_completion` |
| 13. Lexicographic tie breaking | Initial sorted observation and first-water target are covered; altered insertion-order action scenario remains planned |
| 14. Resource-aware harvest fallback | `tests/test_resource_aware_recovery.py::test_resource_aware_harvest_recovers_and_resets_failure_streak` proves zero water removes all water targets while `bed-b` remains an executable harvest target |
| 15. Specific no-applicable-action abstention | `tests/test_no_applicable_action.py::test_no_applicable_action_abstains_and_increments_failure_once`; the companion evaluator test rejects abstention when a protected action is executable |
| 16. Duplicate external tick never creates another action | Idempotent enqueue is protected; complete post-action replay scenario remains planned |
| 17. No negative counters | SQLite constraints and exact success, abstention, recovery, action-failure, budget-exhaustion, maintenance-threshold, and maintenance-clear transitions cover all implemented paths |
| 18. Action attempt is charged before execution | `tests/test_action_failure_savepoint.py::test_classified_action_failure_rolls_back_partial_write_and_preserves_cost` proves the attempt remains charged after the injected failure |
| 19. Savepoint removes partial mutation while preserving failure cost | `tests/test_action_failure_savepoint.py::test_classified_action_failure_rolls_back_partial_write_and_preserves_cost` proves the partial plot write disappears while attempt cost remains and successful mutation cost returns to zero |
| 20. Budget exhaustion occurs before forbidden mutation | `tests/test_budget_exhaustion.py::test_lifecycle_budget_exhaustion_prevents_action_and_checkpoints` proves the lifecycle work deadline is detected before action proposal, attempt, mutation reservation, or environment write |
| 21. Failure streak and maintenance threshold | Completion abstention proves justified zero; Slices 6, 8, and 9 prove classified increments; Slice 7 proves successful reset; Slice 10 proves exact two-to-three threshold entry; Slice 11 leaves maintenance unchanged; maintenance clear proves explicit reset from three to zero |
| 22. Atomic state/event commit | Genesis and classified lifecycle commits are protected; maintenance clear proves state and audit event atomicity; pending repair proves registry, stable-boundary, status, and audit atomicity; `tests/test_rollback_intent.py::test_begin_failure_rolls_back_status_and_audit_event_together` proves `rollback_in_progress` and `rollback_started` commit or roll back together |
| 23. Sequence order is canonical | Genesis, canonical lifecycles, blocked-state, recovery, classified failures, maintenance, retention, repair, and rollback-start sequences are asserted; JSONL export is ordered only by canonical `event_sequence`; rollback begin requires its event at the exact next sequence |
| 24. Event update/delete rejected | `tests/test_initialization.py::test_event_history_rejects_update_and_delete` |
| 25. JSONL export deterministic and non-canonical | `tests/test_event_export.py` proves declared stable-boundary validation, canonical byte-identical output, atomic publication, isolation from canonical state, and preserved wakeability |
| 26. Competing wake has one winner and one non-queued rejection | `tests/test_wake.py::test_competing_wake_is_rejected_and_not_queued`; rollback preparation and begin also have protected fail-fast competing-writer rejection |
| 27. Crash before commit preserves prior state | Transaction/context rollback is covered; process-crash test remains planned |
| 28. Nested wake is rejected | Planned |
| 29. Stable genesis checkpoint before wakeable | Initialization and genesis checkpoint tests |
| 30. Successful wake commits an exact pending boundary | Water validates 13, harvest 24, completion abstention 34, blocked fixture 16, recovery fixture 17, action-failure fixture 17, budget-exhaustion fixture 16, and maintenance-threshold fixture 17 |
| 31. No later wake advances while checkpoint is pending | Pending state and repair rejection are protected; JSONL export, rollback preparation, and rollback begin reject pending state without mutation; rollback-in-progress normal wakes also reject before clock or claim |
| 32. Invalid checkpoint is not stable | Digest and directory-name mismatch tests |
| 33. Checkpoint validation covers protected identity and boundary | Genesis and lifecycle checkpoint validation, pending repair, JSONL export, rollback preparation, and rollback begin all validate their declared protected checkpoint boundaries; rollback begin additionally revalidates the immutable selected source after archive publication |
| 34. Checkpoint failure preserves committed pending state | Checkpoint timeout preserves pending state; pending-checkpoint repair proves exact administrative registration repair of the published artifact |
| 35. Retention is bounded and safe | Successful pruning and classified pruning failure are protected; pre-rollback archives remain outside checkpoint registry and ordinary retention |
| 36–38. Rollback archive, lineage, and failure recovery | Partial: Slice 17 proves source selection and complete verified pre-rollback archive publication. Slice 18 proves archive and active-body revalidation, exact canonical SQLite schema/table/`sqlite_sequence` equality, atomic `rollback_in_progress` plus `rollback_started`, active-drift/foreign/unsafe/busy/pending/repeated rejection, post-event failure rollback, and normal-wake blocking. Restore candidate construction, lineage transformation, active replacement, completion history, and post-replacement recovery remain planned |
| 39. Protected authority cannot be modified by organism | Protected actions and evaluators are used; maintenance, repair, export, rollback preparation, and rollback begin are explicit administrative boundaries; broader authority tests remain planned |
| 40. No organism-writable external workspace | Canonical organism paths remain SQLite-only; JSONL exports and pre-rollback archives are administrative non-canonical artifacts never read or written by organism runtime |
| 41. Administration is distinguishable | Administrative event sources are explicit. Rollback preparation intentionally creates no canonical event; rollback begin records exactly one typed `rollback_started` event from `administration:rollback` |

PR #32 passed GitHub Actions on Python 3.12 with **72 protected tests** on the implementation head.

Every future pull request must update this matrix when it adds or changes protected tests.
