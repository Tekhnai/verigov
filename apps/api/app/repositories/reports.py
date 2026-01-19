from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.models import Report


def create_report(
    db: Session,
    tenant_id: int,
    target_id: int,
    version: int,
    summary: dict,
) -> Report:
    report = Report(
        tenant_id=tenant_id,
        target_id=target_id,
        version=version,
        summary_json=summary,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_latest_report(db: Session, tenant_id: int, target_id: int) -> Report | None:
    return (
        db.query(Report)
        .filter(Report.tenant_id == tenant_id)
        .filter(Report.target_id == target_id)
        .order_by(Report.created_at.desc())
        .first()
    )
