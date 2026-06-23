"""Send email via Gmail SMTP (app password) — used for Slack inbound channel email."""

from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

from shorts_bot.config import settings

log = logging.getLogger(__name__)

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def has_gmail_smtp() -> bool:
    user = (settings.gmail_smtp_user or "").strip()
    password = (settings.gmail_smtp_app_password or "").strip()
    if "@" not in user or len(password) < 8:
        return False
    lower = password.lower()
    return "your" not in lower and "placeholder" not in lower


def send_gmail_email(
    *,
    to: str,
    subject: str,
    body: str,
    from_addr: str | None = None,
) -> tuple[bool, str]:
    """Send plain-text email through Gmail SMTP."""
    user = (settings.gmail_smtp_user or "").strip()
    password = (settings.gmail_smtp_app_password or "").strip()
    recipient = (to or "").strip()
    if not has_gmail_smtp():
        return False, "GMAIL_SMTP_USER + GMAIL_SMTP_APP_PASSWORD required"
    if "@" not in recipient:
        return False, "Invalid recipient address"

    sender = (from_addr or user).strip()
    # formataddr returns "Name <email>" — plain email also works for SMTP
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject[:200]
    msg["From"] = sender
    msg["To"] = recipient

    host = (getattr(settings, "smtp_host", None) or GMAIL_SMTP_HOST).strip()
    port = int(getattr(settings, "smtp_port", None) or GMAIL_SMTP_PORT)
    try:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
            smtp.sendmail(sender, [recipient], msg.as_string())
        log.info("Gmail sent → %s (%s)", recipient, subject[:60])
        return True, ""
    except smtplib.SMTPAuthenticationError:
        log.warning("Gmail SMTP auth failed — check app password")
        return False, "Gmail auth failed — use a Google App Password, not your login password"
    except Exception as exc:  # noqa: BLE001
        log.warning("Gmail send failed: %s", exc)
        return False, str(exc)
