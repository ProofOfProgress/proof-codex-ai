#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/sync_secrets.py 2>/dev/null || true
exec python3 -m shorts_bot.discord_bot
