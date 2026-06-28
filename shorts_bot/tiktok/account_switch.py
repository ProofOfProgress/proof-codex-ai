"""TikTok in-app account switcher (Account center) via UI automation."""

from __future__ import annotations

import time
from typing import Any

SWITCH_ACCOUNT_LABELS = (
    "Switch account",
    "Add account",
    "Manage accounts",
)
PROFILE_LABELS = ("Profile", "Me")


def switch_tiktok_account(device: Any, switch_label: str, steps: list[str]) -> None:
    """
    Switch to an account shown in TikTok's account center.

    switch_label: text shown in the switcher (nickname, @handle, or partial match).
    """
    label = (switch_label or "").strip()
    if not label:
        raise ValueError("switch_label is required for account switching")

    if device(text="Profile").click_exists(timeout=8.0):
        steps.append("Opened Profile tab")
    elif device(text="Me").click_exists(timeout=3.0):
        steps.append("Opened Me tab")
    else:
        raise RuntimeError("Could not open Profile tab for account switch.")
    time.sleep(1.5)

    # Account center: tap header / current username to open account list.
    opened = False
    for candidate in (
        device(className="android.widget.TextView", textContains=label),
        device(textContains=label),
    ):
        if candidate.exists(timeout=2.0):
            candidate.click()
            opened = True
            steps.append(f"Tapped account list entry matching '{label}'")
            break

    if not opened:
        for switch_text in SWITCH_ACCOUNT_LABELS:
            if device(text=switch_text).click_exists(timeout=2.0):
                steps.append(f"Opened '{switch_text}'")
                opened = True
                break
        if not opened:
            # Tap top profile row (common layout).
            profile_row = device(className="android.widget.LinearLayout", clickable=True)
            if profile_row.exists(timeout=2.0):
                profile_row.click()
                steps.append("Tapped profile header row")
                opened = True

    time.sleep(1.0)

    if not device(textContains=label).click_exists(timeout=8.0):
        raise RuntimeError(
            f"Could not select account '{label}' in account center. "
            "Set tiktok_switch_label in accounts.json to match TikTok's display name."
        )
    steps.append(f"Switched to account '{label}'")
    time.sleep(2.5)
