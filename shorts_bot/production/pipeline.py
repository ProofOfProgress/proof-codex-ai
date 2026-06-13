"""Full automated Short pipeline — voice clone → transcript sync → render → optional upload."""

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
from shorts_bot.production.vision_qc import load_cached_report, run_vision_qc
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
    success: bool = True
    qc_passed: bool = True

    @property
    def ok(self) -> bool:
        return self.success


def _manifest_needs_repack(manifest_path: Path) -> bool:
    """Re-pack when visual style requires motion but checkpoint used slideshow."""
    from shorts_bot.config import settings

    if not manifest_path.exists():
        return False
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return True
    if settings.visual_style != "ai_video":
        return False
    expected_mode = "kling_clips" if settings.uses_kling_video else "video_clips"
    if manifest.get("render_mode") != expected_mode:
        return True
    if int(manifest.get("clips_rendered") or 0) < 1:
        return True
    return False


def _write_voice_script(pack_dir: Path, hook: str, script: str) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "VOICEOVER_SCRIPT.txt").write_text(
        f"HOOK: {hook}\n\n{script}\n",
        encoding="utf-8",
    )


def _write_pipeline_report(
    pack_dir: Path,
    draft_id: int,
    messages: list[str],
    timings: dict,
    *,
    vision_qc: dict | None = None,
) -> Path:
    report = {
        "draft_id": draft_id,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "messages": messages,
        "step_timings_sec": timings,
        "variety": variety_for_draft(draft_id).summary(),
    }
    if vision_qc:
        report["vision_qc"] = vision_qc
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
    4. AssemblyAI or TurboScribe → tight timestamps
    5. Rebuild stick-figure pack synced to audio
    6. ffmpeg → final_short.mp4 + video QC
    7. Upload metadata (+ optional YouTube API upload)
    """
    import time

    from shorts_bot.production.paid_stack import ensure_paid_stack_ready

    ensure_paid_stack_ready()

    from shorts_bot.production.pipeline_lock import pipeline_lock

    draft = store.get_draft(draft_id)
    pack_dir = settings.data_dir / "production" / f"draft_{draft_id}"
    pack_dir.mkdir(parents=True, exist_ok=True)

    with pipeline_lock(draft_id):
        return _run_pipeline_locked(
            store,
            draft_id,
            draft=draft,
            pack_dir=pack_dir,
            upload_youtube=upload_youtube,
            resume=resume,
        )


def _run_pipeline_locked(
    store: MemoryStore,
    draft_id: int,
    *,
    draft,
    pack_dir: Path,
    upload_youtube: bool | None,
    resume: bool,
) -> PipelineResult:
    import time

    from shorts_bot.production.horror_guard import (
        ensure_horror_voice_before_pipeline,
        guard_after_humanize,
    )
    from shorts_bot.production.pipeline_integrity import (
        clear_render_artifacts,
        content_stamp_stale,
        write_content_stamp,
    )

    state = load_state(pack_dir, draft_id)
    messages: list[str] = []
    timings: dict[str, float] = {}

    pre = ensure_horror_voice_before_pipeline(
        store,
        draft_id,
        hook=draft.hook,
        script=draft.script,
        help_angle=draft.help_angle,
        topic=draft.topic,
    )
    if pre.repaired:
        messages.append(pre.message)
        draft = store.get_draft(draft_id)
        resume = False

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
        return PipelineResult(
            draft_id,
            pack_dir,
            messages,
            None,
            None,
            report,
            timings,
            success=False,
            qc_passed=False,
        )
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
        if settings.ai_detect_blocks_render and not finalized.passed:
            msg = f"Pipeline blocked — AI detector: {finalized.message}"
            messages.append(msg)
            state.mark("humanize", status="blocked")
            save_state(pack_dir, state)
            log_path = pack_dir / "ai_detect_log.txt"
            log_path.write_text(
                finalized.message + "\nscores: " + str(finalized.scores_log) + "\n",
                encoding="utf-8",
            )
            report = _write_pipeline_report(pack_dir, draft_id, messages, timings)
            return PipelineResult(
                draft_id,
                pack_dir,
                messages,
                None,
                None,
                report,
                timings,
                success=False,
                qc_passed=False,
            )
        guarded = guard_after_humanize(
            store,
            draft_id,
            hook=finalized.hook,
            script=finalized.script,
            help_angle=finalized.help_angle,
            topic=draft.topic,
        )
        store.update_draft_content(
            draft_id,
            hook=guarded.hook,
            script=guarded.script,
            help_angle=guarded.help_angle,
            quality_notes=f"AI score {finalized.final_ai_score}/100 after {finalized.passes} passes",
        )
        msg = finalized.message
        if guarded.repaired:
            msg = f"{msg} | {guarded.message}"
            for step in ("voiceover", "transcript", "pack", "render", "vision_qc"):
                state.steps.pop(step, None)
            save_state(pack_dir, state)
        messages.append(msg)
        log_path = pack_dir / "ai_detect_log.txt"
        log_path.write_text(
            msg + "\nscores: " + str(finalized.scores_log) + "\n",
            encoding="utf-8",
        )
        state.mark("humanize")
        save_state(pack_dir, state)
    draft = store.get_draft(draft_id)
    stamp_was_stale = content_stamp_stale(pack_dir, hook=draft.hook, script=draft.script)
    clips_dir = pack_dir / "clips"
    if stamp_was_stale and clips_dir.is_dir() and any(clips_dir.glob("*.mp4")):
        cleared = clear_render_artifacts(pack_dir)
        if cleared:
            messages.append(
                f"Stale I2V artifacts cleared ({len(cleared)} files) — script/content changed"
            )
            for step in ("voiceover", "transcript", "pack", "render", "vision_qc"):
                state.steps.pop(step, None)
            save_state(pack_dir, state)
    write_content_stamp(pack_dir, hook=draft.hook, script=draft.script)
    _write_voice_script(pack_dir, draft.hook, draft.script)
    _end("humanize", t0)

    # --- Voiceover (skip when Kling carries native character audio) ---
    t0 = _step("voiceover")
    vo_path = pack_dir / "voiceover.mp3"
    from shorts_bot.production.launch_phase import is_silent_launch_draft, skip_narrator_tts

    if skip_narrator_tts(draft_id):
        if is_silent_launch_draft(draft_id):
            messages.append(
                "Skipped narrator TTS — launch phase (videos 1–3): ambient + SFX only, no talking."
            )
        else:
            messages.append(
                "Skipped narrator TTS — Kling native audio (character voices in video clips)."
            )
        state.mark("voiceover")
        save_state(pack_dir, state)
        _end("voiceover", t0)
    else:
        from shorts_bot.production.voiceover import voiceover_checkpoint_stale

        vo_stale = voiceover_checkpoint_stale(pack_dir, draft.script)
        if vo_stale and state.is_done("voiceover"):
            messages.append("Voiceover checkpoint stale — regenerating (provider/delivery/script changed)")
            for step in ("transcript", "pack", "render", "vision_qc"):
                state.steps.pop(step, None)
            for stale in ("transcript.txt", "turboscribe_transcript.txt"):
                (pack_dir / stale).unlink(missing_ok=True)
            save_state(pack_dir, state)
        if resume and state.is_done("voiceover") and vo_path.exists() and not vo_stale:
            messages.append("Resume: skipped voiceover (voiceover.mp3 exists)")
        else:
            vo = generate_voiceover(pack_dir, draft_id=draft_id, script_text=draft.script)
            messages.append(vo.message)
            state.mark("voiceover")
            save_state(pack_dir, state)
        _end("voiceover", t0)

    # --- Transcript sync (AssemblyAI API) ---
    t0 = _step("transcript")
    turboscribe_text = ""
    from shorts_bot.production.launch_phase import skip_transcript_sync

    if skip_transcript_sync(draft_id):
        if is_silent_launch_draft(draft_id):
            messages.append(
                "Skipped transcript sync — launch phase: no subtitles on videos 1–3."
            )
        else:
            messages.append("Skipped transcript sync — caption timing from script (Kling mode).")
        state.mark("transcript")
        save_state(pack_dir, state)
        _end("transcript", t0)
    else:
        from shorts_bot.production.transcript_sync import transcribe_audio

        cached_paths = [pack_dir / "transcript.txt", pack_dir / "turboscribe_transcript.txt"]
        cached_hit = next((p for p in cached_paths if p.exists()), None)
        if resume and state.is_done("transcript") and cached_hit:
            turboscribe_text = cached_hit.read_text(encoding="utf-8").strip()
            messages.append(f"Resume: using cached {cached_hit.name}")
        else:
            try:
                ts = transcribe_audio(vo_path)
                turboscribe_text = ts.transcript_text
                messages.append(ts.message)
                state.mark("transcript")
            except Exception as exc:
                if settings.require_paid_stack and not settings.allow_script_timing_fallback:
                    state.mark("transcript", status="failed")
                    save_state(pack_dir, state)
                    raise RuntimeError(
                        f"Gemini transcript sync required but failed: {exc}. "
                        "Check GEMINI_API_KEY in Cursor secrets (bash scripts/install.sh)."
                    ) from exc
                messages.append(f"Transcript sync failed ({exc}) — falling back to script timing.")
                state.mark("transcript", status="failed")
            save_state(pack_dir, state)
        _end("transcript", t0)

    # --- Pack ---
    t0 = _step("pack")
    if (
        settings.require_paid_stack
        and not settings.allow_script_timing_fallback
        and not settings.uses_kling_native_audio
    ):
        if not turboscribe_text.strip() and not (pack_dir / "turboscribe_transcript.txt").exists():
            raise RuntimeError(
                "Transcript missing — video cannot be built without word-level timestamps. "
                "Re-run after transcript sync succeeds."
            )

    manifest_path = pack_dir / "manifest.json"
    pack_stale = _manifest_needs_repack(manifest_path)
    if pack_stale and state.is_done("pack"):
        messages.append("Pack checkpoint stale — slideshow/manifest mismatch; rebuilding for I2V")
        state.steps.pop("pack", None)
        state.steps.pop("render", None)
        save_state(pack_dir, state)
    if resume and state.is_done("pack") and manifest_path.exists() and not pack_stale:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        from shorts_bot.production.pack import ProductionPack

        pack = ProductionPack(
            draft_id=draft_id,
            topic=manifest.get("topic") or draft.topic,
            output_dir=pack_dir,
            image_count=int(manifest.get("image_count") or 0),
            images_rendered=int(manifest.get("images_rendered") or 0),
            manifest_path=manifest_path,
            message=f"Resume: skipped pack ({manifest_path.name})",
        )
        messages.append(pack.message)
    else:
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
    final_mp4 = pack_dir / "final_short.mp4"
    if resume and state.is_done("render") and final_mp4.exists():
        from shorts_bot.production.render_video import RenderedVideo, _probe_duration

        video = RenderedVideo(
            draft_id=draft_id,
            output_path=final_mp4,
            duration_seconds=_probe_duration(final_mp4),
            message=f"Resume: skipped render ({final_mp4.name})",
        )
        messages.append(video.message)
    else:
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

    # --- Gemini vision QC (sparse frames, one call) ---
    t0 = _step("vision_qc")
    if resume and state.is_done("vision_qc"):
        vision = load_cached_report(pack_dir, video.output_path)
        if not vision:
            vision = run_vision_qc(
                video.output_path,
                pack_dir,
                topic=draft.topic,
                hook=draft.hook,
                use_cache=False,
            )
            if vision.passed:
                state.mark("vision_qc")
            else:
                state.mark("vision_qc", status="failed")
            save_state(pack_dir, state)
        messages.append(f"Resume: {vision.summary()}")
    else:
        vision = run_vision_qc(
            video.output_path,
            pack_dir,
            topic=draft.topic,
            hook=draft.hook,
        )
        messages.append(vision.summary())
        if vision.passed:
            state.mark("vision_qc")
        else:
            state.mark("vision_qc", status="failed")
    save_state(pack_dir, state)
    _end("vision_qc", t0)

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
        if settings.vision_qc_blocks_upload and not vision.passed:
            messages.append("Upload blocked — vision QC failed")
            do_upload = False
            if settings.self_training_enabled:
                from shorts_bot.learning.reflect import reflect_after_vision_qc
                from shorts_bot.memory.extensions import MemoryExtensions

                mem_qc = MemoryExtensions(store)
                msg = reflect_after_vision_qc(
                    mem_qc,
                    draft_id=draft_id,
                    topic=draft.topic,
                    score=vision.score,
                    passed=vision.passed,
                    issues=vision.issues,
                )
                if msg:
                    messages.append(f"Self-learning: {msg[:200]}")

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
            from shorts_bot.youtube.google_auth import upload_ready
            from shorts_bot.youtube.upload import upload_short
            from shorts_bot.youtube.upload_guardrails import preflight_upload

            api_ready = upload_ready()
            use_studio_upload = (
                settings.youtube_studio_upload_fallback
                and settings.youtube_upload_via_api
                and not api_ready
            )

            if settings.youtube_upload_via_api and not api_ready and not use_studio_upload:
                messages.append(
                    "Upload blocked — YouTube token missing API upload scope. "
                    "Run once at home: python3 -m shorts_bot.youtube.auth_cli "
                    "(Google sign-in in your browser, not Playwright)"
                )
                do_upload = False
            elif use_studio_upload:
                messages.append(
                    "YouTube API not ready — uploading via Studio browser (saved profile)."
                )

            mem = MemoryExtensions(store)
            from shorts_bot.compliance.upload_guard import record_upload

            if do_upload:
                pre = preflight_upload(
                    store,
                    mem,
                    draft_id=draft_id,
                    topic=draft.topic,
                    hook=draft.hook,
                    script=draft.script,
                    title=package.title,
                    visibility=package.visibility,
                )
                if not pre.allowed:
                    messages.append(f"Upload blocked — {pre.message}")
                    do_upload = False

        if do_upload:
            try:
                if use_studio_upload:
                    import os

                    from shorts_bot.youtube.studio_upload import upload_via_studio

                    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
                    studio = upload_via_studio(
                        video.output_path,
                        title=package.title,
                        description=package.description,
                        visibility=package.visibility,
                        pack_dir=pack_dir,
                        headless=not has_display,
                    )
                    if not studio.ok:
                        raise RuntimeError(studio.message)
                    up_video_id = studio.video_id
                    upload_url = studio.video_url
                    messages.append(studio.message)
                else:
                    up = upload_short(
                        video.output_path,
                        title=package.title,
                        description=package.description,
                        tags=package.tags,
                        visibility=package.visibility,
                    )
                    up_video_id = up.video_id
                    upload_url = up.video_url
                    messages.append(up.message)
                if settings.post_upload_cta_comment and not use_studio_upload:
                    from shorts_bot.youtube.post_upload import post_upload_cta_comment

                    cta_id = post_upload_cta_comment(up_video_id, draft_id=draft_id)
                    if cta_id:
                        messages.append(f"Post-upload CTA comment posted ({cta_id[:16]}…)")
                if settings.post_upload_analytics_sync and not use_studio_upload:
                    from shorts_bot.youtube.post_upload import sync_analytics_after_upload

                    sync_msg = sync_analytics_after_upload()
                    messages.append(f"Analytics: {sync_msg[:180]}")
                from shorts_bot.learning.reflect import vision_qc_snapshot

                from shorts_bot.production.scare_pillar import pillar_label, scare_pillar_for_topic

                pillar = scare_pillar_for_topic(draft.topic)
                record_upload(
                    mem,
                    draft_id=draft_id,
                    topic=draft.topic,
                    hook=draft.hook,
                    script=draft.script,
                    title=package.title,
                    video_id=up_video_id,
                    extra_snapshot={
                        "scare_pillar": pillar,
                        "scare_pillar_label": pillar_label(pillar),
                        "vision_qc": vision_qc_snapshot(
                            score=vision.score,
                            passed=vision.passed,
                            issues=vision.issues,
                            warnings=vision.warnings,
                        ),
                    },
                )
                if settings.auto_publish_hours > 0 and package.visibility == "unlisted":
                    mem.schedule_publish(
                        video_id=up_video_id,
                        draft_id=draft_id,
                        visibility="unlisted",
                        publish_after_hours=settings.auto_publish_hours,
                    )
                    messages.append(
                        f"Scheduled public publish in {settings.auto_publish_hours}h "
                        f"(video {up_video_id})"
                    )
                state.mark("upload")
                save_state(pack_dir, state)
            except Exception as exc:
                messages.append(f"YouTube upload failed: {exc}")
                state.mark("upload", status="failed")
                save_state(pack_dir, state)

    from shorts_bot.learning.reflect import vision_qc_snapshot

    report = _write_pipeline_report(
        pack_dir,
        draft_id,
        messages,
        timings,
        vision_qc=vision_qc_snapshot(
            score=vision.score,
            passed=vision.passed,
            issues=vision.issues,
            warnings=vision.warnings,
        ),
    )
    qc_ok = vqc.passed and vision.passed
    pipeline_ok = qc_ok and video.output_path.exists()
    return PipelineResult(
        draft_id=draft_id,
        pack_dir=pack_dir,
        messages=messages,
        video_path=video.output_path,
        upload_url=upload_url,
        report_path=report,
        step_timings=timings,
        success=pipeline_ok,
        qc_passed=qc_ok,
    )
