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
    assert "Shorts Bot" in r.text
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


def test_learned_endpoint():
    r = client.get("/api/learned")
    assert r.status_code == 200
    assert "content" in r.json()
