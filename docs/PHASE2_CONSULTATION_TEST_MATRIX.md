# Phase 2 Consultation Boundary Test Matrix

Status: **Proposed design targets; no Phase 2 implementation exists yet**

This matrix maps proposed ADR 0008 and `docs/phase2/CONSULTATION_PROTOCOL_V1.md` to the protected tests required before deterministic fixture plumbing can be accepted.

The complete Phase 1 suite remains unchanged and is the first regression layer.

## A. Frozen Phase 1 baseline

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-A01 | All 152 Phase 1 tests remain unchanged and passing against schema-v1 | Run existing suite without skips, conditionals, caregiver imports, or changed assertions |
| P2-A02 | Schema-v1 initialization, CLI, checkpoint, rollback, authority, and budgets remain supported | Existing Phase 1 tests continue to own those paths |
| P2-A03 | Phase 2 modules add no network, subprocess, arbitrary-code, or external-workspace path to Phase 1 action execution | Re-run guarded action and no-external-workspace tests with Phase 2 package installed |
| P2-A04 | Base contract version remains `0.2`; schema-v2 is an explicit extension | Exact version assertions and no silent Contract v0.2 reinterpretation |

## B. Schema-v2 initialization and exact validation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-B01 | New Phase 2 organisms initialize with schema `2`, protocol `1`, and exactly one accepted Phase 2 budget config | Parameterized exact initialization assertions |
| P2-B02 | `phase2-zero-caregiver-v1` and `phase2-fixture-v1` are distinct protected configurations | Unknown or mixed values fail closed |
| P2-B03 | All original Phase 1 tables, columns, actions, evaluators, and seed rows remain exact | Protected Phase 1 fingerprint subset comparison |
| P2-B04 | No new column is added to an original Phase 1 table | Exact schema introspection |
| P2-B05 | Consultation tables, indexes, uniqueness rules, foreign keys, and no-update/no-delete triggers are exact | Corrupt each object and require active/checkpoint validation failure |
| P2-B06 | Operational consultation tables are empty at genesis | Exact row and sequence assertions |
| P2-B07 | Genesis becomes checkpoint-stable before wakeable | Existing boundary plus schema-v2 validation |
| P2-B08 | Schema-v1 is never auto-migrated by status, garden wake, disposition wake, dispatch, ingress, or reconciliation | Byte/canonical/artifact identity after rejection |
| P2-B09 | No migration or downgrade command exists | CLI and public API surface assertion |

## C. Zero-caregiver control

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-C01 | Zero-caregiver config creates no request in `no_applicable_action` | Ordinary Phase 1 abstention result and exact empty consultation state |
| P2-C02 | Zero config admits no dispatch, fixture, response, proposal, disposition, terminal outcome, or cost | Exact empty tables and guarded adapter non-import/non-invocation |
| P2-C03 | Zero config emits no consultation event or source | Exact event/source comparison |
| P2-C04 | Phase 1-relevant projection matches schema-v1 under identical declared inputs | Normalize only schema and budget config values; compare every original row/column/payload/sequence |
| P2-C05 | Added empty schema objects are the only schema-v2 byte-level exclusion | Reject extra normalization or any non-empty operational Phase 2 object |
| P2-C06 | Ordinary status, lifecycle, checkpoint, rollback, and authority behavior match Phase 1 | Paired schema-v1/schema-v2 scenarios |

