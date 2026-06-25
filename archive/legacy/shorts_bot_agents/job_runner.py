"""Background execution of manager jobs (web async)."""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone

from shorts_bot.agents.duration import clamp_work_seconds, parse_work_duration
from shorts_bot.agents.job_store import ManagerJobStore
from shorts_bot.agents.manager import ChiefManager, run_manager_job, strip_manager_prefix
from shorts_bot.config import settings

log = logging.getLogger(__name__)

_lock = threading.Lock()
_running: set[str] = set()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def start_manager_job(
    store: ManagerJobStore,
    job_id: str,
) -> None:
    """Run job in a daemon thread."""
    with _lock:
        if job_id in _running:
            return
        _running.add(job_id)

    def _run() -> None:
        try:
            job = store.get(job_id)
            store.update(job_id, status="running", started_at=_utc_now())
            parsed = parse_work_duration(strip_manager_prefix(job.message))
            budget = job.work_seconds or parsed.work_seconds or 0
            budget = clamp_work_seconds(
                budget,
                minimum=settings.manager_work_floor_seconds,
                maximum=settings.manager_max_work_seconds,
            ) if budget else 0

            logs: list[str] = []

            def progress(msg: str) -> None:
                logs.append(msg)
                job_now = store.get(job_id)
                wl = list(job_now.work_log)
                wl.append({"progress": msg, "at": _utc_now()})
                store.update(job_id, work_log=wl)

            if budget > 0:
                result = run_manager_job(job.message, budget, on_progress=progress)
            else:
                result = ChiefManager(on_progress=progress).handle(job.message)

            store.update(
                job_id,
                status="done",
                reply=result.reply,
                work_log=result.session.work_log_dicts() if result.session else [],
                finished_at=_utc_now(),
            )
        except Exception as exc:
            log.exception("Manager job %s failed", job_id)
            try:
                store.update(job_id, status="error", error=str(exc), finished_at=_utc_now())
            except Exception:
                pass
        finally:
            with _lock:
                _running.discard(job_id)

    threading.Thread(target=_run, daemon=True, name=f"manager-job-{job_id}").start()
