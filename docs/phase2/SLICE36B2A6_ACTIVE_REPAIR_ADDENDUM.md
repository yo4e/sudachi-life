# Slice 36b2a6 Addendum: Pending Repair Active-Database Admission

Status: implemented on PR #73.

## Test-first evidence

After the initial absolute-limit documentation head was green, final diff review identified that pending checkpoint repair independently checked checkpoint artifact, checkpoint store, and runtime working-set limits, but did not reject an already over-limit active database.

Tests-only head `43f75db71e15aadcca76963c751009b2fe2bc842` produced GitHub Actions run 492:

- 216 tests passed
- one new test failed
- an active schema-v2-zero database at exactly 8 MiB repaired successfully
- the same logical pending state with one additional SQLite page also repaired instead of rejecting

The test changes physical allocation only. It creates a temporary padding table, allocates real pages, drops the table, and revalidates the exact protected schema and canonical pending state. The published orphan remains independently valid.

## Authorized narrow repair

The project owner's same-turn authorization covered further real-test-confirmed Phase 1 repairs limited to missing physical checks, cleanup, and no-partial-mutation invariants.

Repair head `bde72a4637849e34e28bd1b6de34c9634e7f28b0` adds two checks without changing limits or authority:

1. pending repair validates active allocation before reading the repair clock or attempting canonical writes;
2. the shared checkpoint/repair post-write guard revalidates active allocation after transaction writes and before commit.

The pre-repair pending validator remains byte-identical in `checkpoint_repair_validate_impl.py`.

GitHub Actions run 494 passed:

- 217 passed in 26.15 seconds
- exact 8 MiB active repair accepted
- one-page-over active repair rejected without registry/canonical mutation
- exact/one-over 64 MiB checkpoint and repair cases remained green
- installation, compilation, and schema-v1 genesis CLI smoke succeeded

This addendum is part of the P2-O18, P2-O19, and P2-O21 closure recorded in `SLICE36B2A6_ABSOLUTE_PHYSICAL_LIMITS.md`.
