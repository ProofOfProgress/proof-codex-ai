"""CLI — prepare daily pre-launch plan + CEO prompt."""

from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.panel import Panel

from shorts_bot.daily_prelaunch.plan import build_plan, save_plan
from shorts_bot.daily_prelaunch.paths import config_path, today_plan_path, today_prompt_path
from shorts_bot.daily_prelaunch.prompt import load_config, render_prompt, write_today_prompt


def cmd_prepare(console: Console) -> int:
    plan = build_plan()
    save_plan(plan)
    prompt = render_prompt(
        mission_id=str(plan["mission_id"]),
        mission_name=str(plan["mission_name"]),
        products=list(plan.get("products") or []),
    )
    write_today_prompt(prompt)
    console.print(Panel.fit(f"[green]Daily pre-launch prepared[/green]\n{plan['mission_id']}"))
    console.print(f"Plan: {today_plan_path()}")
    console.print(f"Prompt: {today_prompt_path()} ({len(prompt)} chars)")
    console.print(f"Products ({len(plan.get('products') or [])}): {', '.join(plan.get('products') or [])[:200]}")
    console.print(f"Scout: {plan.get('scout_note', '')}")
    return 0


def cmd_show(console: Console) -> int:
    path = today_plan_path()
    if not path.is_file():
        console.print("[yellow]No plan yet — run: daily_prelaunch prepare[/yellow]")
        return 1
    console.print(path.read_text(encoding="utf-8"))
    return 0


def cmd_prompt(console: Console) -> int:
    from shorts_bot.daily_prelaunch.prompt import read_today_prompt

    text = read_today_prompt()
    if not text:
        console.print("[yellow]No prompt — run prepare first[/yellow]")
        return 1
    console.print(text)
    return 0


def cmd_config(console: Console, *, clips: int | None, timezone: str | None) -> int:
    cfg = load_config()
    if clips is not None:
        cfg["clips_target"] = clips
    if timezone:
        cfg["timezone"] = timezone
    config_path().write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    console.print(f"[green]Saved[/green] {config_path()}")
    console.print(json.dumps(cfg, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    console = Console()
    parser = argparse.ArgumentParser(
        description="Daily pre-launch — research, plan, and CEO prompt for affiliate clip prep"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("prepare", help="Scout products, write today_plan.json + today_prompt.txt")
    sub.add_parser("show", help="Print today_plan.json")
    sub.add_parser("prompt", help="Print today_prompt.txt (for Cursor agent)")

    cfg_p = sub.add_parser("config", help="Set clips_target / timezone")
    cfg_p.add_argument("--clips", type=int, default=None)
    cfg_p.add_argument("--timezone", default="")

    args = parser.parse_args(argv)

    if args.cmd == "prepare":
        return cmd_prepare(console)
    if args.cmd == "show":
        return cmd_show(console)
    if args.cmd == "prompt":
        return cmd_prompt(console)
    if args.cmd == "config":
        return cmd_config(console, clips=args.clips, timezone=args.timezone or None)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
