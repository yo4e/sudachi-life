# Slice 31: Nested Wake and Hidden Writer Rejection

## Purpose

Close Minimal Organism Contract v0.2 evaluation 28: nested wakes and hidden write connections must be rejected.

Phase 1 has one fail-fast write owner. A wake may not reenter itself, queue another wake, or open a hidden write path around the acquired outer transaction.

## Protected scenario

`tests/test_nested_wake_rejection.py` begins from one initialized sleeping organism with one queued tick and captures exact stable state.

The test then:

1. acquires one outer `WakeTransaction`
2. attempts nested `WakeTransaction.acquire(...)` for the same organism
3. requires typed `WakeBusyError` with the explicit not-queued message
4. opens a separate canonical connection and attempts `BEGIN IMMEDIATE`
5. requires SQLite busy or locked rejection
6. proves neither rejection consumes organism clock input
7. rolls back and closes the outer transaction
8. requires exact pre-attempt database, canonical, sequence, registry, and checkpoint-artifact equality
9. completes the original tick through the normal first-water lifecycle

## Required boundary

The protected test requires:

- no nested input claim
- no queued request or second inbox row
- no event or sequence increment
- no organism, garden, inventory, or environment mutation
- no active database byte change
- no checkpoint registry or artifact change
- no hidden retry
- one normal action only after the outer owner releases the database

The hidden connection is a protected-test probe of SQLite ownership. It is not a production connection pool or alternate authority.

## Result

The existing locking implementation passed unchanged.

`WakeTransaction.acquire(...)` converts SQLite busy or locked ownership failure into typed `WakeBusyError` and explicitly states that the rejected attempt was not queued. A raw hidden connection cannot acquire `BEGIN IMMEDIATE` while the outer wake owns the body. Closing the rejected connection and rolling back the outer transaction restores normal ownership availability.

No production source, schema, contract, clock, action, evaluator, budget, checkpoint, rollback, or connection-pool behavior changed.

## Validation

GitHub Actions run 286 on Python 3.12 passed:

- clean editable installation
- source and test compilation
- genesis CLI smoke test
- **126 protected tests in 8.88 seconds**
