"""Upload Short MP4 via YouTube Studio when API token lacks youtube.upload scope."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.youtube.studio import CHROME_UA, open_studio, resolve_channel_id


@dataclass
class StudioUploadResult:
    ok: bool
    video_id: str | None
    video_url: str | None
    message: str


def _dismiss_studio_dialogs(page) -> None:
    """Close overlays that block upload form (auth re-verify, tips)."""
    for pattern in (
        r"not now",
        r"no thanks",
        r"got it",
        r"ok",
        r"close",
        r"skip",
        r"cancel",
    ):
        try:
            btn = page.get_by_role("button", name=re.compile(pattern, re.I))
            if btn.count() and btn.first.is_visible():
                btn.first.click(timeout=2000)
                time.sleep(1)
        except Exception:
            pass
    try:
        backdrop = page.locator("tp-yt-iron-overlay-backdrop.opened")
        if backdrop.count():
            page.keyboard.press("Escape")
            time.sleep(0.5)
    except Exception:
        pass


def _fill_contenteditable(page, locator, text: str) -> bool:
    try:
        if not locator.count():
            return False
        el = locator.first
        el.click(timeout=8000, force=True)
        page.keyboard.press("Control+A")
        page.keyboard.type(text, delay=5)
        return True
    except Exception:
        return False


def _load_metadata(pack_dir: Path) -> dict:
    meta_path = pack_dir / "upload_metadata.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {}


def upload_via_studio(
    video_path: Path,
    *,
    title: str | None = None,
    description: str = "",
    visibility: str | None = None,
    pack_dir: Path | None = None,
    headless: bool | None = None,
    skip_preflight: bool = False,
    allow_duplicate_draft: bool = False,
) -> StudioUploadResult:
    """
    Browser upload through saved Playwright profile (data/browser_profile).

    Uses Studio direct upload URL when channel ID is known.
    """
    if not video_path.exists():
        return StudioUploadResult(False, None, None, f"Video not found: {video_path}")

    meta = _load_metadata(pack_dir) if pack_dir else {}
    draft_id = int(meta.get("draft_id") or 0)
    use_title = title or meta.get("title") or video_path.stem
    use_desc = description or meta.get("description") or ""
    use_vis = (visibility or meta.get("visibility") or settings.youtube_upload_visibility).lower()

    if not skip_preflight and draft_id and pack_dir:
        from shorts_bot.memory.extensions import MemoryExtensions
        from shorts_bot.memory.store import MemoryStore
        from shorts_bot.youtube.upload_guardrails import preflight_upload

        store = MemoryStore(settings.database_path)
        mem = MemoryExtensions(store)
        try:
            draft = store.get_draft(draft_id)
            pre = preflight_upload(
                store,
                mem,
                draft_id=draft_id,
                topic=draft.topic,
                hook=draft.hook,
                script=draft.script,
                title=use_title,
                allow_duplicate_draft=allow_duplicate_draft,
            )
            if not pre.allowed:
                return StudioUploadResult(False, None, None, f"Studio upload blocked: {pre.message}")
        except KeyError:
            pass

    from playwright.sync_api import sync_playwright

    use_headless = settings.browser_headless if headless is None else headless
    profile = settings.browser_profile_dir
    profile.mkdir(parents=True, exist_ok=True)

    video_id: str | None = None
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(profile),
            headless=use_headless,
            user_agent=CHROME_UA,
            viewport={"width": 1400, "height": 900},
            accept_downloads=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            status = open_studio(page)
            if not status.logged_in:
                return StudioUploadResult(
                    False,
                    None,
                    None,
                    "Not logged into YouTube Studio — run login_handoff for youtube.",
                )

            cid = resolve_channel_id(page)
            if cid:
                page.goto(
                    f"https://studio.youtube.com/channel/{cid}/videos/upload?d=ud",
                    wait_until="domcontentloaded",
                    timeout=90000,
                )
            else:
                page.goto("https://www.youtube.com/upload", wait_until="domcontentloaded", timeout=90000)
            time.sleep(2)

            # File chooser — input or Create → Upload
            file_input = page.locator('input[type="file"]').first
            if file_input.count():
                file_input.set_input_files(str(video_path.resolve()))
            else:
                with page.expect_file_chooser(timeout=15000) as fc_info:
                    for label in ("Select files", "SELECT FILES", "Upload videos", "Upload video"):
                        try:
                            page.get_by_text(re.compile(re.escape(label), re.I)).first.click(timeout=4000)
                            break
                        except Exception:
                            continue
                    else:
                        page.get_by_role("button", name=re.compile(r"create", re.I)).first.click(timeout=5000)
                        page.get_by_text(re.compile(r"upload videos?", re.I)).first.click(timeout=5000)
                fc_info.value.set_files(str(video_path.resolve()))

            # Wait for upload dialog / metadata form
            for _ in range(60):
                time.sleep(2)
                _dismiss_studio_dialogs(page)
                if page.locator("#textbox, ytcp-social-suggestions-textbox #textbox").count():
                    break
                if page.get_by_text(re.compile(r"uploading|processing|checks", re.I)).count():
                    continue

            _dismiss_studio_dialogs(page)

            # Title — first textbox in upload dialog is usually title
            title_box = page.locator(
                'ytcp-social-suggestions-textbox #textbox[aria-label*="title" i], '
                "#title-textarea #textbox"
            ).first
            if not _fill_contenteditable(page, title_box, use_title):
                tb = page.locator("#textbox").first
                _fill_contenteditable(page, tb, use_title)

            # Description optional — skip if auth overlay blocks
            if use_desc.strip():
                try:
                    show_more = page.get_by_text(re.compile(r"show more", re.I))
                    if show_more.count() and show_more.first.is_visible():
                        show_more.first.click(timeout=3000, force=True)
                        time.sleep(1)
                except Exception:
                    pass
                desc_box = page.locator(
                    'ytcp-social-suggestions-textbox #textbox[aria-label*="description" i], '
                    "#description-textarea #textbox"
                ).first
                _fill_contenteditable(page, desc_box, use_desc)

            # Not made for kids (default for our channel)
            try:
                nfmk = page.get_by_text(re.compile(r"not made for kids", re.I))
                if nfmk.count():
                    page.locator('tp-yt-paper-radio-button[name="NOT_MADE_FOR_KIDS"]').first.click(timeout=5000)
            except Exception:
                pass

            # Visibility
            try:
                page.get_by_text(re.compile(r"visibility", re.I)).first.click(timeout=5000)
                time.sleep(1)
                vis_pat = {
                    "public": r"^public$",
                    "unlisted": r"unlisted",
                    "private": r"private",
                }.get(use_vis, r"unlisted")
                page.get_by_text(re.compile(vis_pat, re.I)).first.click(timeout=5000)
            except Exception:
                pass

            # Publish / Save
            for btn_label in ("Publish", "Save", "Done", "Schedule"):
                try:
                    btn = page.get_by_role("button", name=re.compile(btn_label, re.I)).last
                    if btn.count() and btn.is_enabled():
                        btn.click(timeout=10000)
                        break
                except Exception:
                    continue

            time.sleep(5)

            # Extract video ID from success link or URL
            body = page.content()
            for pattern in (
                r"watch\?v=([\w-]{11})",
                r"/shorts/([\w-]{11})",
                r'"videoId":"([\w-]{11})"',
            ):
                m = re.search(pattern, body)
                if m:
                    video_id = m.group(1)
                    break

            if not video_id:
                # Content page sometimes shows link after upload
                try:
                    link = page.locator('a[href*="watch?v="], a[href*="/shorts/"]').first
                    if link.count():
                        href = link.get_attribute("href") or ""
                        m = re.search(r"([\w-]{11})", href)
                        if m:
                            video_id = m.group(1)
                except Exception:
                    pass

            url = f"https://youtube.com/shorts/{video_id}" if video_id else None
            msg = f"Studio upload complete: {use_title}"
            if video_id:
                msg += f" → {url}"
            else:
                msg += " (check Studio — video ID not detected in page)"

            if page.get_by_text(re.compile(r"confirm it.?s really you", re.I)).count():
                shot = settings.browser_screenshot_dir / f"studio_upload_auth_{int(time.time())}.png"
                settings.browser_screenshot_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(shot))
                return StudioUploadResult(
                    False,
                    video_id,
                    url,
                    "Google re-verification required — complete in Desktop browser "
                    f"(screenshot: {shot}). File may already be uploading in Studio.",
                )

            if video_id and draft_id and pack_dir:
                try:
                    from shorts_bot.compliance.upload_guard import record_upload
                    from shorts_bot.memory.extensions import MemoryExtensions
                    from shorts_bot.memory.store import MemoryStore

                    store = MemoryStore(settings.database_path)
                    mem = MemoryExtensions(store)
                    draft = store.get_draft(draft_id)
                    record_upload(
                        mem,
                        draft_id=draft_id,
                        topic=draft.topic,
                        hook=draft.hook,
                        script=draft.script,
                        title=use_title,
                        video_id=video_id,
                    )
                except Exception:
                    pass

            return StudioUploadResult(ok=bool(video_id), video_id=video_id, video_url=url, message=msg)
        except Exception as exc:
            try:
                shot = settings.browser_screenshot_dir / f"studio_upload_err_{int(time.time())}.png"
                settings.browser_screenshot_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(shot))
                extra = f" screenshot: {shot}"
            except Exception:
                extra = ""
            return StudioUploadResult(False, None, None, f"Studio upload failed: {exc}{extra}")
        finally:
            ctx.close()


def upload_pack_via_studio(pack_dir: Path, *, headless: bool | None = None) -> StudioUploadResult:
    """Upload final_short.mp4 from a production pack folder."""
    video = pack_dir / "final_short.mp4"
    return upload_via_studio(video, pack_dir=pack_dir, headless=headless)
