# Slice 40: Exact Package Ingress and Dispatch Terminalization

Status: implementation-complete on draft PR #103; final exact-head CI and merge pending.

## Scope

This slice connects the accepted ADR 0012 identities and event shapes to canonical administrative package ingress and dispatch terminalization.

It does not implement disposition, execute an action, change the garden, checkpoint, increment lifecycle, clear maintenance, migrate, roll back, create memory or skills, invoke a live caregiver/model, use network/subprocess capability, retry fixture work, or refund a charge.

## Successful ingress

`phase2_ingress_runtime.py` performs raw-size admission before JSON parsing, then uses one fresh fail-fast `BEGIN IMMEDIATE` transaction.

Before mutation it independently checks:

- protected schema/configuration and canonical organism state;
- schema version 2 and fixture configuration;
- sleeping status with no pending checkpoint or maintenance bypass;
- exact immutable request and dispatch rows/envelopes/canonical sizes;
- current lineage and organism/request/dispatch linkage;
- no terminal branch;
- lifecycle-based expiry for a new response;
- exact request-creation and dispatch-admission direct parent events;
- raw UTF-8 and JSON validity;
- exact external package schema, response/proposal identities, digests, cardinality, provenance, evaluator sets, and linkage;
- byte equality between supplied raw bytes and independently reconstructed canonical package bytes;
- 16 KiB raw/canonical package ceiling;
- current-lineage logical payload formula;
- active database, checkpoint store, working set, and 1 MiB reserve.

A new success branch reads the injected clock exactly once and atomically writes:

1. one `consultation_response_ingressed` event from `administration:consultation.response_ingress`;
2. one response row;
3. zero or one proposal row according to exact status cardinality;
4. one ingress-receipt row;
5. one cost-completion row.

The event, response row, receipt row, and receipt envelope share one event sequence. The proposal has no separate event. The event payload contains exactly `completion` and `receipt`.

The receipt ID is `consultation-ingress-receipt:<external-package digest>`. The completion ID is `consultation-cost-completion:<dispatch digest>`. Direct parents are exactly the sorted request-creation and dispatch-admission event sequences.

`measured_package_bytes` equals supplied raw length and independently reconstructed canonical package length. The response stores its exact canonical envelope size and package digest. Proposal content digest and exact envelope are independently recomputed before insertion.

`unavailable` uses the same ingress event/receipt/completion branch, writes no proposal, and is final without disposition.

## Logical payload

The current-lineage logical payload formula is exactly:

```text
sum(request canonical envelope bytes)
+ sum(successfully ingressed package measured bytes)
```

Response, proposal, receipt, completion, event, and terminal metadata are physical state but are not double-counted logically. Invalid/expired/interrupted raw bytes are measured in completion evidence but do not create an ingress receipt and therefore do not enter logical payload.

Duplicate ingress adds no logical bytes.

## Duplicate and resubmission behavior

A byte-identical duplicate success:

- returns the existing response/receipt/completion evidence;
- reads no clock;
- adds no event, response, proposal, receipt, completion, charge, or logical bytes;
- invokes no fixture.

A conflicting package digest, response identity, raw byte representation, or row/event linkage fails closed.

Fail-fast busy rejection and pre-mutation invalid raw input write nothing. The caller may explicitly resubmit the same valid bytes later without fixture recall or another charge.

## Terminalization

Terminalization uses one fresh fail-fast administrative transaction and the same exact immutable request/dispatch/current-lineage/physical-boundary checks.

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
- `expired_before_ingress`: a legitimate lifecycle crossing and attempted raw bytes are required, with the same raw digest/size rules.

Rejected raw digest is SHA-256 over:

```text
b"sudachi.consultation/v1\nrejected-package-bytes\n" + exact raw bytes
```

Successful response and terminal state remain mutually exclusive.

A byte-identical repeated terminalization returns existing evidence with no clock or mutation. A conflicting reason, digest, size, or branch fails closed.

`reconcile_interrupted_dispatch` can create only `dispatch_interrupted` and never imports, invokes, or retries the fixture.

## Atomicity and physical boundaries

Success fault injection exists after:

- event;
- response;
- optional proposal;
- receipt;
- completion;
- immediately before commit.

Terminal fault injection exists after:

- event;
- terminal row;
- completion;
- immediately before commit.

Every injected fault leaves the whole new branch absent.

Both success and terminal operations perform preflight and post-write checks for:

- 8 MiB active database;
- 1 MiB next-wake reserve;
- 40 MiB checkpoint store;
- 64 MiB runtime working set.

Real active allocation above the reserve boundary rejects without partial consultation state.

## Spawned process-crash evidence

A spawned process commits dispatch admission and conservative charge, then exits with `os._exit(23)` inside fixture work. The parent observes:

- exactly one dispatch and charge;
- no response, terminal, or completion;
- released SQLite ownership;
- no automatic retry or refund.

Explicit reconciliation later records one zero-byte `dispatch_interrupted` terminal/completion branch without fixture invocation. This closes the spawned-crash portion of P2-F06 and P2-K04/K05.

## Protected evidence

Tests-only head `df5db681ec335dafbed5e88587d3085ac5209e25`, run 575:

- installation and compilation passed;
- protected enforcement failed because `phase2_ingress_runtime` did not exist.

Initial implementation head `c04dcd1d04174c307b6fa3f96a671fec57779553`, run 576:

- 332 passed, one test-fixture attribute failure;
- implementation paths passed.

Fixture repair head `24a4c480fa2d06ec5a03af2345d2dd25ccbd2008`, run 577:

- 333 passed in 40.03 seconds;
- install, compile, and schema-v1 genesis CLI smoke passed.

Boundary head `db753a4a2a53881bdff5b54e43d5743ccdbad972`, run 578:

- 338 passed in 32.88 seconds;
- spawned crash/reconciliation, real reserve refusal, and logical accounting passed.

Clean logical-reconstruction head `170d6106a9957e977c385b0a94cc5d66e26d434f`, run 579:

- 338 passed in 36.22 seconds;
- install, compile, and schema-v1 genesis CLI smoke passed.

All original 152 Phase 1 tests remain unchanged and included.

## Matrix status

Closed or materially closed in this slice:

- P2-F06 spawned process-crash evidence;
- P2-G06 noncanonical fixture output through explicit ingress boundary;
- P2-J01–J08 for implemented one-cycle structures;
- P2-J11–J27 applicable exact validation, branch atomicity, duplicate, and resubmission evidence;
- P2-K01–K22 applicable exception, invalid, expiry, crash, reconciliation, atomicity, idempotence, and exact terminal evidence;
- P2-N03–N07 and ADR 0012 P2-N09/N10 for implemented ingress/terminal chains;
- ordinary success/refusal portions of P2-O01/O02.

Still dependent on later legitimate cycles or rollback/disposition work:

- exact 64 KiB mixed four-cycle boundary and one-over;
- four request/four charge epoch boundary;
- new-lineage reset and old-lineage late-package rejection;
- maximum-envelope cycle evidence;
- full end-to-end request→dispatch→response→proposal→receipt→disposition reconstruction;
- disposition wake and rollback integration.

No private canonical mutation is used to manufacture those states.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is CI-green and ready for the single implementation-completion audit.
