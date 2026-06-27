"""Operating tips registry — owner rules beyond raw code (JSON + agent memory)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from shorts_bot.config import settings

ContentType = Literal["video", "carousel", "affiliate", "agent"]
Enforcement = Literal["code", "agent", "both"]

DEFAULT_TIPS_PATH = Path("data/operating_tips.json")


@dataclass(frozen=True)
class OperatingTip:
    id: str
    title: str
    content: str
    applies_to: tuple[str, ...]
    enforcement: Enforcement
    code_check: str | None = None


def tips_path() -> Path:
    return settings.data_dir / "operating_tips.json"


def load_tips(path: Path | None = None) -> list[OperatingTip]:
    p = path or tips_path()
    if not p.is_file():
        p = DEFAULT_TIPS_PATH
    if not p.is_file():
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    items = raw.get("tips") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return []
    out: list[OperatingTip] = []
    for row in items:
        if not isinstance(row, dict):
            continue
        tid = str(row.get("id") or "").strip()
        if not tid:
            continue
        applies = row.get("applies_to") or []
        if not isinstance(applies, list):
            applies = [str(applies)]
        enforcement = str(row.get("enforcement") or "agent").lower()
        if enforcement not in ("code", "agent", "both"):
            enforcement = "agent"
        out.append(
            OperatingTip(
                id=tid,
                title=str(row.get("title") or tid),
                content=str(row.get("content") or "").strip(),
                applies_to=tuple(str(a) for a in applies),
                enforcement=enforcement,
                code_check=(str(row.get("code_check") or "").strip() or None),
            )
        )
    return out


def tips_for(
    content_type: ContentType,
    *,
    path: Path | None = None,
) -> list[OperatingTip]:
    tips = load_tips(path)
    return [
        t
        for t in tips
        if content_type in t.applies_to or "agent" in t.applies_to and content_type != "agent"
    ]


def code_tips_for(content_type: ContentType, *, path: Path | None = None) -> list[OperatingTip]:
    return [
        t
        for t in tips_for(content_type, path=path)
        if t.enforcement in ("code", "both") and t.code_check
    ]


def agent_tips_for(content_type: ContentType, *, path: Path | None = None) -> list[OperatingTip]:
    return [
        t
        for t in tips_for(content_type, path=path)
        if t.enforcement in ("agent", "both")
    ]


def format_agent_checklist(
    content_type: ContentType,
    *,
    max_items: int = 50,
    path: Path | None = None,
) -> str:
    """Compact checklist for skills / agent bootstrap — no LLM cost."""
    tips = agent_tips_for(content_type, path=path)
    if not tips:
        return ""
    lines = [f"Operating tips ({content_type}):"]
    for t in tips[:max_items]:
        lines.append(f"- [{t.id}] {t.title}: {t.content}")
    return "\n".join(lines)


def format_all_agent_tips(*, max_items: int = 100, path: Path | None = None) -> str:
    tips = load_tips(path)
    agent_rows = [t for t in tips if t.enforcement in ("agent", "both")]
    lines = ["Owner operating tips (follow unless owner overrides):"]
    for t in agent_rows[:max_items]:
        lines.append(f"- [{t.id}] {t.title}: {t.content}")
    return "\n".join(lines)
