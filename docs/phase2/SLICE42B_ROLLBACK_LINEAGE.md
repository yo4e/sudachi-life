# Slice 42b: Rollback Lineage Epoch Boundaries

Status: merged through PR #116 as `0059e0e20ececcf9e16a9b1a4376c3564cf9c391`.

## Scope

This slice closes the accepted rollback and current-lineage consultation epoch boundaries through public request, dispatch, fixture, ingress, disposition, ordinary checkpoint, rollback archive, source-candidate, transformed-candidate, active-replacement, completion, and event-export APIs.

It proves one complete four-request/four-charge abandoned lineage followed by one complete four-request/four-charge current lineage. It does not manufacture consultation rows, ordinals, charges, lineage values, packages, dispositions, payload sizes, or events through private canonical mutation.

No live caregiver, human chat, model API, network, subprocess, memory, skill, action adoption, migration, generic-agent behavior, or additional rollback is authorized.

## Test-first rollback evidence

Tests-only head `cf430bd7546e8a5f486da7c08e0c5615de0b4bd3`, run 611:

- dependency installation and source/test compilation passed;
- protected tests reported `362 passed, 1 failed in 52.26s`;
- old-lineage late-package rejection passed;
- old-lineage proposal inactivity and current-lineage proposal selection passed;
- the sole failure occurred at the first ordinary checkpoint after a completed rollback.

The failure was:

```text
CheckpointError: checkpoint database is missing or unsafe
```

The failure exposed a deterministic composition defect between retained checkpoint snapshots, later checkpoint retention, rollback transformation, and the next checkpoint.

## Rollback-retention defect

Checkpoint creation snapshots the pending active SQLite database before the new checkpoint row is registered and before retention runs.

The protected retention limit is four checkpoints. A fifth or later checkpoint artifact can therefore contain a registry row whose artifact is legitimately pruned immediately after the snapshot is published and registered.

Rollback restores the selected checkpoint snapshot. The pre-repair transformation preserved every source registry row and added the selected checkpoint registry row. A post-retention rollback could therefore restore a registry row for an artifact that the abandoned future had already pruned. The next retention scan attempted to validate that missing artifact and failed.

This was not filesystem corruption, retryable interruption, or a Phase 2 fixture assumption. It was deterministic temporal skew between the selected checkpoint snapshot and the exact pre-rollback archived future.

Issue #117 records the defect, rejected alternatives, and minimal repair. The project owner explicitly authorized the narrowly scoped frozen-Phase-1 repair on 2026-07-28 JST before implementation continued. Issue #117 closed after PR #116 merged the protected repair.

## Preserved implementation body

The pre-repair transformation remains byte-identical in:

```text
src/sudachi_life/rollback_transform_impl.py
blob 91f77ff91929f53be46dc9b74a3d1558ddd89b00
```

The public `rollback_transform.py` wrapper adds only bounded working-set guards and exact checkpoint-retention reconciliation around the retained implementation.

No Phase 1 protected test, schema, checkpoint-retention rule, rollback event type, authority category, physical limit, consultation rule, or manifest format is changed.

## Exact reconciliation rule

For the selected source candidate and exact pre-rollback archive, the public wrapper independently reloads and validates both checkpoint registries.

A source registry row may be removed from the transformed candidate only when all of these facts are proven:

- the row exists in the selected checkpoint snapshot;
- the exact row is absent from the verified pre-rollback archive registry;
- all registry rows present in both bodies remain byte-for-byte equal;
- the archive contains exactly one later `checkpoint_pruned` event naming that checkpoint;
- the event has source `administration:checkpoint-retention`;
- organism, lineage, event ordering, checkpoint ID, checkpoint event sequence, database size, protected bit, reason, and retention limit match exactly;
- the evidence does not name genesis;
- neither a retained checkpoint directory nor `.pruning-<checkpoint-id>` staging directory exists.

Any unexplained missing row, changed retained row, duplicate evidence, malformed payload, mismatched authority or accounting, unsafe identifier, retained artifact, or staged artifact fails closed before transformed-candidate publication.

The proved rows are deleted inside the same bounded SQLite transformation transaction before the retained implementation changes lineage state and appends `rollback_lineage_prepared`.

The same plan is independently re-derived during candidate validation, repeated transformation, active replacement, and rollback completion. No manifest self-assertion or hidden mutable reconciliation ledger is trusted.

## Dedicated schema-v1 regression

`tests/test_rollback_retention_reconciliation.py` uses the unchanged schema-v1 initialization fixture and public operations only:

1. initialize genesis;
2. perform four ordinary garden wakes, crossing the four-checkpoint retention limit;
3. select the newest stable checkpoint;
4. prepare the exact pre-rollback archive;
5. begin rollback and build the source candidate;
6. prove the source registry contains one row absent from the archive registry and that its artifact is absent;
7. transform the candidate and prove the transformed registry exactly equals the archive registry;
8. repeat transformation idempotently with no clock read;
9. replace the active database and complete rollback;
10. perform the first ordinary new-lineage wake and stabilize its checkpoint;
11. prove every remaining registry row has a retained artifact.

A separate corruption case recreates the exact `.pruning-<checkpoint-id>` staging path. Transformation rejects before publication and leaves only the source candidate.

