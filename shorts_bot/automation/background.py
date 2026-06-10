"""Async background loops for web + Discord."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, time, timezone

from shorts_bot.config import settings

log = logging.getLogger(__name__)


async def analytics_sync_loop(stop_event: asyncio.Event) -> None:
    """Periodic YouTube analytics sync + auto-approve."""
    if not settings.auto_analytics_sync:
        return
    interval = max(1, settings.auto_analytics_sync_interval_hours) * 3600
    while not stop_event.is_set():
        try:
            from shorts_bot.web.deps import run_full_automation

            result = await asyncio.to_thread(run_full_automation)
            if result.sync.ok:
                log.info(
                    "Auto sync: %s videos, %s improvements auto-approved",
                    result.sync.videos_scored,
                    result.improvements_auto_approved,
                )
        except Exception as exc:  # noqa: BLE001
            log.warning("Auto analytics sync failed: %s", exc)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
            break
        except asyncio.TimeoutError:
            pass


async def publish_queue_loop(stop_event: asyncio.Event) -> None:
    """Check scheduled unlisted → public flips every hour."""
    if settings.auto_publish_hours <= 0:
        return
    while not stop_event.is_set():
        try:
            from shorts_bot.automation.coordinator import process_publish_queue
            from shorts_bot.web.deps import get_memory

            n = await asyncio.to_thread(process_publish_queue, get_memory())
            if n:
                log.info("Auto-published %s video(s)", n)
        except Exception as exc:  # noqa: BLE001
            log.warning("Publish queue failed: %s", exc)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=3600)
            break
        except asyncio.TimeoutError:
            pass


def _seconds_until(hour: int, minute: int) -> float:
    now = datetime.now(timezone.utc)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        from datetime import timedelta

        target += timedelta(days=1)
    return (target - now).total_seconds()


async def daily_autopilot_loop(stop_event: asyncio.Event) -> None:
    """Run full daily Short at configured UTC time."""
    if not settings.auto_daily_enabled:
        return
    while not stop_event.is_set():
        wait = _seconds_until(settings.auto_daily_hour, settings.auto_daily_minute)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=wait)
            break
        except asyncio.TimeoutError:
            pass
        if stop_event.is_set():
            break
        try:
            from shorts_bot.production.daily_cli import run_daily

            msg = await asyncio.to_thread(run_daily)
            log.info("Auto daily: %s", msg.split("\n")[0][:120])
        except Exception as exc:  # noqa: BLE001
            log.warning("Auto daily failed: %s", exc)
            from shorts_bot.automation.alerts import record_automation_alert

            record_automation_alert("daily_autopilot", str(exc))


async def comment_reply_loop(stop_event: asyncio.Event) -> None:
    if not settings.auto_reply_comments or not settings.auto_comment_sync:
        return
    interval = max(2, settings.auto_analytics_sync_interval_hours) * 3600
    while not stop_event.is_set():
        try:
            from shorts_bot.comments.runner import run_comment_automation
            from shorts_bot.web.deps import get_memory

            r = await asyncio.to_thread(run_comment_automation, get_memory())
            if r.auto_replied or r.queued_human:
                log.info("Comments: %s", r.message)
        except Exception as exc:  # noqa: BLE001
            log.warning("Comment automation failed: %s", exc)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
            break
        except asyncio.TimeoutError:
            pass


async def start_background_automation() -> asyncio.Event:
    """Start automation tasks; returns stop event for shutdown."""
    stop = asyncio.Event()
    tasks = [
        asyncio.create_task(analytics_sync_loop(stop), name="analytics_sync"),
        asyncio.create_task(publish_queue_loop(stop), name="publish_queue"),
        asyncio.create_task(daily_autopilot_loop(stop), name="daily_autopilot"),
        asyncio.create_task(comment_reply_loop(stop), name="comment_replies"),
    ]
    for t in tasks:
        t.add_done_callback(lambda fut: log.debug("Automation task done: %s", fut.get_name()))
    return stop
