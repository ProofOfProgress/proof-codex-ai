#!/usr/bin/env bash
# Pull hub intel (inbox + weekly drop + discord full shots manifest)
set -euo pipefail
cd "$(dirname "$0")/.."
# shellcheck disable=SC1091
source "$(dirname "$0")/hub_lib.sh"
hub_lib_init
hub_ensure_connected || exit 1

REMOTE="cd ~/proof-codex-ai && tar czf - \
  data/research/course/inbox/momentum-deep \
  data/research/course/inbox/momentum-deep-crawl-*.md \
  data/research/course/inbox/discord-crawl-*.md \
  data/research/course/inbox/discord-desktop-crawl-*.md \
  data/research/course/inbox/discord-full-crawl-*.md \
  data/research/course/inbox/momentum-crawl-*.md \
  data/tiktok_shop/momentum_weekly_drop.json \
  data/tiktok_shop/scout_report.txt \
  data/phone_hub/devices.json \
  2>/dev/null || true"

echo "==> Pulling intel from hub..."
hub_run_ssh "$REMOTE" | tar xzf - -C .
echo "OK — synced hub intel into $(pwd)"
