"""Create or continue Ms. Byte in InVideo — anime cel-shaded library character."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from shorts_bot.invideo.ms_byte import MS_BYTE_CHARACTER_STYLE, ms_byte_character_brief

console = Console()

# Saved InVideo agent workspace (Ms. Byte character lock).
DEFAULT_AGENT_URL = (
    "https://ai.invideo.io/workspace/a21e54e0-865a-4ba0-9a0d-d67f33f42a1f/"
    "v45-copilot/agents-models/d55259f8-bd0b-4cc6-b6ad-982fc9743363/"
    "agent/47391091-604e-4f85-907c-37bd90b69fb7"
)

ASSET_DIR = Path("channel/brand/assets/ms_byte")
DEFAULT_REFS = (
    "reference.png",
    "pose_hook_wave.png",
    "pose_side_angle.png",
)


def _pack_dir() -> Path:
    from shorts_bot.config import settings

    out = settings.data_dir / "production" / "ms_byte"
    out.mkdir(parents=True, exist_ok=True)
    return out


def send_character_build(
    *,
    agent_url: str = DEFAULT_AGENT_URL,
    upload_refs: bool = True,
    wait_sec: int = 120,
) -> str:
    """Attach reference PNGs + send anime-style character build to InVideo Ms. Byte agent."""
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    refs = [ASSET_DIR / name for name in DEFAULT_REFS]
    missing = [p for p in refs if not p.is_file()]
    if missing and upload_refs:
        raise FileNotFoundError(f"Missing reference PNGs: {', '.join(p.name for p in missing)}")

    message = ms_byte_character_brief()

    with sync_playwright() as p:
        ctx = launch_stealth_context(p, headless=True)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(agent_url, wait_until="networkidle", timeout=120_000)
        time.sleep(4)

        if upload_refs:
            page.locator("input[type='file']").last.set_input_files([str(r.resolve()) for r in refs])
            time.sleep(4)

        chat = page.locator(".tiptap.ProseMirror").first
        chat.click(force=True)
        chat.fill(message)
        time.sleep(0.5)
        page.get_by_role("button", name="Send").click(force=True)

        deadline = time.time() + wait_sec
        body = page.inner_text("body") or ""
        while time.time() < deadline:
            time.sleep(10)
            body = page.inner_text("body") or ""
            if any(
                x in body
                for x in ("Generating", "character master sheet", "RTR_MsByte", "Working on it")
            ):
                break

        out = _pack_dir()
        (out / "invideo_character.url").write_text(agent_url + "\n", encoding="utf-8")
        (out / "invideo_character_prompt.txt").write_text(message + "\n", encoding="utf-8")
        (out / "invideo_agent_state.txt").write_text(body[-4000:], encoding="utf-8")
        ctx.close()

    return agent_url


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Ms. Byte in InVideo (anime cel-shaded, save as RTR_MsByte)"
    )
    parser.add_argument(
        "--agent-url",
        default=DEFAULT_AGENT_URL,
        help="InVideo Ms. Byte agent workspace URL",
    )
    parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Send prompt only — refs already attached in browser",
    )
    parser.add_argument("--wait", type=int, default=120, help="Seconds to wait after send")
    parser.add_argument("--print-brief", action="store_true", help="Print character brief only")
    args = parser.parse_args()

    if args.print_brief:
        console.print(ms_byte_character_brief())
        console.print(f"\n[dim]Style lock:[/dim] {MS_BYTE_CHARACTER_STYLE}")
        raise SystemExit(0)

    console.print(
        Panel(
            f"Style: {MS_BYTE_CHARACTER_STYLE}\n"
            "Uploads reference PNGs → InVideo Ms. Byte agent → saves RTR_MsByte to library.\n"
            "If InVideo asks for illustration style: anime / cel-shaded.",
            title="Ms. Byte — InVideo character",
        )
    )

    try:
        url = send_character_build(
            agent_url=args.agent_url,
            upload_refs=not args.no_upload,
            wait_sec=args.wait,
        )
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        console.print("[yellow]Login:[/yellow] python3 -m shorts_bot.invideo.handoff_cli")
        raise SystemExit(1) from exc

    console.print(f"[green]Sent to InVideo Ms. Byte agent[/green]\n{url}")
    console.print(f"[dim]State saved:[/dim] {_pack_dir()}")


if __name__ == "__main__":
    main()
