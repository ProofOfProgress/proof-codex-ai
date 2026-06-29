"""Post queue — videos ready to ship per account."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from shorts_bot.config import settings


def queue_path() -> Path:
    return settings.data_dir / "tiktok_shop" / "queue.json"


def load_queue() -> list[dict]:
    path = queue_path()
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def save_queue(rows: list[dict]) -> None:
    path = queue_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")


def pending_posts(*, account_id: str | None = None) -> list[dict]:
    rows = [r for r in load_queue() if r.get("status", "pending") == "pending"]
    if account_id:
        rows = [r for r in rows if not r.get("account_id") or r.get("account_id") == account_id]
    return rows


def _assert_qc_passed_before_enqueue(
    video_path: Path,
    *,
    caption: str,
    product: str,
    account_id: str,
) -> dict:
    """Run Module 1 QC inline — raises RuntimeError if blocked."""
    from shorts_bot.tiktok_shop.module1_qc import load_qc_report, qc_report_stale_for_video, run_module1_qc

    if not settings.module1_require_qc_before_enqueue:
        return {}

    if not video_path.is_file():
        raise RuntimeError(f"Video not found: {video_path}")

    existing = load_qc_report(video_path)
    if (
        existing
        and existing.get("passed")
        and not qc_report_stale_for_video(video_path, existing)
        and str(existing.get("caption_checked") or "") == (caption or "")
    ):
        return {
            "qc_passed": True,
            "qc_checked_at": existing.get("checked_at"),
            "qc_report_path": str(settings.data_dir / "tiktok_shop" / "module1_qc" / f"{video_path.stem}.json"),
            "qc_reused_report": True,
        }

    report = run_module1_qc(
        video_path,
        caption=caption,
        product=product,
        account_id=account_id,
    )
    report_path = settings.data_dir / "tiktok_shop" / "module1_qc" / f"{video_path.stem}.json"
    if report_path.is_file():
        try:
            payload = json.loads(report_path.read_text(encoding="utf-8"))
            payload["caption_checked"] = caption
            report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except json.JSONDecodeError:
            pass

    if not report.passed:
        detail = "; ".join(report.violations[:5])
        raise RuntimeError(f"Module 1 QC BLOCKED — not queued: {detail}")

    return {
        "qc_passed": True,
        "qc_checked_at": datetime.now(timezone.utc).isoformat(),
        "qc_report_path": str(report_path),
        "qc_reused_report": False,
    }


def enqueue_video(
    *,
    video_path: str,
    product: str,
    caption: str,
    account_id: str = "",
    skip_qc: bool = False,
) -> int:
    path = Path(video_path)
    qc_meta: dict = {}
    if not skip_qc:
        qc_meta = _assert_qc_passed_before_enqueue(
            path,
            caption=caption,
            product=product,
            account_id=account_id,
        )

    rows = load_queue()
    row = {
        "video_path": video_path,
        "product": product,
        "caption": caption,
        "account_id": account_id,
        "status": "pending",
    }
    row.update(qc_meta)
    rows.append(row)
    save_queue(rows)
    return len(rows) - 1
