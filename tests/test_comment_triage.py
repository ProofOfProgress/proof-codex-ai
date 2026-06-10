from shorts_bot.comments.triage import triage_comment
from shorts_bot.memory.extensions import MemoryExtensions
from shorts_bot.memory.store import MemoryStore


def test_auto_reply_thanks():
    r = triage_comment("This helped me so much, thank you!")
    assert r.decision == "auto"


def test_human_crisis():
    r = triage_comment("I don't want to live anymore, please help")
    assert r.decision == "human"


def test_human_medical():
    r = triage_comment("Should I take medication for my anxiety?")
    assert r.decision == "human"


def test_spam_link():
    r = triage_comment("Check out my channel https://spam.example")
    assert r.decision == "spam"


def test_topic_request_auto():
    r = triage_comment("Can you do the minute before Sunday dread?")
    assert r.decision == "auto"


def test_comment_action_storage(tmp_path):
    mem = MemoryExtensions(MemoryStore(tmp_path / "c.db"))
    mem.record_comment_action(
        comment_id="abc",
        video_id="vid1",
        author="user",
        original_text="thanks",
        decision="auto_replied",
        reply_text="glad it helped",
    )
    assert mem.comment_already_handled("abc")
    assert mem.count_comments_needing_human() == 0

    mem.record_comment_action(
        comment_id="xyz",
        video_id="vid1",
        author="user",
        original_text="I'm struggling",
        decision="needs_human",
        reason="serious",
    )
    assert mem.count_comments_needing_human() == 1
    assert mem.list_comments_needing_human()[0]["youtube_comment_id"] == "xyz"
