#!/usr/bin/env python3
"""List agent_credentials.env keys on hub (no values)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.agent_credentials import credential_keys, load_agent_credentials
from shorts_bot.config import settings
from shorts_bot.tiktok_shop import kalodata_client


def main() -> int:
    load_agent_credentials()
    keys = credential_keys()
    print("credential_keys:", ", ".join(keys) or "(none)")
    print("kalodata_pilot:", kalodata_client.configured())
    print("gemini:", bool((settings.gemini_api_key or "").strip()))
    print("has_gemini:", settings.has_gemini)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
