# Slice 38c: Dispatch, Response, and External Package Protocol Graph

Status: implementation-complete on PR #95; final documentation CI and merge pending.

## Scope

This sub-slice implements the pure protected protocol layer enabled by ADR 0010. It does not write SQLite, admit dispatch work, invoke the fixture, perform ingress, terminalize, dispose, execute an action, or add any live caregiver capability.

Protected evidence closes:

- P2-H04: exact dispatch identity, `dispatch-id` preimage, dispatch ID, and final dispatch envelope including `configuration_version`;
- P2-H07: response ID uses already-derived proposal IDs/content digests without a cycle;
- P2-H08: response ID is inserted into final proposal linkage before package digest;
- P2-H09: package preimage has exactly `response` and `proposals` with exact status cardinality;
- the pure protocol portion of P2-H11: two independent builds produce byte-identical final package bytes;
- P2-I01: exact response identity/envelope, protected adapter values, status/cardinality, and exact three-field provenance;
- P2-I10: external package has no writer authority or authoritative command field;
- response/package side of P2-I11: extra fields, free text, wrong adapter/case/linkage, authority spoofing, and malformed cardinality reject.

## Dispatch identity

`phase2_dispatch.py` validates the exact ADR 0010 identity fields:

- dispatch schema and protocol version;
- organism/current lineage;
- linked request ID;
- ordinal `1`;
- consultation configuration version;
- adapter version;
- declared fixture case ID;
- work class.

The final envelope adds only:

- derived dispatch ID;
- later event sequence;
- exact administration authority `administration:consultation.dispatch`.

The fixture case must belong to the ADR 0010 protected allowlist. Unknown cases fail before later canonical use.

## Response and package graph

`phase2_response.py` derives in this order:

1. validate request and dispatch;
2. validate proposal identity and derive proposal content digest/ID;
3. construct exact response identity using the already-derived proposal links;
4. derive response ID;
5. insert response ID into final proposal linkage;
6. construct final response envelope;
7. build package preimage exactly `{"response":...,"proposals":[...]}`;
8. derive `external-package` digest.

`proposals_returned` has exactly one proposal. `unavailable` has none.

External provenance contains exactly:

```json
{"fixture_case_id":"<linked case>","provenance_schema":"sudachi.consultation.provenance/v1","source_type":"deterministic-fixture"}
```

It is bounded inside the package and cannot carry authority, cost, budget, permission, evaluator command, execution command, checkpoint, migration, rollback, code, SQL, shell, path, URL, credential, tool, free text, human identity, model identity, or opaque payload.

## Test-first evidence

Tests-only head `cd37b36cfa7e0c4d0e0996017211c063ae0e8995`, GitHub Actions run 556:

- dependency installation and compilation passed;
- protected enforcement failed because `phase2_dispatch` and `phase2_response` did not exist.

Implementation head `cd1e2f176fffb3e481f5d07f4d4bfdacb4373110`, run 558:

- 294 passed in 36.26 seconds;
- dependency installation succeeded;
- source/test compilation succeeded;
- schema-v1 genesis CLI smoke succeeded.

All original 152 Phase 1 tests remain unchanged and included.

## Remaining boundary

- P2-E10 real largest structural request/checkpoint evidence remains separate;
- Slice 39 must connect dispatch identity to a fresh fail-fast administrative transaction, conservative charge, and post-commit fixture boundary;
- Slice 40 must independently parse and validate raw package bytes before canonical ingress;
- Slice 41 must use ADR 0010 current-state projection for disposition.

No Codex audit was used. Codex remains deferred until the complete Phase 2 implementation candidate is ready for the single implementation-completion audit.
