# ADR 0012: Fix Ingress, Completion, and Terminal Canonical Evidence

- Status: Accepted
- Date: 2026-07-27
- Owners: SUDACHI project owner and implementation record
- Supersedes: no accepted ADR
- Amends: ADRs 0008–0011 and Consultation Protocol v1 only where this ADR is explicit

## Context

The protected schema already reserves immutable rows for consultation responses, proposals, ingress receipts, cost completions, and dispatch terminals. Accepted Protocol v1 requires successful ingress or terminalization to commit one exact administrative branch atomically, but it did not enumerate every primary identifier, event type, event payload, direct parent, or invalid raw-byte digest needed to write that state.

Those values affect checkpoints, rollback, event export, idempotence, lineage logical-payload reconstruction, and provenance. They cannot be chosen privately by implementation code.

Issue #101 recorded the exact gap. On 2026-07-27 the project owner explicitly accepted its recommended clarification. This ADR is the normative durable record of that decision.

## Decision

### Typed aliases

For a dispatch identifier `consultation-dispatch:<dispatch digest>`:

```text
completion_id = "consultation-cost-completion:" + <dispatch digest>
terminal_id   = "consultation-dispatch-terminal:" + <dispatch digest>
```

For a valid external-package digest `<package digest>`:

```text
receipt_id = "consultation-ingress-receipt:" + <package digest>
```

These aliases reuse already-derived unique digests. They add no new digest label, dependency edge, or cycle.

### Successful ingress

Successful ingress uses:

- event type `consultation_response_ingressed`;
- source `administration:consultation.response_ingress`;
- the current committed lifecycle number without incrementing lifecycle;
- one event sequence shared by the event row, response row, ingress-receipt row, and receipt envelope;
- no separate proposal event.

The event payload contains exactly `completion` and `receipt`.

The successful completion object contains exactly:

```json
{
  "completion_id": "consultation-cost-completion:<dispatch digest>",
  "dispatch_id": "<linked dispatch ID>",
  "measured_package_bytes": 0,
  "response_id": "<validated response ID>"
}
```

The receipt envelope contains exactly:

```json
{
  "authority": {
    "source": "administration:consultation.response_ingress",
    "writer_category": "administration"
  },
  "dispatch_id": "<linked dispatch ID>",
  "event_sequence": 1,
  "measured_package_bytes": 0,
  "package_digest": "<external-package digest>",
  "parent_event_sequences": [1, 2],
  "protocol_version": 1,
  "receipt_id": "consultation-ingress-receipt:<package digest>",
  "receipt_schema": "sudachi.consultation.ingress_receipt/v1",
  "request_id": "<linked request ID>",
  "response_id": "<validated response ID>"
}
```

`parent_event_sequences` contains exactly two sorted unique direct parents: the linked request-creation event sequence and dispatch-admission event sequence.

Raw input bytes must equal independently reconstructed canonical external-package bytes. `measured_package_bytes` equals both raw length and canonical package length. One transaction atomically records the response, optional proposal, receipt, completion, and event. `unavailable` uses the same evidence, has no proposal, and is final without disposition.

### Rejected raw package digest

For attempted package bytes that cannot be accepted as the exact canonical package:

```text
rejected_package_digest = sha256(
    UTF8("sudachi.consultation/v1\nrejected-package-bytes\n")
    || raw_package_bytes
)
```

This digest is over exact raw bytes. It is case-sensitive, performs no JSON parse, uses no NUL separator or alternate prefix, and is distinct from `H("external-package", canonical_package)`.

### Terminalization

Terminalization uses:

- event type `consultation_dispatch_terminalized`;
- source `administration:consultation.dispatch_terminal`;
- the current committed lifecycle number without incrementing lifecycle;
- one event sequence shared by the event row, terminal row, and terminal envelope;
- event payload exactly `completion` and `terminal`.

The terminal envelope contains exactly:

```json
{
  "authority": {
    "source": "administration:consultation.dispatch_terminal",
    "writer_category": "administration"
  },
  "dispatch_id": "<linked dispatch ID>",
  "event_sequence": 1,
  "lineage_generation": 0,
  "organism_id": "<linked organism ID>",
  "parent_event_sequences": [1, 2],
  "protocol_version": 1,
  "reason_code": "dispatch_interrupted | fixture_output_invalid | expired_before_ingress",
  "rejected_package_digest": null,
  "rejected_package_size_bytes": null,
  "request_id": "<linked request ID>",
  "terminal_id": "consultation-dispatch-terminal:<dispatch digest>",
  "terminal_schema": "sudachi.consultation.dispatch_terminal/v1"
}
```

The two rejected-package fields are the only explicitly nullable Protocol-v1 fields. Direct parents are exactly the sorted linked request-creation and dispatch-admission event sequences.

Reason rules are exact:

- `dispatch_interrupted`: no package bytes; both rejected fields are null; completion measured bytes are zero;
- `fixture_output_invalid`: raw package bytes are required; rejected digest uses the raw-byte formula; rejected size and completion measured bytes equal raw length;
- `expired_before_ingress`: attempted raw package bytes are required; rejected digest uses the raw-byte formula; rejected size and completion measured bytes equal raw length.

The terminal completion object contains exactly:

```json
{
  "completion_id": "consultation-cost-completion:<dispatch digest>",
  "dispatch_id": "<linked dispatch ID>",
  "measured_package_bytes": 0,
  "terminal_id": "consultation-dispatch-terminal:<dispatch digest>"
}
```

### Atomicity and idempotence

- Successful response and terminal state are mutually exclusive.
- Success ingress and terminalization each commit their complete branch atomically.
- Byte-identical duplicate success adds no event, clock read, charge, completion, or logical payload.
- Repeated byte-identical terminalization is idempotent.
- Conflicting duplicates, bytes, or terminal reasons fail closed.
- Busy or pending-only rejection writes nothing and permits explicit same-byte resubmission.
- Reconciliation may create only `dispatch_interrupted` and never invokes the fixture.
- Ingress and terminalization never checkpoint, increment lifecycle, clear maintenance, execute an action, change authority, budgets, or permissions, retry fixture work, or refund a charge.

## Consequences

Slice 40 may now implement exact ingress and terminalization without private canonical names. Protected tests must independently reconstruct typed aliases, raw-byte digests, exact event payloads, direct parents, sizes, linkage, atomicity, and idempotence.

This ADR does not authorize live caregiver or model access, network or subprocess capability, action execution, disposition, memory, skill creation, schema changes, migration, checkpoint creation, rollback, retry, or refund.

## Evidence gate

Implementation remains incomplete until protected tests and full CI cover the applicable P2-J, P2-K, P2-N, and P2-O requirements. Codex remains deferred until the complete Phase 2 implementation candidate is CI-green and ready for one completion audit.
