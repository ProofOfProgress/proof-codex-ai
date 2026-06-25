from fastapi.testclient import TestClient

from shorts_bot.web.app import app

client = TestClient(app)


def test_manager_jobs_list():
    r = client.get("/api/manager/jobs")
    assert r.status_code == 200
    assert "jobs" in r.json()


def test_manager_run_sync_short():
    r = client.post(
        "/api/manager/run",
        json={"message": "manager: say hello in one sentence", "force_async": False},
    )
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data
    assert data.get("async") is False or "manager" in data
