#!/usr/bin/env bash
# Hub: log into Momentum Academy via Playwright (DOM — no vision).
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"
export LD_LIBRARY_PATH="${HOME}/playwright-libs/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}"
python3 - <<'PY'
from shorts_bot.browser.course_session import login_and_save_session, crawl_visible_text
from pathlib import Path

profile = login_and_save_session(headless=True)
print(f"OK — session saved: {profile}")
text = crawl_visible_text(max_chars=2000)
out = Path("data/research/course/inbox/momentum-login-check.txt")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(text, encoding="utf-8")
print(f"Sample text ({len(text)} chars) -> {out}")
print(text[:800])
PY
