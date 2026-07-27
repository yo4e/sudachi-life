# Slice 42a: Finite Consultation Cycle Boundaries

Status: implementation-complete on draft PR #114; final exact-head CI and merge pending.

## Scope

This slice closes the finite current-lineage request, charge, largest-request, and logical-payload boundaries through public canonical operations only.

It does not mutate consultation rows or event sequences directly, change the frozen Phase 1 wake, alter fixture schemas, migrate, roll back, execute a consultation proposal, add context or filler, or expand authority or capability.

## Preserved implementation bodies

The pre-ADR 0016 ingress runtime remains byte-identical in:

```text
src/sudachi_life/phase2_ingress_runtime_impl.py
blob 34a6e136210311e44d5026b69b5d8f9a38b77f8c
```

The retained request constructor remains byte-identical in:

```text
src/sudachi_life/phase2_request_impl.py
blob 46881e023d990f5c7ce393cac7060958419383c0
```

Public wrappers add only the accepted ADR 0015/0016 classifications and delegate every canonical construction or ingress operation to the retained bodies.

## Exact lineage-payload guard

`phase2_ingress_runtime.py` defines one pure function:

```text
validate_lineage_payload_projection(
    current_request_bytes,
    current_success_package_bytes,
    candidate_success_package_bytes,
)
```

It accepts only nonnegative integers, rejects booleans and every unsupported type, performs exact addition, admits projected payload `65536`, and raises the existing typed ingress rejection at `65537`.

The ingress implementation's pre-mutation logical-payload check is replaced with this same function after independently summing:

- current-lineage request canonical sizes;
- current-lineage successful ingress-receipt measured bytes;
- candidate canonical package bytes.

The pure function creates no row, event, artifact, clock read, or organism history.

## Exact fifth-request classification

`phase2_request.py` preserves the retained constructor and translates its no-create result only when the wrapper independently proves every ADR 0015 condition:

- exact fixture configuration;
- an otherwise eligible incomplete-objective `no_applicable_action` wake;
- exact current-lifecycle abstention and observation events;
- a pre-creation budget snapshot;
- four current-lineage request rows;
- no outstanding current-lineage request;
- no maintenance-entering checkpoint.

The public noncanonical result is exactly:

```json
{
  "canonical_size_bytes": null,
  "created": false,
  "event_sequence": null,
  "reason": "consultation_request_not_created_lineage_request_limit",
  "request_id": null
}
```

It creates no fifth request event or row and no downstream consultation state. The unchanged Phase 1 core and ordinary checkpoint still commit.

## Legitimate four-cycle fixture

One fixture uses a maximum-length legal 64-character organism identifier and completes four cycles through public APIs:

1. set an ordinary incomplete no-action garden state;
2. enqueue one garden tick;
3. perform the frozen garden wake and optional request extension;
4. independently measure every declared legal successful fixture package case;
5. dispatch the largest measured case;
6. ingress the exact fixture bytes;
7. finalize the proposal with the explicit disposition wake;
8. perform one ordinary successful water wake to reset only the frozen Phase 1 failure streak;
9. repeat for ordinals two through four.

The independently measured largest closed-v1 package case for this legal request shape is `valid-abstain`. Its disposition is exactly `accepted / no_supported_action_confirmed`.

The fixture proves exactly:

- request ordinals one through four;
- four dispatch rows and conservative charges;
- four successful receipts and measured completions;
- four proposals and final dispositions;
- no fifth request, charge, fixture call, receipt, or disposition;
- no private consultation-row, event, ordinal, charge, or lifecycle mutation.

## ADR 0014 largest structural request

The fourth request uses:

- the maximum legal 64-character organism identifier;
- request ordinal four;
- both declared protected action IDs;
- both derived permission IDs;
- all three requested proposal types;
- the complete closed Protocol-v1 field set;
- no context, filler, padding, free text, opaque field, or integer inflation.

