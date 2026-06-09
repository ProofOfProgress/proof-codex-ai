from pathlib import Path

from shorts_bot.memory.store import MemoryStore


def test_draft_review_flow(tmp_path: Path):
    store = MemoryStore(tmp_path / "test.db")
    draft = store.save_draft(
        topic="sleep",
        script="A" * 50,
        hook="Stop scrolling if you wake up tired.",
        help_angle="Helps night-shift workers fall asleep faster with one pre-bed routine.",
    )
    assert draft.status == "pending"

    reviewed = store.review_draft(draft.id, "rejected", "Too vague")
    assert reviewed.status == "rejected"
    assert store.stats()["rejected"] == 1
