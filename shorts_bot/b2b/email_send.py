"""Send B2B outreach email via owner business SMTP (Gmail / Google Workspace)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from email.utils import formataddr
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.integrations.gmail_send import send_gmail_email


def _log_path() -> Path:
    return settings.data_dir / "b2b" / "send_log.jsonl"


def smtp_configured() -> bool:
    from shorts_bot.integrations.gmail_send import has_gmail_smtp

    return has_gmail_smtp()


def business_email_address() -> str:
    return (settings.gmail_smtp_user or settings.business_email_user or "").strip()


def from_header() -> str:
    name = (settings.b2b_email_from_name or "Kim").strip()
    addr = business_email_address()
    if not addr:
        return name
    return formataddr((name, addr))


def sends_today() -> int:
    path = _log_path()
    if not path.is_file():
        return 0
    today = datetime.now(timezone.utc).date().isoformat()
    count = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if str(row.get("at", "")).startswith(today):
            count += 1
    return count


def can_send_more() -> tuple[bool, str]:
    if not settings.b2b_email_enabled:
        return False, "B2B email disabled — set B2B_EMAIL_ENABLED=true in Secrets after setup"
    if not smtp_configured():
        return False, "Business email not configured — see docs/FOR_OWNER_B2B_EMAIL.md"
    limit = max(1, int(settings.b2b_email_daily_limit))
    sent = sends_today()
    if sent >= limit:
        return False, f"Daily limit reached ({sent}/{limit}) — try again tomorrow"
    return True, ""


def log_send(*, to: str, subject: str, company: str = "", ok: bool = True, error: str = "") -> None:
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "at": datetime.now(timezone.utc).isoformat(),
        "to": to,
        "subject": subject[:200],
        "company": company,
        "ok": ok,
        "error": error[:300],
        "from": business_email_address(),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def send_business_email(
    *,
    to: str,
    subject: str,
    body: str,
    company: str = "",
    allow_when_disabled: bool = False,
) -> tuple[bool, str]:
    """Send one B2B email from owner business address."""
    if not allow_when_disabled:
        ok, msg = can_send_more()
        if not ok:
            return False, msg
    elif not smtp_configured():
        return False, "Business email not configured — see docs/FOR_OWNER_B2B_EMAIL.md"

    recipient = to.strip()
    if "@" not in recipient:
        return False, "Invalid recipient email"

    success, err = send_gmail_email(
        to=recipient,
        subject=subject,
        body=body,
        from_addr=from_header(),
    )
    log_send(to=recipient, subject=subject, company=company, ok=success, error=err)
    return success, err or "sent"
