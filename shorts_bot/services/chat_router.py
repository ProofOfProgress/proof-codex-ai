from __future__ import annotations

import json
import re


def parse_dev_request(message: str) -> tuple[str, str] | None:
    text = message.strip()
    for prefix in ("dev:", "build:", "code:", "develop:"):
        if text.lower().startswith(prefix):
            body = text[len(prefix) :].strip()
            if "|" in body:
                title, desc = body.split("|", 1)
                return title.strip()[:120], desc.strip()
            if len(body) > 80:
                return body[:80], body
            return body, body
    if re.match(r"^(please\s+)?(build|code|add|implement)\s+", text, re.I):
        return text[:80], text
    return None


def is_sync_command(message: str) -> bool:
    t = message.strip().lower()
    return t in {"sync", "sync youtube", "sync analytics", "youtube sync"} or t.startswith("sync ")


def is_pending_command(message: str) -> bool:
    t = message.strip().lower()
    return t in {"pending", "approvals", "what needs approval", "improvements"}


def is_help_command(message: str) -> bool:
    return message.strip().lower() in {"help", "/help", "commands", "?"}


def is_apply_brand_command(message: str) -> bool:
    t = message.strip().lower()
    return t in {
        "apply brand",
        "apply branding",
        "channel brand",
        "update channel",
        "update channel name",
        "update description",
        "apply channel brand",
    } or t.startswith("apply brand ")
