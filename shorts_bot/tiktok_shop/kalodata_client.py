"""Kalodata KaloPilot API — product research without Enterprise API tier."""

from __future__ import annotations

import os
import time
from typing import Any

import httpx

from shorts_bot.agent_credentials import load_agent_credentials
from shorts_bot.config import settings

DEFAULT_BASE = "https://staging.kalodata.com/api/pilot/skill/ext/v1"


def configured() -> bool:
    load_agent_credentials()
    token = (os.environ.get("KALODATA_PILOT_TOKEN") or settings.kalodata_pilot_token or "").strip()
    if not token:
        return False
    lower = token.lower()
    return "placeholder" not in lower and "your-" not in lower


def _base() -> str:
    return (settings.kalodata_pilot_base or DEFAULT_BASE).rstrip("/")


def _headers() -> dict[str, str]:
    load_agent_credentials()
    token = (os.environ.get("KALODATA_PILOT_TOKEN") or settings.kalodata_pilot_token or "").strip()
    if not token:
        raise RuntimeError("Kalodata not configured — set KALODATA_PILOT_TOKEN")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def submit_query(query: str, *, task_id: str | None = None) -> dict[str, Any]:
    """Submit async KaloPilot query; returns API JSON (includes data.task_id)."""
    text = query.strip()
    if not text:
        raise RuntimeError("Kalodata query is empty")
    payload: dict[str, str] = {"query": text}
    if task_id:
        payload["task_id"] = task_id
    url = f"{_base()}/chat/async/submit"
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=payload, headers=_headers())
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"Kalodata non-JSON ({resp.status_code}): {resp.text[:300]}") from exc
    if resp.status_code >= 400 or body.get("success") is False:
        msg = body.get("message") or body
        raise RuntimeError(f"Kalodata submit error: {msg}")
    return body


def poll_result(task_id: str) -> dict[str, Any]:
    """Poll async task — data.status is running | completed | error | cancelled."""
    url = f"{_base()}/chat/async/result"
    with httpx.Client(timeout=60.0) as client:
        resp = client.get(url, params={"task_id": task_id}, headers=_headers())
    try:
        body = resp.json()
    except Exception as exc:
        raise RuntimeError(f"Kalodata non-JSON ({resp.status_code}): {resp.text[:300]}") from exc
    if resp.status_code >= 400:
        raise RuntimeError(f"Kalodata poll error ({resp.status_code}): {body}")
    return body


def query_and_wait(
    query: str,
    *,
    task_id: str | None = None,
    first_wait_s: float = 45.0,
    poll_interval_s: float = 30.0,
    timeout_s: float = 300.0,
) -> dict[str, Any]:
    """Submit query, poll until completed. Returns data dict with text/report."""
    submitted = submit_query(query, task_id=task_id)
    data = submitted.get("data") if isinstance(submitted.get("data"), dict) else {}
    new_task_id = str(data.get("task_id") or "")
    if not new_task_id:
        raise RuntimeError(f"Kalodata submit missing task_id: {submitted}")

    deadline = time.monotonic() + timeout_s
    time.sleep(first_wait_s)
    while time.monotonic() < deadline:
        polled = poll_result(new_task_id)
        pdata = polled.get("data") if isinstance(polled.get("data"), dict) else {}
        status = str(pdata.get("status") or "").lower()
        if status == "completed":
            return pdata
        if status in ("error", "cancelled"):
            err = pdata.get("error") if isinstance(pdata.get("error"), dict) else {}
            raise RuntimeError(f"Kalodata task {status}: {err.get('message') or pdata}")
        time.sleep(poll_interval_s)
    raise RuntimeError(f"Kalodata task timed out after {timeout_s:.0f}s (task_id={new_task_id})")


def ping() -> dict[str, Any]:
    """Lightweight connectivity test."""
    if not configured():
        return {
            "ok": False,
            "error": "not_configured",
            "message": "Set KALODATA_PILOT_TOKEN — docs/FOR_OWNER_KALODATA_OR_FASTMOSS.md",
        }
    try:
        data = query_and_wait(
            "US TikTok Shop: list 3 trending products with name and estimated GMV only.",
            first_wait_s=20.0,
            poll_interval_s=15.0,
            timeout_s=120.0,
        )
        text = str(data.get("text") or "")[:200]
        return {"ok": True, "provider": "kalodata", "sample": text or "(completed, empty text)"}
    except RuntimeError as exc:
        msg = str(exc)
        if "credits" in msg.lower() or "membership" in msg.lower():
            return {"ok": False, "error": "billing", "message": msg}
        return {"ok": False, "error": "api_error", "message": msg}
