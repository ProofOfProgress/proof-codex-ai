"""Send email via Gmail SMTP (app password)."""

from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

from shorts_bot.config import settings

log = logging.getLogger(__name__)

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587


def _valid_smtp_credentials(user: str, password: str) -> bool:
    if "@" not in user or len(password) < 8:
        return False
    lower = password.lower()
    return "your" not in lower and "placeholder" not in lower


def has_gmail_smtp() -> bool:
    user = (settings.gmail_smtp_user or "").strip()
    password = (settings.gmail_smtp_app_password or "").strip()
    return _valid_smtp_credentials(user, password)


def send_smtp_email(
    *,
    smtp_user: str,
    smtp_password: str,
    to: str,
    subject: str,
    body: str,
    from_addr: str | None = None,
    smtp_host: str | None = None,
    smtp_port: int | None = None,
) -> tuple[bool, str]:
    """Send plain-text email through SMTP (Gmail / Google Workspace)."""
    user = smtp_user.strip()
    password = smtp_password.strip()
    recipient = (to or "").strip()
    if not _valid_smtp_credentials(user, password):
        return False, "SMTP user + app password required"
    if "@" not in recipient:
        return False, "Invalid recipient address"

    sender = (from_addr or user).strip()
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject[:200]
    msg["From"] = sender
    msg["To"] = recipient

    host = (smtp_host or GMAIL_SMTP_HOST).strip()
    port = int(smtp_port or GMAIL_SMTP_PORT)
    try:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
            smtp.sendmail(sender, [recipient], msg.as_string())
        log.info("SMTP sent → %s (%s)", recipient, subject[:60])
        return True, ""
    except smtplib.SMTPAuthenticationError:
        log.warning("SMTP auth failed — check app password")
        return False, "SMTP auth failed — use a Google App Password, not your login password"
    except Exception as exc:  # noqa: BLE001
        log.warning("SMTP send failed: %s", exc)
        return False, str(exc)


def send_gmail_email(
    *,
    to: str,
    subject: str,
    body: str,
    from_addr: str | None = None,
) -> tuple[bool, str]:
    """Send plain-text email through ops Gmail (Slack alerts)."""
    user = (settings.gmail_smtp_user or "").strip()
    password = (settings.gmail_smtp_app_password or "").strip()
    if not has_gmail_smtp():
        return False, "GMAIL_SMTP_USER + GMAIL_SMTP_APP_PASSWORD required"
    host = (getattr(settings, "smtp_host", None) or GMAIL_SMTP_HOST).strip()
    port = int(getattr(settings, "smtp_port", None) or GMAIL_SMTP_PORT)
    return send_smtp_email(
        smtp_user=user,
        smtp_password=password,
        to=to,
        subject=subject,
        body=body,
        from_addr=from_addr,
        smtp_host=host,
        smtp_port=port,
    )
