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

    post = sub.add_parser("post", help="Post next queued video (respects daily cap)")
    post.add_argument("--account", default="", help="Force account id")
    post.add_argument("--confirm", action="store_true", help="Actually upload")

    batch = sub.add_parser("post-batch", help="Post up to N videos across accounts")
    batch.add_argument("--max", type=int, default=1, help="Max posts this run")
    batch.add_argument("--confirm", action="store_true")

    slideshow = sub.add_parser("post-slideshow", help="Post 2-image bubble wrap carousel via Zernio")
    slideshow.add_argument("slide1", help="Hook slide image path")
    slideshow.add_argument("slide2", help="CTA slide image path")
    slideshow.add_argument("--title", required=True, help="Photo title (hook text, 90 chars)")
    slideshow.add_argument("--caption", default="", help="Caption / hashtags")
    slideshow.add_argument("--account", required=True, help="Account id from accounts.json")
    slideshow.add_argument("--private", action="store_true", help="Only me — use for test uploads")
    slideshow.add_argument("--confirm", action="store_true", help="Actually upload")

    enslide = sub.add_parser("enqueue-slideshow", help="Queue a 2-image carousel for later posting")
    enslide.add_argument("slide1")
    enslide.add_argument("slide2")
    enslide.add_argument("--title", required=True)
    enslide.add_argument("--caption", default="")
    enslide.add_argument("--account", default="")

    slidebatch = sub.add_parser("post-slideshow-batch", help="Post up to N queued carousels")
    slidebatch.add_argument("--max", type=int, default=1)
    slidebatch.add_argument("--private", action="store_true")
    slidebatch.add_argument("--confirm", action="store_true")

    sample = sub.add_parser("bubble-sample", help="Show a sample slide pair from owner catalog")
    sample.add_argument("--pair", default="frog", help="Partial match: frog, usa, bubbles, …")

    args = parser.parse_args()

    if args.cmd == "status":
        from shorts_bot.tiktok_shop.accounts import accounts_config_exists, load_accounts, total_daily_cap
        from shorts_bot.tiktok_shop.quota import status_rows
        from shorts_bot.zernio.client import credentials_configured

        if not accounts_config_exists():
            console.print(
                "[yellow]accounts.json missing[/yellow] — run: "
                "python3 -m shorts_bot.tiktok_shop.accounts_cli scaffold"
            )

        table = Table(title="TikTok Shop factory (seller + clip pipeline)")
        table.add_column("Account")
        table.add_column("Track")
        table.add_column("Sent today")
        table.add_column("Limit")
        table.add_column("Remaining")
        table.add_column("Zernio")
        table.add_column("Via")
        for row in status_rows():
            zernio_cell = "✓" if row["zernio_ok"] else "—"
            table.add_row(
                f"{row['label']} ({row['id']})",
                row.get("track", "affiliate"),
                str(row["sent_today"]),
                str(row["limit"]),
                str(row["remaining"]),
                zernio_cell,
                row["post_via"],
            )
        console.print(table)
        console.print(f"Total daily cap: [cyan]{total_daily_cap()}[/cyan] posts")
        from shorts_bot.tiktok_shop import queue as qmod

        pending_v = qmod.pending_posts(media_type="video")
        pending_c = qmod.pending_posts(media_type="carousel")
        console.print(f"Video queue: [cyan]{len(pending_v)}[/cyan] · Carousel queue: [cyan]{len(pending_c)}[/cyan]")
        if credentials_configured():
            console.print("[green]Zernio API: configured[/green]")
        else:
            console.print("[red]Zernio API: not configured[/red]")
        from shorts_bot.tiktok_shop import echotik_client, kling_client

        if echotik_client.configured():
            console.print("[green]EchoTik: configured[/green]")
        else:
            console.print("[dim]EchoTik: deferred — affiliate phase after ~1k followers[/dim]")
        if kling_client.configured():
            console.print("[green]Kling: configured[/green]")
        else:
            console.print("[dim]Kling: deferred — affiliate phase after ~1k followers[/dim]")
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
            )
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc
        console.print(f"[green]Raw:[/green] {result.raw_mp4}")
        if result.loop_mp4:
            console.print(f"[green]Loop:[/green] {result.loop_mp4}")
        console.print(f"Task: {result.task_id}")
        return

    if args.cmd == "make-clip":
        from shorts_bot.tiktok_shop.captions import caption_variants, sanitize_caption
        from shorts_bot.tiktok_shop.queue import enqueue_video
        from shorts_bot.tiktok_shop.render import render_product_clip

        try:
            result = render_product_clip(
                product_id=args.product_id,
                product_name=args.product,
                printify_id=args.printify_id,
                printify_title=args.printify_title,
                style=args.style,
            )
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc
        video = result.loop_mp4 or result.raw_mp4
        name = result.product_name or args.product or "product"
        cap = sanitize_caption(caption_variants(name, limit=1)[0])
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
                (
                    i
                    for i, r in enumerate(rows)
                    if r.get("status") == "pending" and r.get("media_type", "video") == "video"
                ),
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

    if args.cmd == "bubble-sample":
        from shorts_bot.tiktok_shop.bubble_wrap import resolve_sample_pair

        hit = resolve_sample_pair(args.pair)
        if not hit:
            console.print(f"[red]No sample pair matching {args.pair!r}[/red]")
            raise SystemExit(1)
        s1, s2, title = hit
        console.print(f"Title: [cyan]{title}[/cyan]")
        console.print(f"Slide 1: {s1} ({'OK' if s1.is_file() else 'missing'})")
        console.print(f"Slide 2: {s2} ({'OK' if s2.is_file() else 'missing'})")
        console.print(
            "[dim]Post: factory_cli post-slideshow SLIDE1 SLIDE2 --title ... --account ... --private --confirm[/dim]"
        )
        return

    if args.cmd == "enqueue-slideshow":
        from shorts_bot.tiktok_shop.bubble_wrap import default_caption
        from shorts_bot.tiktok_shop.queue import enqueue_carousel

        cap = args.caption or default_caption()
        idx = enqueue_carousel(
            slide1_path=args.slide1,
            slide2_path=args.slide2,
            title=args.title,
            caption=cap,
            account_id=args.account,
        )
        console.print(f"[green]Queued carousel[/green] index {idx}")
        return

    if args.cmd == "post-slideshow":
        from pathlib import Path

        from shorts_bot.tiktok_shop.accounts import load_accounts
        from shorts_bot.tiktok_shop.bubble_wrap import MACKENZIE_SOUND_URL, default_caption
        from shorts_bot.tiktok_shop.poster import post_carousel

        accounts = {a.id: a for a in load_accounts()}
        account = accounts.get(args.account)
        if not account:
            console.print(f"[red]Unknown account {args.account}[/red]")
            raise SystemExit(1)

        cap = args.caption or default_caption()
        console.print(Panel(
            f"{account.label}\n{args.title}\n{cap[:120]}\nPrivate: {args.private}",
            title="Bubble wrap slideshow",
        ))
        console.print(f"[dim]Add Mackenzie sound in TikTok app after upload: {MACKENZIE_SOUND_URL}[/dim]")

        if not args.confirm:
            console.print("[yellow]Dry run — add --confirm to upload[/yellow]")
            return

        ok, msg, pub = post_carousel(
            account,
            slide1=Path(args.slide1),
            slide2=Path(args.slide2),
            title=args.title,
            caption=cap,
            private=args.private,
        )
        if ok:
            console.print(f"[green]{msg}[/green] ({pub})")
        else:
            console.print(f"[red]{msg}[/red]")
            raise SystemExit(1)
        return

    if args.cmd == "post-slideshow-batch":
        from pathlib import Path

        from shorts_bot.tiktok_shop.accounts import load_accounts
        from shorts_bot.tiktok_shop.poster import post_carousel
        from shorts_bot.tiktok_shop.queue import load_queue, save_queue
        from shorts_bot.tiktok_shop.quota import pick_account_for_post, remaining_today

        max_posts = max(1, args.max)
        posted = 0
        accounts = {a.id: a for a in load_accounts()}

        for _ in range(max_posts):
            rows = load_queue()
            pending_idx = next(
                (
                    i
                    for i, r in enumerate(rows)
                    if r.get("status") == "pending" and r.get("media_type") == "carousel"
                ),
                None,
            )
            if pending_idx is None:
                console.print("[yellow]Carousel queue empty[/yellow]")
                break

            row = rows[pending_idx]
            acct_id = (row.get("account_id") or "").strip()
            if acct_id:
                account = accounts.get(acct_id)
                if not account:
                    console.print(f"[red]Unknown account {acct_id}[/red]")
                    break
            else:
                bubble_accts = [a for a in accounts.values() if a.track == "bubble"]
                account = pick_account_for_post(bubble_accts or list(accounts.values()))
            if not account:
                console.print("[red]All accounts at daily cap[/red]")
                break
            if remaining_today(account) <= 0:
                console.print(f"[red]{account.id} at cap[/red]")
                break

            s1 = Path(str(row.get("slide1_path") or ""))
            s2 = Path(str(row.get("slide2_path") or ""))
            title = str(row.get("title") or "")
            caption = str(row.get("caption") or "")
            console.print(Panel(f"{account.label}\n{title}", title="Next carousel"))

            if not args.confirm:
                console.print("[yellow]Dry run — add --confirm to upload[/yellow]")
                break

            ok, msg, pub = post_carousel(
                account,
                slide1=s1,
                slide2=s2,
                title=title,
                caption=caption,
                private=args.private,
            )
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
