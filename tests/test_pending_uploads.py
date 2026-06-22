from datetime import datetime, timedelta, timezone
from pathlib import Path

from shorts_bot.config import settings
from shorts_bot.youtube import pending_uploads


def test_process_keeps_missing_mp4_queued(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "database_path", tmp_path / "shorts_bot.db")

    missing = tmp_path / "production" / "draft_9" / "final_short.mp4"
    pending_uploads.enqueue_upload(
        draft_id=9,
        video_path=missing,
        publish_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        topic="Claude Code",
    )

    results = pending_uploads.process_due_uploads(force=True)

    assert results == [
        {
            "draft_id": 9,
            "ok": False,
            "message": f"Missing MP4, keeping queued: {missing.resolve()}",
            "retry": True,
        }
    ]
    queued = pending_uploads.load_queue()
    assert len(queued) == 1
    assert queued[0].draft_id == 9
    assert queued[0].video_file() == missing.resolve()
    assert queued[0].video_exists() is False
