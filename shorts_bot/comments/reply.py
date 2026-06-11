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
        return "Good one — I'll queue this for a future Don't Blink Short."
    if re.search(r"\b(thank|thanks|helped|useful|needed this|appreciate)\b", lower):
        return "Glad it landed — watch the whole thing on the next one too."
    if re.search(r"\b(love|great|awesome|perfect|amazing)\b", lower):
        return "Means a lot — more impossible-detail horror coming."
    if "?" in comment and len(comment) < 120:
        return (
            "Short answer: rewatch the hook frame — the wrong detail is the clue. "
            "If it's heavier than fiction, reach someone you trust offline too."
        )
    return (
        "Appreciate you stopping by. One sentence for the next story — I read these."
    )


def generate_reply(comment: str, *, video_title: str = "") -> str:
    """Don't Blink channel owner reply — max ~280 chars."""
    backend = get_llm_backend()
    if backend is None:
        return _offline_reply(comment)[:280]

    brand = ChannelBrand()
    channel = settings.youtube_channel_name or "Don't Blink"
    tagline = brand.youtube_fields().tagline or settings.channel_tagline
    prompt = f"""Write ONE YouTube comment reply as {channel} channel owner.

Comment: {comment[:500]}
Video: {video_title[:120] or "a Short"}

Rules:
- Max 220 characters
- Tense but human horror-creator voice — not therapist, not crisis counselor
- If they suggest a topic, say you'll queue it for the next Don't Blink micro-story
- Do NOT paste the channel tagline ("{tagline}") — it sounds robotic in comments
- NEVER spoil the video: no jumpscare, scare at the end, volume warning, headphones, or loud ending
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
