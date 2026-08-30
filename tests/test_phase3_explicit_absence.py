from __future__ import annotations

from pathlib import Path

from sudachi_life.phase3.model import WRITER_CATEGORIES


FORBIDDEN_RUNTIME_IMPORTS = (
    "import requests",
    "import socket",
    "import subprocess",
    "import urllib",
    "from requests",
    "from socket",
    "from subprocess",
    "from urllib",
)


def test_fixture_foundation_has_no_live_external_runtime_route() -> None:
    root = Path(__file__).parents[1] / "src" / "sudachi_life" / "phase3"
    sources = "\n".join(path.read_text(encoding="utf-8") for path in sorted(root.glob("*.py")))

    for forbidden in FORBIDDEN_RUNTIME_IMPORTS:
        assert forbidden not in sources
    assert "os.system(" not in sources
    assert "Popen(" not in sources


def test_canonical_writer_categories_remain_exactly_two() -> None:
    assert WRITER_CATEGORIES == {"organism", "administration"}


def test_phase3_package_does_not_import_phase1_or_phase2_runtime_modules() -> None:
    root = Path(__file__).parents[1] / "src" / "sudachi_life" / "phase3"
    sources = "\n".join(path.read_text(encoding="utf-8") for path in sorted(root.glob("*.py")))

    assert "sudachi_life.lifecycle" not in sources
    assert "sudachi_life.phase2" not in sources
    assert "sqlite3" not in sources
