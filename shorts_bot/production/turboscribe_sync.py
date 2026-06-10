"""TurboScribe Whale transcription — browser automation (paid Unlimited session)."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from pathlib import Path

from shorts_bot.config import settings


@dataclass
class TurboScribeResult:
    transcript_text: str
    source: str
    message: str


def _format_segments_for_parser(lines: list[tuple[float, str]]) -> str:
    """Build text parse_turboscribe understands: 0:07 words..."""
    out: list[str] = []
    for start, text in lines:
        m = int(start // 60)
        s = int(start % 60)
        out.append(f"{m}:{s:02d} {text.strip()}")
    return "\n".join(out)


def _parse_srt(srt_text: str) -> str:
    """Convert SRT to timestamp lines for our parser."""
    blocks = re.split(r"\n\s*\n", srt_text.strip())
    lines: list[tuple[float, str]] = []
    for block in blocks:
        rows = [r.strip() for r in block.splitlines() if r.strip()]
        if len(rows) < 2:
            continue
        time_row = rows[1] if "-->" in rows[1] else rows[0]
        if "-->" not in time_row:
            continue
        start_raw = time_row.split("-->")[0].strip()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+)", start_raw)
        if not m:
            continue
        start = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4)) / 1000
        text_rows = rows[2:] if "-->" in rows[1] else rows[1:]
        text = " ".join(text_rows).strip()
        if text:
            lines.append((start, text))
    return _format_segments_for_parser(lines)


def transcribe_with_playwright(audio_path: Path, *, mode: str = "whale", timeout_sec: int = 600) -> TurboScribeResult:
    """
    Upload voiceover to TurboScribe (saved browser login) and return timestamped transcript.

    Requires TurboScribe Unlimited + logged-in profile at data/browser_profile.
    """
    from playwright.sync_api import sync_playwright

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio not found: {audio_path}")

    audio_path = audio_path.resolve()
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(settings.browser_profile_dir),
            headless=True,
            viewport={"width": 1280, "height": 900},
            accept_downloads=True,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://turboscribe.ai/u", wait_until="domcontentloaded", timeout=120000)
        time.sleep(2)

        body = (page.inner_text("body") or "").lower()
        if "sign in" in body or "log in" in body:
            context.close()
            raise RuntimeError(
                "TurboScribe not logged in. Run: python3 -m shorts_bot.login_handoff --only turboscribe"
            )

        # Upload audio — multiple selectors (TurboScribe UI changes often)
        uploaded = False
        for sel in (
            'input[type="file"]',
            'input[accept*="audio"]',
            'input[accept*="video"]',
        ):
            loc = page.locator(sel)
            if loc.count():
                try:
                    loc.first.set_input_files(str(audio_path), timeout=15000)
                    uploaded = True
                    break
                except Exception:
                    continue
        if not uploaded:
            try:
                with page.expect_file_chooser(timeout=15000) as fc_info:
                    page.get_by_role("button", name=re.compile(r"upload|transcribe|new", re.I)).first.click(
                        timeout=8000
                    )
                fc_info.value.set_files(str(audio_path))
                uploaded = True
            except Exception:
                pass
        if not uploaded:
            context.close()
            raise RuntimeError("TurboScribe upload control not found — check login at turboscribe.ai/u")
        time.sleep(2)

        # Select transcription mode (Whale = max accuracy)
        mode_lower = mode.lower()
        for label in (mode_lower.capitalize(), mode_lower.upper(), "Whale"):
            try:
                btn = page.get_by_text(label, exact=False)
                if btn.count():
                    btn.first.click(timeout=3000)
                    break
            except Exception:
                continue

        # Start transcription
        for label in ("Transcribe", "Start", "Upload", "Submit"):
            try:
                btn = page.get_by_role("button", name=re.compile(label, re.I))
                if btn.count() and btn.first.is_visible():
                    btn.first.click(timeout=5000)
                    break
            except Exception:
                continue

        deadline = time.time() + timeout_sec
        transcript = ""
        while time.time() < deadline:
            time.sleep(5)
            try:
                page.reload(wait_until="domcontentloaded", timeout=60000)
            except Exception:
                pass
            time.sleep(2)

            # Try download SRT / TXT
            for link_text in ("Download", "Export", "SRT", ".srt", "TXT"):
                try:
                    link = page.get_by_text(re.compile(link_text, re.I))
                    if link.count():
                        with page.expect_download(timeout=15000) as dl_info:
                            link.first.click(timeout=5000)
                        download = dl_info.value
                        suffix = Path(download.suggested_filename or "out.txt").suffix.lower()
                        dest = audio_path.parent / f"_turboscribe_dl{suffix}"
                        download.save_as(dest)
                        raw = dest.read_text(encoding="utf-8", errors="replace")
                        if suffix == ".srt" or "-->" in raw:
                            transcript = _parse_srt(raw)
                        else:
                            transcript = raw
                        dest.unlink(missing_ok=True)
                        if transcript.strip():
                            break
                except Exception:
                    continue
            if transcript.strip():
                break

            # Scrape visible transcript lines from page
            scraped = page.inner_text("body") or ""
            time_lines = re.findall(
                r"(?:^|\n)\s*(\d{1,2}:\d{2}(?::\d{2})?)\s+(.+?)(?=\n\s*\d{1,2}:\d{2}|\Z)",
                scraped,
                re.S,
            )
            if len(time_lines) >= 2:
                transcript = "\n".join(f"{t} {txt.strip()}" for t, txt in time_lines)
                break

            if "complete" in scraped.lower() or "finished" in scraped.lower() or "download" in scraped.lower():
                continue

        context.close()

    if not transcript.strip():
        raise RuntimeError("TurboScribe did not return a timestamped transcript in time.")

    out_path = audio_path.parent / "turboscribe_transcript.txt"
    out_path.write_text(transcript.strip() + "\n", encoding="utf-8")
    return TurboScribeResult(
        transcript_text=transcript.strip(),
        source="turboscribe_whale",
        message=f"TurboScribe ({mode}) sync saved → {out_path.name}",
    )


def transcribe_audio(audio_path: Path) -> TurboScribeResult:
    """Transcribe voiceover — TurboScribe if enabled, else read cached file."""
    cached = audio_path.parent / "turboscribe_transcript.txt"
    if cached.exists() and not settings.turboscribe_always_fresh:
        text = cached.read_text(encoding="utf-8").strip()
        if text:
            return TurboScribeResult(
                transcript_text=text,
                source="cache",
                message=f"Using cached {cached.name}",
            )

    if not settings.use_turboscribe_sync:
        raise RuntimeError("TurboScribe sync disabled (USE_TURBOSCRIBE_SYNC=false).")

    return transcribe_with_playwright(audio_path, mode=settings.turboscribe_mode)
