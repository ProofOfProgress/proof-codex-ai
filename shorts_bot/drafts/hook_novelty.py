"""Block recycled hooks — every Short needs a fresh opening line."""

from __future__ import annotations

import re
from dataclasses import dataclass

from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore

# Live channel Shorts — never paraphrase these openings again.
CHANNEL_KNOWN_HOOKS: tuple[str, ...] = (
    "you blinked — your reflection blinked one second later",
    "you blinked at the mirror — your reflection blinked one second later",
)

_REFLECTION_CUES = frozenset(
    {"blink", "blinked", "mirror", "reflection", "glass", "reflections"}
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def _tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9']+", _normalize(text)) if len(w) > 2}


def hook_similarity(a: str, b: str) -> float:
    """0 = unrelated, 1 = same hook."""
    na, nb = _normalize(a), _normalize(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    ta, tb = _tokens(na), _tokens(nb)
    jaccard = len(ta & tb) / len(ta | tb) if ta and tb else 0.0
    # Reflection/mirror family — treat shared scare frame as duplicate.
    if ta & _REFLECTION_CUES and tb & _REFLECTION_CUES:
        shared = ta & tb
        if len(shared) >= 2 or ("blink" in shared and "reflection" in (ta | tb)):
            return max(jaccard, 0.85)
    if na in nb or nb in na:
        return max(jaccard, 0.8)
    return jaccard


@dataclass
class HookNoveltyReport:
    novel: bool
    reason: str = ""


def collect_recent_hooks(
    store: MemoryStore,
    memory: MemoryExtensions | None = None,
    *,
    draft_limit: int = 20,
    upload_limit: int = 10,
) -> list[str]:
    hooks: list[str] = []
    seen: set[str] = set()
    for raw in CHANNEL_KNOWN_HOOKS:
        key = _normalize(raw)
        if key not in seen:
            seen.add(key)
            hooks.append(raw)
    if memory:
        for row in memory.recent_upload_scripts(limit=upload_limit):
            h = str(row.get("hook") or "").strip()
            key = _normalize(h)
            if h and key not in seen:
                seen.add(key)
                hooks.append(h)
    for d in store.list_drafts(limit=draft_limit):
        key = _normalize(d.hook)
        if d.hook.strip() and key not in seen:
            seen.add(key)
            hooks.append(d.hook.strip())
    return hooks


def check_hook_novelty(
    hook: str,
    recent_hooks: list[str],
    *,
    max_similarity: float = 0.55,
) -> HookNoveltyReport:
    h = hook.strip()
    if len(h) < 12:
        return HookNoveltyReport(False, "hook too short")
    for prev in recent_hooks:
        sim = hook_similarity(h, prev)
        if sim >= max_similarity:
            return HookNoveltyReport(
                False,
                f"hook {sim:.0%} similar to recent: {prev[:72]}…",
            )
    return HookNoveltyReport(True)


def format_banned_hooks_block(recent_hooks: list[str], *, max_items: int = 12) -> str:
    if not recent_hooks:
        return ""
    lines = [f"- {h}" for h in recent_hooks[:max_items]]
    return (
        "BANNED HOOKS — do NOT repeat or paraphrase these openings (new idea EVERY time):\n"
        + "\n".join(lines)
    )
