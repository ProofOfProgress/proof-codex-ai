"""Daily scheduled click — same wall-clock time every 24 hours."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Callable
from zoneinfo import ZoneInfo

from shorts_bot.desktop_hub.config import desktop_hub_dir, schedule_path


@dataclass
class DailyClickSchedule:
    enabled: bool = False
    hour: int = 12
    minute: int = 0
    timezone: str = "America/Los_Angeles"
    x: int = 0
    y: int = 0
    button: str = "left"
    label: str = ""

    def validate(self) -> None:
        if not (0 <= self.hour <= 23):
            raise ValueError("hour must be 0-23")
        if not (0 <= self.minute <= 59):
            raise ValueError("minute must be 0-59")
        if self.button not in ("left", "right", "middle"):
            raise ValueError("button must be left, right, or middle")


def default_schedule() -> DailyClickSchedule:
    return DailyClickSchedule(
        enabled=False,
        hour=12,
        minute=0,
        timezone="America/Los_Angeles",
        x=0,
        y=0,
        label="Set x/y in schedule.json or: desktop_hub schedule set-click",
    )


def load_schedule(path: Path | None = None) -> DailyClickSchedule:
    p = path or schedule_path()
    if not p.is_file():
        sched = default_schedule()
        save_schedule(sched, path=p)
        return sched
    raw = json.loads(p.read_text(encoding="utf-8"))
    block = raw.get("daily_click") or raw
    sched = DailyClickSchedule(
        enabled=bool(block.get("enabled", False)),
        hour=int(block.get("hour", 12)),
        minute=int(block.get("minute", 0)),
        timezone=str(block.get("timezone", "America/Los_Angeles")),
        x=int(block.get("x", 0)),
        y=int(block.get("y", 0)),
        button=str(block.get("button", "left")),
        label=str(block.get("label", "")),
    )
    sched.validate()
    return sched


def save_schedule(sched: DailyClickSchedule, *, path: Path | None = None) -> Path:
    sched.validate()
    p = path or schedule_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"daily_click": asdict(sched)}
    p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return p


def _schedule_log_path() -> Path:
    return desktop_hub_dir() / "schedule_log.jsonl"


def log_scheduled_click(sched: DailyClickSchedule, *, detail: str = "ok") -> None:
    row = {
        "at": datetime.now().astimezone().isoformat(),
        "x": sched.x,
        "y": sched.y,
        "label": sched.label,
        "detail": detail,
    }
    path = _schedule_log_path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def should_run_now(sched: DailyClickSchedule, now: datetime | None = None) -> bool:
    if not sched.enabled:
        return False
    tz = ZoneInfo(sched.timezone)
    now = (now or datetime.now(tz)).astimezone(tz)
    if now.hour != sched.hour or now.minute != sched.minute:
        return False
    return True


class DailyClickScheduler:
    """Background thread — fires click callback once per calendar day at scheduled time."""

    def __init__(
        self,
        executor: Callable[[DailyClickSchedule], None],
        *,
        poll_seconds: float = 30.0,
    ) -> None:
        self._executor = executor
        self._poll_seconds = poll_seconds
        self._last_run_date: date | None = None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="daily-click-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                sched = load_schedule()
                if sched.enabled and should_run_now(sched):
                    tz = ZoneInfo(sched.timezone)
                    today = datetime.now(tz).date()
                    if self._last_run_date != today:
                        self._executor(sched)
                        log_scheduled_click(sched)
                        self._last_run_date = today
            except Exception as exc:
                try:
                    sched = load_schedule()
                    log_scheduled_click(sched, detail=f"error: {exc}")
                except Exception:
                    pass
            self._stop.wait(self._poll_seconds)
