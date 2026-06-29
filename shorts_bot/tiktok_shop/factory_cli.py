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
    render.add_argument("--image", default="", help="Module 4 Gemini sample (default: samples/PRODUCT_916.jpg)")
    render.add_argument("--listing-image", default="", help="Original listing photo (reference for scale validate)")
    render.add_argument("--reference-image", default="", help="Alias for --listing-image")
    render.add_argument("--prompt", default="", help="Kling prompt from product-video-prompt-builder")
    render.add_argument("--prompt-file", default="", help="Saved prompt path (prompts/PRODUCT.kling.txt)")
    render.add_argument(
        "--allow-default-prompt",
        action="store_true",
        help="Emergency/tests only — skip prompt-builder requirement",
    )
    render.add_argument(
        "--style",
        default="auto",
        choices=["auto", "studio", "vanity", "lifestyle", "kitchen", "minimal"],
        help="Fallback background if --allow-default-prompt (minimal maps to kitchen)",
    )

    dispatch = sub.add_parser(
        "prompt-dispatch",
        help="Print dispatch brief for product-video-prompt-builder (attach images)",
    )
    dispatch.add_argument("--product", required=True)
    dispatch.add_argument("--product-image", required=True)
    dispatch.add_argument("--reference-image", default="")
    dispatch.add_argument("--mission", default="")
    dispatch.add_argument("--handoff", default="")

    save_p = sub.add_parser("save-prompt", help="Save prompt-builder output to prompts/PRODUCT.kling.txt")
    save_p.add_argument("--product", required=True)
    save_p.add_argument("--prompt", default="")
    save_p.add_argument("--prompt-file", default="")

    checklist = sub.add_parser("pipeline-checklist", help="Required subagent steps for one clip")
    checklist.add_argument("--product", default="")
    checklist.add_argument("--mission", default="")

    sample = sub.add_parser(
        "sample-image",
        help="Module 4: Gemini converts listing photo → full-bleed 9:16 sample for Kling",
    )
    sample.add_argument("--product", required=True)
    sample.add_argument("--source", required=True, help="Listing/isolated product photo")
    sample.add_argument("--reference", default="", help="Optional in-context reference for scale")
    sample.add_argument("--style", default="auto", choices=["auto", "studio", "vanity", "lifestyle", "kitchen"])
    sample.add_argument("--out", default="")
    sample.add_argument("--force", action="store_true")

    pipe = sub.add_parser("make-clip", help="Render + loop + enqueue one product")
    pipe.add_argument("--product-id", default="")
    pipe.add_argument("--product", default="")
    pipe.add_argument("--image", default="", help="Local Module 4 product image (dry run without scout)")
    pipe.add_argument("--reference-image", default="")
    pipe.add_argument("--prompt", default="")
    pipe.add_argument("--prompt-file", default="")
    pipe.add_argument("--allow-default-prompt", action="store_true")
    pipe.add_argument("--printify-id", default="", help="Printify product id (your listing)")
    pipe.add_argument("--printify-title", default="", help="Printify product title substring")
    pipe.add_argument("--style", default="auto", choices=["auto", "studio", "vanity", "lifestyle", "kitchen", "minimal"])
    pipe.add_argument("--confirm-post", action="store_true", help="Also post if queue runs")

    enqueue = sub.add_parser("enqueue", help="Add rendered MP4 to post queue")
    enqueue.add_argument("--video", required=True)
    enqueue.add_argument("--product", required=True)
    enqueue.add_argument("--caption", default="")
    enqueue.add_argument("--account", default="", help="Optional fixed account id")

    captions = sub.add_parser("captions", help="Generate caption variants for a product")
    captions.add_argument("--product", required=True)
    captions.add_argument("--limit", type=int, default=10)

    hook = sub.add_parser("hook-lines", help="Wrap on-screen hook at 20 chars/line (TikTok native)")
    hook.add_argument("--product", default="")
    hook.add_argument("--text", default="", help="Override hook text (else template for --product)")
    hook.add_argument("--max-chars", type=int, default=0, help="Per-line limit (default 20 from config)")

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

    sched = sub.add_parser(
        "scheduler",
        help="Cron-friendly auto-poster (always-on machine — not Cursor automations)",
    )
    sched_sub = sched.add_subparsers(dest="sched_cmd", required=True)
    sched_tick = sched_sub.add_parser("tick", help="Post next queued clip if spacing allows")
    sched_tick.add_argument("--account", default="affiliate_main")
    sched_tick.add_argument("--confirm", action="store_true", help="Actually upload via Zernio")
    sched_sub.add_parser("status", help="Queue, quota, spacing — no upload").add_argument(
        "--account", default="affiliate_main"
    )

    bubble = sub.add_parser("bubble-slides", help="Module 2 — 2 bubble-wrap carousel slides (+ preview MP4)")
    bubble.add_argument("--subject", default="frog", help="Wrapped subject (frog, duck, cake, etc.)")
    bubble.add_argument("--hook", default="", help="Slide 1 hook text (default: SUBJECT BUBBLE WRAP ASMR >>>)")
    bubble.add_argument("--account", default="", help="Output subfolder / account slug")
    bubble.add_argument("--no-preview", action="store_true", help="Skip preview MP4 (slides only)")
    bubble.add_argument("--force", action="store_true")

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
        from shorts_bot.tiktok_shop import fastmoss_client, kling_client

        if fastmoss_client.configured():
            console.print("[green]FastMoss: credentials configured[/green]")
            console.print("[dim]Launch path A: pick products in FastMoss app until API scout ships[/dim]")
        else:
            console.print("[yellow]FastMoss: not configured — subscribe + optional API secrets[/yellow]")
            console.print("[dim]See docs/FOR_OWNER_FASTMOSS_SETUP.md (replaces EchoTik)[/dim]")
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

    if args.cmd == "sample-image":
        from pathlib import Path

        from shorts_bot.tiktok_shop.module4_sample import generate_module4_sample

        ref = Path(args.reference) if args.reference else None
        out = Path(args.out) if args.out else None
        try:
            result = generate_module4_sample(
                product_name=args.product,
                source_image=Path(args.source),
                reference_image=ref,
                style=args.style,
                out_path=out,
                force=args.force,
            )
        except (RuntimeError, FileNotFoundError) as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc
        console.print(f"[green]Sample[/green] {result.sample_path} ({result.width}x{result.height})")
        console.print(f"[dim]Model: {result.model}[/dim]")
        console.print(
            f"[dim]Next: render --product \"{args.product}\" "
            f"--image {result.sample_path} --prompt-file ...[/dim]"
        )
        return

    if args.cmd == "pipeline-checklist":
        from shorts_bot.tiktok_shop.pipeline import checklist_text

        console.print(checklist_text(product=args.product, mission_id=args.mission))
        return

    if args.cmd == "prompt-dispatch":
        from pathlib import Path

        from shorts_bot.tiktok_shop.pipeline import dispatch_brief

        handoff = args.handoff.strip()
        if handoff and Path(handoff).is_file():
            handoff = Path(handoff).read_text(encoding="utf-8")
        ref = Path(args.reference_image) if args.reference_image else None
        console.print(
            dispatch_brief(
                product_name=args.product,
                product_image=Path(args.product_image),
                reference_image=ref,
                mission_id=args.mission,
                visual_handoff=handoff,
            )
        )
        return

    if args.cmd == "save-prompt":
        from pathlib import Path

        from shorts_bot.tiktok_shop.pipeline import save_prompt_file

        prompt = (args.prompt or "").strip()
        if args.prompt_file:
            prompt = Path(args.prompt_file).read_text(encoding="utf-8").strip()
        if not prompt:
            console.print("[red]Provide --prompt or --prompt-file[/red]")
            raise SystemExit(1)
        path = save_prompt_file(product_name=args.product, prompt=prompt)
        console.print(f"[green]Saved[/green] {path}")
        return

    if args.cmd == "render":
        from pathlib import Path

        from shorts_bot.tiktok_shop.render import render_product_clip

        try:
            listing = args.listing_image or args.reference_image
            result = render_product_clip(
                product_id=args.product_id,
                product_name=args.product,
                printify_id=args.printify_id,
                printify_title=args.printify_title,
                image_path=Path(args.image) if args.image else None,
                listing_image=Path(listing) if listing else None,
                reference_image=Path(listing) if listing else None,
                prompt=args.prompt,
                prompt_file=Path(args.prompt_file) if args.prompt_file else None,
                style=args.style,
                loop=not args.no_loop,
                on_screen_caption=args.on_screen_caption,
                skip_if_exists=not args.force,
                allow_default_prompt=args.allow_default_prompt,
            )
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc
        console.print(f"[green]Raw:[/green] {result.raw_mp4}")
        if result.loop_mp4:
            console.print(f"[green]Final:[/green] {result.loop_mp4}")
        console.print(f"Task: {result.task_id}")
        if result.prompt_used:
            console.print(f"[dim]Prompt chars: {len(result.prompt_used)}[/dim]")
        return

    if args.cmd == "burn-caption":
        from pathlib import Path

        from shorts_bot.tiktok_shop.video_editor import burn_on_screen_caption

        out = burn_on_screen_caption(Path(args.video), Path(args.out), args.caption)
        console.print(f"[green]Wrote[/green] {out}")
        return

    if args.cmd == "make-clip":
        from pathlib import Path

        from shorts_bot.tiktok_shop.captions import on_screen_caption, sanitize_caption
        from shorts_bot.tiktok_shop.queue import enqueue_video
        from shorts_bot.tiktok_shop.render import render_product_clip

        name = args.product or args.product_id or "product"
        hook = sanitize_caption(on_screen_caption(name))
        try:
            result = render_product_clip(
                product_id=args.product_id,
                product_name=args.product,
                printify_id=args.printify_id,
                printify_title=args.printify_title,
                image_path=Path(args.image) if args.image else None,
                reference_image=Path(args.reference_image) if args.reference_image else None,
                prompt=args.prompt,
                prompt_file=Path(args.prompt_file) if args.prompt_file else None,
                style=args.style,
                allow_default_prompt=args.allow_default_prompt,
                on_screen_caption=hook,
            )
        except RuntimeError as exc:
            console.print(f"[red]{exc}[/red]")
            raise SystemExit(1) from exc
        name = result.product_name or name
        video = result.loop_mp4 or result.raw_mp4
        idx = enqueue_video(video_path=str(video), product=name, caption=hook)
        console.print(f"[green]Queued[/green] #{idx} → {video}")
        if args.confirm_post:
            console.print("[dim]Run: factory_cli post --confirm[/dim]")
        return

    if args.cmd == "hook-lines":
        from shorts_bot.tiktok_shop.captions import (
            on_screen_caption,
            validate_hook_lines,
            wrap_hook_lines,
        )

        text = (args.text or "").strip() or (
            on_screen_caption(args.product) if args.product else ""
        )
        if not text:
            console.print("[red]Provide --product or --text[/red]")
            raise SystemExit(1)
        kw: dict = {}
        if args.max_chars > 0:
            kw["max_chars_per_line"] = args.max_chars
        lines = wrap_hook_lines(text, **kw)
        over = validate_hook_lines(lines, max_chars=kw.get("max_chars_per_line"))
        for i, line in enumerate(lines, 1):
            console.print(f"[cyan]{i:2d}[/cyan] ({len(line):2d}) {line}")
        if over:
            console.print(f"[red]Over limit:[/red] {over}")
            raise SystemExit(1)
        console.print("[dim]Paste each line as a row in TikTok native text (max 20 chars/line)[/dim]")
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

    if args.cmd == "scheduler":
        if args.sched_cmd == "status":
            from shorts_bot.tiktok_shop.scheduler import scheduler_status

            info = scheduler_status(account_id=args.account)
            console.print(json.dumps(info, indent=2))
            if info.get("queue_pending"):
                console.print(f"[green]Queue:[/green] {info['queue_pending']} pending")
            if info.get("seconds_until_next"):
                console.print(f"[yellow]Spacing:[/yellow] wait {info['seconds_until_next']}s")
            return

        from shorts_bot.tiktok_shop.scheduler import tick_post

        result = tick_post(account_id=args.account, confirm=args.confirm)
        color = "green" if result.ok and result.action in ("posted", "skipped", "dry_run") else "red"
        console.print(f"[{color}]{result.action}[/{color}]: {result.message}")
        if result.publish_id:
            console.print(f"  publish_id: {result.publish_id}")
        if result.action == "failed" or result.action == "error":
            raise SystemExit(1)
        return

    if args.cmd == "bubble-slides":
        from shorts_bot.tiktok_shop.bubble_wrap import generate_bubble_wrap_slides

        result = generate_bubble_wrap_slides(
            subject=args.subject,
            hook=args.hook,
            account=args.account,
            preview=not args.no_preview,
            force=args.force,
        )
        console.print(f"[green]Slide 1 (hook):[/green] {result.slide1}")
        console.print(f"[green]Slide 2 (CTA):[/green] {result.slide2}")
        if result.preview_mp4:
            console.print(f"[green]Preview MP4:[/green] {result.preview_mp4}")
            console.print("[yellow]Preview only — post as 2-photo carousel on TikTok, not this MP4[/yellow]")
        console.print(f"[dim]Model: {result.model} · Hook: {result.hook_text}[/dim]")
        return


if __name__ == "__main__":
    main()
