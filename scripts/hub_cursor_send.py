#!/usr/bin/env python3
"""Standalone Cursor chat send — no pydantic/rich (hub WSL safe)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shorts_bot.desktop_hub.cursor_chat import CursorChatError, resolve_cursor_coords, send_cursor_message


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("Usage: python3 scripts/hub_cursor_send.py <message>", file=sys.stderr)
        print("       python3 scripts/hub_cursor_send.py --coords-only", file=sys.stderr)
        return 2
    if args[0] == "--coords-only":
        try:
            ix, iy, sx, sy = resolve_cursor_coords()
        except CursorChatError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(f"input=({ix},{iy}) send=({sx},{sy})")
        return 0
    if args[0] == "--msg-b64":
        import base64
        message = base64.b64decode(args[1]).decode("utf-8")
    elif args[0] == "--msg-file":
        message = Path(args[1]).read_text(encoding="utf-8")
    else:
        message = " ".join(args)
    try:
        ix, iy, sx, sy = send_cursor_message(message)
    except CursorChatError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK input=({ix},{iy}) send=({sx},{sy})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
