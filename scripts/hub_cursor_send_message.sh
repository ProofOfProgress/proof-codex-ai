#!/usr/bin/env bash
# Cloud agent: type a message into Cursor chat on the hub and click Send.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python3 "$ROOT/scripts/hub_cursor_send.py" "$@"
