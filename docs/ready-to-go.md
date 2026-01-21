# Ready-to-Go (Produção)

Panorama do que já foi feito e o que falta para ficar “pronto para vender” (100%).

## Status atual (feito)
- Backend FastAPI em Docker Compose com Postgres/Redis, auth JWT/refresh, RBAC simples, tenancy por `tenant_id`.
- Domínio core: targets/checks/reports; conector CNPJ público com normalização, retries/backoff e cache Redis.
- Logs estruturados com `request_id`; mensagens de erro do conector incluem status/body.
- Migrations iniciais (Alembic) criadas; auto-create ligado apenas para dev.
- Frontend Vite/React: login/register, proteção de rotas, criação de target, execução de check, exibição de relatório, limpeza de sessão e mensagens de erro do backend.
- Infra Compose: serviços expostos (API 8001, Web 5174, DB 55432, Redis 56379); CORS ajustado para o front.
- Docs: README, arquitetura, API (Swagger/OpenAPI), visão técnica.

## Itens restantes (ordem de execução)

1) Confiabilidade e integrações
- [x] Provedor estável de CNPJ com múltiplos fallbacks (publica.cnpj.ws → BrasilAPI → receitaws) e último recurso mock; normalização do CNPJ e headers/timeout agressivo.
- [x] Fila assíncrona opcional (ThreadPool + Redis para status) acionada via `POST /targets/{id}/check?async_mode=true` quando `ASYNC_CHECKS_ENABLED=true`; status em `/jobs/{job_id}`.
- [x] Cache de CNPJ em Redis com TTL configurável, hits/writes contabilizados (`metrics:cnpj_*`) e fallback para mock se permitido.

2) Observabilidade
- [ ] Métricas (Prometheus + Grafana): latência/erro por provedor, acertos de cache, tempo de fila.
- [ ] Tracing (OTel/Jaeger) e logs centralizados (ELK/CloudWatch equivalente OSS).
- [x] Healthchecks enriquecidos (dependências DB/Redis, readiness/liveness).

3) Segurança e tenancy
- [ ] Desligar `AUTO_CREATE_TABLES` em produção; somente Alembic.
- [ ] RLS no Postgres (opcional, mas recomendado); rate limit por tenant/IP no ingress.
- [ ] Segredos em secret manager; HTTPS/ingress; CORS estrito; headers de segurança.
- [ ] Auditoria preenchida por evento (quem/que/onde) e UI de auditoria.

4) Qualidade e QA
- [ ] Testes: unit (serviços), integração (auth/targets/reports), mock HTTP para conectores, e2e feliz (Playwright/Cypress).
- [ ] CI (GitHub Actions): lint/test/build image; opcional scan de dependências/imagens.
- [ ] Seeds/fixtures para demo; scripts de migração e rollback. *(seed básico criado para tenant demo/admin)*

5) Frontend/UX
- [ ] Toasts, skeleton/loading, estados vazios, mensagens de erro de conector visíveis.
- [ ] Refresh token transparente já existe; adicionar aviso de sessão expirada.
- [ ] Opcional SSR/SEO (Next/Remix) se landing/indexação forem necessárias para marketing.

6) Dados e monetização
- [ ] Planos/limites por tenant (rate/quotas) + bloqueio amigável e upsell.
- [ ] Bilhetagem/usage metering (contagem de checks por tenant) e relatórios de consumo.
- [ ] Politica de retenção LGPD e expurgo; mascaramento de documentos em UI/logs.

7) Infra/DX
- [ ] Pipeline de deploy (staging/prod) com compose/k8s; zero-downtime.
- [x] Scripts Make/CLI para migrações/seeds/clean (`make api-revision msg=...`, `api-upgrade`, `api-downgrade`, `api-seed`, `clean`).
- [ ] Backups automatizados (DB/Redis) e runbooks de incidentes.

## Resumo do caminho até 100%
1) Endurecer integrações: provedor estável + fila + cache + fallback controlado.  
2) Observabilidade completa e healthchecks.  
3) Segurança/tenant: RLS, rate limit, secrets/HTTPS, auditoria.  
4) Qualidade/CI: testes e pipeline.  
5) UX/monetização: toasts/estados, limites por plano, billing/usage.  