## D. Garden request wake and honest failure accounting

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-D01 | Request is justified only by `no_applicable_action` with incomplete objective | Applicable-action and objective-complete conditions create no request |
| P2-D02 | Garden tick, abstention reason, action/mutation ledgers, and Phase 1 outcome remain unchanged by request creation | Exact Phase 1 core row/event comparison within schema-v2 |
| P2-D03 | Request creation increments `consecutive_failures` exactly once and never resets it | Boundary tests from streak 0 and 1 |
| P2-D04 | A wake that reaches the maintenance threshold creates no request | Start at streak 2; require maintenance, no request, no consultation event |
| P2-D05 | One garden wake creates at most one request and two extra canonical records | Exact record-count boundary |
| P2-D06 | At most one request is outstanding | Second request attempt creates no duplicate and no dispatch work |
| P2-D07 | Lifetime request limit is exactly four | Fifth eligible attempt is typed and creates no request or fixture work |
| P2-D08 | Request ordinal, identity object, envelope bytes, digest, and ID are deterministic | Independent repeated construction |
| P2-D09 | Request ID excludes event sequence without losing linkage | Allocate different hypothetical event sequence and prove identity rule; final envelope links actual event |
| P2-D10 | Request contains only declared observation, objective, actions, permissions, versions, budgets, expiry, and provenance | Reject hidden context, paths, URLs, code, SQL, credentials, or free text |
| P2-D11 | Request row and event commit atomically with garden lifecycle | Inject failure before commit and prove complete rollback |
| P2-D12 | Request wake checkpoints before dispatch is eligible | Dispatch rejects pending checkpoint and accepts only stable boundary |
| P2-D13 | Backward wall time cannot reorder request events or change lifecycle expiry | Exact sequence/lifecycle assertions |
| P2-D14 | Competing and nested garden request wakes remain fail-fast | One winner, one typed rejection, exact wakeability |
| P2-D15 | Garden wakes remain allowed after request creation | Later ordinary wake can change current state without hidden consultation priority |

## E. Dispatch admission and conservative charging

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-E01 | Dispatch admission uses fresh fail-fast `BEGIN IMMEDIATE` | Competing writer and nested admin operation reject before mutation |
| P2-E02 | Admission requires sleeping, stable request checkpoint, current lineage, eligibility, and no earlier dispatch | Parameterized precondition rejection |
| P2-E03 | Dispatch row, protected cost charge, and administrative event commit atomically | Inject pre-commit failure and prove rollback |
| P2-E04 | Fixture is never called before dispatch admission commits | Guard fixture function and force admission commit failure |
| P2-E05 | One dispatch attempt, charged invocation, and work unit are consumed at admission | Exact ledger assertions |
| P2-E06 | Charge remains after process interruption even when fixture completion is unknown | Spawn crash after admission and inspect canonical charge |
| P2-E07 | Repeated admission returns already-admitted state and cannot authorize another fixture call | Guarded second-call test |
| P2-E08 | Admission preserves physical ceilings and 1 MiB next-wake reserve before and after write | Real-size exact-boundary and one-over test |
| P2-E09 | Admission emits no checkpoint and performs no organism action | Registry/artifact/action state exact |

## F. External deterministic fixture boundary

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-F01 | No SQLite write lock is held during fixture execution | Separate writer probe can acquire/fail according to its own transaction, not fixture latency |
| P2-F02 | Fixture receives exactly request envelope and fixture case ID | Signature and guarded capability test |
| P2-F03 | Fixture receives no DB, path, workspace, repository, executor, evaluator, checkpoint, rollback, network, subprocess, or randomness handle | Guarded real fixture path |
| P2-F04 | Identical request bytes and case ID produce identical package bytes | Exact repeated construction |
| P2-F05 | Protocol permits only one charged attempt even though fixture is pure and deterministic | Repeated dispatch path cannot call twice |
| P2-F06 | Fixture case selection is declared and canonical in dispatch provenance | Different cases differ only through declared input |
| P2-F07 | Human minutes, model units, money, and declared latency are always zero | Exact protected cost assertions |

