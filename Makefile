SHELL := /bin/bash

.PHONY: up down api-shell api-migrate web-dev test

up:
	docker compose -f infra/compose/docker-compose.yml up --build

down:
	docker compose -f infra/compose/docker-compose.yml down

api-shell:
	docker compose -f infra/compose/docker-compose.yml exec api bash

api-migrate:
	docker compose -f infra/compose/docker-compose.yml exec api alembic upgrade head

web-dev:
	cd apps/web && npm run dev

test:
	cd apps/api && pytest -q
