from shorts_bot.comments.reply import _offline_reply


def test_offline_reply_topic():
    text = _offline_reply("Can you cover the minute before a hard conversation?")
    assert "queue" in text.lower() or "minute" in text.lower()


def test_offline_reply_thanks():
    text = _offline_reply("Thank you this helped")
    assert "glad" in text.lower() or "landed" in text.lower()
