#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
ENV_FILE="$PROJECT_ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_FILE"
  set +a
fi

if [[ -n "${RUN_INTERVAL_HOURS:-}" ]]; then
  echo "[meteo-over-meshtastic] RUN_INTERVAL_HOURS=${RUN_INTERVAL_HOURS}" >&2
fi

exec "$PROJECT_ROOT/.venv/bin/python" "$PROJECT_ROOT/MeteoOverMeshtastic.py"
