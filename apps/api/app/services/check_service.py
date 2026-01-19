from __future__ import annotations

from sqlalchemy.orm import Session

from app.connectors.receita import fetch_cnpj
from app.core.config import settings
from app.repositories.checks import create_check
from app.repositories.reports import create_report
from app.services.report_service import build_summary


def run_cnpj_check(db: Session, tenant_id: int, target_id: int, cnpj: str) -> dict:
    payload = fetch_cnpj(cnpj, use_mock=settings.use_mock_connectors)
    create_check(db, tenant_id, target_id, provider="receita", status="ok", payload=payload)
    summary = build_summary(payload)
    create_report(db, tenant_id, target_id, version=1, summary=summary)
    return summary
