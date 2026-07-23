# Slice 34: Protected Organism Action Authority

## Purpose

Close Minimal Organism Contract v0.2 evaluation 39: organism actions cannot modify protected files, schema, configuration, evaluator, action definitions, contract, ADRs, or checkpoint machinery.

Slice 33 proved that the registered action executor has no filesystem workspace, network interface, subprocess interface, or external mutable-write route. Slice 34 closes the remaining canonical SQLite authority boundary.

## Authority problem

`execute_garden_action(...)` intentionally receives the existing outer-wake SQLite connection. Before this slice, the two protected action implementations used that connection only for their declared garden transitions, but SQLite itself did not independently restrict statements issued while an action helper was running.

Protected source review remained authoritative, but the runtime boundary did not fail closed if an action implementation attempted SQL outside its declared transition.

## Action-scoped SQLite authorizer

`execute_garden_action(...)` now installs a SQLite authorizer only for the duration of one registered action dispatch and removes it in `finally`.

The authorizer allows:

- `SELECT`
- read access to `action_definition`, `garden_plot`, `inventory`, and `environment_state`
- the existing `garden_action` savepoint begin, rollback, and release operations
- for `water_plot` only:
  - `garden_plot.moisture`
  - `inventory.water_units`
  - `environment_state.environment_step`
- for `harvest_plot` only:
  - `garden_plot.fruit`
  - `inventory.harvested_fruit`
  - `environment_state.environment_step`

All other SQL authorization requests are denied.

Denied authorization is converted to typed `ProtectedAuthorityViolationError`. The outer wake treats it as a fatal protected-boundary failure and rolls back the uncommitted wake rather than classifying it as an ordinary garden rejection.

The executor signature, action registry, garden schemas, evaluator, lifecycle event flow, checkpoint machinery, and existing recoverable action-failure savepoint remain unchanged.

## Protected tests

`tests/test_protected_authority.py` first acquires a normal wake transaction, claims one queued tick, builds the canonical observation, and selects `water_plot(bed-a)`.

### Exact valid mutation

The valid action must change only:

- `garden_plot['bed-a'].moisture`: `0 -> 1`
- `inventory.water_units`: `1 -> 0`
- `environment_state.environment_step`: `0 -> 1`

It must leave exact:

- organism identity, protected versions, lifecycle fields, and checkpoint references
- budget configuration
- action definitions
- inbox state after the declared claim
- canonical event history and SQLite sequences
- checkpoint registry
- SQLite `user_version`
- every schema object and append-only trigger
- protected repository source, evaluator, tests, contract, and ADR files
- checkpoint, export, diagnostic, rollback-archive, and restore-candidate artifacts

The protected probe then rolls back. The same queued tick remains unclaimed and completes through a normal full wake and checkpoint.

### Prohibited mutation probes

A protected test fixture substitutes one action helper at a time while preserving the public action-dispatch boundary. Each fixture attempts one representative forbidden statement:

- rewrite organism contract identity
- rewrite protected budget JSON
- change a registered action version
- change protected garden stage rather than an allowed transition column
- consume inbox state directly
- forge a canonical event
- forge a checkpoint registry row
- change SQLite `user_version`
- drop the append-only event trigger
- create a new schema table

Every attempt raises typed `ProtectedAuthorityViolationError` before effect. Canonical tables, schema, repository files, and administrative artifacts remain exact.

The fixture is test administration only. It is not reachable from the CLI, inbox, decision schema, organism state, or registered action parameters.

## Result

Production correction was required: the previous raw SQLite action boundary trusted protected implementation code but did not independently enforce its SQL mutation subset.

The correction is narrow and action-scoped. It does not add arbitrary SQL, a generic sandbox framework, a permission language, a broader action API, or a new schema.

## Validation

GitHub Actions run 307 on Python 3.12 passed:

- clean editable installation
- source and test compilation
- genesis CLI smoke
- **139 protected tests in 7.69 seconds**

No prior protected behavior required weakening or replacement.
