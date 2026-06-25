from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from shorts_bot.brand.loader import ChannelBrand
from shorts_bot.brand.assets import BANNER_PATH, PROFILE_PATH
from shorts_bot.youtube.studio import (
    goto_channel_branding_images,
    goto_channel_customization,
    open_studio,
    _skip_unsupported_warning,
)

BrandStatus = Literal["applied", "partial", "needs_human", "not_logged_in", "failed"]


@dataclass
class BrandApplyResult:
    status: BrandStatus
    message: str
    name_updated: bool = False
    description_updated: bool = False
    profile_updated: bool = False
    banner_updated: bool = False
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
        if self.profile_updated:
            lines.append("✓ Profile picture updated")
        if self.banner_updated:
            lines.append("✓ Banner image updated")
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

    def upload_profile_only(self, profile_path: Path) -> BrandApplyResult:
        """Studio-only profile picture upload (API cannot set avatar)."""
        if not profile_path.exists():
            return BrandApplyResult(status="failed", message=f"Profile image not found: {profile_path}")
        return self.apply(profile_path=profile_path)

    def apply_from_brand_file(self, *, profile_path: Path | None = None) -> BrandApplyResult:
        brand = ChannelBrand()
        fields = brand.youtube_fields()
        if not fields.channel_name and not fields.description:
            return BrandApplyResult(
                status="failed",
                message="No channel name or description in channel/brand/youtube_copy.txt",
            )
        banner_path = BANNER_PATH if BANNER_PATH.exists() else None
        return self.apply(
            channel_name=fields.channel_name or None,
            description=fields.description or None,
            profile_path=profile_path or (PROFILE_PATH if PROFILE_PATH.exists() else None),
            banner_path=banner_path,
        )

    def apply(
        self,
        *,
        channel_name: str | None = None,
        description: str | None = None,
        profile_path: Path | None = None,
        banner_path: Path | None = None,
    ) -> BrandApplyResult:
        channel_name = (channel_name or "").strip() or None
        description = (description or "").strip() or None
        has_image = (profile_path and profile_path.exists()) or (banner_path and banner_path.exists())
        if not channel_name and not description and not has_image:
            return BrandApplyResult(status="failed", message="Provide channel_name, description, and/or image paths.")

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
                if channel_id:
                    page.goto(
                        f"https://studio.youtube.com/channel/{channel_id}/editing/profile",
                        wait_until="networkidle",
                        timeout=90000,
                    )
                    time.sleep(2)
                    _skip_unsupported_warning(page)
                    self._dismiss_blocking_dialogs(page)
                if not channel_id and (channel_name or description):
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
                if channel_name and channel_id:
                    name_ok = self._fill_channel_name(page, channel_name)
                if description and channel_id:
                    desc_ok = self._fill_description(page, description)

                profile_ok = False
                banner_ok = False
                need_branding = (profile_path and profile_path.exists()) or (
                    banner_path and banner_path.exists()
                )
                if need_branding:
                    branding_cid = goto_channel_branding_images(page, channel_id)
                    if branding_cid:
                        if profile_path and profile_path.exists():
                            profile_ok = self._upload_profile_picture(page, profile_path)
                        if banner_path and banner_path.exists():
                            banner_ok = self._upload_banner_image(page, banner_path)

                if name_ok or desc_ok or profile_ok or banner_ok:
                    self._dismiss_blocking_dialogs(page)
                    self._try_publish(page)
                    time.sleep(2)

                self._try_identity_verification(page)
                self._dismiss_blocking_dialogs(page)

                if (name_ok or desc_ok or profile_ok or banner_ok) and not self._verify_modal_visible(page):
                    if self._try_publish(page):
                        time.sleep(2)
                        name_ok = name_ok and self._name_matches(page, channel_name)
                        desc_ok = desc_ok or self._publish_succeeded(page)

                if (name_ok or not channel_name) and (desc_ok or not description) and (
                    profile_ok or not profile_path
                ) and (banner_ok or not banner_path):
                    status: BrandStatus = "applied"
                    msg = "Channel branding applied in YouTube Studio."
                elif name_ok or desc_ok or profile_ok or banner_ok:
                    status = "partial"
                    parts = []
                    if name_ok:
                        parts.append("display name")
                    if desc_ok:
                        parts.append("description")
                    if profile_ok:
                        parts.append("profile picture")
                    if banner_ok:
                        parts.append("banner")
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
                    profile_updated=profile_ok,
                    banner_updated=banner_ok,
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

    def _upload_profile_picture(self, page, profile_path: Path) -> bool:
        try:
            changes = page.get_by_role("button", name=re.compile(r"^Change$", re.I))
            if changes.count() >= 2:
                changes.nth(1).click(timeout=5000)
            else:
                page.get_by_text(re.compile(r"picture", re.I)).first.click(timeout=3000)
                changes.first.click(timeout=5000)
            time.sleep(1)
            page.locator('input[type="file"]').first.set_input_files(
                str(profile_path.resolve()), timeout=8000
            )
            time.sleep(3)
            self._dismiss_crop_dialog(page)
            return True
        except Exception:
            pass
        return False

    def _upload_banner_image(self, page, banner_path: Path) -> bool:
        try:
            changes = page.get_by_role("button", name=re.compile(r"^Change$", re.I))
            if changes.count():
                changes.first.click(timeout=5000)
                time.sleep(1)
                page.locator('input[type="file"]').first.set_input_files(
                    str(banner_path.resolve()), timeout=8000
                )
                time.sleep(3)
                self._dismiss_crop_dialog(page)
                return True
        except Exception:
            pass
        return False

    def _dismiss_crop_dialog(self, page) -> None:
        for label in ("Done", "Save", "Apply"):
            if self._click_enabled_button(page, re.compile(f"^{label}$", re.I)):
                time.sleep(0.5)
                return

    def _dismiss_blocking_dialogs(self, page) -> None:
        for label in ("Cancel", "Close", "Done", "Save"):
            self._click_enabled_button(page, re.compile(f"^{label}$", re.I))

    def _click_enabled_button(self, page, pattern: re.Pattern[str]) -> bool:
        btn = page.get_by_role("button", name=pattern)
        for i in range(btn.count()):
            b = btn.nth(i)
            try:
                if b.is_visible() and b.is_enabled():
                    b.click(timeout=2000)
                    return True
            except Exception:
                continue
        return False

    def _fill_channel_name(self, page, channel_name: str) -> bool:
        inputs = page.locator("input[type=text], input:not([type])")
        for i in range(inputs.count()):
            val = inputs.nth(i).input_value() or ""
            if val and len(val) < 80 and not val.startswith("http"):
                try:
                    inputs.nth(i).fill(channel_name, timeout=5000)
                    time.sleep(0.5)
                    if self._name_matches(page, channel_name) and not self._name_is_taken(page):
                        return True
                except Exception:
                    continue
        selectors = [
            'input[aria-label*="name" i]',
            "ytcp-channel-editing-channel-name input",
        ]
        for sel in selectors:
            loc = page.locator(sel).first
            if not loc.count():
                continue
            try:
                loc.fill(channel_name, timeout=5000)
                time.sleep(0.5)
                if self._name_is_taken(page):
                    return False
                return self._name_matches(page, channel_name)
            except Exception:
                continue
        return False

    def _name_matches(self, page, channel_name: str | None) -> bool:
        if not channel_name:
            return False
        inputs = page.locator("input[type=text], input:not([type])")
        for i in range(inputs.count()):
            if inputs.nth(i).input_value().strip() == channel_name.strip():
                return True
        return False

    def _fill_description(self, page, description: str) -> bool:
        selectors = [
            'textarea[aria-label*="description" i]',
            'ytcp-channel-editing-description textarea',
            "#description-textarea",
            'div#description-container textarea',
            '[contenteditable="true"][aria-label*="description" i]',
            'ytcp-form-input-container#description-container [contenteditable="true"]',
            "textarea",
        ]
        for sel in selectors:
            loc = page.locator(sel).first
            if not loc.count():
                continue
            try:
                if not loc.is_visible():
                    continue
                loc.click(force=True, timeout=5000)
                try:
                    loc.fill(description, timeout=8000)
                except Exception:
                    page.keyboard.press("Control+A")
                    page.keyboard.type(description, delay=5)
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

    def _verify_modal_visible(self, page) -> bool:
        try:
            loc = page.get_by_text(re.compile(r"verify it'?s you", re.I))
            return bool(loc.count() and loc.first.is_visible())
        except Exception:
            return False

    def _try_identity_verification(self, page) -> None:
        if not self._verify_modal_visible(page):
            return
        try:
            page.get_by_role("button", name=re.compile(r"^next$", re.I)).first.click(timeout=3000)
            time.sleep(2)
        except Exception:
            pass

    def _publish_succeeded(self, page) -> bool:
        try:
            toast = page.get_by_text(re.compile(r"changes published", re.I))
            return bool(toast.count() and toast.first.is_visible())
        except Exception:
            return False

    def _try_publish(self, page) -> bool:
        pub = page.locator('button[aria-label="Publish"]:not([disabled])')
        if pub.count():
            try:
                pub.first.click(timeout=5000)
                time.sleep(1)
                return True
            except Exception:
                pass
        return self._click_enabled_button(page, re.compile(r"^Publish$", re.I))

    def _screenshot(self, page, label: str) -> str:
        path = self.screenshot_dir / f"{label}_{int(time.time())}.png"
        try:
            page.screenshot(path=str(path), full_page=True)
            return str(path)
        except Exception:
            return ""
