from shorts_bot.learning.workflow_runner import invideo_recovery_lines


def test_invideo_recovery_lines_are_draft_specific():
    lines = invideo_recovery_lines(12, "https://ai.invideo.io/ai-mcp-video?video=test")

    joined = "\n".join(lines)
    assert "Recovery draft #12" in joined
    assert "python3 -m shorts_bot.invideo.handoff_cli" in joined
    assert "python3 -m shorts_bot.invideo.ship_cli --draft-id 12" in joined
    assert "python3 -m shorts_bot.invideo.fetch_url_cli --draft-id 12" in joined
