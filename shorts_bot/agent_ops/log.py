"""Append-only mission log for CEO ↔ subagent orchestration."""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any

from shorts_bot.agent_ops.models import AgentEvent, utc_now_iso

_MISSION_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{6,64}$")


def ops_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    path = root / "data" / "agent_ops" / "missions"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _mission_path(mission_id: str) -> Path:
    if not _MISSION_ID_RE.match(mission_id):
        raise ValueError(f"Invalid mission id: {mission_id!r}")
    return ops_dir() / f"{mission_id}.jsonl"


def new_mission(name: str, *, owner: str = "") -> str:
    mission_id = uuid.uuid4().hex[:12]
    append_event(
        mission_id,
        agent="ceo",
        event="mission_created",
        message=name,
        data={"owner": owner} if owner else {},
    )
    return mission_id


def append_event(
    mission_id: str,
    *,
    agent: str,
    event: str,
    message: str = "",
    target: str = "",
    data: dict[str, Any] | None = None,
) -> AgentEvent:
    row = AgentEvent(
        ts=utc_now_iso(),
        mission_id=mission_id,
        agent=agent,
        event=event,
        message=message,
        target=target,
        data=data or {},
    )
    path = _mission_path(mission_id)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")
    return row


def mission_events(mission_id: str, *, limit: int = 500) -> list[dict[str, Any]]:
    path = _mission_path(mission_id)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    rows: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def list_missions(*, limit: int = 20) -> list[dict[str, Any]]:
    paths = sorted(ops_dir().glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    out: list[dict[str, Any]] = []
    for path in paths[:limit]:
        mission_id = path.stem
        events = mission_events(mission_id, limit=200)
        if not events:
            continue
        first = events[0]
        last = events[-1]
        agents = sorted({e.get("agent", "") for e in events if e.get("agent")})
        out.append(
            {
                "mission_id": mission_id,
                "name": first.get("message", ""),
                "created_at": first.get("ts", ""),
                "updated_at": last.get("ts", ""),
                "event_count": len(events),
                "agents": agents,
                "last_event": last.get("event", ""),
                "last_agent": last.get("agent", ""),
                "last_message": last.get("message", ""),
            }
        )
    return out


def mission_summary(mission_id: str) -> dict[str, Any] | None:
    events = mission_events(mission_id)
    if not events:
        return None
    first = events[0]
    last = events[-1]
    running = [
        e.get("target") or e.get("agent", "")
        for e in events
        if e.get("event") == "dispatch_background"
    ]
    completed = {
        e.get("agent", "")
        for e in events
        if e.get("event") in ("completed", "failed")
    }
    return {
        "mission_id": mission_id,
        "name": first.get("message", ""),
        "created_at": first.get("ts", ""),
        "updated_at": last.get("ts", ""),
        "events": events,
        "agents": sorted({e.get("agent", "") for e in events if e.get("agent")}),
        "background_dispatched": running,
        "completed_agents": sorted(completed),
    }
