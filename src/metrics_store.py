from __future__ import annotations

import math
import time
from collections import deque
from threading import Lock
from typing import Deque, Dict, List


def _percentile(sorted_values: List[float], percentile: float) -> float:
    if not sorted_values:
        return 0.0
    if percentile <= 0:
        return sorted_values[0]
    if percentile >= 1:
        return sorted_values[-1]
    index = (len(sorted_values) - 1) * percentile
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return sorted_values[int(index)]
    weight = index - lower
    return sorted_values[lower] + (sorted_values[upper] - sorted_values[lower]) * weight


class LatencyMetricsStore:
    def __init__(self, max_samples: int = 5000) -> None:
        self._samples: Deque[float] = deque(maxlen=max_samples)
        self._count = 0
        self._error_count = 0
        self._lock = Lock()
        self._start_time = time.time()

    def record(self, duration_seconds: float, status_code: int) -> None:
        with self._lock:
            self._count += 1
            if status_code >= 500:
                self._error_count += 1
            self._samples.append(duration_seconds)

    def summary(self) -> Dict[str, float]:
        with self._lock:
            samples = list(self._samples)
            count = self._count
            error_count = self._error_count
            uptime_seconds = max(0.0, time.time() - self._start_time)

        if not samples:
            return {
                "requests": float(count),
                "errors": float(error_count),
                "uptime_seconds": round(uptime_seconds, 2),
                "avg_ms": 0.0,
                "p50_ms": 0.0,
                "p95_ms": 0.0,
                "p99_ms": 0.0,
                "rps": round((count / uptime_seconds) if uptime_seconds else 0.0, 4),
            }

        samples_sorted = sorted(samples)
        avg = sum(samples_sorted) / len(samples_sorted)
        p50 = _percentile(samples_sorted, 0.5)
        p95 = _percentile(samples_sorted, 0.95)
        p99 = _percentile(samples_sorted, 0.99)
        rps = (count / uptime_seconds) if uptime_seconds else 0.0

        return {
            "requests": float(count),
            "errors": float(error_count),
            "uptime_seconds": round(uptime_seconds, 2),
            "avg_ms": round(avg * 1000, 2),
            "p50_ms": round(p50 * 1000, 2),
            "p95_ms": round(p95 * 1000, 2),
            "p99_ms": round(p99 * 1000, 2),
            "rps": round(rps, 4),
        }
