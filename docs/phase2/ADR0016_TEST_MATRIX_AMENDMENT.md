# ADR 0016 Phase 2 Test-Matrix Amendment

Status: **Accepted with ADR 0016 on 2026-07-27**

This document synchronizes the protected Phase 2 evidence map with ADR 0016. It replaces only P2-J09's unreachable canonical-at-limit scenario while retaining the exact 64 KiB arithmetic boundary and one-over rejection.

| ID | Accepted protected requirement | Required evidence |
| --- | --- | --- |
| P2-J09 | The exact pure lineage-payload accounting function admits 65536 and rejects 65537. A separate legitimate four-cycle closed Protocol-v1 fixture measures the exact reachable maximum below 65536 and proves runtime linkage to independently measured request and successful-package bytes without double counting or fake canonical payload | Pure table-driven integer boundary/type corpus; legitimate maximum-ID four-cycle request/ingress/disposition fixture; independent SQL/byte reconstruction; fifth-limit guard; physical limits/reserve; no direct consultation mutation |
| P2-J10 | Accepted rollback starts a fresh zero-byte current-lineage accounting epoch; old-lineage request/receipt bytes remain historical and excluded | Pre/post rollback legitimate cycles plus pure/runtime accounting comparison and stale package rejection |
| P2-M07 | Four requests, charges, and the measured legal payload maximum apply per current lineage while the independent hard guard remains 64 KiB | Legitimate four-cycle count and byte reconstruction plus pure 65536/65537 guard |
| P2-M09 | New lineage begins fresh four-call and zero-byte logical-payload epochs | Post-rollback ordinal-one cycle and independent current-lineage sums |

Additional protected evidence:

- the pure function rejects bool, negative, float, string, null, and unsupported-unit inputs;
- ingress uses the same pure function after independently summing stored current-lineage request sizes and successful receipt bytes;
- the largest package case is selected by measuring all declared legal fixture cases for one legal request shape, not by padding;
- response/proposal/provenance and all metadata remain excluded from logical double counting;
- invalid and terminal raw bytes remain excluded from logical payload;
- no 65537-byte canonical epoch is manufactured;
- all original 152 Phase 1 tests remain unchanged and passing.