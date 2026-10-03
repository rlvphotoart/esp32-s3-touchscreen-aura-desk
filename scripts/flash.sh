#!/bin/bash
source "$(dirname "$0")/common.sh"
PORT="$(choose_port)"
printf 'Selected device: %s\n' "$PORT"
exec "$PY" "$ROOT/tools/flash_aura.py" --port "$PORT" --backup "${AURA_BACKUP:-$ROOT/backups/pre-aura-20261003}" "$@"
