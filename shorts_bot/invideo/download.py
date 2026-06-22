"""Download finished InVideo projects via logged-in browser session."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from shorts_bot.config import settings
from shorts_bot.invideo.import_cli import import_mp4
from shorts_bot.invideo.script_pack import draft_pack_dir

LOGIN_MARKERS = ("welcome to invideo ai", "continue with google", "log in", "create an account")
READY_MARKERS = ("download settings", "edit & download")
GENERATE_MARKERS = ("generate", "·", "credits")
GENERATING_MARKERS = ("%", "processing", "rendering", "generating")
SKIP_MP4_SUBSTRINGS = ("film_grain", "placeholder", "preview-thumb")


class ProjectState(str, Enum):
    LOGIN_REQUIRED = "login"
    GENERATE_PENDING = "generate_pending"
    GENERATING = "generating"
    READY = "ready"
    UNKNOWN = "unknown"


@dataclass
class DownloadResult:
    ok: bool
    dest: Path | None
    project_url: str
    message: str
    state: ProjectState = ProjectState.UNKNOWN
    bytes_written: int = 0


def read_project_url(
    *,
    draft_id: int | None = None,
    run_dir: Path | str | None = None,
    project_url: str | None = None,
) -> str:
    if project_url and project_url.strip():
        return project_url.strip()
    if draft_id is not None:
        meta = draft_pack_dir(draft_id) / "invideo_project.url"
        if meta.is_file():
            return meta.read_text(encoding="utf-8").strip()
    if run_dir is not None:
        meta = Path(run_dir) / "invideo_project.url"
        if meta.is_file():
            return meta.read_text(encoding="utf-8").strip()
    raise FileNotFoundError(
        "No project URL — pass --project-url or --draft-id with invideo_project.url saved"
    )


def detect_project_state(body: str, url: str = "") -> ProjectState:
    lower = (body or "").lower()
    url_lower = (url or "").lower()

    logged_in_chrome = "create new" in lower or "library" in lower
    if (
        any(m in lower for m in LOGIN_MARKERS)
        and not logged_in_chrome
    ) or "signup" in url_lower:
        return ProjectState.LOGIN_REQUIRED

    has_download = bool(re.search(r"\bdownload\b", lower))
    has_generate = bool(re.search(r"\bgenerate\b", lower))

    if has_download and ("edit & download" in lower or "edit" in lower):
        return ProjectState.READY
    if has_download:
        return ProjectState.READY

    title_pct = re.search(r"\b(\d{1,3})%\b", lower)
    if title_pct and int(title_pct.group(1)) < 100 and not has_download:
        return ProjectState.GENERATING
    if any(m in lower for m in GENERATING_MARKERS) and has_generate and not has_download:
        return ProjectState.GENERATING
    if has_generate and not has_download:
        return ProjectState.GENERATE_PENDING
    return ProjectState.UNKNOWN


def _looks_like_video_url(url: str) -> bool:
    u = url.lower()
    if any(skip in u for skip in SKIP_MP4_SUBSTRINGS):
        return False
    if ".mp4" in u or ".webm" in u:
        return True
    if any(host in u for host in ("cloudfront.net", "amazonaws.com", "googleusercontent.com")):
        if any(ext in u for ext in (".mp4", "/video", "video/", "renders", "exports")):
            return True
    ct_hosts = ("cdn", "storage", "media", "assets")
    return any(h in u for h in ct_hosts) and any(k in u for k in ("mp4", "export", "render", "download"))


def _pick_resolution_button(page, resolution: str):
    return page.locator("button").filter(has_text=resolution).first


def _open_download_modal(page) -> None:
    btn = page.locator("button").filter(has_text=re.compile(r"^Download$", re.I))
    if not btn.count():
        btn = page.get_by_text("Download", exact=True)
    btn.first.click(force=True, timeout=30_000)
    time.sleep(3)
    page.wait_for_selector("text=Download Settings", timeout=60_000)


def _configure_download_options(
    page,
    *,
    resolution: str = "480p",
    watermarks: str = "stock",
) -> None:
    if watermarks == "stock":
        page.locator("button").filter(has_text="Stock Watermarks").first.click(force=True, timeout=10_000)
    elif watermarks == "none":
        page.locator("button").filter(has_text="No Watermarks").first.click(force=True, timeout=10_000)
    _pick_resolution_button(page, resolution).click(force=True, timeout=10_000)
    time.sleep(0.5)


def _click_modal_download(page) -> None:
    cont = page.locator("button").filter(has_text=re.compile(r"^Continue$", re.I))
    if cont.count():
        cont.first.click(force=True, timeout=15_000)
        return
    buttons = page.locator("button").filter(has_text=re.compile(r"^Download$", re.I))
    if buttons.count() >= 2:
        buttons.last.click(force=True, timeout=15_000)
        return
    page.locator("button").filter(has_text="Download").last.click(force=True, timeout=15_000)


def _maybe_click_generate(page) -> bool:
    gen = page.locator("button").filter(has_text=re.compile(r"^Generate$", re.I))
    if not gen.count():
        gen = page.get_by_text("Generate", exact=False)
    if not gen.count():
        return False
    gen.first.click(force=True, timeout=15_000)
    return True


def wait_for_project_ready(
    page,
    *,
    timeout_sec: int = 900,
    poll_sec: float = 8.0,
    auto_generate: bool = False,
) -> ProjectState:
    deadline = time.time() + timeout_sec
    clicked_generate = False
    first_pass = True
    while time.time() < deadline:
        if not first_pass:
            try:
                page.reload(wait_until="networkidle", timeout=120_000)
            except Exception:
                pass
            time.sleep(2)
        first_pass = False

        body = page.inner_text("body") or ""
        state = detect_project_state(body, page.url)
        if state == ProjectState.LOGIN_REQUIRED:
            return state
        if state == ProjectState.READY:
            return state
        if state == ProjectState.GENERATE_PENDING and auto_generate and not clicked_generate:
            if _maybe_click_generate(page):
                clicked_generate = True
                time.sleep(10)
                continue
        if state in (ProjectState.GENERATING, ProjectState.GENERATE_PENDING, ProjectState.UNKNOWN):
            time.sleep(poll_sec)
            continue
        time.sleep(poll_sec)
    return detect_project_state(page.inner_text("body") or "", page.url)


def _save_playwright_download(download, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    download.save_as(dest)
    return dest.stat().st_size


def _download_url_with_context(context, url: str, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = context.request.get(url, timeout=300_000)
    if not resp.ok:
        raise RuntimeError(f"HTTP {resp.status} fetching {url[:120]}")
    dest.write_bytes(resp.body())
    return dest.stat().st_size


def _collect_video_urls(page, captured: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for url in captured:
        if url in seen or not _looks_like_video_url(url):
            continue
        seen.add(url)
        ordered.append(url)
    try:
        dom_srcs: list[str] = page.evaluate(
            """() => {
              const out = [];
              document.querySelectorAll('video, source, a[href]').forEach(el => {
                const u = el.src || el.href || el.currentSrc || '';
                if (u) out.push(u);
              });
              return out;
            }"""
        )
        for url in dom_srcs:
            if url not in seen and _looks_like_video_url(url):
                seen.add(url)
                ordered.append(url)
    except Exception:
        pass
    return ordered


def download_from_project_url(
    project_url: str,
    dest: Path,
    *,
    wait_ready_sec: int = 900,
    auto_generate: bool = False,
    resolution: str = "480p",
    watermarks: str = "stock",
    headless: bool | None = None,
    open_browser: bool = False,
) -> DownloadResult:
    """
    Open an InVideo project in the saved browser profile, export MP4, save to dest.
    Requires prior login via handoff_cli.
    """
    from playwright.sync_api import TimeoutError as PlaywrightTimeout
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    project_url = project_url.strip()
    dest = dest.expanduser().resolve()
    captured_urls: list[str] = []

    use_headless = settings.browser_headless if headless is None else headless
    if open_browser:
        use_headless = False

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=use_headless)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()

            def on_response(resp) -> None:
                try:
                    url = resp.url
                    ct = (resp.headers.get("content-type") or "").lower()
                    if _looks_like_video_url(url) or "video/mp4" in ct:
                        captured_urls.append(url)
                except Exception:
                    pass

            page.on("response", on_response)
            page.goto(project_url, wait_until="networkidle", timeout=120_000)
            time.sleep(3)

            state = wait_for_project_ready(
                page,
                timeout_sec=wait_ready_sec,
                auto_generate=auto_generate,
            )
            if state == ProjectState.LOGIN_REQUIRED:
                return DownloadResult(
                    ok=False,
                    dest=None,
                    project_url=project_url,
                    message="Not logged into InVideo — run: python3 -m shorts_bot.invideo.handoff_cli",
                    state=state,
                )
            if state != ProjectState.READY:
                return DownloadResult(
                    ok=False,
                    dest=None,
                    project_url=project_url,
                    message=(
                        f"Video not ready yet (state={state.value}). "
                        "Wait for Generate to finish in InVideo, then retry."
                    ),
                    state=state,
                )

            _open_download_modal(page)
            _configure_download_options(page, resolution=resolution, watermarks=watermarks)

            try:
                with page.expect_download(timeout=180_000) as dl_info:
                    _click_modal_download(page)
                size = _save_playwright_download(dl_info.value, dest)
                return DownloadResult(
                    ok=True,
                    dest=dest,
                    project_url=project_url,
                    message=f"Downloaded {size:,} bytes",
                    state=ProjectState.READY,
                    bytes_written=size,
                )
            except PlaywrightTimeout:
                pass

            # Export may return a CDN URL instead of a browser download event.
            for _ in range(30):
                time.sleep(4)
                for url in _collect_video_urls(page, captured_urls):
                    try:
                        size = _download_url_with_context(ctx, url, dest)
                        if size > 50_000:
                            return DownloadResult(
                                ok=True,
                                dest=dest,
                                project_url=project_url,
                                message=f"Fetched export URL ({size:,} bytes)",
                                state=ProjectState.READY,
                                bytes_written=size,
                            )
                    except Exception:
                        continue

            body = page.inner_text("body") or ""
            if "upgrade" in body.lower() and "paid plan" in body.lower():
                hint = "InVideo may require a paid plan for this export setting — try 480p + Stock Watermarks."
            else:
                hint = "Export started but file not captured — retry or open Desktop browser."
            return DownloadResult(
                ok=False,
                dest=None,
                project_url=project_url,
                message=hint,
                state=ProjectState.READY,
            )
        finally:
            ctx.close()


def download_for_draft(
    draft_id: int,
    *,
    project_url: str | None = None,
    dest_name: str = "final_short.mp4",
    import_to_pack: bool = True,
    **kwargs: Any,
) -> DownloadResult:
    url = read_project_url(draft_id=draft_id, project_url=project_url)
    pack = draft_pack_dir(draft_id)
    dest = pack / dest_name
    result = download_from_project_url(url, dest, **kwargs)
    if result.ok and import_to_pack and result.dest:
        import_mp4(draft_id, result.dest)
        result.dest = pack / "final_short.mp4"
        result.message = f"{result.message} → {result.dest}"
    return result


def download_latest_run(
    run_dir: Path | str,
    *,
    dest_name: str = "final_short.mp4",
    **kwargs: Any,
) -> DownloadResult:
    run = Path(run_dir)
    url = read_project_url(run_dir=run)
    dest = run / dest_name
    return download_from_project_url(url, dest, **kwargs)
