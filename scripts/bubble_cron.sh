#!/usr/bin/env bash
# Bubble wrap cron — run on hub laptop every 30–60 min once phones + slides pipeline are live.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/sync_secrets.py 2>/dev/null || true

# Hub worker: finish inbox drafts on phones (dry-run until UI automation ships)
python3 -m shorts_bot.phone_hub.cli tick

# Bubble quota/spacing status (full auto-post: bubble-slides → post-carousel --confirm --enqueue-hub)
ACCOUNT="${BUBBLE_SCHEDULER_ACCOUNT:-}"
if [[ -n "$ACCOUNT" ]]; then
  python3 -c "
from shorts_bot.tiktok_shop.bubble_scheduler import bubble_tick
r = bubble_tick(account_id='${ACCOUNT}', confirm=False)
print(r.action, r.detail)
"
fi
