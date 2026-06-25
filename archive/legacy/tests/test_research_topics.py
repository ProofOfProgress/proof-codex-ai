from shorts_bot.agents.research_topics import (
    AI_VIDEO_RESEARCH_TOPICS,
    research_topic_batch,
    user_excludes_cosy_topics,
    user_wants_ai_video_research,
)
from shorts_bot.agents.work_loop import _pick_next_topic, WorkSession


def test_user_wants_ai_video_research():
    msg = "take 1h to research AI video prompting only — not cosy topics"
    assert user_wants_ai_video_research(msg)
    assert user_excludes_cosy_topics(msg)


def test_research_topic_batch_ai_video_not_cosy():
    msg = "take 1h to research AI video prompting only — not cosy topics"
    batch = research_topic_batch(msg, 3)
    assert all(t.startswith("AI video prompting:") for t in batch)
    assert not any("minute before" in t for t in batch)


def test_research_topic_batch_default_cosy():
    batch = research_topic_batch("plan cosy topics this week", 2)
    assert not batch[0].startswith("AI video prompting:")


def test_pick_next_topic_uses_ai_video_queue():
    session = WorkSession(
        budget_seconds=3600,
        user_request="take 1h to research AI video prompting only — not cosy topics",
    )
    topic = _pick_next_topic(session, 0)
    assert topic in AI_VIDEO_RESEARCH_TOPICS
