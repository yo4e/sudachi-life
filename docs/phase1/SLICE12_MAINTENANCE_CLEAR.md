# Phase 1 Slice 12: Explicit Administrative Maintenance Clear

Status: **implemented and verified in PR #26**

Tracked by: Issue #13

## Scope

This slice adds one explicit administrative transaction for clearing the protected consecutive-failure maintenance condition.

The boundary is available through:

- Python API `clear_maintenance(runtime_root, organism_id, recovery_reason, clock=...)`
- CLI `sudachi maintenance clear <organism_id> --reason <reason>`

It is not an organism action and it does not repair the environment, checkpoints, or lineage.

## Protected clear transaction

The transaction requires a caller-supplied recovery reason matching the bounded administrative token format. It acquires fail-fast SQLite write ownership, validates stable canonical state, and accepts only:

- status `maintenance_required`
- checkpoint pending false
- failure streak exactly `3`
- maintenance reason `consecutive_failure_limit_reached`
- a protected latest stable checkpoint whose lineage and event boundary match the organism row

The transaction then atomically:

1. sets status to `sleeping`
2. resets the failure streak from three to zero
3. clears `maintenance_reason`
4. records the administrative return-to-sleep wall time through the injected clock
5. appends one typed `maintenance_cleared` audit event with the caller-supplied recovery reason and previous protected state

If the audit event fails, the state update rolls back with it.

## Preserved state

The clear transaction preserves:

- plots
- inventory
- objective state
- environment step
- lineage generation
- lifecycle number
- latest stable checkpoint identifier and event boundary
- checkpoint registry
- every queued input row and claim/consumption field

The protected fixture retains one queued, unclaimed, unconsumed garden tick through the clear transaction.

## Later normal wake

After the clear commits, the organism is sleeping with failure streak zero and no maintenance reason. A later normal wake may claim the preserved tick under the unchanged fixed policy.

The blocked fixture produces a classified `no_applicable_action` wake, consumes the preserved tick, advances the failure streak from zero to one, checkpoints the committed boundary, and returns to sleeping. No environment repair is implied.

## Protected tests

`tests/test_maintenance_clear.py` protects:

- exact successful API clear and administrative audit payload
- environment, checkpoint, and inbox preservation
- later normal-wake processing of the preserved tick
- CLI clear and repeat-clear rejection
- recovery-reason validation before clock or database mutation
- fail-fast busy rejection before clock use
- atomic rollback when the audit event is forced to fail
- rejection outside stable maintenance state

Local source-tree validation completed compileall and **41 protected tests**.

A separate local clean editable install could not resolve `hatchling>=1.25` from the execution environment's package mirror. That mirror failure is not treated as success. GitHub Actions on Python 3.12 independently completed clean editable installation, compileall, genesis CLI smoke, and **41 protected tests**.

## Deliberately not implemented

- environment repair
- checkpoint repair or retention pruning
- lineage rollback
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

After PR #26 is merged, Slice 13 will implement the successful bounded checkpoint-retention path. Starting from the canonical four stable checkpoints, it must create and register one newer stable checkpoint before pruning the oldest eligible checkpoint, retain exactly four artifact directories and registry rows, preserve the newest and latest-stable references, and record pruning administratively. Prune-failure recovery, checkpoint repair, and rollback remain later work.
