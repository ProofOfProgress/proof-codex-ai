"""Bubble wrap slideshow helpers (0→1k followers phase)."""

from __future__ import annotations

from pathlib import Path

DEFAULT_HASHTAGS = "#asmr #satisfying #bubblewrap #fyp"
MACKENZIE_SOUND_URL = "https://www.tiktok.com/music/original-sound-7418286946344340256"

# Owner catalog pairs — slide 1 (hook) + slide 2 (CTA)
SAMPLE_PAIRS: list[tuple[str, str, str]] = [
    ("bubble wrap7.png", "bubble wrap10.png", "FROG BUBBLE WRAP ASMR"),
    ("bubble wrap1.png", "bubble wrap3.png", "POP USA BUBBLE WRAP"),
    ("bubble wrap5.png", "bubble wrap3.png", "POP THE BUBBLES"),
]


def samples_dir() -> Path:
    from shorts_bot.config import settings

    return settings.data_dir / "research" / "course" / "_media" / "bubble_wrap" / "samples"


def default_caption(*, extra: str = "") -> str:
    parts = [p.strip() for p in (extra, DEFAULT_HASHTAGS) if p.strip()]
    return " ".join(parts)


def validate_slides(slide1: Path, slide2: Path) -> list[str]:
    """Return validation errors (empty = OK)."""
    errors: list[str] = []
    for label, path in (("slide1", slide1), ("slide2", slide2)):
        if not path.exists():
            errors.append(f"{label} missing: {path}")
            continue
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            errors.append(f"{label} must be PNG/JPEG/WebP: {path}")
        if path.stat().st_size > 20 * 1024 * 1024:
            errors.append(f"{label} exceeds 20 MB: {path}")
    if slide1.resolve() == slide2.resolve():
        errors.append("slide1 and slide2 must be different files")
    return errors


def resolve_sample_pair(name: str) -> tuple[Path, Path, str] | None:
    """Find a catalog pair by partial filename or title match."""
    needle = name.strip().lower()
    base = samples_dir()
    for hook_file, cta_file, title in SAMPLE_PAIRS:
        if needle in hook_file.lower() or needle in title.lower():
            return base / hook_file, base / cta_file, title
    return None
