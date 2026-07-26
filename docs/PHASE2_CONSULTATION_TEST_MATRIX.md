# Phase 2 Consultation Boundary Test Matrix

Status: **Proposed design targets; no Phase 2 implementation exists yet**

This matrix maps proposed ADR 0008 and `docs/phase2/CONSULTATION_PROTOCOL_V1.md` to protected tests required before deterministic fixture plumbing can be accepted.

The complete Phase 1 suite remains unchanged and is the first regression layer.

## A. Frozen Phase 1 baseline

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-A01 | All 152 Phase 1 tests remain unchanged/passing against schema-v1 | Existing suite without skip, conditional, caregiver import, or assertion change |
| P2-A02 | Schema-v1 init/CLI/checkpoint/rollback/authority/budgets remain supported | Existing Phase 1 tests own paths |
| P2-A03 | Phase 2 modules add no network/subprocess/code/workspace route to Phase 1 action execution | Re-run guarded action tests with package installed |
| P2-A04 | Base contract remains `0.2`; schema2 is explicit extension | Exact version assertions |

## B. Schema-v2 initialization and validation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-B01 | Schema2/protocol1 with exactly one accepted Phase 2 budget config | Parameterized init |
| P2-B02 | Zero and fixture configs are distinct/protected | Unknown/mixed reject |
| P2-B03 | Original Phase 1 tables/columns/actions/evaluators/seed exact | Protected fingerprint |
| P2-B04 | No new column in original Phase 1 table | Schema introspection |
| P2-B05 | Consultation tables/indexes/keys/triggers exact | Corrupt each, reject active/checkpoint validation |
| P2-B06 | Operational consultation tables empty at genesis | Row/sequence assertions |
| P2-B07 | Genesis stable before wakeable | Schema2 checkpoint test |
| P2-B08 | Schema1 never auto-migrated by any Phase2 operation | Exact rejection identity |
| P2-B09 | No migration/downgrade command exists | API/CLI surface |

## C. Zero-caregiver control

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-C01 | Zero config creates no request on no-applicable action | Exact ordinary abstention + empty state |
| P2-C02 | No dispatch/fixture/response/proposal/disposition/terminal/cost | Empty tables + guarded adapter |
| P2-C03 | No consultation event/source | Exact history |
| P2-C04 | Phase1 projection matches schema1 | Normalize only schema/budget config; compare every original row/column/payload/sequence |
| P2-C05 | Empty added objects are only byte-level exclusion | Reject extra normalization/nonempty operation object |
| P2-C06 | Status/lifecycle/checkpoint/rollback/authority match Phase1 | Paired scenarios |

## D. Garden request wake and failure honesty

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-D01 | Request only for incomplete-objective no-applicable action | Applicable/action-complete create none |
| P2-D02 | Tick/abstention/action/mutation/core outcome unchanged | Exact Phase1 core comparison |
| P2-D03 | Failure streak increments exactly once, never resets | Streak 0/1 boundaries |
| P2-D04 | Maintenance-entering wake creates no request | Start streak2; maintenance/no consultation event |
| P2-D05 | One request and <=2 extra records per wake | Exact record count |
| P2-D06 | One current-lineage outstanding request | Second attempt no duplicate |
| P2-D07 | Four requests per lineage epoch | Fifth current-lineage attempt blocked |
| P2-D08 | Request ordinal is current-lineage count+1 | Old-lineage rows ignored after rollback |
| P2-D09 | Identity object/envelope/digest/ID deterministic | Independent construction |
| P2-D10 | Request ID excludes event sequence but final envelope links actual event | Golden test |
| P2-D11 | Request contains only declared typed context | Adversarial fields |
| P2-D12 | Request row/event/core lifecycle atomic | Precommit injection |
| P2-D13 | Stable request checkpoint before dispatch | Pending reject, stable accept |
| P2-D14 | Backward wall time no effect on order/expiry | Exact sequences |
| P2-D15 | Competing/nested garden wakes fail fast | Real connections |
| P2-D16 | Later garden wakes remain allowed | State can diverge without hidden proposal priority |

## E. Dispatch admission and charging

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-E01 | Fresh fail-fast administrative transaction | Competing/nested rejection |
| P2-E02 | Requires sleeping/stable checkpoint/current lineage/expiry/no prior dispatch | Precondition matrix |
| P2-E03 | Dispatch/cost/event atomic | Failure injection |
| P2-E04 | Fixture never called before commit | Guard + forced commit failure |
| P2-E05 | One attempt/invocation/work charged at admission | Exact ledger |
| P2-E06 | Charge remains after process interruption | Spawn crash |
| P2-E07 | Repeated admission never authorizes second call | Guard count |
| P2-E08 | Four charges/current lineage; fifth blocked | Epoch boundary |
| P2-E09 | Predicted/post-write physical checks preserve 1 MiB reserve | Real size boundary |
| P2-E10 | No checkpoint/action effect | Registry/action exact |

