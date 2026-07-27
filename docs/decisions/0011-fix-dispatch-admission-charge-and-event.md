# ADR 0011: Fix the dispatch-admission charge identity and event

- Status: Accepted
- Date: 2026-07-27
- Decision owner: project owner
- Clarification issue: #96

## Context

ADRs 0008–0010 and Consultation Protocol v1 require administrative dispatch admission to atomically commit one dispatch row, one conservative cost-charge row, and one administrative event before deterministic fixture work begins. The protected schema already contains `consultation_dispatch`, `consultation_cost_charge`, and their event-sequence links.

The accepted documents did not define the exact `charge_id`, dispatch-admission event type, or event payload. Those values are immutable canonical evidence retained by checkpoints, rollback, event export, and lineage history. They cannot be selected privately by implementation code.

On 2026-07-27 the project owner explicitly adopted the recommendation in Issue #96.

## Decision

### Charge identity

For a validated final dispatch envelope whose `dispatch_id` is:

```text
consultation-dispatch:<64 lowercase hexadecimal characters>
```

its unique charge ID is exactly:

```text
consultation-cost-charge:<the same 64 lowercase hexadecimal characters>
```

The charge ID is a typed bijective alias of the already-derived dispatch digest. It introduces no additional hash label, clock input, event sequence, or dependency cycle.

### Exact protected charge ledger

The canonical charge object contains exactly:

- `attempt_count`: `1`
- `charge_id`: the exact typed alias above
- `declared_latency_ms`: `0`
- `fixture_invocation_count`: `1`
- `human_minutes`: `0`
- `model_units`: `0`
- `money_microunits`: `0`
- `request_bytes`: the independently recomputed canonical byte length of the linked final request envelope
- `work_units`: `1`

`request_bytes` must equal both:

1. `consultation_request.canonical_size_bytes`; and
2. `len(canonical_json(final_request_envelope))`.

A mismatch fails before canonical mutation.

The charge object has no dispatch ID field because the exact final dispatch envelope already contains it. It has no event sequence, response, fixture result, refund, retry, checkpoint, action, authority-expansion, or free-text field.

### Single dispatch-admission event

Administrative admission creates exactly one event:

- event type: `consultation_dispatch_admitted`
- source: `administration:consultation.dispatch`
- writer category: the existing canonical `administration` category
- lifecycle: the currently committed organism lifecycle; dispatch does not increment lifecycle
- event sequence: the single sequence referenced by both the dispatch row and the charge row

Its payload contains exactly two keys:

```json
{
  "charge": <exact protected charge object>,
  "dispatch": <exact final ADR 0010 dispatch envelope>
}
```

The final dispatch envelope's own `event_sequence` equals the new admission event sequence. No separate charge event is created.

### Atomic and post-commit boundary

The dispatch row, charge row, and admission event are inserted in one fresh fail-fast administrative transaction. Either all three commit or none exists.

The transaction commits and releases SQLite write ownership before the deterministic fixture is invoked. Repeated admission or any post-commit interruption never authorizes a second fixture invocation or another charge.

Dispatch admission creates no checkpoint, action effect, garden mutation, lifecycle increment, response, proposal, terminal, disposition, or retry instruction.

## Evidence requirements

Protected evidence must prove:

- exact charge-ID derivation and rejection of alternate prefixes/digests;
- exact charge ledger and request-byte triple equality;
- exact event type, source, payload keys, row/event sequence linkage, and final dispatch envelope;
- atomic rollback at each write boundary;
- commit before fixture invocation and no SQLite ownership during fixture execution;
- idempotent repeated admission with no second charge/call;
- retained conservative charge after interruption;
- physical limits and 1 MiB reserve;
- no checkpoint or Phase 1 effect;
- all original 152 Phase 1 tests unchanged and passing.

## Consequences

The canonical dispatch-admission boundary is now completely named and testable without adding a new digest label or schema migration. Slice 39 may implement dispatch admission, conservative precharge, and the deterministic fixture capability boundary.

This decision does not authorize live models, humans, network, subprocesses, arbitrary code, automatic retries, action execution, memory, or skill creation.