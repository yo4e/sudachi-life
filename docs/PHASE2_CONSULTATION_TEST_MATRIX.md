# Phase 2 Consultation Boundary Test Matrix

Status: **Proposed design targets; no Phase 2 implementation exists yet**

This matrix maps proposed ADR 0008 and `docs/phase2/CONSULTATION_PROTOCOL_V1.md` to protected tests required before deterministic fixture plumbing can be accepted.

The complete Phase 1 suite remains unchanged and is the first regression layer.

## A. Frozen Phase 1 baseline

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-A01 | All 152 Phase 1 tests remain unchanged and passing against schema-v1 | Existing suite without skips, conditionals, caregiver imports, or assertion changes |
| P2-A02 | Schema-v1 initialization, CLI, checkpoints, rollback, authority, and budgets remain supported | Existing Phase 1 tests own these paths |
| P2-A03 | Phase 2 modules add no network, subprocess, arbitrary-code, or workspace route to Phase 1 action execution | Re-run guarded action tests with Phase 2 package installed |
| P2-A04 | Base contract remains `0.2`; schema-v2 is an explicit extension | Exact version assertions |

## B. Schema-v2 initialization and validation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-B01 | Schema-v2 and protocol-v1 initialize with exactly one accepted Phase 2 budget configuration | Parameterized initialization |
| P2-B02 | Zero-caregiver and fixture configurations are distinct and protected | Unknown and mixed configurations reject |
| P2-B03 | Original Phase 1 tables, columns, actions, evaluators, and seed rows remain exact | Protected fingerprint subset |
| P2-B04 | No new column is added to an original Phase 1 table | Schema introspection |
| P2-B05 | Consultation tables, indexes, keys, triggers, and immutable constraints are exact | Corrupt each object and reject active/checkpoint validation |
| P2-B06 | Operational consultation tables and their sequences are empty at genesis | Exact row and sequence assertions |
| P2-B07 | Genesis becomes checkpoint-stable before wakeable | Schema-v2 checkpoint test |
| P2-B08 | Schema-v1 is never auto-migrated by any Phase 2 operation | Exact rejected-state identity |
| P2-B09 | No migration or downgrade command exists in the first implementation | API and CLI surface assertion |

## C. Zero-caregiver control

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-C01 | Zero configuration creates no request on a no-applicable-action wake | Exact ordinary abstention and empty Phase 2 state |
| P2-C02 | No dispatch, fixture, response, proposal, disposition, terminal, or cost occurs | Empty tables and guarded adapter |
| P2-C03 | No consultation event or source is emitted | Exact history |
| P2-C04 | The Phase 1-relevant projection matches schema-v1 | Normalize only schema/budget config; compare every original row, column, payload, and sequence |
| P2-C05 | Empty added objects are the only byte-level exclusion | Reject extra normalization or non-empty operation objects |
| P2-C06 | Status, lifecycle, checkpoint, rollback, and authority behavior match Phase 1 | Paired scenarios |

## D. Garden request wake and failure honesty

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-D01 | Request is created only for incomplete-objective `no_applicable_action` | Applicable-action and objective-complete paths create none |
| P2-D02 | Tick, abstention, action, mutation, and core outcome remain unchanged | Exact Phase 1 core comparison |
| P2-D03 | Failure streak increments exactly once and never resets because of request creation | Streak boundary tests |
| P2-D04 | A maintenance-entering wake creates no request | Start at streak two; require maintenance and no consultation event |
| P2-D05 | At most one request and two additional records are created in one wake | Exact record count |
| P2-D06 | At most one current-lineage request is outstanding | Second attempt creates no duplicate |
| P2-D07 | The current lineage permits exactly four requests | Fifth attempt is typed and non-mutating |
| P2-D08 | Request ordinal equals current-lineage request count plus one | Old-lineage rows ignored after rollback |
| P2-D09 | Request identity object, envelope, digest, and identifier are deterministic | Independent construction |
| P2-D10 | Request ID excludes event sequence while final envelope links the actual event | Golden construction test |
| P2-D11 | Request contains only declared typed context | Adversarial forbidden-field corpus |
| P2-D12 | Request row, event, and core lifecycle commit atomically | Pre-commit fault injection |
| P2-D13 | Request checkpoint is stable before dispatch admission | Pending rejection and stable acceptance |
| P2-D14 | Backward wall time cannot affect order or expiry | Exact event sequence and lifecycle boundary |
| P2-D15 | Competing and nested garden wakes fail fast | Real connections and subprocesses |
| P2-D16 | Later garden wakes remain allowed while a request is outstanding | State may diverge without hidden proposal priority |

