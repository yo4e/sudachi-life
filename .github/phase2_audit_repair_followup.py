from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, *, context: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{context}: expected exactly one match")
    return text.replace(old, new, 1)


def main() -> None:
    runtime_path = ROOT / "src/sudachi_life/phase2_dispatch_runtime.py"
    runtime = runtime_path.read_text(encoding="utf-8")
    runtime = replace_once(
        runtime,
        '{"fixture_exception", "probe_lock_released"}',
        '{"exit_after_admission", "fixture_exception", "probe_lock_released"}',
        context="closed fault set",
    )
    runtime = replace_once(
        runtime,
        '''        if fixture_fault == "fixture_exception":
            raise RuntimeError("protected deterministic fixture failure")
''',
        '''        if fixture_fault == "exit_after_admission":
            raise SystemExit(23)
        if fixture_fault == "fixture_exception":
            raise RuntimeError("protected deterministic fixture failure")
''',
        context="closed crash probe",
    )
    runtime_path.write_text(runtime, encoding="utf-8")

    test_path = ROOT / "tests/test_phase2_ingress_terminalization_boundaries.py"
    test = test_path.read_text(encoding="utf-8")
    test = replace_once(test, "import os\n", "", context="legacy os import")
    test, count = re.subn(
        r'\n\ndef _exit_fixture\(_request: dict\[str, object\], _case: str\) -> bytes:\n    os\._exit\(23\)\n',
        "",
        test,
        count=1,
    )
    if count != 1:
        raise RuntimeError("legacy exit fixture definition mismatch")
    test = replace_once(
        test,
        "fixture_runner=_exit_fixture,",
        'protected_test_fault="exit_after_admission",',
        context="legacy exit fixture call",
    )
    test_path.write_text(test, encoding="utf-8")


if __name__ == "__main__":
    main()
