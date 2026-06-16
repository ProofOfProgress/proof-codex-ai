"""Tests for shared 3D workspace API."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from shorts_bot.web.app import app

client = TestClient(app)


def test_workspace_page(tmp_path, monkeypatch):
    from shorts_bot.config import settings

    pack = tmp_path / "production" / "draft_7"
    pack.mkdir(parents=True)
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    r = client.get("/workspace/draft/7")
    assert r.status_code == 200
    assert "shared 3D" in r.text
    assert "workspace3d.js" in r.text or "initWorkspace" in r.text


def test_scene_layout_get_put_default(tmp_path, monkeypatch):
    from shorts_bot.config import settings

    pack = tmp_path / "production" / "draft_5"
    pack.mkdir(parents=True)
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    r0 = client.get("/api/workspace/draft/5/scene")
    assert r0.status_code == 200
    assert "creature" in r0.json()

    patch = {
        "creature": {"location": [1.0, -8.0, 0.0], "rotation": [0, 0, 0], "scale": [1, 1, 1.4]},
        "camera": {"location": [0, 2, 1.65], "rotation": [1.5, 0, 3.14], "lens": 24},
    }
    r1 = client.put("/api/workspace/draft/5/scene", json=patch)
    assert r1.status_code == 200
    assert r1.json()["creature"]["location"] == [1.0, -8.0, 0.0]

    saved = pack / "scene_layout.json"
    assert saved.is_file()
    data = json.loads(saved.read_text())
    assert data["creature"]["location"][0] == 1.0

    r2 = client.get("/api/workspace/draft/5/scene/default")
    assert r2.status_code == 200
    assert r2.json()["creature"]["location"] == [0.0, -7.5, 0.0]


def test_scene_layout_module(tmp_path):
    from shorts_bot.production.blender.scene_layout import (
        creature_wave_positions,
        load_scene_layout,
        save_scene_layout,
    )

    pack = tmp_path / "draft_3"
    pack.mkdir()
    save_scene_layout(
        pack,
        load_scene_layout(pack, draft_id=3),
        updated_by="test",
    )
    layout = load_scene_layout(pack, draft_id=3)
    start, end, scale = creature_wave_positions(layout)
    assert start == [0.0, -7.5, 0.0]
    assert end[1] == -6.0

    layout["creature"]["location"] = [2.0, -9.0, 0.0]
    start2, end2, _ = creature_wave_positions(layout)
    assert start2 == [2.0, -9.0, 0.0]
    assert end2[1] == -7.5
