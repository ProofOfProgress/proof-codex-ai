"""Single choke point — every upload path must call this (or upload is blocked in code)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.pre_publish_gate import enforce_before_upload, run_pre_publish_gate

ContentType = Literal["video", "carousel", "affiliate"]


def require_pre_publish(
    content_type: ContentType,
    *,
    video_path: Path | None = None,
    image_paths: list[Path] | None = None,
    caption: str = "",
    title: str = "",
    product: str = "",
    shop_account_id: str = "",
    tier: str | None = None,
    skip: bool = False,
) -> None:
    """Raise RuntimeError if gate fails. No-op when skip or PRE_PUBLISH_ALLOW_BYPASS=true."""
    if skip or settings.pre_publish_allow_bypass:
        return
    slide1 = image_paths[0] if image_paths and len(image_paths) >= 1 else None
    slide2 = image_paths[1] if image_paths and len(image_paths) >= 2 else None
    report = run_pre_publish_gate(
        content_type,
        tier=tier,
        video_path=video_path,
        slide1=slide1,
        slide2=slide2,
        caption=caption,
        title=title,
        product=product,
        account_id=shop_account_id,
    )
    enforce_before_upload(report)
