# ADR 0012 Test Matrix Amendment

Status: accepted design amendment; implementation evidence pending Slice 40.

This file amends the Phase 2 consultation test matrix only where ADR 0012 is explicit. Existing requirements remain in force.

## Canonical identifiers

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-J16 | Receipt ID is exactly `consultation-ingress-receipt:` plus the validated external-package digest | Golden vector and forged-prefix corpus |
| P2-J17 | Completion ID is exactly `consultation-cost-completion:` plus the linked dispatch digest | Golden vector and linkage corpus |
| P2-K10 | Terminal ID is exactly `consultation-dispatch-terminal:` plus the linked dispatch digest | Golden vector and linkage corpus |

## Successful ingress evidence

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-J18 | Success event type/source are exactly `consultation_response_ingressed` and `administration:consultation.response_ingress` | Exact event assertion and spoof rejection |
| P2-J19 | One event sequence is shared by event, response row, receipt row, and receipt envelope; proposal has no separate event | Row/event joins and event-count assertion |
| P2-J20 | Success event payload has exactly `completion` and `receipt` | Golden payload and extra/missing-field corpus |
| P2-J21 | Receipt envelope has the exact ADR 0012 field set, authority, schema, protocol, linkage, sizes, and two sorted direct parents | Golden envelope and forgery corpus |
| P2-J22 | Success completion has exactly completion ID, dispatch ID, response ID, and measured package bytes | Golden object and row/payload equality |
| P2-J23 | Raw bytes equal independently reconstructed canonical package bytes and measured bytes equal both lengths | Raw/canonical boundary and noncanonical JSON corpus |
| P2-J24 | `unavailable` commits the same receipt/completion/event branch with no proposal and is final | Exact zero-cardinality state |

## Rejected raw bytes and terminal evidence

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-K11 | Rejected package digest is SHA-256 of the exact ADR 0012 domain prefix followed directly by raw bytes | Golden vectors including non-UTF-8 and malformed JSON |
| P2-K12 | Terminal event type/source are exactly `consultation_dispatch_terminalized` and `administration:consultation.dispatch_terminal` | Exact event assertion and spoof rejection |
| P2-K13 | One event sequence is shared by terminal event, terminal row, and terminal envelope | Row/event joins |
| P2-K14 | Terminal event payload has exactly `completion` and `terminal` | Golden payload and extra/missing-field corpus |
| P2-K15 | Terminal envelope has the exact ADR 0012 field set, authority, schema, protocol, linkage, lineage, reason, nullable fields, and two sorted direct parents | Golden envelope and forgery corpus |
| P2-K16 | `dispatch_interrupted` has no package bytes, null rejected fields, and measured completion zero | Reconciliation and repeated-idempotence evidence |
| P2-K17 | `fixture_output_invalid` requires raw bytes and stores exact raw digest/size with equal completion bytes | Malformed/adversarial package corpus |
| P2-K18 | `expired_before_ingress` requires attempted raw bytes and stores exact raw digest/size with equal completion bytes | Exact lifecycle crossing |
| P2-K19 | Terminal completion has exactly completion ID, dispatch ID, terminal ID, and measured package bytes | Golden object and row/payload equality |

## Atomicity, idempotence, and authority

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-J25 | Response, optional proposal, receipt, completion, and one event commit atomically | Fault injection after every write and before commit |
| P2-J26 | Byte-identical duplicate success adds no event, clock read, charge, completion, or logical bytes | Exact before/after state |
| P2-J27 | Conflicting duplicate bytes fail closed | Same dispatch, altered raw bytes |
| P2-K20 | Terminal row, completion, and one event commit atomically | Fault injection after every write and before commit |
| P2-K21 | Repeated byte-identical terminalization is idempotent; conflicting reason or bytes fail closed | Exact state and conflict corpus |
| P2-K22 | Reconciliation creates only `dispatch_interrupted` and never invokes the fixture | Guarded fixture count |
| P2-N09 | Success receipt and terminal envelopes use only the exact administration sources and preserve untrusted fixture provenance separately | Authority-spoof corpus and event export |
| P2-N10 | Direct parents are exactly the request-creation and dispatch-admission events, sorted, unique, preceding, and current-lineage | Corrupt, future, duplicate, and old-lineage corpus |

## Non-authorized effects

Slice 40 evidence must also prove that ingress, terminalization, duplicates, busy rejection, and reconciliation do not:

- invoke the fixture;
- checkpoint or increment lifecycle;
- claim garden input or execute an action;
- clear maintenance;
- create memory or skills;
- alter authority, budgets, permissions, configuration, migration, or rollback state;
- retry or refund charged work.

All original 152 Phase 1 tests remain unchanged and required.
