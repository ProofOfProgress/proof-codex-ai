#!/usr/bin/env python3
"""Copy API keys from Cursor secrets / environment into .env (if set)."""

from __future__ import annotations

import os
import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
EXAMPLE_PATH = ROOT / ".env.example"

# Keys synced from Cursor secrets — user never hand-edits these if secrets are set.
SYNC_VARS = (
    "CURSOR_API_KEY",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "ASSEMBLYAI_API_KEY",
    "WEB_API_TOKEN",
    "RESEMBLE_API_KEY",
    "RESEMBLE_VOICE_UUID",
    "RESEMBLE_PROJECT_UUID",
    "TTS_PROVIDER",
    "REPLICATE_API_TOKEN",
    "SLACK_BOT_TOKEN",
    "SLACK_CHANNEL_ID",
    "SLACK_WEBHOOK_URL",
    "SLACK_CHANNEL_EMAIL",
    "SLACK_POST_MODE",
    "GMAIL_SMTP_USER",
    "GMAIL_SMTP_APP_PASSWORD",
    "SLACK_CURSOR_LINKED",
    "SLACK_CHANNEL_NAME",
    "SLACK_APP_TOKEN",
    "SLACK_AUTONOMY_ENABLED",
    "FAL_API_KEY",
    "IMAGE_PROVIDER",
    "VISUAL_STYLE",
    "REPLICATE_VIDEO_MODEL",
    "AI_VIDEO_GENERATION_ENABLED",
    "VIDEO_BACKEND",
    "KLING_ACCESS_KEY",
    "KLING_SECRET_KEY",
    "KLING_API_KEY",
    "KLING_PROVIDER",
    "KLING_MODEL",
    "KLING_CLIP_SECONDS",
    "KLING_CLIPS_PER_SHORT",
    "KLING_GENERATE_AUDIO",
    "KLING_SKIP_NARRATOR_TTS",
    "KLING_MODE",
    "KLING_ASPECT_RATIO",
    "KLING_MULTI_SHOT",
    "TIKTOK_CLIENT_KEY",
    "TIKTOK_CLIENT_SECRET",
    "ZERNIO_API_KEY",
    "ZERNIO_API_TOKEN",
    "ECHOTIK_USERNAME",
    "ECHOTIK_PASSWORD",
    "ECHOTIK_REGION",
    "FASTMOSS_CLIENT_ID",
    "FASTMOSS_CLIENT_SECRET",
    "FASTMOSS_API_BASE",
    "PRINTIFY_API_TOKEN",
    "PRINTIFY_SHOP_ID",
    "INVIDEO_API_KEY",
    "GOOGLE_DRIVE_FOLDER_ID",
    "GOOGLE_DRIVE_INBOX_ENABLED",
)

# Sensible production defaults — written only when the key is absent from .env.
DEFAULT_ENV: dict[str, str] = {
    "TRANSCRIPT_PROVIDER": "gemini",
    "TRANSCRIPT_ALWAYS_FRESH": "false",
    "VISION_QC_ENABLED": "true",
    "VISION_QC_BLOCKS_UPLOAD": "true",
    "VISION_QC_MIN_SCORE": "7",
    "AUTO_PUBLISH_HOURS": "0",
    "YOUTUBE_UPLOAD_VISIBILITY": "public",
    "YOUTUBE_DECLARE_SYNTHETIC_MEDIA": "true",
    "AI_DETECT_THRESHOLD": "5",
    "AI_DETECT_MAX_PASSES": "10",
    "AI_DETECT_BLOCKS_RENDER": "true",
    "REQUIRE_PAID_STACK": "true",
    "ALLOW_SCRIPT_TIMING_FALLBACK": "false",
    "VISUAL_STYLE": "ai_video",
    "VIDEO_BACKEND": "blender",
    "KLING_PROVIDER": "official",
    "AI_VIDEO_GENERATION_ENABLED": "false",
    "KLING_MODEL": "kling-v2-6",
    "KLING_CLIP_SECONDS": "15",
    "KLING_CLIPS_PER_SHORT": "2",
    "KLING_GENERATE_AUDIO": "true",
    "KLING_SKIP_NARRATOR_TTS": "true",
    "KLING_MODE": "pro",
    "KLING_ASPECT_RATIO": "9:16",
    "KLING_MULTI_SHOT": "true",
    "AI_VIDEO_MAX_BEATS": "2",
    "REPLICATE_VIDEO_MODEL": "minimax/video-01",
    "REPLICATE_VIDEO_MODEL_JUMPSCARE": "minimax/hailuo-2.3-fast",
    "SLACK_POST_MODE": "email",
    "SLACK_CHANNEL_NAME": "peripheral-ops",
    "SLACK_NOTIFY_ENABLED": "true",
}

PLACEHOLDER_FRAGMENTS = (
    "your-key",
    "your-client-id",
    "your-client-secret",
    "your-gemini",
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


def _has_key(lines: list[str], key: str) -> bool:
    pattern = re.compile(rf"^{re.escape(key)}=")
    return any(pattern.match(line) for line in lines)


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


def _sync_youtube_token(*, quiet: bool) -> bool:
    raw = os.environ.get("YOUTUBE_TOKEN_JSON")
    if not raw or len(raw.strip()) < 40:
        return False
    try:
        from shorts_bot.youtube.google_auth import import_token_json

        import_token_json(raw.strip())
        if not quiet:
            print("  synced YouTube token → data/youtube_token.json")
        return True
    except (ValueError, json.JSONDecodeError) as exc:
        if not quiet:
            print(f"  YOUTUBE_TOKEN_JSON invalid: {exc}")
        return False


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
        target = "ZERNIO_API_KEY" if key == "ZERNIO_API_TOKEN" else key
        lines = _upsert(lines, target, raw.strip())
        written.append(key if target == key else f"{key}→{target}")

    for key, value in DEFAULT_ENV.items():
        if not _has_key(lines, key):
            lines = _upsert(lines, key, value)
            written.append(f"{key} (default)")

    if written:
        ENV_PATH.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        if not quiet:
            print(f"  synced to .env: {', '.join(written)}")
    elif not quiet:
        print("  no secrets in environment to sync")

    if _sync_youtube_token(quiet=quiet):
        written.append("YOUTUBE_TOKEN_JSON → data/youtube_token.json")

    return written


def main() -> None:
    sync(quiet=False)


if __name__ == "__main__":
    main()
