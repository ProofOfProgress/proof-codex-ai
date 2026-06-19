"""Minimal MCP HTTP client for InVideo (mcp.invideo.io)."""

from __future__ import annotations

import json
from typing import Any

import httpx

from shorts_bot.config import settings

MCP_URL = "https://mcp.invideo.io/mcp"
PROTOCOL_VERSION = "2024-11-05"


def _parse_sse_payloads(text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for block in text.split("\n\n"):
        data_line = next((ln[6:] for ln in block.splitlines() if ln.startswith("data: ")), None)
        if not data_line:
            continue
        try:
            out.append(json.loads(data_line))
        except json.JSONDecodeError:
            continue
    return out


class InVideoMcpClient:
    """Talk to InVideo's official MCP server (generate-video-from-script)."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        mcp_url: str | None = None,
    ) -> None:
        self.api_key = (api_key or settings.invideo_api_key or "").strip() or None
        self.mcp_url = (mcp_url or settings.invideo_mcp_url or MCP_URL).strip()
        self.session_id: str | None = None

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _rpc(self, payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=120.0) as client:
            resp = client.post(self.mcp_url, json=payload, headers=self._headers())
        sid = resp.headers.get("mcp-session-id") or resp.headers.get("Mcp-Session-Id")
        if sid:
            self.session_id = sid
        if resp.status_code >= 400:
            raise RuntimeError(f"InVideo MCP HTTP {resp.status_code}: {resp.text[:300]}")
        events = _parse_sse_payloads(resp.text)
        if not events:
            raise RuntimeError(f"InVideo MCP empty SSE response: {resp.text[:200]}")
        last = events[-1]
        if last.get("error"):
            err = last["error"]
            raise RuntimeError(f"InVideo MCP error {err.get('code')}: {err.get('message')}")
        return last.get("result") or {}

    def initialize(self) -> dict[str, Any]:
        result = self._rpc(
            {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "shorts_bot", "version": "1.0"},
                },
                "id": 1,
            }
        )
        try:
            self._rpc(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized",
                    "params": {},
                }
            )
        except RuntimeError:
            pass
        return result

    def list_tools(self) -> list[dict[str, Any]]:
        if not self.session_id:
            self.initialize()
        result = self._rpc({"jsonrpc": "2.0", "method": "tools/list", "id": 2})
        return result.get("tools") or []

    def generate_video_from_script(
        self,
        *,
        script: str,
        topic: str,
        vibe: str | None = None,
        target_audience: str | None = None,
        platform: str | None = None,
    ) -> str:
        """Return InVideo project URL (open in browser while logged in)."""
        if not self.session_id:
            self.initialize()
        vibe = vibe or settings.invideo_default_vibe
        target_audience = target_audience or settings.invideo_default_audience
        platform = platform or settings.invideo_default_platform
        result = self._rpc(
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "generate-video-from-script",
                    "arguments": {
                        "script": script.strip(),
                        "topic": topic.strip(),
                        "vibe": vibe,
                        "targetAudience": target_audience,
                        "platform": platform,
                    },
                },
                "id": 3,
            }
        )
        content = result.get("content") or []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                url = (block.get("text") or "").strip()
                if url.startswith("http"):
                    return url
        raise RuntimeError(f"InVideo MCP returned no project URL: {result!r}")


def probe_mcp(*, api_key: str | None = None) -> tuple[bool, str]:
    """Quick connectivity check — lists MCP tools."""
    try:
        client = InVideoMcpClient(api_key=api_key)
        tools = client.list_tools()
        names = [t.get("name", "?") for t in tools]
        if not names:
            return False, "MCP connected but no tools returned"
        return True, f"MCP OK — tools: {', '.join(names)}"
    except Exception as exc:
        return False, str(exc)[:160]
