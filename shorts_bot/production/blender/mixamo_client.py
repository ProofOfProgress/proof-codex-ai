"""Mixamo browser automation — upload character, download FBX motion clips."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path

MIXAMO_URL = "https://www.mixamo.com/#/?page=1&type=Motion"

# Horror beats for draft #2 gas station / SCP creature
DEFAULT_PHASE_QUERIES: dict[str, str] = {
    "open": "zombie walk",
    "wave": "zombie idle",
    "lunge": "zombie attack",
}


@dataclass
class MixamoFetchResult:
    phase: str
    query: str
    animation_name: str
    output_path: Path


def is_logged_in(url: str, html: str) -> bool:
    if not url.startswith("https://www.mixamo.com") and not url.startswith("https://mixamo.com"):
        return False
    return ">Log in<" not in html and ">Sign up<" not in html


def wait_for_login(page, *, timeout_sec: int = 900) -> None:
    """Poll until Adobe/Mixamo session is active in saved browser profile."""
    deadline = time.time() + timeout_sec
    page.goto(MIXAMO_URL, wait_until="domcontentloaded", timeout=120_000)
    while time.time() < deadline:
        url = page.evaluate("window.location.href")
        html = page.content()
        if is_logged_in(url, html):
            return
        time.sleep(2.0)
    raise TimeoutError(
        "Mixamo login timed out. Open Desktop tab, log in at mixamo.com with Adobe, then re-run."
    )


def _click_upload_character(page) -> None:
    if "autorig-modal" not in page.content():
        page.click('button:has-text("Upload Character")', timeout=15_000)
        page.wait_for_selector('a:has-text("Select character file")', timeout=15_000)


def upload_character(page, model_path: Path) -> None:
    if not model_path.is_file():
        raise FileNotFoundError(model_path)
    _click_upload_character(page)
    with page.expect_file_chooser(timeout=15_000) as fc_info:
        page.click('a:has-text("Select character file")')
    fc_info.value.set_files(str(model_path.resolve()))
    _wait_upload_complete(page)


def _wait_upload_complete(page, *, timeout_sec: int = 600) -> None:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        html = page.content()
        if "unable to map your existing skeleton" in html.lower():
            raise RuntimeError(
                "Mixamo could not rig SCP model — try scp_096.fbx again or use a humanoid FBX."
            )
        if "Meshes without skeletons are not supported" in html:
            raise RuntimeError("Mixamo rejected model — mesh has no skeleton.")
        if "autorig-overlay" in html:
            raise RuntimeError("Mixamo wants manual marker placement — not supported for SCP.")
        if "autorig-holder" in html:
            page.click(".modal-footer button.btn-primary")
            page.wait_for_timeout(1500)
            continue
        if "Change Character" in html and "modal-title" in html:
            page.click(".modal-footer button.btn-primary")
            page.wait_for_timeout(1500)
            continue
        if "autorig-uploading" not in html and "autorig-modal" not in html:
            # Back on main UI with character loaded
            if "product-nav" in html or "type=Motion" in page.url:
                return
        time.sleep(2.0)
    raise TimeoutError("Mixamo character upload/rig timed out.")


def search_animations(page, query: str) -> None:
    q = query.replace(" ", "%20")
    url = f"https://www.mixamo.com/#/?page=1&type=Motion%2CMotionPack&query={q}"
    page.goto(url, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_load_state("networkidle")
    page.wait_for_selector(".product-animation", timeout=30_000)


def select_first_animation(page) -> str:
    name = page.evaluate(
        """() => {
        const card = document.querySelector('.product-animation');
        if (!card) return '';
        card.click();
        const p = card.querySelector('p.text-capitalize');
        return p ? p.textContent.trim() : 'animation';
    }"""
    )
    page.wait_for_timeout(2500)
    if not name:
        raise RuntimeError("No Mixamo animations found for this search.")
    return name


def download_current_animation(page, dest: Path, *, fps: int = 30) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if "asset-download-modal" not in page.content():
        page.click(".sidebar-header button.btn-primary", timeout=15_000)
        page.wait_for_selector(".asset-download-modal", timeout=15_000)
    # Format FBX, Without Skin, FPS
    page.evaluate(
        """() => {
        const selects = document.querySelectorAll('.asset-download-modal select');
        const setter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, 'value').set;
        if (selects[0]) { setter.call(selects[0], 'fbx7_2019'); selects[0].dispatchEvent(new Event('change', {bubbles:true})); }
        if (selects[1]) { setter.call(selects[1], 'false'); selects[1].dispatchEvent(new Event('change', {bubbles:true})); }
        if (selects[2]) { setter.call(selects[2], '%s'); selects[2].dispatchEvent(new Event('change', {bubbles:true})); }
    }"""
        % fps
    )
    with page.expect_download(timeout=120_000) as dl_info:
        page.click(".modal-footer button.btn-primary")
    dl_info.value.save_as(str(dest))


def fetch_draft_motions(
    *,
    draft_id: int,
    model_path: Path,
    out_dir: Path,
    phases: dict[str, str] | None = None,
    login_wait_sec: int = 0,
    headless: bool | None = None,
) -> list[MixamoFetchResult]:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context
    from shorts_bot.config import settings

    queries = phases or DEFAULT_PHASE_QUERIES
    results: list[MixamoFetchResult] = []

    with sync_playwright() as pw:
        use_headless = settings.browser_headless if headless is None else headless
        context = launch_stealth_context(pw, headless=use_headless)
        page = context.pages[0] if context.pages else context.new_page()

        if login_wait_sec > 0:
            wait_for_login(page, timeout_sec=login_wait_sec)
        else:
            page.goto(MIXAMO_URL, wait_until="domcontentloaded", timeout=120_000)
            if not is_logged_in(page.url, page.content()):
                raise RuntimeError(
                    "Not logged into Mixamo. Run: python3 -m shorts_bot.production.blender.mixamo_fetch_cli "
                    "--login-wait 900"
                )

        upload_character(page, model_path)

        for phase, query in queries.items():
            search_animations(page, query)
            anim_name = select_first_animation(page)
            dest = out_dir / f"draft_{draft_id}_{phase}.fbx"
            download_current_animation(page, dest)
            if not dest.is_file() or dest.stat().st_size < 500:
                raise RuntimeError(f"Download failed or empty: {dest}")
            results.append(
                MixamoFetchResult(
                    phase=phase,
                    query=query,
                    animation_name=anim_name,
                    output_path=dest,
                )
            )

        context.close()

    return results
