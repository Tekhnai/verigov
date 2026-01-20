#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="${ROOT_DIR}/.logs"

mkdir -p "${LOG_DIR}"

if [ -f "${LOG_DIR}/compose-api.pid" ]; then
  kill "$(cat "${LOG_DIR}/compose-api.pid")" >/dev/null 2>&1 || true
fi
if [ -f "${LOG_DIR}/compose-web.pid" ]; then
  kill "$(cat "${LOG_DIR}/compose-web.pid")" >/dev/null 2>&1 || true
fi

nohup docker compose -f "${ROOT_DIR}/infra/compose/docker-compose.yml" logs -f --no-log-prefix api \
  > "${LOG_DIR}/compose-api.log" 2>&1 &
echo $! > "${LOG_DIR}/compose-api.pid"

nohup docker compose -f "${ROOT_DIR}/infra/compose/docker-compose.yml" logs -f --no-log-prefix web \
  > "${LOG_DIR}/compose-web.log" 2>&1 &
echo $! > "${LOG_DIR}/compose-web.pid"

echo "Saving logs to ${LOG_DIR}/compose-api.log and ${LOG_DIR}/compose-web.log"
