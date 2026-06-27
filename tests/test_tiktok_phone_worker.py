"""Tests for phone queue + worker (free local automation path)."""

from pathlib import Path

from shorts_bot.tiktok.phone_queue import (
    enqueue_job,
    load_queue,
    pending_jobs,
    queue_path,
    update_job,
)
from shorts_bot.tiktok.phone_worker import run_pending_jobs
from shorts_bot.tiktok.sounds import MACKENZIE_SOUND_ID


def test_enqueue_and_pending(tmp_path: Path, monkeypatch):
    qpath = tmp_path / "phone_queue.json"
    monkeypatch.setattr("shorts_bot.config.settings.phone_queue_path", qpath)

    s1 = tmp_path / "a.png"
    s2 = tmp_path / "b.png"
    s1.write_bytes(b"a")
    s2.write_bytes(b"b")

    job = enqueue_job(
        account_id="bubble_proof",
        switch_label="proofofprogresss",
        slide1=s1,
        slide2=s2,
        sound_id=MACKENZIE_SOUND_ID,
        path=qpath,
    )
    assert job.id.startswith("phone_")
    assert len(pending_jobs(qpath)) == 1


def test_worker_dry_run(tmp_path: Path, monkeypatch):
    qpath = tmp_path / "phone_queue.json"
    monkeypatch.setattr("shorts_bot.config.settings.phone_queue_path", qpath)

    s1 = tmp_path / "hook.png"
    s2 = tmp_path / "cta.png"
    s1.write_bytes(b"1")
    s2.write_bytes(b"2")

    enqueue_job(
        account_id="bubble_isaac",
        switch_label="Isaac",
        slide1=s1,
        slide2=s2,
        sound_id=MACKENZIE_SOUND_ID,
        path=qpath,
    )

    result = run_pending_jobs(dry_run=True)
    assert result.processed == 1
    assert result.succeeded == 1
    jobs = load_queue(qpath)
    assert jobs[0].status == "done"


def test_update_job_marks_failed(tmp_path: Path, monkeypatch):
    qpath = tmp_path / "phone_queue.json"
    monkeypatch.setattr("shorts_bot.config.settings.phone_queue_path", qpath)

    s1 = tmp_path / "x.png"
    s2 = tmp_path / "y.png"
    s1.write_bytes(b"x")
    s2.write_bytes(b"y")

    job = enqueue_job(
        account_id="bubble_msbyte",
        switch_label="Ms. Byte",
        slide1=s1,
        slide2=s2,
        sound_id=MACKENZIE_SOUND_ID,
        path=qpath,
    )
    updated = update_job(job.id, status="failed", error="test")
    assert updated is not None
    assert updated.status == "failed"
