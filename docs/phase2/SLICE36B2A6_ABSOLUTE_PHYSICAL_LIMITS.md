# Slice 36b2a6: Independent Absolute Physical Limits

Status: implemented on PR #73; final review and merge pending.

## Scope

This slice closes the remaining ADR 0009 section 9 physical evidence for matrix requirements P2-O18, P2-O19, P2-O21, and P2-O22. It uses independently measured schema-v2-zero files. Paired schema-v1/schema-v2 overhead evidence remains separately owned by PR #72 and is not used as a substitute for absolute limits.

Accepted limits remain unchanged:

- active database: 8 MiB
- checkpoint/archive/candidate database: 8 MiB
- checkpoint store: 40 MiB
- runtime working set: 64 MiB
- enqueue reserve for one subsequent wake: 1 MiB

## Test-first defects and narrow Phase 1 repairs

Protected real-file tests and final diff review found seven shared trusted-kernel defect groups. Each repair was explicitly authorized by the project owner. The final authorization covered further same-turn repairs only when they closed a missing physical check, post-publication cleanup, or no-partial-mutation invariant without changing accepted limits, authority, idempotence, or semantics.

### Issue #74: candidate manifest bytes omitted

Tests-only head `88ebf6ef70c2e09cfc7668d9e3acde928e23642a`, run 477:

- 200 existing tests passed
- source and transformed candidate publication each left the working set at 67,108,865 bytes

Repair `31d328496c4c1cf6c87207f3ea5fd59e7ebc9cbd` measures complete temporary and final artifacts and removes only a newly published rejected candidate. Run 478 passed with 202 tests.

### Issue #75: checkpoint validator omitted the 8 MiB artifact ceiling

Run 479 proved pending repair could register a logically valid checkpoint database above 8 MiB while aggregate limits still fit.

Repair `615c299317d240f41037c43ff445c5ff59b954a9` adds only the existing checkpoint artifact limit. Run 480 proved one-page-over rejection; run 482 at `7052384a93e725bcead4837ab671383e4b1ece67` proved exact 8 MiB acceptance with 205 tests. The pre-repair validator remains byte-identical in `checkpoint_core_impl.py`.

### Issue #76: rejected rollback archive remained published

Tests-only head `e3aae830821f04de459b538608fa41b5b10cc986`, run 483:

- 206 tests passed
- exact 64 MiB succeeded
- 64 MiB plus one byte raised, but the new rollback archive remained on disk

Repair `4c4373ab0044224b4658a9c651d75497fddec074` removes only this invocation's newly published archive when the retained implementation does not complete. Run 484 passed with 207 tests. The pre-repair body remains byte-identical in `rollback_impl.py`.

### Post-write registration growth crossed the working-set ceiling

Run 487 at `27ca304caebd3fddd209b58123544570f4c38808` produced 213 passing tests and two failures:

- lifecycle checkpoint registration accepted a final working set one byte above 64 MiB
- pending checkpoint repair accepted the same one-byte-over final state

Repair `47da614119d9b11cb4b791ad5ed9a85ff8fbdbce` measures projected committed active pages after transaction writes, adds real CP/RA/RC/TC bytes, and rejects before commit. Checkpoint creation removes only its newly published checkpoint on this rejection; pending repair rolls back and retains the pre-existing orphan. Run 488 passed with 215 tests.

Pre-repair bodies remain byte-identical in `checkpoint_creation_impl.py` and `checkpoint_repair_commit_impl.py`. Shared projection lives in `postwrite_storage.py`.

### Issue #77: pending repair omitted the independent active ceiling

Tests-only head `43f75db71e15aadcca76963c751009b2fe2bc842`, run 492:

- 216 tests passed
- exact 8 MiB active repair succeeded
- one-page-over active repair incorrectly succeeded

Repair `bde72a4637849e34e28bd1b6de34c9634e7f28b0` adds early active admission before the repair clock or writes and rechecks active allocation before commit. Run 494 passed with 217 tests. The pre-repair validator remains byte-identical in `checkpoint_repair_validate_impl.py`.

