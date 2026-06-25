from pathlib import Path

from shorts_bot.production.video_qc import run_video_qc


def test_video_qc_missing_file(tmp_path: Path):
    report = run_video_qc(tmp_path / "nope.mp4")
    assert not report.passed
    assert report.issues
