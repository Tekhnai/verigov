from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.repositories.reports import get_latest_report
from app.schemas.reports import ReportOut

router = APIRouter(prefix="/targets", tags=["reports"])


@router.get("/{target_id}/report/latest", response_model=ReportOut)
def latest_report(
    target_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "analyst")),
) -> ReportOut:
    report = get_latest_report(db, current_user.tenant_id, target_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
