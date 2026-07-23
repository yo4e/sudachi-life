# Phase 1 Slice 25: Declared Seed Independence

Status: **implemented and verified in PR #41**

Tracked by: Issue #13

## Scope

This slice closes Minimal Organism Contract v0.2 evaluation 4 with one protected comparison between two complete canonical first-water wakes that differ only in the declared seed.

The slice adds protected coverage only. It does not change production code, schema, clock semantics, fixed policy, action execution, evaluation, budgets, event format, checkpoint machinery, or rollback behavior.

## Protected scenario

`tests/test_seed_independence.py::test_different_declared_seeds_preserve_first_wake_behavior`:

1. initializes two independent organisms with the same organism identity, protected configuration, genesis clock, and `seed-garden-v1` state
2. enqueues the same uniquely identified `synthetic:garden_tick` with the same injected clock reading
3. supplies the same five wake and checkpoint clock readings
4. performs one complete first-water wake with declared seed `1`
5. performs the same complete first-water wake with declared seed `2`
6. proves both declared values remain visible in `WakeResult.seed` and the canonical `wake_accepted` audit event
7. compares the complete logical canonical bodies and lifecycle checkpoint snapshots through a protected behavior projection

## Behavior projection

The declared seed is an audit input, not a policy input. The comparison therefore normalizes only:

- the `seed` value in `WakeResult` and the `wake_accepted` payload
- digest-derived checkpoint identifiers
- checkpoint database and manifest digests that necessarily inherit the distinct audited seed value

Everything else must match exactly:

- deterministic observation and fixed-policy choice
- `water_plot(bed-a)` parameters
- positive independent evaluation
- complete concrete budget ledger
- garden and inventory transition
- inbox claim and consumption
- lifecycle number and failure state
- event sequence, event types, sources, timestamps, versions, and all non-seed payload fields
- checkpoint-pending boundary 13
- checkpoint registry metadata other than digest-derived identity fields
- lifecycle checkpoint manifest fields other than checkpoint identifier and database digest
- final stable status, event count 14, and wakeability
- SQLite sequence state

The active canonical database and the immutable lifecycle checkpoint snapshot are both compared logically. This prevents a passing result from hiding seed-sensitive state behind a matching top-level decision.

## Exact result

Both organisms:

- select `water_plot(bed-a)`
- change `bed-a.moisture` from `0` to `1`
- consume the one water unit
- advance environment step from `0` to `1`
- leave the protected objective incomplete
- consume one input, one observation, one action attempt, and one successful mutation
- consume zero caregiver, network, subprocess, and external mutable-write capability
- commit lifecycle checkpoint boundary 13
- append `checkpoint_stabilized` at event 14
- return to `sleeping`

The distinct seed remains auditable. Because that seed is part of canonical event history, the lifecycle checkpoint database digest, manifest digest, and digest-derived checkpoint identifier differ as expected. No behavioral or non-derived canonical field differs.

## Verification

GitHub Actions run 233 on Python 3.12 completed:

- clean editable installation
- source and test compilation
- **119 protected tests passed in 5.44 seconds**
- genesis CLI smoke test

No production correction was required. The existing fixed policy already satisfied the accepted contract.

## Deliberately out of scope

- generic random-number or replay machinery
- full repeated-run canonical equivalence
- cleanup-grace behavior
- altered insertion-order tie breaking
- duplicate-input replay after action
- process-crash execution
- nested-wake rejection
- schema, contract, environment, budget, or action changes
- rollback-artifact deletion, pruning, or repeated rollback
- JSONL import
- caregiver, learning, memory, skills, or later-phase machinery

## Exact next action

After PR #41 is merged, reconstruct current `main`, Issue #13, and open pull requests before creating another branch. The next bounded subject is Slice 26: complete repeated-run canonical equivalence for identical declared inputs. It must compare two independent complete canonical runs without normalizing any declared input and require identical logical canonical state, event history, lifecycle boundaries, checkpoint manifests, digest-derived checkpoint identities, stable status, and wakeability. Production code changes are permitted only if that protected comparison exposes a contract violation.