## F. Fixture boundary

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-F01 | No SQLite write lock held during fixture | Independent writer probe |
| P2-F02 | Receives exactly request envelope + case ID | Signature guard |
| P2-F03 | No DB/path/workspace/repo/executor/evaluator/checkpoint/rollback/network/subprocess/randomness handle | Guarded real path |
| P2-F04 | Identical request/case -> identical bytes | Exact repeat |
| P2-F05 | Only one charged call despite deterministic purity | Dispatch guard |
| P2-F06 | Package returned to caller remains noncanonical until ingress | DB exact before ingress |
| P2-F07 | Case ID declared in dispatch provenance | Case variation |
| P2-F08 | Human/model/money/latency zero | Cost assertions |

## G. Acyclic identifiers

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-G01 | Request identity exact and event-sequence exclusion exact | Golden object |
| P2-G02 | Dispatch identity exact | Golden object |
| P2-G03 | Proposal ID excludes response ID | Golden object |
| P2-G04 | Response ID uses proposal IDs/content digests, no cycle | Dependency graph assertion |
| P2-G05 | Response ID inserted before final package digest | Golden bytes |
| P2-G06 | Disposition ID excludes event sequence | Golden object |
| P2-G07 | Complete graph reproducible | Two independent builds |
| P2-G08 | Undeclared normalization/order change invalidates digest | Canonicalization corpus |

## H. External package authority separation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-H01 | External response contains no writer authority | Reject fields |
| P2-H02 | External response contains no authoritative budget/cost | Reject fields |
| P2-H03 | Adapter/case provenance cannot change writer/permission | Spoof tests |
| P2-H04 | Success exactly one proposal; unavailable zero | Cardinality |
| P2-H05 | Only three proposal types | Unknown reject |
| P2-H06 | No free text/code/SQL/shell/path/URL/credential/tool/authority command | Adversarial corpus |

## I. Response ingress

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-I01 | Fresh fail-fast administrative transaction | Competing/nested |
| P2-I02 | Administration recomputes IDs/bytes/digest | Forgery rejection |
| P2-I03 | Exact current-lineage request/dispatch/adapter/case linkage | Unknown/stale reject |
| P2-I04 | Sleeping or maintenance, no pending/rollback/quarantine | State matrix |
| P2-I05 | Before expiry succeeds; after expiry fails | Lifecycle boundary |
| P2-I06 | One response maximum | Conflict rejection |
| P2-I07 | Byte-identical duplicate idempotent | DB/event/artifact/clock exact |
| P2-I08 | Logical/per-lineage byte limits exact | Boundary+one-over |
| P2-I09 | Physical/reserve limits exact | Real size test |
| P2-I10 | Cannot action/change authority/clear/checkpoint/migrate/rollback | Guarded path |
| P2-I11 | Response/proposal/receipt/cost completion/event atomic | Failure injection |
| P2-I12 | Process exit rolls back ingress | Spawn crash |
| P2-I13 | No checkpoint publication | Registry exact |
| P2-I14 | Maintenance evidence recording cannot clear maintenance | Exact status |
| P2-I15 | Unavailable terminalizes without proposal/disposition/retry | Derived state |
| P2-I16 | Busy/pending rejection permits explicit same-byte resubmission without fixture recall | Two bounded ingress attempts, one charge |

## J. Dispatch terminal/reconciliation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-J01 | Fixture exception -> one terminal/no retry | Normal workflow |
| P2-J02 | Invalid package rejects ingress then terminalizes invalid | Explicit operations |
| P2-J03 | Expiry after admission -> expired-before-ingress terminal | Lifecycle test |
| P2-J04 | Crash after admission leaves charged unresolved dispatch | Spawn crash |
| P2-J05 | Explicit reconcile records interrupted without fixture | Guard count |
| P2-J06 | Reconcile fail-fast/idempotent/one terminal | Competing/repeated |
| P2-J07 | No response after terminal | Rejection |
| P2-J08 | No terminal after response | Rejection |
| P2-J09 | Sleeping/maintenance only; no pending/rollback/quarantine | State matrix |
| P2-J10 | Current lineage required | Abandoned dispatch reject |
| P2-J11 | Reserve preserved/no checkpoint | Accounting/artifact |

## K. Explicit disposition wake

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-K01 | Separate explicit work class; garden never claims proposal | API/queue test |
| P2-K02 | Caller choice prevents hidden priority | Interleaved queues |
| P2-K03 | Fresh fail-fast wake transaction | Competing/nested |
| P2-K04 | Requires schema2/sleeping/no pending/fixture config/queued current-lineage proposal | Matrix |
| P2-K05 | No-work/maintenance attempts typed/nonmutating/nonqueued/zero-clock where specified | Exact rejection |
| P2-K06 | Oldest ingress sequence then proposal ID | Reverse insertion |
| P2-K07 | One proposal max, no garden claim | Queue exact |
| P2-K08 | Current state overrides fixture assumptions | Garden change before disposition |
| P2-K09 | Valid through N+2, rejected at considering N+3 | Exact boundary |
| P2-K10 | Accepted has no selector/action/garden effect | Exact state |
| P2-K11 | Rejected reason coverage | Parameterized evaluator |
| P2-K12 | Deferred final/no retry | Later wake |
| P2-K13 | Clarification final/no follow-up | Counts exact |
| P2-K14 | Proposal defer vs disposition deferred distinguishable | Reports/envelopes |
| P2-K15 | Lifecycle increments; Phase1 failure streak preserved | Streak boundaries |
| P2-K16 | Disposition/event/outcome/pending checkpoint atomic | Failure injection |
| P2-K17 | Checkpoint stabilization/pending exclusion unchanged | Existing semantics |
| P2-K18 | Process exit restores queued proposal/releases lock | Spawn crash |
| P2-K19 | No duplicate disposition/event | Repeated wake |
| P2-K20 | Maximum disposition + checkpoint fits reserve | Real-size proof |

