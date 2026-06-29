"""Render daily CEO prompt from template + plan."""

from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from shorts_bot.daily_prelaunch.paths import prelaunch_dir, template_path, today_plan_path, today_prompt_path


def load_config() -> dict:
    from shorts_bot.daily_prelaunch.paths import config_path

    defaults = {
        "clips_target": 8,
        "timezone": "America/Los_Angeles",
        "prelaunch_mode": True,
    }
    path = config_path()
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(defaults, indent=2) + "\n", encoding="utf-8")
        return defaults
    data = json.loads(path.read_text(encoding="utf-8"))
    return {**defaults, **data}


def render_prompt(*, mission_id: str, mission_name: str, products: list[str]) -> str:
    cfg = load_config()
    tz = ZoneInfo(str(cfg.get("timezone", "America/Los_Angeles")))
    now = datetime.now(tz)
    template = template_path().read_text(encoding="utf-8")
    clips = int(cfg.get("clips_target", 8))
    product_list = ", ".join(products) if products else "(scout will fill — read today_plan.json)"
    return template.format(
        mission_id=mission_id,
        mission_name=mission_name,
        date=now.strftime("%Y-%m-%d"),
        timezone=str(cfg.get("timezone", "America/Los_Angeles")),
        clips_target=clips,
        product_list=product_list,
    )


def write_today_prompt(text: str) -> Path:
    path = today_prompt_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def read_today_prompt() -> str:
    path = today_prompt_path()
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()
