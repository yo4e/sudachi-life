# Slice 37a1: Fixture Request-Wake Core

Status: implemented on PR #81; final documentation CI and merge pending.

## Scope

This sub-slice implements the smallest accepted garden request-wake extension from ADR 0008 and Consultation Protocol v1. It does not implement the real storage-refusal boundary, dispatch, fixture execution, ingress, terminalization, disposition, action adoption, memory, or skills.

Protected evidence in this sub-slice covers:

- P2-D01: a request is considered only after the unchanged Phase 1 selector returns `no_applicable_action` for an incomplete objective;
- P2-D02 and P2-D03: the Phase 1 abstention outcome remains a failure and increments `consecutive_failures` exactly once;
- P2-D04: a wake entering `maintenance_required` creates no request;
- P2-D05: an eligible wake creates exactly one immutable request row and one request event;
- P2-D06: an existing unexpired current-lineage request prevents another request;
- P2-D09: request identity, digest preimage, ID, final envelope, canonical bytes, and event linkage are independently reconstructed;
- P2-D10: request identity excludes the later request event sequence;
- P2-D13: the created request is present in the ordinary stable lifecycle checkpoint;
- P2-D16: an outstanding request does not block a later caller-selected garden wake;
- the structural core of P2-E01: request metadata is inserted through a dedicated savepoint extension after the frozen Phase 1 budget ledger and before `checkpoint_pending`.

The following accepted requirements remain open and are not claimed complete by this PR:

- P2-D07 and P2-D08: four-request/current-lineage epoch and ordinal evidence across expiry and rollback;
- P2-D11: adversarial exact-field and forbidden free-text corpus;
- P2-D12: explicit pre-commit fault injection for row/event atomicity;
- P2-D14: backward wall-time independence;
- P2-D15: competing and nested wake fail-fast evidence;
- P2-E02 through P2-E10: exact pre/post-write storage accounting, extension-only rollback, real sidecars, 8 MiB/reserve boundary, core-failure comparison, and maximum-size success.

## Test-first evidence

Tests-only head `e6d87914b005b012ce9a97578d07bb8a6742174a`, GitHub Actions run 516:

- 230 existing tests passed;
- 6 new tests failed because the request result surface did not exist.

Implementation head `4fe1ab57d329cea6ecdaeab41278d327734399f9`, run 518:

- 235 tests passed;
- one test fixture failed because it set only the stored objective flag and did not satisfy the frozen Phase 1 evaluator's independently recomputed completion condition.

The fixture was corrected to use the real complete garden state: at least one harvested fruit, no harvestable fruit, and no dry living plot. No production evaluator or Phase 1 behavior changed.

Final code/test head `33248776ce3746e1a651e367dd49eb26566e4e57`, run 519:

- 236 passed in 82.36 seconds;
- dependency installation succeeded;
- source and test compilation succeeded;
- schema-v1 genesis CLI smoke succeeded.

All original 152 Phase 1 tests remain unchanged and included.

## Implementation boundary

The pre-extension `lifecycle.py` body is retained byte-identically as `lifecycle_impl.py` with blob SHA `c971d77cc9beab22f5c50fb692b4f81210cbf3ed`.

The public wrapper:

1. delegates the complete frozen wake to the retained implementation;
2. uses one invocation-local `ContextVar` state;
3. captures the final Phase 1 budget-ledger payload without another clock read;
4. invokes the fixture request extension immediately before the ordinary `checkpoint_pending` event;
5. returns the non-authoritative request result alongside the unchanged wake result.

The request extension:

- runs only for schema-v2 `phase2-fixture-v1`;
- creates nothing for schema-v1, zero-caregiver, applicable-action, objective-complete, maintenance-entry, request-limit, or outstanding-request paths;
- derives the request ID from the exact declared identity without event sequence, wall time, or authority fields;
- predicts the next event sequence only while the wake already owns the SQLite write transaction;
- writes the request event and immutable request row in one savepoint;
- rolls both back if either write fails;
- adds no fixture call, network, subprocess, tool, path, live caregiver, action, disposition, memory, or skill authority.

## Next boundary

Slice 37a2 must implement and prove P2-E02 through P2-E10 with real file and SQLite sidecar accounting. If the optional extension cannot fit, only consultation state is refused; the unchanged Phase 1 core wake and ordinary checkpoint must still commit, and the caller must receive `consultation_request_not_created_storage_budget`.

Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.
