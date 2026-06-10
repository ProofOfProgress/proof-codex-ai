"""Full automated Short pipeline — voice clone → TurboScribe → render → optional upload."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pack import build_production_pack
from shorts_bot.production.render_video import render_short_video
from shorts_bot.production.script_humanize import finalize_script
from shorts_bot.production.upload_meta import build_upload_package, write_upload_files
from shorts_bot.production.voiceover import generate_voiceover


@dataclass
class PipelineResult:
    draft_id: int
    pack_dir: Path
    messages: list[str]
    video_path: Path | None
    upload_url: str | None


def _write_voice_script(pack_dir: Path, hook: str, script: str) -> None:
    pack_dir.mkdir(parents=True, exist_ok=True)
    (pack_dir / "VOICEOVER_SCRIPT.txt").write_text(
        f"HOOK: {hook}\n\n{script}\n",
        encoding="utf-8",
    )


def finish_draft_pipeline(
    store: MemoryStore,
    draft_id: int,
    *,
    upload_youtube: bool | None = None,
) -> PipelineResult:
    """
    End-to-end production:

    1. Humanize script
    2. Resemble voice clone → voiceover.mp3
    3. TurboScribe Whale → tight timestamps
    4. Rebuild stick-figure pack synced to audio
    5. ffmpeg → final_short.mp4
    6. Upload metadata (+ optional YouTube API upload)
    """
    draft = store.get_draft(draft_id)
    pack_dir = settings.data_dir / "production" / f"draft_{draft_id}"
    messages: list[str] = []

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
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        finalized.message + "\nscores: " + str(finalized.scores_log) + "\n",
        encoding="utf-8",
    )

    draft = store.get_draft(draft_id)
    _write_voice_script(pack_dir, draft.hook, draft.script)

    vo = generate_voiceover(pack_dir, draft_id=draft_id, script_text=draft.script)
    messages.append(vo.message)

    turboscribe_text = ""
    if settings.use_turboscribe_sync:
        from shorts_bot.production.turboscribe_sync import transcribe_audio

        try:
            ts = transcribe_audio(pack_dir / "voiceover.mp3")
            turboscribe_text = ts.transcript_text
            messages.append(ts.message)
        except Exception as exc:
            messages.append(f"TurboScribe sync failed ({exc}) — falling back to script timing.")
            turboscribe_text = ""

    pack = build_production_pack(
        store,
        draft_id=draft_id,
        turboscribe_text=turboscribe_text,
        auto_from_script=not turboscribe_text.strip(),
        render_images=True,
    )
    messages.append(pack.message)

    video = render_short_video(pack_dir, draft_id=draft_id)
    messages.append(video.message)

    from shorts_bot.production.research import load_research

    research = load_research(draft.topic)
    package = build_upload_package(draft.topic, draft.hook, draft_id=draft_id, research=research)
    write_upload_files(pack_dir, package, draft_id=draft_id)

    upload_url: str | None = None
    do_upload = upload_youtube if upload_youtube is not None else settings.auto_upload_youtube
    if do_upload and video.output_path.exists():
        from shorts_bot.drafts.quality import run_quality_checks
        from shorts_bot.memory.extensions import MemoryExtensions
        from shorts_bot.youtube.upload import upload_short

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
            mem = MemoryExtensions(store)
            from shorts_bot.compliance.upload_guard import check_upload_allowed, record_upload

            compliance = check_upload_allowed(
                store,
                mem,
                draft_id=draft_id,
                topic=draft.topic,
                hook=draft.hook,
                script=draft.script,
                title=package.title,
            )
            if not compliance.allowed:
                messages.append(f"Upload blocked — YPP guard: {compliance.summary()}")
                do_upload = False
            elif compliance.warnings:
                messages.append(f"YPP warnings: {'; '.join(compliance.warnings[:3])}")

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
            except Exception as exc:
                messages.append(f"YouTube upload failed: {exc}")

    return PipelineResult(
        draft_id=draft_id,
        pack_dir=pack_dir,
        messages=messages,
        video_path=video.output_path,
        upload_url=upload_url,
    )
