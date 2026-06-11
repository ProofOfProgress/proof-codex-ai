"""Export AI video clip prompts into a production pack (hybrid hook workflow)."""

from __future__ import annotations

import json
from pathlib import Path

from shorts_bot.production.ai_video_prompts import (
    VideoPromptBrief,
    build_video_prompt_briefs,
    match_template,
    negative_block,
    segment_to_video_prompt,
    visual_dna,
)
from shorts_bot.production.turboscribe_parser import TranscriptSegment


def _briefs_to_manifest_entries(
    briefs: list[VideoPromptBrief],
    *,
    hybrid_hook: bool,
) -> list[dict]:
    entries: list[dict] = []
    for i, b in enumerate(briefs):
        entry = {
            "start_seconds": b.start_seconds,
            "end_seconds": b.end_seconds,
            "filename_stem": b.filename_stem,
            "spoken_text": b.spoken_text,
            "template_id": b.template_id,
            "model_hint": b.model_hint,
            "duration_seconds": b.duration_seconds,
            "end_state": b.end_state,
            "prompt_file": f"video_prompts/{b.filename_stem}.txt",
            "negative_prompt_file": f"video_prompts/{b.filename_stem}.negative.txt",
        }
        if hybrid_hook and i == 0:
            entry["ai_video_hero"] = True
            entry["workflow"] = "FLUX still → Kling/Runway I2V 3s → hard cut to stick frames"
        entries.append(entry)
    return entries


def write_video_prompt_pack(
    pack_dir: Path,
    segments: list[TranscriptSegment],
    *,
    topic: str,
    total_duration: float | None = None,
    hybrid_hook: bool = False,
    visual_beats: list[str] | None = None,
    jumpscare_plan=None,
) -> dict:
    """Write video_prompts/*.txt + video_prompts.json + AI_VIDEO_HOOK.md into pack_dir."""
    briefs = build_video_prompt_briefs(
        segments,
        topic=topic,
        total_duration=total_duration,
        visual_beats=visual_beats,
        jumpscare_plan=jumpscare_plan,
    )
    vp_dir = pack_dir / "video_prompts"
    vp_dir.mkdir(parents=True, exist_ok=True)

    for b in briefs:
        (vp_dir / f"{b.filename_stem}.txt").write_text(b.prompt, encoding="utf-8")
        (vp_dir / f"{b.filename_stem}.negative.txt").write_text(b.negative_prompt, encoding="utf-8")

    hook_tmpl = match_template(topic=topic, spoken_text=segments[0].text if segments else "")
    payload = {
        "topic": topic,
        "hybrid_hook": hybrid_hook,
        "visual_dna": visual_dna(),
        "negative_block": negative_block(),
        "hook_template_id": hook_tmpl.id,
        "hook_model_hint": hook_tmpl.model_hint,
        "jumpscare_plan": jumpscare_plan.to_dict() if jumpscare_plan else None,
        "clips": _briefs_to_manifest_entries(briefs, hybrid_hook=hybrid_hook),
    }
    out_path = pack_dir / "video_prompts.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    hook_brief = briefs[0] if briefs else None
    if hook_brief:
        _write_hook_guide(pack_dir, hook_brief, hybrid_hook=hybrid_hook)

    return payload


def _write_hook_guide(pack_dir: Path, hook: VideoPromptBrief, *, hybrid_hook: bool) -> None:
    mode = "HYBRID (recommended)" if hybrid_hook else "optional hero clip"
    lines = [
        f"# AI video hook — {mode}",
        "",
        f"**Template:** `{hook.template_id}` · **Model:** {hook.model_hint}",
        f"**Duration:** ~{hook.duration_seconds:.0f}s · **Stem:** `{hook.filename_stem}`",
        "",
        "## Steps",
        "",
        "1. Generate horror FLUX still from `prompts/00.00.txt` (or first segment still).",
        "2. Run I2V with prompt below + negative file — dread drift or lunge on final beat.",
        "3. Chain motion clips in `clips/` per manifest segments (or hybrid still fallback).",
        "4. Burn captions once via ffmpeg ASS (`subtitles.ass`) — never text in AI prompt.",
        "",
        "## I2V prompt",
        "",
        "```",
        hook.prompt,
        "```",
        "",
        "## Negative",
        "",
        "```",
        hook.negative_prompt,
        "```",
        "",
        f"**END STATE (for chaining):** {hook.end_state}",
        "",
        "See `docs/AI_VIDEO_PROMPTING_RESEARCH.md` and `video_prompts.json`.",
    ]
    (pack_dir / "AI_VIDEO_HOOK.md").write_text("\n".join(lines), encoding="utf-8")


def export_from_manifest(pack_dir: Path, *, hybrid_hook: bool | None = None) -> dict:
    """Re-export video prompts from an existing manifest.json."""
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"No manifest at {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    topic = manifest.get("topic") or "Don't Blink Short"
    style = manifest.get("visual_style") or "ai_video"
    if hybrid_hook is None:
        hybrid_hook = style in ("hybrid", "ai_video", "ai_video_hook")

    segments = [
        TranscriptSegment(
            start_seconds=float(s["start_seconds"]),
            text=str(s.get("spoken_text") or ""),
            label=Path(str(s.get("filename", "00.00.png"))).stem.replace(".png", ""),
        )
        for s in manifest.get("segments") or []
    ]
    if not segments:
        raise ValueError("Manifest has no segments")

    last_end = max(float(s["end_seconds"]) for s in manifest["segments"])
    return write_video_prompt_pack(
        pack_dir,
        segments,
        topic=topic,
        total_duration=last_end,
        hybrid_hook=hybrid_hook,
    )


def hook_only_prompt(topic: str, spoken_text: str = "") -> str:
    """Single hook clip prompt for quick copy-paste."""
    seg = TranscriptSegment(0.0, spoken_text or topic, "00.00")
    tmpl = match_template(topic=topic, spoken_text=spoken_text)
    return segment_to_video_prompt(seg, topic=topic, template=tmpl, clip_index=0)
