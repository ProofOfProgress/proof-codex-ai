"""CLI — draft human-sounding B2B outreach."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()


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

    args = parser.parse_args()
    from shorts_bot.b2b.outreach import draft_outreach

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
        path = Path("data/b2b/prospects.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        rows = json.loads(path.read_text()) if path.is_file() else []
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
        path.write_text(json.dumps(rows, indent=2) + "\n")
        console.print(f"[green]Saved[/green] → {path}")


if __name__ == "__main__":
    main()
