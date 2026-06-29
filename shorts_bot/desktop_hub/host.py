"""Resolve desktop helper host from WSL or env."""

from __future__ import annotations

import os
import re
from pathlib import Path


def windows_host_from_wsl() -> str | None:
    """WSL2: Windows host is usually the nameserver in /etc/resolv.conf."""
    resolv = Path("/etc/resolv.conf")
    if not resolv.is_file():
        return None
    for line in resolv.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("nameserver "):
            ip = line.split()[1]
            if re.match(r"^\d+\.\d+\.\d+\.\d+$", ip):
                return ip
    return None


def default_helper_host() -> str:
    explicit = (os.environ.get("DESKTOP_HELPER_HOST") or "").strip()
    if explicit:
        return explicit
    wsl_host = windows_host_from_wsl()
    if wsl_host:
        return wsl_host
    return "127.0.0.1"


def default_helper_port() -> int:
    raw = (os.environ.get("DESKTOP_HELPER_PORT") or "9876").strip()
    try:
        return int(raw)
    except ValueError:
        return 9876


def helper_base_url() -> str:
    return f"http://{default_helper_host()}:{default_helper_port()}"
