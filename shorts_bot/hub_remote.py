"""Auto-connect cloud agent to owner HP hub (Tailscale + SSH)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HUB_CONNECT = ROOT / "scripts" / "hub_connect.sh"
HUB_RUN = ROOT / "scripts" / "hub_run.sh"
HUB_VERIFY = ROOT / "scripts" / "hub_remote_verify.sh"
TS_SOCKET = os.environ.get("TS_SOCKET", "/var/run/tailscale/tailscaled.sock")


def secrets_configured() -> bool:
    return bool(
        os.environ.get("HUB_SSH_HOST")
        and os.environ.get("HUB_SSH_USER")
        and os.environ.get("HUB_SSH_PRIVATE_KEY")
    )


def tailscale_auth_configured() -> bool:
    return bool(
        os.environ.get("TAILSCALE_AUTH_KEY") or os.environ.get("TALESCALE_AUTH_KEY")
    )


def _run_script(script: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if args and args[0] == "--quiet":
        env["HUB_QUIET"] = "1"
    cmd = ["bash", str(script), *args]
    return subprocess.run(cmd, cwd=ROOT, env=env, check=check, text=True)


def ensure_connected(*, quiet: bool = False) -> bool:
    """Join Tailscale if hub secrets exist. Idempotent."""
    if not secrets_configured():
        if not quiet:
            print("Hub SSH secrets not configured — skip auto-connect")
        return False
    try:
        args = ("--quiet",) if quiet else ()
        _run_script(HUB_CONNECT, *args)
        return True
    except subprocess.CalledProcessError:
        return False


def status() -> dict[str, str | bool]:
    """Return hub connection status without connecting."""
    info: dict[str, str | bool] = {
        "secrets_configured": secrets_configured(),
        "tailscale_auth_configured": tailscale_auth_configured(),
        "tailscale_running": Path(TS_SOCKET).exists(),
        "hub_host": os.environ.get("HUB_SSH_HOST", ""),
        "hub_user": os.environ.get("HUB_SSH_USER", ""),
    }
    if info["tailscale_running"]:
        try:
            proc = subprocess.run(
                ["tailscale", f"--socket={TS_SOCKET}", "ip", "-4"],
                capture_output=True,
                text=True,
                check=False,
            )
            info["vm_tailscale_ip"] = proc.stdout.strip() or ""
        except OSError:
            info["vm_tailscale_ip"] = ""
    else:
        info["vm_tailscale_ip"] = ""
    return info


def run_remote(command: list[str]) -> int:
    """Ensure connected, then run command on hub."""
    if not command:
        print("hub_remote run: command required", file=sys.stderr)
        return 2
    if not ensure_connected(quiet=True):
        return 1
    proc = subprocess.run(["bash", str(HUB_RUN), *command], cwd=ROOT)
    return proc.returncode


def verify() -> int:
    """Full connect + SSH smoke test."""
    proc = subprocess.run(["bash", str(HUB_VERIFY)], cwd=ROOT)
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Auto-connect cloud agent to owner hub (Tailscale + SSH)"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ensure = sub.add_parser("ensure", help="Join Tailscale if hub secrets exist")
    p_ensure.add_argument("--quiet", "-q", action="store_true")

    sub.add_parser("status", help="Show hub secret + Tailscale status")

    p_run = sub.add_parser("run", help="Run a command on the hub")
    p_run.add_argument("remote_command", nargs=argparse.REMAINDER)

    sub.add_parser("verify", help="Connect and run SSH smoke test")

    args = parser.parse_args(argv)

    if args.cmd == "ensure":
        ok = ensure_connected(quiet=args.quiet)
        return 0 if ok or not secrets_configured() else 1
    if args.cmd == "status":
        info = status()
        for key, val in info.items():
            print(f"{key}: {val}")
        return 0
    if args.cmd == "run":
        cmd = args.remote_command
        if cmd and cmd[0] == "--":
            cmd = cmd[1:]
        return run_remote(cmd)
    if args.cmd == "verify":
        return verify()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
