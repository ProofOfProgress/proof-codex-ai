"""Launch phase stubs — silent launch retired."""

from __future__ import annotations

from shorts_bot.production.launch_phase import (
    is_silent_launch_draft,
    silent_launch_script_rules,
    would_be_silent_launch,
)


def test_silent_launch_disabled_by_default():
    assert not would_be_silent_launch(1)
    assert not is_silent_launch_draft(99)
    assert silent_launch_script_rules() == ""
