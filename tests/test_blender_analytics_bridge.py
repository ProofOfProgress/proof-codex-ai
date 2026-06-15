"""YouTube analytics ↔ Blender grind bridge."""

from __future__ import annotations

from shorts_bot.production.blender.analytics_bridge import youtube_reward_to_visual_issues
from shorts_bot.rewards.engine import RewardResult


def test_youtube_punish_maps_to_visual_issues():
    r = RewardResult(
        video_label="test short",
        score=-0.5,
        verdict="punish",
        reason="Weak hook — only 42% viewed vs swiped",
        metrics={},
        diagnosis="Retention drop — pacing issue",
    )
    issues = youtube_reward_to_visual_issues(r)
    assert any("face" in i.lower() for i in issues)
    assert any("mouth" in i.lower() or "retention" in " ".join(issues).lower() for i in issues)


def test_youtube_reward_keeps_mouth_framing():
    r = RewardResult(
        video_label="winner",
        score=0.6,
        verdict="reward",
        reason="Strong swipe-away survival",
        metrics={},
        diagnosis="Good retention",
    )
    issues = youtube_reward_to_visual_issues(r)
    assert any("mouth" in i.lower() for i in issues)
