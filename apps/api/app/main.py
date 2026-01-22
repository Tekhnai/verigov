from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, health, jobs, reports, targets, users, metrics
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestLogMiddleware, SecurityHeadersMiddleware, RateLimitMiddleware
from app.db.base import Base
from app.db.session import engine
from app.domain import models  # noqa: F401
from app.core.tracing import setup_tracing
from app.db.rls import enable_rls


configure_logging()

app = FastAPI(title="VeriGov API")
app.add_middleware(RequestLogMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)

if settings.cors_origin_list():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
    enable_rls(engine)
    setup_tracing(app, otlp_endpoint=None)


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(targets.router)
app.include_router(reports.router)
app.include_router(jobs.router)
app.include_router(metrics.router)
