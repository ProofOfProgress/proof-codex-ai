"""CLI — generate and publish Ms. Byte Facebook status posts."""

from __future__ import annotations

import argparse
import time

from rich.console import Console
from rich.table import Table

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ms. Byte status posts (image + text + caption)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="Build status images locally")
    gen.add_argument("--limit", type=int, default=None)

    pub = sub.add_parser("publish", help="Generate + post to Facebook")
    pub.add_argument("--limit", type=int, default=3, help="How many to post (default 3)")
    pub.add_argument("--slug", default=None, help="Post one template by slug")
    pub.add_argument("--dry-run", action="store_true")

    sub.add_parser("list", help="Show templates")

    args = parser.parse_args()

    from shorts_bot.social.status_posts import STATUS_TEMPLATES, build_status_posts, post_image_to_facebook

    if args.cmd == "list":
        table = Table(title="Ms. Byte status templates")
        table.add_column("Headline")
        table.add_column("Subline")
        for _, head, subline, _ in STATUS_TEMPLATES:
            table.add_row(head, subline)
        console.print(table)
        return

    if args.cmd == "generate":
        posts = build_status_posts(limit=args.limit)
        for p in posts:
            console.print(f"[green]{p.slug}[/green] → {p.image_path}")
        return

    posts = build_status_posts(limit=None if args.slug else args.limit)
    if args.slug:
        posts = [p for p in posts if p.slug == args.slug]
        if not posts:
            raise SystemExit(f"No template matching slug {args.slug!r}")

    for p in posts:
        if args.dry_run:
            console.print(f"[dim]DRY[/dim] {p.slug} → {p.image_path}")
            console.print(f"  caption: {p.caption[:80]}…")
            continue
        try:
            result = post_image_to_facebook(p.image_path, p.caption)
            console.print(f"[green]{p.slug}[/green] → {result.get('url') or result.get('status')}")
            time.sleep(8)
        except Exception as exc:
            console.print(f"[red]{p.slug}[/red] — {exc}")


if __name__ == "__main__":
    main()
