# Slice 28: Insertion-Order-Independent Tie Breaking

## Purpose

Close Minimal Organism Contract v0.2 evaluation 13: lexicographic seed-garden action tie breaking must remain independent of physical row insertion order.

The fixed Phase 1 policy selects:

1. the lexicographically smallest executable dry living plot for watering
2. otherwise the lexicographically smallest executable mature fruit plot for harvesting
3. otherwise an abstention

Physical SQLite row order, rowid, dictionary order, wall time, and declared seed are not policy inputs.

## Protected stable fixture

`tests/test_insertion_order_tie_breaking.py` creates an explicit administrative fixture from a normal initialized organism.

The fixture:

- deletes and reinserts the two protected garden rows
- physically inserts `bed-b` before `bed-a`
- makes both rows dry living plots
- supplies exactly one water unit
- records the fixture through an administrative event
- creates and registers a stable checkpoint before normal input

The protected test verifies that `ORDER BY rowid` returns:

```text
bed-b, bed-a
```

while canonical lexicographic order returns:

```text
bed-a, bed-b
```

The physical order remains reversed after the wake.

## Complete wake proof

One unique external tick and five exact fake-clock readings drive a complete successful lifecycle.

The test requires:

- canonical `observation_created` plot order `bed-a`, `bed-b`
- canonical `water_plot` applicable targets `bed-a`, `bed-b`
- fixed-policy selection of `water_plot(bed-a)`
- audited seed `97` without seed-based target selection
- one input, one observation, one action attempt, and one environment mutation
- zero caregiver, network, subprocess, and external-write use
- `bed-a` becomes wet while physically first `bed-b` remains dry
- environment step advances exactly once
- water inventory reaches zero
- exact lifecycle event order from `wake_accepted` through `checkpoint_stabilized`
- pending checkpoint boundary 16 and stabilization event 17
- final `sleeping` status
- successful later input acceptance

The stable fixture contributes events 4–6, input enqueue is event 7, and the complete lifecycle is events 8–17.

## Result

The existing implementation passed unchanged.

`build_garden_observation(...)` reads garden rows with explicit `ORDER BY plot_id`. Applicable target tuples inherit that order. `select_garden_decision(...)` chooses the first applicable target, so the policy's first target is the lexicographic minimum rather than the physical first row.

No production source, schema, contract, environment version, action definition, evaluator, clock boundary, budget, checkpoint, or rollback behavior changed.

## Validation

GitHub Actions run 263 on Python 3.12 passed twice on the same test-first head:

- initial attempt: **123 protected tests in 99.70 seconds**
- exact rerun: **123 protected tests in 6.92 seconds**
- clean editable installation passed
- source and test compilation passed
- genesis CLI smoke passed

The slow initial attempt did not reproduce on the exact rerun and is treated as transient runner latency, not a test or runtime defect.

## Boundary preserved

Slice 28 adds only protected coverage and durable documentation. It does not generalize the policy, add random machinery, modify protected environment fixtures in production, or make rowid an application-level interface.
