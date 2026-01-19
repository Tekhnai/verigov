from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.models import Check


def create_check(
    db: Session,
    tenant_id: int,
    target_id: int,
    provider: str,
    status: str,
    payload: dict,
) -> Check:
    check = Check(
        tenant_id=tenant_id,
        target_id=target_id,
        provider=provider,
        status=status,
        raw_payload_json=payload,
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check
