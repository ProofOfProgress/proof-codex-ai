from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.image_prompts import build_image_briefs, build_master_prompt
from shorts_bot.production.render_ai_images import render_all_ai_images
from shorts_bot.drafts.meta import visual_beats_for_draft
from shorts_bot.production.segment_sync import normalize_transcript_segments, resolve_segments
from shorts_bot.production.variety import variety_for_draft
from shorts_bot.production.video_prompt_pack import write_video_prompt_pack


@dataclass
class ProductionPack:
    draft_id: int
    topic: str
    output_dir: Path
    image_count: int
    images_rendered: int
    manifest_path: Path
    message: str


def _capcut_instructions(briefs: list, topic: str) -> str:
    lines = [
        f"# CapCut timeline — {topic}",
        "",
        "1. Import voiceover audio track.",
        "2. Import all images from `images/` (or generate from `prompts/` first).",
        "3. Place each image at its **start** second; drag end to the **next** image start.",
        "",
        "| Start | End | File | Spoken |",
        "|-------|-----|------|--------|",
    ]
    for b in briefs:
        lines.append(
            f"| {b.start_seconds:.0f}s | {b.end_seconds:.0f}s | `{b.filename_stem}.png` | {b.spoken_text[:60]}… |"
            if len(b.spoken_text) > 60
            else f"| {b.start_seconds:.0f}s | {b.end_seconds:.0f}s | `{b.filename_stem}.png` | {b.spoken_text} |"
        )
    lines.extend(
        [
            "",
            "4. **SFX:** follow `CAPCUT_SFX.md` — separate audio lane, VO loudest.",
            "5. Add captions (optional — TurboScribe SRT also works).",
            "6. Music: YouTube Audio Library, duck under voice (-12dB or keyframes).",
            "7. Export 1080×1920 H.264 → YouTube Short.",
            "",
            "CapCut horror workflow: `channel/brand/capcut_horror_sfx.md`",
        ]
    )
    return "\n".join(lines)


