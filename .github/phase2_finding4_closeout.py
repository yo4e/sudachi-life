from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_region(path: Path, start_marker: str, end_marker: str | None, replacement: str) -> None:
    text = path.read_text(encoding='utf-8')
    start = text.index(start_marker)
    if end_marker is None:
        updated = text[:start] + replacement.rstrip() + '\n'
    else:
        end = text.index(end_marker, start)
        updated = text[:start] + replacement.rstrip() + '\n\n' + text[end:]
    path.write_text(updated, encoding='utf-8')


agents = ROOT / 'AGENTS.md'
replace_region(
    agents,
    '## Open gate\n',
    '## End-of-work protocol\n',
    '''## Open gate

Issue #120 completed the first independent Phase 2 implementation audit at `44e363e874679537fef43d9f78e382ecf5dc5d3e` and found one high and three medium defects. Issue #121 owns those accepted repairs.

Issue #122 completed the focused completion re-audit at `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`. It independently confirmed Findings 1–3 closed, all 47 original Phase 1 test/helper blobs byte-identical, the 152-test Phase 1 control green, and the full 381-test suite green. It found one remaining medium defect in Finding 4: dispatch did not yet bind the stable checkpoint to the active organism, exact manifest field set, and exact request row/event snapshot.

Issue #123 owns the narrow Phase 2-only closure. PR #119 now contains:

- exact checkpoint manifest field-set enforcement;
- active organism/request-to-manifest binding;
- exact active request row/envelope equality against the selected checkpoint snapshot;
- exact `consultation_request_created` event equality against the snapshot;
- coherent wrong-organism, extra-field, missing-request, and event-mismatch regressions;
- zero clock and zero dispatch/charge/terminal/completion/event effects on every new rejection.

The shared frozen Phase 1 checkpoint validator remains unchanged. The original 47 Phase 1 test/helper blobs remain untouched. No contract, ADR, protocol, schema, authority, resource-limit, or capability meaning changes.

Exact repair implementation head: `9814908aae2646f4c09142030b7381e5f9a1394b`. Strict isolated repair validation: `385 passed in 54.25s`, plus install and source/test compilation. Temporary repair helpers/workflows are absent from that head.

PR #119 remains open and unmerged. Issues #61/#121/#123 remain open. Phase 2 is not frozen. One final focused read-only closure audit is required because Issue #122 directly blocked the completion gate.

## Exact restart point

1. Reconstruct from PR #119, Issues #61/#120/#121/#122/#123, `docs/phase2/PHASE2_IMPLEMENTATION_EVIDENCE_MAP.md`, and `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`.
2. Treat `9814908aae2646f4c09142030b7381e5f9a1394b` as the Finding 4 repair implementation head and verify only durable documentation closeout changes follow it before the final audit candidate.
3. Confirm all temporary repair scripts/workflows are absent and all 47 original Phase 1 test/helper blobs remain byte-identical to `62c9e0c6ba7e33eee85e1687b8bf6a3978a25338`.
4. Confirm the final candidate is ordinary-CI green with all 385 protected tests and schema-v1 CLI smoke.
5. Request one final focused read-only closure audit against one exact PR #119 head, concentrating on Issue #122 Finding 4 and regression across Findings 1–3, the 213-ID map, Phase 1, physical limits, authority, rollback, and explicit absence.
6. Do not modify or merge the candidate while the audit is running.
7. If the conclusion is satisfactory, merge PR #119, close Issues #123/#121/#61, update the final handoff, and freeze Phase 2.
8. Request human confirmation for any new finding that would change contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.'''
)

