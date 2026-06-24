"""CLI — 3 accounts × 10 Shop videos/day factory."""

from __future__ import annotations

import argparse
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok Shop faceless factory")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="Accounts + posts sent today")
    sub.add_parser("rules", help="Kalodata filter presets")

    enqueue = sub.add_parser("enqueue", help="Add rendered MP4 to post queue")
    enqueue.add_argument("--video", required=True)
    enqueue.add_argument("--product", required=True)
    enqueue.add_argument("--caption", default="")
    enqueue.add_argument("--account", default="", help="Optional fixed account id")

    captions = sub.add_parser("captions", help="Generate caption variants for a product")
    captions.add_argument("--product", required=True)
    captions.add_argument("--limit", type=int, default=10)

    loop = sub.add_parser("loop-clip", help="5s forward + reverse → ~10s MP4")
    loop.add_argument("--in", dest="inp", required=True)
    loop.add_argument("--out", required=True)

    post = sub.add_parser("post", help="Post next queued video (respects daily cap)")
    post.add_argument("--account", default="", help="Force account id")
    post.add_argument("--confirm", action="store_true", help="Actually upload")

    batch = sub.add_parser("post-batch", help="Post up to N videos across accounts")
    batch.add_argument("--max", type=int, default=1, help="Max posts this run")
    batch.add_argument("--confirm", action="store_true")

    args = parser.parse_args()

    if args.cmd == "status":
        from shorts_bot.tiktok_shop.accounts import load_accounts, total_daily_cap
        from shorts_bot.tiktok_shop.quota import status_rows

        table = Table(title="TikTok Shop factory (3 × 10/day target)")
        table.add_column("Account")
        table.add_column("Sent today")
        table.add_column("Limit")
        table.add_column("Remaining")
        table.add_column("Via")
        for row in status_rows():
            table.add_row(
                f"{row['label']} ({row['id']})",
                str(row["sent_today"]),
                str(row["limit"]),
                str(row["remaining"]),
                row["post_via"],
            )
        console.print(table)
        console.print(f"Total daily cap: [cyan]{total_daily_cap()}[/cyan] videos")
        pending = __import__("shorts_bot.tiktok_shop.queue", fromlist=["pending_posts"]).pending_posts()
        console.print(f"Queue pending: [cyan]{len(pending)}[/cyan]")
        return

    if args.cmd == "rules":
        from shorts_bot.tiktok_shop import kalodata_rules as rules

        for preset in (rules.PRESET_200_METHOD, rules.PRESET_MIDDLE_CORE):
            console.print(Panel(json.dumps(preset.__dict__, indent=2), title=preset.name))
        console.print("Product checks:")
        for line in rules.PRODUCT_CHECKS:
            console.print(f"  • {line}")
        return

    if args.cmd == "captions":
        from shorts_bot.tiktok_shop.captions import caption_variants

        for i, cap in enumerate(caption_variants(args.product, limit=args.limit)):
            console.print(f"[{i}] {cap}")
        return

    if args.cmd == "loop-clip":
        from pathlib import Path

        from shorts_bot.tiktok_shop.video_variants import make_pan_loop_clip

        out = make_pan_loop_clip(Path(args.inp), Path(args.out))
        console.print(f"[green]Wrote[/green] {out}")
        return

    if args.cmd == "enqueue":
        from shorts_bot.tiktok_shop.captions import caption_variants, sanitize_caption
        from shorts_bot.tiktok_shop.queue import enqueue_video

        cap = args.caption or caption_variants(args.product, limit=1)[0]
        idx = enqueue_video(
            video_path=args.video,
            product=args.product,
            caption=sanitize_caption(cap),
            account_id=args.account,
        )
        console.print(f"[green]Queued[/green] index {idx}")
        return

    if args.cmd in ("post", "post-batch"):
        from pathlib import Path

        from shorts_bot.tiktok_shop.accounts import ShopAccount, load_accounts
        from shorts_bot.tiktok_shop.poster import post_clip
        from shorts_bot.tiktok_shop.queue import load_queue, save_queue
        from shorts_bot.tiktok_shop.quota import pick_account_for_post, remaining_today

        max_posts = 1 if args.cmd == "post" else max(1, args.max)
        posted = 0
        accounts = {a.id: a for a in load_accounts()}

        for _ in range(max_posts):
            rows = load_queue()
            pending_idx = next(
                (i for i, r in enumerate(rows) if r.get("status") == "pending"),
                None,
            )
            if pending_idx is None:
                console.print("[yellow]Queue empty[/yellow]")
                break

            row = rows[pending_idx]
            acct_id = (args.account or row.get("account_id") or "").strip()
            if acct_id:
                account = accounts.get(acct_id)
                if not account:
                    console.print(f"[red]Unknown account {acct_id}[/red]")
                    break
            else:
                account = pick_account_for_post(list(accounts.values()))
            if not account:
                console.print("[red]All accounts at daily cap (10/day each)[/red]")
                break
            if remaining_today(account) <= 0:
                console.print(f"[red]{account.id} at cap[/red]")
                break

            video = Path(str(row.get("video_path") or ""))
            caption = str(row.get("caption") or "")
            product = str(row.get("product") or "")
            console.print(Panel(f"{account.label}\n{video.name}\n{caption[:120]}", title="Next post"))

            if not args.confirm:
                console.print("[yellow]Dry run — add --confirm to upload[/yellow]")
                break

            ok, msg, pub = post_clip(account, video_path=video, caption=caption, product=product)
            if ok:
                rows[pending_idx]["status"] = "posted"
                rows[pending_idx]["account_id"] = account.id
                rows[pending_idx]["publish_id"] = pub
                save_queue(rows)
                console.print(f"[green]Posted[/green] {msg}")
                posted += 1
            else:
                console.print(f"[red]Failed:[/red] {msg}")
                break

        console.print(f"Posted this run: {posted}")
        return


if __name__ == "__main__":
    main()
