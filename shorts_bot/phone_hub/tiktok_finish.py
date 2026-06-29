"""Automated TikTok inbox draft finish — Mackenzie (bubble) + product link (affiliate)."""

from __future__ import annotations

import time

from shorts_bot.phone_hub import ui as phone_ui
from shorts_bot.phone_hub.coords import get_coord

MACKENZIE_SOUND_URL = "https://www.tiktok.com/music/original-sound-7418286946344340256"
MACKENZIE_SEARCH = "Mackenzie"

# Seconds to wait after navigation taps (TikTok UI load)
STEP_PAUSE_S = 1.2


def _pause() -> None:
    time.sleep(STEP_PAUSE_S)


def _tap_coord(slot: str, key: str, *, serial: str) -> bool:
    point = get_coord(slot, key)
    if not point:
        return False
    phone_ui.tap(point[0], point[1], serial=serial)
    return True


def tap_any(
    *labels: str,
    serial: str,
    slot: str = "",
    coord_key: str = "",
    partial: bool = True,
) -> bool:
    """Try uiautomator text match, then calibrated coordinate."""
    for label in labels:
        if label and phone_ui.tap_by_text(label, serial=serial, partial=partial):
            return True
    if slot and coord_key:
        return _tap_coord(slot, coord_key, serial=serial)
    return False


def open_tiktok_url(url: str, *, serial: str) -> bool:
    """Open URL in TikTok app (sound page, etc.)."""
    phone_ui.open_view_url(url, serial=serial, package="com.zhiliaoapp.musically")
    _pause()
    return True


def dismiss_overlays(*, serial: str) -> None:
    """Best-effort dismiss common dialogs."""
    for label in ("Allow", "While using the app", "OK", "Not now", "Skip", "Close"):
        if phone_ui.tap_by_text(label, serial=serial, partial=True):
            _pause()
            break


def open_inbox(*, serial: str, slot: str) -> tuple[bool, str]:
    dismiss_overlays(serial=serial)
    if tap_any("Inbox", serial=serial, slot=slot, coord_key="nav_inbox"):
        _pause()
        return True, "opened Inbox"
    return False, "open_inbox: Inbox not found — calibrate nav_inbox in ui_coords.json"


def open_latest_draft(*, serial: str, slot: str) -> tuple[bool, str]:
    for label in ("Drafts", "Draft", "System notifications"):
        if phone_ui.tap_by_text(label, serial=serial, partial=True):
            _pause()
            break
    if tap_any("Draft", serial=serial, slot=slot, coord_key="draft_row", partial=True):
        _pause()
        return True, "opened draft"
    if _tap_coord(slot, "draft_row", serial=serial):
        _pause()
        return True, "opened draft via coords"
    return False, "open_draft: no draft row — calibrate draft_row in ui_coords.json"


def add_mackenzie_sound(*, serial: str, slot: str) -> tuple[bool, str]:
    """Attach Mackenzie sound to inbox draft."""
    # Path A: sound page deeplink → Use this sound (returns to draft with sound)
    open_tiktok_url(MACKENZIE_SOUND_URL, serial=serial)
    dismiss_overlays(serial=serial)
    if tap_any(
        "Use this sound",
        "Use sound",
        "Use this music",
        serial=serial,
        slot=slot,
        coord_key="sound_use",
    ):
        _pause()
        return True, "Mackenzie via sound page"

    # Path B: draft editor → Sounds → search Mackenzie
    if not tap_any("Sounds", "Add sound", "Sound", serial=serial, slot=slot, coord_key="draft_sounds"):
        return False, "add_mackenzie_sound: Sounds button not found"
    _pause()
    if tap_any("Search", serial=serial, slot=slot, coord_key="sound_search"):
        _pause()
        phone_ui.input_text(MACKENZIE_SEARCH, serial=serial)
        phone_ui.keyevent("66", serial=serial)  # ENTER
        _pause()
    if tap_any("Mackenzie", "original sound", serial=serial, partial=True):
        _pause()
        if tap_any("Use", serial=serial, slot=slot, coord_key="sound_use", partial=True):
            _pause()
            return True, "Mackenzie via search"
    return False, "add_mackenzie_sound: could not select Mackenzie — calibrate ui_coords.json"


def add_product_link(*, serial: str, slot: str, product_name: str = "") -> tuple[bool, str]:
    """Add TikTok Shop product link (orange cart) to affiliate inbox draft."""
    if not tap_any("Add link", "Add Link", "Link", serial=serial, slot=slot, coord_key="add_link"):
        return False, "add_product_link: Add link not found"
    _pause()
    if not tap_any("Products", "Product", serial=serial, slot=slot, coord_key="products_tab"):
        return False, "add_product_link: Products tab not found"
    _pause()

    query = (product_name or "").strip()
    if query:
        if tap_any("Search", serial=serial, slot=slot, coord_key="product_search"):
            _pause()
            phone_ui.input_text(query[:40], serial=serial)
            phone_ui.keyevent("66", serial=serial)
            _pause()
        if phone_ui.tap_by_text(query[:20], serial=serial, partial=True):
            _pause()
        elif not tap_any(query[:15], serial=serial, partial=True):
            if not _tap_coord(slot, "product_pick_first", serial=serial):
                return False, f"add_product_link: product {query!r} not in showcase"
            _pause()
    elif not _tap_coord(slot, "product_pick_first", serial=serial):
        return False, "add_product_link: no product_name and product_pick_first unset"
    else:
        _pause()

    if tap_any("Add", "Done", "Confirm", serial=serial, slot=slot, coord_key="product_confirm"):
        _pause()
        return True, f"product linked: {query or 'first showcase item'}"
    return False, "add_product_link: confirm Add not found"


def publish_draft(*, serial: str, slot: str) -> tuple[bool, str]:
    if tap_any("Post", "Publish", serial=serial, slot=slot, coord_key="post_button"):
        _pause()
        if tap_any("Post", "Publish now", serial=serial, partial=True):
            _pause()
        return True, "published"
    return False, "publish: Post button not found — calibrate post_button in ui_coords.json"
