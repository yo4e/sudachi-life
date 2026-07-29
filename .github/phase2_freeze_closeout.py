from __future__ import annotations

from pathlib import Path


AUDIT_HEAD = "12de7b7d7413f343b2e5a74df369c26a5896c865"
MERGE_COMMIT = "b0941a8ba2a178fc891839198cd5dd5bf6e87719"
PHASE1_BASELINE = "62c9e0c6ba7e33eee85e1687b8bf6a3978a25338"


def replace_section(path: Path, start: str, end: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(start) != 1 or text.count(end) != 1:
        raise SystemExit(f"section anchors are not unique in {path}")
    prefix, remainder = text.split(start, 1)
    _, suffix = remainder.split(end, 1)
    path.write_text(prefix + replacement + end + suffix, encoding="utf-8")


agents = Path("AGENTS.md")
replace_section(
    agents,
    "## Open gate\n",
    "## End-of-work protocol\n",
    f'''## Frozen Phase 2

Issue #127 completed the final independent read-only Phase 2 closure audit at exact candidate `{AUDIT_HEAD}` and concluded **ready to freeze**. No blocker, high, medium, low, or documentation-only finding survived validation.

Independent closure evidence included:

- complete protected suite: `395 passed`;
- original Phase 1 control: `152 passed`;
- all 47 original Phase 1 Python test/helper blobs byte-identical to `{PHASE1_BASELINE}`;
- exactly 213 accepted matrix IDs and exactly the same 213 evidence-map IDs;
- schema-v1 installed CLI behavior preserved;
- Findings 1–4 resolved, including coherent active/checkpoint request-event semantic mutations;
- explicit capability absence, writer authority, checkpoint, rollback, physical-limit, and no-partial-effect boundaries intact.

PR #119 merged the audited candidate as `{MERGE_COMMIT}`. Phase 2 is frozen at that merge. Issues #120/#122/#124/#127 retain the independent audit history; Issues #121/#123/#125 own the now-completed repair history.

The frozen Phase 2 boundary includes ADRs 0008–0016, Consultation Protocol v1, all accepted matrix amendments, the 213-ID evidence map, implemented Slice 36–42c behavior, and the protected tests merged through PR #119.

Do not reinterpret or change Phase 2 request, dispatch, charge, fixture, ingress, terminalization, disposition, finite-cycle, rollback-lineage, checkpoint, authority, physical-limit, or explicit-absence semantics without explicit project-owner authorization for one exact defect or a separately accepted future-phase design.

No live caregiver, model API, human chat, network, subprocess, arbitrary callable/code, memory, skill generation, training, continuous loop, personality/emotion state, action adoption, or proposal-to-Phase-1-selector route is authorized by the Phase 2 freeze.

## Exact restart point

1. Reconstruct from this file, `docs/HANDOFF.md`, `docs/phase2/SLICE42C_FINAL_CLOSURE_AUDIT.md`, PR #119, and Issue #127.
2. Treat Phase 1 and Phase 2 as frozen controls. Repository and current GitHub state outrank conversation history.
3. Begin any later research or implementation only through separately accepted scope; do not silently reopen Phase 2 under a cleanup, refactor, or capability request.
4. Preserve all original Phase 1 blobs, the 213 accepted Phase 2 IDs, writer categories, resource limits, retained evidence, and explicit capability absence.
5. Request human confirmation before changing contract/ADR intent, frozen behavior, authority/security, live capabilities, protected evidence, or material autonomy/resource scope.

''',
)

handoff = Path("docs/HANDOFF.md")
handoff_text = handoff.read_text(encoding="utf-8")
handoff_start = "## Implementation-completion audits and repairs\n"
if handoff_text.count(handoff_start) != 1:
    raise SystemExit("HANDOFF completion section anchor is not unique")
handoff_prefix = handoff_text.split(handoff_start, 1)[0]
handoff_tail = f'''## Phase 2 implementation audit and freeze

Issue #120 audited `44e363e874679537fef43d9f78e382ecf5dc5d3e` and found one high and three medium defects. Issues #121/#123/#125 record the accepted Phase 2-only repairs. Issues #122 and #124 independently re-audited the successive closure candidates and exposed the remaining checkpoint-linkage and request-event semantic-linkage defects.

Issue #127 performed the final independent read-only audit at exact candidate `{AUDIT_HEAD}`. It independently verified:

- `395 passed` for the complete protected suite;
- `152 passed` for the original Phase 1 control;
- all 47 original Phase 1 Python test/helper blobs byte-identical to `{PHASE1_BASELINE}`;
- exactly 213 accepted and evidence-map IDs;
- schema-v1 CLI behavior and schema-v2 zero-caregiver behavior intact;
- Findings 1–4 resolved under independent adversarial probes;
- writer categories exactly `organism` and `administration`;
- checkpoint, rollback, identity, digest, immutable-row, artifact, physical-limit, and no-partial-effect boundaries intact;
- no unauthorized live caregiver, API, chat, network, subprocess, callable/code, memory, skill, training, loop, personality/emotion, action-adoption, or selector route.

The required conclusion was **ready to freeze**, with no surviving finding and no documentation-only correction required.

PR #119 merged the exact audited candidate as `{MERGE_COMMIT}`. Phase 2 is frozen at that merge. The frozen package is ADRs 0008–0016, Consultation Protocol v1, accepted amendments, the 213-ID evidence map, implemented Slice 36–42c behavior, and all protected tests merged through PR #119.

## Exact restart

1. Read `AGENTS.md`, this handoff, `docs/phase2/SLICE42C_FINAL_CLOSURE_AUDIT.md`, PR #119, and Issue #127.
2. Treat both Phase 1 and Phase 2 as frozen controls.
3. Do not reopen frozen semantics for refactoring or convenience. One exact defect requires explicit project-owner authorization; future-phase work requires separately accepted design scope.
4. Preserve the 47 original Phase 1 blobs, 152-test control, 213 Phase 2 IDs, authority categories, resource limits, retained evidence, and explicit capability absence.
5. Keep later capability proposals outside the frozen implementation until their own design and audit gates are accepted.
'''
handoff.write_text(handoff_prefix + handoff_tail, encoding="utf-8")

map_path = Path("docs/phase2/PHASE2_IMPLEMENTATION_EVIDENCE_MAP.md")
map_text = map_path.read_text(encoding="utf-8")
if map_text.count("Mapped; audit pending") != 213:
    raise SystemExit("expected exactly 213 pending evidence statuses")
map_text = map_text.replace("Mapped; audit pending", "Audited; frozen")
replacements = {
    "Status: **Finding 4 repair candidate; final focused closure audit pending**.":
        "Status: **independently audited; Phase 2 frozen**.",
    "This document maps the final accepted Phase 2 Consultation Boundary evidence set to the exact protected tests and durable implementation notes present after Slice 42b. It is an audit input, not an audit conclusion and not a Phase 2 freeze decision.":
        "This document maps the final accepted Phase 2 Consultation Boundary evidence set to the exact protected tests and durable implementation notes. Issue #127 independently audited the complete 213-ID set and concluded ready to freeze.",
    f"- original Phase 1 audit baseline: `{PHASE1_BASELINE}`.":
        f"- original Phase 1 audit baseline: `{PHASE1_BASELINE}`;\n- final Phase 2 audit candidate: `{AUDIT_HEAD}`;\n- final independent audit: Issue #127, conclusion `ready to freeze`;\n- audited candidate merge: PR #119 as `{MERGE_COMMIT}`;\n- final protected controls: 395 complete tests and 152 original Phase 1 tests.",
    "The independent audit must still verify, against one exact candidate commit:":
        f"Issue #127 independently verified the following against exact candidate `{AUDIT_HEAD}`:",
    "- No Codex or other independent implementation audit conclusion is recorded here.":
        "- Issue #127 records the final independent conclusion `ready to freeze`; no finding or documentation-only correction remained.",
    "This map may become the input to the single read-only Phase 2 implementation audit only after its exact branch head is CI-green. Phase 2 remains open under Issue #61 until the audit concludes satisfactorily and any accepted findings are repaired through protected work.":
        f"This map was the input to the final independent read-only audit at `{AUDIT_HEAD}`. Issue #127 verified the complete gate and concluded ready to freeze. PR #119 merged the audited candidate as `{MERGE_COMMIT}`; the 213 mapped requirements are frozen controls.",
    "This map remains an audit input. Issue #124 is an interim audit record, not a final conclusion. One final focused independent read-only closure audit must verify the Issue #125 repair and the complete gate before PR #119 may merge or Issue #61 may close. Phase 2 is not frozen.":
        f"Issue #127 completed the final independent read-only closure audit at `{AUDIT_HEAD}`. It independently reproduced the Issue #125 semantic-linkage boundary, rechecked Findings 1–4, the 213-ID set, original Phase 1 blobs and control, schema-v1 support, authority, physical limits, rollback, and explicit absence, and concluded **ready to freeze** with no surviving finding. PR #119 merged the audited candidate as `{MERGE_COMMIT}`. Phase 2 is frozen.",
}
for old, new in replacements.items():
    if map_text.count(old) != 1:
        raise SystemExit(f"evidence-map replacement anchor is not unique: {old[:60]!r}")
    map_text = map_text.replace(old, new, 1)
map_path.write_text(map_text, encoding="utf-8")

final_note = Path("docs/phase2/SLICE42C_FINAL_CLOSURE_AUDIT.md")
final_note.write_text(
    f'''# Slice 42c Final Closure-Audit Boundary

Status: **complete; Phase 2 frozen**.

## Audit sequence

- Issue #120 found one high and three medium implementation defects at `44e363e874679537fef43d9f78e382ecf5dc5d3e`.
- Issue #122 confirmed Findings 1–3 closed and found the remaining checkpoint-linkage defect.
- Issue #123 repaired exact manifest, active-organism, request-row, and active/snapshot request-event row linkage.
- Issue #124 independently confirmed those reproductions closed, then found the remaining coherent request-event semantic-linkage defect.
- Issue #125 repaired exact request-created event reconstruction and independent active/snapshot semantic validation.
- Issue #127 completed the final independent read-only closure audit at `{AUDIT_HEAD}`.

## Final independent conclusion

Issue #127 reported no surviving blocker, high, medium, low, or documentation-only finding and concluded:

**ready to freeze**

Independent completion evidence included:

- complete protected suite: `395 passed`;
- original Phase 1 control: `152 passed`;
- all 47 original Phase 1 Python test/helper blobs byte-identical to `{PHASE1_BASELINE}`;
- exactly 213 accepted matrix IDs and exactly 213 evidence-map IDs;
- installed schema-v1 CLI behavior preserved;
- coherent active/checkpoint mutations of request-event payload, source, lineage, lifecycle, schema, environment, budget, type, and organism rejected before clock read with zero partial effects;
- prior Findings 1–4 independently rechecked and resolved;
- authority, checkpoint, rollback, physical accounting, retained evidence, and explicit capability absence intact.

## Merge and freeze

PR #119 merged exact audited candidate `{AUDIT_HEAD}` as `{MERGE_COMMIT}`.

Phase 2 is frozen at that merge. The frozen boundary consists of:

- ADRs 0008–0016;
- Consultation Protocol v1 and accepted matrix amendments;
- exactly 213 accepted evidence IDs;
- implemented Slice 36–42c runtime behavior;
- all protected tests and retained evidence merged through PR #119;
- canonical writer categories exactly `organism` and `administration`;
- no authorized live caregiver, model API, human chat, network, subprocess, arbitrary callable/code, memory, skill, training, continuous loop, personality/emotion state, action adoption, or proposal-to-Phase-1-selector route.

Any later change to frozen Phase 2 semantics requires explicit project-owner authorization for one exact defect or a separately accepted future-phase design and audit gate.
''',
    encoding="utf-8",
)
