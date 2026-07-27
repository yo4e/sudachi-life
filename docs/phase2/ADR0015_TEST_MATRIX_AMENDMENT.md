# ADR 0015 Phase 2 Test-Matrix Amendment

Status: **Accepted with ADR 0015 on 2026-07-27**

This document synchronizes the protected Phase 2 evidence map with ADR 0015. It replaces only the typed-result portion of P2-D07.

| ID | Accepted protected requirement | Required evidence |
| --- | --- | --- |
| P2-D07 | Four requests are permitted per current lineage. An otherwise eligible fifth no-action request wake returns the exact noncanonical reason `consultation_request_not_created_lineage_request_limit`, creates no fifth consultation mutation, and still commits the frozen Phase 1 core and ordinary checkpoint | Legitimate four-cycle fixture followed by a fifth eligible wake; exact result object; before/after consultation rows/events/cost/logical bytes; Phase 1 core/checkpoint equality; no private count or ordinal mutation |

Additional protected evidence:

- the typed result is not used for schema-v1, zero-caregiver, applicable-action, objective-complete, maintenance-entering, or outstanding-request paths;
- storage refusal retains its distinct exact reason;
- historical old-lineage rows do not trigger the current-lineage refusal;
- a fresh post-rollback lineage starts with ordinal one;
- all original 152 Phase 1 tests remain unchanged and passing.