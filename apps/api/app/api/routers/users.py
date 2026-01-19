from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.auth import UserOut

router = APIRouter(tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)) -> UserOut:
    return current_user
