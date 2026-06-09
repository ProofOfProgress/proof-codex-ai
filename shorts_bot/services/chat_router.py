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


def parse_auto_video_request(message: str) -> int | None:
    lower = message.strip().lower()
    for prefix in ("make video ", "makevideo ", "auto produce ", "autoproduce ", "build video "):
        if lower.startswith(prefix):
            tail = message.strip()[len(prefix) :].strip()
            if tail.split()[0].isdigit():
                return int(tail.split()[0])
    if lower in {"make video", "auto produce"}:
        return -1
    return None


def parse_produce_request(message: str) -> tuple[int, str] | None:
    """produce 5 | <turboscribe paste> or produce draft 5 then transcript on next lines."""
    text = message.strip()
    lower = text.lower()
    if not lower.startswith("produce "):
        return None
    body = text[8:].strip()
    if "|" in body:
        head, transcript = body.split("|", 1)
        draft_id = int(head.strip().split()[-1])
        return draft_id, transcript.strip()
    parts = body.split(maxsplit=1)
    if parts and parts[0].isdigit():
        return int(parts[0]), parts[1].strip() if len(parts) > 1 else ""
    return None


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
