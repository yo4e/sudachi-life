# Phase 1 Contract Evaluation Matrix

Status: **Slices 1–24 implemented and verified — Phase 1 incomplete**

This matrix maps Minimal Organism Contract v0.2 §15 evaluations to protected tests. Partial coverage is labeled honestly and is not evidence that the full evaluation has passed.

| Contract evaluation | Protected test status |
| --- | --- |
| 1. Identical declared inputs produce identical canonical results | Partial: deterministic initialization, the canonical three-wake policy, blocked-state, classified failures, maintenance, byte-identical JSONL export, deterministic rollback candidates, exact repeated replacement, and exact repeated completion are covered; full repeated-run canonical equivalence remains planned |
| 2. Unexpected clock reads fail | Lifecycle clock counts are protected; maintenance inspection, export, archive preparation, source-candidate construction, active replacement, repeated completion, and completed-rollback preparation rejection consume no clock; rollback begin, candidate transformation, and first completion read their declared clock only after complete validation; rejection paths consume zero |
| 3. Backward wall time does not reorder events | `tests/test_backward_wall_time_ordering.py::test_backward_wall_time_does_not_reorder_complete_first_wake` runs the complete first-water lifecycle and checkpoint with repeatedly decreasing wall timestamps, increasing monotonic readings, exact event sequences 1–14, and stable sleep |
| 4. Seed does not change seed-garden behavior | Fixed first-water policy ignores the declared seed; explicit comparative test remains planned |
| 5. One tick/observation/attempt/mutation maximum | Water and harvest assert one attempt/mutation; abstentions and maintenance-threshold entry assert zero; classified action failure asserts one attempt and zero successful mutations; classified pre-action exhaustion asserts zero attempts and mutations |
| 6. Twelve-step and monotonic deadline | First-water ledger records twelve steps; `tests/test_budget_exhaustion.py::test_lifecycle_budget_exhaustion_prevents_action_and_checkpoints` proves typed lifecycle deadline exhaustion before action |
| 7. Cleanup grace is not action time | Planned with classified failure and cleanup tests |
| 8. Hard-zero external capabilities | Water, harvest, abstentions, recovery, classified failures, and maintenance-threshold entry assert zero caregiver, network, subprocess, and external-write consumption |
| 9. No independent energy field | `tests/test_initialization.py::test_canonical_state_has_no_energy_column` |
| 10. First canonical tick waters `bed-a` | `tests/test_first_water_success.py::test_first_water_wake_commits_evaluates_and_checkpoints` |
| 11. Second canonical tick harvests `bed-b` | `tests/test_second_harvest_success.py::test_second_wake_harvests_and_completes_objective` |
| 12. Third canonical tick abstains after completion | `tests/test_objective_complete_boundary.py::test_third_wake_abstains_after_objective_completion` |
| 13. Lexicographic tie breaking | Initial sorted observation and first-water target are covered; altered insertion-order action scenario remains planned |
| 14. Resource-aware harvest fallback | `tests/test_resource_aware_recovery.py::test_resource_aware_harvest_recovers_and_resets_failure_streak` |
| 15. Specific no-applicable-action abstention | `tests/test_no_applicable_action.py::test_no_applicable_action_abstains_and_increments_failure_once`; the companion evaluator test rejects abstention when an action is executable |
| 16. Duplicate external tick never creates another action | Idempotent enqueue is protected; complete post-action replay scenario remains planned |
| 17. No negative counters | SQLite constraints and exact implemented transitions cover all implemented paths |
| 18. Action attempt is charged before execution | `tests/test_action_failure_savepoint.py::test_classified_action_failure_rolls_back_partial_write_and_preserves_cost` |
| 19. Savepoint removes partial mutation while preserving failure cost | `tests/test_action_failure_savepoint.py::test_classified_action_failure_rolls_back_partial_write_and_preserves_cost` |
| 20. Budget exhaustion occurs before forbidden mutation | `tests/test_budget_exhaustion.py::test_lifecycle_budget_exhaustion_prevents_action_and_checkpoints` |
| 21. Failure streak and maintenance threshold | Slices 5–12 protect justified zero, classified increments, successful reset, exact threshold entry, inspection, and explicit clear; rollback completion resets restored failure and maintenance state before wakeability |
| 22. Atomic state/event commit | Genesis and lifecycle commits are protected; maintenance clear and pending repair are atomic; rollback intent commits status and `rollback_started` together; candidate transformation commits isolated lineage and restoration history together; active replacement transfers a validated body atomically; Slice 22 proves `sleeping` and `rollback_completed` commit or roll back together |
| 23. Sequence order is canonical | Canonical lifecycles and administrative events are sequence-asserted; Slice 24 proves exact order under decreasing wall timestamps; rollback preserves source history, appends `rollback_lineage_prepared` at source plus one, and appends `rollback_completed` at exactly the next sequence |
| 24. Event update/delete rejected | `tests/test_initialization.py::test_event_history_rejects_update_and_delete` |
| 25. JSONL export deterministic and non-canonical | `tests/test_event_export.py` proves stable-boundary validation, canonical byte-identical output, atomic publication, isolation, and preserved wakeability |
| 26. Competing wake has one winner and one non-queued rejection | Wake and every write-owning rollback administrative boundary through completion have protected fail-fast competing-writer rejection |
| 27. Crash before commit preserves prior state | Transaction/context rollback is covered; Slice 21 protects both sides of authority transfer; Slice 22 protects status/event rollback before completion commit; process-crash execution remains planned |
| 28. Nested wake is rejected | Planned |
| 29. Stable genesis checkpoint before wakeable | Initialization and genesis checkpoint tests |
| 30. Successful wake commits an exact pending boundary | Canonical wake fixture boundaries are asserted; Slice 22 additionally proves the first post-rollback new-lineage wake commits and stabilizes a new checkpoint |
| 31. No later wake advances while checkpoint is pending | Pending-state rejection is protected; rollback remains non-wakeable through replacement and becomes wakeable only after atomic completion |
| 32. Invalid checkpoint is not stable | Digest and directory-name mismatch tests |
| 33. Checkpoint validation covers protected identity and boundary | Initialization, lifecycle, repair, export, and all rollback stages revalidate declared checkpoint identity, lineage, registry metadata, digest, and event boundary; first post-rollback checkpoint is new-lineage validated |
| 34. Checkpoint failure preserves committed pending state | Checkpoint timeout preserves pending state; pending-checkpoint repair proves exact registration repair |
| 35. Retention is bounded and safe | Ordinary checkpoint pruning and classified pruning failure are protected. ADR 0007 permits one completed rollback per organism, retains the complete archive and candidate evidence set, and forbids Phase 1 rollback-artifact pruning. `tests/test_single_rollback_retention.py` proves second preparation rejects before source selection or second-archive creation while a separately initialized organism remains independently eligible |
| 36–38. Rollback archive, lineage, and failure recovery | Slices 17–22 protect the complete rollback path: abandoned-future archive, durable intent, exact source restoration, new-lineage transformation, atomic active replacement, immediate validation, recoverable post-transfer interruption, atomic `rollback_completed`, restored wakeability, and a first successful new-lineage checkpoint. Slice 23 enforces ADR 0007 at preparation without changing the first path or its evidence |
| 39. Protected authority cannot be modified by organism | Protected actions and evaluators are used; every rollback operation is an explicit offline administrative boundary; broader authority tests remain planned |
| 40. No organism-writable external workspace | Canonical organism paths remain SQLite-only; exports, archives, and candidates are administrative artifacts never read or written by normal runtime |
| 41. Administration is distinguishable | Sources are explicit. Rollback preparation and source-candidate construction create no event; rollback begin records `rollback_started`; transformation records `rollback_lineage_prepared`; replacement creates no event; completion records `rollback_completed` from `administration:rollback`; completed-history admission rejection creates no event |

PR #39 GitHub Actions run 225 passed on Python 3.12 with clean editable installation, compileall, genesis CLI smoke, and **118 protected tests**. No implementation correction was required.

Every future pull request must update this matrix when it adds or changes protected tests.
