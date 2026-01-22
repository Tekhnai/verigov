from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.repositories.targets import create_target, get_target, list_targets
from app.schemas.targets import TargetCreate, TargetOut
from app.services.check_service import run_cnpj_check
from app.services.job_queue import enqueue_check_job
from app.core.config import settings
from app.services.audit_service import log_event

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
    log_event(db, current_user.tenant_id, current_user.id, "target_create", {"target_id": target.id})
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
    async_mode: bool = Query(default=False, description="Executar check de forma assíncrona"),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "analyst")),
) -> dict:
    target = get_target(db, current_user.tenant_id, target_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found")

    if async_mode and settings.async_checks_enabled:
        job_id = enqueue_check_job(current_user.tenant_id, target.id, target.document)
        log_event(db, current_user.tenant_id, current_user.id, "check_enqueue", {"target_id": target.id})
        return {"status": "queued", "job_id": job_id}

    summary = run_cnpj_check(db, current_user.tenant_id, target.id, target.document)
    log_event(db, current_user.tenant_id, current_user.id, "check_run", {"target_id": target.id, "status": summary.get("status")})
    return {"status": "ok", "summary": summary}
