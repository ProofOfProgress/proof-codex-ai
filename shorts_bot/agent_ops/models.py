"""Mission log event models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass
class AgentEvent:
    ts: str
    mission_id: str
    agent: str
    event: str
    message: str = ""
    target: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        if not row["target"]:
            del row["target"]
        if not row["data"]:
            del row["data"]
        return row
