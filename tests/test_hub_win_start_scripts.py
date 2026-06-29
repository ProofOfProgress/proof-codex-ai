"""Hub Windows start scripts — Desktop path must not break on shortcuts."""

from __future__ import annotations

from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def test_hub_green_start_uses_wsl_repo_not_desktop_parent():
    text = (SCRIPTS / "HUB_GREEN_START.bat").read_text(encoding="utf-8")
    assert 'cd /d "%~dp0.."' not in text
    assert "hub_win_repo_path.bat" in text
    assert "REPO_WSL" in text


def test_fix_hub_once_uses_wsl_repo_not_desktop_parent():
    text = (SCRIPTS / "FIX_HUB_ONCE.bat").read_text(encoding="utf-8")
    assert 'cd /d "%~dp0.."' not in text
    assert "hub_win_repo_path.bat" in text


def test_install_copies_repo_path_helper_to_desktop():
    text = (SCRIPTS / "INSTALL_HUB_START_BUTTON.bat").read_text(encoding="utf-8")
    assert "hub_win_repo_path.bat" in text
    assert "HUB_DESKTOP_NOTE.txt" in text


def test_autostart_ps1_resolves_repo_via_wsl():
    text = (SCRIPTS / "windows_hub_autostart.ps1").read_text(encoding="utf-8")
    assert "proof-codex-ai" in text
    assert "hub_one_click_start.sh" in text


def test_hub_win_repo_path_bat_exists():
    assert (SCRIPTS / "hub_win_repo_path.bat").is_file()
