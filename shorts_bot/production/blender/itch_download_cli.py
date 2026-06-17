"""Download free itch.io asset packs via saved browser profile (owner may be logged in)."""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

from rich.console import Console

console = Console()


def download_itch_asset(
    game_url: str,
    dest: Path,
    *,
    filename_hint: str | None = None,
    headless: bool = True,
    wait_seconds: int = 120,
) -> Path:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    dest.parent.mkdir(parents=True, exist_ok=True)
    purchase_url = game_url.rstrip("/") + "/purchase"
    with sync_playwright() as pw:
        ctx = launch_stealth_context(pw, headless=headless)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        console.print(f"[cyan]Opening[/cyan] {purchase_url}")
        page.goto(purchase_url, wait_until="domcontentloaded", timeout=60_000)
        time.sleep(1)

        no_thanks = page.get_by_text("No thanks", exact=False).first
        if not no_thanks.count():
            no_thanks = page.locator("a.direct_download_btn").first
        if no_thanks.count():
            no_thanks.click()
            page.wait_for_load_state("domcontentloaded", timeout=30_000)
            time.sleep(1)

        dl_btn = page.get_by_role("button", name="Download").first
        if not dl_btn.count():
            dl_btn = page.locator("a.button").filter(has_text="Download").first
        if not dl_btn.count():
            # File list with per-file download buttons
            links = page.locator("a[href*='/file/'], a.download_link, .upload_list a")
            if filename_hint and links.count():
                for i in range(links.count()):
                    txt = links.nth(i).inner_text(timeout=2000) or ""
                    href = links.nth(i).get_attribute("href") or ""
                    if filename_hint.lower() in (txt + href).lower():
                        with page.expect_download(timeout=wait_seconds * 1000) as dl_info:
                            links.nth(i).click()
                        download = dl_info.value
                        out = dest if dest.suffix else dest / download.suggested_filename
                        download.save_as(str(out))
                        console.print(f"[green]Saved[/green] {out} ({out.stat().st_size // 1024} KB)")
                        ctx.close()
                        return out
            shot = dest.parent / "itch_download_debug.png"
            page.screenshot(path=str(shot), full_page=True)
            raise RuntimeError(
                f"No Download button — screenshot saved to {shot}. "
                "Owner may need to log into itch.io in the browser profile."
            )

        with page.expect_download(timeout=wait_seconds * 1000) as dl_info:
            dl_btn.click()
        download = dl_info.value
        suggested = download.suggested_filename
        if filename_hint and filename_hint.lower() not in suggested.lower():
            console.print(f"[yellow]Warning:[/yellow] expected {filename_hint}, got {suggested}")
        out = dest if dest.suffix else dest / suggested
        download.save_as(str(out))
        console.print(f"[green]Saved[/green] {out} ({out.stat().st_size // 1024} KB)")
        ctx.close()
        return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Download itch.io asset via browser profile")
    parser.add_argument("--url", required=True, help="itch.io game page URL")
    parser.add_argument("--dest", required=True, type=Path, help="Output file or directory")
    parser.add_argument("--filename-hint", default="", help="Substring to pick the right file")
    parser.add_argument("--headed", action="store_true", help="Show browser window")
    args = parser.parse_args()
    download_itch_asset(
        args.url,
        args.dest,
        filename_hint=args.filename_hint or None,
        headless=not args.headed,
    )


if __name__ == "__main__":
    main()
