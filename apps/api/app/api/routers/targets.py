from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.repositories.targets import create_target, get_target, list_targets
from app.schemas.targets import TargetCreate, TargetOut
from app.services.check_service import run_cnpj_check

router = APIRouter(prefix="/targets", tags=["targets"])


@router.post("", response_model=TargetOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: TargetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "analyst")),
) -> TargetOut:
    target = create_target(
        db,
        tenant_id=current_user.tenant_id,
        document=payload.document,
        name_hint=payload.name_hint,
        target_type=payload.type,
    )
    return target


@router.get("", response_model=list[TargetOut])
def list_all(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "analyst")),
) -> list[TargetOut]:
    return list_targets(db, tenant_id=current_user.tenant_id)


@router.post("/{target_id}/check")
def run_check(
    target_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "analyst")),
) -> dict:
    target = get_target(db, current_user.tenant_id, target_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")
    summary = run_cnpj_check(db, current_user.tenant_id, target.id, target.document)
    return {"status": "ok", "summary": summary}
