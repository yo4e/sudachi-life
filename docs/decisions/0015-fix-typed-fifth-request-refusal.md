# ADR 0015: Fix the exact typed fifth-request refusal

- Status: Accepted
- Date: 2026-07-27
- Decision authority: project-owner routine clarification delegation
- Implementation issue: #61
- Clarification issue: #111

## Context

The accepted fixture configuration permits exactly four consultation requests per current lineage. P2-D07 requires an otherwise eligible fifth request attempt to be typed and non-mutating.

The existing `ConsultationRequestResult` already represents successful creation and typed storage refusal. The accepted documents did not define the fifth-limit reason or exact result, and the retained constructor returned `None` after four current-lineage request rows. That was indistinguishable from paths where consultation was not configured or request policy was not eligible.

This is a routine clarification under `docs/phase2/CLARIFICATION_DELEGATION.md`. It defines the presentation result already required by P2-D07 without changing request eligibility, canonical state, lineage limits, Phase 1 behavior, or authority.

## Decision

### 1. Exact result

For an otherwise eligible incomplete-objective `no_applicable_action` wake, when the current lineage already contains four consultation request rows, the public wake result contains exactly:

```json
{
  "canonical_size_bytes": null,
  "created": false,
  "event_sequence": null,
  "reason": "consultation_request_not_created_lineage_request_limit",
  "request_id": null
}
```

This object is noncanonical presentation only.

### 2. Exact applicability

The typed result applies only when all request-policy prerequisites are otherwise satisfied:

- schema-v2 fixture configuration is active and exact;
- the wake is not entering maintenance;
- the objective is incomplete;
- the frozen Phase 1 decision is `no_applicable_action`;
- the pre-creation budget snapshot exists and is exact;
- no current-lineage request remains outstanding under the accepted derived-state rules;
- the current-lineage request count is already four.

Current-lineage count excludes every historical old-lineage request.

### 3. Non-mutation

The fifth-limit result creates no:

- request row or request event;
- consultation source, sequence, or logical payload byte;
- dispatch, charge, fixture call, response, receipt, completion, terminal, proposal, or disposition;
- retry, queue, rollover, rollback, or hidden future work.

The unchanged Phase 1 core wake and ordinary checkpoint still commit. The failure streak and maintenance behavior remain the frozen Phase 1 result.

### 4. Other no-request paths remain distinct

Unless another accepted typed refusal applies:

- schema-v1 and zero-caregiver paths return no consultation result;
- applicable-action and objective-complete wakes return no consultation result;
- a maintenance-entering wake returns no consultation result;
- an otherwise eligible wake blocked only by an outstanding request returns no consultation result;
- storage-only refusal continues to use `consultation_request_not_created_storage_budget`.

The exact fifth-limit reason is not reused for any other condition.

### 5. Retained implementation body

The byte-identical retained constructor in `phase2_request_impl.py` remains unchanged. The public request wrapper may classify the current-lineage limit before delegation or translate the retained no-create result after independently validating exact eligibility and count.

## Superseded text

This ADR supersedes only the previously unspecified typed-result portion of P2-D07. The four-request limit and every other request rule remain unchanged.

## Consequences

- Slice 42 can prove four legal requests and one exact non-mutating fifth refusal.
- A post-rollback new lineage begins at ordinal one and does not inherit this refusal from historical rows.
- No private count or ordinal mutation is authorized.
- All original 152 Phase 1 tests remain unchanged and passing.