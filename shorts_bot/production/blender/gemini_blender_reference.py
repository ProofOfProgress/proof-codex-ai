"""LIGHTS ARE OFF reference URLs + quality bar — inject into every Gemini visual prompt."""

from __future__ import annotations

REFERENCE_PATH = "data/research/LIGHTS_ARE_OFF_BLENDER_REFERENCE.md"

# Owner-approved north-star links (always pass to Gemini text prompts).
LIGHTS_ARE_OFF_URLS: tuple[str, ...] = (
    "https://youtube.com/shorts/R7cEIG_gqLU",
    "https://youtu.be/S0x2llxEAjk",
    "https://youtu.be/lnDP902qeqw",
    "https://www.youtube.com/@LIGHTSAREOFF",
)


def reference_links_block() -> str:
    return (
        "QUALITY BAR — LIGHTS ARE OFF (Blender horror, not AI slop):\n"
        f"- Viral Short (swim/dread): {LIGHTS_ARE_OFF_URLS[0]}\n"
        f"- Pt1 Self-Aware Robot (lab craft): {LIGHTS_ARE_OFF_URLS[1]}\n"
        f"- Pt3 Prisoner (escalation + sets): {LIGHTS_ARE_OFF_URLS[2]}\n"
        f"- Channel: {LIGHTS_ARE_OFF_URLS[3]}\n"
        "Peripheral target: same FINISHED Blender look — readable environment, "
        "working textures, horror lighting, intentional camera. "
        "FAIL anything that looks like grey block-out or broken FBX import."
    )


def gemini_blender_quality_prompt(*, scene: str = "Peripheral rural gas station Form 2 horror Short") -> str:
    return (
        f"{reference_links_block()}\n\n"
        f"Scene context: {scene}\n"
        "Codex file: data/research/LIGHTS_ARE_OFF_BLENDER_REFERENCE.md"
    )


def load_reference_markdown() -> str:
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]
    path = root / REFERENCE_PATH
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return reference_links_block()


def ask_gemini_blender_brief(*, scene: str, extra: str = "") -> str:
    """One-shot: send reference links + scene ask to Gemini; return markdown brief."""
    from shorts_bot.llm.provider import get_llm_backend

    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        raise RuntimeError("GEMINI_API_KEY required for blender visual brief")

    prompt = (
        "You are the Blender visual director for Peripheral horror YouTube Shorts.\n\n"
        f"{gemini_blender_quality_prompt(scene=scene)}\n\n"
        f"{load_reference_markdown()[:6000]}\n\n"
        "The owner wants videos like LIGHTS ARE OFF — all Blender, finished sets, horror lighting.\n"
        "You cannot watch YouTube; use your knowledge of that channel's style plus the notes above.\n\n"
        f"{extra}\n\n"
        "Return markdown with:\n"
        "1. What makes those references work (5 bullets)\n"
        "2. Concrete fixes for our gas-station draft (lighting, textures, camera, scale)\n"
        "3. EEVEE settings checklist (exposure, bloom, probes)\n"
        "4. Pass/fail criteria for vision QC before upload\n"
    )
    resp = backend.client.chat.completions.create(
        model=backend.model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1200,
        temperature=0.4,
    )
    return (resp.choices[0].message.content or "").strip()
