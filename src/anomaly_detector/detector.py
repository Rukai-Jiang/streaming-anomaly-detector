from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Detection:
    value: float
    timestamp: Any
    score: float
    is_anomaly: bool
    baseline_mean: float | None
    baseline_std: float | None
    baseline_samples: int


class RollingZScoreDetector:
    """Detect point anomalies against a rolling window in O(1) time."""

    def __init__(
        self,
        *,
        window_size: int = 30,
        threshold: float = 3.0,
        min_samples: int | None = None,
    ) -> None:
        if window_size < 2:
            raise ValueError("window_size must be at least 2")
        if threshold <= 0:
            raise ValueError("threshold must be positive")

        self.window_size = window_size
        self.threshold = threshold
        self.min_samples = min_samples if min_samples is not None else window_size
        if not 2 <= self.min_samples <= window_size:
            raise ValueError("min_samples must be between 2 and window_size")

        self._values: deque[float] = deque()
        self._sum = 0.0
        self._sum_squares = 0.0

    def update(self, value: float, timestamp: Any = None) -> Detection:
        value = float(value)
        if not math.isfinite(value):
            raise ValueError("value must be finite")

        sample_count = len(self._values)
        mean: float | None = None
        standard_deviation: float | None = None
        score = 0.0
        is_anomaly = False

        if sample_count >= self.min_samples:
            mean = self._sum / sample_count
            variance = max(
                0.0, self._sum_squares / sample_count - mean * mean
            )
            standard_deviation = math.sqrt(variance)
            distance = abs(value - mean)
            if standard_deviation > 1e-12:
                score = distance / standard_deviation
            elif distance > 1e-12:
                score = math.inf
            is_anomaly = score >= self.threshold

        self._append(value)
        return Detection(
            value=value,
            timestamp=timestamp,
            score=score,
            is_anomaly=is_anomaly,
            baseline_mean=mean,
            baseline_std=standard_deviation,
            baseline_samples=sample_count,
        )

    def reset(self) -> None:
        self._values.clear()
        self._sum = 0.0
        self._sum_squares = 0.0

    def _append(self, value: float) -> None:
        if len(self._values) == self.window_size:
            expired = self._values.popleft()
            self._sum -= expired
            self._sum_squares -= expired * expired
        self._values.append(value)
        self._sum += value
        self._sum_squares += value * value

