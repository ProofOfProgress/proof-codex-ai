"""Record automation failures for operator visibility (web / file)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings

log = logging.getLogger(__name__)


def record_automation_alert(event: str, message: str, *, detail: str = "") -> None:
    """
    Persist alert to data/ALERTS.md and channel_state for next status check.
    """
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    line = f"- **{ts}** `{event}`: {message}"
    if detail:
        line += f"\n  - {detail[:500]}"

    alerts_path = settings.data_dir / "ALERTS.md"
    alerts_path.parent.mkdir(parents=True, exist_ok=True)
    header = "# Automation alerts\n\n"
    existing = alerts_path.read_text(encoding="utf-8") if alerts_path.exists() else header
    if not existing.startswith("#"):
        existing = header + existing
    # Keep last 40 lines
    body_lines = [ln for ln in existing.splitlines() if ln.strip()]
    body_lines.insert(1 if body_lines and body_lines[0].startswith("#") else 0, line)
    trimmed = body_lines[:42]
    alerts_path.write_text("\n".join(trimmed) + "\n", encoding="utf-8")

    try:
        from shorts_bot.memory.store import MemoryStore

        store = MemoryStore(settings.database_path)
        store.set_channel_state("last_automation_alert", f"{event}: {message[:200]}")
        store.set_channel_state("last_automation_alert_at", ts)
    except Exception as exc:  # noqa: BLE001
        log.debug("Could not write alert to channel_state: %s", exc)

    log.warning("AUTOMATION ALERT [%s]: %s", event, message)

    try:
        from shorts_bot.integrations.slack import notify_automation_alert

        notify_automation_alert(event, message, detail=detail)
    except Exception as exc:  # noqa: BLE001
        log.debug("Slack notify skipped: %s", exc)
