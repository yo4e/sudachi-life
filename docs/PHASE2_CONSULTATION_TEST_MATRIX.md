# Phase 2 Consultation Boundary Test Matrix

Status: **Accepted design evidence map with ADR 0008; no Phase 2 implementation exists yet**

This matrix maps accepted ADR 0008 and `docs/phase2/CONSULTATION_PROTOCOL_V1.md` to protected evidence required before the deterministic-fixture implementation can be accepted.

The unchanged 152-test Phase 1 suite is always the first regression layer.

## A. Frozen Phase 1 baseline

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-A01 | All 152 Phase 1 tests remain unchanged and passing against schema-v1 | Original suite with no skip, conditional, assertion change, or caregiver import |
| P2-A02 | Schema-v1 initialization, CLI, checkpoints, rollback, authority, and budgets remain supported | Existing Phase 1 path tests |
| P2-A03 | Phase 2 adds no network, subprocess, arbitrary-code, or workspace route to Phase 1 action execution | Guarded source/runtime inspection plus existing action tests |
| P2-A04 | Base contract remains `0.2`; schema-v2 is an explicit extension | Exact version assertions |
| P2-A05 | Existing Phase 1 tables receive no new columns | Schema fingerprint and introspection |

## B. Schema-v2 initialization and validation

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-B01 | Schema-v2/protocol-v1 initializes with exactly one accepted Phase 2 budget configuration | Parameterized genesis |
| P2-B02 | Zero-caregiver and fixture configurations are distinct and protected | Unknown and mixed configuration rejection |
| P2-B03 | Original actions, evaluators, seed rows, clocks, and authority mappings are exact | Protected fingerprint |
| P2-B04 | Consultation tables, indexes, keys, triggers, and immutable constraints are exact | Corrupt each object and reject active/checkpoint validation |
| P2-B05 | Operational consultation tables and their sequences are empty at genesis | Exact rows and `sqlite_sequence` assertions |
| P2-B06 | Genesis is checkpoint-stable before wakeable | Schema-v2 genesis checkpoint test |
| P2-B07 | Schema-v1 is never auto-migrated or downgraded | Exact non-mutating rejection |
| P2-B08 | No migration/downgrade command exists in the first implementation | API and CLI surface assertion |

## C. Exact zero-caregiver control

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-C01 | Identical declared inputs and clocks drive paired schema-v1 and schema-v2-zero runs | Paired deterministic harness |
| P2-C02 | Only original columns named exactly `schema_version` and `budget_config_version` receive the declared comparison exception | Projection-location whitelist test |
| P2-C03 | Only top-level event-payload keys with those exact names are normalized | Nested/similar-key adversarial corpus |
| P2-C04 | Every other original row, column, event type, sequence, authority, source, parent, key, and payload value matches exactly | Canonical projection equality |
| P2-C05 | No additional or missing original event-payload key is hidden by projection | Add/remove-key rejection |
| P2-C06 | All operational consultation tables are empty and have no sequence entry | Exact DB assertions |
| P2-C07 | No consultation event, source, cost, adapter invocation, terminal, disposition, or effect occurs | Guarded adapter plus history/report assertions |
| P2-C08 | Status, lifecycle, failure streak, behavior, checkpoint eligibility, rollback eligibility, and authority match | Paired scenarios |
| P2-C09 | Raw SQLite bytes/checkpoint digests are explicitly not claimed equal because empty schema-v2 objects exist | Negative control |

