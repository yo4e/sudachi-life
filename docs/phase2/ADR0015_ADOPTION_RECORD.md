# ADR 0015 Adoption Record

Date: 2026-07-27

Issue #111 identified that P2-D07 required a typed fifth-request refusal but the accepted documents did not define its exact public result.

Under the project owner's standing routine-clarification delegation, the smallest deterministic resolution is formally adopted as ADR 0015:

```text
consultation_request_not_created_lineage_request_limit
```

The exact noncanonical result and applicability rules are recorded in:

- `docs/decisions/0015-fix-typed-fifth-request-refusal.md`;
- `docs/phase2/ADR0015_TEST_MATRIX_AMENDMENT.md`.

This adoption changes no canonical state, request limit, Phase 1 behavior, lineage semantics, authority, or external capability. It authorizes only the public typed result and its protected evidence.

Issue #111 closes after the documentation PR merges with protected CI.