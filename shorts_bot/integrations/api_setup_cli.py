"""One-shot API setup — Facebook Page + Meta token + probe all integrations."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.table import Table

console = Console()


def run_api_setup(*, create_page: bool = True, scrape_meta: bool = True) -> list[str]:
    lines: list[str] = []

    if create_page:
        from shorts_bot.integrations.facebook_page_create import create_peripheral_page
        from shorts_bot.integrations.facebook_credentials import save_facebook_api_file

        pages, msg = create_peripheral_page()
        lines.append(f"Facebook Page: {msg}")
        for p in pages:
            lines.append(f"  • {p.name} (id={p.page_id})")
            save_facebook_api_file(page_id=p.page_id, page_name=p.name)

    if scrape_meta:
        try:
            from shorts_bot.integrations.meta_app_create import setup_meta_app_and_token

            lines.append(setup_meta_app_and_token())
        except Exception as exc:
            lines.append(f"Meta app + token: {exc}")
            try:
                from shorts_bot.integrations.meta_token_scrape import setup_meta_page_api

                lines.append(setup_meta_page_api())
            except Exception as exc2:
                lines.append(f"Meta token fallback: {exc2}")

    if create_page or scrape_meta:
        try:
            from pathlib import Path

            from shorts_bot.integrations.facebook_page_polish import polish_facebook_page

            pack = Path("data/production/draft_5")
            for msg in polish_facebook_page(pack_dir=pack):
                lines.append(f"Page polish: {msg}")
        except Exception as exc:
            lines.append(f"Page polish: {exc}")

    from shorts_bot.integrations.meta_token_scrape import probe_saved_credentials

    ok, detail = probe_saved_credentials()
    lines.append(f"Facebook API probe: {'OK' if ok else 'FIX'} — {detail}")

    if ok:
        try:
            from shorts_bot.integrations.facebook_analytics import probe_facebook_analytics

            a_ok, a_msg = probe_facebook_analytics()
            lines.append(f"Facebook analytics: {'OK' if a_ok else '—'} {a_msg}")
        except Exception as exc:
            lines.append(f"Facebook analytics: {exc}")

    return lines


def print_api_matrix() -> None:
    from shorts_bot.cloud_secrets import cloud_secret_lists
    from shorts_bot.integrations.facebook_credentials import resolve_facebook_credentials
    from shorts_bot.integrations.facebook_reel_api import probe_facebook_reel_api
    from shorts_bot.youtube.google_auth import upload_ready

    table = Table(title="API setup status")
    table.add_column("API")
    table.add_column("Ready")
    table.add_column("Detail")

    lists = cloud_secret_lists()
    fb_pid, fb_token, fb_src = resolve_facebook_credentials()
    fb_ok = False
    fb_detail = "not configured"
    if fb_pid and fb_token:
        fb_ok, fb_detail = probe_facebook_reel_api(page_id=fb_pid, access_token=fb_token)
        fb_detail = f"{fb_detail} ({fb_src})"

    table.add_row("YouTube upload", "✓" if upload_ready() else "—", "Graph API")
    table.add_row("Facebook Reels", "✓" if fb_ok else "—", fb_detail)
    table.add_row(
        "FACEBOOK_PAGE_ID in Cursor",
        "✓" if "FACEBOOK_PAGE_ID" in lists.get("injected", set()) else "—",
        "add to Cloud Agent Secrets",
    )
    table.add_row(
        "META_PAGE_ACCESS_TOKEN in Cursor",
        "✓" if "META_PAGE_ACCESS_TOKEN" in lists.get("injected", set()) else "—",
        "add to Cloud Agent Secrets",
    )
    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(description="Set up Facebook/Meta APIs for closed loop")
    parser.add_argument("--status", action="store_true", help="Show API matrix only")
    parser.add_argument("--skip-page", action="store_true", help="Skip Page creation")
    parser.add_argument("--skip-meta", action="store_true", help="Skip Meta token scrape")
    args = parser.parse_args()

    if args.status:
        print_api_matrix()
        raise SystemExit(0)

    console.print("[bold]API setup — Facebook Page + Meta Graph token[/bold]\n")
    for line in run_api_setup(create_page=not args.skip_page, scrape_meta=not args.skip_meta):
        console.print(line)
    console.print("")
    print_api_matrix()


if __name__ == "__main__":
    main()
