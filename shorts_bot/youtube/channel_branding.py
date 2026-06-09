from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.youtube.studio import goto_channel_customization, open_studio

BrandStatus = Literal["applied", "partial", "needs_human", "not_logged_in", "failed"]


@dataclass
class BrandApplyResult:
    status: BrandStatus
    message: str
    name_updated: bool = False
    description_updated: bool = False
    channel_name: str | None = None
    screenshot_path: str | None = None
    current_url: str | None = None

    def for_human(self) -> str:
        lines = [f"Status: {self.status}", self.message]
        if self.channel_name:
            lines.append(f"Channel name target: {self.channel_name}")
        if self.name_updated:
            lines.append("✓ Display name updated")
        if self.description_updated:
            lines.append("✓ Description updated")
        if self.current_url:
            lines.append(f"URL: {self.current_url}")
        if self.screenshot_path:
            lines.append(f"Screenshot: {self.screenshot_path}")
        return "\n".join(lines)


class YouTubeChannelBranding:
    """Apply channel display name and description in YouTube Studio."""

    PUBLISH_LABELS = ("Publish", "Save", "Done", "Update")

    def __init__(
        self,
        profile_dir: Path,
        *,
        headless: bool = False,
        screenshot_dir: Path | None = None,
    ) -> None:
        self.profile_dir = profile_dir
        self.headless = headless
        self.screenshot_dir = screenshot_dir or profile_dir / "screenshots"
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def apply_from_brand_file(self) -> BrandApplyResult:
        brand = ChannelBrand()
        fields = brand.youtube_fields()
        if not fields.channel_name and not fields.description:
            return BrandApplyResult(
                status="failed",
                message="No channel name or description in channel/brand/youtube_copy.txt",
            )
        return self.apply(
            channel_name=fields.channel_name or None,
            description=fields.description or None,
        )

    def apply(
        self,
        *,
        channel_name: str | None = None,
        description: str | None = None,
    ) -> BrandApplyResult:
        channel_name = (channel_name or "").strip() or None
        description = (description or "").strip() or None
        if not channel_name and not description:
            return BrandApplyResult(status="failed", message="Provide channel_name and/or description.")

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return BrandApplyResult(
                status="failed",
                message="Playwright not installed. Run: pip install playwright && playwright install chromium",
            )

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(self.profile_dir),
                headless=self.headless,
                viewport={"width": 1280, "height": 900},
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = context.pages[0] if context.pages else context.new_page()
            result = BrandApplyResult(status="failed", message="Brand apply did not run.")
            try:
                studio = open_studio(page)
                if not studio.logged_in:
                    return BrandApplyResult(
                        status="not_logged_in",
                        message=(
                            "Not logged into YouTube. Sign in once in the browser profile, "
                            "then run apply again."
                        ),
                        screenshot_path=self._screenshot(page, "brand_not_logged_in"),
                        current_url=page.url,
                    )

                channel_id = goto_channel_customization(page)
                if not channel_id:
                    return BrandApplyResult(
                        status="needs_human",
                        message=(
                            "Could not open channel customization. "
                            "Open Studio → Customization → Basic info manually."
                        ),
                        screenshot_path=self._screenshot(page, "brand_no_channel_id"),
                        current_url=page.url,
                    )

                name_ok = False
                desc_ok = False
                if channel_name:
                    name_ok = self._fill_channel_name(page, channel_name)
                if description:
                    desc_ok = self._fill_description(page, description)

                if name_ok or desc_ok:
                    self._try_publish(page)
                    time.sleep(2)

                if name_ok and (desc_ok or not description):
                    status: BrandStatus = "applied"
                    msg = "Channel branding applied in YouTube Studio."
                elif name_ok or desc_ok:
                    status = "partial"
                    parts = []
                    if name_ok:
                        parts.append("display name")
                    if desc_ok:
                        parts.append("description")
                    msg = f"Updated {' and '.join(parts)}. Check Studio for anything still missing."
                else:
                    status = "needs_human"
                    msg = (
                        "Could not find name/description fields. "
                        "Paste from channel/brand/youtube_copy.txt in Studio → Customization → Basic info."
                    )

                return BrandApplyResult(
                    status=status,
                    message=msg,
                    name_updated=name_ok,
                    description_updated=desc_ok,
                    channel_name=channel_name,
                    screenshot_path=self._screenshot(page, "brand_apply"),
                    current_url=page.url,
                )
            except Exception as exc:  # noqa: BLE001
                return BrandApplyResult(
                    status="failed",
                    message=f"Brand apply error: {exc}",
                    screenshot_path=self._screenshot(page, "brand_error"),
                    current_url=page.url,
                )
            finally:
                context.close()

    def _fill_channel_name(self, page, channel_name: str) -> bool:
        selectors = [
            'input[aria-label*="name" i]',
            'input[placeholder*="name" i]',
            "ytcp-channel-editing-channel-name input",
            "#channel-name-input input",
        ]
        for sel in selectors:
            loc = page.locator(sel).first
            if not loc.count():
                continue
            try:
                loc.click(timeout=3000)
                loc.fill(channel_name, timeout=5000)
                time.sleep(0.5)
                if self._name_is_taken(page):
                    return False
                return True
            except Exception:
                continue
        return False

    def _fill_description(self, page, description: str) -> bool:
        selectors = [
            'textarea[aria-label*="description" i]',
            'ytcp-channel-editing-description textarea',
            "#description-textarea",
            'div#description-container textarea',
            "textarea",
        ]
        for sel in selectors:
            loc = page.locator(sel).first
            if not loc.count():
                continue
            try:
                if not loc.is_visible():
                    continue
                loc.click(timeout=3000)
                loc.fill(description, timeout=8000)
                time.sleep(0.5)
                return True
            except Exception:
                continue
        return False

    def _name_is_taken(self, page) -> bool:
        taken = (
            "already taken",
            "not available",
            "isn't available",
            "is not available",
            "already in use",
            "choose another",
        )
        for phrase in taken:
            try:
                loc = page.get_by_text(re.compile(phrase, re.I))
                if loc.count() and loc.first.is_visible():
                    return True
            except Exception:
                continue
        return False

    def _try_publish(self, page) -> None:
        for label in self.PUBLISH_LABELS:
            try:
                page.get_by_role("button", name=re.compile(label, re.I)).first.click(timeout=3000)
                time.sleep(1)
                return
            except Exception:
                try:
                    page.get_by_text(re.compile(f"^{label}$", re.I)).first.click(timeout=2000)
                    time.sleep(1)
                    return
                except Exception:
                    continue

    def _screenshot(self, page, label: str) -> str:
        path = self.screenshot_dir / f"{label}_{int(time.time())}.png"
        try:
            page.screenshot(path=str(path), full_page=True)
            return str(path)
        except Exception:
            return ""
