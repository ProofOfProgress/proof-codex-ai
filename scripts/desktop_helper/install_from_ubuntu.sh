#!/usr/bin/env bash
# Run Windows desktop helper install FROM Ubuntu (WSL) — easiest if PowerShell paths confuse you.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

PS="/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
if [[ ! -f "$PS" ]]; then
  PS="/mnt/c/WINDOWS/System32/WindowsPowerShell/v1.0/powershell.exe"
fi
if [[ ! -f "$PS" ]]; then
  echo "ERROR: PowerShell not found. Run INSTALL_DESKTOP_HELPER.bat from Windows instead."
  exit 1
fi

WIN_PS1=$(wslpath -w "$ROOT/scripts/desktop_helper_install.ps1")
echo "Repo (Linux): $ROOT"
echo "Running Windows install via PowerShell..."
"$PS" -NoProfile -ExecutionPolicy Bypass -File "$WIN_PS1"
echo ""
echo "Next steps:"
echo "  1. Copy data/desktop_hub/helper.env.example to data/desktop_hub/helper.env"
echo "  2. Paste DESKTOP_HELPER_TOKEN (no spaces)"
echo "  3. In Windows File Explorer open this folder and double-click START_DESKTOP_HELPER.bat:"
wslpath -w "$ROOT/scripts"
