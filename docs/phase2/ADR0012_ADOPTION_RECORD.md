# ADR 0012 Adoption Record

Date: 2026-07-27

The SUDACHI project owner explicitly accepted the complete recommended clarification in Issue #101:

> Issue #101の推奨clarificationを正式採用する。

The accepted scope is exactly the Issue #101 recommendation and ADR 0012:

- typed-alias receipt, completion, and terminal identifiers;
- exact success-ingress event type, source, shared sequence, receipt envelope, completion object, and two-key payload;
- exact raw rejected-package digest domain and byte preimage;
- exact terminal event type, source, shared sequence, terminal envelope, completion object, nullable fields, and reason-specific size rules;
- exact direct request/dispatch parents;
- atomicity, duplicate idempotence, conflict rejection, explicit same-byte resubmission, and interrupted-dispatch reconciliation without fixture recall;
- no checkpoint, lifecycle increment, action, maintenance clearing, authority expansion, retry, or refund.

This adoption does not broaden fixture capability, authorize live caregiver/model work, alter Phase 1, modify schema, or accept implementation without protected evidence.

Durable normative record:

- `docs/decisions/0012-fix-ingress-completion-and-terminal-evidence.md`
- `docs/phase2/ADR0012_TEST_MATRIX_AMENDMENT.md`

Issue #101 closes after the documentation PR merges. Slice 40 begins test-first only from the merged ADR 0012 state.
