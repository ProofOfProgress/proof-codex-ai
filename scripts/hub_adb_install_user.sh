#!/usr/bin/env bash
# Install adb to ~/android-sdk without sudo (hub laptop).
set -euo pipefail

PT="$HOME/android-sdk/platform-tools"
mkdir -p "$HOME/android-sdk"
cd "$HOME/android-sdk"

if [[ ! -x "$PT/adb" ]]; then
  echo "==> Downloading platform-tools (user install, no sudo)..."
  curl -fsSL -o pt.zip https://dl.google.com/android/repository/platform-tools-latest-linux.zip
  python3 -c 'import zipfile; zipfile.ZipFile("pt.zip").extractall(".")'
  chmod +x "$PT/adb" "$PT/fastboot" 2>/dev/null || true
fi

# Windows copy for USB phones (WSL2)
WIN_PT="/mnt/c/Users/$(whoami)/android-sdk/platform-tools"
if [[ ! -x "$WIN_PT/adb.exe" ]]; then
  echo "==> Downloading Windows platform-tools..."
  /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe -NoProfile -Command "
    \$dest = Join-Path \$env:USERPROFILE 'android-sdk'
    New-Item -ItemType Directory -Force -Path \$dest | Out-Null
    \$zip = Join-Path \$dest 'platform-tools.zip'
    if (-not (Test-Path (Join-Path \$dest 'platform-tools\\adb.exe'))) {
      Invoke-WebRequest -Uri 'https://dl.google.com/android/repository/platform-tools-latest-windows.zip' -OutFile \$zip
      Expand-Archive -Force -Path \$zip -DestinationPath \$dest
    }
  "
fi

echo ""
echo "OK — add to ~/.bashrc (optional):"
echo "  export PHONE_HUB_ADB=\"/mnt/c/Users/$(whoami)/android-sdk/platform-tools/adb.exe\""
echo ""
"$PT/adb" version | head -1 || true
