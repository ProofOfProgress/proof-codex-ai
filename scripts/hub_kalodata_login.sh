#!/usr/bin/env bash
# Owner: one double-click path to log into Kalodata on the hub (saves session for scout).
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Opening Kalodata in browser — log in, then close the window when done."
echo "Session saves to data/browser_profile/kalodata/"
python3 -m shorts_bot.browser.cli open kalodata --minutes 15
echo "Done. Next: paste filter URLs — see docs/FOR_OWNER_KALODATA_HUB_SETUP.md"