## D. Garden request wake and failure honesty

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-D01 | Request is considered only after incomplete-objective `no_applicable_action` | Applicable-action and objective-complete paths create none |
| P2-D02 | Tick, abstention, action, mutation, outcome, and failure increment remain exact Phase 1 behavior | Core projection equality |
| P2-D03 | `consecutive_failures` increments exactly once and is never reset by consultation | Streak boundary tests |
| P2-D04 | A maintenance-entering wake creates no request | Start at streak two; exact maintenance and empty consultation state |
| P2-D05 | At most one request and two additional records occur in one wake | Exact record count |
| P2-D06 | At most one current-lineage request is outstanding | Second-attempt no-effect test |
| P2-D07 | Four requests are permitted per lineage; the fifth is typed and non-mutating | Epoch boundary |
| P2-D08 | Request ordinal is current-lineage count plus one | Rollback/old-lineage test |
| P2-D09 | Request identity, preimage bytes, digest, ID, final envelope, and event linkage are deterministic | Golden independent construction |
| P2-D10 | Request ID excludes the later event sequence and no other undeclared field | Exact identity object assertion |
| P2-D11 | Request contains only declared typed context and no free text | Adversarial field corpus |
| P2-D12 | Created request row and event commit atomically | Savepoint/pre-commit fault injection |
| P2-D13 | Created request is checkpoint-stable before dispatch | Pending rejection and stable acceptance |
| P2-D14 | Backward wall time cannot affect order or expiry | Exact lifecycle/event test |
| P2-D15 | Competing and nested garden wakes fail fast | Real connections and subprocesses |
| P2-D16 | Later garden wakes remain allowed while a request is outstanding | Interleaved garden scenario |

## E. Request-extension storage boundary

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-E01 | Request metadata is an optional savepoint extension, not a requirement for the Phase 1 core wake | Core-only commit when extension is refused |
| P2-E02 | Pre-write accounting includes core wake, request extension, resulting checkpoint, active DB, sidecars, reserve, and working set | Exact accounting fixture |
| P2-E03 | If extension prediction fails, no consultation row/event/source is written | Near-boundary preflight test |
| P2-E04 | If page growth causes post-write failure, only the extension savepoint rolls back | Injected/real page-growth test |
| P2-E05 | The unchanged Phase 1 core outcome and ordinary checkpoint still commit after extension refusal | Canonical equality plus checkpoint validation |
| P2-E06 | Caller receives noncanonical `consultation_request_not_created_storage_budget` | Exact result type |
| P2-E07 | Real 8 MiB boundary where core wake fits but request extension would consume the 1 MiB reserve leaves DB within ceiling and next wake possible | Real file-size test, not mocked accounting |
| P2-E08 | Boundary test covers SQLite `-wal`/`-shm`, checkpoint staging, and working-set accounting | Real sidecars and aggregate measurement |
| P2-E09 | If the Phase 1 core wake itself cannot fit, frozen Phase 1 failure behavior remains unchanged | Existing Phase 1 boundary comparison |
| P2-E10 | Successful maximum-size request plus checkpoint also preserves reserve | Real success boundary |

## F. Dispatch admission and conservative charging

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-F01 | Dispatch uses a fresh fail-fast administrative transaction | Competing/nested rejection |
| P2-F02 | Sleeping, stable checkpoint, current lineage, expiry, no prior dispatch, and no terminal state are required | Admission matrix |
| P2-F03 | Dispatch, cost charge, and administrative event commit atomically | Fault injection |
| P2-F04 | Fixture is never called before admission commits | Guard plus forced commit failure |
| P2-F05 | One dispatch attempt, invocation charge, and work unit are recorded | Exact ledger |
| P2-F06 | Charge remains after process interruption | Spawned crash |
| P2-F07 | Repeated admission never authorizes another fixture call | Guarded call count |
| P2-F08 | Four charges are allowed per lineage; fifth is blocked | Epoch boundary |
| P2-F09 | Physical checks preserve the 1 MiB reserve | Real-size boundary |
| P2-F10 | Dispatch creates no checkpoint or action effect | Registry/action exact |

