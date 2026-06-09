#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Starting Shorts Bot web UI..."
echo "    Open: http://localhost:8080"
echo "    Stop: Ctrl+C"
echo ""

python3 -m shorts_bot.web
