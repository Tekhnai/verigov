from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.repositories.tenants import create_tenant, get_tenant_by_name
from app.repositories.users import create_user, get_user_by_email


def register_user(db: Session, email: str, password: str, tenant_name: str) -> tuple[str, str, int]:
    if get_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if get_tenant_by_name(db, tenant_name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant already exists")

    tenant = create_tenant(db, tenant_name)
    user = create_user(db, tenant.id, email, hash_password(password), role="admin")

    access = create_access_token(str(user.id), tenant.id, user.role)
    refresh = create_refresh_token(str(user.id), tenant.id, user.role)
    return access, refresh, user.id


def login_user(db: Session, email: str, password: str) -> tuple[str, str, int]:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not active")

    access = create_access_token(str(user.id), user.tenant_id, user.role)
    refresh = create_refresh_token(str(user.id), user.tenant_id, user.role)
    return access, refresh, user.id
