# Slice 42c: Phase 2 Implementation-Audit Repairs

Status: **repair candidate complete; focused completion re-audit pending**.

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
