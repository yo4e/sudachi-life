from __future__ import annotations

from pathlib import Path


def replace_between(path: str, start: str, end: str, replacement: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    target.write_text(
        text[:start_index] + replacement.rstrip() + "\n\n" + text[end_index:],
        encoding="utf-8",
    )


def replace_to_end(path: str, start: str, replacement: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    start_index = text.index(start)
    target.write_text(text[:start_index] + replacement.rstrip() + "\n", encoding="utf-8")


agents_gate = '''## Open gate

Issue #120 completed the first independent Phase 2 implementation audit at `44e363e874679537fef43d9f78e382ecf5dc5d3e` and found one high and three medium defects. Issue #121 owns those accepted repairs.

Issue #122 completed the focused completion re-audit at `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`. It independently confirmed Findings 1–3 closed and found one remaining medium checkpoint-linkage defect in Finding 4. Issue #123 repaired the exact manifest, active-organism, request-row, and active/snapshot event-equality boundaries without changing the frozen Phase 1 validator.

Issue #124 then began the final closure audit at `b0ac020dee450238b4267b76eb59addef036618c`. Its interim independent record confirmed:

- all prior demonstrated Finding 4 reproductions closed;
- Findings 1–3 remained closed;
- all 47 original Phase 1 Python test/helper blobs remained byte-identical;
- the independent Phase 1 control passed 152 tests;
- the complete candidate passed 385 tests;
- the accepted matrix and evidence map each contained exactly 213 IDs;
- schema-v1 installed CLI support and the explicit capability-absence boundary remained intact.

The interim audit found one additional medium implementation defect: the active and checkpoint `consultation_request_created` rows were required to equal each other but were not independently reconstructed from the validated request. Coherent active-and-snapshot mutations to payload, source, or lineage could therefore pass dispatch admission.

Issue #125 owns the narrow Phase 2-only closure. `phase2_dispatch_runtime.py` now reconstructs the exact request-created event semantics before any dispatch clock read or mutation and independently requires both active and checkpoint rows to match:

- request event sequence, organism, lineage, and lifecycle;
- event type `consultation_request_created`;
- source `organism:consultation.request`;
- exact canonical two-field request payload and canonical size;
- schema version 2, environment `seed-garden-v1`, and budget version `phase1-v1`;
- complete active/snapshot row equality, retaining exact wall-time evidence.

Protected regressions coherently mutate both active and snapshot event payload, source, lineage, lifecycle, schema, environment, budget, type, or organism. A missing request-created event is rejected by canonical foreign-key validation. Every case rejects before clock read with zero dispatch, charge, admission event, terminal, completion, or fixture effect.

Exact Issue #125 implementation head: `3ddf1116b0aecc4842d257131e3e62481729db58`. Strict isolated validation: `395 passed in 49.62s`, plus install and source/test compilation. The shared frozen Phase 1 checkpoint validator and all original Phase 1 test/helper files remain unchanged. Temporary repair infrastructure is absent after cleanup.

PR #119 remains open and unmerged. Issues #61/#121/#123/#124/#125 remain open. Phase 2 is not frozen. Issue #124 is an interim record, not a final conclusion; one final independent read-only closure audit is still required at one exact ordinary-CI-green candidate.

## Exact restart point

1. Reconstruct from PR #119; Issues #61/#120/#121/#122/#123/#124/#125; `docs/phase2/PHASE2_IMPLEMENTATION_EVIDENCE_MAP.md`; and the Slice 42c notes.
2. Treat `3ddf1116b0aecc4842d257131e3e62481729db58` as the request-event semantic repair implementation head and verify only durable documentation closeout follows it before the final audit candidate.
3. Confirm all temporary repair scripts/workflows are absent and all 47 original Phase 1 test/helper blobs remain byte-identical to `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`.
4. Confirm the final candidate is ordinary-CI green with all 395 protected tests and schema-v1 CLI smoke.
5. Request one final focused read-only closure audit against the exact fixed PR #119 head. The reviewer must independently reproduce coherent active/snapshot request-event mutations rather than trusting the new tests.
6. Do not modify or merge the candidate while the audit is running.
7. If the conclusion is satisfactory, merge PR #119, close Issues #125/#123/#121/#61, update final handoff, and freeze Phase 2.
8. Request human confirmation for any new finding that would change contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.'''
replace_between("AGENTS.md", "## Open gate", "## End-of-work protocol", agents_gate)

handoff_tail = '''## Implementation-completion audits and repairs

Issue #120 audited exact candidate `44e363e874679537fef43d9f78e382ecf5dc5d3e` and concluded **not ready to freeze; specified repairs required**. Issue #121 accepted four repairs without changing the accepted contract.

Issue #122 audited `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`, independently confirmed Findings 1–3 closed, and found the remaining Finding 4 checkpoint-linkage defect. Issue #123 repaired exact manifest fields, active organism binding, complete request-row equality, and complete active/snapshot request-event row equality in the Phase 2 dispatch boundary only.

Issue #124 began the final closure audit at `b0ac020dee450238b4267b76eb59addef036618c`. Its interim record confirmed the earlier Finding 4 reproductions closed, Findings 1–3 still closed, the 47 original Phase 1 blobs byte-identical, the independent Phase 1 control at 152 passed, the full candidate at 385 passed, exactly 213 accepted/evidence-map IDs, schema-v1 support, and explicit capability absence.

The interim audit found one medium semantic-linkage gap: coherent mutations to both the active and checkpoint `consultation_request_created` event could pass because the two rows were compared to each other without reconstructing the accepted event from the validated request.

Issue #125 owns the narrow repair. Before any dispatch clock read or mutation, the Phase 2 boundary now reconstructs and checks the exact event sequence, organism, lineage, lifecycle, type, source, canonical request payload/size, schema, environment, and budget semantics against both active and checkpoint rows, then retains complete row equality including wall time.

Protected coherent mutations cover payload, source, lineage, lifecycle, schema, environment, budget, event type, and organism; a missing event is rejected through canonical foreign-key validation. All reject with zero clock, dispatch, charge, admission event, terminal, completion, or fixture effect.

Exact Issue #125 implementation head: `3ddf1116b0aecc4842d257131e3e62481729db58`. Strict isolated verification: `395 passed in 49.62s`, plus install and source/test compilation. The shared frozen Phase 1 checkpoint validator and original Phase 1 tests/helpers are unchanged. Temporary repair helpers/workflows are absent after cleanup.

The repaired candidate adds no live caregiver, model API, human chat, network, subprocess, arbitrary code/callable, memory, skill, training, continuous loop, personality/emotion state, action adoption, or proposal-to-Phase-1-selector route. Writer categories remain exactly `organism` and `administration`.

## Remaining gate

PR #119 remains open and unmerged. Issues #61/#121/#123/#124/#125 remain open. Phase 2 is not frozen. Issue #124 contains an interim finding rather than a final conclusion.

One final focused independent read-only closure audit is required at one exact ordinary-CI-green PR #119 head. It must independently test coherent active-and-snapshot request-event mutations and verify no regression across Findings 1–3 or the complete 213-ID gate.

## Exact restart

1. Read PR #119; Issues #61/#120/#121/#122/#123/#124/#125; the evidence map; and the Slice 42c notes.
2. Verify the final PR candidate contains request-event semantic repair head `3ddf1116b0aecc4842d257131e3e62481729db58` and only durable documentation closeout afterward.
3. Confirm all 395 protected tests pass under ordinary CI, schema-v1 CLI smoke passes, and all temporary helpers/workflows are absent.
4. Confirm all 47 original Phase 1 Python test/helper blobs remain byte-identical and the 152-test control remains green.
5. Request one final focused read-only audit against the exact fixed head.
6. Require a conclusion of `ready to freeze`, `ready to freeze after specified documentation-only corrections`, or `not ready to freeze; specified repairs required`.
7. Do not merge PR #119, close completion Issues, or declare Phase 2 frozen before a satisfactory conclusion.
8. After a satisfactory conclusion, merge PR #119, update final evidence/handoff, close Issues #125/#123/#121/#61, and freeze Phase 2.
9. Request human confirmation for any finding that changes contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.'''
replace_to_end("docs/HANDOFF.md", "## Implementation-completion audits and repairs", handoff_tail)

map_tail = '''## Independent audits and accepted repair supplement

Issue #120 inspected exact candidate `44e363e874679537fef43d9f78e382ecf5dc5d3e` and concluded **not ready to freeze; specified repairs required**. Issue #121 owns its accepted repairs.

Issue #122 inspected exact candidate `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`, independently confirmed Findings 1–3 closed, and found the remaining Finding 4 checkpoint-linkage defect. Issue #123 added `REPAIR-F4` evidence for exact manifest fields, active organism binding, complete request-row equality, complete active/snapshot request-event row equality, coherent wrong-organism and extra-field rejection, and zero partial effects.

Issue #124 began the final closure audit at `b0ac020dee450238b4267b76eb59addef036618c`. Its interim record independently confirmed the Issue #123 reproductions closed, Findings 1–3 remained closed, the 47 original Phase 1 blobs remained byte-identical, the Phase 1 control passed 152 tests, the complete candidate passed 385 tests, and the normative/evidence sets each contained exactly 213 IDs.

The interim audit identified one additional medium gap: active and checkpoint request-created event rows were equal but their semantics were not reconstructed from the validated request. Issue #125 adds `REPAIR-REQUEST-EVENT` evidence without changing any accepted ID or requirement meaning:

- exact reconstruction of event sequence, organism, lineage, lifecycle, type, and source;
- exact canonical payload reconstruction from the validated request envelope and stored canonical size;
- exact schema-v2, `seed-garden-v1`, and `phase1-v1` binding;
- independent active-event and checkpoint-event semantic validation;
- retained complete row equality, including wall-time evidence;
- coherent active-and-snapshot payload/source/lineage/lifecycle/schema/environment/budget/type/organism mutation rejection;
- missing-event rejection through canonical foreign-key validation;
- zero clock, dispatch, charge, admission-event, terminal, completion, or fixture effects.

Exact Issue #125 implementation head: `3ddf1116b0aecc4842d257131e3e62481729db58`. Strict isolated validation: `395 passed in 49.62s`, plus install and source/test compilation. The shared frozen Phase 1 validator and original Phase 1 test/helper blobs remain unchanged. Temporary repair infrastructure is absent after cleanup.

`REPAIR-REQUEST-EVENT` strengthens P2-F02, P2-N02, P2-N07, P2-O20, ADR 0008's stable request-checkpoint admission boundary, and existing authority/checkpoint/no-partial-effect evidence. It adds no live capability, authority, schema, resource, protocol, or Phase 1 behavior.

This map remains an audit input. Issue #124 is an interim audit record, not a final conclusion. One final focused independent read-only closure audit must verify the Issue #125 repair and the complete gate before PR #119 may merge or Issue #61 may close. Phase 2 is not frozen.'''
replace_to_end(
    "docs/phase2/PHASE2_IMPLEMENTATION_EVIDENCE_MAP.md",
    "## Independent audits and accepted repair supplement",
    map_tail,
)

repair_note = Path("docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md")
repair_text = repair_note.read_text(encoding="utf-8")
marker = "## Interim closure audit and request-event semantic repair"
if marker in repair_text:
    raise SystemExit("request-event repair note already present")
repair_text += '''

## Interim closure audit and request-event semantic repair

Issue #124 began the final closure audit at `b0ac020dee450238b4267b76eb59addef036618c`. Its interim record independently confirmed all prior demonstrated checkpoint-linkage reproductions closed and Findings 1–3 remained closed, but found one medium semantic-linkage defect.

The active and selected-checkpoint `consultation_request_created` event rows were required to equal each other, yet neither row was independently reconstructed from the validated request. Coherent mutation of both rows' payload, source, or lineage could therefore pass dispatch admission.

Issue #125 closes that gap only in the Phase 2 dispatch admission boundary. The shared frozen Phase 1 checkpoint validator remains unchanged. The exact request-created event is reconstructed from the validated request row/envelope and binds event sequence, organism, lineage, lifecycle, event type, protected source, canonical payload and size, schema, environment, and budget. Both active and checkpoint rows must independently match before complete row equality is accepted.

Protected regressions coherently mutate payload, source, lineage, lifecycle, schema, environment, budget, type, and organism in both databases; missing event evidence is rejected through canonical foreign-key validation. Every case fails before clock read with zero consultation or fixture effects.

Exact implementation head: `3ddf1116b0aecc4842d257131e3e62481729db58`. Strict isolated verification: `395 passed in 49.62s`, plus install and source/test compilation. Temporary repair infrastructure is absent after cleanup.

A final focused independent read-only closure audit remains required before PR #119 may merge or Phase 2 may freeze.
'''
repair_note.write_text(repair_text, encoding="utf-8")

Path("docs/phase2/SLICE42C_FINAL_CLOSURE_AUDIT.md").write_text(
    '''# Slice 42c Final Closure-Audit Boundary

Status: **request-event semantic repair complete; final independent closure audit pending**.

## Audit history

Issue #120 audited `44e363e874679537fef43d9f78e382ecf5dc5d3e` and found one high and three medium defects. Issue #122 audited `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`, confirmed Findings 1–3 closed, and found the remaining Finding 4 checkpoint-linkage defect. Issue #123 repaired exact manifest, active-organism, request-row, and active/snapshot event-equality boundaries.

Issue #124 began the final closure audit at `b0ac020dee450238b4267b76eb59addef036618c`. Its interim independent record confirmed:

- prior demonstrated Finding 4 reproductions closed;
- Findings 1–3 remained closed;
- 47 original Phase 1 Python test/helper blobs byte-identical;
- independent Phase 1 control: 152 passed;
- independent complete candidate: 385 passed;
- exactly 213 accepted and evidence-map IDs;
- schema-v1 support and explicit capability absence intact.

The interim audit did not issue a final conclusion. It found one additional medium implementation defect: complete active/snapshot request-created event equality did not prove that either event had the accepted semantics.

## Issue #125 semantic closure

Before any dispatch clock read or mutation, the Phase 2 admission boundary now reconstructs the exact expected `consultation_request_created` event from the validated request row and canonical envelope. It independently requires both active and checkpoint event rows to match:

- exact event sequence, organism, lineage, and lifecycle;
- event type `consultation_request_created`;
- source `organism:consultation.request`;
- canonical payload containing exactly the canonical size and request envelope;
- schema version 2, environment `seed-garden-v1`, and budget version `phase1-v1`.

Complete active/snapshot row equality is retained afterward, including exact wall-time evidence. The shared frozen Phase 1 checkpoint validator is unchanged.

Protected coherent mutations cover payload, source, lineage, lifecycle, schema, environment, budget, event type, and organism. A missing request-created event is rejected through canonical foreign-key validation. Every rejection occurs before clock read and leaves zero dispatch, charge, admission event, terminal, completion, or fixture effects.

## Exact implementation evidence

- Issue #125 implementation head: `3ddf1116b0aecc4842d257131e3e62481729db58`;
- strict isolated verification: `395 passed in 49.62s`;
- package installation and source/test compilation: passed;
- shared frozen Phase 1 validator: unchanged;
- original Phase 1 tests/helpers: unchanged;
- temporary repair infrastructure: absent after cleanup;
- PR #119: open and unmerged;
- Phase 2: not frozen.

The exact final audit candidate is the ordinary-CI-green commit containing this evidence synchronization. Do not modify or merge that candidate, close completion Issues, or declare Phase 2 frozen while the final independent audit is running.
''',
    encoding="utf-8",
)
