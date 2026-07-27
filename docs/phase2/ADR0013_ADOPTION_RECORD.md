# ADR 0013 Adoption Record

Date: 2026-07-27

The project owner explicitly adopted the recommended clarification in Issue #105:

> Issue #105's recommended clarification is formally adopted.

The accepted decision is recorded normatively in:

- `docs/decisions/0013-fix-disposition-wake-evidence.md`;
- `docs/phase2/ADR0013_TEST_MATRIX_AMENDMENT.md`.

This adoption authorizes the test-first Slice 41 implementation of the exact separate disposition wake. It does not authorize action execution, garden mutation, memory or skill creation, live caregiver/model/API use, network, subprocess, retry, migration, rollback, new writer categories, or any weakening of the unchanged Phase 1 controls.

Issue #105 closes only after the ADR documentation PR merges.