## G. Non-circular identifiers and external package

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-G01 | Request ID uses exact identity fields and excludes request event sequence | Golden identity-object test |
| P2-G02 | Dispatch ID links request, lineage, adapter, case, and ordinal | Golden identity-object test |
| P2-G03 | Proposal ID excludes response ID and uses proposal content | Golden identity-object test |
| P2-G04 | Response ID uses proposal IDs/content digests without requiring final proposal response linkage | Explicit acyclic dependency graph assertion |
| P2-G05 | Final response ID is inserted into proposal linkage before package digest | Golden complete-package bytes/digest |
| P2-G06 | Disposition ID excludes event sequence and includes current-state/evaluator outcome | Golden identity-object test |
| P2-G07 | Identical declared graph produces exact IDs, envelopes, digests, rows, and event payloads | Two independent complete constructions |
| P2-G08 | Any undeclared normalization, omitted field, or changed ordering changes or invalidates the digest | Adversarial canonicalization corpus |

## H. External response authority separation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-H01 | External response contains no writer authority fields | Parser rejects `authority_category` and `authority_source` |
| P2-H02 | External response contains no authoritative budget or cost claims | Parser rejects limit/cost authority fields |
| P2-H03 | Caregiver adapter identity and case are provenance only | Changing them cannot change writer category or permission |
| P2-H04 | `proposals_returned` has exactly one proposal; `unavailable` has none | Exact cardinality tests |
| P2-H05 | Only action_candidate, abstain, and defer proposal types parse | Unknown types reject |
| P2-H06 | No free text, code, SQL, shell, path, URL, credential, tool, permission, migration, rollback, or execution command parses | Adversarial package corpus |

## I. Administrative response ingress

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-I01 | Ingress owns fresh fail-fast `BEGIN IMMEDIATE` | Competing writer and nested admin rejection |
| P2-I02 | Administration independently recomputes every ID, byte count, and package digest | Forged supplied values reject |
| P2-I03 | Ingress validates exact request, dispatch, adapter, fixture case, and current lineage | Unknown/completed/stale linkage rejects |
| P2-I04 | Ingress before expiry succeeds; after expiry fails closed | Exact lifecycle tests with no ambient time |
| P2-I05 | One response maximum per dispatch/request | First succeeds; conflicting second rejects |
| P2-I06 | Byte-identical duplicate package is idempotent | Exact DB/events/artifacts and zero new clock read |
| P2-I07 | Logical request/response/proposal/provenance/total byte limits are exact | Boundary accepted; one byte over rejected |
| P2-I08 | Ingress preserves active DB ceiling, working set, and 1 MiB wake reserve | Real-size predicted/post-write tests |
| P2-I09 | Ingress cannot execute action, change budget/permission/evaluator, clear maintenance, checkpoint, migrate, or roll back | Guarded real ingress path |
| P2-I10 | Response, optional proposal, receipt, measured-byte completion, and event commit atomically | Inject failure before commit |
| P2-I11 | Process exit during ingress releases ownership and restores exact prior state | Spawn crash test |
| P2-I12 | Ingress creates no checkpoint | Registry/artifacts unchanged |
| P2-I13 | Ingress may record already-admitted evidence in maintenance but cannot clear or bypass maintenance | Maintenance-state exact assertions |
| P2-I14 | Unavailable ingress terminalizes request with no proposal, disposition, or retry | Exact state derivation and cost charge |

## J. Dispatch failure, crash, and reconciliation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-J01 | Fixture exception produces one terminal outcome and no retry | Normal command catches and terminalizes |
| P2-J02 | Invalid fixture package fails ingress before mutation, then terminalizes as `fixture_output_invalid` | Two explicit bounded transactions and exact evidence |
| P2-J03 | Expiry after admission but before ingress terminalizes as `expired_before_ingress` | Lifecycle boundary test |
| P2-J04 | Process crash after admission leaves one unresolved charged dispatch | Spawn crash after durable admission |
| P2-J05 | Explicit reconciliation records `dispatch_interrupted` without calling fixture | Guard invocation count and exact terminal row/event |
| P2-J06 | Reconciliation is fail-fast, idempotent, and one-terminal maximum | Competing/repeated calls |
| P2-J07 | No response may ingress after dispatch terminalization | Exact rejection with no mutation |
| P2-J08 | No terminal row may be added after response ingress | Exact rejection |
| P2-J09 | Reconciliation may record evidence in sleeping or maintenance-required but not pending-checkpoint/rollback/quarantine | State matrix |
| P2-J10 | Reconciliation preserves storage reserve and creates no checkpoint | Boundary accounting and artifact assertions |

