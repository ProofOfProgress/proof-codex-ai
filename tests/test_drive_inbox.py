from shorts_bot.drive.client import parse_folder_id
from shorts_bot.drive.inbox import infer_draft_id_from_filename, load_state, save_state


def test_parse_folder_id_from_url():
    url = "https://drive.google.com/drive/folders/abc123XYZ/view"
    assert parse_folder_id(url) == "abc123XYZ"


def test_parse_folder_id_raw():
    assert parse_folder_id("abc123XYZ") == "abc123XYZ"


def test_infer_draft_id_from_filename():
    assert infer_draft_id_from_filename("draft_6.mp4") == 6
    assert infer_draft_id_from_filename("Draft-12-final.mp4") == 12
    assert infer_draft_id_from_filename("6_chatgpt_plus.mp4") == 6
    assert infer_draft_id_from_filename("chatgpt_plus.mp4") is None


def test_inbox_state_roundtrip(tmp_path, monkeypatch):
    from shorts_bot.config import Settings

    state_path = tmp_path / "drive_inbox_state.json"
    fake = Settings(google_drive_state_path=state_path)
    monkeypatch.setattr("shorts_bot.drive.inbox.settings", fake)

    save_state({"processed_file_ids": ["file1"], "assignments": {}})
    loaded = load_state()
    assert loaded["processed_file_ids"] == ["file1"]
    assert loaded["assignments"] == {}


def test_drive_configured_false_when_no_folder(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.drive.client import drive_configured

    fake = Settings(google_drive_folder_id="", google_drive_inbox_enabled=True)
    monkeypatch.setattr("shorts_bot.config.settings", fake)
    assert not drive_configured()


def test_drive_configured_true_when_folder_set(monkeypatch):
    from shorts_bot.config import Settings
    from shorts_bot.drive.client import drive_configured

    fake = Settings(google_drive_folder_id="abc123", google_drive_inbox_enabled=True)
    monkeypatch.setattr("shorts_bot.config.settings", fake)
    assert drive_configured()