def build_production_pack(
    store: MemoryStore,
    *,
    draft_id: int,
    turboscribe_text: str = "",
    output_root: Path | None = None,
    auto_from_script: bool = False,
    render_images: bool = False,
) -> ProductionPack:
    draft = store.get_draft(draft_id)
    root = output_root or (settings.data_dir / "production" / f"draft_{draft_id}")
    audio_duration: float | None = None
    audio_path = root / "voiceover.mp3"
    if audio_path.exists():
        from shorts_bot.production.render_video import _probe_duration

        try:
            audio_duration = _probe_duration(audio_path)
        except Exception:
            audio_duration = None

    variety = variety_for_draft(draft_id)
    if audio_duration and variety.segment_merge_bias != 1.0:
        audio_duration = audio_duration  # used below via resolve_segments

    segments, sync_source = resolve_segments(
        script=draft.script,
        pack_dir=root,
        turboscribe_text=turboscribe_text if turboscribe_text.strip() else "",
        audio_duration=audio_duration,
    )
    if audio_duration and audio_duration > 0:
        segments = normalize_transcript_segments(segments, audio_duration)
    from shorts_bot.production.paid_stack import ensure_turboscribe_segments

    ensure_turboscribe_segments(sync_source)
    if not segments and auto_from_script:
        from shorts_bot.production.script_segments import segments_from_script

        segments = segments_from_script(draft.script)
        sync_source = "script_estimate"
    if not segments:
        raise ValueError(
            "No timestamps found. Use auto_from_script=True or paste TurboScribe export "
            "with lines like '0:07 your words...'"
        )

    beats = visual_beats_for_draft(draft_id)
    briefs = build_image_briefs(
        segments,
        topic=draft.topic,
        total_duration=audio_duration,
        visual_beats=beats or None,
    )
    root.mkdir(parents=True, exist_ok=True)
    prompts_dir = root / "prompts"
    images_dir = root / "images"
    clips_dir = root / "clips"
    prompts_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    clips_dir.mkdir(exist_ok=True)

    for b in briefs:
        (prompts_dir / f"{b.filename_stem}.txt").write_text(b.prompt, encoding="utf-8")

    from shorts_bot.production.jumpscare_timing import persist_plan, plan_for_draft

    scare_plan = plan_for_draft(draft_id, len(segments))
    persist_plan(draft_id, scare_plan)

    hybrid_hook = settings.visual_style in ("hybrid", "ai_video", "ai_video_hook")
    video_payload = write_video_prompt_pack(
        root,
        segments,
        topic=draft.topic,
        total_duration=audio_duration,
        hybrid_hook=hybrid_hook,
        visual_beats=beats or None,
        jumpscare_plan=scare_plan,
    )

    (root / "VOICEOVER_SCRIPT.txt").write_text(
        f"HOOK: {draft.hook}\n\n{draft.script}\n\n---\nRecord this, then optional TurboScribe re-sync.\n",
        encoding="utf-8",
    )

    image_note = ""
    render_mode = "slideshow"
    clips_rendered = 0
    rendered = 0
    if render_images:
        if settings.uses_kling_video and settings.has_kling_official:
            from shorts_bot.production.render_kling import render_kling_clips

            clips_rendered = render_kling_clips(
                topic=draft.topic,
                hook=draft.hook,
                script=draft.script,
                clips_dir=clips_dir,
                draft_id=draft_id,
                force_regen=settings.kling_force_regen,
            )
            if clips_rendered > 0:
                rendered = clips_rendered
                render_mode = "kling_clips"
                from shorts_bot.production.launch_phase import is_silent_launch_draft

                audio_note = (
                    "silent video + post SFX"
                    if is_silent_launch_draft(draft_id)
                    else "native audio"
                )
                image_note = (
                    f" via Kling ({settings.kling_model}, "
                    f"{clips_rendered}×{settings.kling_clip_seconds}s, {settings.kling_mode}, {audio_note})"
                )
            else:
                raise RuntimeError(
                    f"Kling returned 0 clips — expected {settings.kling_clips_per_short}."
                )
        elif settings.uses_kling_video:
            raise RuntimeError(
                "Kling video requires KLING_ACCESS_KEY + KLING_SECRET_KEY in Cursor secrets."
            )
        elif settings.visual_style == "ai_video" and settings.has_paid_images:
            from shorts_bot.production.render_ai_video import render_all_ai_video_clips

            priority = [scare_plan.primary_segment_index]
            if scare_plan.decoy_segment_index is not None:
                priority.append(scare_plan.decoy_segment_index)
            clips_rendered = render_all_ai_video_clips(
                briefs,
                segments,
                topic=draft.topic,
                images_dir=images_dir,
                clips_dir=clips_dir,
                priority_indices=priority,
            )
            if clips_rendered > 0:
                rendered = clips_rendered
                render_mode = "video_clips"
                image_note = f" via Replicate I2V ({settings.replicate_video_model})"
                if clips_rendered < len(briefs):
                    image_note += f" ({clips_rendered}/{len(briefs)} clips)"
            else:
                raise RuntimeError(
                    f"I2V returned 0 clips for {len(briefs)} beats — no stick-figure fallback on Don't Blink."
                )
        elif settings.has_paid_images:
            rendered = render_all_ai_images(briefs, images_dir)
            render_mode = "slideshow"
            image_note = f" via {settings.image_provider} stills (set VISUAL_STYLE=ai_video for motion)"
        else:
            raise RuntimeError(
                "Don't Blink requires paid image stack (REPLICATE_API_TOKEN). No stick-figure fallback."
            )
    else:
        rendered = 0

    manifest = {
        "draft_id": draft_id,
        "topic": draft.topic,
        "hook": draft.hook,
        "script": draft.script,
        "workflow": sync_source,
        "variety": variety.summary(),
        "visual_beats": beats,
        "jumpscare_plan": scare_plan.to_dict(),
        "visual_style": settings.visual_style,
        "video_backend": settings.video_backend,
        "render_mode": render_mode,
        "hybrid_ai_hook": hybrid_hook,
        "video_prompts": f"video_prompts.json ({len(video_payload.get('clips', []))} clips)",
        "image_count": len(briefs),
        "images_rendered": rendered,
        "clips_rendered": clips_rendered,
        "segments": [
            {
                "start_seconds": b.start_seconds,
                "end_seconds": b.end_seconds,
                "filename": f"{b.filename_stem}.png",
                "clip_filename": f"{b.filename_stem}.mp4",
                "spoken_text": b.spoken_text,
                "prompt_file": f"prompts/{b.filename_stem}.txt",
            }
            for b in briefs
        ],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    (root / "MASTER_IMAGE_PROMPT.md").write_text(
        build_master_prompt() + "\n\n---\n\n## Timestamped script\n\n"
        + "\n".join(f"{s.label} {s.text}" for s in segments),
        encoding="utf-8",
    )
    (root / "CAPCUT_TIMELINE.md").write_text(_capcut_instructions(briefs, draft.topic), encoding="utf-8")

    from shorts_bot.production.capcut_sfx import build_capcut_sfx_markdown

    (root / "CAPCUT_SFX.md").write_text(
        build_capcut_sfx_markdown(
            [
                {
                    "start_seconds": b.start_seconds,
                    "spoken_text": b.spoken_text,
                }
                for b in briefs
            ],
            topic=draft.topic,
            jumpscare_plan=scare_plan.to_dict(),
            audio_duration=audio_duration,
        ),
        encoding="utf-8",
    )
    (root / "README.txt").write_text(
        "Don't Blink horror production pack\n\n"
        "1. Record voiceover from script in manifest.json\n"
        "2. Transcript sync via Gemini audio timestamps\n"
        "3. AI motion clips: clips/ (VISUAL_STYLE=ai_video)\n"
        "4. video_prompts/ for I2V motion prompts per beat\n"
        "5. CAPCUT_SFX.md — per-beat sound effects for CapCut\n"
        "6. Save PNGs to images/ named like 00.07.png\n"
        "7. Follow CAPCUT_TIMELINE.md + channel/brand/capcut_horror_sfx.md\n"
        "8. captions.srt — upload to YouTube for extra subtitle track\n"
        "9. Captions: ffmpeg ASS burn-in at render (Jenny 05 safe zone) + captions.srt\n",
        encoding="utf-8",
    )

    msg = (
        f"Production pack ready: {len(briefs)} segments for '{draft.topic}'. "
        f"Folder: {root}."
    )
    if rendered:
        if render_mode == "video_clips":
            msg += f" Rendered {rendered} motion clips in clips/{image_note}."
        else:
            msg += f" Rendered {rendered} still PNGs in images/{image_note}."
    else:
        msg += " Open prompts/ or run with render_images=True."

    return ProductionPack(
        draft_id=draft_id,
        topic=draft.topic,
        output_dir=root,
        image_count=len(briefs),
        images_rendered=rendered,
        manifest_path=manifest_path,
        message=msg,
    )


def auto_produce_draft(
    store: MemoryStore,
    draft_id: int,
    *,
    render_images: bool = True,
) -> ProductionPack:
    """
    Legacy pack-only path (script timing). Production videos should use finish_draft_pipeline
    (Resemble + TurboScribe Whale).
    """
    if settings.require_paid_stack and not settings.allow_script_timing_fallback:
        raise ValueError(
            "auto_produce_draft bypasses the paid stack (Resemble + TurboScribe). "
            "Use: python3 -m shorts_bot.production.finish_cli --draft-id "
            f"{draft_id}"
        )
    return build_production_pack(
        store,
        draft_id=draft_id,
        auto_from_script=True,
        render_images=render_images,
    )
