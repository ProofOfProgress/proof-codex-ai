#!/usr/bin/env bash
# One-phone hub setup — bind USB serial, init coords, smoke-test worker.
# Run on hub laptop Ubuntu (or: bash scripts/hub_run.sh bash scripts/hub_one_phone_setup.sh phone_1)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SLOT="${1:-phone_1}"

echo ""
echo "  PROOF CODEX — ONE PHONE SETUP ($SLOT)"
echo ""

if ! command -v adb >/dev/null 2>&1; then
  echo "  Installing adb..."
  bash scripts/hub_adb_install.sh
fi

echo "  Step 1 — bind USB serial → $SLOT"
python3 -m shorts_bot.phone_hub.cli setup-phone --slot "$SLOT" --serial auto

echo ""
echo "  Step 2 — readiness check"
python3 -m shorts_bot.phone_hub.cli readiness --slot "$SLOT"

echo ""
echo "  Step 3 — dry-run worker (no TikTok taps)"
python3 -m shorts_bot.phone_hub.cli test-job --slot "$SLOT" --type bubble --run

echo ""
echo "  DONE — one phone wired in software."
echo ""
echo "  When a real Zernio inbox draft exists on this phone:"
echo "    python3 -m shorts_bot.phone_hub.cli tick --slot $SLOT --confirm"
echo ""
