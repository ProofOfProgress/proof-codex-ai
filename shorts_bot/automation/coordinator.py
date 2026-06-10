"""Orchestrate automated sync, approvals, and publish queue."""

from __future__ import annotations

from dataclasses import dataclass

from shorts_bot.automation.auto_approve import dev_task_is_auto_approvable, improvement_is_auto_approvable
from shorts_bot.automation.dev_queue import export_dev_queue
from shorts_bot.config import settings
from shorts_bot.learning.learned_file import LearnedFile
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.training.proposer import ImprovementProposer
from shorts_bot.youtube.sync import AnalyticsSync, SyncResult


@dataclass
class AutomationResult:
    sync: SyncResult
    improvements_auto_approved: int = 0
    dev_tasks_auto_approved: int = 0
    videos_published: int = 0

    @property
    def ok(self) -> bool:
        return self.sync.ok


def auto_approve_pending_improvements(memory: MemoryExtensions) -> int:
    if not settings.auto_approve_improvements:
        return 0
    learned = LearnedFile(settings.learned_path)
    count = 0
    for imp in memory.list_improvements(status="pending", limit=20):
        if not improvement_is_auto_approvable(imp):
            continue
        memory.review_improvement(imp.id, approved=True, note="Auto-approved (safe rule)")
        learned.record_improvement(memory.get_improvement(imp.id), approved=True)
        count += 1
    return count


def auto_approve_pending_dev_tasks(memory: MemoryExtensions) -> int:
    if not settings.auto_approve_dev_tasks:
        return 0
    learned = LearnedFile(settings.learned_path)
    count = 0
    for task in memory.list_dev_tasks(status="pending", limit=20):
        if not dev_task_is_auto_approvable(task):
            continue
        memory.review_dev_task(task.id, approved=True, note="Auto-approved (no login/payment)")
        learned.record_dev_task(memory.get_dev_task(task.id), approved=True)
        count += 1
    if count:
        export_dev_queue(memory)
    return count


def process_publish_queue(memory: MemoryExtensions) -> int:
    if settings.auto_publish_hours <= 0:
        return 0
    from shorts_bot.youtube.publish import publish_due_videos

    published = publish_due_videos(memory)
    return len(published)


def run_analytics_sync_with_automation(
    memory: MemoryExtensions,
    proposer: ImprovementProposer,
    *,
    days: int = 28,
    max_videos: int = 15,
) -> AutomationResult:
    sync = AnalyticsSync(memory, proposer).run(days=days, max_videos=max_videos)
    imp_n = auto_approve_pending_improvements(memory) if sync.ok else 0
    dev_n = auto_approve_pending_dev_tasks(memory) if sync.ok else 0
    pub_n = process_publish_queue(memory)
    return AutomationResult(
        sync=sync,
        improvements_auto_approved=imp_n,
        dev_tasks_auto_approved=dev_n,
        videos_published=pub_n,
    )
