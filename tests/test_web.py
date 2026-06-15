import subprocess

import pytest
from fastapi.testclient import TestClient

from shorts_bot.web.app import app

client = TestClient(app)


def test_status_endpoint():
    r = client.get("/api/status")
    assert r.status_code == 200
    assert "openai" in r.json()


def test_home_page():
    r = client.get("/")
    assert r.status_code == 200
    assert "Peripheral" in r.text
    assert "Sync YouTube Analytics" in r.text


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_youtube_status():
    r = client.get("/api/youtube/status")
    assert r.status_code == 200
    data = r.json()
    assert "ready" in data


def test_login_status():
    r = client.get("/api/login-status")
    assert r.status_code == 200
    data = r.json()
    assert "services" in data
    assert data["total"] >= 4


def test_youtube_sync_graceful():
    r = client.post("/api/youtube/sync")
    assert r.status_code == 200
    data = r.json()
    assert "ok" in data
    assert "message" in data


def test_dev_api_create_and_list():
    r = client.post("/api/dev", json={"title": "Test task", "description": "Do something"})
    assert r.status_code == 200
    assert "id" in r.json()
    r2 = client.get("/api/dev")
    assert r2.status_code == 200
    assert "pending" in r2.json()


def test_preview_draft_page_404():
    r = client.get("/preview/draft/99999")
    assert r.status_code == 404


def test_preview_draft_page_lists_videos(tmp_path, monkeypatch):
    from shorts_bot.config import settings

    pack = tmp_path / "production" / "draft_42"
    clips = pack / "clips"
    clips.mkdir(parents=True)
    # Minimal valid-ish mp4 header stub — use real tiny file from test fixture
    tiny = tmp_path / "tiny.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64:d=1",
            "-c:v", "libx264", "-movflags", "+faststart", str(tiny),
        ],
        capture_output=True,
        check=False,
    )
    if tiny.is_file():
        (clips / "blender_part_wave.mp4").write_bytes(tiny.read_bytes())
    else:
        pytest.skip("ffmpeg not available for preview test")
    (pack / "preview_frames").mkdir()
    (pack / "preview_frames" / "wave_0s.png").write_bytes(b"\x89PNG\r\n")

    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(
        "shorts_bot.production.blender.preview_validate.is_browser_playable_mp4",
        lambda p, **_: p.is_file() and p.stat().st_size > 50,
    )
    r = client.get("/preview/draft/42")
    assert r.status_code == 200
    assert "blender_part_wave.mp4" in r.text
    assert "wave_0s.png" in r.text


def test_preview_preflight_still(tmp_path, monkeypatch):
    from shorts_bot.config import settings

    pack = tmp_path / "production" / "draft_7"
    preflight = pack / "preflight"
    preflight.mkdir(parents=True)
    (preflight / "peak_still.jpg").write_bytes(b"\xff\xd8\xff" + b"\x00" * 200)
    (preflight / "preflight_qc.json").write_text(
        '{"passed": false, "score": 4.5, "issues": ["face too small"]}', encoding="utf-8"
    )
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    r = client.get("/preview/draft/7?preflight=1")
    assert r.status_code == 200
    assert "peak_still.jpg" in r.text
    assert "FAIL" in r.text
    assert "4.5" in r.text
    img = client.get("/preview/draft/7/preflight/peak_still.jpg")
    assert img.status_code == 200

