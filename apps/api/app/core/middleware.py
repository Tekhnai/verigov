from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.metrics import record_request
from app.core.config import settings
import redis
from redis.exceptions import RedisError

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        start = time.monotonic()
        logger = structlog.get_logger()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = int((time.monotonic() - start) * 1000)
            logger.exception(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
            )
            raise

        duration_ms = int((time.monotonic() - start) * 1000)
        response.headers["x-request-id"] = request_id
        logger.info(
            "request_complete",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        record_request(request.method, request.url.path, response.status_code, duration_ms / 1000)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._store: dict[str, list[float]] = {}
        try:
            self._redis = redis.Redis.from_url(settings.redis_url)
        except Exception:
            self._redis = None

    async def dispatch(self, request: Request, call_next):
        import time

        ip = request.client.host if request.client else "unknown"
        tenant_id = getattr(request.state, "tenant_id", None)
        now = time.time()
        window_start = now - 60

        # Prefer Redis for distributed limiting
        if self._redis:
            try:
                keys = [f"ratelimit:ip:{ip}"]
                if tenant_id:
                    keys.append(f"ratelimit:tenant:{tenant_id}")
                for key in keys:
                    count = self._redis.incr(key)
                    if count == 1:
                        self._redis.expire(key, 60)
                    limit = settings.rate_limit_per_minute_tenant if "tenant" in key else self.requests_per_minute
                    if count > limit:
                        from starlette.responses import JSONResponse

                        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
            except RedisError:
                pass  # fallback to in-memory

        # In-memory fallback per IP
        entries = self._store.get(ip, [])
        entries = [ts for ts in entries if ts >= window_start]
        if len(entries) >= self.requests_per_minute:
            from starlette.responses import JSONResponse

            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        entries.append(now)
        self._store[ip] = entries
        return await call_next(request)
