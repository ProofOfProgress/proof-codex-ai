#!/usr/bin/env bash
# Start Edge with remote debugging so Playwright attaches to owner's Kalodata login.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m shorts_bot.hub_remote run -- \
  'powershell.exe -NoProfile -Command "Start-Process msedge -ArgumentList ''--remote-debugging-port=9222'',''https://www.kalodata.com/product''"'
echo "Edge CDP port 9222 — wait 5s then retry scout"
