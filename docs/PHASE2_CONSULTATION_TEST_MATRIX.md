# Phase 2 Consultation Boundary Test Matrix

Status: **Proposed design targets; no Phase 2 implementation exists yet**

This matrix maps proposed ADR 0008 and `docs/phase2/CONSULTATION_PROTOCOL_V1.md` to the protected tests required before the first deterministic fixture implementation can be accepted.

The complete Phase 1 suite remains unchanged and is the first regression layer.

## A. Frozen Phase 1 baseline

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-A01 | All 152 Phase 1 tests remain unchanged and passing against schema-v1 organisms | Run the existing suite without skips, conditionals, fixture caregiver imports, or changed assertions |
| P2-A02 | Schema-v1 initialization, CLI behavior, checkpoints, rollback, authority, and budgets remain supported | Exact existing Phase 1 tests continue to own these paths |
| P2-A03 | Phase 2 modules do not introduce network, subprocess, arbitrary-code, or external-workspace capability into Phase 1 action execution | Re-run guarded action and no-external-workspace tests with Phase 2 package installed |

## B. Schema-v2 initialization and validation

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-B01 | New Phase 2 organisms initialize with schema version `2`, protocol version `1`, and budget config `phase2-fixture-v1` | Exact initialization assertions |
| P2-B02 | All Phase 1 protected objects and seed-garden rows remain exact under schema-v2 | Compare the protected Phase 1 fingerprint subset |
| P2-B03 | Consultation tables, indexes, constraints, and no-update/no-delete triggers are exact and protected | Corrupt each required object and require active/checkpoint validation failure |
| P2-B04 | Consultation tables are empty at genesis | Exact row-count assertions |
| P2-B05 | Genesis becomes checkpoint-stable before wakeable | Existing checkpoint boundary plus schema-v2 validation |
| P2-B06 | Schema-v1 organism is never auto-migrated by status, enqueue, wake, fixture dispatch, or ingress | Byte/canonical/artifact identity after rejected Phase 2 operations |
| P2-B07 | No Phase 1-to-Phase 2 migration command exists in the first implementation | CLI and public API surface assertion |

## C. Zero-caregiver control

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-C01 | Consultation lifetime budget zero creates no request | Run the no-applicable-action condition and require ordinary Phase 1 abstention behavior |
| P2-C02 | Zero budget creates no dispatch, response, proposal, disposition, or cost row | Exact empty consultation tables and zero adapter invocation |
| P2-C03 | Zero budget emits no consultation event or consultation source | Exact event/source assertions |
| P2-C04 | Phase 1-relevant canonical projection matches schema-v1 under identical declared inputs | Normalize only declared version fields; compare all original table rows and original SQLite sequences exactly |
| P2-C05 | Empty Phase 2 objects are the only schema-v2 exclusion from byte-level Phase 1 comparison | Reject any extra normalized field or non-empty Phase 2 row |
| P2-C06 | Ordinary status, checkpoint eligibility, and rollback eligibility match the Phase 1 control | Paired schema-v1/schema-v2 scenario assertions |

## D. Request wake

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-D01 | A request is justified only by `no_applicable_action` with an incomplete objective | Applicable-action and objective-complete conditions create no request |
| P2-D02 | One wake creates at most one request | Multiple candidate reasons still produce one immutable row and one event |
| P2-D03 | At most one request is outstanding | A second request attempt abstains or rejects with a typed budget outcome and no duplicate request |
| P2-D04 | Lifetime request limit is exactly four | Fifth request attempt is typed, non-mutating, and consumes no fixture invocation |
| P2-D05 | Request envelope bytes, fields, ordering, and identifier are deterministic | Independent repeated construction yields exact canonical bytes and digest-derived ID |
| P2-D06 | Request contains only declared observation, objective, actions, permissions, versions, budgets, expiry, and provenance | Reject hidden context, paths, URLs, code, SQL, credentials, or free text |
| P2-D07 | Request creation is atomic with its event and lifecycle outcome | Inject failure before commit and prove complete rollback |
| P2-D08 | Request wake checkpoints before fixture execution is eligible | Dispatch rejects while checkpoint is pending and succeeds only after stability |
| P2-D09 | Backward wall time cannot reorder request events or change expiry | Exact event sequences and lifecycle expiry under decreasing wall timestamps |
| P2-D10 | Competing and nested request wakes remain fail-fast | One winner, one typed rejection, exact later wakeability |