## E. Dispatch admission and conservative charging

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-E01 | Dispatch uses a fresh fail-fast administrative transaction | Competing and nested rejection |
| P2-E02 | Admission requires sleeping, stable checkpoint, current lineage, valid expiry, and no prior dispatch | Precondition matrix |
| P2-E03 | Dispatch, cost charge, and administrative event commit atomically | Fault injection |
| P2-E04 | Fixture is never called before dispatch admission commits | Guard plus forced commit failure |
| P2-E05 | One dispatch attempt, invocation charge, and work-unit charge are recorded at admission | Exact ledger |
| P2-E06 | Charge remains after process interruption | Spawned process crash |
| P2-E07 | Repeated admission never authorizes a second fixture invocation | Guarded call count |
| P2-E08 | Four charges are permitted per lineage; the fifth is blocked | Epoch boundary |
| P2-E09 | Predicted and post-write accounting preserve the 1 MiB reserve | Real-size boundary |
| P2-E10 | Admission creates no checkpoint and no action effect | Registry and action state exact |

## F. External deterministic fixture boundary

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-F01 | No SQLite write lock is held during fixture execution | Independent writer probe |
| P2-F02 | Fixture receives exactly the request envelope and declared case identifier | Signature guard |
| P2-F03 | Fixture receives no DB, path, workspace, repository, executor, evaluator, checkpoint, rollback, network, subprocess, or randomness capability | Guarded real path |
| P2-F04 | Identical request and case produce identical bytes | Exact repeated construction |
| P2-F05 | Deterministic purity cannot bypass the single charged invocation | Dispatch guard |
| P2-F06 | The returned package remains noncanonical until ingress | Database exact before ingress |
| P2-F07 | Fixture case is declared in dispatch provenance | Case-variation assertions |
| P2-F08 | Human, model, money, and declared-latency values remain zero | Protected cost assertions |

## G. Acyclic identifiers and canonical encoding

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-G01 | Request identity is exact and event-sequence exclusion is explicit | Golden identity object |
| P2-G02 | Dispatch identity is exact | Golden identity object |
| P2-G03 | Proposal ID excludes response ID | Golden identity object |
| P2-G04 | Response ID uses already-derived proposal IDs and content digests without a cycle | Dependency graph assertion |
| P2-G05 | Response ID is inserted before final package digest | Golden bytes |
| P2-G06 | Disposition ID excludes the later event sequence | Golden identity object |
| P2-G07 | The complete graph is reproducible from identical declared inputs | Two independent builds |
| P2-G08 | Undeclared normalization or ordering changes invalidate the digest | Canonicalization corpus |

## H. External package authority separation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-H01 | External response contains no canonical writer authority | Reject undeclared authority fields |
| P2-H02 | External response contains no authoritative budget or cost | Reject forged accounting fields |
| P2-H03 | Adapter and case provenance cannot change writer category or permission | Spoof tests |
| P2-H04 | Successful response has exactly one proposal; unavailable has none | Cardinality tests |
| P2-H05 | Only `action_candidate`, `abstain`, and `defer` are accepted | Unknown type rejection |
| P2-H06 | No free text, code, SQL, shell, path, URL, credential, tool, or authority command is accepted | Adversarial corpus |

## I. Administrative response ingress

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-I01 | Ingress owns a fresh fail-fast administrative transaction | Competing and nested rejection |
| P2-I02 | Administration recomputes identifiers, canonical bytes, and package digest | Forgery rejection |
| P2-I03 | Exact current-lineage request, dispatch, adapter, and case linkage is required | Unknown and stale rejection |
| P2-I04 | Ingress is allowed only in declared durable states and never behind pending checkpoint, rollback, or quarantine | State matrix |
| P2-I05 | Ingress before expiry succeeds and after expiry fails | Lifecycle boundary |
| P2-I06 | At most one response exists per dispatch | Conflict rejection |
| P2-I07 | Byte-identical duplicate ingress is idempotent | Database, event, artifact, and clock identity |
| P2-I08 | Logical and per-lineage byte limits are exact | Boundary and one-over tests |
| P2-I09 | Physical database, working-set, and reserve limits are exact | Real-size test |
| P2-I10 | Ingress cannot execute an action, change authority, clear maintenance, checkpoint, migrate, or roll back | Guarded real path |
| P2-I11 | Response, proposal, receipt, measured cost completion, and event commit atomically | Fault injection |
| P2-I12 | Process exit rolls back ingress and releases ownership | Spawned process crash |
| P2-I13 | Ingress publishes no checkpoint | Registry and artifacts exact |
| P2-I14 | Evidence recording while maintenance is active cannot clear maintenance | Exact status |
| P2-I15 | Unavailable response terminalizes without proposal, disposition, or retry | Derived-state assertion |
| P2-I16 | Busy or pending-checkpoint rejection permits explicit same-byte resubmission without fixture recall | Two bounded ingress attempts and one charge |

