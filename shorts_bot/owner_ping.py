"""Ping owner when agent needs human help — email or Slack."""

from __future__ import annotations

import argparse
import os
import sys


def ping_owner(message: str, *, subject: str = "Agent needs you") -> int:
    """Try Slack email first, then Gmail to AGENT_EMAIL."""
    from shorts_bot.config import settings

    body = message.strip()
    if not body:
        print("Empty message", file=sys.stderr)
        return 2

    # Slack channel email (recommended in docs/FOR_OWNER_SLACK_EMAIL.md)
    try:
        from shorts_bot.integrations.slack_email import has_slack_email, post_slack_via_email

        if has_slack_email():
            post_slack_via_email(body, event=subject)
            print("Sent via Slack email")
            return 0
    except Exception as exc:
        print(f"Slack email skip: {exc}", file=sys.stderr)

    # Fallback: Gmail to owner/agent inbox
    agent = (os.environ.get("AGENT_EMAIL") or settings.gmail_smtp_user or "").strip()
    if not agent:
        cred = settings.data_dir / "agent_credentials.env"
        if cred.is_file():
            for line in cred.read_text(encoding="utf-8").splitlines():
                if line.startswith("AGENT_EMAIL="):
                    agent = line.split("=", 1)[1].strip().strip('"')
                    break

    try:
        from shorts_bot.integrations.gmail_send import has_gmail_smtp, send_gmail_email

        if has_gmail_smtp() and agent:
            send_gmail_email(to=agent, subject=f"[Proof Codex] {subject}", body=body)
            print(f"Sent email to {agent}")
            return 0
    except Exception as exc:
        print(f"Gmail skip: {exc}", file=sys.stderr)

    print(
        "Could not ping — set SLACK_CHANNEL_EMAIL + Gmail SMTP or GMAIL_* in secrets",
        file=sys.stderr,
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ping owner when agent is blocked")
    parser.add_argument("message", help="Plain-English what you need")
    parser.add_argument("--subject", default="Agent needs you")
    args = parser.parse_args(argv)
    return ping_owner(args.message, subject=args.subject)


if __name__ == "__main__":
    raise SystemExit(main())
