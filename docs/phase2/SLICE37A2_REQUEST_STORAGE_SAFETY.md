# Slice 37a2: Request-Extension Storage Safety

Status: implemented on PR #83; final documentation CI and merge pending.

## Scope

This sub-slice implements the accepted storage-safe optional request extension around the retained Phase 1 garden wake. It does not implement dispatch, fixture execution, ingress, terminalization, disposition, action adoption, memory, skills, or a new optional request-context schema.

Protected evidence closes:

- P2-E01: request metadata is optional and the retained Phase 1 core commits when only the extension is refused;
- P2-E02: pre-write projection includes current active allocation, real SQLite sidecars, request row/event bytes, checkpoint tail allowance, resulting checkpoint database and manifest allowance, checkpoint store, full working set, and the 1 MiB reserve;
- P2-E03: pre-write refusal writes no consultation row, event, source, sequence, or partial cost;
- P2-E04: post-write refusal rolls back the request event and row inside the extension savepoint and restores the original physical allocation;
- P2-E05: refusal commits the exact retained Phase 1 abstention, failure update, event history, status, and ordinary checkpoint;
- P2-E06: refusal returns exact noncanonical reason `consultation_request_not_created_storage_budget`;
- P2-E07: a real active body at exactly 7 MiB preserves the 1 MiB reserve, refuses only the request, checkpoints, and completes a second queued garden wake;
- P2-E08: real WAL and SHM bytes are included in active-files and working-set projection together with checkpoint-store and resulting-checkpoint bytes;
- P2-E09: if the core active body is already above 8 MiB, the public wake raises the same frozen Phase 1 error and rolls back exactly instead of returning optional refusal;
- P2-D12: explicit pre-write and post-write refusal probes prove request row/event atomicity and extension-only rollback.

A normal successful request plus ordinary checkpoint is also measured under the 8 MiB active/artifact, 40 MiB checkpoint-store, 64 MiB working-set, and 1 MiB reserve limits.

P2-E10 remains open. The accepted protocol permits optional bounded typed request context but does not enumerate its exact field set. This sub-slice does not invent private fields merely to inflate an envelope to 16 KiB. A later reviewed exact request-context schema, or an accepted proof that the closed v1 request field set defines the maximum, is required before claiming maximum-size request evidence.

## Test-first evidence

Tests-only head `44f9f89db5cf8c8367443b84558502be8b5bd048`, GitHub Actions run 524:

- 236 existing tests passed;
- 2 new tests failed because pre-write and post-write storage-refusal probes did not exist.

Savepoint refusal implementation head `683bca2968a54388cc80565371790df6a362b0af`, run 526:

- 238 passed in 32.37 seconds;
- refusal state matched an identical retained-core control, including checkpoint bytes and active allocation.

Real-boundary head `d4ca1ac559f9ac349363afa2b75ea98fc045ab36`, run 529:

- 239 passed;
- the real 7 MiB reserve/two-wake case passed;
- one WAL test failed because a no-op SQL update produced a zero-byte WAL.

The WAL fixture was corrected to perform a real canonical `environment_step + 1` write with automatic checkpointing disabled. No production storage rule changed.

Core-failure comparison head `193a610d499fc0c970cf8ab2b8c8f15ab3373122`, run 531:

- 241 passed in 36.69 seconds;
- public and retained core over-limit failures were identical and non-mutating.

Final code/test head `d6b8e2b27f888fdc56f83b9f56cdb8708cbfeadb`, run 532:

- 242 passed in 35.51 seconds;
- dependency installation succeeded;
- source and test compilation succeeded;
- schema-v1 genesis CLI smoke succeeded.

All original 152 Phase 1 tests remain unchanged and included.

## Admission model

The pre-write projection is conservative and transparent:

1. measure SQLite page allocation and the actual database, journal, WAL, and SHM files;
2. add page-rounded request row/event canonical bytes plus bounded B-tree/index overhead;
3. add bounded remaining `checkpoint_pending` tail pages;
4. require projected active files plus the exact 1 MiB reserve to fit 8 MiB;
5. add the projected checkpoint database and the established 4096-byte canonical manifest allowance;
6. require the projected checkpoint store to fit 40 MiB;
7. require the projected complete runtime working set to fit 64 MiB.

After the request event and row are written inside `consultation_request_extension`, the implementation remeasures actual SQLite page allocation and repeats the active/reserve, checkpoint-store, and working-set projections before releasing the savepoint.

If either check rejects, the extension returns the noncanonical refusal result. The request event and row do not exist, the request source and sequence do not exist, no consultation cost exists, and the retained core proceeds to its ordinary checkpoint.

If the retained core itself exceeds its frozen physical limit, the entire wake fails through the unchanged Phase 1 transaction path.

## Next boundary

The remaining request-core requirements are P2-D07/D08, P2-D11, P2-D14, and P2-D15. P2-E10 requires an exact reviewed maximum-envelope interpretation before implementation evidence can be honest.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.
