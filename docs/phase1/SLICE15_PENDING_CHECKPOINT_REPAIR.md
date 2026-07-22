# Phase 1 Slice 15: Pending Checkpoint Registration Repair

Status: **implemented locally; GitHub validation pending in PR #29**

Tracked by: Issue #13

## Scope

This slice protects one explicit administrative repair for exactly one valid immutable lifecycle checkpoint artifact that was published before a checkpoint-deadline failure but was not registered.

The repair is not an organism action. It is exposed through:

- `repair_pending_checkpoint_registration(runtime_root, organism_id)`
- `sudachi checkpoint repair-pending <organism_id>`

## Protected fixture

The fixture performs the canonical first water wake with the protected checkpoint deadline exceeded by one nanosecond.

Before repair:

- lifecycle number `1`
- environment step `1`
- water inventory `0`
- objective incomplete
- committed pending boundary `13`
- event count `13`
- status `checkpoint_pending`
- latest stable boundary still `2`
- genesis remains registered
- one lifecycle checkpoint artifact for boundary `13` is published and fully formed but absent from the registry

## Exact administrative validation

The repair acquires fail-fast `BEGIN IMMEDIATE` ownership and performs no clock read until every eligibility check has passed.

It requires:

- exact canonical `checkpoint_pending` state without maintenance
- pending generation equal to the active lineage
- the maximum canonical event equal to the pending boundary
- a valid previous latest-stable registry row and artifact
- no unresolved hidden staging entries or unsafe visible entries
- exactly one visible unregistered checkpoint directory
- a canonical checkpoint identifier derived from lineage, event boundary, and database digest
- matching organism identity, lifecycle, versions, provenance, and published status
- exact manifest and database digests and protected byte limits
- an immutable snapshot whose organism row, protected configuration, environment, plots, inventory, action definitions, inbox, events, and previous checkpoint registry exactly match the active committed pending state

Zero, multiple, mismatched, or invalid candidates are rejected without clearing pending state or reading the clock.

## Atomic repair

After validation, one injected administrative clock read supplies the registration and audit timestamp.

One SQLite transaction then:

1. inserts exactly one protected checkpoint-registry row
2. sets the repaired checkpoint as latest stable at boundary `13`
3. clears pending generation and event-boundary fields
4. restores status `sleeping`
5. appends typed `checkpoint_registration_repaired` event `14` from `administration:checkpoint-repair`

The audit payload records the checkpoint identity, lineage, event boundary, database and manifest digests, database bytes, total checkpoint-store bytes, previous latest-stable checkpoint, typed reason `published_checkpoint_registration_missing`, and before/after status.

No checkpoint artifact is changed, copied, renamed, or deleted by the repair.

## Preserved state and continuation

The repair preserves:

- lifecycle number `1`
- environment step `1`
- garden plots and inventory
- incomplete objective
- failure streak zero
- the consumed first tick
- genesis registry and artifact
- exact checkpoint-store bytes

After repair, a second tick can be enqueued normally. The unchanged fixed policy harvests `bed-b`, commits boundary `24`, stabilizes at event `25`, completes the objective, and returns to `sleeping`.

## Rejection coverage

Protected tests prove that:

- no orphan candidate leaves canonical pending state unchanged
- two visible orphan candidates are rejected as ambiguous
- one internally valid artifact from another organism is rejected as mismatched
- one corrupted manifest is rejected as invalid
- every rejected case performs zero clock reads and changes no canonical row, event, database digest, or checkpoint file digest
- a competing SQLite writer produces typed fail-fast busy rejection without queueing or clock use
- a repeated repair after success is rejected because the organism is no longer pending

## Validation

Local source-tree validation completed:

- `python -m compileall -q src tests`
- **50 protected tests**

A separate local clean editable install could not resolve `hatchling>=1.25` from the execution environment's package mirror. That mirror failure is not treated as success. GitHub Actions must independently complete clean installation and the protected suite before merge.

## Deliberately out of scope

- ambiguous-orphan cleanup or checkpoint deletion
- broad checkpoint repair
- retention-failure maintenance clear
- lineage-preserving rollback
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

The next slice must be selected from the remaining Contract v0.2 evaluation matrix only after PR #29 is independently verified and merged. The exact scope must be confirmed against current Issue #13 and repository state before implementation.
