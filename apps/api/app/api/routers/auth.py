from __future__ import annotations

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.services.auth_service import login_user, register_user
from app.repositories.users import get_user_by_id
from app.services.audit_service import log_event

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access, refresh, _user_id = register_user(db, payload.email, payload.password, payload.tenant_name)
    log_event(db, tenant_id=1, user_id=_user_id, action="register", metadata={"email": payload.email})  # tenant created on the fly
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    access, refresh, _user_id = login_user(db, payload.email, payload.password)
    user = get_user_by_id(db, _user_id)
    log_event(db, tenant_id=user.tenant_id, user_id=user.id, action="login", metadata={"email": payload.email})
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        data = decode_token(payload.refresh_token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user = get_user_by_id(db, int(data["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")

    access = create_access_token(str(user.id), user.tenant_id, user.role)
    refresh_token = create_refresh_token(
        str(user.id), user.tenant_id, user.role
    )
    return TokenResponse(access_token=access, refresh_token=refresh_token)
