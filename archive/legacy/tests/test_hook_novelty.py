from shorts_bot.drafts.hook_novelty import (
    CHANNEL_KNOWN_HOOKS,
    check_hook_novelty,
    hook_similarity,
)


def test_mirror_hooks_detected_as_duplicates():
    a = "You blinked at the mirror — your reflection blinked one second later."
    b = "You blinked — your reflection blinked one second later."
    assert hook_similarity(a, b) >= 0.55


def test_different_pillars_are_novel():
    a = "Your own voice called your name from the basement — you hadn't gone down yet."
    b = CHANNEL_KNOWN_HOOKS[0]
    assert hook_similarity(a, b) < 0.55
    assert check_hook_novelty(a, list(CHANNEL_KNOWN_HOOKS)).novel


def test_recycled_hook_blocked():
    novel = check_hook_novelty(
        "You blinked at the mirror — your reflection blinked one second later.",
        list(CHANNEL_KNOWN_HOOKS),
    )
    assert not novel.novel
    assert "similar" in novel.reason


def test_offline_basement_not_mirror_recycle():
    from pathlib import Path

    from shorts_bot.drafts.generator import DraftGenerator
    from shorts_bot.memory.store import MemoryStore

    store = MemoryStore(Path("/tmp/test_hook_novelty.db"))
    gen = DraftGenerator(store)
    draft = gen._generate_offline("you heard your voice calling from the basement", None)
    assert "basement" in draft.hook.lower() or "voice" in draft.hook.lower()
    assert hook_similarity(draft.hook, CHANNEL_KNOWN_HOOKS[0]) < 0.55
