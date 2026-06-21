from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

from shorts_bot.config import settings
from shorts_bot.learning.workflow import WorkflowDefinition, WorkflowStep
from shorts_bot.learning.workflow_runner import run_daily_invideo_workflow
from shorts_bot.memory.store import MemoryStore


def _minimal_workflow() -> WorkflowDefinition:
    return WorkflowDefinition(
        id="daily_invideo",
        version=1,
        steps=[
            WorkflowStep("pick_topic"),
            WorkflowStep(
                "build_brief",
                params={
                    "hook_template": "Is {product} worth paying for? Honest 30s verdict.",
                    "verdict_hint": "Pay, Skip, or Wait",
                },
            ),
            WorkflowStep("save_draft"),
            WorkflowStep("invideo_project"),
            WorkflowStep("invideo_render", params={"wait_render_sec": 1}),
            WorkflowStep("youtube_upload"),
        ],
    )


def test_daily_cli_upload_flag_passes_explicit_upload(monkeypatch):
    from shorts_bot.production import daily_cli

    seen: dict[str, object] = {}

    def fake_run_invideo_daily(**kwargs):
        seen.update(kwargs)
        return SimpleNamespace(summary="done")

    monkeypatch.setattr(daily_cli, "run_invideo_daily", fake_run_invideo_daily)
    monkeypatch.setattr(
        sys,
        "argv",
        ["daily_cli", "--topic", "ChatGPT Plus", "--upload", "--wait-render-sec", "3"],
    )

    daily_cli.main()

    assert seen["topic"] == "ChatGPT Plus"
    assert seen["upload"] is True
    assert seen["wait_render_sec"] == 3


def test_daily_workflow_keeps_mp4_path_when_upload_fails(tmp_path: Path, monkeypatch):
    data_dir = tmp_path / "data"
    monkeypatch.setattr(settings, "data_dir", data_dir)
    store = MemoryStore(tmp_path / "shorts.db")

    def fake_generate_from_prompt(*args, **kwargs):
        return SimpleNamespace(project_url="https://ai.invideo.io/project/test")

    def fake_ship(project_url, dest, **kwargs):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"0" * 60_000)
        return dest

    def fake_upload(*args, **kwargs):
        raise RuntimeError("YouTube upload not authorized")

    monkeypatch.setattr(
        "shorts_bot.learning.workflow_runner.generate_from_prompt",
        fake_generate_from_prompt,
    )
    monkeypatch.setattr("shorts_bot.invideo.ship_cli.ship", fake_ship)
    monkeypatch.setattr("shorts_bot.production.upload_canonical_cli.upload_canonical", fake_upload)

    result = run_daily_invideo_workflow(
        store,
        topic="ChatGPT Plus honest AI product review",
        upload=True,
        wait_render_sec=1,
        workflow=_minimal_workflow(),
    )

    assert result.ok is False
    assert result.video_path is not None
    assert result.video_path.is_file()
    assert any("MP4 kept for retry" in message for message in result.messages)
