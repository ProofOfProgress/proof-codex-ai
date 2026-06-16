"""WebSocket rooms for shared 3D workspace — live transform sync per draft."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import WebSocket


class WorkspaceHub:
    def __init__(self) -> None:
        self._rooms: dict[int, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, draft_id: int, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._rooms.setdefault(draft_id, set()).add(ws)

    async def disconnect(self, draft_id: int, ws: WebSocket) -> None:
        async with self._lock:
            room = self._rooms.get(draft_id)
            if not room:
                return
            room.discard(ws)
            if not room:
                self._rooms.pop(draft_id, None)

    async def broadcast(self, draft_id: int, message: dict[str, Any], *, skip: WebSocket | None = None) -> None:
        async with self._lock:
            peers = list(self._rooms.get(draft_id, set()))
        dead: list[WebSocket] = []
        payload = json.dumps(message)
        for ws in peers:
            if ws is skip:
                continue
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(draft_id, ws)


workspace_hub = WorkspaceHub()
