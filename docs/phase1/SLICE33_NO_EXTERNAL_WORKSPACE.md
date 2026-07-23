# Slice 33: No Organism-Writable External Workspace

## Purpose

Close Minimal Organism Contract v0.2 evaluation 40: Phase 1 exposes no organism-writable external workspace.

This slice tests the organism-action boundary itself. It does not remove or redefine checkpoint, export, diagnostic, rollback-archive, or restore-candidate artifacts, because those remain explicit runtime or administrative operations outside organism action execution.

## Existing action surface

`execute_garden_action(...)` receives exactly:

- the already acquired canonical SQLite connection
- one typed `GardenActionDecision`
- one protected `WakeBudgetLedger`
- the existing keyword-only protected action-failure fixture flag

It receives no `OrganismPaths`, runtime root, path, workspace, export directory, diagnostic directory, rollback archive, restore candidate, network client, or subprocess handle.

The reachable production imports for action execution are limited to deterministic garden types, protected budget accounting, typed errors, and SQLite. The registered water and harvest executors query and mutate canonical SQLite rows only.

## Protected probe

`tests/test_no_external_workspace.py::test_action_execution_has_no_external_workspace_or_effect_surface`:

1. initializes the canonical organism and queues one garden tick
2. acquires the normal fail-fast wake transaction
3. claims the tick, builds the canonical observation, and selects `water_plot(bed-a)` before installing guards
4. captures the complete organism directory set and the exact export, diagnostic, rollback-archive, and restore-candidate workspace entries
5. guards Python filesystem open and mutation APIs, temporary-file creation, network socket creation, subprocess APIs, and operating-system process launch APIs only during action execution
6. requires the valid SQLite water transition to succeed without invoking any guarded interface
7. passes an absolute path-like string as `plot_id` and requires typed `ActionRejectedError` because no such SQLite plot exists
8. proves the path and parent directory remain absent
9. proves the organism directory set and all administrative workspace entries remain exactly unchanged
10. proves both ledgers preserve zero caregiver, network, subprocess, and external mutable-write use
11. rolls back the probe and requires exact pre-probe status and an unclaimed, unconsumed tick
12. completes that same tick through the normal lifecycle and checkpoint path with all hard-zero external capability budgets unchanged

The valid action mutates only `garden_plot`, `inventory`, and `environment_state` inside the existing SQLite transaction. The rejected path-like target never becomes a filesystem target.

## Result

The existing production implementation passed unchanged.

No production source, schema, action definition, evaluator, path abstraction, budget, checkpoint mechanism, export mechanism, rollback machinery, or administrative artifact behavior changed.

No workspace API or generic sandbox framework was added. The protected test provides executable evidence that the current registered organism action surface has no external workspace or effect route.

## CI history

The first two test-only heads failed because the new test encoded incorrect fixed expectations about already initialized administrative directories and the exact pre-probe event count. Existing protected tests remained green, and neither failure exposed a production external-effect path.

The corrected test compares declared pre-action and pre-probe state directly. The implementation head passed **128 protected tests** on Python 3.12. The complete synchronized pull-request head must also pass clean installation, source and test compilation, protected tests, and the genesis CLI smoke test before merge.
