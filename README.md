# VeriGov

Plataforma SaaS multi-tenant para compliance automatizado e integracoes governamentais.

## Quickstart

Prereqs: Docker, Docker Compose, Node 20+, Python 3.11+

```bash
make up
```

URLs:
- Web: http://localhost:5174
- API: http://localhost:8001/docs
- Postgres: localhost:55432
- Redis: localhost:56379

## Estrutura

```
apps/
  api/        # FastAPI
  web/        # Vite + React
packages/
  shared/     # tipos e utilitarios (placeholder)
  ui/         # design system (placeholder)
infra/
  compose/    # docker compose
```

## Docs

- Arquitetura: `docs/architecture.md`
- API: `docs/api.md`
- Tecnico: `docs/technical.md`

## MVP atual (estado inicial)

- Auth JWT (register/login/refresh)
- Multi-tenant por tenant_id
- CRUD basico de targets (CNPJ)
- Check de CNPJ com fallback mock
- Relatorio simples (snapshot JSON)
- UI com telas: login, dashboard, targets, detalhe

## Dependencias reais (para producao/staging)

Infra obrigatoria:
- Postgres (dados primarios)
- Redis (cache e fila quando habilitada)

APIs e bases externas (exemplos recomendados):
- CNPJ (MVP): https://publica.cnpj.ws (open). Alternativa enterprise: SERPRO "Dados CNPJ".
- CEIS/CNEP: Portal da Transparencia (token de API).
- Certidao Federal/PGFN/Receita: geralmente exige autenticacao forte; pode precisar certificado digital.
- FGTS (Caixa): nao ha API publica confiavel; costuma exigir RPA/web automation com credenciais.

Web scraping/RPA (quando nao houver API):
- Usar somente onde permitido pelos termos/lei.
- Registrar evidencias (timestamp, payload bruto, screenshot/PDF) para auditoria.
- Implementar backoff, limites e rotacao de IP se necessario.
- Isolar credenciais por tenant e aplicar criptografia em repouso.

## Variaveis de ambiente (API)

- `DATABASE_URL` (ex: `postgresql+psycopg://verigov:verigov@localhost:55432/verigov`)
- `REDIS_URL` (ex: `redis://localhost:56379/0`)
- `JWT_SECRET`
- `JWT_ACCESS_MINUTES`
- `JWT_REFRESH_DAYS`
- `CORS_ORIGINS` (ex: `http://localhost:5174`)
- `USE_MOCK_CONNECTORS` (`true` ou `false`)
- `AUTO_CREATE_TABLES` (`true` em dev)

## Variaveis de ambiente (Web)

- `VITE_API_URL` (ex: `http://localhost:8001`)

## Proximos passos

- Alembic migrations iniciais
- RBAC por rota
- Observabilidade (request_id + logs)
- UI com estados vazios e toasts
# verigov
# verigov
