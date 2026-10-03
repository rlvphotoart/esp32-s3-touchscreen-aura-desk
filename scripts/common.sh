#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$ROOT/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Missing inspection environment. Follow docs/SETUP.md." >&2
  exit 1
fi
choose_port() {
  if [[ -n "${ESP32_PORT:-}" ]]; then
    printf '%s\n' "$ESP32_PORT"
  else
    "$PY" "$ROOT/tools/device_inventory.py" --port-only
  fi
}
