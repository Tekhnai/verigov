SHELL := /bin/bash

.PHONY: up down api-shell api-migrate web-dev test clean api-revision api-upgrade api-downgrade api-seed

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

clean:
	rm -rf apps/web/node_modules
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
	rm -f .logs/*.log .logs/*.pid

api-revision:
	cd apps/api && alembic revision --autogenerate -m "$(msg)"

api-upgrade:
	cd apps/api && alembic upgrade head

api-downgrade:
	cd apps/api && alembic downgrade -1

api-seed:
	cd apps/api && DATABASE_URL=postgresql+psycopg://verigov:verigov@localhost:55432/verigov \
		REDIS_URL=redis://localhost:56379/0 \
		JWT_SECRET=dev-secret-change \
		poetry run python -m app.scripts.seed