## L. Current-lineage state and rollback epoch

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-L01 | Awaiting dispatch counts outstanding only through expiry | Lifecycle derivation |
| P2-L02 | Expired pre-dispatch no longer blocks new request | Later request |
| P2-L03 | Admitted dispatch remains outstanding until response/terminal | Expiry crossing |
| P2-L04 | Successful response outstanding until disposition | Second request blocked |
| P2-L05 | Unavailable/terminal/disposition final | Derived state |
| P2-L06 | No caregiver-writable mutable status | Schema/corruption |
| P2-L07 | Four requests/charges/payload budget per current lineage | Boundaries |
| P2-L08 | Rollback increments lineage and old rows become historical/inactive | Restored candidate test |
| P2-L09 | New lineage begins fresh four-call epoch | Post-rollback request boundary |
| P2-L10 | ADR0007 bounds whole physical organism to at most eight charges | One rollback then second rollback rejection |
| P2-L11 | Old-lineage unresolved dispatch needs no current reconciliation and cannot block current request | State derivation |

## M. Authority and provenance

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-M01 | Writer categories exactly organism/administration | Reject caregiver/evaluator/repo writers |
| P2-M02 | Request/disposition protected organism sources | Mapping/spoof |
| P2-M03 | Dispatch/ingress/terminal protected admin sources | Mapping/spoof |
| P2-M04 | Caregiver provenance separate from ingress authority in reports | Nonspoofable output |
| P2-M05 | Request->dispatch->response->proposal->receipt->disposition reconstructable | Join/digest |
| P2-M06 | Terminal path reconstructable without fake response/proposal | Chain |
| P2-M07 | Parent events exist/precede/current lineage | Corrupt/future/old reject |
| P2-M08 | All consultation rows update/delete protected | Trigger tests |

## N. Budgets and physical storage

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-N01 | Every counter/record cap exact | Boundary/one-over |
| P2-N02 | No scalar energy | Schema |
| P2-N03 | Consultation/sidecars count in active ceiling/reserve | Real 8 MiB test |
| P2-N04 | Consultation/checkpoint/staging/rollback evidence count in working set | Aggregate after rollback |
| P2-N05 | Rejection has no hidden fixture/retry/row/event/clock/artifact | Exact no-effect |
| P2-N06 | Caregiver cannot alter protected cost | Forged fields |
| P2-N07 | Precharge never refunded after unavailable/invalid/expiry/interruption | Ledger |
| P2-N08 | Garden core <=16, request extension <=2 | Max record test |
| P2-N09 | Per-lineage 64 KiB logical total resets only on lineage change | Boundary + rollback |

## O. Checkpoint and rollback interactions

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-O01 | Checkpoint validates schema2 objects/links/digests/immutability | Corruption rejection |
| P2-O02 | Request checkpoint preserves exact request | Restore inspection |
| P2-O03 | Disposition checkpoint preserves terminal provenance | Exact linkage |
| P2-O04 | Admin operations create no checkpoint | Registry/artifact |
| P2-O05 | Rollback may abandon later consultation history | Archive/restored assertions |
| P2-O06 | Abandoned-lineage package cannot ingress | Pre-mutation reject |
| P2-O07 | Abandoned-lineage proposal cannot dispose | Current-lineage filter |
| P2-O08 | One-completed-rollback rule/evidence unchanged | ADR0007 tests schema2 |
| P2-O09 | Pending repair/retention reconciliation preserve consultation rows | Cross-boundary tests |

## P. Explicit absence

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-P01 | No live API/HTTP/provider SDK/chat automation | Source/import/runtime |
| P2-P02 | No free-form human/model text | Parser |
| P2-P03 | No memory/skill/training/source/test generation | Surface inspection |
| P2-P04 | No arbitrary code/SQL/shell/tool/path/URL/credential | Corpus |
| P2-P05 | No continuous loop | CLI/runtime |
| P2-P06 | No personality/emotion/pet state | Schema/report |
| P2-P07 | No proposal enters existing action selector | Selector guard |

## Acceptance rule

The first implementation issue must map each slice to matrix IDs. No test may weaken/condition the 152-test Phase 1 baseline.

Before design acceptance, one independent read-only Codex audit must review the exact draft PR head, proposed ADR 0008, protocol v1, this matrix, Issue #59, and frozen Phase 1 authority, transaction, failure, lineage budget, storage, checkpoint, and rollback boundaries.
