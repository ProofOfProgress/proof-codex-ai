#!/usr/bin/env bash
# Hub: log into Discord web (Playwright headless) then crawl Momentum server channels.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export LD_LIBRARY_PATH="${HOME}/playwright-libs/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
python3 -m shorts_bot.browser.cli login-discord
python3 -m shorts_bot.browser.cli crawl-discord