All original 152 Phase 1 tests remain unchanged.

## Two-lineage consultation evidence

The full fixture completes four old-lineage consultation cycles through public APIs:

```text
garden request wake
-> administrative fixture dispatch and conservative charge
-> exact fixture package ingress
-> explicit disposition wake and checkpoint
-> ordinary successful garden wake and checkpoint
```

It selects the final old-lineage stable checkpoint, executes one complete public rollback, and reconstructs consultation tables in:

- the selected checkpoint;
- the pre-rollback archive;
- the source restore candidate;
- the transformed candidate;
- the completed active database.

Every consultation table and consultation AUTOINCREMENT sequence remains exact across those bodies.

Immediately after completion:

- active lineage is one;
- old lineage still contains four requests, dispatches, charges, receipts, proposals, and dispositions;
- new lineage contains zero consultation operational rows;
- old-lineage logical payload is unchanged;
- new-lineage logical payload is exactly zero.

The fixture then completes new-lineage request ordinals one through four and proves:

- four fresh new-lineage charges;
- eight total charged fixture invocations across the physical organism;
- the exact typed fifth-request refusal in the new lineage;
- no ninth fixture invocation;
- rejection of a second rollback preparation because one `rollback_completed` event exists.

## Historical inactivity and stale work

One fixture rolls back a checkpoint that already contains an unresolved old-lineage charged dispatch.

After rollback:

- byte-exact ingress of the old fixture package rejects before clock use or mutation because the work is not in the current lineage;
- consultation tables and event count remain exact;
- a new-lineage ordinal-one request and charged dispatch remain available.

A second fixture rolls back a checkpoint that already contains an unresolved old-lineage proposal.

After rollback:

- a disposition wake reports no eligible current-lineage proposal without a clock read or mutation;
- a new-lineage proposal can be created and is selected;
- the old proposal receives no disposition row.

Old rows are immutable historical evidence, not deleted work and not eligible current work.

## Event, authority, ancestry, and artifact evidence

The final stable event export is independently decoded and proves:

- complete event sequences from one through the declared boundary;
- events from both lineage zero and lineage one;
- exactly eight request-created events and eight dispatch-admitted events;
- rollback lineage preparation and completion in lineage one;
- exact protected sources `administration:rollback-candidate` and `administration:rollback`;
- manifest linkage across archive, source candidate, transformed candidate, and completion.

Request, dispatch, ingress, proposal, disposition, checkpoint, rollback, and export operations retain the existing protected organism/administration authority map. Fixture provenance never becomes writer authority.

The rollback archive, source candidate, transformed candidate, and retained checkpoint artifacts remain present and independently validated. Every database artifact remains at or below 8 MiB, active allocation plus reserve remains at or below 8 MiB, checkpoint store remains at or below 40 MiB, and the runtime working set remains at or below 64 MiB.

## CI evidence

Implementation and regression head `685e62d4260bc686cbbb65ec1d8f41b9e28a4d14`, run 613:

- dependency installation passed;
- source and test compilation passed;
- `365 passed in 51.81s`;
- protected test enforcement passed;
- schema-v1 genesis CLI smoke passed.

Final exact PR head `7f9b718f8b65f71e411a5ed632257ed5609d3ede`, run 614:

- dependency installation passed;
- source and test compilation passed;
- `365 passed in 46.13s`;
- protected test enforcement passed;
- schema-v1 genesis CLI smoke passed.

PR #116 merged that head as `0059e0e20ececcf9e16a9b1a4376c3564cf9c391`.

## Matrix status

Closed or materially closed in this slice:

- P2-D08 fresh request ordinal after rollback;
- P2-F08 fresh four-charge epoch after rollback;
- P2-J10 fresh logical-payload epoch with historical old rows;
- P2-M08 rollback lineage increment and historical inactivity;
- P2-M09 fresh four-call and payload epoch;
- P2-M10 eight-call physical maximum under the one-completed-rollback rule;
- P2-M11 unresolved old work nonblocking and late package rejection;
- P2-N03 protected rollback administration sources;
- rollback-crossing portions of P2-N05 and P2-N07;
- P2-O03 aggregate rollback working-set accounting;
- P2-O12 abandoned consultation history and blocked abandoned work;
- P2-O13 unchanged one-completed-rollback rule and evidence retention;
- P2-O14 rollback-to-retention reconciliation with consultation preservation;
- P2-O18 absolute inherited physical limits after two epochs;
- P2-O20 fail-closed missing/staged artifact and registry-link validation;
- P2-O22 exact consultation rows and immutable configuration across rollback artifacts.

No new Phase 2 behavior remains to be designed in this slice.

## Next gate

After the Slice 42b closeout merges:

1. map every accepted P2-A through P2-P row to its protected implementation evidence;
2. verify all 152 Phase 1 tests remain byte-unchanged and included;
3. verify schema-v1 support and explicit-absence surfaces at the exact candidate head;
4. assemble accepted ADRs, implementation notes, completed matrix mapping, CI evidence, and current Issues;
5. request the single independent read-only Phase 2 implementation audit required by `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`;
6. repair only accepted audit findings through protected evidence;
7. freeze Phase 2 only after a satisfactory completion conclusion.

No per-slice Codex audit was used for Slice 42b.
