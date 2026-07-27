# ADR 0010 Phase 2 Test-Matrix Amendment

Status: **Accepted with ADR 0010 on 2026-07-27**

This document synchronizes the protected Phase 2 evidence map with ADR 0010. It replaces only the rows listed below. Every unlisted row in `docs/PHASE2_CONSULTATION_TEST_MATRIX.md` remains unchanged.

| ID | Accepted protected requirement | Required evidence |
| --- | --- | --- |
| P2-D11 | Protocol v1 request has the exact closed field set implemented by Slice 38a and no optional context or free text | Missing/extra/context/padding/free-text/authority adversarial corpus |
| P2-E10 | A successful largest structural protocol-v1 request—maximum legal organism ID, ordinal four, all declared action/permission/proposal-type entries, and 16 current-lifecycle parent events—plus its ordinary checkpoint preserves all physical limits and the 1 MiB reserve | Real schema-v2 fixture and checkpoint; no synthetic filler field |
| P2-H04 | Dispatch identity has exactly the ADR 0010 fields, including `configuration_version`, and excludes later sequence, wall time, cost, authority metadata, and fixture output | Independent golden preimage/ID/envelope vectors plus extra/missing-field corpus |
| P2-H07 | Response ID uses the exact ADR 0010 response identity and already-derived proposal IDs/content digests without a cycle | Independent graph construction for `proposals_returned` and `unavailable` |
| P2-H08 | Derived response ID is inserted into final proposal linkage before the package digest | Exact final proposal/response/package bytes |
| P2-H09 | Package preimage has exactly `response` and `proposals`; cardinality is one or zero according to response status | Missing/extra/reordered/cardinality rejection |
| P2-H10 | Current-state digest uses the exact `sudachi.consultation.current_state/v1` projection and disposition identity fields fixed by ADR 0010 | Golden projection/digest/disposition vectors plus stale/current mutation corpus |
| P2-I01 | Response identity/envelope and the exact three-field provenance object have closed fields, protected adapter values, exact status/cardinality, and linked fixture case | Unknown/missing/extra/wrong-adapter/wrong-case/empty-provenance corpus |
| P2-J03 | Exact three-field provenance is at most 8 KiB and is included inside—not added to—the 16 KiB package | Independent raw/canonical byte measurement and double-count guard |

Additional required evidence introduced by ADR 0010:

- the declared fixture case allowlist is exact and unknown cases fail before canonical mutation;
- `adapter_type`, `adapter_version`, and `adapter_instance_id` are exact protected values;
- external provenance carries no authority, command, cost, budget, permission, evaluator, path, URL, code, credential, tool, free text, human identity, model identity, or opaque payload;
- current-state projection is built from current canonical rows under the disposition lock, not copied from fixture output or the stale request observation;
- request context cannot be added by fixture configuration, dispatch, ingress, or a future caregiver payload;
- all original 152 Phase 1 tests remain unchanged and passing.
