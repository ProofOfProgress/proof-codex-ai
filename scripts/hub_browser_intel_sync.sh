#!/usr/bin/env bash
# Run on hub laptop (WSL) after owner logged into Discord web + course site once.
# Read-only — extracts page text to data/research/course/inbox/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 - <<'PY'
from shorts_bot.integrations.hub_browser_intel import sync_hub_browser_inbox
path = sync_hub_browser_inbox(screenshot=True)
print(f"OK — wrote {path}")
PY
