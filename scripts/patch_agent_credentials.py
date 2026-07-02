#!/usr/bin/env python3
"""Patch gitignored agent_credentials.env on hub (never commit values)."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRED = ROOT / "data" / "agent_credentials.env"


def upsert(text: str, key: str, val: str) -> str:
    line = f"{key}={val}"
    pat = re.compile(rf"^{re.escape(key)}=.*$", re.M)
    if pat.search(text):
        return pat.sub(line, text)
    return text.rstrip() + "\n" + line + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--key", required=True)
    p.add_argument("--value", required=True)
    args = p.parse_args()
    text = CRED.read_text(encoding="utf-8") if CRED.is_file() else ""
    text = upsert(text, args.key, args.value)
    CRED.parent.mkdir(parents=True, exist_ok=True)
    CRED.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    CRED.chmod(0o600)
    print(f"OK {args.key} → {CRED}")


if __name__ == "__main__":
    main()
