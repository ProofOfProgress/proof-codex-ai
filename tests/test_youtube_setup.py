from shorts_bot.youtube.channel_setup import ChannelSetupResult, YouTubeChannelSetup


def test_setup_requires_channel_name(tmp_path):
    operator = YouTubeChannelSetup(tmp_path / "profile")
    result = operator.run(channel_name="")
    assert result.status == "failed"


def test_result_for_human():
    result = ChannelSetupResult(
        status="needs_human",
        message="Complete phone verification.",
        current_url="https://accounts.google.com",
    )
    assert "needs_human" in result.for_human()
    assert "phone" in result.for_human()
