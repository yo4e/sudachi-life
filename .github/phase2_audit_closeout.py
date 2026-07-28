from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPAIR_HEAD = "6cc312a4e2ac64f866babe7cbab44aca8493b24d"
CI_HEAD = "579e7098e66b679c5d69baa8290e452e4ab10db6"


def replace_once(text: str, old: str, new: str, *, context: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{context}: expected exactly one match")
    return text.replace(old, new, 1)


def update_evidence_map() -> None:
    path = ROOT / "docs/phase2/PHASE2_IMPLEMENTATION_EVIDENCE_MAP.md"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "Status: **implementation-completion candidate; independent audit not yet run**.",
        "Status: **implementation repair candidate; focused completion re-audit pending**.",
        context="evidence-map status",
    )
    supplement = f'''\n\n## Independent audit and accepted repair supplement\n\nThe single independent read-only implementation audit in Issue #120 inspected exact candidate `44e363e874679537fef43d9f78e382ecf5dc5d3e` and concluded **not ready to freeze; specified repairs required**. Issue #121 owns the accepted repairs.\n\nExact repair evidence:\n\n- runtime repair head: `{REPAIR_HEAD}`;\n- ordinary CI candidate: `{CI_HEAD}`;\n- GitHub Actions run 636: `381 passed in 52.21s`;\n- install, source/test compilation, protected-test enforcement, and schema-v1 genesis CLI smoke passed;\n- original 152 Phase 1 tests remain unchanged;\n- durable repair note: `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`;\n- repair regressions: `tests/test_phase2_implementation_audit_repairs.py`;\n- exact audited pre-repair dispatch bytes retained outside the installed package at `docs/phase2/retained/phase2_dispatch_runtime_impl.py`, SHA-256 `ed573180a7017b9ec8b1002ec59f2376e90653ee8a4013f8b24775a80a0f80ac`.\n\nThe repair evidence supplements the existing row mapping without changing any accepted ID or requirement meaning. In particular it strengthens the mapped evidence for the Phase 1 capability-isolation boundary, exact deterministic-fixture dispatch and charge boundary, stable-checkpoint admission, package ingress and terminalization, maintenance-state preservation, interrupted-dispatch reconciliation, and explicit absence of arbitrary caller-selected execution.\n\nThe repaired candidate adds no live caregiver, model API, human chat, network, subprocess, arbitrary code, memory, skill, training, continuous loop, personality/emotion state, action adoption, or proposal-to-Phase-1-selector route. Canonical writer categories remain exactly `organism` and `administration`.\n\nThis map remains an audit input. It does not declare the repairs accepted by an independent reviewer and does not freeze Phase 2. One focused read-only completion re-audit is required before PR #119 may merge or Issue #61 may close.\n'''
    if "## Independent audit and accepted repair supplement" in text:
        raise RuntimeError("repair supplement already present")
    path.write_text(text.rstrip() + supplement, encoding="utf-8")


def update_agents() -> None:
    path = ROOT / "AGENTS.md"
    text = path.read_text(encoding="utf-8")
    start = text.index("## Open gate")
    end = text.index("## End-of-work protocol")
    replacement = f'''## Open gate\n\nIssue #120 completed the single independent Phase 2 implementation audit at `44e363e874679537fef43d9f78e382ecf5dc5d3e` and found one high and three medium implementation defects. The conclusion was **not ready to freeze; specified repairs required**.\n\nIssue #121 owns the accepted repairs. PR #119 now contains the repaired implementation and evidence:\n\n- repair implementation head `{REPAIR_HEAD}`;\n- ordinary CI head `{CI_HEAD}`, run 636: `381 passed in 52.21s`;\n- install, compile, protected enforcement, and schema-v1 CLI smoke passed;\n- original 152 Phase 1 tests remain unchanged;\n- durable note: `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`.\n\nThe repairs close the arbitrary caller-supplied fixture callable, terminalize caught fixture failure exactly once, admit and preserve canonical stable maintenance state during ingress/terminalization, and validate the exact stable checkpoint artifact before dispatch effects. They do not change ADR 0008–0016 or Protocol v1 meaning and add no live external capability.\n\nBecause the prior audit conclusion blocks the phase gate and the repairs touch capability, persistence, checkpoint, and terminalization boundaries, one focused read-only completion re-audit is required under `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`. PR #119 must remain unmerged and Issue #61/#121 must remain open until that conclusion is satisfactory.\n\n## Exact restart point\n\n1. Reconstruct from PR #119, Issue #120, Issue #121, and `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`.\n2. Confirm the final exact re-audit candidate includes `{REPAIR_HEAD}` and run 636 evidence, plus only documentation closeout changes after `{CI_HEAD}`.\n3. Confirm all temporary repair scripts/workflows are absent and all original 152 Phase 1 tests are unchanged.\n4. Request one focused read-only completion re-audit against the final exact PR #119 head.\n5. Require the reviewer to independently inspect all four Issue #120 findings, affected cross-boundaries, the 213-ID evidence map, Phase 1 byte identity, schema-v1 support, physical accounting, authority, rollback, and explicit-absence surfaces.\n6. Do not modify or merge the candidate while the re-audit is running.\n7. If the conclusion is satisfactory, merge PR #119, close Issue #121 and Issue #61, update the final handoff, and freeze Phase 2.\n8. Request human confirmation for any new finding that would change contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.\n\n'''
    path.write_text(text[:start] + replacement + text[end:], encoding="utf-8")


