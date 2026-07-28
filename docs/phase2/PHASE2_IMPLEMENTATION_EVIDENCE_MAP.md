# Phase 2 Implementation Evidence Map

Status: **Finding 4 repair candidate; final focused closure audit pending**.

This document maps the final accepted Phase 2 Consultation Boundary evidence set to the exact protected tests and durable implementation notes present after Slice 42b. It is an audit input, not an audit conclusion and not a Phase 2 freeze decision.

## Exact candidate boundary

- merged implementation baseline: PR #116 merge `0059e0e20ececcf9e16a9b1a4376c3564cf9c391`;
- final implementation head: `7f9b718f8b65f71e411a5ed632257ed5609d3ede`;
- implementation CI: run 614, `365 passed in 46.13s`, plus install, compile, protected enforcement, and schema-v1 CLI smoke;
- Slice 42b closeout baseline: `e466d93c57d837f4fbfdeac63ff97806431e270f`;
- closeout CI: run 616, `365 passed in 48.09s`, plus install, compile, protected tests, and schema-v1 CLI smoke;
- original Phase 1 audit baseline: `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`.

The GitHub compare from the Phase 1 audit baseline to the Slice 42b closeout adds Phase 2 tests and one Phase 1 compatibility regression but does not modify or delete an original Phase 1 test file. The original 152-test control remains included in every cited green run.

## Normative row set and precedence

The final accepted evidence set contains **213 identifiers**:

- the 186 rows in `docs/PHASE2_CONSULTATION_TEST_MATRIX.md`;
- ADR 0012 additions P2-J16–P2-J27, P2-K10–P2-K22, and P2-N09–P2-N10;
- ADR 0010 replacements for P2-D11, P2-E10, P2-H04, P2-H07–P2-H10, P2-I01, and P2-J03;
- ADR 0011 exact dispatch admission/charge/event evidence for P2-F03 and P2-F05;
- ADR 0013 replacements for P2-H10, P2-L01–P2-L14, P2-M01, P2-N08, and P2-O03;
- ADR 0014's final eight-parent replacement for P2-E10, superseding ADR 0010's earlier example;
- ADR 0015's exact typed fifth-request replacement for P2-D07;
- ADR 0016's final P2-J09 evidence and its accepted P2-J10/P2-M07/P2-M09 epoch clarifications.

Unlisted base-matrix rows remain in force. A later amendment is authoritative only for the identifiers it names.

## Evidence bundle legend

| Code | Evidence | Durable ownership |
| --- | --- | --- |
| `P1` | the original 152 Phase 1 tests; `tests/test_phase1_budget_compatibility.py` | Phase 1 audit commit `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`; GitHub compare to closeout `e466d93c57d837f4fbfdeac63ff97806431e270f`; run 616 |
| `GEN` | `tests/test_phase2_genesis.py`; `tests/test_phase2_schema_profile.py` | PR #65; `docs/phase2/SLICE36A_SCHEMA_V2_GENESIS.md` |
| `PROJ-CORE` | `tests/test_phase2_projection_core.py` | PR #66; `docs/phase2/SLICE36B1_ZERO_CAREGIVER_CHECKPOINT_CORE.md` |
| `PROJ-REPAIR` | `tests/test_phase2_projection_repair.py` | PR #67; `docs/phase2/SLICE36B2A1_PENDING_REPAIR_EVIDENCE.md` |
| `PROJ-RET` | `tests/test_phase2_projection_retention.py`; `tests/test_phase2_projection_retention_corruption.py` | PR #69; `docs/phase2/SLICE36B2A2_RETENTION_PROJECTION.md` |
| `PROJ-RB` | `tests/test_phase2_projection_rollback.py`; `tests/test_phase2_projection_rollback_lineage_collision.py` | PR #70; `docs/phase2/SLICE36B2A3_ROLLBACK_PROJECTION.md` |
| `PROJ-EXPORT` | `tests/test_phase2_projection_event_export.py`; `tests/test_phase2_projection_event_export_corruption.py` | PR #71; `docs/phase2/SLICE36B2A4_EVENT_EXPORT_PROJECTION.md` |
| `PHYS-PAIR` | `tests/test_phase2_physical_overhead.py`; `tests/test_phase2_physical_overhead_active_cap.py` | PR #72; `docs/phase2/SLICE36B2A5_PHYSICAL_OVERHEAD.md` |
| `PHYS-ABS` | `tests/test_phase2_absolute_active_and_repair_limits.py`; `tests/test_phase2_absolute_candidate_working_set.py`; `tests/test_phase2_absolute_checkpoint_and_repair_working_set.py`; `tests/test_phase2_absolute_idempotent_working_set.py`; `tests/test_phase2_absolute_repair_active_limit.py`; `tests/test_phase2_absolute_retention_admission.py`; `tests/test_phase2_absolute_rollback_archive_working_set.py`; `tests/test_phase2_absolute_rollback_replace_complete.py`; `tests/test_phase2_absolute_store_and_raw_artifacts.py`; `tests/test_phase2_checkpoint_artifact_exact_limit.py` | PR #73; `docs/phase2/SLICE36B2A6_ABSOLUTE_PHYSICAL_LIMITS.md` |
| `REQ-CORE` | `tests/test_phase2_request_wake_core.py` | PR #81; `docs/phase2/SLICE37A1_REQUEST_WAKE_CORE.md` |
| `REQ-STORAGE` | `tests/test_phase2_request_storage_core_failure.py`; `tests/test_phase2_request_storage_real_boundaries.py`; `tests/test_phase2_request_storage_refusal.py`; `tests/test_phase2_request_storage_success.py` | PR #83; `docs/phase2/SLICE37A2_REQUEST_STORAGE_SAFETY.md` |
| `REQ-TIME` | `tests/test_phase2_request_time_and_concurrency.py` | PR #85; `docs/phase2/SLICE37A3_REQUEST_TIME_CONCURRENCY.md` |
| `PROTO-REQ` | `tests/test_phase2_protocol_digest_request_schema.py` | PR #87; `docs/phase2/SLICE38A_CANONICAL_DIGEST_REQUEST_SCHEMA.md` |
| `PROPOSAL` | `tests/test_phase2_proposal_schema.py` | PR #91; `docs/phase2/SLICE38B_PROPOSAL_SCHEMA.md` |
| `PROTO-GRAPH` | `tests/test_phase2_dispatch_response_package.py` | PR #95; `docs/phase2/SLICE38C_DISPATCH_RESPONSE_PACKAGE.md` |
| `DISPATCH` | `tests/test_phase2_dispatch_admission_fixture.py`; `tests/test_phase2_dispatch_admission_matrix.py` | PR #99; `docs/phase2/SLICE39A_DISPATCH_ADMISSION_FIXTURE.md` |
| `INGRESS` | `tests/test_phase2_ingress_terminalization.py`; `tests/test_phase2_ingress_terminalization_boundaries.py` | PR #103; `docs/phase2/SLICE40_INGRESS_TERMINALIZATION.md` |
| `DISPOSITION` | `tests/test_phase2_disposition_wake.py`; `tests/test_phase2_disposition_wake_boundaries.py` | PR #107; `docs/phase2/SLICE41_DISPOSITION_WAKE.md` |
| `FINITE` | `tests/test_phase2_finite_cycle_boundaries.py` | PR #114; `docs/phase2/SLICE42A_FINITE_CYCLE_BOUNDARIES.md` |
| `ROLLBACK` | `tests/test_phase2_rollback_lineage_boundaries.py`; `tests/test_rollback_retention_reconciliation.py` | PR #116; `docs/phase2/SLICE42B_ROLLBACK_LINEAGE.md` |
| `ABSENCE` | `tests/test_phase2_explicit_absence.py` | audit-preparation branch; package AST/import, CLI, schema/status/configuration, and selector/executor isolation |
| `REPAIR-F4` | `tests/test_phase2_implementation_audit_repairs.py` | Issue #123; exact manifest fields, active-organism binding, request-row/event snapshot equality, and coherent adversarial substitutions |