handoff = ROOT / 'docs/HANDOFF.md'
replace_region(
    handoff,
    '## Implementation-completion audit and repairs\n',
    None,
    '''## Implementation-completion audits and repairs

Issue #120 audited exact candidate `44e363e874679537fef43d9f78e382ecf5dc5d3e` and concluded **not ready to freeze; specified repairs required**. Issue #121 accepted four repairs without changing the accepted contract.

Issue #122 then audited exact candidate `6567ec96ecc139e3be1dd0255465e7ac5e8efae1`. Independent evidence confirmed:

- Findings 1–3 fully resolved;
- exactly 213 accepted IDs and evidence-map IDs;
- all 47 original Phase 1 test/helper blobs byte-identical to the Phase 1 audit baseline;
- independent `152 passed` Phase 1 control and `381 passed` full suite;
- schema-v1 installed CLI support and explicit capability absence.

Issue #122 still concluded **not ready to freeze; specified repairs required** because Finding 4 remained partially open. A coherently linked checkpoint from another organism and a manifest with an undeclared field could still certify dispatch, and the selected snapshot was not required to contain the exact active request row/event.

Issue #123 owns the narrow Phase 2-only closure. The repair:

1. requires the exact 18-field checkpoint manifest schema;
2. binds manifest/snapshot organism ID to the active organism and request;
3. requires the checkpoint snapshot's complete `consultation_request` row and validated envelope to equal the active row/envelope;
4. requires the snapshot's complete linked `consultation_request_created` event to equal the active event;
5. retains all existing directory, digest, size, ID, lineage, boundary, registry, SQLite integrity, canonical state, checkpoint-store, working-set, charge, and no-partial-effect checks.

Protected adversarial evidence now covers coherent wrong-organism substitution, a registry-linked undeclared manifest field, a missing request row, and a mismatched request event. Every case rejects before clock read with zero dispatch, charge, admission event, terminal, completion, or fixture effect.

Exact Finding 4 implementation head: `9814908aae2646f4c09142030b7381e5f9a1394b`. Strict isolated validation: `385 passed in 54.25s`, plus install and source/test compilation. The shared frozen Phase 1 checkpoint validator and all original Phase 1 tests/helpers are unchanged. Temporary repair scripts/workflows are absent.

The repaired candidate adds no live caregiver, model API, human chat, network, subprocess, arbitrary code, caller-selected callable, memory, skill, training, continuous loop, personality/emotion state, action adoption, or proposal-to-Phase-1-selector route. Writer categories remain exactly `organism` and `administration`.

## Remaining gate

PR #119 remains open and unmerged. Issues #61, #121, and #123 remain open. Phase 2 is not frozen.

Because Issue #122 directly blocked the completion gate, one final focused read-only closure audit is required at one exact ordinary-CI-green PR #119 head. The audit must independently close Finding 4 and verify no regression of Findings 1–3 or the complete Phase 2 boundary.

## Exact restart

1. Read PR #119; Issues #61/#120/#121/#122/#123; the updated evidence map; and `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`.
2. Verify the final PR #119 candidate contains Finding 4 implementation head `9814908aae2646f4c09142030b7381e5f9a1394b` and only durable documentation closeout changes afterward.
3. Confirm all 385 protected tests, including the unchanged original 152 Phase 1 tests, pass under ordinary CI and schema-v1 CLI smoke passes.
4. Confirm all temporary repair helpers/workflows are absent and all 47 original Phase 1 test/helper blobs remain byte-identical.
5. Request one final focused read-only closure audit against the exact fixed head.
6. Require a conclusion of `ready to freeze`, `ready to freeze after specified documentation-only corrections`, or `not ready to freeze; specified repairs required`.
7. Do not merge PR #119, close Issues #61/#121/#123, or declare Phase 2 frozen before a satisfactory conclusion.
8. After a satisfactory conclusion, merge PR #119, update final evidence and handoff, close the completion issues, and freeze Phase 2.
9. Request human confirmation for any finding that would change contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.'''
)

evidence = ROOT / 'docs/phase2/PHASE2_IMPLEMENTATION_EVIDENCE_MAP.md'
text = evidence.read_text(encoding='utf-8')
text = text.replace(
    'Status: **implementation repair candidate; focused completion re-audit pending**.',
    'Status: **Finding 4 repair candidate; final focused closure audit pending**.',
    1,
)
text = text.replace(
    'Every status below means **mapped to protected evidence; independent implementation audit pending**. It does not mean the audit has accepted the evidence or that Phase 2 is frozen.',
    'Every status below means **mapped to protected evidence; final focused closure audit pending**. It does not mean the remaining Finding 4 closure has been independently accepted or that Phase 2 is frozen.',
    1,
)
absence_row = '| `ABSENCE` | `tests/test_phase2_explicit_absence.py` | audit-preparation branch; package AST/import, CLI, schema/status/configuration, and selector/executor isolation |'
repair_row = '| `REPAIR-F4` | `tests/test_phase2_implementation_audit_repairs.py` | Issue #123; exact manifest fields, active-organism binding, request-row/event snapshot equality, and coherent adversarial substitutions |'
if repair_row not in text:
    if text.count(absence_row) != 1:
        raise RuntimeError('ABSENCE evidence row mismatch')
    text = text.replace(absence_row, absence_row + '\n' + repair_row, 1)
start = text.index('## Independent audit and accepted repair supplement\n')
new_tail = '''## Independent audits and accepted repair supplement

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
'''
text = text[:start] + new_tail
evidence.write_text(text, encoding='utf-8')

slice_note = ROOT / 'docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md'
text = slice_note.read_text(encoding='utf-8')
text = text.replace(
    'Status: **repair candidate complete; focused completion re-audit pending**.',
    'Status: **Finding 4 repair complete; final focused closure audit pending**.',
    1,
)
section = '''

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
'''
if '## Focused re-audit and remaining Finding 4 closure' not in text:
    text = text.rstrip() + section + '\n'
slice_note.write_text(text, encoding='utf-8')
