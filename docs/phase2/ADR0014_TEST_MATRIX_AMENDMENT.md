# ADR 0014 Phase 2 Test-Matrix Amendment

Status: **Accepted with ADR 0014 on 2026-07-27**

This document synchronizes the protected Phase 2 evidence map with ADR 0014. It replaces only P2-E10's impossible sixteen-parent example. Every other accepted row and every other ADR 0010 requirement remain unchanged.

| ID | Accepted protected requirement | Required evidence |
| --- | --- | --- |
| P2-E10 | A successful largest structural Protocol-v1 request uses the maximum legal organism ID, current-lineage ordinal four, every declared action/permission/proposal-type entry, the full closed envelope, and exactly the eight existing eligible `no_applicable_action` core parents; its ordinary checkpoint preserves all physical limits and the 1 MiB reserve | Legitimate four-cycle schema-v2 fixture; independent exact event-type/sequence, identity/ID/byte, row/event, checkpoint, sidecar, active/artifact/store/working-set/reserve assertions; no filler or private canonical mutation |

The exact parent event types in order are:

1. `wake_accepted`;
2. `input_claimed`;
3. `observation_created`;
4. `action_abstained`;
5. `evaluation_completed`;
6. `failure_streak_updated`;
7. `lifecycle_completed`;
8. `budget_ledger`.

Additional protected evidence:

- parent sequences are sorted unique, same-organism, same-lineage, same-lifecycle, existing, and earlier than the request event;
- `consultation_request_created` and the later `checkpoint_pending` event are not request parents;
- missing, extra, reordered, future, cross-lineage, cross-lifecycle, and wrong-type parent corpora reject;
- request ordinal four is reached only through legitimate earlier consultation finalization and ordinary garden transitions;
- the maximum-length legal organism ID and all fixed arrays are used without context, filler, padding, free text, opaque fields, repeated collections, or integer inflation;
- exact canonical request bytes remain below the 16 KiB hard ceiling;
- all original 152 Phase 1 tests remain unchanged and passing.