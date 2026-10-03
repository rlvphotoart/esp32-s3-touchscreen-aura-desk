#!/bin/bash
source "$(dirname "$0")/common.sh"
exec "$PY" "$ROOT/tools/device_inventory.py" "$@"