## Row-by-row mapping

Every status below means **mapped to protected evidence; final focused closure audit pending**. It does not mean the remaining Finding 4 closure has been independently accepted or that Phase 2 is frozen.

### A. Frozen Phase 1 baseline

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-A01 | All 152 Phase 1 tests remain byte-unchanged and pass on schema-v1. | `P1` | Mapped; audit pending |
| P2-A02 | Schema-v1 initialization, CLI, checkpoints, rollback, authority, and budgets remain supported. | `P1`, `GEN`, `PROJ-RB` | Mapped; audit pending |
| P2-A03 | Phase 2 adds no network, subprocess, arbitrary-code, or workspace route to Phase 1 action execution. | `P1`, `ABSENCE`, `DISPOSITION` | Mapped; audit pending |
| P2-A04 | The base contract remains 0.2 and schema-v2 is an explicit extension. | `GEN`, `P1` | Mapped; audit pending |
| P2-A05 | Existing Phase 1 tables receive no new columns. | `GEN`, `P1` | Mapped; audit pending |

### B. Schema-v2 initialization and validation

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-B01 | Schema-v2 preserves the original phase1-v1 budget singleton and every original budget-version location. | `GEN` | Mapped; audit pending |
| P2-B02 | Exactly one immutable accepted consultation-configuration singleton exists with protocol 1. | `GEN` | Mapped; audit pending |
| P2-B03 | Original actions, evaluators, seed state, clocks, Phase 1 budgets, and authority mappings remain exact. | `GEN` | Mapped; audit pending |
| P2-B04 | Consultation tables, indexes, keys, triggers, configuration objects, and immutable constraints are exact. | `GEN` | Mapped; audit pending |
| P2-B05 | Operational consultation tables and their SQLite sequences are empty at genesis. | `GEN` | Mapped; audit pending |
| P2-B06 | Schema-v2 genesis is checkpoint-stable before it is wakeable. | `GEN` | Mapped; audit pending |
| P2-B07 | Schema-v1 is never automatically migrated or downgraded. | `GEN` | Mapped; audit pending |
| P2-B08 | No migration or downgrade command exists. | `GEN` | Mapped; audit pending |
| P2-B09 | Unknown, missing, duplicate, mixed, noncanonical, or contradictory configuration fails before mutation. | `GEN` | Mapped; audit pending |
| P2-B10 | Configuration version appears in every configuration-dependent consultation identity/row/event and never in Phase 1 budget fields. | `GEN`, `PROTO-REQ`, `PROTO-GRAPH`, `DISPATCH`, `INGRESS`, `DISPOSITION` | Mapped; audit pending |
| P2-B11 | The protected configuration singleton is immutable and has exact cardinality one in active and checkpoint databases. | `GEN` | Mapped; audit pending |
| P2-B12 | The schema-v2 protected-object fingerprint includes empty consultation objects without changing Phase 1 columns. | `GEN` | Mapped; audit pending |

