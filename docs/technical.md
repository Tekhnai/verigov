# Technical Overview

## Scope
VeriGov is a multi-tenant compliance SaaS focused on fast CNPJ checks first,
then CEIS/CNEP, with production-ready foundations from day one.

## Architecture
- Web SPA (Vite + React) calls FastAPI.
- FastAPI persists to Postgres, caches with Redis, and emits audit logs.
- Workers (Celery/RQ) planned for async checks and scheduled monitoring.

## Backend Modules
- `auth`: login/register/refresh, JWT, roles.
- `tenancy`: tenant isolation enforced by tenant_id.
- `entities`: targets (CNPJ) and check history.
- `connectors`: external API clients and normalization.
- `reports`: summary snapshots.
- `audit`: who did what and when.

## Observability
- Structured JSON logs with request_id.
- Each response includes `x-request-id` for tracing.

## API Docs (Auto)
- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

## External Integrations
Priority order:
1. CNPJ (publica.cnpj.ws or SERPRO Dados CNPJ)
2. CEIS/CNEP (Portal da Transparencia API)
3. Certificates/FGTS (may require credentials or RPA)

## Production Notes
- Use migrations (Alembic) instead of auto-create tables.
- Secrets via env or secret manager.
- Restrict CORS and rate limit per tenant/IP.
