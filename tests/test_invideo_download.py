from pathlib import Path

from shorts_bot.invideo.download import (
    ProjectState,
    detect_project_state,
    read_project_url,
    _looks_like_video_url,
)


def test_detect_login():
    body = "Welcome to invideo AI\nContinue with Google\n0%"
    assert detect_project_state(body) == ProjectState.LOGIN_REQUIRED


def test_detect_ready():
    body = "Home\nLibrary\nCreate New\nEdit\nDownload\nEdit & Download"
    assert detect_project_state(body) == ProjectState.READY


def test_detect_generate_pending():
    body = "Home\nCreate New\nGenerate\n·\n2 credits"
    assert detect_project_state(body) == ProjectState.GENERATE_PENDING


def test_detect_generating():
    body = "Home\nCreate New\n45%\nGenerate still running"
    assert detect_project_state(body) == ProjectState.GENERATING


def test_read_project_url_from_draft(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "shorts_bot.invideo.download.draft_pack_dir",
        lambda draft_id: tmp_path / f"draft_{draft_id}",
    )
    pack = tmp_path / "draft_3"
    pack.mkdir()
    (pack / "invideo_project.url").write_text("https://ai.invideo.io/ai-mcp-video?video=abc\n")
    url = read_project_url(draft_id=3)
    assert "video=abc" in url


def test_video_url_filter():
    assert not _looks_like_video_url("https://ai.invideo.io/film_grain.mp4")
    assert _looks_like_video_url("https://cdn.example.com/exports/render-123.mp4")
