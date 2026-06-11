from pathlib import Path

from shorts_bot.memory.store import MemoryStore
from shorts_bot.production.pack import build_production_pack
from shorts_bot.production.turboscribe_parser import label_from_seconds, parse_turboscribe


SAMPLE = """
0:00 Imagine waking up at 2 a.m. and not reaching for your phone.
0:07 Just absolute darkness.
0:15 You listen for the quiet.
0:23 One small breath. You're still here.
"""


def test_label_from_seconds():
    assert label_from_seconds(0) == "00.00"
    assert label_from_seconds(7) == "00.07"
    assert label_from_seconds(65) == "01.05"


def test_parse_turboscribe():
    segs = parse_turboscribe(SAMPLE)
    assert len(segs) == 4
    assert segs[0].start_seconds == 0
    assert segs[1].start_seconds == 7
    assert "darkness" in segs[1].text.lower()


def test_build_production_pack(tmp_path: Path):
    store = MemoryStore(tmp_path / "test.db")
    d = store.save_draft(
        topic="sleep at 3am",
        script="Full script here.",
        hook="Stop scrolling.",
        help_angle="Helps insomniacs.",
        quality_notes="ok",
    )
    pack = build_production_pack(
        store,
        draft_id=d.id,
        turboscribe_text=SAMPLE,
        output_root=tmp_path / "out",
    )
    assert pack.image_count == 4
    assert (pack.output_dir / "manifest.json").exists()
    assert (pack.output_dir / "prompts" / "00.07.txt").exists()
    assert (pack.output_dir / "CAPCUT_TIMELINE.md").exists()
