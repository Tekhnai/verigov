from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.models import AuditLog


def create_audit_log(db: Session, tenant_id: int, user_id: int, action: str, metadata: dict | None = None) -> AuditLog:
    entry = AuditLog(tenant_id=tenant_id, user_id=user_id, action=action, metadata_json=metadata or {})
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
