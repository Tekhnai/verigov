from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def _encode(payload: dict[str, Any], expires_delta: timedelta) -> str:
    expire_at = datetime.now(timezone.utc) + expires_delta
    payload["exp"] = expire_at
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_access_token(subject: str, tenant_id: int, role: str) -> str:
    return _encode(
        {"sub": subject, "tenant_id": tenant_id, "role": role, "type": "access"},
        timedelta(minutes=settings.jwt_access_minutes),
    )


def create_refresh_token(subject: str, tenant_id: int, role: str) -> str:
    return _encode(
        {"sub": subject, "tenant_id": tenant_id, "role": role, "type": "refresh"},
        timedelta(days=settings.jwt_refresh_days),
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
