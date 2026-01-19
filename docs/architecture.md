# Architecture

- Web SPA (Vite + React) -> FastAPI
- FastAPI persists in Postgres, uses Redis for cache/jobs
- Workers (Celery/RQ) for async checks (planned)

MVP focuses on auth, targets, checks, and snapshot reports.
