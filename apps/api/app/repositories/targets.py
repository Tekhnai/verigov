from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.models import Target


def create_target(
    db: Session,
    tenant_id: int,
    document: str,
    name_hint: str | None,
    target_type: str,
) -> Target:
    target = Target(tenant_id=tenant_id, document=document, name_hint=name_hint, type=target_type)
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def list_targets(db: Session, tenant_id: int) -> list[Target]:
    return db.query(Target).filter(Target.tenant_id == tenant_id).order_by(Target.id.desc()).all()


def get_target(db: Session, tenant_id: int, target_id: int) -> Target | None:
    return (
        db.query(Target)
        .filter(Target.tenant_id == tenant_id)
        .filter(Target.id == target_id)
        .one_or_none()
    )
