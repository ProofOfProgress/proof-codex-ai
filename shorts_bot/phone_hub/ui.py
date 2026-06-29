"""ADB UI helpers for bubble phones — tap, type, uiautomator dump.

Full TikTok inbox → Mackenzie → publish needs live phones + coordinate map
(``data/phone_hub/ui_coords.json``) or uiautomator text search. This module
scaffolds the primitives the worker will call.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from shorts_bot.phone_hub.adb import AdbError, run_adb


def tap(x: int, y: int, *, serial: str, check: bool = True) -> None:
    run_adb("shell", "input", "tap", str(x), str(y), serial=serial, check=check)


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int, *, serial: str) -> None:
    run_adb(
        "shell",
        "input",
        "swipe",
        str(x1),
        str(y1),
        str(x2),
        str(y2),
        str(duration_ms),
        serial=serial,
        check=True,
    )


def input_text(text: str, *, serial: str) -> None:
    """Type text via ADB (spaces → %s, special chars escaped)."""
    safe = text.replace(" ", "%s").replace("'", "\\'")
    run_adb("shell", "input", "text", safe, serial=serial, check=True)


def keyevent(code: str, *, serial: str) -> None:
    run_adb("shell", "input", "keyevent", code, serial=serial, check=True)


def uiautomator_dump(*, serial: str) -> str:
    """Return UI hierarchy XML from device (may be empty on failure)."""
    remote = "/sdcard/window_dump.xml"
    run_adb("shell", "uiautomator", "dump", remote, serial=serial, check=False)
    result = run_adb("shell", "cat", remote, serial=serial, check=False)
    if not result.ok or not result.stdout.strip():
        raise AdbError("uiautomator dump failed — is the screen on?")
    return result.stdout


def find_bounds_by_text(xml: str, text: str, *, partial: bool = True) -> tuple[int, int] | None:
    """Parse dump XML; return center (x, y) of first node matching text."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return None
    target = text.lower()
    for node in root.iter("node"):
        label = (node.attrib.get("text") or "") + " " + (node.attrib.get("content-desc") or "")
        label = label.strip().lower()
        if not label:
            continue
        if partial and target in label:
            match = True
        elif not partial and label == target:
            match = True
        else:
            match = False
        if not match:
            continue
        bounds = node.attrib.get("bounds", "")
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
        if not m:
            continue
        x1, y1, x2, y2 = (int(m.group(i)) for i in range(1, 5))
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    return None


def tap_by_text(text: str, *, serial: str, partial: bool = True) -> bool:
    """Dump UI, find text, tap center. Returns True if tapped."""
    xml = uiautomator_dump(serial=serial)
    point = find_bounds_by_text(xml, text, partial=partial)
    if not point:
        return False
    tap(point[0], point[1], serial=serial)
    return True
