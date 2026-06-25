from shorts_bot.youtube.analytics_review import _review_one


def test_review_one_flags_low_watch():
    row = {
        "video_label": "abc123",
        "metrics": {
            "title": "Test Product Review",
            "views": 50,
            "likes": 0,
            "comments": 0,
            "average_view_percentage": 38,
        },
    }
    r = _review_one(row)
    assert r.verdict in ("bad", "mixed")
    assert any("watch" in b.lower() for b in r.bads)


def test_review_one_good_metrics():
    row = {
        "video_label": "xyz789",
        "metrics": {
            "title": "Grok Review",
            "views": 800,
            "likes": 40,
            "comments": 5,
            "average_view_percentage": 62,
        },
    }
    r = _review_one(row)
    assert r.verdict == "good"
    assert r.goods
