"""Research topic routing — Don't Blink horror vs AI video prompting sessions."""

from __future__ import annotations

from shorts_bot.production.niche import DEFAULT_TOPICS

AI_VIDEO_RESEARCH_TOPICS: tuple[str, ...] = (
    "AI video prompting: MiniMax I2V for 9:16 horror Shorts night-vision CCTV beats",
    "AI video prompting: Kling image-to-video dread drift and final lunge scares",
    "AI video prompting: temporal consistency END STATE to CONTINUITY IN clip chaining",
    "AI video prompting: negative prompts for horror (no cosy palette, no stick figures)",
    "AI video prompting: caption safe zone composition for 9:16 horror",
    "AI video prompting: security cam grain + mirror reflection motion templates",
    "AI video prompting: Fal and Replicate I2V API integration for Shorts pipelines",
    "AI video prompting: competitor faceless horror Shorts using AI motion clips",
    "AI video prompting: 5-part framework (subject action camera environment style) for dread",
    "AI video prompting: Don't Blink VISUAL DNA translation from stills to motion",
    "AI video prompting: jumpscare_lunge final beat prompt patterns",
    "AI video prompting: ffmpeg concat hybrid still + motion clip workflow",
    "AI video prompting: face and text-in-frame QC for automated video rejection",
    "AI video prompting: false calm beat — slow motion before sting",
    "AI video prompting: horror Shorts retention — hook in first 3 seconds",
)

HORROR_HOOK_RESEARCH_TOPICS: tuple[str, ...] = (
    "mirror horror shorts hook patterns wrong reflection blink",
    "security camera horror shorts motion alert home alone",
    "wrong text delivered horror shorts phone glitch",
    "closet knock horror shorts false calm jumpscare",
    "psychological horror shorts false calm before scare retention",
    "horror shorts volume warning title SEO jumpscare",
)


def user_excludes_cosy_topics(user_request: str) -> bool:
    """Owner asked to skip self-help / minute-before cosy research."""
    lower = (user_request or "").lower()
    return any(
        s in lower
        for s in (
            "not cosy",
            "no cosy",
            "not cozy",
            "no cozy",
            "not self-help",
            "not self help",
            "not minute before",
            "no minute before",
        )
    )


def user_wants_ai_video_research(user_request: str) -> bool:
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
        "minimax",
        "temporal consistency",
        "clip chain",
        "visual dna",
    )
    if any(s in lower for s in signals):
        return True
    return "video" in lower and ("prompt" in lower or "research" in lower)


def user_wants_horror_hook_research(user_request: str) -> bool:
    lower = (user_request or "").lower()
    return any(
        s in lower
        for s in (
            "horror hook",
            "jumpscare",
            "don't blink",
            "dont blink",
            "scare type",
            "competitor horror",
            "mirror horror",
            "security cam",
        )
    )


def research_topic_batch(
    user_request: str,
    count: int,
    *,
    offset: int = 0,
) -> list[str]:
    """Pick research topics from the right queue for this session."""
    if user_wants_ai_video_research(user_request):
        pool = AI_VIDEO_RESEARCH_TOPICS
    elif user_wants_horror_hook_research(user_request):
        pool = HORROR_HOOK_RESEARCH_TOPICS
    else:
        pool = DEFAULT_TOPICS
    n = len(pool)
    if n == 0:
        return ["horror shorts impossible hook research"]
    return [pool[(offset + i) % n] for i in range(count)]


def ai_video_context_block() -> str:
    try:
        from shorts_bot.production.ai_video_prompts import visual_dna

        dna = visual_dna()
    except Exception:
        dna = (
            "VISUAL DNA: cinematic horror, cold blue/black, night vision green optional, "
            "9:16, faceless until final lunge, caption-safe lower third empty."
        )

    return f"""RESEARCH MODE: AI VIDEO PROMPTING for Don't Blink horror Shorts.

Channel: Don't Blink — faceless ~30s horror micro-stories, jumpscare in last 3 seconds.

Focus research on:
- I2V dread drift + final lunge (MiniMax, Kling, Replicate)
- END STATE → CONTINUITY IN chaining between beats
- Security cam / mirror / knock / wrong text visual templates
- Caption-safe 9:16 (no text in AI frames)
- Competitor horror Shorts hooks and retention

Do NOT research cosy self-help or stick-figure mental-health Shorts.

{dna}

See data/research/HORROR_PSYCHOLOGY_DEEP_RESEARCH.md and docs/AI_VIDEO_PROMPTING_RESEARCH.md.
"""