## E. External deterministic fixture boundary

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-E01 | Fixture execution begins only after the request transaction and checkpoint are complete | Guard dispatch against open write ownership and pending checkpoint state |
| P2-E02 | No SQLite write lock is held while fixture code executes | Hold a separate writer probe during fixture invocation and require normal fail-fast semantics independent of fixture latency |
| P2-E03 | Fixture receives only the canonical request envelope | Signature and guarded-capability test proves no DB connection, path, workspace, executor, evaluator, or checkpoint handle |
| P2-E04 | Fixture behavior is deterministic from declared case input | Exact repeated response/proposal bytes and identifiers |
| P2-E05 | Fixture invocation and work-unit counters are exactly one per dispatched request | Duplicate dispatch attempt rejects without second invocation |
| P2-E06 | Human minutes, model units, money, and declared latency remain exactly zero | Exact cost-ledger assertions for every fixture case |
| P2-E07 | Fixture unavailable case creates one bounded response and no retry | One `unavailable` response, no proposal, terminal request, exact cost row |

## F. Administrative response ingress

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-F01 | Ingress owns a fresh fail-fast `BEGIN IMMEDIATE` transaction | Competing writer and nested administrative operation reject before mutation |
| P2-F02 | Ingress validates exact request, response, proposal, cost, and protocol versions before mutation | Unknown or malformed version leaves database and artifacts exact |
| P2-F03 | Ingress accepts only the exact outstanding request and current lineage | Unknown request, completed request, and stale lineage reject |
| P2-F04 | Ingress before expiry succeeds; ingress after expiry fails closed | Lifecycle-boundary tests with no ambient time dependence |
| P2-F05 | One response maximum per request | First valid response succeeds; conflicting second response rejects |
| P2-F06 | Byte-identical duplicate response is idempotent | Exact database, canonical projection, events, and artifacts remain unchanged |
| P2-F07 | One proposal maximum and only allowed proposal types | Zero/two proposals or unknown type reject for `proposals_returned` |
| P2-F08 | Request, response, proposal, provenance, and total payload byte limits are exact | Exact boundary accepted; one byte over rejected before mutation |
| P2-F09 | Total consultation canonical payload limit is exactly 64 KiB | Limit-crossing ingress rejects and preserves prior state |
| P2-F10 | Ingress cannot execute action, change budget/permission/evaluator, clear maintenance, checkpoint, migrate, or roll back | Guarded authority test through the real ingress path |
| P2-F11 | Valid ingress writes immutable response/proposal/cost rows and one administrative event atomically | Inject failure before commit and prove complete rollback |
| P2-F12 | Process exit during ingress releases ownership and restores exact prior state | Spawned process crash test |
| P2-F13 | Ingress does not publish a checkpoint | Checkpoint registry/artifacts unchanged until later wake |

## G. Proposal validation and disposition wake

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-G01 | Later wake considers at most one queued proposal | Two independent organisms or staged fixtures prove one-per-wake behavior |
| P2-G02 | Only `action_candidate`, `abstain`, and `defer` are accepted protocol-v1 types | Unknown types fail at ingress or protected evaluation as specified |
| P2-G03 | `action_candidate` may name only an existing allowed action and valid parameters | Unknown action and invalid parameter cases produce `rejected` |
| P2-G04 | Current canonical state overrides stale caregiver assumptions | Mutate state through an ordinary committed path before disposition and require `stale_observation` or `contradictory_state` |
| P2-G05 | Proposal valid through lifecycle `N+2` and expired at `N+3` | Exact lifecycle-boundary assertions |
| P2-G06 | One proposal receives exactly one disposition | Duplicate/repeated wake creates no second disposition or event |
| P2-G07 | `accepted` has no action-selector or garden effect in the first slice | Exact action, garden, inventory, environment, and attempt counters unchanged |
| P2-G08 | `rejected` records exact protected reason and provenance | Cover expired, stale, unknown action, invalid parameters, permission, budget, contradiction, and provenance reasons |
| P2-G09 | `deferred` is final and creates no hidden retry | Later wake does not reconsider the same proposal |
| P2-G10 | `clarification_requested` creates no follow-up request because clarification limit is zero | Exact request count and fixture invocation remain unchanged |
| P2-G11 | Disposition event and row commit atomically with lifecycle accounting | Inject pre-commit failure and prove complete rollback |
| P2-G12 | Disposition wake uses ordinary checkpoint and pending-checkpoint exclusion | Successful disposition stabilizes; later wake rejects while pending |
| P2-G13 | Classified evaluator/action-independent failure uses existing savepoint, failure, maintenance, and checkpoint rules | Fault injection without caregiver authority escalation |
| P2-G14 | Process exit during disposition restores undisposed proposal and releases ownership | Spawned crash followed by one normal disposition |

