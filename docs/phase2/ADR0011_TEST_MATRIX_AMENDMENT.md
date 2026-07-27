# ADR 0011 Test Matrix Amendment

Status: **Accepted with ADR 0011**

This amendment resolves Issue #96 and is normative together with ADRs 0008–0011, Consultation Protocol v1, and `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`.

It changes no Phase 1 requirement, database schema, physical limit, consultation budget, fixture capability, or authority category.

## Exact replacements and additions

### P2-F03 — atomic dispatch admission

Required evidence now includes exact assertions that one fresh fail-fast administrative transaction atomically inserts:

1. one final ADR 0010 dispatch envelope row;
2. one ADR 0011 conservative charge row; and
3. one `consultation_dispatch_admitted` event whose sequence is referenced by both rows.

Fault injection before and after each insert must leave either all three objects or none.

### P2-F05 — exact conservative ledger

The charge ID is exactly:

```text
consultation-cost-charge:<the 64 lowercase hexadecimal characters from dispatch_id>
```

The charge ledger contains exactly:

```json
{
  "attempt_count": 1,
  "charge_id": "consultation-cost-charge:<dispatch digest>",
  "declared_latency_ms": 0,
  "fixture_invocation_count": 1,
  "human_minutes": 0,
  "model_units": 0,
  "money_microunits": 0,
  "request_bytes": "<exact measured integer>",
  "work_units": 1
}
```

`request_bytes` must equal both the request row's stored `canonical_size_bytes` and the independently recomputed canonical request-envelope byte length.

Alternate prefixes, changed digests, extra/missing fields, boolean-as-integer values, nonzero forbidden resources, and byte mismatches reject before canonical mutation.

### Dispatch-admission event

The event is exactly:

- type `consultation_dispatch_admitted`;
- source `administration:consultation.dispatch`;
- current committed lifecycle, with no lifecycle increment;
- payload keys exactly `charge` and `dispatch`.

The payload is:

```json
{
  "charge": <exact ADR 0011 charge ledger>,
  "dispatch": <exact final ADR 0010 dispatch envelope>
}
```

The final dispatch envelope's `event_sequence`, `consultation_dispatch.event_sequence`, `consultation_cost_charge.event_sequence`, and the event row sequence must be identical.

No separate cost event exists.

## Additional protected evidence

- A forced commit failure proves the fixture is not invoked and no dispatch/charge/event remains.
- A successful admission proves commit and lock release precede fixture execution.
- A competing writer can acquire ownership during fixture execution.
- Repeated admission returns the existing admitted work and never authorizes another call or charge.
- A process interruption after admission retains exactly one conservative charge.
- Dispatch admission creates no checkpoint, lifecycle increment, garden/action mutation, response, proposal, terminal, disposition, refund, or retry instruction.
- Real-file evidence proves active DB, sidecars, checkpoint store, working set, and 1 MiB next-wake reserve remain within accepted limits.
- All original 152 Phase 1 tests remain unchanged and passing.

## Implementation order

1. merge ADR 0011 documentation and close Issue #96;
2. add tests-first exact charge/event helpers;
3. implement fresh administrative admission and atomic write set;
4. commit and release ownership;
5. invoke the deterministic fixture through a capability-minimal boundary;
6. retain noncanonical fixture bytes for later Slice 40 ingress or terminalization.

No live caregiver, model API, network, subprocess, arbitrary code, automatic retry, action execution, memory, or skill behavior is authorized.