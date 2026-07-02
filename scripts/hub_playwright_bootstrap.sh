#!/usr/bin/env bash
# One-shot Playwright bootstrap on hub WSL (no sudo).
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"

if ! python3 -m pip --version >/dev/null 2>&1; then
  curl -fsSL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
  python3 /tmp/get-pip.py --user --break-system-packages
fi

python3 -m pip install --user --break-system-packages -r requirements.txt
python3 -m playwright install chromium
bash scripts/hub_playwright_libs.sh >/tmp/pwlibs.env
# shellcheck disable=SC1091
source /tmp/pwlibs.env
python3 -m shorts_bot.browser.cli status
