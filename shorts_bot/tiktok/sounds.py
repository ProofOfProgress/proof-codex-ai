"""TikTok sound IDs and deep-link URIs for phone automation."""

from __future__ import annotations

# Bubble wrap growth track — original user sound (not CML).
MACKENZIE_SOUND_ID = "7418286946344340256"
MACKENZIE_SOUND_URL = (
    f"https://www.tiktok.com/music/original-sound-{MACKENZIE_SOUND_ID}"
)
MACKENZIE_SEARCH_HINT = "original sound Mackenzie"

TIKTOK_PACKAGES = (
    "com.zhiliaoapp.musically",  # global TikTok
    "com.ss.android.ugc.trill",  # some regions
)


def sound_deep_link_uri(sound_id: str) -> str:
    """Android intent URI — opens the sound page inside the TikTok app."""
    sid = (sound_id or "").strip()
    if not sid.isdigit():
        raise ValueError(f"Invalid TikTok sound id: {sound_id!r}")
    return f"tiktok://music/{sid}"


def mackenzie_deep_link_uri() -> str:
    return sound_deep_link_uri(MACKENZIE_SOUND_ID)
