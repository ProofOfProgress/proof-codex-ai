"""Tests for hub_lib SSH helpers (sourced in subshell)."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _hub_lib_eval(func: str, *, env: dict[str, str] | None = None) -> str:
    env_exports = ""
    if env:
        env_exports = " ".join(f'{k}="{v}"' for k, v in env.items()) + "; "
    script = f"""
set -euo pipefail
source scripts/hub_lib.sh
hub_lib_init
{env_exports}
{func}
"""
    proc = subprocess.run(
        ["bash", "-c", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.strip()


def test_wrap_windows_gateway_uses_wsl_repo_cd():
    out = _hub_lib_eval('hub_wrap_windows_gateway_cmd "python3 --version"')
    assert out.startswith('wsl.exe -d Ubuntu --cd /home/isaac/proof-codex-ai -e bash -lc "')
    assert "python3 --version" in out
    assert out.endswith('"')


def test_wrap_windows_gateway_passthrough_wsl():
    cmd = "wsl.exe bash -lc echo ok"
    out = _hub_lib_eval(f'hub_wrap_windows_gateway_cmd "{cmd}"')
    assert out == cmd


def test_wrap_windows_gateway_skips_when_not_port_2222():
    out = _hub_lib_eval(
        'hub_wrap_windows_gateway_cmd "python3 --version"',
        env={"HUB_SSH_PORT": "22"},
    )
    assert out == "python3 --version"


def test_ssh_opts_userspace_adds_tailscale_nc(monkeypatch, tmp_path):
    monkeypatch.delenv("HUB_SSH_PORT", raising=False)
    # Simulate cloud VM without tun device
    fake_tun = tmp_path / "tun"
    script = f"""
set -euo pipefail
source scripts/hub_lib.sh
hub_lib_init
hub_uses_userspace_tailscale() {{ [[ ! -e "{fake_tun}/missing" ]]; }}
mapfile -t opts < <(hub_ssh_opts /tmp/key)
printf '%s\\n' "${{opts[@]}}"
"""
    proc = subprocess.run(["bash", "-c", script], cwd=ROOT, capture_output=True, text=True, check=True)
    assert any("ProxyCommand=tailscale" in line and " nc %h 22" in line for line in proc.stdout.splitlines())
