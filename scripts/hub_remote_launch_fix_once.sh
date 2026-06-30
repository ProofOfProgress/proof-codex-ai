#!/usr/bin/env bash
# Cloud agent: open FIX HUB ONCE on the owner Windows desktop (owner types Ubuntu password once).
set -euo pipefail

CMD="/mnt/c/Windows/System32/cmd.exe"
DESKTOP_BAT='C:\Users\isaac\Desktop\FIX HUB ONCE (Proof Codex).bat'

if [[ ! -x "$CMD" ]]; then
  echo "Windows cmd.exe not found — run FIX HUB ONCE from Desktop manually."
  exit 1
fi

if [[ ! -f "/mnt/c/Users/isaac/Desktop/FIX HUB ONCE (Proof Codex).bat" ]]; then
  echo "Desktop shortcut missing — copy scripts/FIX_HUB_ONCE.bat to Desktop first."
  exit 1
fi

"$CMD" /c start "" "$DESKTOP_BAT"
echo "Opened FIX HUB ONCE on Windows Desktop."
echo "Owner: click the Ubuntu window, enter Ubuntu password once when [sudo] asks."
