#!/usr/bin/env bash
# Bubble wrap cron — run on hub laptop every 30–60 min once phones + Zernio are live.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/sync_secrets.py 2>/dev/null || true

# Hub worker: finish inbox drafts on phones (dry-run until UI coords calibrated)
python3 -m shorts_bot.phone_hub.cli tick

# Bubble scheduler: slides → Zernio inbox draft → hub job queue
CONFIRM_FLAG=""
if [[ "${BUBBLE_SCHEDULER_CONFIRM:-}" == "1" || "${BUBBLE_SCHEDULER_CONFIRM:-}" == "true" ]]; then
  CONFIRM_FLAG="--confirm"
fi

ACCOUNT="${BUBBLE_SCHEDULER_ACCOUNT:-}"
EXTRA_ACCOUNT=()
if [[ -n "$ACCOUNT" ]]; then
  EXTRA_ACCOUNT=(--account "$ACCOUNT")
fi

python3 -m shorts_bot.tiktok_shop.factory_cli bubble-sched tick "${EXTRA_ACCOUNT[@]}" $CONFIRM_FLAG