### C. Zero-caregiver semantic artifact control

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-C01 | Paired schema-v1/schema-v2-zero scenarios use identical declared inputs, clocks, reasons, boundaries, faults, and operation order. | `PROJ-CORE` | Mapped; audit pending |
| P2-C02 | Only the exact ADR 0009 schema-version locations receive the semantic sentinel; budget versions are never normalized. | `PROJ-CORE` | Mapped; audit pending |
| P2-C03 | Checkpoint, repair, retention, rollback, and export identities are projected only at exact declared paths. | `PROJ-CORE`, `PROJ-REPAIR`, `PROJ-RET`, `PROJ-RB`, `PROJ-EXPORT` | Mapped; audit pending |
| P2-C04 | Every unlisted row, column, event, authority, parent, key, value, manifest field, and boundary remains exact. | `PROJ-CORE` | Mapped; audit pending |
| P2-C05 | Extra, missing, moved, wrongly nested, or wrongly positioned values are not hidden by projection. | `PROJ-CORE` | Mapped; audit pending |
| P2-C06 | All operational consultation tables are empty with no sequence entry. | `GEN`, `PROJ-CORE`, `ABSENCE` | Mapped; audit pending |
| P2-C07 | Zero-caregiver creates no consultation event, source, charge, fixture call, terminal, disposition, or effect. | `GEN`, `PROJ-CORE`, `ABSENCE` | Mapped; audit pending |
| P2-C08 | Paired admitted operations preserve behavior, lifecycle, failure streak, maintenance, event order, checkpoints, rollback, lineage, and authority. | `PROJ-CORE`, `PROJ-REPAIR`, `PROJ-RET`, `PROJ-RB` | Mapped; audit pending |
| P2-C09 | Raw bytes and byte-derived identities are independently validated and are not claimed equal across schemas. | `PROJ-CORE` | Mapped; audit pending |
| P2-C10 | Genesis, ordinary, and maintenance checkpoint events map to exact CP(g,e) boundaries. | `PROJ-CORE`, `PROJ-RET` | Mapped; audit pending |
| P2-C11 | Checkpoint-registration repair maps exact current/previous identities and independently validates SHA, size, and store bytes. | `PROJ-REPAIR` | Mapped; audit pending |
| P2-C12 | Retention prune, failure, staging, interruption, reconciliation, and retry map to exact typed evidence. | `PROJ-RET` | Mapped; audit pending |
| P2-C13 | Rollback archive, source candidate, transformed candidate, completion, and checkpoint identities map to exact RA/RC/TC/CP tokens. | `PROJ-RB` | Mapped; audit pending |
| P2-C14 | Every omitted digest, size, aggregate byte count, and directory name is recomputed and bijectively linked first. | `PROJ-CORE`, `PROJ-REPAIR`, `PROJ-RET`, `PROJ-RB`, `PROJ-EXPORT` | Mapped; audit pending |
| P2-C15 | Projection uses closed typed locations and no wildcard, recursive key walk, regex, or global key normalization. | `PROJ-CORE`, `PROJ-RET` | Mapped; audit pending |
| P2-C16 | Event export independently validates raw bytes, digest, count, order, and source checkpoint before semantic comparison. | `PROJ-EXPORT` | Mapped; audit pending |
| P2-C17 | Only noncanonical wrappers and paths are excluded; canonical state and events remain exact. | `PROJ-EXPORT` | Mapped; audit pending |
| P2-C18 | A value permitted at one exact location is rejected at unrelated locations. | `PROJ-CORE` | Mapped; audit pending |

### D. Garden request wake and failure honesty

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-D01 | A request is considered only after incomplete-objective no_applicable_action. | `REQ-CORE` | Mapped; audit pending |
| P2-D02 | The Phase 1 tick, abstention/action, mutation, outcome, and failure behavior remains exact. | `REQ-CORE` | Mapped; audit pending |
| P2-D03 | consecutive_failures increments exactly once and consultation never resets it. | `REQ-CORE` | Mapped; audit pending |
| P2-D04 | A maintenance-entering wake creates no request. | `REQ-CORE` | Mapped; audit pending |
| P2-D05 | An eligible wake creates at most one request and the exact bounded additional records. | `REQ-CORE` | Mapped; audit pending |
| P2-D06 | At most one current-lineage request is outstanding. | `REQ-CORE` | Mapped; audit pending |
| P2-D07 | Four requests are allowed; an otherwise eligible fifth returns the exact typed noncanonical refusal and creates no fifth consultation mutation. | `FINITE` | Mapped; audit pending |
| P2-D08 | Request ordinal is the current-lineage count plus one, including a fresh ordinal one after rollback. | `FINITE`, `ROLLBACK` | Mapped; audit pending |
| P2-D09 | Request identity, preimage, digest, ID, final envelope, bytes, and event linkage are deterministic. | `REQ-CORE` | Mapped; audit pending |
| P2-D10 | Request ID excludes the later request event sequence and all undeclared fields. | `REQ-CORE` | Mapped; audit pending |
| P2-D11 | Protocol-v1 request has the exact closed field set, no context/padding/free text, and no authority spoofing. | `PROTO-REQ`, `FINITE` | Mapped; audit pending |
| P2-D12 | Request row and event are atomic; extension-only faults leave no partial request. | `REQ-STORAGE`, `PROTO-REQ` | Mapped; audit pending |
| P2-D13 | A created request is checkpoint-stable before dispatch. | `REQ-CORE` | Mapped; audit pending |
| P2-D14 | Request eligibility and expiry are lifecycle-based and independent of wall-time direction. | `REQ-TIME` | Mapped; audit pending |
| P2-D15 | Nested and competing garden wakes fail fast without queueing or request mutation. | `REQ-TIME` | Mapped; audit pending |
| P2-D16 | A later caller-selected garden wake remains allowed while a request is outstanding. | `REQ-CORE` | Mapped; audit pending |

### E. Request-extension storage boundary

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-E01 | Request metadata is an optional savepoint extension; the frozen Phase 1 core can commit without it. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E02 | Pre-write accounting includes active DB, sidecars, request extension, resulting checkpoint, store, working set, and reserve. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E03 | Pre-write refusal creates no consultation row, event, source, or partial cost. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E04 | Post-write storage refusal rolls back only the request extension savepoint. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E05 | Extension refusal still commits the exact Phase 1 outcome and ordinary checkpoint. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E06 | Storage refusal returns the exact noncanonical storage-budget reason. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E07 | A real reserve boundary refuses only the extension and leaves a subsequent wake possible. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E08 | Real WAL/SHM, checkpoint staging/store, and working-set bytes are included. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E09 | If the frozen Phase 1 core cannot fit, its original failure behavior remains unchanged. | `REQ-STORAGE` | Mapped; audit pending |
| P2-E10 | The legitimate ordinal-four largest structural request uses the maximum legal ID, all declared arrays, exactly eight eligible parents, and preserves all physical limits/reserve without filler. | `FINITE` | Mapped; audit pending |

