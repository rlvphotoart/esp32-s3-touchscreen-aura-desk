#!/bin/bash
source "$(dirname "$0")/common.sh"
exec "$PY" "$ROOT/tools/verify_backup.py" "${1:-$ROOT/backups}"
