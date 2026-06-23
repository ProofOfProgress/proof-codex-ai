"""Tests for Ms. Byte status post generator."""

from pathlib import Path

from shorts_bot.social.status_posts import build_status_posts, generate_status_post_image


def test_generate_status_post_image(tmp_path: Path):
    out = tmp_path / "test_status.png"
    generate_status_post_image(
        pose_file="pose_hook_surprise.png",
        headline="New lesson dropping soon.",
        subline="Grok · $30 · live Twitter",
        out_path=out,
    )
    assert out.is_file()
    assert out.stat().st_size > 50_000


def test_build_status_posts():
    posts = build_status_posts(limit=1)
    assert len(posts) == 1
    assert posts[0].image_path.is_file()
    assert posts[0].caption
