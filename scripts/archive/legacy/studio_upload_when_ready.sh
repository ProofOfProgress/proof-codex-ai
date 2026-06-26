#!/usr/bin/env bash
# Poll YouTube Studio login, then upload draft #3 (rebrand launch).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=/workspace

DRAFT_ID="${1:-3}"
PACK="data/production/draft_${DRAFT_ID}"

echo "Waiting for YouTube Studio login + ${PACK}/final_short.mp4 …"

while true; do
  if [[ ! -f "${PACK}/final_short.mp4" ]]; then
    echo "$(date -u +%H:%M:%S) missing final_short.mp4 — sleeping 30s"
    sleep 30
    continue
  fi
  if PYTHONPATH=/workspace python3 -m shorts_bot.login_status 2>/dev/null | grep -q "YouTube Studio.*✓"; then
    echo "$(date -u +%H:%M:%S) Studio logged in — uploading draft #${DRAFT_ID}…"
    PYTHONPATH=/workspace python3 -m shorts_bot.production.finish_cli --draft-id "${DRAFT_ID}" --upload
    exit $?
  fi
  echo "$(date -u +%H:%M:%S) not logged in yet — sleeping 45s"
  sleep 45
done
