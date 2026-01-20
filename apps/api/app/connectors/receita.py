from __future__ import annotations

from datetime import datetime, timezone
import time

import httpx
import structlog
import redis
import json

from app.core.config import settings
from app.core.utils import normalize_cnpj

logger = structlog.get_logger()
RETRY_STATUSES = {500, 502, 503, 504}
MAX_ATTEMPTS = 3
CACHE_TTL_SECONDS = settings.cnpj_cache_ttl_seconds

_redis_client: redis.Redis | None = None


def _get_redis() -> redis.Redis | None:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        _redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    except Exception as exc:  # pragma: no cover - fallback if redis down
        logger.warning("cnpj_cache_disabled", error=str(exc))
        _redis_client = None
    return _redis_client


def _mock_response(cnpj: str) -> dict:
    return {
        "cnpj": cnpj,
        "razao_social": "ACME TECNOLOGIA LTDA",
        "situacao": "ATIVA",
        "abertura": "2012-05-14",
        "consulta_em": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
    }


def fetch_cnpj(cnpj: str, use_mock: bool = False) -> dict:
    cnpj_clean = normalize_cnpj(cnpj)

    redis_client = _get_redis()
    cache_key = f"cnpj:{cnpj_clean}"
    if redis_client:
        cached = redis_client.get(cache_key)
        if cached:
            logger.info("cnpj_fetch_cache_hit", cnpj=cnpj_clean)
            return json.loads(cached)

    if use_mock:
        logger.info("cnpj_fetch_mock", cnpj=cnpj_clean)
        return _mock_response(cnpj_clean)

    # First attempt: publica.cnpj.ws
    try:
        url = f"https://publica.cnpj.ws/cnpj/{cnpj_clean}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        # Shorten timeout for primary to fail faster to fallback
        timeout = httpx.Timeout(15.0, connect=5.0)

        logger.info("cnpj_fetch_primary_start", source="publica.cnpj.ws", cnpj=cnpj_clean)
        
        with httpx.Client(timeout=timeout, headers=headers, follow_redirects=True, http2=False) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            payload = {
                "cnpj": cnpj_clean,
                "razao_social": data.get("razao_social"),
                "situacao": data.get("estabelecimento", {}).get("situacao_cadastral"),
                "abertura": data.get("estabelecimento", {}).get("data_inicio_atividade"),
                "consulta_em": datetime.now(timezone.utc).isoformat(),
                "source": "publica.cnpj.ws",
                "full_data": data,
            }
            
            if redis_client:
                try:
                    redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(payload))
                except Exception as exc:
                    logger.warning("cnpj_cache_set_failed", cnpj=cnpj_clean, error=str(exc))
            return payload

    except Exception as primary_exc:
        logger.warning(
            "cnpj_fetch_primary_failed",
            cnpj=cnpj_clean,
            error=str(primary_exc),
            detail="Falling back to BrasilAPI"
        )

    # Second attempt: BrasilAPI
    try:
        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_clean}"
        headers = {
             "User-Agent": "VeriGov/1.0",
             "Accept": "application/json",
        }
        timeout = httpx.Timeout(30.0, connect=10.0)
        
        logger.info("cnpj_fetch_fallback_start", source="brasilapi", cnpj=cnpj_clean)

        with httpx.Client(timeout=timeout, headers=headers, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            payload = {
                "cnpj": cnpj_clean,
                "razao_social": data.get("razao_social"),
                "situacao": data.get("descricao_situacao_cadastral"),
                "abertura": data.get("data_inicio_atividade"),
                "consulta_em": datetime.now(timezone.utc).isoformat(),
                "source": "brasilapi",
                "full_data": data,
            }
            
            if redis_client:
                try:
                    redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(payload))
                except Exception as exc:
                    logger.warning("cnpj_cache_set_failed", cnpj=cnpj_clean, error=str(exc))
            return payload

    except Exception as fallback_exc:
        logger.error(
            "cnpj_fetch_fallback_failed",
            cnpj=cnpj_clean,
            error=str(fallback_exc)
        )
        raise fallback_exc
