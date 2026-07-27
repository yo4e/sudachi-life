# ADR 0011 Adoption Record

Status: **Accepted**

Date: **2026-07-27**

The project owner explicitly stated:

> Issue #96の推奨clarificationを正式採用する

This is an explicit design instruction under the SUDACHI collaboration rules. It authorizes the exact recommendation recorded in Issue #96 and no broader change.

Accepted scope:

- `consultation_cost_charge.charge_id` is the typed alias of the linked dispatch digest;
- the single event type is `consultation_dispatch_admitted`;
- dispatch and charge rows reference that one event sequence;
- the event payload contains exactly `dispatch` and `charge`;
- the dispatch payload value is the exact final ADR 0010 dispatch envelope;
- the charge payload value is the exact ADR 0011 conservative ledger;
- request bytes satisfy stored/recomputed equality;
- no separate cost event, refund, retry, checkpoint, action, authority expansion, or fixture result is added.

Durable normative records:

- `docs/decisions/0011-fix-dispatch-admission-charge-and-event.md`
- `docs/phase2/ADR0011_TEST_MATRIX_AMENDMENT.md`

This adoption does not authorize live caregivers or models, network or subprocess access, arbitrary code, automatic retry, action execution, memory, skills, training, or generic-agent behavior.