"""Background automation — sync, auto-approve, publish queue."""

from shorts_bot.automation.coordinator import (
    auto_approve_pending_improvements,
    process_publish_queue,
    run_analytics_sync_with_automation,
)

__all__ = [
    "auto_approve_pending_improvements",
    "process_publish_queue",
    "run_analytics_sync_with_automation",
]
