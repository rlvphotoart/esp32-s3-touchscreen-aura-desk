#!/bin/bash
source "$(dirname "$0")/common.sh"
PORT="$(choose_port)"
DEST="$ROOT/logs/serial-$(TZ=Europe/Bucharest date '+%Y%m%d-%H%M%S').bin"
printf 'Receive-only capture: %s at 115200 baud\nPrivate raw log: %s\n' "$PORT" "$DEST"
exec "$PY" "$ROOT/tools/capture_serial.py" --port "$PORT" --baud 115200 --seconds "${1:-30}" --output "$DEST"