## K. Explicit consultation disposition wake

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-K01 | Disposition is a separate explicit wake class; garden wake never claims proposal work | API/CLI and cross-queue assertions |
| P2-K02 | Caller choice prevents hidden priority; garden ticks and proposals retain independent deterministic order | Interleaved work tests |
| P2-K03 | Disposition wake uses fresh fail-fast `BEGIN IMMEDIATE` before mutable reads | Competing/nested wake tests |
| P2-K04 | Admission requires schema2, sleeping, no pending checkpoint, fixture config, and queued proposal | Precondition matrix |
| P2-K05 | No-work and maintenance attempts are typed, non-mutating, non-queued, and zero-clock where specified | Exact rejection tests |
| P2-K06 | Selection is oldest ingress event sequence then proposal ID | Reverse physical insertion test |
| P2-K07 | At most one proposal is considered and no garden inbox row is claimed | Exact queue state |
| P2-K08 | Current canonical state overrides stale fixture assumptions | Ordinary garden wake changes state before disposition |
| P2-K09 | Proposal is valid through request `N+2` and rejected at considering lifecycle `N+3` | Exact boundary test |
| P2-K10 | Accepted disposition has no action-selector, action-attempt, garden, inventory, or environment effect | Exact state/effect assertion |
| P2-K11 | Rejected reasons cover expired, stale, unknown action, invalid parameters, permission, budget, contradiction, and provenance | Parameterized evaluator tests |
| P2-K12 | Deferred disposition is final and creates no retry | Later disposition wake cannot reconsider |
| P2-K13 | Clarification requested is final and creates no follow-up request at zero clarification budget | Exact request/dispatch counts |
| P2-K14 | Proposal type defer and disposition deferred remain distinguishable | Exact envelope/evaluator reporting |
| P2-K15 | Lifecycle increments, but Phase 1 garden consecutive failures remain exact | Start at streak 0/1/2 and verify preservation |
| P2-K16 | Disposition row/event/outcome/pending checkpoint commit atomically | Inject pre-commit failure |
| P2-K17 | Successful disposition requires checkpoint stabilization and blocks later wake while pending | Existing pending-checkpoint semantics |
| P2-K18 | Process exit during disposition restores queued undisposed proposal and releases ownership | Spawn crash then normal disposition |
| P2-K19 | Repeated wake cannot create a second disposition/event | Exact idempotence |
| P2-K20 | Maximum permitted disposition wake and checkpoint fit inside preserved 1 MiB reserve | Real-size boundary proof |

## L. Derived request state and limits

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-L01 | Awaiting-dispatch request counts outstanding only through expiry | Exact current-lifecycle derivation |
| P2-L02 | Expired pre-dispatch request no longer blocks a later request | New eligible garden request after expiry |
| P2-L03 | Admitted dispatch remains outstanding after expiry until response or terminal reconciliation | Exact one-outstanding enforcement |
| P2-L04 | Successful response remains outstanding until disposition | Second request blocked |
| P2-L05 | Unavailable response, dispatch terminal, and disposition are terminal states | Exact derived status |
| P2-L06 | No caregiver-writable mutable status flag controls state | Schema and corruption tests |
| P2-L07 | Lifetime limit counts immutable request history including expired/terminal requests | Four-total boundary |

