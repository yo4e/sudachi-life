# Slice 39a: Dispatch Admission, Conservative Precharge, and Fixture Boundary

Status: merged through PR #99 as `b7c434aed249ed0bc52160db66e594824186890e`.

## Scope

This slice connects the accepted ADR 0010 dispatch identity and ADR 0011 charge/event identity to canonical administrative admission, then invokes a pure deterministic fixture only after the transaction commits and releases SQLite ownership.

It does not perform ingress, terminalization, disposition, action execution, garden mutation, memory, skill creation, live caregiver/model work, network, or subprocess access.

## Canonical admission

`phase2_dispatch_runtime.py` uses one fresh fail-fast `BEGIN IMMEDIATE` transaction.

Before mutation it independently checks:

- protected schema/configuration and canonical organism state;
- schema version 2 and fixture configuration;
- sleeping status with no pending checkpoint or maintenance reason;
- exact immutable request row/envelope/canonical byte equality;
- current lineage and lifecycle-based expiry;
- registered stable checkpoint boundary containing the request event;
- stable checkpoint artifact presence;
- no response or terminal state;
- no prior dispatch unless byte-identical idempotent reentry;
- current-lineage charged invocation count below four;
- active database, checkpoint store, working set, and 1 MiB reserve.

A new admission reads the injected clock exactly once after all eligibility checks.

## Exact ADR 0011 write set

Under the held write lock, the next event sequence is predicted and inserted into the final ADR 0010 dispatch envelope.

The transaction writes exactly:

1. one event:
   - type `consultation_dispatch_admitted`;
   - source `administration:consultation.dispatch`;
   - current committed lifecycle;
   - payload keys exactly `charge` and `dispatch`;
2. one immutable `consultation_dispatch` row;
3. one immutable `consultation_cost_charge` row.

The event, final dispatch envelope, dispatch row, and charge row share one event sequence.

The charge ID is the typed alias of the dispatch digest:

```text
consultation-cost-charge:<dispatch digest>
```

The exact charge ledger records one attempt, one fixture invocation, one work unit, exact request bytes, and zero human/model/money/declared latency. Request bytes equal both the stored request size and independently recomputed canonical request bytes.

Fault injection after the event, dispatch row, charge row, and immediately before commit proves no partial state remains. Preflight and post-write physical checks both run before commit.

## Idempotence and interruption

Byte-identical repeated admission:

- returns the already-admitted dispatch evidence;
- reads no clock;
- adds no event or charge;
- never authorizes another fixture call.

A conflicting fixture case rejects.

A fixture exception occurs only after the admission commit and therefore retains exactly one conservative charge. The first implementation does not automatically retry or refund.

## Deterministic fixture boundary

`phase2_fixture.py` exposes exactly:

```python
run_deterministic_fixture(request_envelope, fixture_case_id) -> bytes
```

It imports no filesystem path, SQLite, network, subprocess, randomness, credential, repository, evaluator, executor, checkpoint, or rollback capability.

`perform_fixture_dispatch` passes only a deep-copied final request envelope and the declared case ID after the database connection has closed. A real independent connection can acquire `BEGIN IMMEDIATE` during fixture execution and observes the committed dispatch/charge/event.

Valid action-candidate, abstain, defer, and unavailable cases produce deterministic package bytes that validate against the actual committed dispatch. Other declared adversarial cases produce deterministic typed noncanonical fixture bytes for later Slice 40 ingress/terminalization tests.

Fixture bytes are not inserted into canonical response, proposal, receipt, or cost-completion tables in this slice.

## Protected evidence

Tests-only head `a349c23ca697e5c4dce33194a8081a8cf00206f2`, GitHub Actions run 565:

- installation and compilation passed;
- protected enforcement failed because the Slice 39 modules did not exist.

Initial implementation head `4cf2e4fa8dcda6f799ed4e0c362e9d74ba57fa57`, run 567:

- 305 passed in 41.87 seconds;
- install, compile, and schema-v1 genesis CLI smoke passed.

Extended admission-matrix head `39e67ab69a2670de425a977ee6c38b514fd94de4`, run 568:

- 316 passed in 38.59 seconds;
- install, compile, and schema-v1 genesis CLI smoke passed;
- real 7 MiB-plus active allocation rejected without consuming the 1 MiB reserve;
- pending, unstable, missing-checkpoint, and legitimately expired requests rejected without consultation mutation;
- valid fixture bytes validated against the actual committed dispatch.

Final exact PR head `64720b736fcab47b5ebfff26155ab17728f47b14`, run 569:

- 316 passed in 56.74 seconds;
- dependency installation succeeded;
- source/test compilation succeeded;
- schema-v1 genesis CLI smoke succeeded.

All original 152 Phase 1 tests remain unchanged and included.

## Matrix status

Closed in this slice:

- P2-F01;
- P2-F02 for sleeping, pending-checkpoint, stable-boundary/artifact, current-lineage implementation guard, expiry, and prior-dispatch admission;
- P2-F03;
- P2-F04;
- P2-F05;
- P2-F07;
- ordinary and refusal portions of P2-F09;
- P2-F10;
- P2-G01–P2-G07.

Partially closed:

- P2-F06: fixture exception/interruption retains the charge; spawned process-crash evidence remains for a later runtime closeout slice.

Deferred without private canonical mutation:

- P2-F08 four-charge epoch boundary requires legitimate response/terminal/disposition cycles;
- exact current-lineage/abandoned-lineage package scenarios close with rollback and ingress slices;
- full raw-package parsing, measured completion, terminalization, and same-byte resubmission belong to Slice 40.

## Exact continuation

Slice 40 must first confirm that every immutable ingress/terminal ID, event type, and event payload is normatively closed. It then implements raw-size-before-parse validation, exact package ingress, response/proposal/receipt/cost-completion atomicity, duplicate and same-byte resubmission behavior, invalid-package terminalization, and explicit interrupted-dispatch reconciliation. It must not invoke the fixture again.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.