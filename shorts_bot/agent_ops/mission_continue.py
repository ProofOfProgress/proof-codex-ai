"""Suggest next CEO step from mission log (self-continue Phase 2)."""

from __future__ import annotations

from typing import Any

from shorts_bot.agent_ops.log import list_missions, mission_events, mission_summary


def _pending_background(events: list[dict[str, Any]]) -> list[str]:
    dispatched: list[str] = []
    done: set[str] = set()
    for row in events:
        event = row.get("event", "")
        agent = row.get("agent", "")
        target = row.get("target", "")
        if event == "dispatch_background" and target:
            dispatched.append(target)
        if event in ("completed", "failed") and agent:
            done.add(agent)
        if event in ("completed", "failed") and target:
            done.add(target)
    return [t for t in dispatched if t not in done]


def mission_continue_hint(*, mission_id: str | None = None) -> dict[str, Any]:
    """
    Read mission log and return the next recommended action for the CEO agent.

    Does not auto-run — prints actionable next step for owner or scheduler.
    """
    mid = mission_id
    if not mid or mid == "latest":
        missions = list_missions(limit=1)
        if not missions:
            return {"ok": False, "message": "No missions yet — create one with agent_ops mission new"}
        mid = missions[0]["mission_id"]

    summary = mission_summary(mid)
    if not summary:
        return {"ok": False, "message": f"Mission not found: {mid}"}

    pending = _pending_background(summary["events"])
    last = summary["events"][-1] if summary["events"] else {}
    last_event = last.get("event", "")
    last_msg = last.get("message", "")

    if pending:
        return {
            "ok": True,
            "mission_id": mid,
            "action": "poll_background",
            "targets": pending,
            "message": f"Poll background employees: {', '.join(pending)}. Check outputs before next dispatch.",
        }

    if last_event == "mission_created":
        return {
            "ok": True,
            "mission_id": mid,
            "action": "start_work",
            "message": f"Mission started: {summary['name']}. Begin first pipeline step.",
        }

    if last_event in ("hub_job_started", "dispatch_background"):
        return {
            "ok": True,
            "mission_id": mid,
            "action": "wait_or_poll",
            "message": last_msg or "Hub/background job running — poll status then continue.",
        }

    if last_event == "blocked":
        return {
            "ok": True,
            "mission_id": mid,
            "action": "owner_ping",
            "message": last_msg or "Blocked — run owner_ping with plain-English ask.",
        }

    return {
        "ok": True,
        "mission_id": mid,
        "action": "continue_pipeline",
        "message": last_msg or "Review mission log and run next affiliate pipeline step.",
    }