## J. Dispatch terminalization and reconciliation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-J01 | Fixture exception produces one terminal outcome and no retry | Normal administrative workflow |
| P2-J02 | Invalid package is rejected then terminalized as invalid through an explicit operation | Separate operation assertions |
| P2-J03 | Expiry after admission produces `expired_before_ingress` terminal outcome | Lifecycle crossing |
| P2-J04 | Crash after admission leaves a charged unresolved dispatch | Spawned process crash |
| P2-J05 | Explicit reconciliation records interruption without invoking the fixture | Guarded call count |
| P2-J06 | Reconciliation is fail-fast, idempotent, and creates at most one terminal row | Competing and repeated attempts |
| P2-J07 | No response may be ingressed after terminalization | Rejection |
| P2-J08 | No terminal row may be added after accepted response ingress | Rejection |
| P2-J09 | Terminalization is restricted to declared durable states and no pending, rollback, or quarantine | State matrix |
| P2-J10 | Current lineage is required | Abandoned dispatch rejection |
| P2-J11 | Reserve is preserved and no checkpoint is created | Accounting and artifact assertions |

## K. Explicit disposition wake

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-K01 | Disposition is a separate explicit work class; garden wake never claims a proposal | API and queue test |
| P2-K02 | Caller selection prevents hidden garden-versus-proposal priority | Interleaved queues |
| P2-K03 | Disposition uses a fresh fail-fast wake transaction | Competing and nested rejection |
| P2-K04 | Schema-v2, sleeping, no pending checkpoint, fixture configuration, and queued current-lineage proposal are required | Admission matrix |
| P2-K05 | No-work and maintenance attempts are typed, non-mutating, non-queued, and consume no undeclared clocks | Exact rejection |
| P2-K06 | Selection is oldest ingress event sequence then proposal identifier | Reverse insertion |
| P2-K07 | At most one proposal is considered and no garden input is claimed | Queue exact |
| P2-K08 | Current state overrides fixture assumptions | Garden change before disposition |
| P2-K09 | Proposal is valid through `N+2` and rejected at considering lifecycle `N+3` | Exact boundary |
| P2-K10 | Accepted disposition has no selector, action, or garden effect | Exact state |
| P2-K11 | Rejected reason codes are protected and complete | Parameterized evaluator |
| P2-K12 | Deferred is final and creates no retry | Later wake |
| P2-K13 | Clarification is final and creates no follow-up request | Counts exact |
| P2-K14 | Proposal type `defer` and disposition `deferred` remain distinguishable | Reports and envelopes |
| P2-K15 | Lifecycle increments while Phase 1 garden failure streak is preserved | Streak boundaries |
| P2-K16 | Disposition, event, outcome, and pending-checkpoint boundary commit atomically | Fault injection |
| P2-K17 | Checkpoint stabilization and pending-checkpoint exclusion remain unchanged | Existing semantics |
| P2-K18 | Process exit restores the queued proposal and releases ownership | Spawned crash |
| P2-K19 | Repeated wake cannot create a duplicate disposition or event | Idempotence |
| P2-K20 | Maximum disposition wake and checkpoint fit inside the inherited reserve | Real-size proof |

## L. Current-lineage state and rollback epoch

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-L01 | Awaiting-dispatch request counts outstanding only through expiry | Lifecycle derivation |
| P2-L02 | Expired pre-dispatch request no longer blocks a new request | Later request |
| P2-L03 | Admitted dispatch remains outstanding until response or terminalization | Expiry crossing |
| P2-L04 | Successful response remains outstanding until disposition | Second-request rejection |
| P2-L05 | Unavailable, terminal, and disposition states are final | Derived-state assertions |
| P2-L06 | No caregiver-writable mutable status flag exists | Schema and corruption tests |
| P2-L07 | Four requests, charges, and 64 KiB payload apply per current lineage | Boundary tests |
| P2-L08 | Rollback increments lineage and old consultation rows become historical and inactive | Restored-candidate test |
| P2-L09 | New lineage begins a fresh four-call epoch | Post-rollback request boundary |
| P2-L10 | ADR 0007 bounds one physical organism to at most eight charged fixture invocations | One rollback followed by second-rollback rejection |
| P2-L11 | Old-lineage unresolved dispatch requires no current reconciliation and cannot block a current request | State derivation |

