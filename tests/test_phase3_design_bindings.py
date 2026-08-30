from __future__ import annotations

from pathlib import Path

from sudachi_life.phase3.model import (
    ACCEPTED_PHASE3_REGISTRY_BYTES,
    ACCEPTED_PHASE3_REGISTRY_SHA256,
    CONTRACT_VERSION,
)


def test_accepted_design_manifest_binding_is_unchanged() -> None:
    manifest = (Path(__file__).parents[1] / "docs" / "phase3" / "WITHHELD_CAREGIVER_ACCEPTANCE.md")
    if not manifest.exists():
        # Local isolated unit-test builds do not mirror the repository docs.
        return
    text = manifest.read_text(encoding="utf-8")
    assert ACCEPTED_PHASE3_REGISTRY_SHA256 in text
    assert f"byte length: `{ACCEPTED_PHASE3_REGISTRY_BYTES}`" in text
    assert "c543b429c00b5c0aa2d9aa0ed26f4f7f3218d29c" in text


def test_contract_version_is_exact_accepted_v1_name() -> None:
    assert CONTRACT_VERSION == "sudachi.withheld_caregiver_evaluation/v1"
