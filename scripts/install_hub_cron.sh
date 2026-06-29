#!/usr/bin/env bash
# Install affiliate post cron on this machine (HP hub laptop or any always-on Linux).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
CRON_LINE="*/30 * * * * cd ${REPO} && bash scripts/affiliate_cron.sh >> ${REPO}/data/tiktok_shop/scheduler.log 2>&1"

echo "This installs a cron job that runs every 30 minutes:"
echo "  $CRON_LINE"
echo ""
read -r -p "Install on THIS machine? [y/N] " ans
if [[ "${ans,,}" != "y" ]]; then
  echo "Cancelled. Copy the line above into: crontab -e"
  exit 0
fi

mkdir -p "${REPO}/data/tiktok_shop"
( crontab -l 2>/dev/null | grep -v 'affiliate_cron.sh' || true
  echo "$CRON_LINE"
) | crontab -

echo "Installed. Verify with: crontab -l"
echo "Logs: ${REPO}/data/tiktok_shop/scheduler.log"
echo "Status: python3 -m shorts_bot.tiktok_shop.factory_cli scheduler status"
