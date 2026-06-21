"""Daily autopilot — product topic → InVideo → MP4 → YouTube."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.invideo.generate import generate_from_prompt
from shorts_bot.invideo.prompts import shorts_product_brief
from shorts_bot.invideo.script_pack import draft_pack_dir
from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.product_rotation import next_product_topic, product_name_from_topic


@dataclass
class InVideoDailyResult:
    ok: bool
    draft_id: int
    topic: str
    project_url: str
    video_path: Path | None
    upload_url: str | None
    messages: list[str]

    @property
    def summary(self) -> str:
        return "\n".join(self.messages)


def run_invideo_daily(
    *,
    topic: str | None = None,
    upload: bool | None = None,
    wait_render_sec: int = 2400,
) -> InVideoDailyResult:
    """
    One daily Short via InVideo (soul of the channel):
    pick product → brief → MCP project → browser generate/download → YouTube upload.
    """
    store = MemoryStore(settings.database_path)
    topic = topic or next_product_topic(store)
    product = product_name_from_topic(topic)
    hook = f"Everyone's paying for {product} — I tested if it's worth it."
    brief = shorts_product_brief(
        product=product,
        hook=hook,
        verdict_hint="Pay, Skip, or Wait",
        extra=f"Topic line for upload: {topic}",
    )

    messages: list[str] = [f"Product: {product}", f"Topic: {topic}"]
    draft = store.save_draft(
        topic=topic,
        script=brief,
        hook=hook,
        help_angle="Pay / Skip / Wait — honest 30s AI product review",
        quality_notes="InVideo daily autopilot",
    )
    messages.append(f"Draft #{draft.id} created")

    if settings.auto_approve_drafts:
        store.review_draft(draft.id, "approved", "Auto-approved (InVideo daily)")
        messages.append(f"Auto-approved draft #{draft.id}")

    gen = generate_from_prompt(brief, topic=topic, draft_id=draft.id)
    messages.append(f"InVideo project: {gen.project_url}")

    pack = draft_pack_dir(draft.id)
    video_path = pack / "final_short.mp4"
    upload_url: str | None = None

    try:
        from shorts_bot.invideo.ship_cli import ship

        ship(gen.project_url, video_path, wait_render_sec=wait_render_sec)
        messages.append(f"MP4 saved: {video_path}")
    except Exception as exc:
        msg = str(exc)[:300]
        messages.append(f"InVideo render/download: {msg}")
        from shorts_bot.automation.alerts import record_automation_alert

        record_automation_alert(
            "invideo_daily",
            msg,
            detail=(
                f"draft={draft.id} project={gen.project_url} — "
                "If credits exhausted: Generate on laptop → Drive link → fetch_url_cli"
            ),
        )

    do_upload = settings.auto_upload_youtube if upload is None else upload
    ok = video_path.is_file() and video_path.stat().st_size > 50_000

    if ok and do_upload:
        try:
            from shorts_bot.production.upload_canonical_cli import upload_canonical

            upload_url = upload_canonical(draft.id, video_path)
            messages.append(f"PUBLISHED: {upload_url}")
            store.review_draft(draft.id, "published", upload_url or "uploaded")
        except Exception as exc:
            messages.append(f"YouTube upload failed: {exc}")
            ok = False
    elif not ok:
        messages.append(
            "No MP4 on disk — daily run stopped before upload. "
            "Check InVideo credits or paste Drive link for fetch_url_cli."
        )

    return InVideoDailyResult(
        ok=ok and bool(upload_url) if do_upload else ok,
        draft_id=draft.id,
        topic=topic,
        project_url=gen.project_url,
        video_path=video_path if ok else None,
        upload_url=upload_url,
        messages=messages,
    )