## G. External deterministic fixture boundary

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-G01 | No SQLite write lock is held during fixture execution | Independent writer probe |
| P2-G02 | Fixture receives exactly final request envelope and declared case ID | Signature/capability guard |
| P2-G03 | No DB, path, workspace, repository, executor, evaluator, checkpoint, rollback, network, subprocess, credential, tool, or randomness capability exists | Guarded real path and source inspection |
| P2-G04 | Identical request and case produce identical bytes | Exact repeated construction |
| P2-G05 | Deterministic purity cannot bypass the one charged invocation | Dispatch guard |
| P2-G06 | Output remains noncanonical before ingress | Exact DB/history identity |
| P2-G07 | Human, model, money, and declared latency remain zero | Cost assertions |

## H. Digest preimages and canonical graph

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-H01 | `H(label,value)` uses the exact domain prefix, newline separators, label, and canonical bytes | Golden byte vectors |
| P2-H02 | Alternate NUL, whitespace, pretty JSON, Unicode form, separator, or label fails | Adversarial vectors |
| P2-H03 | Request identity contains exactly declared fields | Golden object |
| P2-H04 | Dispatch identity contains exactly declared fields | Golden object |
| P2-H05 | Proposal content digest and proposal ID share the exact proposal-content preimage | Golden object |
| P2-H06 | Proposal identity excludes response ID | Dependency assertion |
| P2-H07 | Response ID uses already-derived proposal IDs/content digests without a cycle | Graph test |
| P2-H08 | Final response ID is inserted into proposal before package digest | Golden package bytes |
| P2-H09 | Package preimage has exactly `response` and `proposals` keys | Extra/missing-key rejection |
| P2-H10 | Disposition identity and current-state digest use exact labels and fields | Golden vectors |
| P2-H11 | Complete graph is reproducible in two independent builds | Full equality |

## I. Exact response and proposal schemas

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-I01 | Response exact field set and status/cardinality rules are enforced | Unknown/missing/extra-field corpus |
| P2-I02 | Proposal exact common field set is enforced | Unknown/missing/extra-field corpus |
| P2-I03 | Proposal expiry equals linked request expiry exactly | Shorter/longer/independent expiry rejection |
| P2-I04 | Confidence basis exactly links deterministic fixture case | Forgery rejection |
| P2-I05 | Required evaluator IDs equal protected type-specific set | Add/remove/reorder/rename rejection |
| P2-I06 | `action_candidate` subject, parameters, rationale, action allowlist, and registered schema are exact | Parameterized valid/invalid actions |
| P2-I07 | `abstain` has exact objective subject and `no_supported_action` value/rationale | Exact valid and mutation corpus |
| P2-I08 | `defer` has exact objective subject and `await_state_change` value/rationale | Exact valid and mutation corpus |
| P2-I09 | `defer` contains no schedule, wake time, retry command, or effect | Forbidden-field corpus |
| P2-I10 | External package contains no writer authority or authoritative cost/budget/permission/evaluator command | Spoof corpus |
| P2-I11 | Free text, code, SQL, shell, path, URL, credential, tool, and new-action definition reject | Adversarial corpus |

## J. Logical payload and ingress

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-J01 | Request final envelope is at most 16 KiB | Boundary and one-over |
| P2-J02 | Complete external package is at most 16 KiB before parse and after canonicalization | Raw/canonical boundary |
| P2-J03 | Provenance is at most 8 KiB and included inside, not added to, package limit | Boundary and double-count guard |
| P2-J04 | Lineage formula is exactly sum(request envelope bytes) plus sum(successfully ingressed package bytes) | Independent ledger reconstruction |
| P2-J05 | Response/proposal/provenance are not double-counted | Max-envelope scenario |
| P2-J06 | Duplicate ingress adds zero logical bytes | Idempotence |
| P2-J07 | Metadata rows are excluded logically but included physically | Dual accounting assertions |
| P2-J08 | Invalid pre-mutation package adds no logical payload but terminal digest/size counts physically | Invalid/terminal scenario |
| P2-J09 | 64 KiB per-lineage boundary and one-over are exact across mixed request/package sizes | Table-driven combinations |
| P2-J10 | New lineage begins a fresh 64 KiB epoch; old rows remain historical | Rollback boundary |
| P2-J11 | Ingress recomputes every identity, digest, canonical size, linkage, expiry, and proposal schema | Forgery corpus |
| P2-J12 | Response, optional proposal, receipt, measured completion, and event commit atomically | Fault injection |
| P2-J13 | Byte-identical duplicate is idempotent with no event, clock, charge, or payload increment | Exact state |
| P2-J14 | Busy/pending rejection permits explicit same-byte resubmission without fixture recall | Two attempts, one fixture charge |
| P2-J15 | Ingress cannot action, clear maintenance, checkpoint, migrate, roll back, or change authority | Guarded path |

