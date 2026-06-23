"""CLI — draft human-sounding B2B outreach."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

PROSPECTS_PATH = Path("data/b2b/prospects.json")


def _load_prospects() -> list[dict]:
    if not PROSPECTS_PATH.is_file():
        return []
    return json.loads(PROSPECTS_PATH.read_text(encoding="utf-8"))


def _save_prospects(rows: list[dict]) -> None:
    PROSPECTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROSPECTS_PATH.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="B2B outreach drafts (humanized)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    draft = sub.add_parser("draft", help="Generate one DM or email")
    draft.add_argument("--company", required=True)
    draft.add_argument("--product", required=True)
    draft.add_argument("--detail", default="", help="Specific fact you noticed (required for human feel)")
    draft.add_argument("--sample-url", default="https://youtube.com/shorts/FRGbCIH5R1k")
    draft.add_argument("--sender", default="Kim")
    draft.add_argument("--channel", choices=("dm", "email"), default="dm")
    draft.add_argument("--json", action="store_true")

    save = sub.add_parser("save", help="Draft + append to data/b2b/prospects.json")
    save.add_argument("--company", required=True)
    save.add_argument("--product", required=True)
    save.add_argument("--detail", default="")
    save.add_argument("--channel", choices=("dm", "email"), default="dm")
    save.add_argument("--contact", default="", help="Twitter handle or email")

    sub.add_parser("status", help="Business email + daily send limit")

    test_email = sub.add_parser("test-email", help="Send a test email to yourself")
    test_email.add_argument("--to", default="", help="Recipient (default: your business email)")

    send = sub.add_parser("send", help="Send a saved email prospect (requires --confirm)")
    send.add_argument("--index", type=int, required=True, help="Row index in prospects.json (0-based)")
    send.add_argument("--confirm", action="store_true", help="Required — actually send the email")

    args = parser.parse_args()
    from shorts_bot.b2b.outreach import draft_outreach

    if args.cmd == "status":
        from shorts_bot.b2b import email_send
        from shorts_bot.config import settings

        table = Table(title="B2B business email")
        table.add_column("Setting")
        table.add_column("Value")
        addr = email_send.business_email_address() or "(not set)"
        table.add_row("From address", addr)
        table.add_row("Display name", email_send.from_header())
        table.add_row("SMTP configured", "yes" if email_send.smtp_configured() else "no")
        enabled = settings.b2b_email_enabled
        table.add_row("Sending enabled", "yes" if enabled else "no — set B2B_EMAIL_ENABLED=true")
        if email_send.smtp_configured():
            sent = email_send.sends_today()
            limit = max(1, int(settings.b2b_email_daily_limit))
            table.add_row("Sent today", f"{sent}/{limit}")
        console.print(table)
        if not email_send.smtp_configured():
            console.print("[yellow]Setup:[/yellow] docs/FOR_OWNER_B2B_EMAIL.md")
        return

    if args.cmd == "test-email":
        from shorts_bot.b2b import email_send

        to = (args.to or email_send.business_email_address()).strip()
        if "@" not in to:
            console.print("[red]No recipient — set GMAIL_SMTP_USER or pass --to[/red]")
            raise SystemExit(1)
        ok, msg = email_send.send_business_email(
            to=to,
            subject="[Rapid Tool Review] B2B email test",
            body=(
                "If you got this, business email is wired up.\n\n"
                "Next: set B2B_EMAIL_ENABLED=true in Cursor Secrets, then:\n"
                "  python3 -m shorts_bot.b2b.outreach_cli send --index N --confirm\n"
            ),
            company="(test)",
            allow_when_disabled=True,
        )
        if ok:
            console.print(f"[green]Test email sent[/green] → {to}")
        else:
            console.print(f"[red]Failed:[/red] {msg}")
            raise SystemExit(1)
        return

    if args.cmd == "send":
        from shorts_bot.b2b import email_send

        rows = _load_prospects()
        if args.index < 0 or args.index >= len(rows):
            console.print(f"[red]Invalid index {args.index} — {len(rows)} prospects saved[/red]")
            raise SystemExit(1)
        row = rows[args.index]
        if row.get("channel") != "email":
            console.print("[red]That prospect is not an email — use channel email when saving[/red]")
            raise SystemExit(1)
        contact = (row.get("contact") or "").strip()
        if "@" not in contact:
            console.print("[red]Prospect has no email in contact field[/red]")
            raise SystemExit(1)
        subject = (row.get("subject") or "").strip()
        body = (row.get("body") or "").strip()
        if not subject or not body:
            console.print("[red]Prospect missing subject or body[/red]")
            raise SystemExit(1)

        console.print(Panel(f"To: {contact}\nSubject: {subject}", title=f"Prospect #{args.index}"))
        console.print(Panel(body, title="Body"))
        if not args.confirm:
            console.print("[yellow]Dry run — add --confirm to send[/yellow]")
            return

        ok, msg = email_send.send_business_email(
            to=contact,
            subject=subject,
            body=body,
            company=str(row.get("company") or ""),
        )
        if ok:
            rows[args.index]["status"] = "sent"
            _save_prospects(rows)
            console.print(f"[green]Sent[/green] → {contact}")
        else:
            console.print(f"[red]Failed:[/red] {msg}")
            raise SystemExit(1)
        return

    if args.cmd == "draft":
        result = draft_outreach(
            company=args.company,
            product=args.product,
            detail=args.detail,
            sample_url=args.sample_url,
            sender_name=args.sender,
            channel=args.channel,
        )
        if args.json:
            console.print_json(json.dumps({
                "channel": result.channel,
                "subject": result.subject,
                "body": result.body,
                "ai_score": result.ai_score,
                "passed": result.passed,
                "issues": result.issues,
            }))
            return
        if result.subject:
            console.print(Panel(result.subject, title="Subject"))
        style = "green" if result.passed else "yellow"
        console.print(Panel(result.body, title=f"{result.channel.upper()} (AI-ish score {result.ai_score}/100)", border_style=style))
        if result.issues:
            console.print("Issues:", ", ".join(result.issues))
        console.print("[dim]Copy, tweak one word, send from YOUR account. Approve before sending.[/dim]")
        return

    if args.cmd == "save":
        result = draft_outreach(
            company=args.company,
            product=args.product,
            detail=args.detail,
            channel=args.channel,
        )
        rows = _load_prospects()
        rows.append({
            "company": args.company,
            "product": args.product,
            "contact": args.contact,
            "channel": args.channel,
            "subject": result.subject,
            "body": result.body,
            "status": "draft",
            "ai_score": result.ai_score,
        })
        _save_prospects(rows)
        console.print(f"[green]Saved[/green] → {PROSPECTS_PATH} (index {len(rows) - 1})")


if __name__ == "__main__":
    main()
