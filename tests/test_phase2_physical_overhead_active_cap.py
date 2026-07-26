from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.phase2_physical_projection import (
    PhysicalProjectionError,
    measure_zero_caregiver_physical_overhead,
)

from test_phase2_physical_overhead import _complete_full_rollback_pair


def test_real_active_database_overhead_enforces_the_declared_cap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    v1, v2, left, right = _complete_full_rollback_pair(tmp_path)
    report = measure_zero_caregiver_physical_overhead(v1, v2, left, right)

    import sudachi_life.phase2_physical_projection as physical

    monkeypatch.setattr(
        physical,
        "ACTIVE_DATABASE_OVERHEAD_CAP_BYTES",
        report.active_database_overhead_bytes - 1,
    )
    with pytest.raises(
        PhysicalProjectionError,
        match="active database overhead exceeds the accepted cap",
    ):
        measure_zero_caregiver_physical_overhead(v1, v2, left, right)
