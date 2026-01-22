from __future__ import annotations

from fastapi import APIRouter, Response, Depends

from app.core.config import settings
from app.core.metrics import metrics_response
from app.core.deps import require_roles

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def prometheus_metrics(current_user=Depends(require_roles("admin")) if False else None):
    # Currently open for scraping without auth; tighten in prod if needed.
    data, content_type = metrics_response()
    return Response(content=data, media_type=content_type)
