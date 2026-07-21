# ADR 0002: Clock Injection and Deterministic Time

- **Status:** Accepted
- **Date:** 2026-07-21
- **Issue:** #1
- **Scope:** SUDACHI-0 seed architecture

## Context

SUDACHI records events, enforces wall-time budgets, reports durations, may later wake on schedules, and must reproduce deterministic Phase 1 behavior in tests.

Direct calls to the operating-system clock from arbitrary code would create hidden inputs. The same state, event, configuration, and random seed could produce different decisions or records merely because the test ran at another instant or the system clock moved.

One clock cannot safely serve every purpose:

- civil or wall time is useful for audit records and human presentation, but it can jump because of synchronization, manual changes, suspend/resume behavior, or administrative correction
- elapsed-time enforcement needs a clock that does not go backward
- deterministic tests need time supplied as controlled input

ADR 0001 already decides that canonical event order is a monotonically increasing database sequence. Timestamps are metadata and must not compete with that ordering rule.

## Decision

### 1. All time access goes through an injected clock interface

Organism, lifecycle, action, evaluator, budget, persistence, and export code must not call `datetime.now()`, `time.time()`, `time.monotonic()`, or equivalent APIs directly.

They receive a clock dependency through an explicit boundary.

The conceptual interface is:

```text
read() -> ClockReading
```

where a reading contains:

- `wall_time_utc_us`: signed integer microseconds since the Unix epoch in UTC
- `monotonic_ns`: integer nanoseconds from an unspecified monotonic origin

The exact Python protocol or class is deferred to implementation. The two values are exposed together so clock use is visible and tests can count readings.

### 2. Operational runs use a real clock implementation

The production implementation reads:

- UTC epoch time for audit and presentation metadata
- a monotonic nanosecond clock for elapsed durations and deadlines

The real implementation may derive `wall_time_utc_us` from an integer nanosecond epoch clock and truncate to microseconds.

No local timezone is stored in canonical organism state. Local-time rendering is a user-interface concern.

### 3. Tests and deterministic replay use an explicit fake clock

A fake clock supplies declared readings and advances only when the test or replay scenario explicitly advances it.

The fake clock must support:

- fixed time
- explicit forward advancement
- explicit backward wall-time movement while monotonic time continues forward
- equal wall timestamps for multiple events
- deadline crossing
- exhaustion or rejection when code performs an unexpected extra read

Unexpected clock reads should fail tests rather than silently returning the current system time. This exposes hidden time dependencies and unstable call counts.

### 4. Canonical wall timestamps are integer UTC microseconds

Persist wall-clock values as SQLite `INTEGER` values representing microseconds since the Unix epoch.

Reasons:

- integer comparison and serialization are unambiguous
- UTC offset and local-time ambiguity are excluded
- microsecond precision matches the standard Python `datetime` model used for human rendering
- the project does not depend on deprecated default SQLite datetime adapters or converters
- JSONL exports can render the integer directly and may also include a derived ISO 8601 UTC string for readability

The integer is canonical. A rendered timestamp string is derived presentation data.

Negative epoch values are structurally valid even if ordinary experiments do not use them. The storage layer must not silently reinterpret integers as local time.

### 5. Monotonic clock origins are never persisted as global timestamps

The absolute value returned by a monotonic clock has no portable meaning across machines or process restarts.

Canonical records may persist:

- elapsed duration in nanoseconds
- declared timeout or budget duration
- whether a deadline was reached

They must not persist a monotonic reading and later treat it as comparable to a reading from another process lifetime.

Within one wake cycle, deadlines are calculated from monotonic readings. Across cycles, durable scheduling uses explicit wall-time or event data, not a saved monotonic origin.

### 6. Event sequence, not time, defines order

Canonical event order remains the integer sequence accepted in ADR 0001.

Wall timestamps may:

- repeat
- move backward
- be absent on imported external observations
- differ from a source-provided timestamp

None of those conditions reorders committed events.

When the real wall clock moves backward relative to a previously recorded wall timestamp, the system may append a clock-anomaly fact or diagnostic metadata, but it must continue to use event sequence for order.

### 7. Time affects behavior only through declared inputs and policies

Code must not use the current time as:

- a random seed
- an implicit identifier
- a tie breaker
- an unrecorded action-selection input
- a substitute for canonical event sequence

If a policy depends on time, the relevant wall or elapsed value is a declared input to that policy and is covered by deterministic tests.

A scheduled wake is represented by a trigger or queued event. The scheduler's private current time is not an invisible organism observation.

### 8. Time budgets use monotonic elapsed time

Wall-time budgets and action deadlines are enforced using monotonic nanoseconds.

A wall-clock correction must not grant extra runtime or cause premature timeout.

