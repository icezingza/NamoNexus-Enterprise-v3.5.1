from __future__ import annotations


def fibonacci_retry(
    attempt: int,
    base_seconds: float = 0.5,
    max_seconds: float = 30.0,
) -> float:
    """Return a Fibonacci backoff delay for a 1-based attempt count."""
    if attempt <= 0:
        return 0.0
    a, b = 0, 1
    for _ in range(attempt):
        a, b = b, a + b
    delay = a * base_seconds
    return max(0.0, min(delay, max_seconds))
