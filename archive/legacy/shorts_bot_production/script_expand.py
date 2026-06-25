"""Expand a winning Short script into a long-form narrative outline."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LongScriptOutline:
    draft_id: int
    topic: str
    hook: str
    target_words: int
    sections: list[dict[str, str]]
    word_count_estimate: int
    message: str


def _estimate_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _split_sentences(script: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", script.strip())
    return [p.strip() for p in parts if p.strip()]


def expand_short_to_long_outline(
    *,
    draft_id: int,
    topic: str,
    hook: str,
    script: str,
    target_words: int = 1000,
) -> LongScriptOutline:
    """Template scaffold — Gemini prose pass can replace section bodies later."""
    sentences = _split_sentences(script)
    opener = hook.strip() or (sentences[0] if sentences else topic)
    mid = sentences[1:-1] if len(sentences) > 2 else sentences[1:]
    closer = sentences[-1] if sentences else opener

    sections = [
        {
            "id": "hook",
            "label": "Cold open (0:00–0:45)",
            "beats": (
                f"{opener} Expand the impossible detail — what did you notice first, "
                "and why did you tell yourself it was nothing?"
            ),
        },
        {
            "id": "escalation_1",
            "label": "First wrongness (0:45–2:30)",
            "beats": (
                f"Deepen the setting from the Short: {topic}. "
                f"Reuse lines: {' '.join(mid[:2]) if mid else opener}"
            ),
        },
        {
            "id": "escalation_2",
            "label": "Pattern breaks (2:30–4:30)",
            "beats": (
                "Second-person you investigates — timestamps, recordings, "
                "something that should not repeat but does."
            ),
        },
        {
            "id": "false_calm",
            "label": "False calm (4:30–6:00)",
            "beats": (
                "Brief relief that is obviously a lie. Reader thinks they figured it out."
            ),
        },
        {
            "id": "finale",
            "label": "Finale scare (6:00–end)",
            "beats": (
                f"Pay off the Short ending harder: {closer} "
                "One new detail that recontextualizes everything."
            ),
        },
    ]

    body = "\n\n".join(f"## {s['label']}\n{s['beats']}" for s in sections)
    word_est = _estimate_words(body)

    return LongScriptOutline(
        draft_id=draft_id,
        topic=topic,
        hook=hook,
        target_words=target_words,
        sections=sections,
        word_count_estimate=word_est,
        message=(
            f"Outline scaffold for draft #{draft_id} — expand to ~{target_words} words "
            f"(current template ~{word_est} words). Run VO + long_still pack next."
        ),
    )


def write_long_outline(pack_dir: Path, outline: LongScriptOutline) -> Path:
    pack_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "draft_id": outline.draft_id,
        "topic": outline.topic,
        "hook": outline.hook,
        "target_words": outline.target_words,
        "word_count_estimate": outline.word_count_estimate,
        "sections": outline.sections,
        "format": "long_still",
    }
    json_path = pack_dir / "long_script_outline.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        f"# Long script outline — draft {outline.draft_id}",
        "",
        f"**Topic:** {outline.topic}",
        f"**Target:** ~{outline.target_words} words (template ~{outline.word_count_estimate})",
        "",
    ]
    for sec in outline.sections:
        md_lines.extend(
            [
                f"## {sec['label']}",
                sec["beats"],
                "",
            ]
        )
    (pack_dir / "LONG_SCRIPT_OUTLINE.md").write_text("\n".join(md_lines), encoding="utf-8")
    return json_path
