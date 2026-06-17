"""Drive Mixamo browser to the handoff point — owner finishes Adobe login + confirm."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from rich.console import Console

console = Console()

HANDOFF_INSTRUCTIONS = """
═══════════════════════════════════════════════════════════════
  YOUR TURN — Mixamo handoff (about 5 minutes)
═══════════════════════════════════════════════════════════════

The browser is open on the Desktop tab. Do these steps in order:

1. LOG IN
   • If you see Adobe login → enter email + password (+ 2FA if asked)
   • Free Adobe account is fine — create one if needed

2. UPLOAD SCP (if not already uploading)
   • On Mixamo: Characters tab → Upload Character
   • Choose file: channel/assets/creatures/scp_096/scp_096.fbx
   • Wait for auto-rig → click Next through any dialogs

3. DOWNLOAD 3 ANIMATIONS (Animations tab)
   For each search, click an animation, then Download (orange button):
   • Search "zombie walk"  → download FBX, Without Skin, 30 FPS
   • Search "zombie idle"  → save as draft_2_wave.fbx idea (uncanny idle/wave)
   • Search "zombie attack" → lunge clip

   Save all three into:
   channel/assets/motion_exports/
   as draft_2_open.fbx, draft_2_wave.fbx, draft_2_lunge.fbx

4. Tell the agent: "Mixamo done" — cloud re-render starts.

OR leave browser open and run (after login):
  python3 -m shorts_bot.production.blender.mixamo_fetch_cli --draft-id 2

═══════════════════════════════════════════════════════════════
"""


def drive_to_handoff(
    *,
    model_path: Path,
    minutes: int = 20,
) -> str:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context
    from shorts_bot.config import settings
    from shorts_bot.production.blender.mixamo_client import is_logged_in

    settings.browser_screenshot_dir.mkdir(parents=True, exist_ok=True)
    shot = settings.browser_screenshot_dir / f"mixamo_handoff_{int(time.time())}.png"

    with sync_playwright() as pw:
        context = launch_stealth_context(pw, headless=False)
        page = context.pages[0] if context.pages else context.new_page()

        page.goto("https://www.mixamo.com/#/", wait_until="domcontentloaded", timeout=120_000)
        page.wait_for_timeout(2000)
        html = page.content()
        url = page.url

        if is_logged_in(url, html):
            console.print("[green]Already logged into Mixamo — opening upload.[/green]")
            page.goto(
                "https://www.mixamo.com/#/?page=1&type=Motion",
                wait_until="domcontentloaded",
                timeout=120_000,
            )
            page.wait_for_timeout(1500)
            try:
                page.click('button:has-text("Upload Character")', timeout=8000)
                page.wait_for_selector('a:has-text("Select character file")', timeout=8000)
                handoff_msg = (
                    "Logged in. Upload dialog is OPEN — click Select character file and pick:\n"
                    f"  {model_path.resolve()}\n"
                    "Then wait for rigging → Next → pick animations."
                )
            except Exception:
                handoff_msg = "Logged in. Click Upload Character and select scp_096.fbx."
        else:
            console.print("[yellow]Not logged in — clicking Log In for Adobe.[/yellow]")
            try:
                page.get_by_role("link", name="Log in").first.click(timeout=8000)
            except Exception:
                try:
                    page.get_by_role("button", name="Log In").first.click(timeout=8000)
                except Exception:
                    page.click('text=Log in', timeout=8000)
            page.wait_for_timeout(3000)
            handoff_msg = (
                "Browser is on Adobe login. Sign in with your Adobe account.\n"
                "After login you'll land on Mixamo — then Upload Character → scp_096.fbx"
            )

        page.screenshot(path=str(shot), full_page=False)
        console.print(HANDOFF_INSTRUCTIONS)
        console.print(f"[cyan]{handoff_msg}[/cyan]")
        console.print(f"Screenshot: {shot}")
        console.print(f"[bold]Browser stays open {minutes} minutes — Desktop tab.[/bold]")

        time.sleep(minutes * 60)
        context.close()

    return str(shot)


def main() -> None:
    parser = argparse.ArgumentParser(description="Mixamo browser handoff for owner")
    parser.add_argument(
        "--model",
        type=Path,
        default=Path("channel/assets/creatures/scp_096/scp_096.fbx"),
    )
    parser.add_argument("--minutes", type=int, default=20, help="Keep browser open")
    args = parser.parse_args()

    if not args.model.is_file():
        raise SystemExit(f"Model missing: {args.model}")

    drive_to_handoff(model_path=args.model, minutes=args.minutes)


if __name__ == "__main__":
    main()
