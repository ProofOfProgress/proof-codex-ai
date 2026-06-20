"""One-shot InVideo ship: Generate → wait → download MP4."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from rich.console import Console

console = Console()


def ship(
    project_url: str,
    dest: Path,
    *,
    wait_render_sec: int = 1800,
    resolution: str = "480p",
) -> Path:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context
    from shorts_bot.invideo.download import (
        _click_modal_download,
        _configure_download_options,
        _open_download_modal,
        _save_playwright_download,
    )

    dest = dest.expanduser().resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=True)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        console.print(f"[cyan]Open[/cyan] {project_url[:70]}…")
        page.goto(project_url, wait_until="networkidle", timeout=120_000)
        time.sleep(5)

        body = page.inner_text("body") or ""
        if "welcome to invideo ai" in body.lower() and "create new" not in body.lower():
            raise RuntimeError("Not logged in — run handoff_cli or paste Drive link")
        if "need more credits" in body.lower() or "plan paywall" in body.lower():
            raise RuntimeError(
                "InVideo credits exhausted on this account — Generate blocked. "
                "Open the project on your laptop (may share same account) or add credits, "
                "then paste a Google Drive link: fetch_url_cli --draft-id 6 'URL'"
            )

        # Platform: YouTube Shorts
        yt = page.get_by_text("YouTube Shorts", exact=False)
        if yt.count():
            yt.first.click(force=True)
            time.sleep(1)

        gen = page.locator("button").filter(has_text="Generate")
        if gen.count():
            console.print("[cyan]Click Generate[/cyan] (2 credits)")
            gen.first.click(force=True)
            time.sleep(5)
        elif page.get_by_text("Download", exact=True).count():
            console.print("[green]Already rendered[/green]")
        else:
            raise RuntimeError(f"No Generate/Download on page: {body[:200]}")

        deadline = time.time() + wait_render_sec
        while time.time() < deadline:
            time.sleep(15)
            try:
                page.reload(wait_until="networkidle", timeout=90_000)
            except Exception:
                pass
            time.sleep(3)
            if page.get_by_text("Download", exact=True).count():
                console.print("[green]Render ready — downloading[/green]")
                break
            pct = page.title() or ""
            console.print(f"[dim]Waiting… {pct[:40]}[/dim]")
        else:
            raise RuntimeError("Render timed out")

        _open_download_modal(page)
        _configure_download_options(page, resolution=resolution)
        with page.expect_download(timeout=180_000) as dl_info:
            _click_modal_download(page)
        size = _save_playwright_download(dl_info.value, dest)
        ctx.close()

    console.print(f"[green]Saved {size:,} bytes[/green] → {dest}")
    return dest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate + download InVideo project")
    parser.add_argument("--draft-id", type=int, default=6)
    parser.add_argument("--url", default=None)
    args = parser.parse_args()

    from shorts_bot.invideo.download import read_project_url
    from shorts_bot.invideo.script_pack import draft_pack_dir

    url = args.url or read_project_url(draft_id=args.draft_id)
    dest = draft_pack_dir(args.draft_id) / "final_short.mp4"
    ship(url, dest)
    console.print(
        f"Upload: python3 -m shorts_bot.production.upload_canonical_cli "
        f"--draft-id {args.draft_id} --video {dest}"
    )


if __name__ == "__main__":
    main()
