"""
Post a 2-slide TikTok photo carousel with a specific sound via Android ADB.

Lead-3 flow (sound first):
  1. Open Mackenzie via tiktok://music/{id}
  2. Tap "Use this sound"
  3. Open gallery → select 2 images → photo carousel → Post

Requires: Android phone, USB/WiFi debugging, TikTok logged in, uiautomator2 on the host.
"""

from __future__ import annotations

import datetime
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from shorts_bot.config import settings
from shorts_bot.tiktok.adb import AdbClient, AdbError
from shorts_bot.tiktok.sounds import (
    MACKENZIE_SOUND_ID,
    mackenzie_deep_link_uri,
    sound_deep_link_uri,
)

# Folder on phone — isolated so we can wipe between runs.
PHONE_UPLOAD_DIR = "Pictures/BubbleWrapBot"
USE_SOUND_LABELS = (
    "Use this sound",
    "Use sound",
    "Use audio",
    "Use this audio",
)
GALLERY_LABELS = ("Upload", "Gallery", "Photos")
PHOTO_MODE_LABELS = ("Switch to photo mode", "Photo")
NEXT_LABELS = ("Next", "OK")
POST_LABELS = ("Post", "Publish")
DRAFT_LABELS = ("Drafts", "Save to drafts")
AIGC_LABELS = (
    "Content disclosure",
    "AI-generated content",
    "Made with AI",
    "Video made with AI",
)


@dataclass
class CarouselPostResult:
    ok: bool
    message: str
    steps: list[str] = field(default_factory=list)
    device_id: str = ""
    sound_id: str = ""


def _require_u2() -> Any:
    try:
        import uiautomator2 as u2  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "uiautomator2 is required for phone automation. "
            "Install: pip install uiautomator2 && python -m uiautomator2 init"
        ) from exc
    return u2


def _click_first_text(device: Any, labels: tuple[str, ...], *, timeout: float = 8.0) -> str | None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        for label in labels:
            if device(text=label).click_exists(timeout=0.5):
                return label
            if device(textContains=label).click_exists(timeout=0.5):
                return label
        time.sleep(0.4)
    return None


def _push_carousel_images(adb: AdbClient, image_paths: list[Path]) -> list[str]:
    adb.shell(f"rm -rf /sdcard/{PHONE_UPLOAD_DIR}")
    adb.shell(f"mkdir -p /sdcard/{PHONE_UPLOAD_DIR}")
    remote_names: list[str] = []
    for path in image_paths:
        if not path.is_file():
            raise FileNotFoundError(path)
        stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        remote_name = f"{stamp}_{path.name}"
        remote = f"/sdcard/{PHONE_UPLOAD_DIR}/{remote_name}"
        adb.push(path, remote)
        adb.media_scan(f"{PHONE_UPLOAD_DIR}/{remote_name}")
        remote_names.append(remote_name)
    return remote_names


def _open_sound_and_use(device: Any, sound_id: str, steps: list[str]) -> None:
    uri = sound_deep_link_uri(sound_id)
    adb = AdbClient(device_id=settings.tiktok_adb_device_id or None)
    adb.ensure_device()
    package = adb.open_deep_link(uri)
    steps.append(f"Opened {uri} via {package}")
    time.sleep(3.0)

    label = _click_first_text(device, USE_SOUND_LABELS, timeout=12.0)
    if not label:
        raise RuntimeError(
            "Could not find 'Use this sound' on the Mackenzie page. "
            "Open TikTok manually once and confirm the button label."
        )
    steps.append(f"Tapped '{label}'")


def _open_gallery_multi_select(device: Any, count: int, steps: list[str]) -> None:
    gallery = _click_first_text(device, GALLERY_LABELS, timeout=10.0)
    if gallery:
        steps.append(f"Tapped gallery control '{gallery}'")
        time.sleep(1.5)

    multi = device(text="Select multiple")
    if multi.exists(timeout=3.0):
        if not device(className="android.widget.CheckBox", checked=True).exists(timeout=0.5):
            multi.click()
            steps.append("Enabled multi-select")
        time.sleep(0.5)

    # Pick newest images in gallery grid (we just pushed them).
    recycler = device(className="androidx.recyclerview.widget.RecyclerView")
    if not recycler.exists(timeout=8.0):
        raise RuntimeError("Gallery grid not found after opening upload picker.")

    for index in range(count):
        cell = recycler.child(index=index)
        if cell.exists(timeout=3.0):
            cell.click()
            steps.append(f"Selected image slot {index + 1}")
            time.sleep(0.3)

    next_label = _click_first_text(device, NEXT_LABELS, timeout=8.0)
    if not next_label:
        raise RuntimeError("Could not find Next after selecting images.")
    steps.append(f"Tapped '{next_label}'")


def _ensure_photo_mode(device: Any, steps: list[str]) -> None:
    label = _click_first_text(device, PHOTO_MODE_LABELS, timeout=4.0)
    if label:
        steps.append(f"Switched to photo mode via '{label}'")


