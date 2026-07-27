# Slice 37a3: Request Time and Wake Concurrency

Status: merged through PR #85 as `82e17c6ccba65323315b399ea6fad345a52db5f4`.

## Scope

This evidence-only sub-slice closes the request-boundary requirements that are independent of dispatch, ingress, disposition, and optional request context.

Protected evidence closes:

- P2-D14: lifecycle-based request eligibility and expiry do not depend on wall-clock direction;
- P2-D15: nested and competing-process wakes fail fast before request mutation, are not queued or retried, and leave the eligible input available for one later explicit wake.

No production source file changes were required.

## Backward wall time

Two byte-identical fixture-configured schema-v2 organisms receive the same input, seed, monotonic readings, and canonical starting state. One wake receives increasing wall times and the other receives decreasing wall times.

The resulting request rows are identical across:

- request ID;
- organism and lineage;
- request ordinal;
- lifecycle and event sequence;
- expiry lifecycle;
- configuration version;
- final canonical envelope bytes;
- canonical size.

Expiry remains exactly request lifecycle plus two. Wall time may differ in canonical event metadata and checkpoint bytes, but it does not enter request identity, ordinal, or lifecycle eligibility.

## Fail-fast wake ownership

The nested case holds an acquired `WakeTransaction` in the same process. The competing case holds a real `BEGIN IMMEDIATE` transaction in a separately spawned process.

In both cases the attempted public garden wake:

- raises `WakeBusyError` with `this attempt was not queued`;
- creates no request row;
- creates no request event or source;
- does not claim or consume the eligible input;
- performs no hidden retry.

After the lock is explicitly released, one caller-selected wake consumes the original input and creates exactly one request.

## CI evidence

Test head `b21c02c82a15a4f0c2bf5353e9fa5db4d2223711`, GitHub Actions run 537:

- 245 passed in 32.86 seconds.

Final exact PR head `2d147d8acc1a4bd4f8750c499e5f94209b05ff55`, run 538:

- 245 tests passed;
- dependency installation succeeded;
- source and test compilation succeeded;
- schema-v1 genesis CLI smoke succeeded.

All original 152 Phase 1 tests remain unchanged and included.

## Remaining request boundary

- P2-D07/D08 require request terminalization/disposition cycles to make four current-lineage requests reachable without contradicting the frozen failure/maintenance threshold;
- P2-D11 belongs with the exact typed-envelope validation work because request creation has no untrusted field input;
- P2-E10 remains blocked on an exact reviewed maximum-envelope interpretation. No unreviewed optional context fields may be invented.

## Next boundary

Issue #61 orders Slice 38 before dispatch. The next implementation work is the exact canonical digest graph and typed external schemas, P2-H01–P2-H11 and P2-I01–P2-I11. Slice 39 dispatch follows only after that foundation is merged.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.
