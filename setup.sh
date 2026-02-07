#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required but was not found."
  exit 1
fi

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

VENV_PYTHON=".venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "Virtual environment python not found at $VENV_PYTHON"
  exit 1
fi

"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements.txt

echo "Setup complete."
echo "Activate with: source .venv/bin/activate"
echo "Run with: .venv/bin/python MeteoOverMeshtastic.py"
