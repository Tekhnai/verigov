from __future__ import annotations

try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    _PROM_AVAILABLE = True
except Exception:  # pragma: no cover - fallback when lib not installed/offline
    _PROM_AVAILABLE = False

    class _DummyMetric:
        def __init__(self, *args, **kwargs):
            self.name = args[0] if args else "metric"

        def labels(self, **kwargs):
            return self

        def inc(self, amount: float = 1.0) -> None:
            return None

        def observe(self, value: float) -> None:
            return None

    Counter = _DummyMetric  # type: ignore
    Histogram = _DummyMetric  # type: ignore

    def generate_latest() -> bytes:
        # minimal exposition format so scraping/tests still succeed
        return b"# dummy metrics\nhttp_requests_total 0\n"

    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)

LOGIN_COUNT = Counter(
    "logins_total",
    "Total login attempts",
    ["outcome"],
)

REGISTER_COUNT = Counter(
    "registrations_total",
    "Total user registrations",
    ["outcome"],
)

CNPJ_CHECK_COUNT = Counter(
    "cnpj_checks_total",
    "Total CNPJ checks executed",
    ["outcome", "source"],
)


def record_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    REQUEST_COUNT.labels(method=method, path=path, status_code=str(status_code)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(duration_seconds)


def record_login(outcome: str) -> None:
    LOGIN_COUNT.labels(outcome=outcome).inc()


def record_registration(outcome: str) -> None:
    REGISTER_COUNT.labels(outcome=outcome).inc()


def record_cnpj_check(outcome: str, source: str) -> None:
    CNPJ_CHECK_COUNT.labels(outcome=outcome, source=source).inc()


def metrics_response():
    return generate_latest(), CONTENT_TYPE_LATEST
