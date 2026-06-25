"""Resemble voice clone setup — list voices, test synthesis."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

from shorts_bot.config import settings
from shorts_bot.production.tts.resemble import list_voices, probe_resemble, synthesize_resemble

console = Console()


def cmd_list() -> int:
    key = (settings.resemble_api_key or "").strip()
    if not key:
        console.print("[red]Set RESEMBLE_API_KEY in Cursor Secrets[/red]")
        return 1
    voices = list_voices(key)
    table = Table(title="Resemble voices on your account")
    table.add_column("Name")
    table.add_column("UUID")
    table.add_column("Type")
    for v in voices:
        table.add_row(
            str(v.get("name") or v.get("title") or "?"),
            str(v.get("uuid") or v.get("voice_uuid") or "?"),
            str(v.get("voice_type") or v.get("type") or ""),
        )
    console.print(table)
    console.print(
        "\n[yellow]Copy your clone UUID → RESEMBLE_VOICE_UUID in Cursor Secrets[/yellow]"
    )
    return 0


def cmd_test(text: str) -> int:
    if not settings.has_resemble:
        console.print("[red]RESEMBLE_API_KEY + RESEMBLE_VOICE_UUID required[/red]")
        return 1
    ok, msg = probe_resemble(settings.resemble_api_key or "", settings.resemble_voice_uuid or "")
    console.print(f"Probe: {'OK' if ok else 'FAIL'} — {msg}")
    if not ok:
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test_clone.mp3"
        provider, detail = synthesize_resemble(text, out)
        console.print(f"[green]{provider}: {detail}[/green]")
        console.print(f"Sample written: {out} ({out.stat().st_size} bytes)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Resemble voice clone helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List voices on Resemble account")
    p_test = sub.add_parser("test", help="Synthesize test phrase with your clone")
    p_test.add_argument("--text", default="Hey. I couldn't sleep again. Here's what helped me.")
    args = parser.parse_args()
    if args.cmd == "list":
        raise SystemExit(cmd_list())
    raise SystemExit(cmd_test(args.text))


if __name__ == "__main__":
    main()