### F. Dispatch admission and conservative charging

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-F01 | Dispatch uses one fresh fail-fast administrative transaction. | `DISPATCH` | Mapped; audit pending |
| P2-F02 | Sleeping, stable checkpoint/artifact, current lineage, expiry, no prior dispatch, and no terminal/response are required. | `DISPATCH` | Mapped; audit pending |
| P2-F03 | Final dispatch row, conservative charge row, and one admission event commit atomically. | `DISPATCH` | Mapped; audit pending |
| P2-F04 | Fixture execution never occurs before dispatch admission commits and releases the lock. | `DISPATCH` | Mapped; audit pending |
| P2-F05 | The exact conservative ledger records one attempt, invocation, work unit, measured request bytes, and zero forbidden resources. | `DISPATCH` | Mapped; audit pending |
| P2-F06 | A spawned interruption after admission retains exactly one charge and unresolved dispatch. | `DISPATCH`, `INGRESS` | Mapped; audit pending |
| P2-F07 | Repeated admission never authorizes another fixture call or charge. | `DISPATCH` | Mapped; audit pending |
| P2-F08 | Four charges are allowed per current lineage; no fifth or ninth physical-organism invocation occurs. | `FINITE`, `ROLLBACK` | Mapped; audit pending |
| P2-F09 | Dispatch physical checks preserve the 1 MiB reserve and inherited limits. | `DISPATCH`, `PHYS-ABS` | Mapped; audit pending |
| P2-F10 | Dispatch creates no checkpoint, lifecycle increment, action, garden effect, response, terminal, or disposition. | `DISPATCH` | Mapped; audit pending |

### G. External deterministic fixture boundary

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-G01 | No SQLite write lock is held during fixture execution. | `DISPATCH` | Mapped; audit pending |
| P2-G02 | Fixture receives exactly the final request envelope and declared case ID. | `DISPATCH` | Mapped; audit pending |
| P2-G03 | Fixture receives no DB, path, workspace, repository, executor, evaluator, checkpoint, rollback, network, subprocess, credential, tool, or randomness capability. | `DISPATCH` | Mapped; audit pending |
| P2-G04 | Identical request and case produce byte-identical output. | `DISPATCH` | Mapped; audit pending |
| P2-G05 | Deterministic purity cannot bypass the one charged invocation. | `DISPATCH` | Mapped; audit pending |
| P2-G06 | Fixture output remains noncanonical before explicit ingress. | `DISPATCH`, `INGRESS` | Mapped; audit pending |
| P2-G07 | Human, model, money, and declared latency costs remain zero. | `DISPATCH` | Mapped; audit pending |

### H. Digest preimages and canonical graph

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-H01 | H(label,value) uses the exact domain prefix, separators, label, canonical bytes, and SHA-256. | `PROTO-REQ` | Mapped; audit pending |
| P2-H02 | Alternate separators, whitespace/pretty JSON, unsupported values, labels, or Unicode normalization reject. | `PROTO-REQ` | Mapped; audit pending |
| P2-H03 | Request identity contains exactly its declared fields. | `PROTO-REQ` | Mapped; audit pending |
| P2-H04 | Dispatch identity contains exactly ADR 0010 fields including configuration_version and excludes later/cost/authority/output fields. | `PROTO-GRAPH` | Mapped; audit pending |
| P2-H05 | Proposal content digest and proposal ID share the exact proposal-content preimage. | `PROPOSAL` | Mapped; audit pending |
| P2-H06 | Proposal identity excludes response ID and therefore has no digest cycle. | `PROPOSAL` | Mapped; audit pending |
| P2-H07 | Response ID uses already-derived proposal IDs/content digests with exact status/cardinality. | `PROTO-GRAPH` | Mapped; audit pending |
| P2-H08 | Derived response ID is inserted into final proposal linkage before package digest. | `PROTO-GRAPH` | Mapped; audit pending |
| P2-H09 | Package preimage contains exactly response and proposals with status-controlled cardinality. | `PROTO-GRAPH` | Mapped; audit pending |
| P2-H10 | Current-state and disposition identities use ADR 0010/0013 exact fields; final envelope adds exact authority, full state, ID, sequence, and three parents. | `DISPOSITION` | Mapped; audit pending |
| P2-H11 | The complete declared protocol graph is reproducible in independent builds. | `PROTO-GRAPH`, `DISPOSITION` | Mapped; audit pending |

### I. Exact response and proposal schemas

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-I01 | Response identity/envelope and exact three-field provenance use closed fields, protected adapter values, exact status/cardinality, and linked fixture case. | `PROTO-GRAPH` | Mapped; audit pending |
| P2-I02 | Proposal common field set is exact. | `PROPOSAL` | Mapped; audit pending |
| P2-I03 | Proposal expiry equals the linked request expiry exactly. | `PROPOSAL` | Mapped; audit pending |
| P2-I04 | Confidence basis exactly links the deterministic fixture case. | `PROPOSAL` | Mapped; audit pending |
| P2-I05 | Required evaluator IDs equal the protected type-specific set. | `PROPOSAL` | Mapped; audit pending |
| P2-I06 | action_candidate subject, parameters, rationale, action allowlist, and registered schema are exact. | `PROPOSAL` | Mapped; audit pending |
| P2-I07 | abstain has the exact objective subject and no_supported_action value/rationale. | `PROPOSAL` | Mapped; audit pending |
| P2-I08 | defer has the exact objective subject and await_state_change value/rationale. | `PROPOSAL` | Mapped; audit pending |
| P2-I09 | defer contains no schedule, retry, wake, command, or effect. | `PROPOSAL` | Mapped; audit pending |
| P2-I10 | External package contains no writer authority or authoritative cost/budget/permission/evaluator/execution command. | `PROTO-GRAPH`, `INGRESS` | Mapped; audit pending |
| P2-I11 | Free text, code, SQL, shell, path, URL, credential, tool, unknown action, and undeclared fields reject. | `PROTO-REQ`, `PROPOSAL`, `PROTO-GRAPH`, `INGRESS` | Mapped; audit pending |

