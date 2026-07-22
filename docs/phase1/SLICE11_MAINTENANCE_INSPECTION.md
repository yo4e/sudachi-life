# Phase 1 Slice 11: Read-Only Maintenance Inspection

Status: **implemented and verified in PR #25**

Tracked by: Issue #13

## Scope

This slice adds one explicit administrative inspection boundary for a stable organism whose canonical status is `maintenance_required`.

The boundary is available through:

- Python API `inspect_maintenance(runtime_root, organism_id)`
- CLI `sudachi maintenance inspect <organism_id>`

It is not a normal organism wake and it cannot clear or repair maintenance.

## Read-only boundary

Inspection opens the canonical SQLite database with `mode=ro`, begins one read transaction, and runs `validate_canonical_state(..., expect_checkpoint_pending=False)` before reporting anything.

The API has no clock parameter and performs no clock read. It exposes no write connection, mutation callback, retry, or maintenance-clear switch.

Inspection is accepted only when canonical status is exactly `maintenance_required`. Sleeping and other non-maintenance states are rejected through typed `MaintenanceInspectionRejectedError`.

## Reported state

The result reports:

- organism identifier
- lineage generation and lifecycle number
- canonical status
- typed maintenance reason
- consecutive failure count
- checkpoint-pending flag
- latest stable checkpoint identifier, lineage, event boundary, and protected flag
- total inbox rows
- consumed inbox rows
- unclaimed queued rows
- claimed but unconsumed rows
- exact unconsumed input rows in stable `inbox_id` order

The inspection independently proves that the latest stable checkpoint registry row matches the organism's lineage and stable event boundary. It also proves that inbox totals equal consumed plus queued-unclaimed plus claimed-unconsumed rows.

## Protected fixture

The isolated protected fixture has:

- lifecycle number `0`
- incomplete blocked garden
- water inventory `0`
- failure streak `3`
- maintenance reason `consecutive_failure_limit_reached`
- one queued unclaimed `synthetic:garden_tick`
- stable checkpoint boundary `6`
- event count `8`
- final status `maintenance_required`

The inspection reports the queued tick without claiming or consuming it.

## Zero-mutation proof

`tests/test_maintenance_inspection.py::test_read_only_maintenance_inspection_reports_without_mutation` invokes both the Python API and JSON CLI.

Before and after both inspections, the test proves:

- every file under the organism directory has the same size
- every file has the same modification time
- every file has the same SHA-256 digest
- organism status is identical
- event count is identical
- every inbox row is identical
- every checkpoint-registry row is identical

A later normal wake remains rejected while consuming zero clock readings and changing no file.

`tests/test_maintenance_inspection.py::test_maintenance_inspection_rejects_nonmaintenance_state` proves that a stable sleeping organism cannot be misreported as being under maintenance and that the CLI returns a typed error.

## Validation

Local source-tree validation completed compileall and **36 protected tests**.

A separate local clean editable install could not resolve `hatchling>=1.25` from the execution environment's package mirror. That mirror failure is not treated as success.

GitHub Actions on Python 3.12 independently completed clean editable installation, compileall, genesis CLI smoke, and **36 protected tests**.

## Deliberately not implemented

- maintenance exit or failure-counter clearing
- environment repair
- checkpoint repair or retention pruning
- lineage rollback
- caregiver consultation, learning, memory, or generic planning

## Exact next slice

After PR #25 is merged, Slice 12 will add one explicit administrative maintenance-clear transaction for the protected consecutive-failure condition.

It must require a recorded recovery reason, acquire fail-fast SQLite write ownership, validate the stable maintenance state and latest checkpoint, atomically reset the failure streak to zero, clear the maintenance reason, restore `sleeping`, append a distinct administrative audit event, preserve the environment, checkpoint references, and queued inputs, and prove a later normal wake is permitted to process the queued tick.

It must not add environment repair, checkpoint repair, rollback, caregiver consultation, learning, memory, or generic planning.
