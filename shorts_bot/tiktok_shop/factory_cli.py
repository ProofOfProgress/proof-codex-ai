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

    qc = sub.add_parser("qc", help="Module 1 mandatory QC (run before upload)")
    qc.add_argument("--video", required=True)
    qc.add_argument("--product", default="")
    qc.add_argument("--caption", default="")
    qc.add_argument("--account", default="")

    prep = sub.add_parser("prep-images", help="Download product cover images from scout list")
    prep.add_argument("--force", action="store_true")

    render = sub.add_parser("render", help="Kling image→video for a scouted product")
    render.add_argument("--product-id", default="")
    render.add_argument("--product", default="", help="Product name substring")
    render.add_argument("--no-loop", action="store_true")
    render.add_argument("--force", action="store_true", help="Ignore cached MP4s")
    render.add_argument("--on-screen-caption", default="", help="Module 6 burn-in hook text")
    render.add_argument("--printify-id", default="")
    render.add_argument("--printify-title", default="")
    render.add_argument("--prompt", default="", help="Override Kling prompt")
    render.add_argument(
        "--style",
        default="auto",
        choices=["auto", "studio", "vanity", "lifestyle", "minimal"],
        help="Background look (auto picks from product name)",
    )

    pipe = sub.add_parser("make-clip", help="Render + loop + enqueue one product")
    pipe.add_argument("--product-id", default="")
    pipe.add_argument("--product", default="")
    pipe.add_argument("--printify-id", default="", help="Printify product id (your listing)")
    pipe.add_argument("--printify-title", default="", help="Printify product title substring")
    pipe.add_argument("--style", default="auto", choices=["auto", "studio", "vanity", "lifestyle", "minimal"])
    pipe.add_argument("--confirm-post", action="store_true", help="Also post if queue runs")

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

    burn = sub.add_parser("burn-caption", help="Module 6 on-screen caption burn-in")
    burn.add_argument("--video", required=True, help="Input MP4 (usually loop clip)")
    burn.add_argument("--out", required=True, help="Output MP4 with burned caption")
    burn.add_argument("--caption", required=True, help="Pain-point hook text")

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

        table = Table(title="TikTok Shop factory (seller + clip pipeline)")
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
        from shorts_bot.tiktok_shop import echotik_client, kling_client

        if echotik_client.configured():
            console.print("[green]EchoTik: configured[/green]")
        else:
            console.print("[red]EchoTik: not configured[/red]")
        if kling_client.configured():
            console.print("[green]Kling: configured[/green]")
        else:
            console.print("[red]Kling: not configured[/red]")
        from shorts_bot.tiktok_shop import printify_client

        if printify_client.configured():
            console.print("[green]Printify: configured[/green]")
        else:
            console.print("[red]Printify: not configured[/red] — docs/FOR_OWNER_PRINTIFY_API.md")
        return

    if args.cmd == "rules":
        from shorts_bot.tiktok_shop import kalodata_rules as rules

        for preset in (rules.PRESET_200_METHOD, rules.PRESET_MIDDLE_CORE):
            console.print(Panel(json.dumps(preset.__dict__, indent=2), title=preset.name))
        console.print("Product checks:")
        for line in rules.PRODUCT_CHECKS:
            console.print(f"  • {line}")
        return

    if args.cmd == "qc":
        from pathlib import Path

        from shorts_bot.tiktok_shop.module1_qc import run_module1_qc

        report = run_module1_qc(
            Path(args.video),
            caption=args.caption,
            product=args.product,
            account_id=args.account,
        )
        console.print(report.summary())
        if report.violations:
            for v in report.violations:
                console.print(f"[red]• {v}[/red]")
        if report.warnings:
            for w in report.warnings:
                console.print(f"[yellow]• {w}[/yellow]")
        raise SystemExit(0 if report.passed else 1)

    if args.cmd == "prep-images":
        from shorts_bot.tiktok_shop.product_images import download_for_products
        from shorts_bot.tiktok_shop.product_scout import (
            enrich_cover_urls,
            load_products,
            save_product_dicts,
            save_products,
            scout_products,
        )

        rows = load_products()
        if not rows or args.force:
            console.print("[cyan]Running scout to refresh products…[/cyan]")
            products = scout_products(limit=10)
            save_products(products)
            rows = [p.to_dict() for p in products]
        else:
            rows = enrich_cover_urls(rows)
            save_product_dicts(rows)
        paths = download_for_products(rows, force=args.force)
        with_url = sum(1 for r in rows if r.get("cover_url"))
        console.print(f"[green]{with_url}[/green] products have cover URLs")
        console.print(f"[green]Downloaded {len(paths)}[/green] local images → data/tiktok_shop/images/")
        return

    if args.cmd == "render":
        from shorts_bot.tiktok_shop.render import render_product_clip

        try:
            result = render_product_clip(
                product_id=args.product_id,
                product_name=args.product,
                printify_id=args.printify_id,
                printify_title=args.printify_title,
                prompt=args.prompt,
                style=args.style,
                loop=not args.no_loop,
                on_screen_caption=args.on_screen_caption,
                skip_if_exists=not args.force,
            )
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc
        console.print(f"[green]Raw:[/green] {result.raw_mp4}")
        if result.loop_mp4:
            console.print(f"[green]Final:[/green] {result.loop_mp4}")
        console.print(f"Task: {result.task_id}")
        return

    if args.cmd == "burn-caption":
        from pathlib import Path

        from shorts_bot.tiktok_shop.video_editor import burn_on_screen_caption

        out = burn_on_screen_caption(Path(args.video), Path(args.out), args.caption)
        console.print(f"[green]Wrote[/green] {out}")
        return

    if args.cmd == "make-clip":
        from shorts_bot.tiktok_shop.captions import caption_variants, sanitize_caption
        from shorts_bot.tiktok_shop.queue import enqueue_video
        from shorts_bot.tiktok_shop.render import render_product_clip

        name = args.product or args.product_id or "product"
        cap = sanitize_caption(caption_variants(name, limit=1)[0])
        try:
            result = render_product_clip(
                product_id=args.product_id,
                product_name=args.product,
                printify_id=args.printify_id,
                printify_title=args.printify_title,
                style=args.style,
                on_screen_caption=cap,
            )
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc
        name = result.product_name or name
        video = result.loop_mp4 or result.raw_mp4
        idx = enqueue_video(video_path=str(video), product=name, caption=cap)
        console.print(f"[green]Queued[/green] #{idx} → {video}")
        if args.confirm_post:
            console.print("[dim]Run: factory_cli post --confirm[/dim]")
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

            from shorts_bot.tiktok_shop.module1_qc import run_module1_qc

            qc = run_module1_qc(
                video,
                caption=caption,
                product=product,
                account_id=account.id,
            )
            console.print(qc.summary())
            if not qc.passed:
                console.print("[red]Upload blocked — fix violations and regenerate video[/red]")
                if qc.violations:
                    for v in qc.violations:
                        console.print(f"  • {v}")
                break

            if not args.confirm:
                console.print("[yellow]Dry run — Module 1 QC passed; add --confirm to upload[/yellow]")
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
