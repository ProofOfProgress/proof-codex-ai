"""Generate short on-brand replies for auto-safe comments."""

from __future__ import annotations

import re

from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.config import settings
from shorts_bot.comments.triage import TOPIC_REQUEST
from shorts_bot.llm.provider import get_llm_backend


def _offline_reply(comment: str) -> str:
    lower = comment.lower()
    if TOPIC_REQUEST.search(comment):
        return (
            "Good one — I'll queue this for a future Minute Before Short. "
            "you're still here. good."
        )
    if re.search(r"\b(thank|thanks|helped|useful|needed this|appreciate)\b", lower):
        return "Glad it landed. you're still here. good."
    if re.search(r"\b(love|great|awesome|perfect|amazing)\b", lower):
        return "Means a lot — more minute-before protocols coming."
    if "?" in comment and len(comment) < 120:
        return (
            "Short answer: try the one-breath reset from the video, then name what's "
            "actually scaring you. If it's heavier than that, reach someone you trust offline too."
        )
    return (
        "Appreciate you stopping by. If you want a specific minute covered, "
        "drop it in one sentence — I read these."
    )


def generate_reply(comment: str, *, video_title: str = "") -> str:
    """Warm Soft Continuity reply — max ~280 chars."""
    backend = get_llm_backend()
    if backend is None:
        return _offline_reply(comment)[:280]

    brand = ChannelBrand()
    tagline = brand.youtube_fields().tagline or settings.channel_tagline
    prompt = f"""Write ONE YouTube comment reply as Soft Continuity channel owner.

Comment: {comment[:500]}
Video: {video_title[:120] or "a Short"}

Rules:
- Max 220 characters
- Warm, first-person, calm — not therapist, not crisis counselor
- If they suggest a topic, say you'll queue it for "The Minute Before"
- Tagline sparingly: "{tagline}"
- No links, no medical advice, no "as an AI"
- Plain text only
"""
    try:
        resp = backend.client.chat.completions.create(
            model=backend.model,
            messages=[
                {"role": "system", "content": "You reply to YouTube comments briefly and humanly."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=120,
        )
        text = (resp.choices[0].message.content or "").strip()
        text = re.sub(r"\s+", " ", text)
        return text[:280] if text else _offline_reply(comment)[:280]
    except Exception:
        return _offline_reply(comment)[:280]
