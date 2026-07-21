from __future__ import annotations

from pathlib import Path

import pytest

from sudachi_life.clock import FakeClock
from sudachi_life.organism import initialize_organism


@pytest.fixture
def fixed_clock() -> FakeClock:
    return FakeClock.fixed(
        wall_time_utc_us=1_700_000_000_000_000,
        monotonic_ns=10_000_000,
    )


@pytest.fixture
def initialized(tmp_path: Path, fixed_clock: FakeClock):
    status, checkpoint = initialize_organism(
        tmp_path / "runtime",
        "sudachi-0",
        clock=fixed_clock,
    )
    return tmp_path / "runtime", status, checkpoint