### J. Logical payload and successful ingress

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-J01 | Final request envelope is bounded by 16 KiB. | `PROTO-REQ`, `INGRESS` | Mapped; audit pending |
| P2-J02 | Complete external package is bounded by 16 KiB before parse and after canonical reconstruction. | `PROTO-GRAPH`, `INGRESS` | Mapped; audit pending |
| P2-J03 | Exact three-field provenance is bounded by 8 KiB inside—not in addition to—the package limit. | `PROTO-GRAPH`, `INGRESS`, `FINITE` | Mapped; audit pending |
| P2-J04 | Logical payload equals current-lineage request bytes plus successful-ingress package bytes. | `INGRESS`, `FINITE` | Mapped; audit pending |
| P2-J05 | Response, proposal, provenance, receipt, completion, event, and other metadata are not double counted. | `INGRESS`, `FINITE` | Mapped; audit pending |
| P2-J06 | Duplicate successful ingress adds zero logical bytes. | `INGRESS`, `FINITE` | Mapped; audit pending |
| P2-J07 | Metadata is excluded logically but included physically. | `INGRESS`, `FINITE` | Mapped; audit pending |
| P2-J08 | Invalid/terminal raw bytes add no logical payload but their bounded digest/size evidence counts physically. | `INGRESS`, `FINITE` | Mapped; audit pending |
| P2-J09 | Pure accounting admits 65536 and rejects 65537; the legitimate four-cycle reachable maximum is independently measured below the guard. | `FINITE` | Mapped; audit pending |
| P2-J10 | Accepted rollback starts a fresh zero-byte current-lineage payload epoch while old bytes remain historical. | `ROLLBACK` | Mapped; audit pending |
| P2-J11 | Ingress recomputes every identity, digest, size, linkage, expiry, provenance, and proposal schema. | `INGRESS` | Mapped; audit pending |
| P2-J12 | Response, optional proposal, receipt, completion, and event commit atomically. | `INGRESS` | Mapped; audit pending |
| P2-J13 | Byte-identical duplicate success is idempotent with no event, clock, charge, or payload increment. | `INGRESS` | Mapped; audit pending |
| P2-J14 | Busy/pending refusal permits explicit same-byte resubmission without fixture recall or new charge. | `INGRESS` | Mapped; audit pending |
| P2-J15 | Ingress cannot execute an action, clear maintenance, checkpoint, migrate, roll back, or change authority. | `INGRESS`, `ABSENCE` | Mapped; audit pending |
| P2-J16 | Receipt ID is exactly consultation-ingress-receipt:<external-package digest>. | `INGRESS` | Mapped; audit pending |
| P2-J17 | Completion ID is exactly consultation-cost-completion:<dispatch digest>. | `INGRESS` | Mapped; audit pending |
| P2-J18 | Success event type/source are exactly consultation_response_ingressed and administration:consultation.response_ingress. | `INGRESS` | Mapped; audit pending |
| P2-J19 | Event, response, receipt row, and receipt envelope share one sequence; proposal has no separate event. | `INGRESS` | Mapped; audit pending |
| P2-J20 | Success event payload contains exactly completion and receipt. | `INGRESS` | Mapped; audit pending |
| P2-J21 | Receipt envelope has the exact ADR 0012 field set, authority, linkage, sizes, and two sorted direct parents. | `INGRESS` | Mapped; audit pending |
| P2-J22 | Successful completion contains exactly completion ID, dispatch ID, response ID, and measured package bytes. | `INGRESS` | Mapped; audit pending |
| P2-J23 | Supplied raw bytes equal independently reconstructed canonical package bytes and both measured lengths. | `INGRESS` | Mapped; audit pending |
| P2-J24 | unavailable commits the same receipt/completion/event branch with zero proposals and is final. | `INGRESS` | Mapped; audit pending |
| P2-J25 | Success writes are atomic at every write boundary and immediately before commit. | `INGRESS` | Mapped; audit pending |
| P2-J26 | Byte-identical duplicate success adds no event, clock read, charge, completion, or logical bytes. | `INGRESS` | Mapped; audit pending |
| P2-J27 | Conflicting duplicate bytes fail closed. | `INGRESS` | Mapped; audit pending |