Its exact eight parent event types are independently reloaded by sequence and asserted in order:

1. `wake_accepted`;
2. `input_claimed`;
3. `observation_created`;
4. `action_abstained`;
5. `evaluation_completed`;
6. `failure_streak_updated`;
7. `lifecycle_completed`;
8. `budget_ledger`.

The parent sequences are sorted unique, same lineage, same lifecycle, existing, and earlier than `consultation_request_created`. The request event and later checkpoint boundary are excluded.

The test independently reconstructs the exact request identity, digest-domain preimage, request ID, final canonical bytes, and stored canonical size. The final envelope remains below the 16 KiB hard ceiling.

## Legal Protocol-v1 payload maximum

For every cycle, the test independently measures all declared legal successful fixture cases and uses the largest exact canonical package shape rather than a hard-coded assumption or padding.

After four cycles it independently computes:

```text
sum(stored request canonical_size_bytes)
+ sum(stored successful receipt measured_package_bytes)
```

The result equals the sum of the independently observed request and fixture byte lengths and equals the pure accounting function's projection with zero candidate bytes.

The legal four-cycle total is strictly below 64 KiB. Response and proposal canonical sizes are separately measured to prove that metadata would increase the number if it were incorrectly double-counted. They remain excluded from the logical formula.

A fifth eligible wake cannot increase logical payload because the four-request limit applies first and returns the exact ADR 0015 refusal.

## Physical and checkpoint evidence

After all four cycles and the fifth refusal:

- active allocated database bytes plus the 1 MiB reserve remain at or below 8 MiB;
- every retained checkpoint database artifact remains at or below 8 MiB;
- checkpoint-store bytes remain at or below 40 MiB;
- runtime working-set bytes remain at or below 64 MiB;
- the fifth Phase 1 core wake produces and stabilizes an ordinary checkpoint;
- consultation table counts remain exactly four for requests, charges, receipts, and dispositions.

## Test-first evidence

Tests-only head `7364c428d79bce4a20196913ce4116a66add0fa9`, run 601:

- installation and compilation passed;
- protected enforcement failed because the ADR 0016 pure function did not exist.

Initial implementation head `60e5a9c5b62f2cc17fa7e6e500eb7287fe43fe40`, run 603:

- 354 passed and six failed;
- five failures shared one fifth-limit eligibility reconstruction bug;
- one failure assumed a 128-character organism ID although the repository path contract permits exactly 64.

Corrected wrapper and identifier head `49323d175c9725d82ac0632fb3f9c74d66da842d`, run 605:

- 359 passed and one failed;
- the remaining failure was the test assumption that `valid-action-candidate` was the largest package; independent measurement showed `valid-abstain` is larger.

Measured-case head `663443f5f45b0157b1fdaf182d176360dc9b7a45`, run 606:

- 360 passed in 50.75 seconds;
- dependency installation, source/test compilation, and schema-v1 genesis CLI smoke passed.

All original 152 Phase 1 tests remain unchanged and included.

## Matrix status

Closed or materially closed in this slice:

- P2-D07 current-lineage four-request boundary and exact fifth refusal;
- P2-D08 four complete legitimate request cycles;
- P2-E10 legal largest structural request under ADR 0014;
- P2-F08 four conservative charges and no fifth invocation;
- P2-J09 pure 64 KiB/one-over guard and legal closed-v1 maximum under ADR 0016;
- P2-M07 current-lineage four request/charge cycle;
- applicable physical portions of P2-O01–P2-O03.

Still dependent on later accepted rollback and closure work:

- P2-J10 and P2-M08–P2-M10 new-lineage epoch reset;
- old-lineage package/proposal rejection after rollback;
- full two-lineage maximum of eight charges under the one-rollback rule;
- complete event export and authority reconstruction across rollback;
- remaining explicit absence and implementation-completion matrix review.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is CI-green and ready for the single implementation-completion audit.