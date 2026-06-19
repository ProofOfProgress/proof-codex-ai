"""Generate InVideo project from approved draft script."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.invideo.mcp_client import InVideoMcpClient
from shorts_bot.invideo.script_pack import draft_pack_dir, write_script_pack
from shorts_bot.memory.store import MemoryStore


@dataclass
class InVideoGenerateResult:
    draft_id: int
    topic: str
    project_url: str
    script_path: Path
    message: str


def generate_from_script(
    script: str,
    *,
    topic: str,
    vibe: str | None = None,
    target_audience: str | None = None,
    platform: str | None = None,
    api_key: str | None = None,
) -> str:
    client = InVideoMcpClient(api_key=api_key)
    return client.generate_video_from_script(
        script=script,
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
) -> InVideoGenerateResult:
    store = MemoryStore(settings.database_path)
    draft = store.get_draft(draft_id)
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
        try:
            from shorts_bot.browser.session import spawn_visible_browser

            spawn_visible_browser(project_url, minutes=20)
        except Exception:
            pass

    return InVideoGenerateResult(
        draft_id=draft_id,
        topic=draft.topic,
        project_url=project_url,
        script_path=script_path,
        message=(
            f"InVideo project started for draft #{draft_id}. "
            "Open project URL in Desktop browser (must be logged in) → Generate → Export MP4 "
            f"to {draft_pack_dir(draft_id) / 'final_short.mp4'}"
        ),
    )
