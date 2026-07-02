#!/usr/bin/env bash
# Hub: log into Momentum Academy via Playwright (DOM — no vision).
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export LD_LIBRARY_PATH="${HOME}/playwright-libs/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
python3 - <<'PY'
from shorts_bot.browser.course_session import login_and_save_session

profile = login_and_save_session(headless=True)
print(f"OK — session saved: {profile}")
PY
