"""Create Recraft custom style from a folder of reference images (no Studio save needed)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from rich.console import Console

console = Console()


def _write_style_id(env_key: str, style_id: str) -> None:
    from shorts_bot.config import settings

    env_path = settings.data_dir.parent / ".env"
    if not env_path.is_file():
        env_path = Path(".env")
    text = env_path.read_text(encoding="utf-8") if env_path.is_file() else ""
    line = f"{env_key}={style_id}"
    if re.search(rf"^{re.escape(env_key)}=.*$", text, re.M):
        text = re.sub(rf"^{re.escape(env_key)}=.*$", line, text, flags=re.M)
    else:
        text = text.rstrip() + "\n" + line + "\n"
    env_path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload 1–5 reference PNG/JPG files → Recraft API style ID (no Studio save)"
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("data/recraft_refs/creepy"),
        help="Folder with up to 5 reference images",
    )
    parser.add_argument(
        "--env-key",
        default="RECRAFT_STYLE_ID_HORROR",
        help="Which .env key to write (default: horror style)",
    )
    parser.add_argument(
        "--base-style",
        default="digital_illustration",
        choices=["any", "realistic_image", "digital_illustration", "vector_illustration", "icon"],
    )
    args = parser.parse_args()

    from shorts_bot.config import settings
    from shorts_bot.production.images.recraft_style import create_recraft_style

    if not settings.has_recraft_images:
        console.print("[red]RECRAFT_API_KEY missing in .env / Cursor Secrets[/red]")
        raise SystemExit(1)

    folder = args.dir
    if not folder.is_dir():
        console.print(
            f"[red]Folder not found:[/red] {folder}\n\n"
            "Create it and add up to 5 PNG/JPG files, then re-run.\n"
            "Example: data/recraft_refs/creepy/01.png … 05.png"
        )
        raise SystemExit(1)

    exts = {".png", ".jpg", ".jpeg", ".webp"}
    refs = sorted(
        p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts
    )[:5]
    if not refs:
        console.print(f"[red]No PNG/JPG/WEBP images in {folder}[/red]")
        raise SystemExit(1)

    console.print(f"[cyan]Uploading {len(refs)} reference(s) to Recraft API…[/cyan]")
    for p in refs:
        console.print(f"  • {p.name} ({p.stat().st_size // 1024} KB)")

    style_id = create_recraft_style(
        refs,
        api_key=settings.recraft_api_key or "",
        base_style=args.base_style,
    )
    _write_style_id(args.env_key, style_id)

    console.print(f"\n[bold green]Style created via API[/bold green]")
    console.print(f"{args.env_key}={style_id}")
    console.print(
        "\nTest frame:\n"
        f"  IMAGE_PROVIDER=recraft {args.env_key}={style_id} "
        'python3 -m shorts_bot.production.image_cli --prompt "creepy crayon forest creature, wrong smile, 9:16, no text"'
    )


if __name__ == "__main__":
    main()
