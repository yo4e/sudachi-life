"""Injected real and deterministic clocks."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, Protocol
import time

from .errors import ClockExhaustedError


@dataclass(frozen=True, slots=True)
class ClockReading:
    """One explicit wall and monotonic time input."""

    wall_time_utc_us: int
    monotonic_ns: int


class Clock(Protocol):
    """The only time boundary available to organism code."""

    def read(self) -> ClockReading:
        """Return one explicit clock reading."""


class RealClock:
    """Operational UTC wall and monotonic clock."""

    def read(self) -> ClockReading:
        return ClockReading(
            wall_time_utc_us=time.time_ns() // 1_000,
            monotonic_ns=time.monotonic_ns(),
        )


class FakeClock:
    """A deterministic clock that fails on unexpected reads."""

    def __init__(self, readings: Iterable[ClockReading]) -> None:
        self._readings = deque(readings)
        self.read_count = 0

    @classmethod
    def fixed(
        cls,
        *,
        wall_time_utc_us: int,
        monotonic_ns: int,
        reads: int = 1,
    ) -> "FakeClock":
        if reads < 0:
            raise ValueError("reads must be nonnegative")
        reading = ClockReading(wall_time_utc_us, monotonic_ns)
        return cls([reading] * reads)

    def append(self, reading: ClockReading) -> None:
        self._readings.append(reading)

    def read(self) -> ClockReading:
        if not self._readings:
            raise ClockExhaustedError("unexpected clock read")
        self.read_count += 1
        return self._readings.popleft()

    @property
    def remaining_reads(self) -> int:
        return len(self._readings)
