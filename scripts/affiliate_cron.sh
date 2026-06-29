#!/usr/bin/env bash
# Affiliate auto-poster — run every 30 minutes from cron on an ALWAYS-ON machine.
# Do NOT rely on Cursor automations for this; they do not keep a VM running.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/sync_secrets.py 2>/dev/null || true

ACCOUNT="${TIKTOK_SHOP_SCHEDULER_ACCOUNT:-affiliate_main}"
python3 -m shorts_bot.tiktok_shop.factory_cli scheduler tick --account "$ACCOUNT" --confirm
