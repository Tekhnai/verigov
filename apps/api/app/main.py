from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, health, jobs, reports, targets, users
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import RequestLogMiddleware
from app.db.base import Base
from app.db.session import engine
from app.domain import models  # noqa: F401


configure_logging()

app = FastAPI(title="VeriGov API")
app.add_middleware(RequestLogMiddleware)

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


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(targets.router)
app.include_router(reports.router)
app.include_router(jobs.router)
