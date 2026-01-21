from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import require_roles
from app.services.job_queue import get_job_state

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}")
def get_job(job_id: str, current_user=Depends(require_roles("admin", "analyst"))) -> dict:
    state = get_job_state(job_id)
    if not state:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return state