## K. Dispatch terminalization and reconciliation

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-K01 | Fixture exception produces one terminal outcome and no retry | Normal administrative workflow |
| P2-K02 | Invalid package is rejected then explicitly terminalized | Separate-operation assertions |
| P2-K03 | Expiry after admission produces `expired_before_ingress` | Lifecycle crossing |
| P2-K04 | Crash after admission leaves charged unresolved dispatch | Spawned crash |
| P2-K05 | Explicit reconciliation records interruption without fixture call | Guarded count |
| P2-K06 | Terminalization is fail-fast, idempotent, and mutually exclusive with response | Competing/repeated tests |
| P2-K07 | Terminal evidence stores only bounded digest, size, reason, linkage, and event | Schema/size assertion |
| P2-K08 | Current lineage and declared durable state are required | State/rollback matrix |
| P2-K09 | Reserve is preserved and no checkpoint is created | Real accounting/artifacts |

## L. Explicit disposition wake

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-L01 | Disposition is a separate caller-selected work class; garden never claims a proposal | API and interleaved queue test |
| P2-L02 | Fresh fail-fast wake transaction and sleeping/no-pending admission are required | Competing/state matrix |
| P2-L03 | Selection is oldest ingress event sequence then proposal ID | Reverse insertion |
| P2-L04 | At most one proposal is considered and no garden input is claimed | Queue exact |
| P2-L05 | Current state overrides fixture assumptions | State change before disposition |
| P2-L06 | Proposal valid through request `N+2` and rejected at considering `N+3` | Exact lifecycle boundary |
| P2-L07 | Accepted disposition has no selector, action, memory, skill, or garden effect | Full state assertion |
| P2-L08 | Rejected reason codes are protected and complete | Parameterized evaluator |
| P2-L09 | Deferred and clarification are final with no retry/follow-up | Later-wake counts |
| P2-L10 | Proposal type `defer` and disposition `deferred` remain distinct | Envelope/report assertions |
| P2-L11 | Lifecycle increments while garden failure streak is preserved | Streak boundaries |
| P2-L12 | Disposition, event, outcome, and pending checkpoint commit atomically | Fault injection |
| P2-L13 | Process exit restores queued proposal and releases ownership | Spawned crash |
| P2-L14 | Maximum disposition plus checkpoint fits inherited reserve | Real-size proof |

## M. Current-lineage state and rollback epoch

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-M01 | Pre-dispatch request is outstanding only through expiry | Lifecycle derivation |
| P2-M02 | Expired pre-dispatch request no longer blocks a new request | Later request |
| P2-M03 | Admitted dispatch remains outstanding until response/terminal | Expiry crossing |
| P2-M04 | Successful response remains outstanding until disposition | Second-request rejection |
| P2-M05 | Unavailable, terminal, and disposition states are final | Derived-state assertions |
| P2-M06 | No caregiver-writable mutable status exists | Schema/corruption |
| P2-M07 | Four requests, charges, and 64 KiB apply per current lineage | Boundary tests |
| P2-M08 | Rollback increments lineage and old rows become historical/inactive | Restored-candidate test |
| P2-M09 | New lineage begins a fresh four-call/payload epoch | Post-rollback boundary |
| P2-M10 | ADR 0007 bounds one physical organism to eight charged invocations | One rollback then second-rollback rejection |
| P2-M11 | Old-lineage unresolved work neither blocks current work nor accepts late packages | State derivation and stale ingress |

