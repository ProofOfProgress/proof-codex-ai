"""Research topic routing — cosy Shorts vs AI video prompting sessions."""

from __future__ import annotations

from shorts_bot.production.niche import DEFAULT_TOPICS

# Focused queue for "research AI video prompting only" manager sessions.
AI_VIDEO_RESEARCH_TOPICS: tuple[str, ...] = (
    "AI video prompting: Kling 3 image-to-video for 9:16 faceless mental-health Shorts",
    "AI video prompting: Runway Gen-4 cinematic B-roll and camera control patterns",
    "AI video prompting: Veo 3.1 vs Kling for cosy illustration style (not photoreal)",
    "AI video prompting: temporal consistency END STATE to CONTINUITY IN clip chaining",
    "AI video prompting: Pika and Luma for stylized 3-5s B-roll clips",
    "AI video prompting: negative prompts and quality pitfalls (morphing, shake, faces)",
    "AI video prompting: caption safe zone composition for 9:16 (bottom 40% empty)",
    "AI video prompting: hybrid stick-figure + single AI hero hook clip ROI",
    "AI video prompting: Fal and Replicate Kling I2V API integration for Shorts pipelines",
    "AI video prompting: competitor faceless mental-health Shorts using AI video tools",
    "AI video prompting: 5-part framework (subject action camera environment style) best practices",
    "AI video prompting: Soft Continuity VISUAL DNA translation from stills to motion",
    "AI video prompting: Minimax Hailuo narrative prompts vs keyword lists",
    "AI video prompting: ffmpeg xfade cross-dissolve between AI clips workflow",
    "AI video prompting: face and text-in-frame QC for automated video rejection",
)


def user_wants_ai_video_research(user_request: str) -> bool:
    """True when the human asked for AI video / I2V research (not cosy topic scoring)."""
    lower = (user_request or "").lower()
    signals = (
        "ai video",
        "video prompt",
        "video prompting",
        "i2v",
        "image-to-video",
        "image to video",
        "kling",
        "runway gen",
        "runway",
        "veo",
        "pika",
        "luma",
        "hailuo",
        "temporal consistency",
        "clip chain",
        "visual dna",
    )
    if any(s in lower for s in signals):
        return True
    return "video" in lower and ("prompt" in lower or "research" in lower)


def user_excludes_cosy_topics(user_request: str) -> bool:
    lower = (user_request or "").lower()
    return any(
        p in lower
        for p in (
            "not cosy",
            "not cozy",
            "no cosy",
            "no cozy",
            "only ai video",
            "only video",
            "not topics",
        )
    )


def research_topic_batch(
    user_request: str,
    count: int,
    *,
    offset: int = 0,
) -> list[str]:
    """Pick research topics from the right queue for this session."""
    if user_wants_ai_video_research(user_request) or (
        user_excludes_cosy_topics(user_request) and "research" in (user_request or "").lower()
    ):
        pool = AI_VIDEO_RESEARCH_TOPICS
    else:
        pool = DEFAULT_TOPICS
    n = len(pool)
    if n == 0:
        return ["AI video prompting: high-quality 9:16 Shorts"]
    return [pool[(offset + i) % n] for i in range(count)]


def ai_video_context_block() -> str:
    """Context for Gemini specialists during AI video research sessions."""
    try:
        from shorts_bot.production.ai_video_prompts import visual_dna

        dna = visual_dna()
    except Exception:
        dna = "VISUAL DNA: cosy minimal illustration, 9:16, faceless, bottom 40% caption-safe."

    return f"""RESEARCH MODE: AI VIDEO PROMPTING (not cosy Short topics).

Channel: Soft Continuity — faceless mental-health Shorts, stick-figure default, AI video for hero clips only.

Focus research on:
- Model-specific prompt patterns (Kling, Runway, Veo, Pika, Luma, Hailuo)
- Image-to-video continuity chaining (END STATE → CONTINUITY IN)
- Caption-safe 9:16 composition (no text in AI frames)
- Hybrid pipeline: stick figures + 1-3s AI hook
- Tool APIs (Fal/Replicate Kling I2V), ffmpeg xfade, QC

Do NOT score cosy domestic topics. Do NOT draft mental-health scripts unless explicitly asked.

{dna}

See docs/AI_VIDEO_PROMPTING_RESEARCH.md for baseline framework.
"""
