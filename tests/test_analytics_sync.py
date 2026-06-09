from pathlib import Path
from unittest.mock import patch

from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore
from shorts_bot.training.proposer import ImprovementProposer
from shorts_bot.youtube.google_auth import auth_status
from shorts_bot.youtube.sync import AnalyticsSync


SAMPLE_METRICS = [
    {
        "video_id": "abc123",
        "video_label": "Bad Short",
        "title": "Bad Short",
        "views": 1000,
        "likes": 10,
        "comments": 2,
        "retention_rate": 25.0,
        "viewed_vs_swiped_away": 30.0,
    },
    {
        "video_id": "def456",
        "video_label": "Good Short",
        "title": "Good Short",
        "views": 5000,
        "likes": 400,
        "comments": 50,
        "retention_rate": 70.0,
        "viewed_vs_swiped_away": 78.0,
    },
]


def _sync(tmp_path: Path) -> AnalyticsSync:
    mem = MemoryExtensions(MemoryStore(tmp_path / "sync.db"))
    return AnalyticsSync(mem, ImprovementProposer(mem, client=None))


def test_sync_not_ready_without_credentials(tmp_path: Path):
    with patch("shorts_bot.youtube.sync.auth_status", return_value={"credentials_configured": False, "token_saved": False, "ready": False}):
        result = _sync(tmp_path).run()
    assert not result.ok
    assert "TOMORROW" in result.message


def test_sync_not_ready_without_token(tmp_path: Path):
    with patch("shorts_bot.youtube.sync.auth_status", return_value={"credentials_configured": True, "token_saved": False, "ready": False}):
        result = _sync(tmp_path).run()
    assert not result.ok
    assert "auth_cli" in result.message


def test_sync_scores_and_proposes(tmp_path: Path):
    ready = {"credentials_configured": True, "token_saved": True, "ready": True}
    with (
        patch("shorts_bot.youtube.sync.auth_status", return_value=ready),
        patch("shorts_bot.youtube.sync.fetch_video_metrics", return_value=SAMPLE_METRICS),
        patch("shorts_bot.youtube.sync.enrich_titles", side_effect=lambda m: m),
    ):
        sync = _sync(tmp_path)
        result = sync.run()

    assert result.ok
    assert result.videos_scored == 2
    assert result.improvements_created >= 1
    assert len(result.rewards) == 2
    pending = sync.memory.list_improvements(status="pending")
    assert pending
    assert sync.memory.get_training_config("last_analytics_sync")


def test_sync_caps_improvements(tmp_path: Path):
    many = []
    for i in range(10):
        many.append(
            {
                "video_id": f"v{i}",
                "video_label": f"Video {i}",
                "title": f"Video {i}",
                "views": 100,
                "likes": 1,
                "comments": 0,
                "retention_rate": 20.0 + i,
                "viewed_vs_swiped_away": 25.0 + i,
            }
        )
    ready = {"credentials_configured": True, "token_saved": True, "ready": True}
    with (
        patch("shorts_bot.youtube.sync.auth_status", return_value=ready),
        patch("shorts_bot.youtube.sync.fetch_video_metrics", return_value=many),
        patch("shorts_bot.youtube.sync.enrich_titles", side_effect=lambda m: m),
    ):
        result = _sync(tmp_path).run()

    assert result.ok
    assert result.improvements_created <= 3


def test_auth_status_structure():
    status = auth_status()
    assert "credentials_configured" in status
    assert "token_saved" in status
    assert "ready" in status
