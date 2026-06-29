"""Generate multiple bubble-wrap slide sets — store only, no TikTok/Zernio."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.tiktok_shop.bubble_wrap import BubbleWrapResult, generate_bubble_wrap_slides

# Varied subjects for volume tests — Module 2 carousel format (2 slides each).
DEFAULT_BUBBLE_SUBJECTS: tuple[str, ...] = (
    "frog",
    "duck",
    "cake",
    "soccer jersey",
    "teddy bear",
    "pizza slice",
    "sneakers",
    "watermelon",
    "guitar",
    "smartphone",
)


@dataclass(frozen=True)
class BubbleBatchItem:
    subject: str
    account: str
    slide1: str
    slide2: str
    preview_mp4: str | None
    model: str
    hook_text: str
    ok: bool
    error: str = ""


@dataclass(frozen=True)
class BubbleBatchResult:
    manifest_path: Path
    total: int
    succeeded: int
    failed: int
    items: tuple[BubbleBatchItem, ...]


def batch_output_root() -> Path:
    path = settings.data_dir / "bubble_wrap" / "batches"
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_subjects(*, count: int, subjects: list[str] | None) -> list[str]:
    if subjects:
        picked = [s.strip() for s in subjects if s.strip()]
    else:
        picked = list(DEFAULT_BUBBLE_SUBJECTS)
    if count < 1:
        raise ValueError("count must be >= 1")
    if len(picked) >= count:
        return picked[:count]
    # Cycle defaults if owner asks for more than the default list length.
    out = list(picked)
    defaults = list(DEFAULT_BUBBLE_SUBJECTS)
    idx = 0
    while len(out) < count:
        out.append(defaults[idx % len(defaults)])
        idx += 1
    return out


def run_bubble_batch(
    *,
    count: int = 10,
    subjects: list[str] | None = None,
    force: bool = False,
    preview: bool = True,
) -> BubbleBatchResult:
    """Generate N bubble slide pairs. Files only — never posts."""
    subject_list = resolve_subjects(count=count, subjects=subjects)
    items: list[BubbleBatchItem] = []

    for i, subject in enumerate(subject_list, start=1):
        account = f"batch_{i:02d}_{subject.lower().replace(' ', '_')[:24]}"
        try:
            result: BubbleWrapResult = generate_bubble_wrap_slides(
                subject=subject,
                account=account,
                preview=preview,
                force=force,
            )
            items.append(
                BubbleBatchItem(
                    subject=subject,
                    account=account,
                    slide1=str(result.slide1),
                    slide2=str(result.slide2),
                    preview_mp4=str(result.preview_mp4) if result.preview_mp4 else None,
                    model=result.model,
                    hook_text=result.hook_text,
                    ok=True,
                )
            )
        except Exception as exc:  # noqa: BLE001 — batch continues on one failure
            items.append(
                BubbleBatchItem(
                    subject=subject,
                    account=account,
                    slide1="",
                    slide2="",
                    preview_mp4=None,
                    model="",
                    hook_text="",
                    ok=False,
                    error=str(exc),
                )
            )

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest_path = batch_output_root() / f"batch_{stamp}.json"
    succeeded = sum(1 for it in items if it.ok)
    payload = {
        "created_at": datetime.now(UTC).isoformat(),
        "store_only": True,
        "posted": False,
        "count_requested": count,
        "count_ok": succeeded,
        "count_failed": len(items) - succeeded,
        "items": [asdict(it) for it in items],
    }
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return BubbleBatchResult(
        manifest_path=manifest_path,
        total=len(items),
        succeeded=succeeded,
        failed=len(items) - succeeded,
        items=tuple(items),
    )
