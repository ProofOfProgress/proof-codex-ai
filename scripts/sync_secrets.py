#!/usr/bin/env python3
"""Copy API keys from environment variables into .env (if set)."""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
EXAMPLE_PATH = ROOT / ".env.example"

SYNC_VARS = (
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "DISCORD_BOT_TOKEN",
    "DISCORD_PUBLIC_KEY",
    "DISCORD_OWNER_ID",
    "DISCORD_NOTIFY_IDS",
)

PLACEHOLDER_FRAGMENTS = (
    "your-key",
    "your-client-id",
    "your-client-secret",
    "your-bot-token",
    "your-discord",
    "paste-your",
    "here",
)


def _is_real_value(key: str, value: str) -> bool:
    v = value.strip()
    if not v:
        return False
    lower = v.lower()
    if any(p in lower for p in PLACEHOLDER_FRAGMENTS):
        return False
    if key == "OPENAI_API_KEY" and not v.startswith("sk-"):
        return False
    return True


def _ensure_env_file() -> None:
    if ENV_PATH.exists():
        return
    if EXAMPLE_PATH.exists():
        ENV_PATH.write_text(EXAMPLE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        ENV_PATH.write_text("", encoding="utf-8")


def _upsert(lines: list[str], key: str, value: str) -> list[str]:
    pattern = re.compile(rf"^{re.escape(key)}=.*$")
    replaced = False
    out: list[str] = []
    for line in lines:
        if pattern.match(line):
            out.append(f"{key}={value}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        if out and out[-1].strip():
            out.append("")
        out.append(f"{key}={value}")
    return out


def sync(*, quiet: bool = False) -> list[str]:
    """Return list of keys written to .env."""
    _ensure_env_file()
    text = ENV_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    written: list[str] = []

    for key in SYNC_VARS:
        raw = os.environ.get(key)
        if raw is None or not _is_real_value(key, raw):
            continue
        lines = _upsert(lines, key, raw.strip())
        written.append(key)

    if written:
        ENV_PATH.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        if not quiet:
            print(f"  synced to .env: {', '.join(written)}")
    elif not quiet:
        print("  no secrets in environment to sync")

    return written


def main() -> None:
    sync(quiet=False)


if __name__ == "__main__":
    main()
