#!/usr/bin/env bash
set -euo pipefail

API_PORT=${API_PORT:-8002}
WEB_PORT=${WEB_PORT:-5174}
DB_PORT=${DB_PORT:-55432}
REDIS_PORT=${REDIS_PORT:-56379}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/.logs"

mkdir -p "${LOG_DIR}"

if command -v docker >/dev/null 2>&1; then
  if ! docker ps --format '{{.Names}}' | grep -q '^verigov-db$'; then
    if docker ps -a --format '{{.Names}}' | grep -q '^verigov-db$'; then
      docker start verigov-db
    else
      docker run -d --name verigov-db \
        -e POSTGRES_DB=verigov \
        -e POSTGRES_USER=verigov \
        -e POSTGRES_PASSWORD=verigov \
        -p "${DB_PORT}:5432" postgres:15
    fi
  fi

  if ! docker ps --format '{{.Names}}' | grep -q '^verigov-redis$'; then
    if docker ps -a --format '{{.Names}}' | grep -q '^verigov-redis$'; then
      docker start verigov-redis
    else
      docker run -d --name verigov-redis -p "${REDIS_PORT}:6379" redis:7
    fi
  fi
else
  echo "Docker not found. Please start Postgres and Redis manually." >&2
fi

export POETRY_VIRTUALENVS_IN_PROJECT=true

if [ ! -d "${ROOT_DIR}/apps/api/.venv" ]; then
  (cd "${ROOT_DIR}/apps/api" && poetry install --only main --no-root)
fi

if ! pgrep -f "uvicorn app.main:app --host 0.0.0.0 --port ${API_PORT}" >/dev/null 2>&1; then
  (
    cd "${ROOT_DIR}/apps/api"
    DATABASE_URL="postgresql+psycopg://verigov:verigov@localhost:${DB_PORT}/verigov" \
    REDIS_URL="redis://localhost:${REDIS_PORT}/0" \
    JWT_SECRET="dev-secret-change" \
    JWT_ACCESS_MINUTES="15" \
    JWT_REFRESH_DAYS="7" \
    CORS_ORIGINS="http://localhost:${WEB_PORT}" \
    USE_MOCK_CONNECTORS="true" \
    nohup poetry run uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT}" \
      > "${LOG_DIR}/api.log" 2>&1 &
    echo $! > "${LOG_DIR}/api.pid"
  )
fi

if [ ! -d "${ROOT_DIR}/apps/web/node_modules" ]; then
  (cd "${ROOT_DIR}/apps/web" && npm install)
fi

if ! pgrep -f "vite --host 0.0.0.0 --port ${WEB_PORT}" >/dev/null 2>&1; then
  (
    cd "${ROOT_DIR}/apps/web"
    VITE_API_URL="http://localhost:${API_PORT}" \
    nohup npm run dev -- --host 0.0.0.0 --port "${WEB_PORT}" \
      > "${LOG_DIR}/web.log" 2>&1 &
    echo $! > "${LOG_DIR}/web.pid"
  )
fi

echo "API running on http://localhost:${API_PORT}/docs"
echo "Web running on http://localhost:${WEB_PORT}/"
