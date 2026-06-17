"""Pull reference images from open Recraft Studio tabs and create custom style."""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from rich.console import Console

console = Console()

RECRAFT_HOSTS = ("recraft.ai", "www.recraft.ai", "app.recraft.ai")


def _is_recraft_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in RECRAFT_HOSTS)


def _pick_largest_image_src(page) -> str | None:
    """Best-effort: largest visible img/canvas-backed preview in the editor."""
    return page.evaluate(
        """() => {
        const imgs = Array.from(document.querySelectorAll('img'));
        const scored = imgs
            .map((img) => {
                const r = img.getBoundingClientRect();
                const w = img.naturalWidth || r.width;
                const h = img.naturalHeight || r.height;
                const src = img.currentSrc || img.src || '';
                if (!src || src.startsWith('data:') || w < 120 || h < 120) return null;
                if (r.width < 80 || r.height < 80) return null;
                return { src, area: w * h, right: r.left };
            })
            .filter(Boolean);
        if (!scored.length) return null;
        scored.sort((a, b) => (b.right - a.right) || (b.area - a.area));
        return scored[0].src;
    }"""
    )


def harvest_recraft_tab_images(*, out_dir: Path, headless: bool = True) -> list[Path]:
    from playwright.sync_api import sync_playwright

    from shorts_bot.browser.stealth import launch_stealth_context

    out_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    with sync_playwright() as p:
        context = launch_stealth_context(p, headless=headless)
        pages = [pg for pg in context.pages if _is_recraft_url(pg.url)]
        if not pages:
            for pg in context.pages:
                pages.append(pg)
        console.print(f"[cyan]Found {len(context.pages)} browser tab(s)[/cyan]")

        for i, page in enumerate(context.pages):
            url = page.url or ""
            if not _is_recraft_url(url):
                console.print(f"[dim]Skip tab {i + 1}: {url[:80]}[/dim]")
                continue
            try:
                page.bring_to_front()
                page.wait_for_timeout(1200)
            except Exception:
                pass

            src = _pick_largest_image_src(page)
            if not src:
                shot = out_dir / f"ref_tab_{i + 1}_screenshot.png"
                page.screenshot(path=str(shot), full_page=False)
                saved.append(shot)
                console.print(f"[yellow]Tab {i + 1}: no img src — saved screenshot {shot.name}[/yellow]")
                continue

            ext = ".png"
            if ".webp" in src.split("?")[0]:
                ext = ".webp"
            elif ".jpg" in src.split("?")[0] or ".jpeg" in src.split("?")[0]:
                ext = ".jpg"
            dest = out_dir / f"ref_tab_{i + 1}{ext}"

            try:
                resp = page.request.get(src, timeout=120000)
                if not resp.ok:
                    raise RuntimeError(f"HTTP {resp.status}")
                dest.write_bytes(resp.body())
                saved.append(dest)
                console.print(f"[green]Tab {i + 1}:[/green] {dest.name} ({dest.stat().st_size // 1024} KB)")
            except Exception as exc:
                shot = out_dir / f"ref_tab_{i + 1}_screenshot.png"
                page.screenshot(path=str(shot), full_page=False)
                saved.append(shot)
                console.print(f"[yellow]Tab {i + 1}: download failed ({exc}) — screenshot fallback[/yellow]")

        if not saved and headless:
            context.close()
            return harvest_recraft_tab_images(out_dir=out_dir, headless=False)

        time.sleep(1)
        context.close()

    return saved[:5]


def _write_style_id(style_id: str) -> None:
    import re

    env_path = Path("/workspace/.env")
    text = env_path.read_text() if env_path.is_file() else ""
    line = f"RECRAFT_STYLE_ID={style_id}"
    if re.search(r"^RECRAFT_STYLE_ID=.*$", text, re.M):
        text = re.sub(r"^RECRAFT_STYLE_ID=.*$", line, text, flags=re.M)
    else:
        text = text.rstrip() + "\n" + line + "\n"
    env_path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create Recraft style from open browser tabs")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/production/recraft_style_refs"),
    )
    parser.add_argument(
        "--base-style",
        default="digital_illustration",
        choices=["any", "realistic_image", "digital_illustration", "vector_illustration", "icon"],
    )
    parser.add_argument("--visible", action="store_true", help="Use visible browser (Desktop tab)")
    parser.add_argument("--dry-run", action="store_true", help="Only harvest refs, do not create style")
    args = parser.parse_args()

    from shorts_bot.config import settings

    if not settings.has_recraft_images:
        console.print("[red]RECRAFT_API_KEY missing — add to .env or Cursor Secrets[/red]")
        raise SystemExit(1)

    refs = harvest_recraft_tab_images(out_dir=args.out_dir, headless=not args.visible)
    if not refs:
        console.print(
            "[red]No Recraft images found.[/red] Keep your 5 Recraft tabs open, then run:\n"
            "  python3 -m shorts_bot.production.recraft_style_from_browser_cli --visible"
        )
        raise SystemExit(1)

    console.print(f"\n[bold]Harvested {len(refs)} reference(s)[/bold] → {args.out_dir}")
    if args.dry_run:
        raise SystemExit(0)

    from shorts_bot.production.images.recraft_style import create_recraft_style

    style_id = create_recraft_style(
        refs,
        api_key=settings.recraft_api_key or "",
        base_style=args.base_style,
    )
    _write_style_id(style_id)
    console.print(f"\n[bold green]Style created![/bold green]")
    console.print(f"RECRAFT_STYLE_ID={style_id}")
    console.print("\nTest frame:")
    console.print(
        '  IMAGE_PROVIDER=recraft python3 -m shorts_bot.production.image_cli '
        '--prompt "funny crayon horror character in dark apartment at 3am, vertical, no text"'
    )


if __name__ == "__main__":
    main()
