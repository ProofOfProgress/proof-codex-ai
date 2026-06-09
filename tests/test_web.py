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
