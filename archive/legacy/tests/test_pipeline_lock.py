import os
from unittest.mock import patch

from shorts_bot.production.pipeline_lock import acquire_lock, read_lock, release_lock


def test_lock_acquire_and_release(tmp_path, monkeypatch):
    from shorts_bot import config

    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    monkeypatch.setattr(config.settings, "pipeline_exclusive_lock", True)

    assert acquire_lock(3) is True
    info = read_lock()
    assert info is not None
    assert info.draft_id == 3
    assert info.pid == os.getpid()
    release_lock(3)
    assert read_lock() is None


def test_lock_blocks_second_holder(tmp_path, monkeypatch):
    from shorts_bot import config

    monkeypatch.setattr(config.settings, "data_dir", tmp_path)
    monkeypatch.setattr(config.settings, "pipeline_exclusive_lock", True)
    acquire_lock(3)

    with patch("shorts_bot.production.pipeline_lock.os.getpid", return_value=99999):
        assert acquire_lock(4) is False

    release_lock(3)
