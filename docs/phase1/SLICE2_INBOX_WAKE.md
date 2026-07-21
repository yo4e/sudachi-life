# Phase 1 Slice 2: Inbox, Wake Acquisition, and Observation

Status: **Implemented on `agent/phase1-inbox-wake`; normal lifecycle commit remains disabled**

Tracked by: Issue #13

## Scope

This slice adds only the entrance to a normal wake:

- idempotent administrative enqueueing of `synthetic:garden_tick`
- fail-fast SQLite write ownership before mutable reads
- one oldest tick claim inside the uncommitted wake transaction
- one deterministic full garden observation

It deliberately does not commit a normal wake, execute `water_plot`, execute `harvest_plot`, consume action budgets, or create a post-wake checkpoint.

`WakeTransaction` is rollback-only in this slice. This prevents an incomplete lifecycle from becoming canonical merely because its acquisition code exists.

## Implemented invariants

### Input enqueueing

- caller-supplied external event identifiers are validated
- the same identifier is idempotent and creates one inbox row and one `input_enqueued` canonical event
- a duplicate returns the existing inbox identity
- a duplicate does not consume another clock reading
- input is accepted only from stable sleeping state with no pending checkpoint
- administrative enqueue uses a fail-fast write transaction

### Wake ownership

- a fresh SQLite connection attempts `BEGIN IMMEDIATE`
- mutable canonical validation occurs only after acquisition
- a competing attempt receives `WakeBusyError`
- the losing attempt is not queued
- an explicit later call is required to retry
- context exit rolls back claimed input and closes the connection

### Input claim

- one wake transaction may claim at most one event
- only unconsumed, unclaimed `synthetic:garden_tick` rows are eligible
- the smallest `inbox_id` is selected
- claim state is transactional and disappears on rollback

### Observation

The observation is fully deterministic and includes:

- environment version and step
- objective status
- inventory
- plots ordered by `plot_id`
- protected water and harvest action definitions
- applicable targets in stable order

No clock, process identity, row insertion order, natural language, hidden state, or random seed affects observation order.

## Protected tests

New tests cover:

- idempotent enqueue without a second clock read
- stable inbox ordering
- one winner and one fail-fast non-queued wake loser
- no canonical validation before lock acquisition
- one oldest tick claim
- rollback of claim state on context exit
- deterministic sorted observation
- rejection of observation before input claim

The full branch validation result must be recorded in the pull request and Issue #13 after a clean checkout test.

## Known incomplete work

- the main `sudachi` CLI is not yet wired to enqueue; the Python administrative API is present
- a normal wake cannot commit
- claimed input is not yet consumed
- no lifecycle events or budget ledger are written for a normal wake
- no action policy or evaluator runs
- no post-wake checkpoint is created
- crash, nested-wake, and full lifecycle timeout tests remain

## Exact next slice

Implement the smallest complete canonical wake for the initial garden action:

1. wire enqueue into the primary CLI
2. load the protected per-wake budget ledger
3. choose `water_plot(bed-a)` from the deterministic observation
4. reserve action and mutation budgets before change
5. execute inside a savepoint
6. independently evaluate the transition
7. mark the tick consumed and append lifecycle records
8. commit an exact checkpoint-pending boundary
9. create and register the stable post-wake checkpoint
10. prove the first canonical wake in protected tests

Do not implement harvest, rollback, caregiver consultation, or generic planning in that slice.
