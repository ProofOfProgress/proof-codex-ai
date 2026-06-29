"""Daily pre-launch — research, plan, and prompt for CEO agent missions."""

from __future__ import annotations

from pathlib import Path

from shorts_bot.config import settings


def prelaunch_dir() -> Path:
    path = settings.data_dir / "daily_prelaunch"
    path.mkdir(parents=True, exist_ok=True)
    return path


def template_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "daily_prelaunch" / "PROMPT.template.md"


def today_plan_path() -> Path:
    return prelaunch_dir() / "today_plan.json"


def today_prompt_path() -> Path:
    return prelaunch_dir() / "today_prompt.txt"


def config_path() -> Path:
    return prelaunch_dir() / "config.json"
