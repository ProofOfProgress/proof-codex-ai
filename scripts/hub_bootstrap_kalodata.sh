#!/usr/bin/env bash
# One-time hub setup for Kalodata scout (run ON the HP in WSL).
set -euo pipefail
cd "$(dirname "$0")/.."

export PATH="$HOME/.local/bin:$PATH"
PIP_USER=(python3 -m pip install --user)
PIP_BREAK=(--break-system-packages)

echo "==> Kalodata hub scout bootstrap"

if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "Installing pip (no sudo — Debian PEP 668 workaround)..."
  curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
  python3 /tmp/get-pip.py --user "${PIP_BREAK[@]}"
fi

echo "==> Installing Python deps (user install)..."
"${PIP_USER[@]}" "${PIP_BREAK[@]}" -r requirements.txt

echo "==> Installing Playwright Chromium..."
python3 -m playwright install chromium

if [[ -x scripts/hub_playwright_libs.sh ]]; then
  echo "==> Installing Playwright system libs (no sudo)..."
  eval "$(bash scripts/hub_playwright_libs.sh | tail -1)"
  if ! LD_LIBRARY_PATH="${LD_LIBRARY_PATH:-}" python3 -m shorts_bot.browser.cli status >/dev/null 2>&1; then
    echo "WARN: Playwright may still need: sudo apt install python3-pip (see docs)"
  fi
fi

chmod +x scripts/hub_kalodata_login.sh scripts/scout_on_hub.sh 2>/dev/null || true

echo ""
echo "==> Next (owner):"
echo "  1. bash scripts/hub_kalodata_login.sh     # log into Kalodata"
echo "  2. Apply filters in Kalodata → copy URL →:"
echo "     python3 scripts/kalodata_set_filter_url.py middle_core 'PASTE_URL_HERE'"
echo "  3. bash scripts/scout_on_hub.sh run --preset middle_core --limit 10"
echo ""
echo "Guide: docs/FOR_OWNER_KALODATA_HUB_SETUP.md"