## M. Authority and provenance

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-M01 | Canonical writer categories remain exactly organism and administration | Reject caregiver/evaluator/repository writer labels |
| P2-M02 | Request/disposition sources are protected organism consultation sources | Exact mapping and spoof rejection |
| P2-M03 | Dispatch/ingress/reconciliation sources are protected administration consultation sources | Exact mapping and spoof rejection |
| P2-M04 | External caregiver provenance is visibly separate from ingress writer authority in status/reporting | Non-spoofable report assertions |
| P2-M05 | Complete request→dispatch→response→proposal→receipt→disposition chain is reconstructable | Join and digest verification |
| P2-M06 | Dispatch-terminal path is reconstructable without fabricated response/proposal | Exact chain verification |
| P2-M07 | Every parent event sequence exists, precedes child, and is in current lineage | Corrupt/future/abandoned parent rejection |
| P2-M08 | Every consultation row rejects update/delete | Exact trigger tests |

## N. Budgets and physical storage

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-N01 | Every consultation counter and record cap has exact boundary and one-over behavior | Parameterized config tests |
| P2-N02 | No scalar energy field exists | Schema inspection |
| P2-N03 | Consultation rows and SQLite sidecars count toward active database ceiling and reserve | Real 8 MiB boundary analogous to Phase 1 audit repair |
| P2-N04 | Consultation data/checkpoints/staging/rollback evidence/candidates count toward runtime working set | Aggregate accountant after completed rollback |
| P2-N05 | Rejection has no hidden fixture call, retry, row, event, clock read, or artifact | Exact no-side-effect assertions |
| P2-N06 | Caregiver package cannot alter protected cost or evade charge | Forged cost/budget fields rejected |
| P2-N07 | Conservative pre-charge is never refunded after unavailable, invalid output, expiry, or interruption | Exact ledger history |
| P2-N08 | Core garden records remain at most 16 and request extension at most 2 | Exact maximum record test |

## O. Checkpoint and rollback interactions

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-O01 | Checkpoint validation covers exact schema-v2 objects, links, digests, and immutability | Missing/corrupt object rejection |
| P2-O02 | Request checkpoint preserves outstanding request exactly | Validate checkpoint and restored candidate |
| P2-O03 | Disposition checkpoint preserves complete terminal provenance | Exact linked state |
| P2-O04 | Administrative dispatch/ingress/reconciliation do not create checkpoint boundaries | Registry/artifact assertions |
| P2-O05 | Rollback may abandon later dispatch/response/disposition according to selected checkpoint | Archive and restored-lineage assertions |
| P2-O06 | External package from abandoned lineage cannot ingress into restored lineage | Reject before mutation |
| P2-O07 | Queued proposal from abandoned lineage cannot be disposed in restored lineage | Exact current-lineage validation |
| P2-O08 | Existing one-completed-rollback rule and evidence retention remain unchanged | Re-run ADR 0007 tests on schema-v2 where applicable |
| P2-O09 | Pending checkpoint repair and retention reconciliation preserve consultation rows and provenance | Cross-boundary failure tests analogous to Issue #56 |

## P. Explicit absence tests

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-P01 | No live API, HTTP client, provider SDK, or unattended chat automation exists | Source/import and guarded runtime inspection |
| P2-P02 | No free-form human/model text is accepted | Parser rejection |
| P2-P03 | No memory, skill, training, source-patch, or test-generation path exists | Public API/schema/source inspection |
| P2-P04 | No arbitrary Python, shell, SQL, tool, path, URL, credential, or executable payload is accepted | Adversarial value corpus |
| P2-P05 | No continuous or always-on loop exists | CLI/runtime surface assertion |
| P2-P06 | No personality, emotion, affection, mood, or virtual-pet state exists | Schema/report inspection |
| P2-P07 | No action-candidate proposal enters existing action selection in protocol v1 | Guard selector inputs and exact effects |

## Acceptance rule

The first implementation issue must map every slice to matrix IDs. No test may weaken or condition the 152-test Phase 1 baseline.

Before Phase 2.0 design is accepted, one independent read-only Codex design audit must review the exact draft PR head, proposed ADR 0008, protocol v1, this matrix, Issue #59, and frozen Phase 1 authority, transaction, failure, budget, storage, checkpoint, and rollback boundaries.
