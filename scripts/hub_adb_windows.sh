#!/usr/bin/env bash
# Run ADB on Windows host (phones plug into HP USB, not WSL).
set -euo pipefail
cd "$(dirname "$0")/.."

ADB_WIN="${ADB_WIN:-/mnt/c/Users/isaac/AppData/Local/Android/Sdk/platform-tools/adb.exe}"
if [[ ! -x "$ADB_WIN" ]]; then
  ADB_WIN="/mnt/c/platform-tools/adb.exe"
fi
if [[ ! -x "$ADB_WIN" ]]; then
  echo "Windows adb not found. Install: bash scripts/hub_adb_install_user.sh (WSL) OR Android SDK on Windows."
  echo "If phone is USB to HP: run usbipd attach in Admin PowerShell — see scripts/hub_usbipd_attach.ps1"
  exit 1
fi

echo "==> Windows adb: $ADB_WIN"
"$ADB_WIN" devices -l
echo ""
echo "If empty: unlock phone, accept USB debugging, try usbipd wsl attach."
