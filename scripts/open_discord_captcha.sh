#!/usr/bin/env bash
# Launch visible Discord login on HP (WSLg). Cloud agent or owner can trigger.
set -euo pipefail
cd "$(dirname "$0")/.."

PS="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
if [[ ! -x "$PS" ]]; then
  echo "Run on hub WSL. Or double-click scripts/OPEN_DISCORD_CAPTCHA.bat on Windows."
  exit 1
fi

"$PS" -NoProfile -ExecutionPolicy Bypass -Command "
Start-Process wsl.exe -ArgumentList @(
  '-d','Ubuntu','--cd','/home/isaac/proof-codex-ai',
  '-e','bash','-lc',
  'export DISPLAY=:0 WAYLAND_DISPLAY=wayland-0 BROWSER_ENABLED=true BROWSER_ALLOW_VISIBLE=true; python3 -m shorts_bot.browser.cli open discord --minutes 25 --block'
)
Write-Host 'Opening Discord in Chromium — complete CAPTCHA on your screen.'
"
