#!/bin/bash
source "$(dirname "$0")/common.sh"
PORT="$(choose_port)"
DEST="$ROOT/backups/$(TZ=Europe/Bucharest date '+%Y%m%d-%H%M%S')"
printf 'Backup port: %s\nOutput: %s\nThis enters ROM download mode, checks MAC/security/flash, and reads flash only.\n' "$PORT" "$DEST"
exec "$PY" -u "$ROOT/tools/backup_device.py" --port "$PORT" --output-directory "$DEST" --baud 115200 --verify-erased
