from shorts_bot.production.content_format import (
    effective_max_i2v_beats,
    profile_for,
    PROFILES,
)


def test_short_hybrid_caps_i2v():
    prof = profile_for("short_hybrid")
    assert prof.max_i2v_beats == 3
    assert prof.aspect_ratio == "9:16"


def test_long_compilation_zero_i2v():
    prof = profile_for("long_compilation")
    assert prof.max_i2v_beats == 0
    assert prof.reuse_short_clips is True
    assert prof.is_long_form


def test_effective_max_respects_format(monkeypatch):
    from shorts_bot.config import settings

    monkeypatch.setattr(settings, "content_format", "short_hybrid")
    monkeypatch.setattr(settings, "ai_video_max_beats", 10)
    assert effective_max_i2v_beats() == 3

    monkeypatch.setattr(settings, "content_format", "long_compilation")
    assert effective_max_i2v_beats() == 0


def test_unknown_format_falls_back_to_short_30():
    prof = profile_for("unknown_xyz")
    assert prof.id == "short_30"


def test_all_profiles_have_labels():
    assert len(PROFILES) >= 5
    for p in PROFILES.values():
        assert p.label
        assert p.target_duration_seconds[1] >= p.target_duration_seconds[0]
