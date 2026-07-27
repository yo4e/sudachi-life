# Slice 41: Exact Explicit Disposition Wake

Status: implementation-complete on draft PR #107; final exact-head CI and merge pending.

## Scope

This slice connects ADR 0010 current-state/disposition identities and ADR 0013 final evidence to one explicit caller-selected organism disposition wake.

It does not execute or enqueue an action, mutate the garden, claim garden input, invoke the fixture, create another consultation object, clear maintenance, migrate, roll back, retry, or expand canonical authority.

## Pure canonical schema

`phase2_disposition.py` validates and derives:

- the exact `sudachi.consultation.current_state/v1` identity;
- `H("current-state-reference", current_state_identity)`;
- the exact `sudachi.consultation.disposition/v1` identity;
- `consultation-disposition:H("disposition-id", disposition_identity)`;
- the exact ADR 0013 final envelope;
- exact organism authority;
- the complete six disposition/reason combinations;
- exactly three sorted unique direct parent events.

Independent golden tests reconstruct both digest preimages and IDs without trusting runtime return values.

## Selection and independent reconstruction

`phase2_disposition_runtime.py` is a small public row-link wrapper over the implementation body in `phase2_disposition_runtime_impl.py`.

A fresh fail-fast `WakeTransaction`:

1. requires schema-v2 fixture configuration, sleeping status, no pending checkpoint, and no maintenance reason;
2. selects the oldest eligible current-lineage proposal by ingress sequence then proposal ID;
3. excludes every proposal with an existing immutable disposition;
4. independently reloads and validates the linked request, dispatch, response, proposal, ingress receipt, cost completion, and ingress event;
5. checks canonical envelope bytes, row-only organism/lineage links, IDs, content/package digests, cardinality, event payload, direct ancestry, stable checkpoint registry, and artifact presence;
6. reconstructs the current garden observation from canonical rows under the disposition lock;
7. checks active/reserve/checkpoint-store/working-set limits before reading the clock.

The fixture, external response, and stale request observation do not certify current state.

## Closed disposition mapping

The implementation applies ADR 0013 precedence exactly:

1. considering lifecycle after request expiry: `rejected / expired`;
2. currently applicable permitted action candidate: `accepted / required_evaluators_passed`;
3. valid but currently inapplicable action candidate: `rejected / action_not_applicable_current_state`;
4. abstain with no currently applicable request-allowed action: `accepted / no_supported_action_confirmed`;
5. abstain contradicted by a currently applicable request-allowed action: `clarification_requested / proposal_contradicts_current_state`;
6. unexpired defer: `deferred / await_state_change`.

Unknown disposition/reason combinations reject. Clarification remains final and creates no follow-up work.

## Exact transaction

After every preflight succeeds, the runtime reads the injected clock once and writes exactly four organism events in one transaction:

1. `wake_accepted`;
2. `consultation_disposition_created`;
3. `consultation_disposition_budget_ledger`;
4. `checkpoint_pending`.

The disposition event payload contains exactly `disposition` and `outcome`. The outcome contains exactly disposition, disposition ID, `input_consumed=false`, proposal ID, and reason code.

The fixed ledger is exactly:

```json
{
  "canonical_records_limit": 12,
  "canonical_records_used": 4,
  "configuration_version": "phase2-fixture-v1",
  "phase1_budget_config_version": "phase1-v1",
  "semantic_steps_limit": 10,
  "semantic_steps_used": 8
}
```

All four event rows retain inherited `budget_config_version=phase1-v1` and schema version 2.

The immutable disposition row, event sequence, final envelope, lifecycle increment, organism pending status, and checkpoint boundary commit atomically. The garden failure streak is preserved exactly. No inbox row is claimed or consumed, and environment, inventory, and plot rows remain unchanged.

## Checkpoint publication and repair

After transaction commit and SQLite ownership release, the existing lifecycle checkpoint publisher is invoked with the same injected clock.

Successful publication and registration return the organism to sleeping.

A protected deadline failure after publication but before registration leaves:

- one final disposition;
- one committed pending checkpoint boundary;
- one published orphan checkpoint artifact;
- no repeated proposal eligibility.

The existing `repair_pending_checkpoint_registration` path registers the artifact and returns to sleeping without creating another disposition.

## Atomicity and finality

Protected fault points exist after:

- wake accepted;
- disposition event;
- disposition row;
- budget ledger;
- checkpoint-pending event;
- immediately before commit.

Every precommit fault rolls back every new event/row/lifecycle mutation and restores proposal eligibility.

After successful disposition, another explicit caller-selected wake selects the next eligible proposal or reports no eligible proposal before reading a clock. It never replays the final disposition.

Same-process and spawned competing writers fail fast, queue no hidden work, and permit an explicit later wake after ownership release.

## Physical boundaries

Real-file evidence covers nonmutating refusal for:

- active database with less than the 1 MiB next-wake reserve;
- checkpoint store over 40 MiB;
- runtime working set over 64 MiB.

The runtime also projects the next checkpoint database plus manifest allowance before disposition mutation and repeats the active/reserve/checkpoint/working-set checks after writes but before commit.

## Capability absence

Static source evidence verifies that the disposition runtime does not import or call fixture execution, the garden action executor, networking, subprocesses, or adaptive-state facilities.

The first implementation stops at the disposition record and checkpoint.

## Test-first evidence

Tests-only head `7253671f472ec9b6c85928caf2eccc2c813b6603`, run 586:

- dependency installation and compilation passed;
- protected enforcement failed because `phase2_disposition` did not exist.

Initial runtime head `6942893c28b60505dd896626977402a864c12884`, run 588:

- 340 passed and 15 failed;
- fourteen failures shared one row/envelope linkage bug;
- one failure was the known request-result test fixture attribute.

Corrected core/test head `634876758166680b32dd07b226744aa32cdc6a76`, run 591:

- 355 passed in 34.99 seconds;
- install, compile, and schema-v1 genesis CLI smoke passed.

Boundary head `d7865fdbdde50bd639009919fbc963ae667835ac`, run 592:

- 358 passed in 66.65 seconds;
- spawned fail-fast and real checkpoint-store/working-set refusal passed;
- install, compile, and schema-v1 genesis CLI smoke passed.

All original 152 Phase 1 tests remain unchanged and included.

## Matrix status

Closed or materially closed in this slice:

- ADR 0013 P2-H10 final-envelope evidence;
- P2-L01–P2-L14;
- P2-M01 disposition checkpoint publication and repair;
- P2-N08 exact authority/event/parent reconstruction;
- ordinary and real-refusal portions of P2-O03.

Still dependent on later legitimate cycles or rollback work:

- exact four-request/four-charge epoch boundary;
- mixed 64 KiB logical payload boundary and one-over;
- largest structural request cycle;
- rollback lineage reset and old-lineage late-package rejection;
- complete repeated request→dispatch→ingress→disposition reconstruction across all four ordinals.

No private canonical mutation is used to manufacture those states.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is CI-green and ready for the single implementation-completion audit.