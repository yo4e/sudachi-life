# Phase 1 Contract Evaluation Matrix

Status: **Slice 1 mapping — implementation incomplete**

This matrix maps Minimal Organism Contract v0.2 §15 evaluations to protected tests. A blank or planned row is not evidence of compliance.

| Contract evaluation | Protected test status |
| --- | --- |
| 1. Identical declared inputs produce identical canonical results | Planned with full wake implementation |
| 2. Unexpected clock reads fail | `tests/test_clock.py::test_unexpected_clock_read_fails` |
| 3. Backward wall time does not reorder events | Planned with event append tests |
| 4. Seed does not change seed-garden behavior | Planned with wake implementation |
| 5. One tick/observation/attempt/mutation maximum | Planned |
| 6. Twelve-step and monotonic deadline | Planned |
| 7. Cleanup grace is not action time | Planned |
| 8. Hard-zero external capabilities | Schema constants implemented; effect tests planned |
| 9. No independent energy field | `tests/test_initialization.py::test_canonical_state_has_no_energy_column` |
| 10–16. Seed-garden canonical behavior | Genesis fixture tested; wake scenarios planned |
| 17. No negative counters | SQLite checks implemented; exhaustive tests planned |
| 18–21. Attempt, savepoint, exhaustion, and failure streak | Planned |
| 22. Atomic state/event commit | Genesis transaction implemented; injected-failure tests planned |
| 23. Sequence order is canonical | Genesis sequences asserted; clock-anomaly tests planned |
| 24. Event update/delete rejected | `tests/test_initialization.py::test_event_history_rejects_update_and_delete` |
| 25. JSONL export deterministic and non-canonical | Planned |
| 26–28. Competing, crash, and nested wake locking | Planned with wake implementation |
| 29. Stable genesis checkpoint before wakeable | `tests/test_initialization.py::test_initialization_creates_contract_v0_2_genesis` |
| 30–31. Pending boundary and wake blocking | Genesis snapshot boundary tested; normal wake planned |
| 32. Invalid checkpoint not stable | `tests/test_checkpoint.py::test_checkpoint_digest_mismatch_is_rejected` |
| 33. Checkpoint validation | `tests/test_checkpoint.py::test_genesis_checkpoint_manifest_and_database_validate` |
| 34–35. Checkpoint failure and retention | Planned |
| 36–38. Rollback archive, lineage, and failure recovery | Planned |
| 39. Protected authority cannot be modified by organism | Runtime action tests planned |
| 40. No organism-writable external workspace | Directory layout implemented; effect tests planned |
| 41. Administration is distinguishable | Genesis events and checkpoint registry implemented; report tests planned |

Every future pull request must update this matrix when it adds or changes protected tests.
