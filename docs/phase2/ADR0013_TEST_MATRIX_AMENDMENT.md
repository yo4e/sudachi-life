# ADR 0013 Phase 2 Test-Matrix Amendment

Status: **Accepted with ADR 0013 on 2026-07-27**

This document synchronizes the protected Phase 2 evidence map with ADR 0013. It replaces only the rows listed below. Every unlisted row in `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` remains unchanged.

| ID | Accepted protected requirement | Required evidence |
| --- | --- | --- |
| P2-H10 | Current-state identity and disposition identity use ADR 0010; the final envelope adds exactly ADR 0013 authority, full current-state reference, disposition ID, event sequence, and three direct parents | Independent golden current-state/digest/identity/ID/envelope vectors; missing/extra/wrong-parent/wrong-authority corpus |
| P2-L01 | Disposition is a separate caller-selected fail-fast organism work class requiring schema-v2 fixture configuration, sleeping, no pending checkpoint, and no maintenance reason | Busy/nested/process overlap and status/configuration rejection with no queued work |
| P2-L02 | Oldest eligible current-lineage proposal is selected by ingress sequence then proposal ID; one proposal with an existing disposition is final and skipped | Multiple-proposal order, prior-disposition skip, old-lineage filtering, and at-most-one evidence |
| P2-L03 | Current-state reference is the exact ADR 0010 projection measured under the disposition lock and stored in the final envelope | Current-row reconstruction, stale-request divergence, fixture-state spoof rejection, digest equality |
| P2-L04 | The complete ADR 0013 disposition/reason mapping and precedence are exact; undeclared combinations reject | Golden vectors for all six mapping branches plus invalid-combination corpus |
| P2-L05 | Invalid schema, ID, digest, linkage, lineage, permission, evaluator set, unknown action, or invalid parameters fail before disposition mutation | One adversarial case per pre-mutation rejection class |
| P2-L06 | One successful transaction writes exactly four events in ADR 0013 order and one immutable disposition row | Exact sequence/source/lifecycle/payload/row linkage and no-extra-event evidence |
| P2-L07 | Disposition event payload contains exactly `disposition` and `outcome`; outcome contains the exact five fields and `input_consumed=false` | Missing/extra/wrong-value corpus and independent payload reconstruction |
| P2-L08 | Disposition budget ledger has the exact six-field ADR 0013 payload, record count 4, semantic-step count 8, and inherited Phase 1 budget version | Exact ledger bytes and no Phase 1 counter consumption |
| P2-L09 | Disposition increments lifecycle by one, preserves the garden failure streak, claims no inbox row, and changes no garden/environment/inventory state | Before/after canonical table and inbox comparison |
| P2-L10 | Transaction commits one pending-checkpoint boundary, then existing checkpoint publication stabilizes to sleeping | Exact pending state, checkpoint registry/artifact, lifecycle, boundary, and return status |
| P2-L11 | Precommit faults leave no disposition and restore selection eligibility; postcommit checkpoint interruption leaves one disposition and repairable pending state | Fault at each write boundary plus publication/registration interruption and repair |
| P2-L12 | Repeated caller-selected wake never replays a final disposition; it selects the next proposal or reports no eligible proposal | No-clock/no-event/no-duplicate evidence for final proposal and deterministic next selection |
| P2-L13 | Expiry uses considering lifecycle: through request expiry is eligible; later is final `rejected/expired`; wall time is irrelevant | Exact boundary and backward/forward wall-time corpus |
| P2-L14 | First implementation stops at disposition and has no action, garden, maintenance, request, dispatch, response, proposal, fixture, retry, memory, or skill effect | Static import/capability absence plus before/after canonical state evidence |
| P2-M01 | Disposition checkpoint publication and repair reuse existing protected checkpoint machinery without repeating disposition | Pending repair, retention/failure, and no-repeat evidence |
| P2-N08 | Event and row authority reconstructs one organism disposition chain with exact three direct parents | Event export and parent/link reconstruction |
| P2-O03 | Disposition ordinary success and real active/reserve/checkpoint-store/working-set refusal preserve inherited physical limits | Real files near each protected boundary; no partial disposition on refusal |

Additional required evidence introduced by ADR 0013:

- all four disposition values and all six reason mappings are exercised;
- clarification is final and creates no follow-up request or fixture work;
- no garden input event, observation, selector, action, evaluation, failure update, or garden lifecycle-completed event appears;
- a spawned or injected crash before commit leaves no disposition;
- a crash after commit but before checkpoint stabilization leaves one disposition and one repairable pending checkpoint;
- all original 152 Phase 1 tests remain unchanged and passing.