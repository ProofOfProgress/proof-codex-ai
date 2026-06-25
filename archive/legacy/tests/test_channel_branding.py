from shorts_bot.youtube.channel_branding import BrandApplyResult, YouTubeChannelBranding


def test_brand_apply_requires_fields(tmp_path):
    operator = YouTubeChannelBranding(tmp_path / "profile")
    result = operator.apply(channel_name=None, description=None)
    assert result.status == "failed"


def test_result_for_human():
    result = BrandApplyResult(
        status="applied",
        message="Channel branding applied.",
        name_updated=True,
        description_updated=True,
        channel_name="Soft Continuity",
    )
    text = result.for_human()
    assert "applied" in text
    assert "Display name updated" in text
    assert "Description updated" in text
