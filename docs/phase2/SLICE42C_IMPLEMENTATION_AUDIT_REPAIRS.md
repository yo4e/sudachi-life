# Slice 42c: Phase 2 Implementation-Audit Repairs

Status: **Finding 4 repair complete; final focused closure audit pending**.

## Gate origin

The single independent read-only Phase 2 implementation audit in Issue #120 inspected exact candidate `44e363e874679537fef43d9f78e382ecf5dc5d3e` and concluded:

> not ready to freeze; specified repairs required

Issue #121 owns the accepted repairs. The findings did not change the accepted ADR 0008–0016 or Consultation Protocol v1 meanings, the frozen Phase 1 control, writer authority, resource limits, or authorized capabilities.

## Exact repaired implementation boundary

- audited candidate: `44e363e874679537fef43d9f78e382ecf5dc5d3e`;
- repair implementation head: `6cc312a4e2ac64f866babe7cbab44aca8493b24d`;
- isolated green repair run: GitHub Actions repair-driver run 14;
- protected suite at that head: **381 tests passed**;
- ordinary CI evidence head: `579e7098e66b679c5d69baa8290e452e4ab10db6`;
- ordinary GitHub Actions run 636: `381 passed in 52.21s`;
- install, source/test compilation, protected-test enforcement, and schema-v1 genesis CLI smoke: passed;
- original 152 Phase 1 tests: unchanged;
- temporary repair and closeout scripts and workflows: absent from the repaired candidate;
- durable evidence closeout head: `6546c079520981e99668dd4ed1c46473d503cc73`.

The repaired candidate remains on PR #119 and is not merged. Issue #61 and Issue #121 remain open. Phase 2 is not frozen.

## Accepted repair 1: closed fixture execution surface

The public `perform_fixture_dispatch` signature no longer accepts `fixture_runner` or any other caller-supplied callable. Production execution is bound to exact `run_deterministic_fixture(request_envelope, fixture_case_id)`.

The existing protected fault seam remains a closed string-valued test surface. It cannot select arbitrary code. Protected cases cover precommit rollback, post-commit lock release, caught deterministic-fixture failure, and process exit after committed admission.

Protected evidence verifies:

- the public signature has no callable execution parameter;
- the production module contains no `fixture_runner` route;
- passing `fixture_runner=` raises `TypeError` before runtime access;
- fixture execution still occurs only after the dispatch, charge, and admission event commit and after SQLite ownership is released.

## Accepted repair 2: caught fixture failure terminalization

A caught deterministic-fixture exception, non-bytes return, or oversize return is terminalized through the existing accepted `fixture_output_invalid` branch.

The repair preserves the committed conservative charge and writes exactly:

- one `consultation_dispatch_terminal` row;
- one `consultation_cost_completion` row;
- one `consultation_dispatch_terminalized` event.

The public call then raises `FixtureExecutionError`. Repeating the same dispatch reads no clock, invokes no fixture, adds no row or event, and performs no refund or retry.

The intentionally abrupt protected `exit_after_admission` process boundary remains outside `Exception` handling. It preserves the accepted interrupted-dispatch reconciliation case without reintroducing a callable seam.

## Accepted repair 3: stable maintenance ingress and terminalization

Consultation ingress and terminalization now admit the two accepted stable evidence-recording states, always with no checkpoint pending:

- `sleeping` with no maintenance reason;
- `maintenance_required` with an existing canonical maintenance reason.

They continue to reject pending checkpoint, rollback, quarantine, malformed state, sleeping-with-reason, and maintenance-without-reason cases.

Successful ingress and terminalization preserve status, maintenance reason, consecutive failure count, lifecycle number, garden state, and the existing authority boundary.

## Accepted repair 4: exact stable-checkpoint validation before dispatch mutation

Dispatch admission now validates the selected stable checkpoint directory before reading the dispatch clock or writing any consultation state.

The validation binds:

- checkpoint directory and manifest structure;
- checkpoint ID;
- organism ID;
- lineage generation;
- event boundary;
- database SHA-256;
- database size;
- manifest SHA-256;
- checkpoint registry row;
- SQLite integrity and canonical checkpoint state through the existing checkpoint validator.

One-at-a-time protected corruptions cover database bytes, manifest bytes, database digest, database size, lineage, event boundary, and checkpoint ID. Every case fails with zero clock reads and zero dispatch, charge, terminal, completion, or terminal-event effects.

