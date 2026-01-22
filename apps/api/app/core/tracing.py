from __future__ import annotations

from typing import Optional

import structlog

logger = structlog.get_logger()

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

    _OTEL_AVAILABLE = True
except Exception as exc:  # pragma: no cover - fallback when deps absent
    logger.warning("otel_not_available", error=str(exc))
    _OTEL_AVAILABLE = False


def setup_tracing(app=None, otlp_endpoint: str | None = None) -> None:
    """
    Configure OTLP tracing if opentelemetry libs are present.
    Safe no-op when deps are missing.
    """
    if not _OTEL_AVAILABLE:
        return

    try:
        provider = TracerProvider()
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint) if otlp_endpoint else OTLPSpanExporter()
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)

        if app is not None:
            FastAPIInstrumentor.instrument_app(app)
        Psycopg2Instrumentor().instrument()
        RedisInstrumentor().instrument()
        logger.info("otel_tracing_enabled", endpoint=otlp_endpoint or "default")
    except Exception as exc:  # pragma: no cover - swallow instrumentation errors
        logger.warning("otel_setup_failed", error=str(exc))
