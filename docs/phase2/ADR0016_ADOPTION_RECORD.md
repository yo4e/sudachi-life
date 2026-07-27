# ADR 0016 Adoption Record

Date: 2026-07-27

Issue #112 identified that P2-J09's canonical-at-64-KiB scenario became unreachable after Protocol v1 request, provenance, proposal, and package fields were closed and finite cycles remained capped at four.

Under the project owner's standing routine-clarification delegation, the smallest deterministic resolution is formally adopted as ADR 0016:

- retain the exact 64 KiB hard guard and one-over rejection in one pure accounting function;
- separately measure the exact reachable four-cycle Protocol-v1 maximum below the limit;
- prove runtime linkage to independently measured canonical request and successful-package bytes;
- forbid filler, forged packages, direct consultation mutation, and metadata double counting.

The accepted decision is recorded in:

- `docs/decisions/0016-fix-legal-lineage-payload-boundary-evidence.md`;
- `docs/phase2/ADR0016_TEST_MATRIX_AMENDMENT.md`.

This adoption changes no schema, request/package shape, finite limit, lineage rule, authority, Phase 1 behavior, or external capability.

Issue #112 closes after the documentation PR merges with protected CI.