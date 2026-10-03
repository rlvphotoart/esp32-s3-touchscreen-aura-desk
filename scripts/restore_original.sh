#!/bin/bash
source "$(dirname "$0")/common.sh"
PORT="$(choose_port)"
printf 'Restore target port: %s\nDefault is a local review; no hardware is opened unless --execute is explicit.\n' "$PORT"
exec "$PY" "$ROOT/tools/restore_original.py" --port "$PORT" "$@"