## H. Authority and provenance

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-H01 | Canonical writer categories remain exactly `organism` and `administration` | Reject caregiver/evaluator/repository labels as event writer categories |
| P2-H02 | Request and disposition sources are protected `organism:consultation.*` sources | Exact source mapping and spoof rejection |
| P2-H03 | Ingress source is protected `administration:consultation.response_ingress` | Exact source mapping and spoof rejection |
| P2-H04 | Caregiver identity is untrusted provenance data, not authority | Changing adapter identity cannot change permissions or writer category |
| P2-H05 | Complete request→response→proposal→disposition linkage is reconstructable | Join and digest verification from final canonical state |
| P2-H06 | Every parent event sequence exists and is ordered before its child | Corrupt or future parent reference rejected |
| P2-H07 | Prior envelopes and dispositions reject update/delete | Exact append-only trigger tests |
| P2-H08 | Public status and reports expose writer authority separately from caregiver provenance | Non-spoofable report assertions |

## I. Budgets and physical storage

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-I01 | Every logical consultation counter has an exact protected limit | Boundary and one-over tests for requests, outstanding work, dispatches, responses, proposals, dispositions, and clarification |
| P2-I02 | No scalar energy field exists | Schema inspection |
| P2-I03 | Consultation rows and SQLite sidecars count toward the existing active-database ceiling and wake reserve | Real-size boundary test analogous to Phase 1 enqueue audit repair |
| P2-I04 | Consultation data, checkpoints, staging, rollback evidence, and candidates count toward the existing runtime working set | Aggregate accountant test after one completed rollback |
| P2-I05 | Budget rejection has no hidden fixture call, clock read, retry, row, event, or artifact | Exact no-side-effect assertions |
| P2-I06 | Cost ledger cannot be altered by caregiver payload to evade configured limits | Invalid cost values reject before mutation |

## J. Checkpoint and rollback interactions

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-J01 | Checkpoint validation covers exact schema-v2 consultation objects and immutable rows | Missing trigger/table/index/linkage causes rejection |
| P2-J02 | A checkpoint after request creation preserves the outstanding request exactly | Validate and restore candidate inspection |
| P2-J03 | A checkpoint after disposition preserves complete provenance and terminal state | Exact request/response/proposal/disposition/cost linkage |
| P2-J04 | Rollback before disposition may restore a state without the later ingress or disposition according to selected checkpoint history | Explicit lineage and abandoned-future evidence assertions |
| P2-J05 | Caregiver response from an abandoned lineage cannot enter or affect the restored lineage | Lineage mismatch rejects before mutation |
| P2-J06 | Existing one-completed-rollback limit and evidence retention remain unchanged | Re-run ADR 0007 tests on schema-v2 organisms where applicable |
| P2-J07 | Pending checkpoint repair and retention reconciliation preserve consultation rows and provenance | Cross-boundary failure tests analogous to Issue #56 repairs |

## K. Explicit absence tests

| ID | Protected requirement | Planned evidence |
| --- | --- | --- |
| P2-K01 | No live API, HTTP client, provider SDK, or unattended chat automation exists | Source/import and guarded runtime assertions |
| P2-K02 | No free-form human/model text is accepted | Envelope parser rejects undeclared text fields |
| P2-K03 | No memory, skill, training, source-patch, or test-generation path exists | Public API, schema, and source inspection |
| P2-K04 | No arbitrary Python, shell, SQL, tools, paths, URLs, or executable payload enters protocol envelopes | Adversarial field/value corpus |
| P2-K05 | No continuous or always-on loop exists | CLI and runtime surface assertion |
| P2-K06 | No personality, emotion, affection, mood, or virtual-pet state is introduced | Schema and public report inspection |

## Acceptance rule

The first implementation issue must map every accepted slice to these IDs. No test may weaken or condition the 152-test Phase 1 baseline.

Before Phase 2.0 design is accepted, one independent read-only Codex design audit must review proposed ADR 0008, the protocol schema, this matrix, Issue #59, and the frozen Phase 1 authority, transaction, budget, checkpoint, and rollback boundaries.
