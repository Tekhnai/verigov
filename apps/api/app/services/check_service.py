from __future__ import annotations

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.connectors.receita import fetch_cnpj
from app.core.config import settings
from app.core.metrics import record_cnpj_check
from app.repositories.checks import create_check
from app.repositories.reports import create_report
from app.services.report_service import build_summary


def run_cnpj_check(db: Session, tenant_id: int, target_id: int, cnpj: str) -> dict:
    try:
        payload = fetch_cnpj(cnpj, use_mock=settings.use_mock_connectors)
    except Exception as exc:
        create_check(
            db,
            tenant_id,
            target_id,
            provider="receita",
            status="error",
            payload={"cnpj": cnpj, "error": str(exc), "source": "publica.cnpj.ws"},
        )
        record_cnpj_check("error", "error")
        # Include the actual error message for debugging
        detail = f"Falha ao consultar CNPJ: {str(exc)}"
        
        if isinstance(exc, httpx.TimeoutException):
            detail = f"Falha ao consultar CNPJ (timeout): {str(exc)}"
        if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
            detail = f"Falha ao consultar CNPJ (status {exc.response.status_code})"
            
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
        ) from exc

    create_check(db, tenant_id, target_id, provider="receita", status="ok", payload=payload)
    summary = build_summary(payload)
    create_report(db, tenant_id, target_id, version=1, summary=summary)
    record_cnpj_check("success", payload.get("source", "unknown"))
    return summary