### K. Dispatch terminalization and reconciliation

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-K01 | Fixture exception produces one explicit terminal outcome and no automatic retry. | `INGRESS` | Mapped; audit pending |
| P2-K02 | Invalid package is rejected before mutation and then explicitly terminalized. | `INGRESS` | Mapped; audit pending |
| P2-K03 | Expiry after admission produces expired_before_ingress with measured attempted bytes. | `INGRESS` | Mapped; audit pending |
| P2-K04 | Spawned crash after admission leaves one charged unresolved dispatch. | `INGRESS` | Mapped; audit pending |
| P2-K05 | Explicit reconciliation records interruption without fixture invocation. | `INGRESS` | Mapped; audit pending |
| P2-K06 | Terminalization is fail-fast, idempotent, and mutually exclusive with response. | `INGRESS` | Mapped; audit pending |
| P2-K07 | Terminal evidence stores only bounded digest, size, reason, linkage, completion, and event data. | `INGRESS` | Mapped; audit pending |
| P2-K08 | Current lineage and exact durable request/dispatch state are required. | `INGRESS`, `ROLLBACK` | Mapped; audit pending |
| P2-K09 | Terminalization preserves reserve/physical limits and creates no checkpoint. | `INGRESS`, `PHYS-ABS` | Mapped; audit pending |
| P2-K10 | Terminal ID is exactly consultation-dispatch-terminal:<dispatch digest>. | `INGRESS` | Mapped; audit pending |
| P2-K11 | Rejected-package digest uses the exact ADR 0012 domain prefix followed by raw bytes. | `INGRESS` | Mapped; audit pending |
| P2-K12 | Terminal event type/source are exactly consultation_dispatch_terminalized and administration:consultation.dispatch_terminal. | `INGRESS` | Mapped; audit pending |
| P2-K13 | Terminal event, row, and envelope share one event sequence. | `INGRESS` | Mapped; audit pending |
| P2-K14 | Terminal event payload contains exactly completion and terminal. | `INGRESS` | Mapped; audit pending |
| P2-K15 | Terminal envelope has the exact field set, authority, linkage, lineage, reason, nullable fields, and two sorted direct parents. | `INGRESS` | Mapped; audit pending |
| P2-K16 | dispatch_interrupted has no package bytes, null rejected fields, and zero measured completion. | `INGRESS` | Mapped; audit pending |
| P2-K17 | fixture_output_invalid requires raw bytes and stores exact raw digest/size with equal completion bytes. | `INGRESS` | Mapped; audit pending |
| P2-K18 | expired_before_ingress requires attempted raw bytes and stores exact raw digest/size with equal completion bytes. | `INGRESS` | Mapped; audit pending |
| P2-K19 | Terminal completion contains exactly completion ID, dispatch ID, terminal ID, and measured package bytes. | `INGRESS` | Mapped; audit pending |
| P2-K20 | Terminal row, completion, and event commit atomically at every write boundary. | `INGRESS` | Mapped; audit pending |
| P2-K21 | Repeated byte-identical terminalization is idempotent and conflicting reason/bytes fail closed. | `INGRESS` | Mapped; audit pending |
| P2-K22 | Reconciliation creates only dispatch_interrupted and never invokes the fixture. | `INGRESS` | Mapped; audit pending |

### L. Explicit disposition wake (ADR 0013 final rows)

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-L01 | Disposition is a separate caller-selected fail-fast organism work class with exact schema/config/status admission. | `DISPOSITION` | Mapped; audit pending |
| P2-L02 | Oldest eligible current-lineage proposal is selected by ingress sequence then proposal ID; final proposals are skipped. | `DISPOSITION` | Mapped; audit pending |
| P2-L03 | Current-state reference is reconstructed from current canonical rows under the disposition lock. | `DISPOSITION` | Mapped; audit pending |
| P2-L04 | All six disposition/reason mappings and precedence are exact; undeclared combinations reject. | `DISPOSITION` | Mapped; audit pending |
| P2-L05 | Invalid schema, ID, digest, linkage, lineage, permission, evaluator, action, or parameters reject before mutation. | `DISPOSITION` | Mapped; audit pending |
| P2-L06 | One successful disposition transaction writes exactly four ordered events and one immutable disposition row. | `DISPOSITION` | Mapped; audit pending |
| P2-L07 | Disposition event payload contains exactly disposition and the exact five-field outcome. | `DISPOSITION` | Mapped; audit pending |
| P2-L08 | Disposition ledger has the exact six fields, record count four, semantic-step count eight, and Phase 1 budget version. | `DISPOSITION` | Mapped; audit pending |
| P2-L09 | Disposition increments lifecycle once, preserves failure streak, claims no input, and changes no garden state. | `DISPOSITION` | Mapped; audit pending |
| P2-L10 | Transaction commits one pending checkpoint and existing publication stabilizes to sleeping. | `DISPOSITION` | Mapped; audit pending |
| P2-L11 | Precommit faults leave no disposition; postcommit publication interruption leaves one repairable final disposition. | `DISPOSITION` | Mapped; audit pending |
| P2-L12 | A repeated wake never replays a final disposition and deterministically selects the next or reports none. | `DISPOSITION` | Mapped; audit pending |
| P2-L13 | Expiry uses considering lifecycle; wall time is irrelevant. | `DISPOSITION` | Mapped; audit pending |
| P2-L14 | Disposition stops at the record/checkpoint and creates no action, garden, maintenance, request, fixture, retry, memory, or skill effect. | `DISPOSITION` | Mapped; audit pending |

### M. Current-lineage state and rollback epoch

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-M01 | Disposition checkpoint publication/repair reuses protected checkpoint machinery without repeating disposition. | `DISPOSITION` | Mapped; audit pending |
| P2-M02 | An expired pre-dispatch request no longer blocks a new request. | `REQ-CORE`, `DISPATCH` | Mapped; audit pending |
| P2-M03 | An admitted dispatch remains outstanding until response or terminal. | `DISPATCH`, `INGRESS` | Mapped; audit pending |
| P2-M04 | A successful response remains outstanding until disposition. | `INGRESS`, `DISPOSITION` | Mapped; audit pending |
| P2-M05 | Unavailable, terminal, and disposition states are final. | `INGRESS`, `DISPOSITION` | Mapped; audit pending |
| P2-M06 | No caregiver-writable mutable consultation status exists. | `GEN`, `INGRESS` | Mapped; audit pending |
| P2-M07 | Four requests, charges, and the measured legal payload maximum apply per current lineage under the independent 64 KiB guard. | `FINITE` | Mapped; audit pending |
| P2-M08 | Rollback increments lineage and old consultation rows become immutable inactive history. | `ROLLBACK` | Mapped; audit pending |
| P2-M09 | New lineage begins fresh four-call and zero-byte payload epochs. | `ROLLBACK` | Mapped; audit pending |
| P2-M10 | ADR 0007 bounds one physical organism to at most eight charged invocations across one completed rollback. | `ROLLBACK` | Mapped; audit pending |
| P2-M11 | Old-lineage unresolved work does not block current work and cannot accept late packages. | `ROLLBACK` | Mapped; audit pending |

