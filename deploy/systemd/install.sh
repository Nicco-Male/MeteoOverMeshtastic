#!/usr/bin/env bash
set -euo pipefail

if [[ $EUID -ne 0 ]]; then
  echo "This script must be run as root (use sudo)." >&2
  exit 1
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
ENV_FILE="$PROJECT_ROOT/.env"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing .env at $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "$ENV_FILE"
set +a

if [[ -z "${RUN_INTERVAL_HOURS:-}" ]]; then
  echo "RUN_INTERVAL_HOURS is not set in $ENV_FILE" >&2
  exit 1
fi

SERVICE_DEST="/etc/systemd/system/meteo-over-meshtastic.service"
TIMER_DEST="/etc/systemd/system/meteo-over-meshtastic.timer"

sed "s#/path/al/progetto#${PROJECT_ROOT}#g" \
  "$SCRIPT_DIR/meteo-over-meshtastic.service" > "$SERVICE_DEST"

sed "s/@RUN_INTERVAL_HOURS@/${RUN_INTERVAL_HOURS}/g" \
  "$SCRIPT_DIR/meteo-over-meshtastic.timer" > "$TIMER_DEST"

chmod 644 "$SERVICE_DEST" "$TIMER_DEST"

systemctl daemon-reload
systemctl enable --now meteo-over-meshtastic.timer

echo "Installed meteo-over-meshtastic systemd units with interval ${RUN_INTERVAL_HOURS} h."