## M. Authority and provenance

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-M01 | Writer categories remain exactly organism and administration | Reject caregiver, evaluator, and repository writer labels |
| P2-M02 | Request and disposition use protected organism sources | Exact mapping and spoof rejection |
| P2-M03 | Dispatch, ingress, and terminalization use protected administration sources | Exact mapping and spoof rejection |
| P2-M04 | Caregiver provenance is reported separately from ingress writer authority | Non-spoofable output |
| P2-M05 | Request-to-dispatch-to-response-to-proposal-to-receipt-to-disposition linkage is reconstructable | Join and digest verification |
| P2-M06 | Terminal path is reconstructable without inventing response or proposal rows | Provenance chain |
| P2-M07 | Parent events exist, precede children, and belong to the correct lineage | Corrupt, future, and old-lineage rejection |
| P2-M08 | Every consultation row rejects update and delete | Trigger tests |

## N. Budgets and physical storage

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-N01 | Every counter and record cap is exact | Boundary and one-over tests |
| P2-N02 | No scalar energy field exists | Schema inspection |
| P2-N03 | Consultation rows and SQLite sidecars count toward active ceiling and reserve | Real 8 MiB boundary |
| P2-N04 | Consultation data, checkpoints, staging, rollback evidence, and candidates count toward the working set | Aggregate accounting after rollback |
| P2-N05 | Rejection has no hidden fixture call, retry, row, event, clock, or artifact | Exact no-effect assertions |
| P2-N06 | Caregiver package cannot alter protected cost | Forged field rejection |
| P2-N07 | Pre-charge is never refunded after unavailable, invalid, expiry, or interruption | Ledger assertions |
| P2-N08 | Phase 1 core records remain at most 16 and request extension at most two | Maximum record test |
| P2-N09 | The 64 KiB logical total is per lineage and resets only on lineage change | Boundary plus rollback |

## O. Checkpoint and rollback interactions

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-O01 | Checkpoint validation covers exact schema-v2 objects, links, digests, and immutability | Corruption rejection |
| P2-O02 | Request checkpoint preserves the exact request | Restore inspection |
| P2-O03 | Disposition checkpoint preserves terminal provenance | Exact linkage |
| P2-O04 | Administrative operations create no checkpoint | Registry and artifacts |
| P2-O05 | Rollback may abandon later consultation history | Archive and restored-state assertions |
| P2-O06 | Abandoned-lineage package cannot ingress | Pre-mutation rejection |
| P2-O07 | Abandoned-lineage proposal cannot be disposed | Current-lineage filter |
| P2-O08 | One-completed-rollback rule and evidence retention remain unchanged | ADR 0007 tests on schema-v2 |
| P2-O09 | Pending repair and retention reconciliation preserve consultation rows and provenance | Cross-boundary tests |

## P. Explicit absence

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-P01 | No live API, HTTP client, provider SDK, or chat automation exists | Source, import, and runtime inspection |
| P2-P02 | No free-form human or model text is accepted | Parser rejection |
| P2-P03 | No memory, skill, training, source, or test generation path exists | Surface inspection |
| P2-P04 | No arbitrary code, SQL, shell, tool, path, URL, or credential is accepted | Adversarial corpus |
| P2-P05 | No continuous or always-on loop exists | CLI and runtime surface |
| P2-P06 | No personality, emotion, affection, mood, or virtual-pet state exists | Schema and report inspection |
| P2-P07 | No proposal enters the existing action selector in the first implementation | Selector guard |

## Acceptance and audit rule

The design is accepted through ordinary repository review of Issue #59, ADR 0008, protocol v1, and this matrix.

The Phase 2 implementation Issue must map every slice to matrix IDs. No test may weaken or condition the 152-test Phase 1 baseline.

Do not run a separate Codex design audit. Run one independent read-only Codex audit only after the complete Phase 2 implementation is finished, all accepted matrix requirements have protected evidence, the unchanged Phase 1 suite passes, and one exact CI-green candidate is ready to be judged for freezing.