#!/usr/bin/env bash
# Server-side equivalent of Cursor /loop — runs daily ship every 24h on this machine.
set -euo pipefail
cd "$(dirname "$0")/.."

LOG="${DAILY_LOOP_LOG:-data/daily_loop.log}"
INTERVAL="${DAILY_LOOP_INTERVAL_SEC:-86400}"

mkdir -p data
echo "=== daily_loop started $(date -u +%Y-%m-%dT%H:%M:%SZ) interval=${INTERVAL}s ===" | tee -a "$LOG"

while true; do
  echo "--- tick $(date -u +%Y-%m-%dT%H:%M:%SZ) ---" | tee -a "$LOG"
  if python3 -m shorts_bot.production.invideo_daily_cli >>"$LOG" 2>&1; then
    echo "OK $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a "$LOG"
  else
    echo "FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ) exit=$?" | tee -a "$LOG"
  fi
  echo "sleep ${INTERVAL}s …" | tee -a "$LOG"
  sleep "$INTERVAL"
done
