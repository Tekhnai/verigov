from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import redis
import structlog

from app.core.config import settings
from app.db.session import SessionLocal

logger = structlog.get_logger()

_executor: ThreadPoolExecutor | None = None
_redis_client: redis.Redis | None = None
JOB_TTL_SECONDS = 3600 * 6  # 6h para acompanhar checks em filas curtas


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=settings.async_max_workers)
    return _executor


def _get_redis() -> redis.Redis | None:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        _redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    except Exception as exc:  # pragma: no cover - fallback if redis down
        logger.warning("job_queue_redis_disabled", error=str(exc))
        _redis_client = None
    return _redis_client


def _set_job_state(job_id: str, status: str, payload: dict | None = None, error: str | None = None) -> None:
    redis_client = _get_redis()
    data = {"status": status}
    if payload is not None:
        data["payload"] = payload
    if error is not None:
        data["error"] = error
    if redis_client:
        try:
            redis_client.setex(f"job:{job_id}", JOB_TTL_SECONDS, json.dumps(data))
            return
        except Exception as exc:  # pragma: no cover - log only
            logger.warning("job_state_set_failed", job_id=job_id, error=str(exc))
    logger.info("job_state", job_id=job_id, status=status, payload=payload, error=error)


def get_job_state(job_id: str) -> dict | None:
    redis_client = _get_redis()
    if redis_client:
        data = redis_client.get(f"job:{job_id}")
        if data:
            return json.loads(data)
    return None


def enqueue_check_job(tenant_id: int, target_id: int, document: str) -> str:
    job_id = uuid4().hex
    _set_job_state(job_id, "queued")

    def _task() -> None:
        db = SessionLocal()
        try:
            from app.services.check_service import run_cnpj_check  # local import to avoid cycle

            _set_job_state(job_id, "running")
            summary = run_cnpj_check(db, tenant_id, target_id, document)
            _set_job_state(job_id, "done", payload={"summary": summary})
        except Exception as exc:  # pragma: no cover - error path
            logger.error("job_failed", job_id=job_id, error=str(exc))
            _set_job_state(job_id, "error", error=str(exc))
        finally:
            db.close()

    _get_executor().submit(_task)
    return job_id
