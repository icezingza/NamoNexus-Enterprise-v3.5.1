from __future__ import annotations

from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "namo_nexus_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "namo_nexus_http_request_latency_ms",
    "HTTP request latency in milliseconds",
    ["method", "path"],
)
REQUEST_ERRORS = Counter(
    "namo_nexus_http_request_errors_total",
    "Total HTTP error responses",
    ["method", "path", "status"],
)


def record_metrics(method: str, path: str, status: int, latency_ms: float) -> None:
    REQUEST_COUNT.labels(method=method, path=path, status=str(status)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(latency_ms)
    if status >= 400:
        REQUEST_ERRORS.labels(method=method, path=path, status=str(status)).inc()