def update_handoff() -> None:
    path = ROOT / "docs/HANDOFF.md"
    text = path.read_text(encoding="utf-8")
    start = text.index("## Implementation-completion gate")
    replacement = f'''## Implementation-completion audit and repairs\n\nIssue #120 completed the single independent read-only Phase 2 implementation audit at `44e363e874679537fef43d9f78e382ecf5dc5d3e`. It independently reconstructed the 213 accepted IDs and the unchanged 152-test Phase 1 control, then concluded **not ready to freeze; specified repairs required**.\n\nIssue #121 accepted four repairs without changing the accepted contract:\n\n1. remove the public caller-supplied fixture callable and bind exact deterministic fixture execution;\n2. terminalize caught fixture failure through the existing `fixture_output_invalid` branch exactly once;\n3. admit and preserve canonical stable `maintenance_required` state during ingress and terminalization;\n4. validate the exact stable checkpoint artifact and registry linkage before dispatch clock or mutation.\n\nExact repair evidence:\n\n- implementation head `{REPAIR_HEAD}`;\n- ordinary CI head `{CI_HEAD}`;\n- run 636: `381 passed in 52.21s`;\n- install, source/test compilation, protected enforcement, and schema-v1 genesis CLI smoke passed;\n- original 152 Phase 1 tests remain unchanged;\n- temporary repair scripts/workflows are absent;\n- durable note: `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`.\n\nThe repaired candidate adds no live caregiver, model API, human chat, network, subprocess, arbitrary code, memory, skill, training, continuous loop, personality/emotion state, action adoption, or proposal-to-Phase-1-selector route. Writer categories remain exactly `organism` and `administration`.\n\n## Remaining gate\n\nThe prior independent conclusion directly blocks Phase 2 freeze, and the repairs touch capability, persistence, checkpoint, and terminalization boundaries. One focused read-only completion re-audit is therefore required under `docs/CODEX_INDEPENDENT_AUDIT_POLICY.md`.\n\nPR #119 remains open and unmerged. Issue #61 and Issue #121 remain open. Phase 2 is not frozen.\n\n## Exact restart\n\n1. Read PR #119, Issue #120, Issue #121, the updated evidence map, and `docs/phase2/SLICE42C_IMPLEMENTATION_AUDIT_REPAIRS.md`.\n2. Verify the final exact PR #119 head contains the repaired implementation head `{REPAIR_HEAD}`, ordinary run 636 evidence at `{CI_HEAD}`, and only documentation closeout changes afterward.\n3. Confirm all 381 protected tests, including the unchanged original 152 Phase 1 tests, are present and green.\n4. Confirm no temporary repair helper or workflow remains.\n5. Request one focused read-only completion re-audit against the final exact head.\n6. Require a conclusion of `ready to freeze`, `ready to freeze after specified documentation-only corrections`, or `not ready to freeze; specified repairs required`.\n7. Do not merge PR #119, close Issue #61/#121, or declare Phase 2 frozen before a satisfactory conclusion.\n8. After a satisfactory conclusion, merge PR #119, update final evidence and handoff, close the completion issues, and freeze Phase 2.\n9. Request human confirmation for any finding that would change contract/ADR intent, frozen Phase 1, authority/security, capabilities, protected evidence, or material scope.\n'''
    path.write_text(text[:start] + replacement, encoding="utf-8")


def main() -> None:
    update_evidence_map()
    update_agents()
    update_handoff()


if __name__ == "__main__":
    main()
