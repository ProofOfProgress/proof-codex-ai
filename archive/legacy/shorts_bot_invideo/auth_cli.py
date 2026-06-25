"""InVideo connection status + MCP probe."""

from __future__ import annotations

import argparse

from rich.console import Console
from rich.panel import Panel

from shorts_bot.invideo.auth import auth_status, credentials_status_message_full
from shorts_bot.invideo.mcp_client import probe_mcp

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="InVideo AI — status and MCP test")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("status", help="Show API key + MCP + browser session")
    sub.add_parser("test", help="Probe InVideo MCP (lists tools)")

    args = parser.parse_args()
    cmd = args.cmd or "status"

    if cmd == "test":
        ok, detail = probe_mcp()
        if ok:
            console.print(f"[green]{detail}[/green]")
        else:
            console.print(f"[red]{detail}[/red]")
        raise SystemExit(0 if ok else 1)

    st = auth_status()
    console.print(Panel(credentials_status_message_full(), title="InVideo"))
    console.print(f"API key saved: {st['api_key_configured']}")
    console.print(f"MCP ready: {st['mcp_ready']}")
    console.print(f"Browser logged in: {st['browser_logged_in']}")
    console.print(f"Production ready: {st['production_ready']}")
    console.print(f"App: {st['app_url']}")
    if not st["production_ready"]:
        console.print("\n[yellow]Next:[/yellow] python3 -m shorts_bot.invideo.handoff_cli")


if __name__ == "__main__":
    main()
