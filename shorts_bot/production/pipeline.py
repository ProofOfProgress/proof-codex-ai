"""Full automated Short pipeline — voice clone → TurboScribe → render → optional upload."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pack import build_production_pack
from shorts_bot.production.pipeline_state import load_state, save_state
from shorts_bot.production.render_video import render_short_video
from shorts_bot.production.script_humanize import finalize_script
from shorts_bot.production.upload_meta import build_upload_package, write_upload_files
from shorts_bot.production.variety import variety_for_draft
from shorts_bot.production.video_qc import run_video_qc
from shorts_bot.production.voiceover import generate_voiceover


@dataclass
class PipelineResult:
    draft_id: int
    pack_dir: Path
    messages: list[str]
    video_path: Path | None
    upload_url: str | None
    report_path: Path | None = None
    step_timings: dict[str, float] = field(default_factory=dict)


def _write_voice_script(pack_dir: Path, hook: str, script: str) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "VOICEOVER_SCRIPT.txt").write_text(
        f"HOOK: {hook}\n\n{script}\n",
        encoding="utf-8",
    )


def _write_pipeline_report(pack_dir: Path, draft_id: int, messages: list[str], timings: dict) -> Path:
    report = {
        "draft_id": draft_id,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "messages": messages,
        "step_timings_sec": timings,
        "variety": variety_for_draft(draft_id).summary(),
    }
    path = pack_dir / "pipeline_report.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def finish_draft_pipeline(
    store: MemoryStore,
    draft_id: int,
    *,
    upload_youtube: bool | None = None,
    resume: bool = True,
) -> PipelineResult:
    """
    End-to-end production with checkpoints:

    1. Pre-flight quality gate
    2. Humanize script
    3. Resemble voice clone → voiceover.mp3
    4. TurboScribe Whale → tight timestamps
    5. Rebuild stick-figure pack synced to audio
    6. ffmpeg → final_short.mp4 + video QC
    7. Upload metadata (+ optional YouTube API upload)
    """
    import time

    from shorts_bot.production.paid_stack import ensure_paid_stack_ready

    ensure_paid_stack_ready()

    draft = store.get_draft(draft_id)
    pack_dir = settings.data_dir / "production" / f"draft_{draft_id}"
    pack_dir.mkdir(parents=True, exist_ok=True)
    state = load_state(pack_dir, draft_id)
    messages: list[str] = []
    timings: dict[str, float] = {}

    def _step(name: str):
        return time.perf_counter()

    def _end(name: str, t0: float) -> None:
        timings[name] = round(time.perf_counter() - t0, 2)

    # --- Pre-flight quality (before TTS credits) ---
    t0 = _step("preflight")
    from shorts_bot.drafts.quality import run_quality_checks

    pre_qc = run_quality_checks(
        topic=draft.topic,
        script=draft.script,
        hook=draft.hook,
        help_angle=draft.help_angle,
    )
    if settings.quality_gate_blocks_render and not pre_qc.passed:
        msg = f"Pipeline blocked — pre-flight quality: {pre_qc.summary()}"
        messages.append(msg)
        state.mark("preflight", status="blocked")
        save_state(pack_dir, state)
        report = _write_pipeline_report(pack_dir, draft_id, messages, timings)
        return PipelineResult(draft_id, pack_dir, messages, None, None, report, timings)
    if pre_qc.warnings:
        messages.append(f"Pre-flight warnings: {'; '.join(pre_qc.warnings[:3])}")
    state.mark("preflight")
    save_state(pack_dir, state)
    _end("preflight", t0)

    # --- Humanize ---
    t0 = _step("humanize")
    if resume and state.is_done("humanize") and (pack_dir / "ai_detect_log.txt").exists():
        messages.append("Resume: skipped humanize (checkpoint)")
    else:
        finalized = finalize_script(draft.topic, draft.hook, draft.script, draft.help_angle)
        store.update_draft_content(
            draft_id,
            hook=finalized.hook,
            script=finalized.script,
            help_angle=finalized.help_angle,
            quality_notes=f"AI score {finalized.final_ai_score}/100 after {finalized.passes} passes",
        )
        messages.append(finalized.message)
        log_path = pack_dir / "ai_detect_log.txt"
        log_path.write_text(
            finalized.message + "\nscores: " + str(finalized.scores_log) + "\n",
            encoding="utf-8",
        )
        state.mark("humanize")
        save_state(pack_dir, state)
    draft = store.get_draft(draft_id)
    _write_voice_script(pack_dir, draft.hook, draft.script)
    _end("humanize", t0)

    # --- Voiceover ---
    t0 = _step("voiceover")
    vo_path = pack_dir / "voiceover.mp3"
    if resume and state.is_done("voiceover") and vo_path.exists():
        messages.append("Resume: skipped voiceover (voiceover.mp3 exists)")
    else:
        vo = generate_voiceover(pack_dir, draft_id=draft_id, script_text=draft.script)
        messages.append(vo.message)
        state.mark("voiceover")
        save_state(pack_dir, state)
    _end("voiceover", t0)

    # --- TurboScribe ---
    t0 = _step("turboscribe")
    turboscribe_text = ""
    if settings.use_turboscribe_sync:
        from shorts_bot.production.turboscribe_sync import transcribe_audio

        cached = pack_dir / "turboscribe_transcript.txt"
        if resume and state.is_done("turboscribe") and cached.exists():
            turboscribe_text = cached.read_text(encoding="utf-8").strip()
            messages.append(f"Resume: using cached {cached.name}")
        else:
            try:
                ts = transcribe_audio(vo_path)
                turboscribe_text = ts.transcript_text
                messages.append(ts.message)
                state.mark("turboscribe")
            except Exception as exc:
                if settings.require_paid_stack and not settings.allow_script_timing_fallback:
                    state.mark("turboscribe", status="failed")
                    save_state(pack_dir, state)
                    raise RuntimeError(
                        f"TurboScribe Whale sync required but failed: {exc}. "
                        "Fix: python3 -m shorts_bot.login_handoff --only turboscribe"
                    ) from exc
                messages.append(f"TurboScribe sync failed ({exc}) — falling back to script timing.")
                state.mark("turboscribe", status="failed")
            save_state(pack_dir, state)
    _end("turboscribe", t0)

    # --- Pack ---
    t0 = _step("pack")
    if settings.require_paid_stack and not settings.allow_script_timing_fallback:
        if not turboscribe_text.strip() and not (pack_dir / "turboscribe_transcript.txt").exists():
            raise RuntimeError(
                "TurboScribe transcript missing — video cannot be built without Whale timestamps. "
                "Re-run after TurboScribe sync succeeds."
            )

    pack = build_production_pack(
        store,
        draft_id=draft_id,
        turboscribe_text=turboscribe_text,
        auto_from_script=not turboscribe_text.strip(),
        render_images=True,
    )
    messages.append(pack.message)
    state.mark("pack")
    save_state(pack_dir, state)
    _end("pack", t0)

    # --- Render ---
    t0 = _step("render")
    variety = variety_for_draft(draft_id)
    messages.append(variety.summary())
    video = render_short_video(
        pack_dir,
        draft_id=draft_id,
        caption_y_offset=variety.caption_y_offset,
        zoom_motion=variety.zoom_motion if settings.video_ken_burns else "none",
    )
    messages.append(video.message)
    state.mark("render")
    save_state(pack_dir, state)
    _end("render", t0)

    # --- Video QC ---
    t0 = _step("video_qc")
    vqc = run_video_qc(video.output_path)
    messages.append(vqc.summary())
    if not vqc.passed:
        state.mark("video_qc", status="failed")
    else:
        state.mark("video_qc")
    save_state(pack_dir, state)
    _end("video_qc", t0)

    # --- Upload metadata ---
    t0 = _step("metadata")
    from shorts_bot.production.research import load_research

    research = load_research(draft.topic)
    package = build_upload_package(draft.topic, draft.hook, draft_id=draft_id, research=research)
    write_upload_files(pack_dir, package, draft_id=draft_id)
    state.mark("metadata")
    save_state(pack_dir, state)
    _end("metadata", t0)

    upload_url: str | None = None
    do_upload = upload_youtube if upload_youtube is not None else settings.auto_upload_youtube
    if do_upload and video.output_path.exists():
        if settings.video_qc_blocks_upload and not vqc.passed:
            messages.append("Upload blocked — video QC failed")
            do_upload = False

        qc = run_quality_checks(
            topic=draft.topic,
            script=draft.script,
            hook=draft.hook,
            help_angle=draft.help_angle,
        )
        if settings.quality_gate_blocks_upload and not qc.passed:
            messages.append(f"Upload blocked — quality gate: {qc.summary()}")
            do_upload = False
        elif qc.warnings:
            messages.append(f"Quality warnings: {'; '.join(qc.warnings[:3])}")

        if do_upload:
            from shorts_bot.memory.extensions import MemoryExtensions
            from shorts_bot.youtube.upload import upload_short
            from shorts_bot.youtube.upload_guardrails import preflight_upload

            mem = MemoryExtensions(store)
            from shorts_bot.compliance.upload_guard import record_upload

            pre = preflight_upload(
                store,
                mem,
                draft_id=draft_id,
                topic=draft.topic,
                hook=draft.hook,
                script=draft.script,
                title=package.title,
            )
            if not pre.allowed:
                messages.append(f"Upload blocked — {pre.message}")
                do_upload = False

        if do_upload:
            try:
                up = upload_short(
                    video.output_path,
                    title=package.title,
                    description=package.description,
                    tags=package.tags,
                    visibility=package.visibility,
                )
                upload_url = up.video_url
                messages.append(up.message)
                record_upload(
                    mem,
                    draft_id=draft_id,
                    topic=draft.topic,
                    hook=draft.hook,
                    script=draft.script,
                    title=package.title,
                    video_id=up.video_id,
                )
                if settings.auto_publish_hours > 0 and package.visibility == "unlisted":
                    mem.schedule_publish(
                        video_id=up.video_id,
                        draft_id=draft_id,
                        visibility="unlisted",
                        publish_after_hours=settings.auto_publish_hours,
                    )
                    messages.append(
                        f"Scheduled public publish in {settings.auto_publish_hours}h "
                        f"(video {up.video_id})"
                    )
                state.mark("upload")
                save_state(pack_dir, state)
            except Exception as exc:
                messages.append(f"YouTube upload failed: {exc}")
                state.mark("upload", status="failed")
                save_state(pack_dir, state)

    report = _write_pipeline_report(pack_dir, draft_id, messages, timings)
    return PipelineResult(
        draft_id=draft_id,
        pack_dir=pack_dir,
        messages=messages,
        video_path=video.output_path,
        upload_url=upload_url,
        report_path=report,
        step_timings=timings,
    )