### Issue #78: idempotent rollback reentry bypassed full admission

Tests-only head `7de3d963dfaeed260ec27a937adec7beacb58b6c`, run 499:

- 217 tests passed
- existing RA, RC, and TC reentry each returned while the real working set was 64 MiB plus one byte

Repair `a752273d0ba3c9b8610d609da15050e70ddca6a5` checks the complete current working set at each public rollback entry before the retained implementation runs. Existing artifacts are never deleted by this admission rejection. Run 500 passed with 220 tests.

### Issue #78: retention no-op bypassed full admission

Tests-only head `08426feb176a75ff4161b066c52a4487ff0a40e4`, run 501:

- 221 tests passed
- exact 64 MiB retention no-op succeeded
- 64 MiB plus one byte also returned because checkpoint count was already within the retention limit

Repair `409b82962cee00f59e573b6bf5c90d0d9d426cb6` checks the complete current working set at the public retention enforcement entry. The over-limit case rejects before staging, registry mutation, or event insertion. Reconciliation remains unchanged as the explicit interrupted-staging recovery API. Run 502 passed with 222 tests.

## Protected physical evidence

### Active database and reserve

A schema-v2-zero database is grown with valid canonical inbox and event rows near the 8 MiB ceiling. Enqueue proceeds while one page-rounded MiB remains, rejects before consuming the reserve, writes no rejected inbox/event row, and leaves a subsequent real garden wake and checkpoint possible.

Pending repair independently accepts an active body at exactly 8 MiB and rejects one page over before reading the repair clock or writing canonical state.

### Checkpoint artifact

A genuine pending checkpoint orphan is constructed through the protected timeout path. SQLite freelist allocation changes physical bytes without changing protected schema or logical canonical state.

- exact 8 MiB validates and repairs
- one page over 8 MiB rejects before registry/canonical mutation

### Checkpoint store

A completed control checkpoint measures the complete database plus canonical manifest. Real sparse regular padding places an identical probe at:

- exactly 40 MiB: publication succeeds
- 40 MiB plus one byte: publication rejects and removes the temporary checkpoint, retaining the recoverable pending state

### Runtime working set

Independent exact and one-over cases cover:

- lifecycle checkpoint publication and registration
- pending checkpoint repair
- retention admission
- pre-rollback archive publication and existing-archive reentry
- source restore candidate publication and existing-candidate reentry
- transformed restore candidate publication and existing-candidate reentry

Exact 64 MiB succeeds. One byte over rejects without retaining a new artifact, deleting an existing artifact, or committing rejected canonical state.

### Raw zero-caregiver preservation

The exact immutable `consultation_configuration` row and empty operational consultation tables are read directly from each SQLite body, not only through semantic projection, for:

- active database
- stable checkpoint (`CP`)
- pre-rollback archive (`RA`)
- source restore candidate (`RC`)
- transformed restore candidate (`TC`)

No operational consultation `sqlite_sequence` entry exists.

## Regression and audit state

- all original 152 Phase 1 tests remain unchanged
- latest code CI: run 502, 222 passed in 32.16 seconds
- installation, source/test compilation, and schema-v1 genesis CLI smoke passed
- no test was skipped, weakened, conditioned, or reinterpreted
- no Codex audit was used

The touched shared Phase 1 boundary is re-frozen after PR #73 final documentation CI and merge. Future changes require a new explicit defect and authorization; these wrappers are not permission for general Phase 1 redesign.

## Next boundary

After PR #73 merges, Slice 36 is complete. Slice 37 may begin from updated `main` with request-envelope and storage-safe request-extension requirements. Codex remains deferred until the single full Phase 2 implementation-completion candidate exists.

See `SLICE36B2A6_ACTIVE_REPAIR_ADDENDUM.md` for the final active-repair red/green evidence.