The lifecycle records the declared budget and the resulting elapsed duration or timeout outcome. Tests use the fake monotonic clock, not sleep calls.

### 9. Reproducibility distinguishes decisions from incidental operation time

For deterministic Phase 1 tests, identical:

- canonical state
- ordered input events
- configuration
- random seed
- fake-clock reading sequence

must produce identical decisions, state transitions, and canonical event content.

A real operational run naturally receives different wall timestamps and measured durations. Those differences do not count as behavioral nondeterminism when time is not part of the action-selection policy.

A replay that must reproduce timestamped canonical output supplies the recorded clock readings rather than consulting the current real clock.

### 10. Clock reads occur at explicit semantic points

The implementation must define and test named read points instead of scattering clock access through helper functions.

Expected Phase 1 points include:

- wake start
- before and after an operation whose duration is measured or bounded
- canonical record creation when wall metadata is required

A later schema may allow multiple records created in one transaction to share a wall timestamp. Sequence still distinguishes them.

Clock-read count and placement are part of deterministic behavior and should change only through a reviewed implementation or contract update.

## Consequences

### Positive

- Tests can fully control time without patching global functions.
- Timeout behavior does not depend on wall-clock corrections.
- Stored timestamps are UTC, integer, and portable.
- Event ordering remains stable when timestamps repeat or move backward.
- Hidden time-based identifiers, seeds, and tie breakers are prohibited.
- Replay can supply recorded clock facts explicitly.

### Negative

- Clock dependencies must be threaded through code that needs them.
- Tests must declare time advancement and expected read counts.
- Human-readable timestamps require formatting at boundaries.
- Operational records may contain wall-clock anomalies that need explanation rather than normalization.
- Exact timing measurements are environment-dependent and cannot be compared as if they were deterministic decisions.

### Neutral or deferred

- This ADR does not select the external scheduler.
- This ADR does not define wake cadence.
- This ADR does not define stale-lock age or recovery; ADR 0003 must use these clock semantics.
- This ADR does not define checkpoint timestamps or retention; ADR 0004 must use these clock semantics.
- This ADR does not define the random-number interface.

## Alternatives rejected

### Direct system-clock calls with test monkeypatching

Rejected because time access remains hidden and new calls can bypass patches or change deterministic call order.

### Store ISO 8601 text as the canonical timestamp

Rejected because formatting variants, offsets, precision, and parser behavior create unnecessary canonical choices. ISO strings remain useful derived presentation.

### Store naive local datetime values

Rejected because they are ambiguous across timezone changes and daylight-saving transitions.

### Use wall time for deadlines

Rejected because wall time can move backward or forward independently of elapsed process time.

### Persist absolute monotonic readings across wakes

Rejected because the monotonic origin is intentionally unspecified and not portable across process lifetimes.

### Derive event order from timestamps

Rejected because timestamps may repeat or regress and ADR 0001 already provides a stronger database sequence.

## Required implementation invariants

The later implementation and fixed tests must demonstrate:

1. organism code cannot obtain time without an injected clock
2. identical fake-clock readings produce identical canonical outputs
3. an unexpected extra clock read fails a deterministic test
4. wall time moving backward does not reorder events
5. equal wall timestamps remain unambiguous because event sequence differs
6. timeout enforcement uses monotonic elapsed time
7. wall-clock correction does not change an in-progress monotonic deadline
8. canonical stored wall time is an integer UTC microsecond value
9. local timezone settings do not change canonical storage
10. monotonic origins are not compared across process lifetimes
11. current time is not used as an implicit random seed, identifier, or tie breaker
12. replay can supply recorded clock readings without consulting real time
13. SQLite's deprecated default datetime adapters and converters are not relied upon

## Operational notes for later implementation

- use integer nanosecond APIs for elapsed time to avoid floating-point precision loss
- convert epoch nanoseconds to microseconds with an explicit, tested rule
- create timezone-aware UTC `datetime` values only at presentation or integration boundaries
- define overflow and range validation for persisted microseconds
- use fake-clock advancement rather than real sleeps in tests
- record source-provided event time separately from SUDACHI's recorded time when both matter
- report clock anomalies; do not rewrite historical timestamps to make them appear monotonic

## References

- Python, `time` — monotonic clocks and `monotonic_ns()`: https://docs.python.org/3/library/time.html
- Python, `datetime` — aware UTC datetimes and epoch conversion: https://docs.python.org/3/library/datetime.html
- Python, `sqlite3` — adapters and converters, including deprecation and offset caveats: https://docs.python.org/3/library/sqlite3.html

## Follow-up

Proceed to ADR 0003. It must define runtime locking, duplicate-wake rejection, transaction opening, stale-lock handling, and how real and fake clock readings participate without making wall timestamps authoritative for mutual exclusion.