### N. Authority and provenance

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-N01 | Canonical writer categories remain exactly organism and administration. | `GEN`, `REQ-CORE`, `DISPATCH`, `INGRESS`, `DISPOSITION`, `ABSENCE` | Mapped; audit pending |
| P2-N02 | Request and disposition use exact protected organism sources. | `REQ-CORE`, `DISPOSITION` | Mapped; audit pending |
| P2-N03 | Dispatch, ingress, terminalization, rollback, and related administrative operations use exact protected administration sources. | `DISPATCH`, `INGRESS`, `ROLLBACK` | Mapped; audit pending |
| P2-N04 | Fixture/caregiver provenance remains untrusted and separate from writer authority. | `PROTO-GRAPH`, `INGRESS` | Mapped; audit pending |
| P2-N05 | Request→dispatch→response→proposal→receipt→disposition is reconstructable by rows, digests, events, and artifacts. | `INGRESS`, `DISPOSITION`, `FINITE`, `ROLLBACK` | Mapped; audit pending |
| P2-N06 | Terminal path is reconstructable without a fake response or proposal. | `INGRESS` | Mapped; audit pending |
| P2-N07 | Parent events exist, precede children, are sorted/unique where required, and match organism/lineage. | `PROTO-REQ`, `INGRESS`, `DISPOSITION`, `FINITE`, `ROLLBACK` | Mapped; audit pending |
| P2-N08 | ADR 0013 disposition authority reconstructs one organism chain with exactly three direct parents; consultation rows remain immutable. | `GEN`, `DISPOSITION` | Mapped; audit pending |
| P2-N09 | Success receipt and terminal envelopes use exact administration sources while fixture provenance remains separate. | `INGRESS` | Mapped; audit pending |
| P2-N10 | Ingress/terminal direct parents are exactly request-created and dispatch-admitted events, sorted, unique, preceding, and current-lineage. | `INGRESS` | Mapped; audit pending |

### O. Physical budgets, checkpoints, and rollback

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-O01 | Every consultation record and semantic-step cap is exact at its boundary and one-over. | `GEN`, `REQ-CORE`, `DISPATCH`, `INGRESS`, `DISPOSITION`, `FINITE` | Mapped; audit pending |
| P2-O02 | Consultation rows and real SQLite sidecars count toward active ceiling and reserve. | `REQ-STORAGE`, `DISPATCH`, `INGRESS`, `PHYS-ABS` | Mapped; audit pending |
| P2-O03 | Consultation data, checkpoints, staging, rollback evidence, candidates, and disposition count toward the working set and inherited physical limits. | `PHYS-ABS`, `DISPOSITION`, `FINITE`, `ROLLBACK` | Mapped; audit pending |
| P2-O04 | No scalar energy field exists. | `GEN`, `ABSENCE` | Mapped; audit pending |
| P2-O05 | Rejections create no hidden fixture call, retry, row, event, clock read, or artifact. | `REQ-STORAGE`, `REQ-TIME`, `DISPATCH`, `INGRESS`, `DISPOSITION`, `FINITE`, `ROLLBACK` | Mapped; audit pending |
| P2-O06 | External input cannot alter protected consultation cost. | `PROTO-GRAPH`, `DISPATCH`, `INGRESS` | Mapped; audit pending |
| P2-O07 | Conservative precharge is never refunded after unavailable, invalid, expiry, or interruption. | `DISPATCH`, `INGRESS` | Mapped; audit pending |
| P2-O08 | Checkpoint validation covers schema-v2 objects, links, digests, sizes, configuration, and immutability. | `GEN`, `PROJ-CORE`, `PROJ-REPAIR`, `PROJ-RET`, `PROJ-RB` | Mapped; audit pending |
| P2-O09 | Request checkpoint preserves the exact request. | `REQ-CORE`, `PROJ-CORE` | Mapped; audit pending |
| P2-O10 | Disposition checkpoint preserves terminal consultation provenance. | `DISPOSITION`, `ROLLBACK` | Mapped; audit pending |
| P2-O11 | Administrative dispatch/ingress/terminal operations create no checkpoint. | `DISPATCH`, `INGRESS` | Mapped; audit pending |
| P2-O12 | Rollback can abandon later consultation history and blocks abandoned packages/proposals. | `ROLLBACK` | Mapped; audit pending |
| P2-O13 | The one-completed-rollback rule and retained evidence remain unchanged on schema-v2. | `ROLLBACK` | Mapped; audit pending |
| P2-O14 | Pending repair and retention reconciliation preserve consultation rows and provenance. | `PROJ-REPAIR`, `PROJ-RET`, `ROLLBACK` | Mapped; audit pending |
| P2-O15 | Schema-v2-zero active database overhead over paired schema-v1 is at most 256 KiB. | `GEN`, `PHYS-PAIR` | Mapped; audit pending |
| P2-O16 | Each zero-caregiver checkpoint/archive/source/transformed database overhead is at most 256 KiB. | `PHYS-PAIR` | Mapped; audit pending |
| P2-O17 | Aggregate additional zero-caregiver manifest/directory metadata is at most 1 MiB. | `PHYS-PAIR` | Mapped; audit pending |
| P2-O18 | Schema-v2-zero independently obeys 8 MiB active/artifact, 40 MiB store, 64 MiB working set, and 1 MiB reserve limits. | `PHYS-ABS`, `ROLLBACK` | Mapped; audit pending |
| P2-O19 | Independently measured schema-v2 bytes control admission, retention, repair, and rollback at one-below/at/one-over. | `PHYS-ABS` | Mapped; audit pending |
| P2-O20 | Wrong SHA/size, missing artifact, duplicate boundary, or broken manifest/registry/directory link fails before comparison/use. | `PROJ-CORE`, `PROJ-REPAIR`, `PROJ-RET`, `PROJ-RB`, `PROJ-EXPORT`, `PHYS-ABS`, `ROLLBACK` | Mapped; audit pending |
| P2-O21 | Near physical ceilings each schema proceeds or fails independently without assuming cross-version byte equality or partial mutation. | `PHYS-PAIR`, `PHYS-ABS` | Mapped; audit pending |
| P2-O22 | Schema-v2 checkpoint/repair/retention/rollback artifacts preserve exact consultation rows/provenance and immutable configuration. | `PHYS-ABS`, `ROLLBACK` | Mapped; audit pending |

