#!/usr/bin/env bash
# Daily autonomous grind on hub (cron-friendly). Read-only Discord + intel.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export PHONE_HUB_ADB="${PHONE_HUB_ADB:-/mnt/c/Users/isaac/android-sdk/platform-tools/adb.exe}"

echo "==> Phone status"
bash scripts/hub_adb_windows.sh || true

echo "==> Discord full scrape (Edge must be logged in)"
PYTHONPATH=. python3 scripts/hub_discord_full_scrape.py || true

echo "==> Momentum course deep crawl (weekly)"
bash scripts/hub_course_deep_crawl.sh 50 || true

echo "Done — cloud agent: bash scripts/hub_pull_intel.sh && python3 scripts/process_discord_full.py"
