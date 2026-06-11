from shorts_bot.production.pipeline_integrity import (
    clear_render_artifacts,
    content_digest,
    content_stamp_stale,
    write_content_stamp,
)


def test_content_stamp_detects_script_change(tmp_path):
    pack = tmp_path / "draft_1"
    pack.mkdir()
    write_content_stamp(pack, hook="Hook A", script="Script A")
    assert not content_stamp_stale(pack, hook="Hook A", script="Script A")
    assert content_stamp_stale(pack, hook="Hook B", script="Script B")


def test_clear_render_artifacts(tmp_path):
    pack = tmp_path / "draft_1"
    clips = pack / "clips"
    clips.mkdir(parents=True)
    (clips / "00.01.mp4").write_bytes(b"x" * 20_000)
    (pack / "voiceover.mp3").write_bytes(b"audio")
    removed = clear_render_artifacts(pack)
    assert any("clips" in r for r in removed)
    assert not (clips / "00.01.mp4").exists()


def test_digest_stable():
    assert content_digest("a", "b") == content_digest("a", "b")
