# Phase 1 Contract Evaluation Matrix

Status: **Slices 1–3 implemented — Phase 1 incomplete**

This matrix maps Minimal Organism Contract v0.2 §15 evaluations to protected tests. Partial coverage is labeled honestly and is not evidence that the full evaluation has passed.

| Contract evaluation | Protected test status |
| --- | --- |
| 1. Identical declared inputs produce identical canonical results | Partial: deterministic initialization, input, observation, and first-water policy are protected; full repeated-run equivalence remains planned |
| 2. Unexpected clock reads fail | `tests/test_clock.py::test_unexpected_clock_read_fails`; `tests/test_first_water_success.py` proves the successful wake consumes four declared readings |
| 3. Backward wall time does not reorder events | Event sequence is canonical; complete first-wake backward-time scenario remains planned |
| 4. Seed does not change seed-garden behavior | Fixed first-water policy ignores the declared seed; explicit comparative test remains planned |
| 5. One tick/observation/attempt/mutation maximum | `tests/test_first_water_success.py` asserts the exact first-water budget ledger |
| 6. Twelve-step and monotonic deadline | First-water ledger records twelve steps; lifecycle deadline failure history remains planned |
| 7. Cleanup grace is not action time | Planned with classified failure and cleanup tests |
| 8. Hard-zero external capabilities | `tests/test_first_water_success.py` asserts zero caregiver, network, subprocess, and external-write consumption |
| 9. No independent energy field | `tests/test_initialization.py::test_canonical_state_has_no_energy_column` |
| 10. First canonical tick waters `bed-a` | `tests/test_first_water_success.py::test_first_water_wake_commits_evaluates_and_checkpoints` |
| 11. Second canonical tick harvests `bed-b` | Planned for Slice 4 |
| 12. Third canonical tick abstains after completion | Planned |
| 13. Lexicographic tie breaking | Initial sorted observation and first-water target are covered; altered insertion-order action scenario remains planned |
| 14. Resource-aware harvest fallback | Planned |
| 15. Specific no-applicable-action abstention | Planned |
| 16. Duplicate external tick never creates another action | Idempotent enqueue is protected; complete post-action replay scenario remains planned |
| 17. No negative counters | SQLite constraints and exact first-water ledger assertions cover the successful path |
| 18. Action attempt is charged before execution | Implemented in protected action execution; injected action-failure assertion remains planned |
| 19. Savepoint removes partial mutation while preserving failure cost | Implemented; explicit protected failure test remains planned |
| 20. Budget exhaustion occurs before forbidden mutation | Checkpoint deadline is tested separately; lifecycle budget-exhaustion outcome remains planned |
| 21. Failure streak and maintenance threshold | Planned |
| 22. Atomic state/event commit | Genesis transaction and rollback-only wake preparation are protected; injected action-failure lifecycle test remains planned |
| 23. Sequence order is canonical | Genesis and complete first-water event sequences are asserted |
| 24. Event update/delete rejected | `tests/test_initialization.py::test_event_history_rejects_update_and_delete` |
| 25. JSONL export deterministic and non-canonical | Planned |
| 26. Competing wake has one winner and one non-queued rejection | `tests/test_wake.py::test_competing_wake_is_rejected_and_not_queued` |
| 27. Crash before commit preserves prior state | Transaction/context rollback is covered; process-crash test remains planned |
| 28. Nested wake is rejected | Planned |
| 29. Stable genesis checkpoint before wakeable | Initialization and genesis checkpoint tests |
| 30. Successful wake commits an exact pending boundary | `tests/test_first_water_success.py` validates active and checkpoint boundary sequence 13 |
| 31. No later wake advances while checkpoint is pending | Pending status is preserved by timeout test; explicit second-wake rejection remains planned |
| 32. Invalid checkpoint is not stable | Digest and directory-name mismatch tests |
| 33. Checkpoint validation covers protected identity and boundary | Genesis tests plus first lifecycle checkpoint validation |
| 34. Checkpoint failure preserves committed pending state | `tests/test_checkpoint_timeout.py::test_checkpoint_timeout_preserves_committed_pending_boundary` |
| 35. Retention is bounded and safe | Limits are stored and publication size is enforced; pruning behavior remains planned |
| 36–38. Rollback archive, lineage, and failure recovery | Planned |
| 39. Protected authority cannot be modified by organism | Fixed action definition and independent evaluator are used; broader authority tests remain planned |
| 40. No organism-writable external workspace | SQLite-only first-water action and hard-zero ledger cover the successful path |
| 41. Administration is distinguishable | Input and checkpoint events use administrative sources; lifecycle events use the organism fixed-policy source |

PR #17 passed GitHub Actions on Python 3.12 with **25 protected tests**.

Every future pull request must update this matrix when it adds or changes protected tests.
