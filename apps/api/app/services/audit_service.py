from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.audit_logs import create_audit_log


def log_event(db: Session, tenant_id: int, user_id: int, action: str, metadata: dict | None = None) -> None:
    try:
        create_audit_log(db, tenant_id, user_id, action, metadata or {})
    except Exception:
        # Best-effort audit; avoid breaking main flow
        db.rollback()
