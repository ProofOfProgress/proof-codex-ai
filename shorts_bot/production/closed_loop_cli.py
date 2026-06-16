"""One command: finish Short → optional YouTube + Facebook publish."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

console = Console()


def closed_loop_status(draft_id: int) -> str:
    from shorts_bot.config import settings
    from shorts_bot.integrations.facebook_reel_api import probe_facebook_reel_api
    from shorts_bot.production.pack_health import assess_pack_health
    from shorts_bot.production.turboscribe_probe import probe_turboscribe
    from shorts_bot.youtube.google_auth import upload_ready

    pack = settings.data_dir / "production" / f"draft_{draft_id}"
    lines = [f"Closed loop status — draft #{draft_id}", ""]

    vo = pack / "voiceover.mp3"
    ts = pack / "turboscribe_transcript.txt"
    video = pack / "final_short.mp4"
    lines.append(f"Voiceover: {'✓' if vo.is_file() else '—'} {vo.name if vo.is_file() else 'missing'}")
    if ts.is_file():
        lines.append(f"TurboScribe transcript: ✓ ({ts.stat().st_size} bytes)")
    else:
        lines.append("TurboScribe transcript: — missing")
    probe = probe_turboscribe(timeout_sec=25)
    lines.append(f"TurboScribe browser: {probe.state.value} — {probe.detail}")
    health = assess_pack_health(pack, draft_id=draft_id, require_final_short=video.is_file())
    lines.append(f"Pack render: {'✓ ready' if health.ready_to_render else '— blocked'}")
    for issue in health.issues[:4]:
        lines.append(f"  • {issue}")
    lines.append(f"Final video: {'✓' if video.is_file() else '—'} {video}")
    lines.append(f"YouTube API: {'✓' if upload_ready() else '— not ready'}")
    fb_ok, fb_msg = probe_facebook_reel_api()
    lines.append(f"Facebook API: {'✓' if fb_ok else '—'} {fb_msg}")
    lines.append("")
    if video.is_file() and upload_ready():
        lines.append("Next: python3 -m shorts_bot.production.closed_loop_cli --draft-id "
                     f"{draft_id} --youtube" + (" --facebook" if fb_ok else ""))
    elif not ts.is_file():
        lines.append("Next: export TurboScribe timestamps → turboscribe_transcript.txt in pack folder")
    elif not fb_ok:
        lines.append("Next: add FACEBOOK_PAGE_ID + META_PAGE_ACCESS_TOKEN to Cursor Secrets")
    return "\n".join(lines)


def closed_loop_publish(
    draft_id: int,
    *,
    upload_youtube: bool = False,
    upload_facebook: bool = False,
    resume: bool = True,
) -> str:
    from shorts_bot.config import settings
    from shorts_bot.memory.store import MemoryStore
    from shorts_bot.production.pipeline import finish_draft_pipeline

    store = MemoryStore(settings.database_path)
    result = finish_draft_pipeline(
        store,
        draft_id,
        upload_youtube=upload_youtube,
        resume=resume,
    )
    lines = list(result.messages)
    pack = result.pack_dir
    video = result.video_path or (pack / "final_short.mp4")

    if upload_facebook and video.is_file():
        from shorts_bot.integrations.facebook_reel_api import upload_facebook_reel

        draft = store.get_draft(draft_id)
        desc = f"{draft.hook}\n\n#horror #scarystories #lostinthewoods"
        try:
            fb = upload_facebook_reel(video, description=desc, title=draft.hook[:100])
            lines.append(fb.message)
        except Exception as exc:
            lines.append(f"Facebook upload skipped: {exc}")

    lines.append(f"Pack: {pack}")
    if video.is_file():
        lines.append(f"Video: {video}")
        srt = pack / "captions.srt"
        if srt.is_file():
            lines.append(f"Captions: {srt} (audio-linked, not burned in)")
    if result.upload_url:
        lines.append(f"YouTube: {result.upload_url}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Closed loop: render + publish")
    parser.add_argument("--draft-id", type=int, required=True)
    parser.add_argument("--status", action="store_true", help="Show closed-loop readiness")
    parser.add_argument("--youtube", action="store_true")
    parser.add_argument("--facebook", action="store_true")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args()

    if args.status:
        console.print(closed_loop_status(args.draft_id))
        raise SystemExit(0)

    from shorts_bot.config import settings

    fb = args.facebook or settings.auto_upload_facebook
    msg = closed_loop_publish(
        args.draft_id,
        upload_youtube=args.youtube,
        upload_facebook=fb,
        resume=not args.no_resume,
    )
    console.print(f"[green]{msg}[/green]")


if __name__ == "__main__":
    main()
