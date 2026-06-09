#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/sync_secrets.py 2>/dev/null || true
bash scripts/backup.sh 2>/dev/null || true

echo "==> Starting Shorts Bot (web + Discord)"
echo "    Web:     http://localhost:8080"
echo "    Discord: python3 -m shorts_bot.discord_bot (if token set)"
echo "    Stop:    Ctrl+C"
echo ""

cleanup() {
  echo ""
  echo "==> Stopping..."
  jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT INT TERM

python3 -m shorts_bot.web &
WEB_PID=$!

if grep -qE '^DISCORD_BOT_TOKEN=.+' .env 2>/dev/null && ! grep -qi 'your-bot-token' .env 2>/dev/null; then
  python3 -m shorts_bot.discord_bot &
  DISCORD_PID=$!
  echo "    Discord bot starting (pid $DISCORD_PID)"
else
  echo "    Discord skipped — add DISCORD_BOT_TOKEN to .env (see docs/MORNING.md)"
fi

wait $WEB_PID