## N. Authority and provenance

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-N01 | Writer categories remain exactly organism and administration | Reject caregiver/evaluator/repository writers |
| P2-N02 | Request/disposition use protected organism sources | Exact mapping/spoof rejection |
| P2-N03 | Dispatch/ingress/terminal use protected administration sources | Exact mapping/spoof rejection |
| P2-N04 | Caregiver provenance is separate from ingress writer authority | Reports and forgery test |
| P2-N05 | Request→dispatch→response→proposal→receipt→disposition is reconstructable | Join/digest verification |
| P2-N06 | Terminal path is reconstructable without fake response/proposal | Provenance chain |
| P2-N07 | Parent events exist, precede children, and match lineage | Corrupt/future/old rejection |
| P2-N08 | Every consultation row rejects update and delete | Trigger tests |

## O. Physical budgets, checkpoints, and rollback

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-O01 | Every record and semantic-step cap is exact | Boundary/one-over |
| P2-O02 | Consultation rows and SQLite sidecars count toward active ceiling/reserve | Real 8 MiB scenarios |
| P2-O03 | Consultation data, checkpoints, staging, rollback evidence, and candidates count toward working set | Aggregate after rollback |
| P2-O04 | No scalar energy field exists | Schema inspection |
| P2-O05 | Rejections create no hidden fixture call, retry, row, event, clock, or artifact | Exact no-effect assertions |
| P2-O06 | Caregiver cannot alter protected cost | Forged-field rejection |
| P2-O07 | Precharge is never refunded after unavailable, invalid, expiry, or interruption | Ledger assertions |
| P2-O08 | Checkpoint validation covers schema-v2 objects, links, digests, and immutability | Corruption rejection |
| P2-O09 | Request checkpoint preserves exact request | Restore inspection |
| P2-O10 | Disposition checkpoint preserves terminal provenance | Exact linkage |
| P2-O11 | Administrative operations create no checkpoint | Registry/artifact assertion |
| P2-O12 | Rollback may abandon later consultation history and blocks abandoned packages/proposals | Archive/restored assertions |
| P2-O13 | One-completed-rollback rule and evidence retention remain unchanged | ADR 0007 tests on schema-v2 |
| P2-O14 | Pending repair and retention reconciliation preserve consultation rows/provenance | Cross-boundary tests |

## P. Explicit absence

| ID | Protected requirement | Required evidence |
| --- | --- | --- |
| P2-P01 | No live API, HTTP client, provider SDK, or chat automation exists | Source/import/runtime inspection |
| P2-P02 | No free-form human/model text is accepted | Parser rejection |
| P2-P03 | No memory, skill, training, source, or test generation exists | Surface inspection |
| P2-P04 | No arbitrary code, SQL, shell, tool, path, URL, credential, or executable payload is accepted | Adversarial corpus |
| P2-P05 | No continuous or always-on loop exists | CLI/runtime surface |
| P2-P06 | No personality, emotion, affection, mood, or virtual-pet state exists | Schema/report inspection |
| P2-P07 | No proposal enters the existing action selector in the first implementation | Selector guard |

## Acceptance and audit rule

The independent Phase 2.0 design audit at PR #60 head `8cfd65d6e6b153a9dd028333ddf898e7dd4b0647` concluded:

> Phase 2.0 Consultation Boundary is ready after specified documentation or test-matrix corrections.

This accepted matrix incorporates the required corrections for:

- exact zero-caregiver projection rules
- exact proposal schemas and inherited expiry
- exact digest preimages and lineage 64 KiB formula
- real request-wake storage-boundary evidence

The implementation Issue must map every slice to matrix IDs. No test may weaken or condition the 152-test Phase 1 baseline.

A separate independent read-only Phase 2 implementation audit is required only after all accepted matrix requirements have protected evidence and one exact CI-green implementation candidate is ready to freeze.
