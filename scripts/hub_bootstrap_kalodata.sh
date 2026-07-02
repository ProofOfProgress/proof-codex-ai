#!/usr/bin/env bash
# One-time hub setup for Kalodata scout (run ON the HP in WSL).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Kalodata hub scout bootstrap"

if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "Installing pip..."
  python3 -m ensurepip --user || true
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "==> Installing Python deps (user install)..."
python3 -m pip install --user -r requirements.txt

echo "==> Installing Playwright Chromium..."
python3 -m playwright install chromium

chmod +x scripts/hub_kalodata_login.sh scripts/scout_on_hub.sh 2>/dev/null || true

echo ""
echo "==> Next (owner):"
echo "  1. bash scripts/hub_kalodata_login.sh     # log into Kalodata"
echo "  2. Apply filters in Kalodata → copy URL →:"
echo "     python3 scripts/kalodata_set_filter_url.py middle_core 'PASTE_URL_HERE'"
echo "  3. bash scripts/scout_on_hub.sh run --preset middle_core --limit 10"
echo ""
echo "Guide: docs/FOR_OWNER_KALODATA_HUB_SETUP.md"
