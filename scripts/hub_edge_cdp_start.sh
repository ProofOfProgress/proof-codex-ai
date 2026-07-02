#!/usr/bin/env bash
# Start Edge with remote debugging so Playwright attaches to owner's Kalodata login.
# Run ONCE per Windows boot (or when Edge was opened without debug port).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 -m shorts_bot.hub_remote run -- \
  'cmd.exe /c start "" msedge --remote-debugging-port=9222 https://www.kalodata.com/product'
echo "Edge CDP on port 9222 — Playwright will attach automatically (KALODATA_EDGE_CDP=auto)"
