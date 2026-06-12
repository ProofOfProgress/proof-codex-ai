#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/sync_secrets.py 2>/dev/null || true
bash scripts/backup.sh 2>/dev/null || true

echo "==> Starting Shorts Bot (web UI)"
echo "    Open: http://localhost:8080"
echo "    Stop: Ctrl+C"
echo ""

exec python3 -m shorts_bot.web
