from __future__ import annotations

import pytest

from sudachi_life.clock import ClockReading, FakeClock
from sudachi_life.errors import ClockExhaustedError


def test_fake_clock_returns_declared_readings_in_order() -> None:
    clock = FakeClock(
        [
            ClockReading(100, 10),
            ClockReading(90, 20),
        ]
    )

    assert clock.read() == ClockReading(100, 10)
    assert clock.read() == ClockReading(90, 20)
    assert clock.read_count == 2


def test_unexpected_clock_read_fails() -> None:
    clock = FakeClock.fixed(wall_time_utc_us=100, monotonic_ns=10)
    assert clock.read() == ClockReading(100, 10)

    with pytest.raises(ClockExhaustedError, match="unexpected clock read"):
        clock.read()