def _set_aigc_disclosure(device: Any, steps: list[str]) -> None:
    if not settings.tiktok_declare_aigc:
        return
    more = device(text="More options")
    if more.exists(timeout=3.0):
        more.click()
        time.sleep(0.8)
    label = _click_first_text(device, AIGC_LABELS, timeout=4.0)
    if label:
        steps.append(f"Opened disclosure '{label}'")
        toggle = device(textContains="AI")
        if toggle.exists(timeout=2.0):
            toggle.click()
            steps.append("Toggled AI disclosure")
        done = _click_first_text(device, ("Done", "Save", "OK"), timeout=3.0)
        if done:
            steps.append(f"Closed disclosure via '{done}'")


def _finalize_post(device: Any, *, draft: bool, steps: list[str]) -> None:
    labels = DRAFT_LABELS if draft else POST_LABELS
    label = _click_first_text(device, labels, timeout=10.0)
    if not label:
        raise RuntimeError(f"Could not find post button ({', '.join(labels)}).")
    steps.append(f"Tapped '{label}'")

    confirm = _click_first_text(device, ("Post Now", "Confirm"), timeout=3.0)
    if confirm:
        steps.append(f"Confirmed via '{confirm}'")


def post_carousel_with_sound(
    image_paths: list[Path],
    *,
    sound_id: str | None = None,
    device_id: str | None = None,
    draft: bool = False,
    dry_run: bool = False,
) -> CarouselPostResult:
    """
    Post a photo carousel starting from a TikTok sound deep link (Lead 3).

    images: 2+ local PNG/JPG paths (bubble wrap = 2 slides).
    """
    paths = [Path(p) for p in image_paths]
    if len(paths) < 2:
        raise ValueError("Carousel requires at least 2 images")

    sid = (sound_id or settings.tiktok_bubble_wrap_sound_id or MACKENZIE_SOUND_ID).strip()
    dev = (device_id or settings.tiktok_adb_device_id or "").strip()
    uri = sound_deep_link_uri(sid)
    steps: list[str] = []

    if dry_run:
        steps.append(f"DRY RUN — would open {uri}")
        steps.append(f"DRY RUN — would push {len(paths)} images to /sdcard/{PHONE_UPLOAD_DIR}")
        steps.append("DRY RUN — would tap Use this sound → gallery → photo mode → post")
        return CarouselPostResult(
            ok=True,
            message="Dry run — no device actions performed",
            steps=steps,
            device_id=dev,
            sound_id=sid,
        )

    adb = AdbClient(device_id=dev or None)
    serial = adb.ensure_device()
    u2 = _require_u2()
    device = u2.connect(serial)

    _push_carousel_images(adb, paths)
    steps.append(f"Pushed {len(paths)} images to phone")

    _open_sound_and_use(device, sid, steps)
    time.sleep(2.0)

    _open_gallery_multi_select(device, len(paths), steps)
    time.sleep(1.5)

    _ensure_photo_mode(device, steps)

    next_after_edit = _click_first_text(device, NEXT_LABELS, timeout=8.0)
    if next_after_edit:
        steps.append(f"Editor next: '{next_after_edit}'")
        time.sleep(1.0)

    _set_aigc_disclosure(device, steps)
    _finalize_post(device, draft=draft, steps=steps)

    return CarouselPostResult(
        ok=True,
        message="Carousel posted via ADB (sound-first flow)",
        steps=steps,
        device_id=serial,
        sound_id=sid,
    )


def post_bubble_wrap_via_adb(
    slide1: Path,
    slide2: Path,
    *,
    device_id: str | None = None,
    draft: bool = False,
    dry_run: bool = False,
) -> CarouselPostResult:
    """Bubble wrap: Mackenzie sound + 2-slide carousel."""
    try:
        return post_carousel_with_sound(
            [slide1, slide2],
            sound_id=MACKENZIE_SOUND_ID,
            device_id=device_id,
            draft=draft,
            dry_run=dry_run,
        )
    except (AdbError, RuntimeError, FileNotFoundError, ValueError) as exc:
        return CarouselPostResult(
            ok=False,
            message=str(exc),
            device_id=(device_id or settings.tiktok_adb_device_id or ""),
            sound_id=MACKENZIE_SOUND_ID,
        )


def status_dict() -> dict[str, Any]:
    """Quick check for owner/agent — adb devices + deep link target."""
    adb = AdbClient(device_id=settings.tiktok_adb_device_id or None)
    try:
        serials = adb.devices()
    except (AdbError, FileNotFoundError) as exc:
        return {
            "adb_available": False,
            "devices": [],
            "mackenzie_uri": mackenzie_deep_link_uri(),
            "error": str(exc),
        }
    return {
        "adb_available": True,
        "devices": serials,
        "configured_device": settings.tiktok_adb_device_id or "",
        "mackenzie_sound_id": MACKENZIE_SOUND_ID,
        "mackenzie_uri": mackenzie_deep_link_uri(),
    }