### P. Explicit absence

| ID | Final accepted requirement synopsis | Primary evidence bundles | Status |
| --- | --- | --- | --- |
| P2-P01 | No live API, HTTP client, provider SDK, or chat automation exists. | `ABSENCE`, `GEN`, `DISPOSITION` | Mapped; audit pending |
| P2-P02 | No free-form human/model text is accepted. | `PROTO-REQ`, `PROPOSAL`, `PROTO-GRAPH`, `INGRESS` | Mapped; audit pending |
| P2-P03 | No memory, skill, training, source-generation, or test-generation runtime exists. | `ABSENCE`, `DISPOSITION` | Mapped; audit pending |
| P2-P04 | No arbitrary code, SQL, shell, tool, path, URL, credential, or executable payload is accepted. | `PROTO-REQ`, `PROPOSAL`, `PROTO-GRAPH`, `INGRESS` | Mapped; audit pending |
| P2-P05 | No continuous, daemon, serve, watch, or always-on loop exists. | `ABSENCE` | Mapped; audit pending |
| P2-P06 | No personality, emotion, affection, mood, or virtual-pet canonical state exists. | `ABSENCE`, `GEN` | Mapped; audit pending |
| P2-P07 | No external proposal enters the existing Phase 1 action selector or executor. | `ABSENCE`, `DISPOSITION` | Mapped; audit pending |

## Cross-cutting audit checks

The independent audit must still verify, against one exact candidate commit:

1. every bundle above still names existing tests and the tests exercise the stated invariant rather than only a neighboring happy path;
2. the original 152 Phase 1 tests remain byte-unchanged and included;
3. schema-v1, schema-v2-zero, and deterministic-fixture paths remain simultaneously supported;
4. all direct-parent, authority, immutable-row, artifact, and physical-accounting claims reconstruct from canonical state and published artifacts;
5. the explicit-absence test and distributed adversarial corpora cover the complete current source/CLI/schema surface;
6. no accepted amendment row is omitted, counted twice as a substitute for another row, or interpreted using an obsolete superseded wording.

## Known audit-attention areas, not findings

- P2-A01 depends on both the actual unchanged Phase 1 suite and the repository compare; CI count alone is not a byte-identity proof.
- P2-C03/C08/C14/C18 and P2-O20 intentionally have multiple evidence bundles because checkpoint, repair, retention, rollback, and export each require independent integrity evidence.
- P2-J12/P2-J25 and P2-K06/P2-K20/P2-K21 overlap by design but are not interchangeable: the ADR 0012 rows require exact row/event identities and fault points in addition to the base atomicity/idempotence requirement.
- P2-P01–P2-P07 combine exact protocol rejection tests with candidate-wide source, import, CLI, schema, and selector/executor isolation inspection.
- No Codex or other independent implementation audit conclusion is recorded here.

## Completion rule

This map may become the input to the single read-only Phase 2 implementation audit only after its exact branch head is CI-green. Phase 2 remains open under Issue #61 until the audit concludes satisfactorily and any accepted findings are repaired through protected work.

## Independent audits and accepted repair supplement

Issue #120 inspected exact candidate `44e363e874679537fef43d9f78e382ecf5dc5d3e` and concluded **not ready to freeze; specified repairs required**. Issue #121 owns its accepted repairs.

Issue #122 inspected exact candidate `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`. It independently confirmed Findings 1–3 closed, all 47 original Phase 1 test/helper blobs byte-identical, the 152-test control green, the full 381-test suite green, the 213-ID set exact, schema-v1 support intact, and the explicit-absence surface intact. It still concluded **not ready to freeze; specified repairs required** because Finding 4 lacked active-organism, exact-manifest-field, and exact request snapshot linkage.

Issue #123 adds the following `REPAIR-F4` evidence without changing any accepted ID or requirement meaning:

- exact 18-field checkpoint manifest enforcement;
- `manifest.organism_id` and validated snapshot organism binding to the active organism/request;
- complete checkpoint request row/envelope equality with the active request;
- complete checkpoint `consultation_request_created` event equality with the active event;
- coherent wrong-organism substitution rejection;
- registry-linked undeclared manifest field rejection;
- missing request row and mismatched request event rejection;
- zero clock, dispatch, charge, admission-event, terminal, completion, or fixture effects on every rejection.

Exact Finding 4 implementation head: `9814908aae2646f4c09142030b7381e5f9a1394b`. Strict isolated validation: `385 passed in 54.25s`, plus install and source/test compilation. The shared frozen Phase 1 validator and original Phase 1 test/helper blobs are unchanged. Temporary repair infrastructure is absent.

This supplement strengthens P2-F02, P2-O20, ADR 0008's stable request-checkpoint admission boundary, and the existing dispatch/physical/explicit-absence evidence. It does not add live capability, authority, schema, resource, or protocol behavior.

This map remains an audit input. One final focused read-only closure audit must independently verify Finding 4 and regression across the complete gate before PR #119 may merge or Issue #61 may close. Phase 2 is not frozen.
