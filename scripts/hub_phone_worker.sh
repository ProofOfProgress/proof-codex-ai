#!/usr/bin/env bash
# Hub phone worker loop — drain Zernio inbox jobs on all connected phones.
# Run on hub WSL (or via: bash scripts/hub_run.sh bash scripts/hub_phone_worker.sh)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

INTERVAL="${HUB_WORKER_INTERVAL_SEC:-45}"
MAX="${HUB_WORKER_MAX_JOBS:-10}"

echo "Phone hub worker — interval ${INTERVAL}s, max ${MAX} jobs per cycle"
while true; do
  python3 -m shorts_bot.phone_hub.cli tick --confirm --max "$MAX" 2>&1 || true
  sleep "$INTERVAL"
done