## Retained audited body

The exact pre-repair dispatch source bytes are retained outside the installed package at:

`docs/phase2/retained/phase2_dispatch_runtime_impl.py`

Protected evidence fixes their SHA-256 to:

`ed573180a7017b9ec8b1002ec59f2376e90653ee8a4013f8b24775a80a0f80ac`

The retained file is evidence only. It is not imported, installed, or executed.

## Capability and authority boundary

These repairs add no live caregiver, model API, human chat, network, subprocess, arbitrary code, memory, skill, training, continuous loop, personality/emotion state, action adoption, or proposal-to-Phase-1-selector route.

Canonical writer categories remain exactly `organism` and `administration`. Fixture identity remains untrusted provenance only.

## Required next gate

Because Issue #120 directly blocked the Phase 2 completion gate and the repairs touch capability, persistence, checkpoint, and terminalization boundaries, `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md` requires one focused read-only completion re-audit at the final exact repair candidate.

The commit containing this final evidence synchronization is the proposed re-audit candidate. Its exact SHA and ordinary CI run are fixed in the focused re-audit Issue. Do not modify or merge that candidate while the re-audit is running.

Do not merge PR #119, close Issue #61 or Issue #121, or declare Phase 2 frozen until the focused re-audit conclusion is satisfactory.

## Focused re-audit and remaining Finding 4 closure

Issue #122 independently audited exact candidate `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`. It confirmed Findings 1–3 fully resolved, but found that Finding 4 was only partially closed: a coherently relinked checkpoint belonging to another organism and a manifest containing an undeclared field could still pass dispatch admission, and the selected snapshot was not required to contain the exact active request row/event.

Issue #123 closes that gap only in `phase2_dispatch_runtime.py`; the shared frozen Phase 1 checkpoint validator remains unchanged.

The Phase 2 admission check now requires:

- the exact 18-field checkpoint manifest set;
- manifest/snapshot organism identity equal to the active organism and request;
- byte-equivalent canonical request envelope and complete request-row equality between active and snapshot databases;
- complete equality of the linked `consultation_request_created` event between active and snapshot databases;
- all previously accepted ID, lineage, boundary, digest, size, registry, SQLite integrity, canonical-state, store, working-set, and pre-mutation checks.

New coherent adversarial regressions cover wrong-organism artifact substitution, an undeclared manifest field with a matching registry SHA, a missing snapshot request row, and a mismatched snapshot request event. Each rejects before clock read with zero dispatch, charge, admission event, terminal, completion, or fixture effect.

Exact implementation head: `9814908aae2646f4c09142030b7381e5f9a1394b`. Strict validation: `385 passed in 54.25s`, plus install and source/test compilation. All temporary repair helpers/workflows are absent from the implementation head.

One final focused read-only closure audit is required before merge or Phase 2 freeze.



## Interim closure audit and request-event semantic repair

Issue #124 began the final closure audit at `b0ac020dee450238b4267b76eb59addef036618c`. Its interim record independently confirmed all prior demonstrated checkpoint-linkage reproductions closed and Findings 1–3 remained closed, but found one medium semantic-linkage defect.

The active and selected-checkpoint `consultation_request_created` event rows were required to equal each other, yet neither row was independently reconstructed from the validated request. Coherent mutation of both rows' payload, source, or lineage could therefore pass dispatch admission.

Issue #125 closes that gap only in the Phase 2 dispatch admission boundary. The shared frozen Phase 1 checkpoint validator remains unchanged. The exact request-created event is reconstructed from the validated request row/envelope and binds event sequence, organism, lineage, lifecycle, event type, protected source, canonical payload and size, schema, environment, and budget. Both active and checkpoint rows must independently match before complete row equality is accepted.

Protected regressions coherently mutate payload, source, lineage, lifecycle, schema, environment, budget, type, and organism in both databases; missing event evidence is rejected through canonical foreign-key validation. Every case fails before clock read with zero consultation or fixture effects.

Exact implementation head: `3ddf1116b0aecc4842d257131e3e62481729db58`. Strict isolated verification: `395 passed in 49.62s`, plus install and source/test compilation. Temporary repair infrastructure is absent after cleanup.

A final focused independent read-only closure audit remains required before PR #119 may merge or Phase 2 may freeze.
