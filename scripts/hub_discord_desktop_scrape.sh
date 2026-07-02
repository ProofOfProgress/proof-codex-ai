#!/usr/bin/env bash
# Hub: scrape Discord from logged-in Edge (desktop helper + Gemini). Read-only.
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
python3 -m shorts_bot.integrations.discord_desktop_scrape --scroll "${1:-50}" --every "${2:-2}"
