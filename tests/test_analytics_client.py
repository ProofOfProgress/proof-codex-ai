"""YouTube analytics client — no fake Shorts swipe metrics."""

from unittest.mock import MagicMock, patch

from shorts_bot.youtube.analytics_client import fetch_video_metrics


def test_fetch_video_metrics_does_not_fake_swipe():
    fake_resp = {
        "columnHeaders": [
            {"name": "video"},
            {"name": "views"},
            {"name": "likes"},
            {"name": "comments"},
            {"name": "averageViewPercentage"},
        ],
        "rows": [["abc123", 100, 5, 1, 72.5]],
    }
    mock_analytics = MagicMock()
    mock_analytics.reports.return_value.query.return_value.execute.return_value = fake_resp

    with patch("shorts_bot.youtube.analytics_client._services", return_value=(None, mock_analytics)):
        rows = fetch_video_metrics(days=7, max_videos=5)

    assert len(rows) == 1
    assert rows[0]["average_view_percentage"] == 72.5
    assert rows[0]["swipe_source"] == "unavailable"
    assert "viewed_vs_swiped_away" not in rows[0]
