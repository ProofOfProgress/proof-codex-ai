#!/usr/bin/env bash
# Move mouse to top-right corner on hub Windows desktop (via local helper daemon).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PS="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
if [[ ! -f "$PS" ]]; then
  PS="/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"
fi

bash "$ROOT/scripts/desktop_helper_ensure.sh"

repo_win="$("$PS" -NoProfile -Command "wslpath -w '$ROOT'" 2>/dev/null || wslpath -w "$ROOT")"
ps1_win="$("$PS" -NoProfile -Command "wslpath -w '$ROOT/scripts/desktop_helper/move_top_right.ps1'" 2>/dev/null || wslpath -w "$ROOT/scripts/desktop_helper/move_top_right.ps1")"

"$PS" -NoProfile -ExecutionPolicy Bypass -Command "\$env:DESKTOP_HUB_REPO_WIN='$repo_win'; & '$ps1_win'"
