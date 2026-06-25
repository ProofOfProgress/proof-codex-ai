"""Generate InVideo project from approved draft script."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.invideo.mcp_client import InVideoMcpClient
from shorts_bot.invideo.script_pack import draft_pack_dir, write_script_pack
from shorts_bot.invideo.ms_byte import ms_byte_brief
from shorts_bot.memory.store import MemoryStore


@dataclass
class InVideoGenerateResult:
    draft_id: int | None
    topic: str
    project_url: str
    prompt: str
    script_path: Path | None
    message: str


def generate_from_prompt(
    prompt: str,
    *,
    topic: str,
    open_browser: bool = False,
    vibe: str | None = None,
    target_audience: str | None = None,
    platform: str | None = None,
    draft_id: int | None = None,
) -> InVideoGenerateResult:
    """
    Send a creative brief to InVideo — it writes the script and builds the project.
    The MCP `script` field carries the prompt; InVideo generates copy on its side.
    """
    project_url = generate_from_script(
        prompt,
        topic=topic,
        vibe=vibe,
        target_audience=target_audience,
        platform=platform,
    )

    script_path: Path | None = None
    if draft_id is not None:
        script_path = write_script_pack(draft_id, script=prompt, topic=topic)
        meta_path = draft_pack_dir(draft_id) / "invideo_project.url"
        meta_path.write_text(project_url + "\n", encoding="utf-8")
        (draft_pack_dir(draft_id) / "invideo_prompt.txt").write_text(prompt + "\n", encoding="utf-8")
    else:
        out_dir = settings.data_dir / "production" / "invideo_runs"
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = topic.lower().replace(" ", "-")[:40]
        run_dir = out_dir / slug
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "invideo_prompt.txt").write_text(prompt + "\n", encoding="utf-8")
        (run_dir / "invideo_project.url").write_text(project_url + "\n", encoding="utf-8")
        script_path = run_dir / "invideo_prompt.txt"

    if open_browser:
        _open_project_browser(project_url)

    return InVideoGenerateResult(
        draft_id=draft_id,
        topic=topic,
        project_url=project_url,
        prompt=prompt,
        script_path=script_path,
        message=(
            "InVideo project started from prompt — InVideo writes the script. "
            "Desktop browser → watch it generate → export MP4 when done."
        ),
    )


def _open_project_browser(project_url: str) -> None:
    try:
        from shorts_bot.browser.session import _has_display, _launch_context
        import time

        if not _has_display():
            from shorts_bot.browser.session import spawn_visible_browser

            spawn_visible_browser(project_url, minutes=25)
            return
        pw, context = _launch_context(headless=False)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(project_url, wait_until="domcontentloaded", timeout=120000)
            time.sleep(25 * 60)
        finally:
            context.close()
            pw.stop()
    except Exception:
        try:
            from shorts_bot.browser.session import spawn_visible_browser

            spawn_visible_browser(project_url, minutes=25)
        except Exception:
            pass


def generate_from_script(
    script: str,
    *,
    topic: str,
    vibe: str | None = None,
    target_audience: str | None = None,
    platform: str | None = None,
    api_key: str | None = None,
    include_master_context: bool = True,
) -> str:
    from shorts_bot.invideo.system_context import wrap_invideo_prompt

    payload = wrap_invideo_prompt(script) if include_master_context else script.strip()
    client = InVideoMcpClient(api_key=api_key)
    return client.generate_video_from_script(
        script=payload,
        topic=topic,
        vibe=vibe,
        target_audience=target_audience,
        platform=platform,
    )


def generate_from_draft(
    draft_id: int,
    *,
    open_browser: bool = False,
    vibe: str | None = None,
    target_audience: str | None = None,
    platform: str | None = None,
    use_prompt: bool = True,
) -> InVideoGenerateResult:
    """Optional draft link — by default sends topic as InVideo prompt, not our script."""
    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)
    if use_prompt:
        prompt = ms_byte_brief(
            product=draft.topic,
            hook=draft.hook or f"Most people overpay for {draft.topic} — here's what's actually good and broken.",
            angle=draft.help_angle or "",
        )
        return generate_from_prompt(
            prompt,
            topic=draft.topic,
            open_browser=open_browser,
            vibe=vibe,
            target_audience=target_audience,
            platform=platform,
            draft_id=draft_id,
        )

    script_path = write_script_pack(draft_id, script=draft.script, topic=draft.topic, hook=draft.hook)
    project_url = generate_from_script(
        draft.script,
        topic=draft.topic,
        vibe=vibe,
        target_audience=target_audience,
        platform=platform,
    )
    meta_path = draft_pack_dir(draft_id) / "invideo_project.url"
    meta_path.write_text(project_url + "\n", encoding="utf-8")
    if open_browser:
        _open_project_browser(project_url)
    return InVideoGenerateResult(
        draft_id=draft_id,
        topic=draft.topic,
        project_url=project_url,
        prompt=draft.script,
        script_path=script_path,
        message=(
            f"InVideo project started for draft #{draft_id}. "
            "Open project URL in Desktop browser (must be logged in) → Generate → Export MP4 "
            f"to {draft_pack_dir(draft_id) / 'final_short.mp4'}"
        ),
    )
