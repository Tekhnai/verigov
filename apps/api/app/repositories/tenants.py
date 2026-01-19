from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.models import Tenant


def get_tenant_by_name(db: Session, name: str) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.name == name).one_or_none()


def create_tenant(db: Session, name: str) -> Tenant:
    tenant = Tenant(name=name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant
