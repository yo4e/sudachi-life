# Slice 40: Exact Package Ingress and Dispatch Terminalization

Status: complete and merged.

PR #103 merged as `f0238f108b2eb05a6774ca68a0b056eb12772dd1`.

Final exact PR head `e6221bb42ad5e94ddd4d0c2e576975d64693464c`, GitHub Actions run 580:

- 338 passed in 73.21 seconds;
- dependency installation passed;
- source and test compilation passed;
- schema-v1 genesis CLI smoke passed;
- all original 152 Phase 1 tests remained unchanged and included.

## Scope

This slice connects ADR 0012 identities and event shapes to canonical administrative package ingress and dispatch terminalization.

It does not implement disposition, execute an action, change the garden, checkpoint, increment lifecycle, clear maintenance, migrate, roll back, create memory or skills, invoke a live caregiver/model, use network/subprocess capability, retry fixture work, or refund a charge.

## Successful ingress

`phase2_ingress_runtime.py` checks the raw 16 KiB ceiling before JSON parsing, then uses one fresh fail-fast `BEGIN IMMEDIATE` transaction.

Before mutation it independently verifies:

- protected schema/configuration and canonical organism state;
- schema version 2, fixture configuration, sleeping status, and no pending checkpoint or maintenance bypass;
- exact immutable request and dispatch rows, envelopes, canonical sizes, current lineage, and linkage;
- no terminal branch and lifecycle-based expiry for a new response;
- exact request-creation and dispatch-admission direct parents;
- UTF-8/JSON validity and exact external package, response, proposal, digest, provenance, evaluator, cardinality, and linkage rules;
- byte equality between supplied raw bytes and independently reconstructed canonical package bytes;
- current-lineage logical payload capacity;
- active database, checkpoint store, working set, and 1 MiB reserve.

A new success branch reads the injected clock exactly once and atomically writes:

1. one `consultation_response_ingressed` event from `administration:consultation.response_ingress`;
2. one response row;
3. zero or one proposal row according to exact status cardinality;
4. one ingress-receipt row;
5. one cost-completion row.

The event, response row, receipt row, and receipt envelope share one event sequence. The proposal has no separate event. The event payload contains exactly `completion` and `receipt`.

Typed aliases are exact:

```text
receipt_id    = consultation-ingress-receipt:<external-package digest>
completion_id = consultation-cost-completion:<dispatch digest>
```

Direct parents are exactly the sorted request-creation and dispatch-admission event sequences. Measured package bytes equal both supplied raw length and independently reconstructed canonical package length.

`unavailable` uses the same branch with no proposal and is final without disposition.

## Logical payload

The current-lineage logical formula is exactly:

```text
sum(request canonical envelope bytes)
+ sum(successfully ingressed package measured bytes)
```

Response, proposal, receipt, completion, event, and terminal metadata are physical state but are not double-counted logically. Invalid, expired, and interrupted raw bytes are measured in completion evidence but create no ingress receipt and therefore add zero logical bytes.

## Idempotence and resubmission

A byte-identical duplicate success:

- returns existing response/receipt/completion evidence;
- reads no clock;
- adds no event, row, charge, or logical bytes;
- invokes no fixture.

Conflicting bytes, digest, identity, or linkage fail closed. Busy rejection and invalid pre-mutation input write nothing; the caller may explicitly resubmit the same valid bytes without fixture recall or another charge.

## Terminalization

Terminalization uses one fresh fail-fast administrative transaction and the same exact immutable/current-lineage/physical-boundary checks.

One terminal branch atomically writes:

1. one `consultation_dispatch_terminalized` event from `administration:consultation.dispatch_terminal`;
2. one dispatch-terminal row;
3. one cost-completion row.

The event, terminal row, and terminal envelope share one event sequence. The payload contains exactly `completion` and `terminal`. Direct parents are exactly the request-creation and dispatch-admission events.

Typed aliases are exact:

```text
terminal_id   = consultation-dispatch-terminal:<dispatch digest>
completion_id = consultation-cost-completion:<dispatch digest>
```

Reason rules are exact:

- `dispatch_interrupted`: no raw package, null rejected digest/size, measured completion zero;
- `fixture_output_invalid`: raw bytes required, exact raw-byte digest and size, completion bytes equal raw length;
- `expired_before_ingress`: legitimate lifecycle crossing and attempted raw bytes required, with the same raw digest/size rules.

Rejected raw digest is SHA-256 over:

```text
b"sudachi.consultation/v1\nrejected-package-bytes\n" + exact raw bytes
```

Response and terminal branches are mutually exclusive. Byte-identical repeated terminalization reads no clock and adds no state. Conflicting reason, digest, size, or branch fails closed.

`reconcile_interrupted_dispatch` creates only `dispatch_interrupted` and never imports, invokes, or retries the fixture.

## Atomicity and physical boundaries

Success fault injection exists after the event, response, optional proposal, receipt, completion, and immediately before commit.

Terminal fault injection exists after the event, terminal row, completion, and immediately before commit.

Every injected fault leaves the whole new branch absent.

Both branches perform preflight and post-write checks for the 8 MiB active database, 1 MiB next-wake reserve, 40 MiB checkpoint store, and 64 MiB runtime working set. Real allocation beyond the reserve boundary rejects without partial consultation state.

## Spawned process-crash evidence

A spawned process commits dispatch admission and conservative charge, then exits with `os._exit(23)` inside fixture work. The parent observes one dispatch and charge, no response/terminal/completion, released SQLite ownership, and no retry or refund.

Explicit reconciliation then records one zero-byte `dispatch_interrupted` terminal/completion branch without fixture invocation. This closes the spawned-crash portions of P2-F06 and P2-K04/K05.

## Test-first history

- tests-only `df5db681ec335dafbed5e88587d3085ac5209e25`, run 575: expected missing-module failure after install/compile passed;
- initial implementation `c04dcd1d04174c307b6fa3f96a671fec57779553`, run 576: 332 passed and one test-fixture attribute failure;
- repaired core `24a4c480fa2d06ec5a03af2345d2dd25ccbd2008`, run 577: 333 passed in 40.03 seconds;
- boundary `db753a4a2a53881bdff5b54e43d5743ccdbad972`, run 578: 338 passed in 32.88 seconds;
- clean logical reconstruction `170d6106a9957e977c385b0a94cc5d66e26d434f`, run 579: 338 passed in 36.22 seconds;
- final exact head `e6221bb42ad5e94ddd4d0c2e576975d64693464c`, run 580: 338 passed in 73.21 seconds.

## Matrix status

Closed or materially closed:

- P2-F06 spawned process-crash evidence;
- P2-G06 through the explicit ingress boundary;
- P2-J01–J08 for implemented one-cycle structures;
- applicable P2-J11–J27 exact validation, atomicity, duplicate, and resubmission evidence;
- applicable P2-K01–K22 exception, invalid, expiry, crash, reconciliation, atomicity, idempotence, and exact terminal evidence;
- applicable P2-N03–N07 and ADR 0012 P2-N09/N10;
- ordinary success/refusal portions of P2-O01/O02.

Still dependent on legitimate later disposition/rollback cycles:

- exact mixed 64 KiB four-cycle boundary and one-over;
- four-request/four-charge epoch boundary;
- new-lineage reset and old-lineage late-package rejection;
- maximum-envelope cycle evidence;
- complete request→dispatch→response→proposal→receipt→disposition reconstruction;
- disposition wake and rollback integration.

No private canonical mutation was used to manufacture those states. No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.
