from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.models import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).one_or_none()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).one_or_none()


def create_user(db: Session, tenant_id: int, email: str, password_hash: str, role: str) -> User:
    user = User(tenant_id=tenant_id, email=email, password_hash=password_hash, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
