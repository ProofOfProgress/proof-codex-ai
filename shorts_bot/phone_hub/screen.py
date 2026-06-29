"""Phone screen capture + on-screen text for cloud agent visibility."""

from __future__ import annotations

import base64
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.phone_hub.adb import run_adb, run_adb_bytes


def _adb_text(*args: str, serial: str | None = None, check: bool = False) -> str:
    return run_adb(*args, serial=serial, check=check).stdout


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _devices_path() -> Path:
    return _repo_root() / "data" / "phone_hub" / "devices.json"


def serial_for_slot(slot: str) -> str:
    slot = (slot or "").strip()
    path = _devices_path()
    if not path.is_file():
        raise RuntimeError(f"Missing {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    for row in data.get("slots", []):
        if row.get("slot") == slot:
            serial = str(row.get("adb_serial") or "").strip()
            if serial:
                return serial
            raise RuntimeError(f"{slot} has no adb_serial — run setup-phone first")
    raise RuntimeError(f"Unknown slot {slot!r}")


def screenshots_dir() -> Path:
    path = _repo_root() / "data" / "phone_hub" / "screenshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass
class PhoneScreenReport:
    slot: str
    serial: str
    screenshot_path: Path
    ui_lines: list[str] = field(default_factory=list)
    gemini_summary: str = ""
    screen_size: str = ""

    def to_markdown(self) -> str:
        lines = [
            f"# Phone screen — {self.slot}",
            "",
            f"- **Serial:** `{self.serial}`",
            f"- **Screenshot:** `{self.screenshot_path}`",
        ]
        if self.screen_size:
            lines.append(f"- **Size:** {self.screen_size}")
        if self.gemini_summary:
            lines.extend(["", "## What Gemini sees", "", self.gemini_summary])
        if self.ui_lines:
            lines.extend(["", "## On-screen text (UI dump)", ""])
            lines.extend(f"- {ln}" for ln in self.ui_lines[:40])
        return "\n".join(lines)


def capture_screenshot(*, serial: str, out_path: Path | None = None) -> Path:
    """PNG screencap via adb exec-out."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = out_path or (screenshots_dir() / f"screen_{serial}_{ts}.png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    png = run_adb_bytes("exec-out", "screencap", "-p", serial=serial, timeout=30)
    if not png.startswith(b"\x89PNG"):
        raise RuntimeError("screencap did not return PNG data — is the phone unlocked?")
    dest.write_bytes(png)
    return dest


def ui_visible_text(*, serial: str) -> list[str]:
    """Extract visible text labels from uiautomator dump (no vision API)."""
    remote = "/sdcard/window_dump.xml"
    run_adb("shell", "uiautomator", "dump", remote, serial=serial, check=False)
    xml = _adb_text("shell", "cat", remote, serial=serial, check=False)
    if not xml.strip():
        return []
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []
    seen: set[str] = set()
    lines: list[str] = []
    for node in root.iter("node"):
        for key in ("text", "content-desc"):
            val = (node.attrib.get(key) or "").strip()
            if not val or val in seen:
                continue
            seen.add(val)
            lines.append(val)
    return lines


def screen_size(*, serial: str) -> str:
    try:
        return _adb_text("shell", "wm", "size", serial=serial).replace("Physical size:", "").strip()
    except RuntimeError:
        return ""


def describe_screenshot_with_gemini(image_path: Path, *, slot: str) -> str:
    """Optional vision summary — needs GEMINI_API_KEY on hub."""
    try:
        from shorts_bot.config import settings
        from shorts_bot.llm.provider import get_llm_backend
    except ImportError:
        return ""
    if not settings.has_gemini:
        return ""
    backend = get_llm_backend()
    if backend is None or backend.provider != "gemini":
        return ""
    model = (settings.gemini_vision_model or settings.gemini_model).strip()
    b64 = base64.standard_b64encode(image_path.read_bytes()).decode("ascii")
    prompt = (
        f"TikTok Shop phone hub ({slot}). Describe what is on this Android screen in plain English "
        "for a non-developer owner: app name, main buttons, dialogs, errors, inbox/draft state. "
        "List any visible text verbatim. Under 120 words."
    )
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
    ]
    resp = backend.client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=250,
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()


def build_screen_report(
    slot: str,
    *,
    describe: bool = True,
    out_path: Path | None = None,
) -> PhoneScreenReport:
    serial = serial_for_slot(slot)
    shot = capture_screenshot(serial=serial, out_path=out_path)
    # Symlink-style latest for agent
    latest = screenshots_dir() / f"last_{slot}.png"
    latest.write_bytes(shot.read_bytes())

    ui_lines = ui_visible_text(serial=serial)
    summary = ""
    if describe:
        try:
            summary = describe_screenshot_with_gemini(shot, slot=slot)
        except Exception as exc:
            summary = f"(Gemini describe skipped: {exc})"

    report = PhoneScreenReport(
        slot=slot,
        serial=serial,
        screenshot_path=shot,
        ui_lines=ui_lines,
        gemini_summary=summary,
        screen_size=screen_size(serial=serial),
    )
    meta = screenshots_dir() / f"last_{slot}.json"
    meta.write_text(
        json.dumps(
            {
                "slot": slot,
                "serial": serial,
                "screenshot": str(shot),
                "screen_size": report.screen_size,
                "ui_lines": ui_lines,
                "gemini_summary": summary,
                "at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return report
