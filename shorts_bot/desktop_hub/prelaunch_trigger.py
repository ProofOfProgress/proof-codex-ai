"""Daily pre-launch schedule + Cursor submit trigger."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from shorts_bot.desktop_hub.config import desktop_hub_dir, schedule_path
from shorts_bot.desktop_hub.schedule import should_run_now


@dataclass
class DailyPrelaunchSchedule:
    enabled: bool = False
    hour: int = 7
    minute: int = 0
    timezone: str = "America/Los_Angeles"
    clips_target: int = 8
    prepare_via_wsl: bool = True
    focus_x: int = 0
    focus_y: int = 0
    submit_x: int = 0
    submit_y: int = 0
    label: str = "Cursor — send daily CEO mission"

    def validate(self) -> None:
        if not (0 <= self.hour <= 23):
            raise ValueError("hour must be 0-23")
        if not (0 <= self.minute <= 59):
            raise ValueError("minute must be 0-59")


def load_full_schedule(path: Path | None = None) -> dict[str, Any]:
    p = path or schedule_path()
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def load_prelaunch_schedule(path: Path | None = None) -> DailyPrelaunchSchedule:
    raw = load_full_schedule(path)
    block = raw.get("daily_prelaunch") or {}
    sched = DailyPrelaunchSchedule(
        enabled=bool(block.get("enabled", False)),
        hour=int(block.get("hour", 7)),
        minute=int(block.get("minute", 0)),
        timezone=str(block.get("timezone", "America/Los_Angeles")),
        clips_target=int(block.get("clips_target", 8)),
        prepare_via_wsl=bool(block.get("prepare_via_wsl", True)),
        focus_x=int(block.get("focus_x", block.get("focus_click", {}).get("x", 0))),
        focus_y=int(block.get("focus_y", block.get("focus_click", {}).get("y", 0))),
        submit_x=int(block.get("submit_x", block.get("submit_click", {}).get("x", 0))),
        submit_y=int(block.get("submit_y", block.get("submit_click", {}).get("y", 0))),
        label=str(block.get("label", "")),
    )
    sched.validate()
    return sched


def save_prelaunch_schedule(sched: DailyPrelaunchSchedule, *, path: Path | None = None) -> Path:
    sched.validate()
    p = path or schedule_path()
    raw = load_full_schedule(p) if p.is_file() else {}
    raw["daily_prelaunch"] = {
        "enabled": sched.enabled,
        "hour": sched.hour,
        "minute": sched.minute,
        "timezone": sched.timezone,
        "clips_target": sched.clips_target,
        "prepare_via_wsl": sched.prepare_via_wsl,
        "focus_x": sched.focus_x,
        "focus_y": sched.focus_y,
        "submit_x": sched.submit_x,
        "submit_y": sched.submit_y,
        "label": sched.label,
    }
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
    return p


def _prelaunch_log(detail: str, *, sched: DailyPrelaunchSchedule | None = None) -> None:
    row = {
        "at": datetime.now().astimezone().isoformat(),
        "kind": "daily_prelaunch",
        "detail": detail,
        "label": sched.label if sched else "",
    }
    path = desktop_hub_dir() / "prelaunch_log.jsonl"
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def run_prepare_via_wsl(repo_root: Path | None = None) -> None:
    root = repo_root or Path(__file__).resolve().parents[2]
    cmd = f"cd {root.as_posix()} && python3 -m shorts_bot.daily_prelaunch.cli prepare"
    proc = subprocess.run(
        ["wsl.exe", "-e", "bash", "-lc", cmd],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "wsl prepare failed").strip())


def read_prompt_for_trigger(repo_root: Path | None = None) -> str:
    root = repo_root or Path(__file__).resolve().parents[2]
    prompt_path = root / "data" / "daily_prelaunch" / "today_prompt.txt"
    if not prompt_path.is_file():
        raise RuntimeError(f"Missing {prompt_path} — run daily_prelaunch prepare first")
    return prompt_path.read_text(encoding="utf-8").strip()


def execute_prelaunch_trigger(
    executor: Any,
    sched: DailyPrelaunchSchedule,
    *,
    repo_root: Path | None = None,
    paste_via_clipboard: Callable[[str], None] | None = None,
) -> None:
    """Focus Cursor → paste daily prompt → click Run (submit coords)."""
    root = repo_root or Path(__file__).resolve().parents[2]

    if sched.prepare_via_wsl:
        run_prepare_via_wsl(root)

    prompt = read_prompt_for_trigger(root)
    if not prompt:
        raise RuntimeError("today_prompt.txt is empty")

    if sched.focus_x or sched.focus_y:
        executor.execute({"action": "click", "x": sched.focus_x, "y": sched.focus_y, "button": "left"})

    executor.execute({"action": "hotkey", "keys": ["ctrl", "a"]})

    if paste_via_clipboard:
        paste_via_clipboard(prompt)
        executor.execute({"action": "hotkey", "keys": ["ctrl", "v"]})
    else:
        # Chunk long prompts — pynput types in reasonable blocks
        chunk = 500
        for i in range(0, len(prompt), chunk):
            executor.execute({"action": "type", "text": prompt[i : i + chunk]})

    if sched.submit_x or sched.submit_y:
        executor.execute(
            {"action": "click", "x": sched.submit_x, "y": sched.submit_y, "button": "left", "clicks": 1}
        )

    _prelaunch_log(f"triggered CEO prompt ({len(prompt)} chars)", sched=sched)


class DailyPrelaunchScheduler:
    """Fire prelaunch trigger once per calendar day."""

    def __init__(
        self,
        executor_factory: Callable[[], Any],
        *,
        poll_seconds: float = 30.0,
        paste_via_clipboard: Callable[[str], None] | None = None,
    ) -> None:
        self._executor_factory = executor_factory
        self._poll_seconds = poll_seconds
        self._paste = paste_via_clipboard
        self._last_run_date: date | None = None
        self._stop = __import__("threading").Event()
        self._thread = None

    def start(self) -> None:
        import threading

        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="daily-prelaunch-scheduler", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        import time

        while not self._stop.is_set():
            try:
                sched = load_prelaunch_schedule()
                if sched.enabled and should_run_now(sched):
                    tz = ZoneInfo(sched.timezone)
                    today = datetime.now(tz).date()
                    if self._last_run_date != today:
                        executor = self._executor_factory()
                        execute_prelaunch_trigger(executor, sched, paste_via_clipboard=self._paste)
                        self._last_run_date = today
            except Exception as exc:
                _prelaunch_log(f"error: {exc}")
            self._stop.wait(self._poll_seconds)
